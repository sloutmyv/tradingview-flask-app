import pandas as pd
import config 
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT, ORDER_TYPE_STOP_LOSS_LIMIT, TIME_IN_FORCE_GTC

client = Client(config.BINANCE_API_KEY,config.BINANCE_API_SECRET)

REFERENCE = 'USDT'
COLATERAL = ['USDT','USDC']

def get_binance_portfolio():
    info = client.get_account()

    # Lister les assets en porteufeuille 
    df = pd.DataFrame(info['balances'])

    df["free"] = pd.to_numeric(df["free"], errors="coerce") # conversion en chiffre
    df["locked"] = pd.to_numeric(df["locked"], errors="coerce") # conversion en chiffre   
    df = df[(df["free"] != 0) | (df["locked"] != 0)] # Suppression des assets à qté nulle
    df['total'] = df['free'] + df['locked'] # calcul du total libre et bloqué sur un ordre 
    df = df[~df['asset'].isin(['ETHW', 'LDUSDC'])] # Suppression des assets 'ETHW' ou 'LDUSDC'
    df["pair"] = df["asset"] + REFERENCE # création d'une colonne pair avec une référence 

    def apply_formula(row):
        if row['asset'] == REFERENCE:
            return row['total'] * 1
        else:
            return row['total'] * float(client.get_avg_price(symbol=row['pair'])['price'])

    df['reference'] = df.apply(apply_formula, axis=1) # création d'une colonne reference indiquant le prix des assets par rapport à cette référence 
    df = df.loc[df['reference'] > 5] # suppression des assets dont la valeur référence est inférieur à 5
    df = df.sort_values(by='reference', ascending=False) # tri des assets possédé du plus important au moins important

    total_reference = df['reference'].sum() # Calcul du pourcentage de chaque ligne par rapport au total de la colonne 'reference'
    df['percentage_of_total'] = (df['reference'] / total_reference) * 100

    liste_asset = df["asset"].to_list()
    filtered_cryptos = [c for c in liste_asset if c not in ['USDT', 'USDC']]
    dict_awp = {}
    for i in filtered_cryptos:
        dict_awp[i]=weighted_avg_price(i, df[df['asset'] == i]['total'].iloc[0])
    
    # Désactiver la notation scientifique pour l'affichage
    df['percentage_of_total'] = df['percentage_of_total'].apply(lambda x: '{:.1f}'.format(x))   
    df['reference'] = df['reference'].apply(lambda x: '{:.1f}'.format(x))
    df['free'] = df['free'].apply(lambda x: '{:.4f}'.format(x))
    df['locked'] = df['locked'].apply(lambda x: '{:.4f}'.format(x))
    df['total'] = df['total'].apply(lambda x: '{:.4f}'.format(x))
    df = df.drop(columns=['pair'])

    # Renommer les colonnes
    df = df.rename(columns={
        "asset": "ASSET",
        "free": "AVAILABLE",
        "locked": "LOCKED",
        "total": "TOTAL",
        "reference": "$",
        "percentage_of_total": "%"
    })

    return df, float(total_reference), dict_awp, filtered_cryptos

