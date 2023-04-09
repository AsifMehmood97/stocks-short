#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
from flask import Flask
from flask import request
import pandas as pd
import io
from tqdm import tqdm
from pandas_market_calendars import get_calendar
import requests


# In[2]:


app = Flask(__name__)

@app.route('/watchlist',methods=["POST","GET"])
def watchlist():
    
    dataframe_5m = pd.DataFrame(columns=['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits', 'ticker'])
    dataframe_5m.index = dataframe_5m['Datetime']
    dataframe_5m = dataframe_5m.drop(['Datetime'], axis=1)
    
    url = 'http://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt'
    response = requests.get(url)
    data = response.content.decode('utf-8')

    nasdaq_tickers = pd.read_csv(io.StringIO(data), delimiter='|')
    nasdaq_symbols = nasdaq_tickers['Symbol'].tolist()[:-1]

    stocks_not_availiable = []

    for i in tqdm(nasdaq_symbols[:150]):

        try:
            df = fetch_data(i,interval='5m')

            if len(df) > 101:
                dataframe_5m = pd.concat([dataframe_5m,df])

            else:
                print("Skipped: ",i)
                stocks_not_availiable.append(i)

        except:
            stocks_not_availiable.append(i)
                
    filtered_5m = pd.DataFrame(columns=['ticker','score','total'])
    
    tickers = list(pd.unique(dataframe_5m['ticker']))

    required = [i for i in tickers if i not in list(filtered_5m['ticker'])]

    for ticker in tqdm(required):

        ls = list(dataframe_5m[dataframe_5m['ticker']==ticker]['Close'].values)

        if len(ls) < 201:
            continue

        res = score(ls[-202:])

        row = {
            'ticker':ticker,
            'score':res['Score'],
            'total':res['Total_Score']
        }

        filtered_5m = filtered_5m.append(row, ignore_index=True)
        
    sorted_df = filtered_5m.sort_values('score', ascending=False)
        
    records =[(key,value) for key,value in zip(sorted_df['score'].value_counts().index,sorted_df['score'].value_counts().values)]
    counts = sorted(records,key =lambda x : x[0],reverse=True)

    desired_count = 10
    curr_count = 0
    highest_scores = []
    half = 0

    for i in counts:
        curr_count += i[1]

        if curr_count >= desired_count:
            half = i[0]
            break

        highest_scores.append(i[0])

    filtered_stocks = pd.DataFrame(columns=sorted_df.columns)

    if highest_scores == []:

        filtered_stocks = pd.concat([filtered_stocks,sorted_df[sorted_df['score']==half]])

        filtered_stocks = filtered_stocks.iloc[:desired_count, :]

    else:

        for i in highest_scores:
            filtered_stocks = pd.concat([filtered_stocks,sorted_df[sorted_df['score']==i]])

        req_count = abs(desired_count - len(filtered_stocks))

        filtered_stocks = pd.concat([filtered_stocks,sorted_df[sorted_df['score']==half].iloc[:req_count, :]])
    
    return dict([(item['ticker'],[item['score'],item['total']]) for item  in json.loads(filtered_stocks.to_json(orient="records"))])
    
    

@app.route('/')
def index():
    return "Trend Indicator"


def fetch_data(t,interval="1h"):
    ticker = yf.Ticker(t)
    hourly_data = ticker.history(interval=interval, period='15d')
    hourly_data['ticker'] = [t]*len(hourly_data["Open"])
    return hourly_data


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
            
    score_df = pd.DataFrame(columns=['EMA5','EMA10','EMA20','EMA30','EMA50','EMA100','EMA150','EMA200',                                    'MA5','MA10','MA20','MA30','MA50','MA100','MA150','MA200'])
    
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


# In[ ]:




