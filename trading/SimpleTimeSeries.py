import pandas as pd
import numpy as np
from datetime import datetime,timedelta
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from fastcore.all import *

def get_momentum_actions(df, n_periods,threshold):
    _x = df.shift(n_periods)
    
    # Calculate percent change
    momentum_rate = df.apply(lambda x: (x-x.shift(n_periods))/x.shift(n_periods))[n_periods:]

    # Select Action Based on Threshold
    actions = pd.DataFrame(np.where(momentum_rate < -threshold, 'Short',
                           np.where(momentum_rate > threshold,  'Buy',
                                                                 '')),
                   columns=momentum_rate.columns,index=momentum_rate.index)
    
    # Because we use close price, we can't make the trade action until the following day
    actions.index = actions.index + timedelta(1)
    
    return actions

def get_momentum_regr_actions(df, n_periods,threshold):
    _x = df.shift(n_periods)
    
    # Calculate Momentum
    mom_window = df.rolling(n_periods)
    mom_rate = mom_window.apply(lambda y: LinearRegression().
                                    fit(np.array(range(n_periods)).
                                    reshape(-1, 1),y).coef_)
    mom_rate = mom_rate[n_periods:]
    
    # Select Action Based on Threshold
    actions = pd.DataFrame(np.where(mom_rate < -threshold, 'Short',
                           np.where(mom_rate > threshold,  'Buy',
                                                                 '')),
                   columns=mom_rate.columns,index=mom_rate.index)
    
    # Because we use close price, we can't make the trade action until the following day
    actions.index = actions.index + timedelta(1)
    
    return actions

def calculate_bollinger(df, tickers=['AAPL','MSFT'],window_sz=28,band_sz=2):
    out = {}

    for ticker in tickers:
        raw = df.loc[:,ticker] 
        
        # Calculate window statistics
        _mean = raw.rolling(window_sz).mean()
        _std = raw.rolling(window_sz).std()

        # Calculate bands based on window statistics
        upper_band = _mean + (band_sz*_std)
        lower_band = _mean - (band_sz*_std)
        
        # Combine in a dataframe
        _out = pd.concat([lower_band, raw, upper_band, ],axis=1)
        _out.columns = ['lower_band','raw','upper_band']
        _out['lower_limit'] = _out.raw < _out.lower_band
        _out['upper_limit'] = _out.raw > _out.upper_band

        out[ticker] = _out
    return out

def plot_bollinger(data,min_date,plt_cols=2):
    # Create Plot    
    rows = int(len(data.keys())/plt_cols)
    fig, ax = plt.subplots(rows,plt_cols,figsize=(20,8*rows))
    fig.suptitle("Bollinger Bands",fontsize=50)

    
    for i,(ticker,df) in enumerate(data.items()):
        # Determind plot location
        row_num = int(i / plt_cols) if len(data.keys()) > 2 else i
        col_num = i - (row_num * plt_cols)
        
        # Filter for dates
        _d = data[ticker].loc[df.index>=min_date]
        
        # Draw Plots
        if plt_cols >2: _tmp = ax[row_num,col_num]
        else: _tmp = ax[row_num]
        _tmp.set_title(ticker,fontsize=18)
        _tmp.plot(_d[['lower_band','raw','upper_band']])
        _tmp.scatter(_d[_d.lower_limit].index,_d[_d.lower_limit].raw,c='red')
        _tmp.scatter(_d[_d.upper_limit].index,_d[_d.upper_limit].raw,c='red')
        
def get_bollinger_actions(df,window_sz=28,band_sz=2):
    
    # Calculate Statistics
    bollinger_data = calculate_bollinger(df, tickers=df.columns,window_sz=window_sz,band_sz=band_sz)
    
    # Calculate Actions
    _d = L()
    for ticker,dataframe in bollinger_data.items():
        _d.append(pd.DataFrame(np.where(dataframe['lower_limit'] == True, 'Short',
                           np.where(dataframe['upper_limit'] == True,  'Buy',
                                                                 '')),
                   columns=[ticker],index=dataframe.index))
    bollinger_actions = pd.concat(_d,axis=1)
    
    # Because we use close price, we can't make the trade action until the following day
    bollinger_actions.index = bollinger_actions.index + timedelta(1)
    
    return bollinger_actions[window_sz:]
        