import json
from flask import Flask
from flask import request
import pandas as pd


app = Flask(__name__)

@app.route('/trend',methods=["POST","GET"])
def trend():
    
    if request.method == "POST":
        
        close = eval(request.args.get("close"))
                
        result = score(close)
                
        return result

@app.route('/')
def index():
    return "Trend Indicator"


def score(close):
    
    score = 0

    temp = list()
    
    df = pd.DataFrame()
    df['Close'] = close
    
    for i in [5,10,20,30,50,100,150,200]:
        temp.append(df['Close'].rolling(window=i).mean().values.tolist())
        
    ma_5_period,ma_10_period,ma_20_period,ma_30_period,ma_50_period,ma_100_period,ma_150_period,ma_200_period=temp
    
    temp = list()

    for i in [5,10,20,30,50,100,150,200]:
        temp.append(df['Close'].ewm(span=i, adjust=False).mean().values.tolist())
        
    ema_5_period,ema_10_period,ema_20_period,ema_30_period,ema_50_period,ema_100_period,ema_150_period,ema_200_period=temp
    
    # Stock Price
    price = close[-1]
            
    score_df = pd.DataFrame(columns=['EMA5','EMA10','EMA20','EMA30','EMA50','EMA100','EMA150','EMA200',\
                                    'MA5','MA10','MA20','MA30','MA50','MA100','MA150','MA200'])
    
    row = {

        'EMA5':ema_5_period[-1],
        'EMA10':ema_10_period[-1],
        'EMA20':ema_20_period[-1],
        'EMA30':ema_30_period[-1],
        'EMA50':ema_50_period[-1],
        'EMA100':ema_100_period[-1],
        'EMA150':ema_150_period[-1],
        'EMA200':ema_200_period[-1],
        'MA5':ma_5_period[-1],
        'MA10':ma_10_period[-1],
        'MA20':ma_20_period[-1],
        'MA30':ma_30_period[-1],
        'MA50':ma_50_period[-1],
        'MA100':ma_100_period[-1],
        'MA150':ma_150_period[-1],
        'MA200':ma_200_period[-1]
    }

    score_df = score_df.append(row, ignore_index=True)
            
    score = sum(score_df[score_df < price].count())
    
    row = {

        'EMA5':ema_5_period,
        'EMA10':ema_10_period,
        'EMA20':ema_20_period,
        'EMA30':ema_30_period,
        'EMA50':ema_50_period,
        'EMA100':ema_100_period,
        'EMA150':ema_150_period,
        'EMA200':ema_200_period,
        'MA5':ma_5_period,
        'MA10':ma_10_period,
        'MA20':ma_20_period,
        'MA30':ma_30_period,
        'MA50':ma_50_period,
        'MA100':ma_100_period,
        'MA150':ma_150_period,
        'MA200':ma_200_period,
        'Total_Score':16,
        'Score':score
    }

        
    return row    
    
    
app.run()