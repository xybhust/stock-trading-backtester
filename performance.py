# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 12:42:17 2015

@author: Yibing
"""
# performance.py
import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis
import matplotlib.pyplot as plt
import pprint

class Performance(object):
    """Visualize cumulative returns, as well as performance indicators
    
    Parameters
    ---------
    data_handler : instance
    position_handler : instance
    periods : int
        The number of intervals in one year. We assume:
        52 weeks in a year
        250 days in a year
        250 * 4 hours 
        250 * 4 * 60 minutes
        250 * 4 * 60 * 60 seconds
        For example, if you are researching a 5-min strategy, then the 
        periods should be 250 * 4 * 12.
    name : string
        Unique identifier of the stragegy    
        
    Attributes
    ----------
    returns : pd.Series
    cumulative_returns : pd.Series
    benchmark_rturns : dictionary of pd.Series
    benchmark_cumulative_returns: dictionary of pd.Series
    excess_returns : dictionary of pd.Series
      (returns - benchmark_returns)
    periods : int
    strategy_name : string
    """
    def __init__(self, data_handler, position_record, periods, name):
        
        self.returns = position_record['total'].pct_change()
        self.returns[0] = 0.
        self.cumulative_returns = (1.0 + self.returns).cumprod()
        
        self.benchmark_returns = dict((b, s.pct_change()) for b, s in 
            data_handler.benchmarks.items())
        # pct_change() will cause the first element to be nan, set it to zero
        for b in self.benchmark_returns.keys():
            self.benchmark_returns[b][0] = 0.
        
        self.benchmark_cumulative_returns = dict((b, (1. + s).cumprod()) for 
            b, s in self.benchmark_returns.items())
        
        # calculate excess returns over each benchmark
        self.excess_returns = {}
        for b, s in self.benchmark_returns.items():
            assert (self.returns.index == s.index).all()
            self.excess_returns[b] = self.returns - s
        
        self.periods = periods
        self.strategy_name = name
        
    @staticmethod
    def mean_return(returns, periods):
        """
        annual return.
        """
        return np.mean(returns)*periods

    @staticmethod        
    def volatility(returns, periods):
        """
        annual volatility
        """
        return np.std(returns, ddof=1)*np.sqrt(periods)

    @staticmethod        
    def sharpe_ratio(returns, risk_free, periods):
        """
        Create the Sharpe ratio for the strategy, based on a zero
        benchmark.
        
        @Parameters:
        returns - A pandas Series representing period percentage returns.
        """
        return (Performance.mean_return(returns, periods) - risk_free) / \
            Performance.volatility(returns, periods)

    @staticmethod    
    def downside_deviation(returns, periods):
        """
        sqrt(sum{r_t < 0}(r_t^2 / T))
        """
        neg_returns = returns[returns < 0]
        return np.sqrt(sum([r ** 2 for r in neg_returns]) / len(returns)) * \
            np.sqrt(periods)

    @staticmethod       
    def sortino_ratio(returns, periods):
        """
        @Parameter:
        returns - Pandas series.
        """
        return Performance.mean_return(returns, periods) / \
            Performance.downside_deviation(returns, periods)

    @staticmethod    
    def risk_adjusted_return(returns, periods):
        """
        mean - lambda * volatility. Useful for negative returns.
        2.33 - 99%
        """
        return Performance.mean_return(returns, periods) - \
            2.33*Performance.volatility(returns, periods)

    @staticmethod    
    def max_drawdown(cumulative_returns):
        """
        maximal loss before a new peak is formed.
        @return (through_value - peak_value) / peak_value
        """
        peak_idx, low_idx = 0, 0
        max_drawdown = 0.
        for i, cr in enumerate(cumulative_returns):
            if cr < cumulative_returns.iloc[low_idx]:
                low_idx = i
            elif cr > cumulative_returns.iloc[peak_idx]:
                prev_peak = cumulative_returns.iloc[peak_idx]
                prev_low = cumulative_returns.iloc[low_idx]
                if (prev_low - prev_peak) / prev_peak < max_drawdown:
                    max_drawdown = (prev_low - prev_peak) / prev_peak
                # reset peak and low index
                peak_idx, low_idx = i, i
            # if no peak is formed again, calculate max drawdown
            prev_peak = cumulative_returns.iloc[peak_idx]
            prev_low = cumulative_returns.iloc[low_idx]
            if (prev_low - prev_peak) / prev_peak < max_drawdown:
                max_drawdown = (prev_low - prev_peak) / prev_peak
                
        return max_drawdown
                
            
    def create_performance(self):
        """
        @Return:
            annualized return, downside_deviation, sharpe_ratio, sortino ratio
        """
        num = len(self.returns)
        strategy_return = (self.cumulative_returns.iloc[-1] ** (1./num) - 1) * self.periods
        sigma = Performance.volatility(self.returns, self.periods)
        downside = Performance.downside_deviation(self.returns, self.periods)
        max_down = Performance.max_drawdown(self.cumulative_returns)
        sharpe = Performance.sharpe_ratio(self.returns, 0.0, self.periods)
        sortino = Performance.sortino_ratio(self.returns, self.periods)
        RaR = Performance.risk_adjusted_return(self.returns, self.periods)
        skewness = skew(self.returns, bias=False)
        kurt = kurtosis(self.returns, bias=False)
        
        return (strategy_return, sigma, downside, max_down, sharpe, sortino, RaR, 
                skewness, kurt)
        
        
    def output_performance(self):
        """
        Creates a list of summary statistics for the portfolio.
        """
        print("Creating summary stats...")    
        strategy_return, strategy_sigma, downside, max_down, sharpe, sortino, RaR, \
           skewness, kurt = self.create_performance()
            
        stats = [
                ("Strategy Return: %0.2f%%" % (strategy_return * 100,)),
                ("Strategy Volatility: %0.4f" % strategy_sigma),
                ("Risk Adjusted Return: %0.2f%%" % (RaR * 100.,)),
                ("Downside Deviation: %0.4f" % downside),
                ("Maximal Drawdown: %0.2f%%" % (max_down * 100.,)),
                ("Sharpe Ratio: %0.2f" % (sharpe,)),
                ("Sortino Ratio: %0.2f" % (sortino,)),
                ("Skewness: %0.4f" % (skewness,)),
                ("Kurtosis: %0.4f" % (kurt,))
                ]
        num_of_benchmark = len(self.benchmark_returns)
        fig, axes = plt.subplots(1 + num_of_benchmark, sharex=True)
        axes[0].plot(self.cumulative_returns.index, 
                     self.cumulative_returns, 
                     label=self.strategy_name)
        axes[0].set_ylabel('Cumulative Return')
        axes[0].set_title('Performance against the benchmark')
        for b, s in self.benchmark_cumulative_returns.items():
            axes[0].plot(s.index,
                         s,
                         label='Benchmark: %s' % b)
        axes[0].legend(loc='best', bbox_to_anchor=(1, 1))
        axes[0].grid(True)
     #   plt.legend(loc='best')

        
        # plot excess return, this runs VERY SLOW, uncomment below if needed
        # ------------------------------------------------------------------
        index = self.returns.index
        for i, item in enumerate(self.excess_returns.items()):
            axes[i+1].vlines(index, 0., item[1], color='red', 
                             label='Excess returns over %s' % item[0])
            axes[i+1].axhline(y=0., ls='dotted', color='k')
            axes[i+1].legend(loc='best')
            axes[i+1].grid(True)
        fig.subplots_adjust(hspace=0)
        fig.show()

        pprint.pprint(stats)
        
