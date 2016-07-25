# -*- coding: utf-8 -*-
"""
Created on Sun Sep 13 23:58:46 2015

@author: Yibing
"""
import pandas as pd
from copy import copy            

class CSVDataHandler(object):
    """This is the most common type of datahandler, the csv file contains 
    the market information (OHLVC) as well as all the information you might
    need to backtest the trading strategies.

    Parameters
    ----------
    tickers : array-like
        Represents different stocks, also the name of the file.
    benchmarks : list of string
        The close price of the benchmark index along the time.
    
    Attributes
    ----------
    benchmarks : Dictionary, (ticker: pd.Series)
        Close price along the index. Could be multiple benchmarks
    historical_data : Dictionay, (ticker: pd.DataFrame) 
        Each DataFrame stores generators of each row (data of each date). 
    recent_data : Dictionary of list
        Each list stores most recent bars with the latest at the end. 
    index : pandas index object
        Datetime of each row.
    columns : List of strings
        Labels of each feature   
    
    Example:
    -------
    If you want to test the simple moving average crossover strategy, then 
    the csv file must also contain the short term and long term average price, 
    which is necessary in the trading decision making.
    
    Notice:
    -------
    The first column must be datetime, the multiple files must have the same
    index and the same column names, or it might cause assertion error.
    

    """
    def __init__(self, tickers, benchmarks):
        self.tickers = tickers
        self.benchmarks = {}
        self.historical_data = {}
        ##################
        # Importing data #
        ##################        
        for i, s in enumerate(self.tickers):
            self.historical_data[s] = pd.read_csv(u'C:\\Users\\Yibing\\Documents\\Python\\back_test\\strategy\\data\\%s.csv'%s, 
                                                  index_col=0,
                                                  parse_dates=True)
                                                 
            # double check whether the indeces of multipe files are matched                                     
            assert (self.historical_data[s].index == \
                self.historical_data[tickers[0]].index).all(), 'index not match'
            assert (self.historical_data[s].columns == \
                self.historical_data[tickers[0]].columns).all(), 'columns not match'
                
            print('Successfully loaded %s' % (s,))
        print('\n')

        self.index = self.historical_data[tickers[0]].index
        self.columns = self.historical_data[tickers[0]].columns
        
        for b in benchmarks:
            self.benchmarks[b] = pd.read_csv(u'C:\\Users\\Yibing\\Documents\\Python\\back_test\\resampled_data\\%s.csv'%b, 
                                             index_col=0,
                                             parse_dates=True).reindex(index=self.index).close
            print('Successfully loaded %s' % (b,))
        print('\n')

        self.cursor = 0
        self.length = len(self.index)
    
    def get_datetime(self):
        return copy(self.index[self.cursor])
        
    def get_cursor_value(self, ticker, label):
        return copy(self.historical_data[ticker].ix[self.cursor, label])
 
# Just for testing         
if __name__ == '__main__':
    tickers = ['600030.SH'] 
    benchmark = ['600030.SH']                               
    datahandler = CSVDataHandler(tickers, benchmark)
    d = datahandler.get_datetime()
   