import json, config 
import pandas as pd
from binance.client import Client
from datetime import datetime, timezone
from flask import Flask, render_template, request 

app = Flask(__name__, template_folder='templates')

client = Client(config.BINANCE_API_KEY,config.BINANCE_API_SECRET)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/binance_account')
def binance():
    info = client.get_account()
    
    # Composition du portefeuille binance 
    df = pd.DataFrame(info['balances'])
    df["free"] = pd.to_numeric(df["free"], errors="coerce")
    df["locked"] = pd.to_numeric(df["locked"], errors="coerce") 
    df['total'] = df['free'] + df['locked']
    df = df[(df["free"] != 0) | (df["locked"] != 0)]
    df = df[~df['asset'].isin(['ETHW', 'LDUSDC'])] # Supprimer les lignes où 'asset' est 'ETHW' ou 'LDUSDC'
    
    REFERENCE = 'USDT'
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
    
    print(df)

    return render_template('binance.html', df=df, titles=df.columns.values)


@app.route('/webhook_order_one', methods=['POST'])
def strategy_one():
    
    data = json.loads(request.data)

    if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            'code' : 'error',
            'message' : 'Invalid passphrase'
        }

    else:
        #######
        # PYTHON CODE TO EXECUTE ORDER
        info = client.get_account()
        print(info)
        print(data['ticker'])
        #######
        return {
            'code' : 'sucess',
            'message' : data
        }

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5555, debug=True)

