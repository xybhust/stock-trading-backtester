# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 12:39:47 2015

@author: Yibing
"""

class OrderHandler(object):
    """Receive signals and infer the number of shares to trade based on 
    relative weights.    
    """
    def __init__(self, data_handler, position_handler):
        self.data_handler = data_handler
        self.position_handler = position_handler

    def execute_order(self, signal):
        """Receive the relative weight and calculate the exact number of 
        shares to buy or sell. 
        
        Parameters
        ---------
        signal : tuple. (act, dictionary)
            act could be 'ENTER' or 'EXIT'
            For 'ENTER', dictionary has ticker and its weights against cash, where
            weight could be +/-, which stands for buy/sell.
            For 'EXIT', dictionary has ticker and exit ratio, which stands for
            how much position would be closed out.
            
        Returns
        -------
        execute : tuple. (type, transaction_cost, dictionary)
            type could be 'ENTER' and 'EXIT'
            transaction_cost is the total transaction cost.
            dictionary has ticker and weights 
            
        Notice
        ------
        Transaction cost is calculated only when entering the market.
        """
        transaction_rate = 0.00
        transaction_cost = 0. # cumulative
        weights = signal[1]
        qtys = {}
        
        if signal[0] == 'ENTER':
            # to enter market, we need to calculate how much money to allocate
            # to each stock and : qty = alloc / traded_price
            for k, w in weights.items():
                # get the price 
                price = self.data_handler.get_cursor_value(k, 'transaction')
                cash = self.position_handler.current_position['cash']
                alloc = cash * w
                qtys[k] = alloc / ((1.+transaction_rate)*price)
                transaction_cost += abs(qtys[k]*price)*transaction_rate
       
        elif signal[0] == 'EXIT':
            for k, w in weights.items():
                qtys[k] = w
                
        return signal[0], transaction_cost, qtys
    
