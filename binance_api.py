import pandas as pd
import config 
from binance.client import Client

client = Client(config.BINANCE_API_KEY,config.BINANCE_API_SECRET)

REFERENCE = 'USDT'

def get_binance_portfolio():
    info = client.get_account()
    df = pd.DataFrame(info['balances'])

    df["free"] = pd.to_numeric(df["free"], errors="coerce")
    df["locked"] = pd.to_numeric(df["locked"], errors="coerce") 
    df['total'] = df['free'] + df['locked']

    df = df[(df["free"] != 0) | (df["locked"] != 0)]
    df = df[~df['asset'].isin(['ETHW', 'LDUSDC'])] # Supprimer les lignes où 'asset' est 'ETHW' ou 'LDUSDC'

    df["pair"] = df["asset"] + REFERENCE 

    def apply_formula(row):
        if row['asset'] == REFERENCE:
            return row['total'] * 1
        else:
            return row['total'] * float(client.get_avg_price(symbol=row['pair'])['price'])

    df['reference'] = df.apply(apply_formula, axis=1)
    df = df.sort_values(by='reference', ascending=False)

    total_reference = df['reference'].sum() # Calcul du pourcentage de chaque ligne par rapport au total de la colonne 'reference'
    df['percentage_of_total'] = (df['reference'] / total_reference) * 100

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

    return df, float(total_reference)