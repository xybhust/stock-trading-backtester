# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 10:43:36 2016

@author: Yibing
"""
from copy import deepcopy, copy
import numpy as np

class PositionHandler(object):
    """PositionHandler object handles account balances and support both
    long and short position. However, it does NOT support margin transaction
    by far. More importantly, it does NOT allow cumulative orders, which means 
    all the buying and selling actions will be finished at once.
    
    Parameters
    ----------
    data_handler : DataHandler object.
    initial_capital : float
    
    Attributes
    ----------
    tickers : list
    historical_position : list of dictionaries
        The elements are current_posisions at each time.
    current_position : dictionary
        The first type of items are (tickers, 1d array).
        ------------------------------------------------
        The 1d array is [quantity, market_price, cost, avg_cost,
        market_value, unrealized_pnl, realizable_value], where
        0. quantity could be +/-
        1. market_price is the price up-to-date
        2. cost = abs(quantity * initial_price), always positive
        3. avg_cost = cost / num_of_shares
        4. market_value could be +/-, which = (quantity * market_price)
        5. unrealized_pnl is calculated as follows:
            for long position: = mkt_value - cost
            for short position:= mkt_value + cost
        6. realizable_value = cost + unrealized_pnl
        ----------------------------------------
        The second type of items are {'cash':float} and {'total': float}, where
        total = cash + sum(realizable_value)                                     
    """
    def __init__(self, data_handler, initial_capital): 
        self.data_handler = data_handler
        self.initial_capital = initial_capital
        self.tickers = self.data_handler.tickers
        self.historical_position = []
        
        self.current_position = dict((s, np.zeros(7)) for s in self.tickers)
        self.current_position['cash'] = self.initial_capital
        self.current_position['total'] = self.initial_capital
      
    def update_from_market(self):
        """Every time new market data is looped over, 
        the portfolio must update the current market value of all the 
        positions held. This function is executed before any transactions.
        """ 
        # Update position for new market bar
        total_realizable_value = 0.
        
        for s in self.tickers:
            if self.current_position[s][0] == 0.:
                continue;
            
            price = self.data_handler.get_cursor_value(s, 'close')
            # Approximation to the real value
            mkt_value = self.current_position[s][0] * price
            self.current_position[s][1] = price
            self.current_position[s][4] = mkt_value
            
            # different methods to cal pnl between long and short sale
            # long position: 
            # unrealized_pnl = mkt_value - cost
            # short position:
            # unrealized_pnl = mkt_value + cost
            d = -1. if self.current_position[s][0] > 0. else 1.
            
            self.current_position[s][5] = mkt_value + \
                d*self.current_position[s][2]
                    
            # realizable_value = cost + unrealized
            self.current_position[s][6] = \
                self.current_position[s][2] + self.current_position[s][5]
                
            # calculate total realizable value    
            total_realizable_value += self.current_position[s][6]
                        
        # end loop, calculate balance
        self.current_position['total'] = self.current_position['cash'] + \
            + total_realizable_value
                 
    def update_from_order(self, execute):
        """Takes a signal object and updates the holdings matrix to
        reflect the holdings value.
        
        Parameters
        ----------
        execute : tuple. (transaction_cost, dictionary)
            transaction_cost is the total transaction cost
            dictionary has ticker and quantity
        """
        signal_type = execute[0]
        transaction_cost = execute[1]
        qtys = execute[2]
        total_realizable_value = 0.
        for k, q in qtys.items():
            if q == 0.:
                continue
            # keep track of old numbers
            old_qty = self.current_position[k][0]
            old_cost = self.current_position[k][2]
            signed_old_cost = old_cost if old_qty > 0 else -old_cost
            
            new_qty = old_qty + q
            price = self.data_handler.get_cursor_value(k, 'transaction')
            if round(new_qty, 3) == 0.:
                # set all values to zero
                self.current_position['cash'] += self.current_position[k][6]
                self.current_position[k] = np.zeros(7)
                
            elif signal_type == 'ENTER':
                new_cost = abs(signed_old_cost + q*price)
                self.current_position[k][0] = new_qty
                self.current_position[k][1] = price
                self.current_position[k][2] = new_cost
                self.current_position[k][3] = new_cost / new_qty
                self.current_position[k][4] = price * new_qty
                if new_qty > 0:
                    self.current_position[k][5] = price*new_qty - new_cost
                else:
                    self.current_position[k][5] = price*new_qty + new_cost
                self.current_position[k][6] = new_cost + self.current_position[k][5]
                self.current_position['cash'] -= abs(q*price)
            
            elif signal_type == 'EXIT':
                ratio = q
                self.current_position['cash'] += (self.current_position[k][6]
                    * ratio)
                self.current_position[k][[0,2,4,5,6]] *= (1 - ratio)

                    
            total_realizable_value += self.current_position[k][6]
            
        self.current_position['cash'] -= transaction_cost
        self.current_position['total'] = self.current_position['cash'] + \
            total_realizable_value
    
    def add_one_record(self):
        # Add a new record to all positions
        datetime = deepcopy(self.data_handler.index[self.data_handler.cursor])
        new_position = deepcopy(self.current_position)
        new_position['datetime'] =  datetime # Current time
        
        self.historical_position.append(new_position)
        
               