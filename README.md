# Stock-trading backtester
Version:  Python 2.7 (Compatible with Python 3) 

Author:   Yibing Xie 

Contact:  xybhust@gmail.com 

Features
--------
1. Support short selling
2. Support multi-asset strategies
3. Support stepwise adding or reducing positions
4. Support user-defined strategies with friendly interface
5. Support multiple benchmarking
6. Performance visualization 


Assumptions
-----------
1. Each order is executed with certainty.
2. The transaction price is the open price at the next period which follows 
   the period when the signal is released.
3. Commision fee is charged only at opening positions at a rate of 0.0015.
4. No transfer-out or transfer-in money.
5. For short selling, the margin rate is 100%. For example, if you short a 
   stock at $100 for 100 shares, then the cost would be $10,000.
6. For stepwise adding positions, sell it proportionally when 
   closing out positions. e.g. First buy 10 shares for $100, then buy 5 shares
   for $150, later we sell 6 shares. I assume the 6 shares is a weighted mix
   of the previous shares, which consists of 4 shares from $100 and 2 shares
   from $150.


Limitations
-----------
1. Only one strategy at a time. e.g. You can't combine pairs-trading strategy with moving average crossover strategy.
2. Only support market order, no limit order and stop-loss order. (You need to define stop-loss actions in your strategy class.)


Data
----
The data pipeline in the backtest follows three steps:
  1. Define your own functions to resample the raw tick data 
  2. Calculate necessary features required by each strategy
  3. Feed the complete data to the DataHandler and start backtest


Files
-----
The files in `tick_data` directory are the original raw data, which consists of
transaction records at second level. You are supposed to output the new
resampled file and put it into the resampled_data directory. However, If you 
already have data at desired frequency (this is what resample means), say, you
collect daily data from Yahoo finance api, then you can skip the first step 
and put them straight into the resampled_data directory. Keep in mind that 
`transaction` and `close` are two required columns in order to make the 
components running free of troubles.

The files in resampled_data directory contains necessary market information,
which will be read by the strategy class and the output file will be stored
in the `strategy/data` directory.

The files in `strategy/data` directory are files processed by a specific strategy,
which will be read by the DataHandler class. 


Instructions
------------
First you need to define your own functions to preprocess the raw tick data,
which should return the resampled csv file with datetime as index. And the 
two MUST-HAVE columns are `transaction` and `close` as mentioned above.

`resample_tick_data.py` is just my own example. Name the new file after the 
tick file, eg. `600030.SH.csv` and put it into the `strategy/data` directory. 
I didn't want to integrate this functionality into the Backtest class because 
different tick files might have different time index, however, the DataHandler 
class requires each file have exactly the same indices. Therefore, you need to
doublecheck manually to ensure the data feeding to the DataHandler class come 
up to standard.

With everything ready, run the `backtest.py` to conduct backtest. Just run it 
and the figures will pop up automatically.

To research a new strategy, simply create your own strategy class, which MUST 
implemente the following two method
```python
@staticmethod 
csv_processor(tickers)
```
and
```python
generate_signal()
```

The files `buy and hold` and `simple moving average cross` are two examples. 
The return type of the user-defined methods should follow the patterns of the 
examples. All you need to do is to copy and modified it.


Important settings
------------------
Don't forget to modify the absolute path in the DataHandler
class as well as the strategy class.

Also, the Performance class expects the `periods` as the argument, which is an int number 
representing the number of intervals in one year. I assume:
  * 52 weeks in a year
  * 250 days in a year
  * 250 * 4 hours in a year
  * 250 * 4 * 60 minutes in a year
  * 250 * 4 * 60 * 60 seconds in a year

For example, if you are researching a 5-min strategy, then the periods should
be 250 * 4 * 12.

If you follow my steps correctly, you are expected to see exactly the same
graphs and results as I do.


Sample graphs
-------------
![Sample](https://raw.githubusercontent.com/xybhust/stock-trading-backtester/master/images/figure_1.png)


Advice is greatly appreciated. 


Future improvements
-------------------
1. Consider bilateral transaction fees
2. Support multiple signal at one unit of time. e.g. Close out a position and enter a opposite position immediately.
3. Support limit order and stop-loss order. (Currently the stop-loss action is defined by the strategy class)

