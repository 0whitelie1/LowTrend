from pandas_datareader import data as pdr
from datetime import date, timedelta
import yfinance as yf
import pandas as pd
import numpy as np


today = date.today() + timedelta(1)
start_date= "2010-01-01"


end_date= today.strftime("%Y-%m-%d")


def getData(ticker):
    # ticker = "DURDO.IS"
    # yf_hisse = yf.Ticker(ticker)
    # data = yf_hisse.history(interval="1d", start=start_date, end=end_date, auto_adjust=False)
    data = yf.download(ticker, start=start_date, end=end_date)
    dataname= ticker.split(".")
    data.to_csv("./data/yahoo/"+dataname[0]+".IS.csv")


    
bist_list = np.genfromtxt('./data/sp500.txt', delimiter=";", unpack=True, dtype=None, encoding=None)
len_of_bist_list: int = len(bist_list[0])

for i in range(len_of_bist_list):
    symbol = bist_list[0][i]+".IS"
    getData(symbol)


input("finished ...")
