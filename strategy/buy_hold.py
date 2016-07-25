# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 12:34:22 2015

@author: Yibing
"""              
import pandas as pd  

class BuyHold(object):
    """Keep initial quantities constant.
    
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
        self.name = 'Buy_Hold'
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
            pd.read_csv(u'C:\\Users\\Yibing\\Documents\\Python\\back_test\\resampled_data\\%s.csv'%t,
                        index_col=0,
                        header=0,
                        parse_dates=True).to_csv(u'C:\\Users\\Yibing\\Documents\\Python\\back_test\\strategy\\data\\%s.csv'%t, 
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
        if self.status == 'EMPTY':
            num = len(self.data_handler.tickers)
            signal = 'ENTER', dict((t, 1./num) for t in self.data_handler.tickers)
            self.status = 'LONG'
            return signal
        else:
            return None            
    

if __name__ == '__main__':
    tickers = ['600030.SH']
    BuyHold.csv_processor(tickers)
                                    
                                    
