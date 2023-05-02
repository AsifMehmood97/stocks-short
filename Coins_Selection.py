#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
from flask import Flask
from flask import request
import pandas as pd
import io
from tqdm import tqdm
import requests
import json
from datetime import datetime
from datetime import timedelta
import os


# In[ ]:


app = Flask(__name__)

@app.route('/coins_selection',methods=["POST","GET"])
def watchlist():
    
    dataframe = pd.DataFrame(columns=['v','vw','o','c','h','l','t','n','ticker','change'])
    
    symbols = getSymbols()
    
    stocks_not_available = list()

    for i in tqdm(symbols[:500]):

        try:
            ticker = fetch_data(i)

            dataframe = dataframe.append(ticker, ignore_index=True)
                
        except:
            stocks_not_available.append(i)
    
    
    dataframe.columns = ['Volume','Volume Weighted','Open','Close','High','Low','Datetime','N','ticker','change']
    dataframe['Datetime'] = pd.to_datetime(dataframe['Datetime'], unit='ms')
    dataframe.index = dataframe['Datetime']
    dataframe = dataframe.drop(['Datetime'], axis=1)
    
    print(dataframe)
    
    dataframe.to_csv("coins.csv")
    
    return "List done"
    
    

@app.route('/')
def index():
    return "Trend Indicator"


def getSymbols():

    url = 'http://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt'
    response = requests.get(url)
    data = response.content.decode('utf-8')

    nasdaq_tickers = pd.read_csv(io.StringIO(data), delimiter='|')
    nasdaq_symbols = nasdaq_tickers['Symbol'].tolist()[:-1]
    
    return nasdaq_symbols


def fetch_data(symbol_ticker, time='1', span='day'):
    
    # get today's date
    today = datetime.today().date()
    date = today - timedelta(days=7)
    
    # format the date in YYYY-MM-DD format
    start_date = date.strftime('%Y-%m-%d')

    url = "https://api.polygon.io/v2/aggs/ticker/"+symbol_ticker+"/range/"+time+"/"+span+"/"+str(start_date)+"/"+str(today)+"?adjusted=true&sort=asc&limit=1000&apiKey=OZ9qMq2BGinATfiZlYwW2GZ7lh4uDR8U"
    
    response = requests.get(url)
    ticker = json.loads(response.text)
    
    ticker['results'][-1]['ticker'] = symbol_ticker
    
    ticker['results'][-1]['change'] = ((ticker['results'][-1]['c']-ticker['results'][-1]['o'])/ticker['results'][-1]['o'])*100
    
    return ticker['results'][-1]

if __name__ == '__main__':
    app.run(debug=True)