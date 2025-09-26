from datetime import datetime
import yfinance as yf
import pandas as pd
def get_data(stock_symbol, start_date = None, end_date = None, period = None, frequency="1d"):
    ticker = yf.Ticker(stock_symbol)
    if period == None:
        financial_data = ticker.history(start = start_date, end = end_date, interval = frequency)
    else:
        financial_data = ticker.history(period = period, interval = frequency)
    financial_data.reset_index(names="Date", inplace=True)
    return financial_data

def clean_data(dataframe):
    dataframe["Date"] = [datetime.strptime(str(date).split(" ")[0], '%Y-%m-%d') for date in dataframe["Date"]]
    if "Dividends" in dataframe.columns:
        dataframe.drop(dataframe[~(dataframe["Dividends"] == 0.0)].index, inplace=True)
        dataframe.drop(columns=["Dividends"], inplace=True)
    if "Stock Splits" in dataframe.columns:
        dataframe.drop(columns=["Stock Splits"], inplace= True)
   
   # get Year and Week
    dataframe['Year'] = dataframe['Date'].dt.isocalendar().year
    dataframe['Week'] = dataframe['Date'].dt.isocalendar().week
    dataframe["Next_Open"] = dataframe["Open"].shift(-1)
    dataframe["Next_Date"] = dataframe["Date"].shift(-1)

    return dataframe

