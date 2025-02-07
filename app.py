import json, config 
from binance.client import Client
from flask import Flask, render_template, request 

app = Flask(__name__, template_folder='templates')

client = Client(config.BINANCE_API_KEY,config.BINANCE_API_SECRET)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

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

