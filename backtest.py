# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 17:15:30 2015

@author: Yibing
"""
import pandas as pd

from data_handler import CSVDataHandler
from order_handler import OrderHandler
from position_handler import PositionHandler
from performance import Performance
from strategy.buy_hold import BuyHold
from strategy.sma_cross import MovingAverage


class Backtest(object):
    """Enscapsulates the settings and components for carrying out
    an event-driven backtest. 
    
    Parameters
    ----------
    tickers : list of string
    benchmarks : list of string
    intial_capital : float
    data_handler_cls : (Class) 
        Handles the market data feed.
    order_handler_cls : (Class) 
        Keeps track of current and prior positions.
    strategy_cls : (Class) 
        Generates signals based on market data.
    
    Attributes
    ----------
    tickers : list
    data_handler : instance
    position_handler : instance
    order_handler : instance
    stragegy : instance
    transactions : int
    """
    def __init__(
            self, tickers, benchmarks, initial_capital,
           data_handler_cls, position_handler_cls, order_handler_cls, 
           strategy_cls, performance_cls
        ): 

        strategy_cls.csv_processor(tickers)
        
        self.data_handler = data_handler_cls(tickers, benchmarks)
        
        self.position_handler = position_handler_cls(self.data_handler,
                                                     initial_capital)
                                                     
        self.order_handler = order_handler_cls(self.data_handler,
                                               self.position_handler)
                                               
        self.strategy = strategy_cls(self.data_handler, self.position_handler)
        
        self.performance_cls = performance_cls
        self.transactions = 0

        
    def simulate_trading(self):
        """Executes the backtest.
        """
        # loop over each rows to backtest your strategy!
        for _ in range(self.data_handler.length):
 
            # update positions based on newst data
            self.position_handler.update_from_market()
            

            # generate signals based on newest data
            signal = self.strategy.generate_signal()
            
            if signal: 
                # in this naive backtester, I assume every order will be
                # executed for sure               
                execute = self.order_handler.execute_order(signal)
                # update position from orders and newest market price
                self.position_handler.update_from_order(execute)
                self.transactions += 1            
          
            # push the account balance
            self.position_handler.add_one_record()
            
            if self.position_handler.current_position['total'] < 0:
                print('Bankruptcy! GAME OVER')
                break
            
            self.data_handler.cursor += 1
            
        print('Number of transactions: %d' % self.transactions)
        print('\n')
        
        self.position_record = pd.DataFrame(self.position_handler.historical_position)
        self.position_record.set_index('datetime', inplace=True)
#        52 weeks in a year
#        250 days in a year
#        250 * 4 hours 
#        250 * 4 * 60 minutes
#        250 * 4 * 60 * 60 seconds
        periods = 250 * 4 * 12.
        self.performance = self.performance_cls(self.data_handler,
                                                self.position_record, 
                                                periods,
                                                self.strategy.name)
        self.performance.output_performance()
        
if __name__ == '__main__':
    tickers = ['600030.SH']
    benchmarks = ['600030.SH']
    initial_capital = 100.
    b = Backtest(tickers, benchmarks, initial_capital, CSVDataHandler, 
                 PositionHandler, OrderHandler, MovingAverage, Performance)
    b.simulate_trading()
    r = b.position_record
   
