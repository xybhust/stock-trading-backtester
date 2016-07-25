# -*- coding: utf-8 -*-
"""
Created on Sat Jul 23 17:14:32 2016

@author: Yibing
"""
import pandas as pd

class MovingAverage(object):
    """Simple moving average crossover strategy. Buy it if the short-term
    moving average cross the long-term moving average from below. Sell it
    if crossing from above. Short selling is not allowed.
    
    Parameters
    ----------
    data_handler : cls obj
    position_handler : cls obj
    
    Attributes
    ----------
    name : string
        unique identifier of the strategy
    status : string
        'EMPTY', 'LONG'  
    """
    def __init__(self, data_handler, position_handler):
        self.data_handler = data_handler
        self.position_handler = position_handler
        self.name = 'Simple_Moving_Average'
        self.status = 'EMPTY'

    
    @staticmethod
    def csv_processor(tickers):
        """Preprocess the raw csv files to obtain necessary features and save
        the new file to the folder
        
        Parameters
        ----------
        tickers : list
            Name of raw files.
        """
        for t in tickers:
            df = pd.read_csv(u'C:\\Users\\Yibing\\Documents\\Python\\back_test\\resampled_data\\%s.csv'%t,
                             index_col=0,
                             header=0,
                             parse_dates=True)
            df['MA-short'] = pd.rolling_mean(df['close'], window=10)
            df['MA-long'] = pd.rolling_mean(df['close'], window=30)
   
            df.dropna().to_csv(u'C:\\Users\\Yibing\\Documents\\Python\\back_test\\strategy\\data\\%s.csv'%t, 
                                                     index_label='datetime')

    def generate_signal(self):
        """Generate buy signal at the beginning and do not do anything later.
        
        Returns
        -------
        signal : tuple. (act, dictionary)
            act could be 'ENTER' or 'EXIT'
            For 'ENTER', dictionary has ticker and its weights against cash, where
            weight could be +/-, which stands for buy/sell.
            For 'EXIT', dictionary has ticker and exit ratio, which stands for
            how much position would be closed out.
        
        Examples
        --------
        Buy one stock with full cash availabe, 
        then the signal would be : 'ENTER', {ticker: 1.}
        
        Buy one stock with half amount of cash available,
        then the signal would be : 'ENTER', {ticker: 0.5}
        
        Buy two stocks with equal weight,
        then the signal would be : 'ENTER', {ticker1: 0.5, ticker2: 0.5}
        
        Buy one stock and sell another stock of the same amount,
        then the signal would be : 'ENTER', {ticker1: 0.5, ticker2: -0.5}
        
        Close out 30% of current position:
        then the signal would be : 'EXIT', {ticker1: 0.3, ticker2: 0.3}
        
        Close out full position:
        then the signal would be : 'EXIT', {ticker1: 1., ticker2: 1.}
        """
        # This is a single stock strategy
        assert len(self.data_handler.tickers) == 1, 'Too many stocks'
        ticker = self.data_handler.tickers[0]
        short = self.data_handler.get_cursor_value(ticker, 'MA-short')
        long_ = self.data_handler.get_cursor_value(ticker, 'MA-long')
        
        if (self.status == 'EMPTY') and short > long_:
            signal = 'ENTER', {ticker: 1.}
            self.status = 'LONG'
            self.recent_action_cursor = self.data_handler.cursor
            return signal
    
        elif (self.status == 'LONG') and short < long_:
            signal = 'EXIT', {ticker: 1.}
            self.status = 'EMPTY'
            return signal
            
        else:
            return None
        
            

                                    
            
