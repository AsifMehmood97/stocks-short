import json
from flask import Flask
from flask import request
import pandas as pd
import numpy as np

app = Flask(__name__)

@app.route('/indicator',methods=["POST","GET"])
def indicator():
    
    if request.method == "POST":
        
        data = eval(request.args.get("data"))
        
        df = pd.DataFrame(data, columns=['timestamp', 'Open', 'High', 'Low', 'Close'])
        
        result = chandelier_exit(df['timestamp'], df['Close'], df['High'], df['Low'])
                
        return result
    
    
def chandelier_exit(timestamp, close, high, low, length=1, mult=2, use_close=True):

    atr = pd.Series(np.nan, index=high.index)  # initialize True Range series with NaNs
    
    for i in range(len(high.values)):
        atr[i] = 2 * max(high.values[i] - low.values[i], abs(high.values[i] - close.values[i-1]), abs(low.values[i] - close.values[i-1]))

    atr = atr.dropna()

    long_stop_list = list()
    prev_long_stop_list = list()

    short_stop_list = list()
    prev_short_stop_list = list()

    dirs = list()

    bought_first = False
    
    result = {}
    
    for i in range(len(atr)):
        ls = close.values[i] - atr[i]

        if i == 0:
            prev_ls = ls
            prev_long_stop_list.append(ls)
            dirs.append(1)
        else:
            prev_ls = long_stop_list[i-1]
            prev_long_stop_list.append(prev_ls)

            if close.values[i-1] > prev_ls:
                ls = max(ls, prev_ls)
            else:
                ls = ls

        long_stop_list.append(ls)

        # Short Stop
        ss = close.values[i] + atr[i]

        if i == 0:
            prev_ss = ss
            prev_short_stop_list.append(ss)
        else:
            prev_ss = short_stop_list[i-1]
            prev_short_stop_list.append(prev_ss)

            if close.values[i-1] < prev_ss:
                ss = min(ss, prev_ss)
            else:
                ss = ss

        short_stop_list.append(ss)

        if close.values[i] > prev_ss:
            dirs.append(1)
        elif close.values[i] < prev_ls:
            dirs.append(-1)
        elif i != 0:
            dirs.append(dirs[-1])

        buy_signal = False
        sell_signal = False

        if dirs[-1] == 1 and dirs[i-1] == -1:
            buy_signal = True
        elif dirs[-1] == -1 and dirs[i-1] == 1:
            sell_signal = True
                    
        if buy_signal:
            bought_first = True
            result[timestamp.values[i]] = {"Buy":True, "Sell":False}
        
        elif sell_signal:
            bought_first = False
            result[timestamp.values[i]] = {"Buy":False, "Sell":True}
            
        else:
            result[timestamp.values[i]] = {"Buy":False, "Sell":False}

    return result

@app.route('/')
def index():
    return "Indicator (Buy-Sell)"


app.run()