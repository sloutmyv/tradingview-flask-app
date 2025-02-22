import json, config 
from binance_api import get_binance_portfolio, get_orders, merge_and_sort_dataframes
from flask import Flask, render_template, request 

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/binance_account')
def binance():
    df, total_reference, dict_wap, filtered_cryptos = get_binance_portfolio()
    df_order = merge_and_sort_dataframes(filtered_cryptos, 'CREATED TIME')
    return render_template('binance.html', df=df, titles=df.columns.values, total_usd=float(total_reference), dict_wap=dict_wap, df_order=df_order, titles_order=df_order.columns.values)


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

