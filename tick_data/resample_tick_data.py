# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 11:18:42 2016

@author: Yibing
"""
import pandas as pd
import numpy as np
import datetime

column_names = "time,price,quantity,amount,num,side,volume,turnover,ask_price,ask_qty,bid_price,bid_qty,ask_avg_price,bid_avg_price,total_ask_qty,total_bid_qty".split(",")

def clean_raw_data(file_name):
    """First step to preprocess the raw data, delete rows which are irrelevant
    and reset the index as timestamp
    
    Parameters
    ----------
    file_name : string
        full path of the data file
    
    Returns
    -------
    Dataframe 
    
    """
#    def parser(date):
#        return datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
        
    df = pd.read_csv(file_name, index_col=0, names=column_names, 
                     parse_dates=['time'])
                     
    # some of the indices might be wrong since they contain seconds larger than 60,
    # therefore, we need to ensure the indices fall into the right range
    qualified_index = map(lambda x: ((x.split(' ')[1] >= '0930') & (x.split(' ')[1] <= '1130')) | \
                             ((x.split(' ')[1] >= '1300') & (x.split(' ')[1] <= '1500')),
                             df.index)
                             
    # eliminate possible duplicate indices
    df = df[qualified_index].reset_index().drop_duplicates(subset='time', keep='first').set_index('time')
    converted_index = map(lambda x: pd.datetime(year=int(x.split(' ')[0][:4]),
                                               month=int(x.split(' ')[0][4:6]),
                                               day=int(x.split(' ')[0][6:]),
                                               hour=int(x.split(' ')[1][:2]),
                                               minute=int(x.split(' ')[1][2:4]),
                                               second=int(x.split(' ')[1][4:6]),
                                               microsecond=int(x.split(' ')[1][6:])),
                         df.index)
#    converted_index = map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f'),
#                          df.index)
    return pd.DataFrame(df.values, columns=column_names[1:], index=converted_index)
    

def resample(raw_df, freq):
    """Resample the original tick data given frequency and calculate essential
    figures which includes:
        open : the price where the first transaction take place during the interval
        high : highest price during the interval
        low : lowest price during the interval
        close : the price where the last transaction take place during the interval
        ewap : equal weighted average price during the interval
        quantity : quantity of transactions during the interval
        amount : amount of transactions during the interval
        vwap : volume weighted average price
        transaction : price at which transaction actually occurs, 
            approximated by the open price at the next period
    """
    ohlc = raw_df['price'].resample(freq, closed='left', label='right').ohlc().dropna()
    ewap = raw_df['price'].resample(freq, closed='left', label='right').mean().dropna()
    ewap.name = 'ewap'
    qty_amt = raw_df.loc[:, ['quantity', 'amount']].resample(
        freq, closed='left', label='right').sum().dropna()
    vwap = qty_amt['amount'] / qty_amt['quantity']
    vwap.name = 'vwap'
    transaction = ohlc['open'].shift(-1).dropna()
    transaction.name = 'transaction'
    concat = pd.concat([ohlc, ewap, vwap, transaction, qty_amt], axis=1,
                       join='inner')
    concat['date'] = concat.index

    return concat.dropna()

if __name__ == '__main__':
    df = clean_raw_data('stocks/600030.SH.csv')
    resampled_df = resample(df, '5min')
    
