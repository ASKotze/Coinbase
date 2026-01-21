import time
import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

while True:
    def print_targets(ticker_data):
        # print('Tick Data: ', ticker_data)
        sorted_ticker_data = sorted(ticker_data, key=lambda x: x['pair'])
        # print('Sorted Tick Data: ', sorted_ticker_data)
        print('__________________________________________________________________')
        print('PAIR'.ljust(10), 'Low Target (' + str(-low_target) + ')'.ljust(5), 'Rise Target (' + str(rise_target) + ')'.ljust(5), 'Instruction'.ljust(5))
        print(now)
        print('__________________________________________________________________')
        for i in range(len(sorted_ticker_data)):
            print((i+1), sorted_ticker_data[i]['pair'].ljust(15),
                  (sorted_ticker_data[i]['low_target'] + '[' + str(round(sorted_ticker_data[i]['max-min'],1)) + ']').ljust(20),
                  (sorted_ticker_data[i]['rise_target'] + '[' + str(round(sorted_ticker_data[i]['diffs'],1)) + ']').ljust(20),
                  sorted_ticker_data[i]['instruction'].ljust(20))

    def send_telegram_message():
        global buy_message
        TOKEN = os.getenv('Telegram_Token')
        chat_id = os.getenv('Chat_ID')
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={buy_message}"
        try:
            requests.get(url).json()  # this sends the message
            time.sleep(15)
        except requests.exceptions.ConnectionError:
            status_code = "Connection refused"

    ticker_data = []
    ticker_data_list = []
    low_target = 40.0
    rise_target = 15.0
    buy = '\u2705'
    hold = '\u274C'
    coinbase_dict = ['AAVE-USD', 'ADA-USD', 'ALGO-USD', 'ANKR-USD','APE-USD', 'ARB-USD', 'ATOM-USD', 'AVAX-USD',
                     'AXS-USD', 'BCH-USD', 'BERA-USD', 'BTC-USD', 'CRV-USD', 'DOGE-USD', 'DOT-USD', 'ENS-USD',
                     'ETH-USD', 'EURC-USDC', 'FET-USD', 'GRT-USD', 'HBAR-USD', 'HNT-USD', 'IMX-USD', 'INJ-USD',
                     'LDO-USD', 'LINK-USD', 'LRC-USD', 'LTC-USD', 'MKR-USD', 'NEAR-USD', 'ONDO-USD', 'OP-USD',
                     'PAXG-USD', 'POL-USD', 'PYTH-USD', 'RENDER-USD', 'SAND-USD', 'SEI-USD', 'SNX-USD', 'SOL-USD',
                     'STRK-USD', 'SUI-USD', 'S-USD', 'TAO-USD', 'TIA-USD', 'UNI-USD', 'XLM-USD', 'XRP-USD', 'ZEC-USD',
                     'ZRO-USD']
    print(len(coinbase_dict))
    for pair in coinbase_dict:
        try:
            reply_coinbase = requests.get('https://api.coinbase.com/v2/prices/' + pair + '/spot')
        except requests.RequestException as e:
            print('Communication error', e)
        else:
            if reply_coinbase.status_code == requests.codes.ok:
                # print(reply_coinbase.headers['Content-Type'])
                ticker_string = reply_coinbase.json()
                # print('Original Ticker String: ', ticker_string)
                for key, value in ticker_string.items():
                    ticker_string = value
                    ticker_string['pair'] = pair
                for key in ['base', 'currency']:
                    del ticker_string[key]
                now = datetime.now()
                ticker_string['timestamp'] = str(now)
                bid_current = ticker_string['amount']
                # print('Bid Current: ', bid_current)
                ticker_string['max'] = bid_current
                ticker_string['min'] = bid_current
                # print('Ticker String: ', ticker_string)
                output_file = 'C:/ASK/Python/ASK - Projects/Coinbase/ticker_data_coinbase.json'
                with open(output_file, 'r') as f:
                    ticker_data = json.load(f)
                # print('Ticker Data: ', ticker_data)
                for i in range(len(ticker_data)):
                    if ticker_data[i]['pair'] not in ticker_data_list:
                        ticker_data_list.append(ticker_data[i]['pair'])
                # print('Ticker Data List = ', ticker_data_list)
                # print(ticker_string['pair'])
                # print('Ticker Data: ', ticker_data)
                if ticker_string['pair'] not in ticker_data_list:
                    ticker_data.append(ticker_string)
                else:
                    for i in range(len(ticker_data)):
                        if ticker_string['pair'] == ticker_data[i]['pair']:
                            ticker_data[i]['timestamp'] = str(now)
                            if bid_current > ticker_data[i]['max']:
                                ticker_data[i]['max'] = bid_current
                                ticker_data[i]['min'] = bid_current
                            elif bid_current < ticker_data[i]['min']:
                                ticker_data[i]['min'] = bid_current
                            ticker_data[i]['amount'] = ticker_string['amount']
                            ticker_data[i]['max-min'] = 100 * (((float(ticker_data[i]['min'])) / float(ticker_data[i]['max'])) - 1)
                            ticker_data[i]['max-amount'] = 100 * (((float(ticker_data[i]['amount'])) / float(ticker_data[i]['max'])) - 1)
                            ticker_data[i]['diffs'] = ticker_data[i]['max-amount'] - ticker_data[i]['max-min']
                            if ticker_data[i]['max-min'] < -low_target:
                                ticker_data[i]['low_target'] = buy
                            else:
                                ticker_data[i]['low_target'] = hold
                            if (ticker_data[i]['diffs'] > rise_target) and (ticker_data[i]['low_target'] == buy):
                                ticker_data[i]['rise_target'] = buy
                            else:
                                ticker_data[i]['rise_target'] = hold
                            if (ticker_data[i]['low_target'] == buy) and (ticker_data[i]['rise_target'] == buy) and (ticker_data[i]['instruction'] == hold):
                                ticker_data[i]['instruction'] = buy
                                buy_message = ("\u2705                        \u2705                        \u2705" +
                                                  "\n".ljust(18) + "💥 " + ticker_data[i]['pair'] + " 💥" +
                                                  "\n".ljust(10) + "Low Target = BUY (" + str(round(ticker_data[i]['max-min'], 2)) + ')' +
                                                  "\n".ljust(10) + "Rise Target = BUY (" + str(round(ticker_data[i]['diffs'], 2)) + ')' +
                                               "\n".ljust(11) + "Instruction = BUY" +
                                               "\n".ljust(18) + "💥 " + ticker_data[i]['pair'] + " 💥" +
                                                  "\n\u2705                        \u2705                        \u2705")
                                send_telegram_message()
                            elif (ticker_data[i]['low_target'] == buy) and (ticker_data[i]['rise_target'] == buy) and (ticker_data[i]['instruction'] == buy):
                                ticker_data[i]['instruction'] = buy + buy
                                buy_message = ("\u2705\u2705                  \u2705\u2705                  \u2705\u2705" +
                                                  "\n".ljust(18) + "💥 " + ticker_data[i]['pair'] + " 💥" +
                                                  "\n".ljust(10) + "Low Target = BUY (" + str(round(ticker_data[i]['max-min'], 2)) + ')' +
                                                  "\n".ljust(10) + "Rise Target = BUY (" + str(round(ticker_data[i]['diffs'], 2)) + ')' +
                                               "\n".ljust(11) + "Instruction = BUYBUY" +
                                               "\n".ljust(18) + "💥 " + ticker_data[i]['pair'] + " 💥" +
                                                  "\n\u2705\u2705                  \u2705\u2705                  \u2705\u2705")
                                send_telegram_message()
                            elif (ticker_data[i]['low_target'] == buy) and (ticker_data[i]['rise_target'] == buy) and (ticker_data[i]['instruction'] == buy + buy):
                                ticker_data[i]['instruction'] = buy + buy + buy
                                buy_message = ("\u2705\u2705\u2705           \u2705\u2705\u2705           \u2705\u2705\u2705" +
                                                  "\n".ljust(18) + "💥 " + ticker_data[i]['pair'] + " 💥" +
                                                  "\n".ljust(10) + "Low Target = BUY (" + str(round(ticker_data[i]['max-min'], 2)) + ')' +
                                                  "\n".ljust(10) + "Rise Target = BUY (" + str(round(ticker_data[i]['diffs'], 2)) + ')' +
                                               "\n".ljust(11) + "Instruction = BUYBUYBUY" +
                                               "\n".ljust(18) + "💥 " + ticker_data[i]['pair'] + " 💥" +
                                                  "\n\u2705\u2705\u2705           \u2705\u2705\u2705           \u2705\u2705\u2705")
                                send_telegram_message()
                                ticker_data[i]['max'] = bid_current
                                ticker_data[i]['min'] = bid_current
                            else:
                                ticker_data[i]['instruction'] = hold
                # print('Ticker Data: ', ticker_data)
                with open(output_file, 'w') as f:
                    json.dump(ticker_data, f, indent=4)
                # print('Wallets :', len(wallets_dict))
                # print('###################################')
            else:
                print('Status Code: ', reply_coinbase.status_code, pair)
                print('Server error')
    # print(ticker_data)
    print_targets(ticker_data)
    time.sleep(300)