def get_orders(symbol, nb=10):
    """
    Cette fonction renvoi la liste des 10 dernier ordres créer pour ce
    symbol

    :param symbol: BTCUSDT par exemple
    :param nb: qté des derniers ordes demandé
    :return: df des nb ordres passé pour ce symbol
    """
    orders = client.get_all_orders(symbol=symbol, limit=nb)
    df = pd.DataFrame(orders)
    df = df.drop(columns=['orderListId','timeInForce','icebergQty','selfTradePreventionMode','isWorking','workingTime','orderId','origQuoteOrderQty'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df['updateTime'] = pd.to_datetime(df['updateTime'], unit='ms')

    df = df.sort_values(by='time', ascending=False)
    

    def categorize_order(client_id):
        if client_id.startswith("ios"):
            return "IOS"
        elif client_id.startswith("web"):
            return "WEB"
        else:
            return "API"

    df["clientOrderId"] = df["clientOrderId"].apply(categorize_order)

    # Convertir les colonnes en float avant d'appliquer le formatage
    cols_to_format = ['price', 'executedQty','origQty', 'cummulativeQuoteQty', 'stopPrice']

    for col in cols_to_format:
        df[col] = df[col].astype(float)  # Conversion en float pour éviter les erreurs de formatage

    # Désactiver la notation scientifique pour l'affichage
    df['price'] = df['price'].apply(lambda x: '{:.1f}'.format(x))   
    df['executedQty'] = df['executedQty'].apply(lambda x: '{:.4f}'.format(x))
    df['origQty'] = df['origQty'].apply(lambda x: '{:.4f}'.format(x))
    df['cummulativeQuoteQty'] = df['cummulativeQuoteQty'].apply(lambda x: '{:.1f}'.format(x))
    df['stopPrice'] = df['stopPrice'].apply(lambda x: '{:.1f}'.format(x))

    # Renommer les colonnes
    df = df.rename(columns={
        "symbol": "PAIR",
        "clientOrderId": "TOOLS",
        "price": "LIMIT PRICE",
        'origQty':'ORDER QTY',
        "executedQty": "EXECUTED QTY",
        "cummulativeQuoteQty": "$",
        "status": "STATUS",
        "type": "TYPE",
        "side" : "SIDE",
        "stopPrice" : "STOP PRICE",
        "time" : "CREATED TIME",
        "updateTime" : "EXECUTED TIME",
    })

    new_order = ['PAIR', 'SIDE', 'TYPE','STOP PRICE','LIMIT PRICE','ORDER QTY','EXECUTED QTY','$','CREATED TIME','EXECUTED TIME','STATUS']
    df=df[new_order]

    return df


def weighted_avg_price(asset, qty_limit):
    """
    Cette fonction permet de calculer le pmp d'un asset relativement à un 
    ensemble de colateral choisi pour les trades (ici UDST, USDC)

    :param asset: asset (BTC, SOL...)
    :param qty_limit: qté de l'asset en portefeuille
    :return: Prix moyen pondéré des assets (en fonction des colaterals)
    """
    list_df = []
    for i in COLATERAL:
        pair = asset + i
        trades = client.get_my_trades(symbol=pair)
        df = pd.DataFrame(trades)
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df = df.sort_values(by='time', ascending=False)
        list_df.append(df)

    # Fusionner tous les DataFrames en un seul
    merged_df = pd.concat(list_df, ignore_index=True)
    merged_df = merged_df.sort_values(by='time', ascending=False)
    df_buy = merged_df[merged_df["isBuyer"] == True]

    # Calculer la somme cumulative de qty
    cumulative_qty = 0
    total_value = 0
    total_qty = 0

    # Ajouter les achats tant que la somme des quantités est inférieure ou égale à qty_limit
    for index, row in df_buy.iterrows():
        reel = float(row["qty"])-float(row["commission"])
        if cumulative_qty + reel <= qty_limit:
            cumulative_qty += reel
            total_value += float(row["price"]) * reel
            total_qty += reel
        else:
            break

    # Calcul du prix moyen pondéré
    if total_qty > 0:
        return total_value / total_qty
    else:
        return None  # Si aucune quantité n'a été ajoutée

def merge_and_sort_dataframes(liste, sort_column):
    """
    Cette fonction prend en entrée une liste d'assets.
    Son but est de sortir un df de l'ensemble des ordres de ces assets en fonction 
    des colaterals définit ('COLATERAL')
    Cette fonction appel la fonction get_order

    :param liste: liste des assets 
    :param sort_column: Nom de la colonne de tri
    :return: DataFrame fusionné et trié
    """
    # Fusionner tous les DataFrames en un seul
    liste_dfs=[]
    for i in liste:
        for j in COLATERAL:
            symbol = i + j
            df=get_orders(symbol)
            liste_dfs.append(df)

    merged_df = pd.concat(liste_dfs, ignore_index=True)

    # Trier du plus récent au plus ancien
    sorted_df = merged_df.sort_values(by=sort_column, ascending=False)

    return sorted_df

def withdrawal():
    w_h = client.get_withdraw_history()
    df = pd.DataFrame(w_h)
    df = df.drop(columns=['id','status','walletType','txKey','confirmNo','info','transferType','txId','network'])
    
    new_order = ['coin','amount','transactionFee','address','applyTime','completeTime']
    df=df[new_order]

    return df

def place_order_with_tp_sl(symbol, quantity, entry_type, entry_price=None, order_type="MARKET", tp_price=None, sl_price=None):
    """
    Passe un ordre (Market ou Limit) avec Take Profit et Stop Loss.

    :param symbol: La paire de trading, ex: "BTCUSDT"
    :param quantity: Quantité à acheter/vendre
    :param entry_type: "BUY" ou "SELL"
    :param entry_price: Prix d'entrée (nécessaire si order_type="LIMIT")
    :param order_type: "MARKET" ou "LIMIT"
    :param tp_price: Prix du Take Profit (facultatif)
    :param sl_price: Prix du Stop Loss (facultatif)
    """
    try:
        side = SIDE_BUY if entry_type.upper() == "BUY" else SIDE_SELL
        order = None

        # Passer l'ordre d'entrée
        if order_type.upper() == "MARKET":
            order = client.order_market(symbol=symbol, side=side, quantity=quantity)
        elif order_type.upper() == "LIMIT":
            if not entry_price:
                raise ValueError("entry_price est requis pour un ordre LIMIT")
            order = client.order_limit(
                symbol=symbol, side=side, quantity=quantity, price=entry_price, timeInForce=TIME_IN_FORCE_GTC
            )
        else:
            raise ValueError("order_type doit être 'MARKET' ou 'LIMIT'")

        print(f"Ordre {order_type} exécuté: {order}")

        # Placer le Take Profit (si défini)
        tp_order = None
        if tp_price:
            tp_order = client.order_limit_sell(
                symbol=symbol, quantity=quantity, price=tp_price
            ) if side == SIDE_BUY else client.order_limit_buy(
                symbol=symbol, quantity=quantity, price=tp_price
            )
            print(f"Take Profit placé: {tp_order}")

        # 3Placer le Stop Loss (si défini)
        sl_order = None
        if sl_price:
            sl_order = client.create_order(
                symbol=symbol,
                side=SIDE_SELL if side == SIDE_BUY else SIDE_BUY,
                type=ORDER_TYPE_STOP_LOSS_LIMIT,
                quantity=quantity,
                price=sl_price,  # Prix limite
                stopPrice=sl_price,  # Prix déclencheur
                timeInForce=TIME_IN_FORCE_GTC
            )
            print(f"Stop Loss placé: {sl_order}")

        return order, tp_order, sl_order

    except Exception as e:
        print(f"Erreur lors de l'exécution de l'ordre: {e}")
