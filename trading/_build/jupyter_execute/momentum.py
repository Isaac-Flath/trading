#!/usr/bin/env python
# coding: utf-8

# # Momentum

# In[1]:


from fastcore.all import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# In[2]:


path = Path('../data')


# ## Overview

# In this article we will discuss basic windows for stock prices and test different methodologies for using them to make buy/sell decisions.  This is intended to be a first step in exploring quant trading and not a full fledged strategy or discussion of all apects of trading.  I hope that after reading this you will walk away understanding:
# 
# + What good minimal example of a trading strategy could look like that we can build ontop of
# + How to take a concept/idea and understand what the tunable parameters/levers are
# + What are the most important things that should be top of mind when testing an approach
# 
# There are many more concepts not covered in this article that are absolutely crucial to being a successful quant.  Future articles will cover many of those concepts, but I think this will be an interesting and informative first step!

# ## Intuition

# ### Importance

# Before diving into the technical bits, it is *always* a good idea to take the time to think about things at a high level and why your idea might work.  We can generate ideas *much* faster than we can code and test them, so we need to use intuition and experience to help guide us in which ideas we want to prioritize.  Intuition is important and where I start - but intuition is not reliable enough on it's own - we **must** then turn intuition into code with rigorous testing before we can decide whether to implement the strategy.  Every chapter will start with this.

# ### Belief

# I believe how a company is doing over the last month can be used to predict how how well it will do in the future.  This isn't much of a leap, but let's think about a few reasons as to why this may be true.
# 
# + **Available Capital:** If a company is doing well, it typically means they have more profit.  More profit means more that can be reinvested.  More reinvestment can mean faster growth.
# 
# + **Economies of Scale:** Often the more successful a company is the more they can drive down cost in some areas.  For example, General Mills can buy sugar at a lower price than a small business due to their buying power.  As buying power increase, they can leverage that to drive down costs.
#     
# + **Brand Recognition:** The more successful a business is and the larger it grows, the more brand recognition it has.  The more brand recognition it has the more it can leverage it's brand to grow.

# ### Hypothesis

# The *hypothesis* for this chapter is that recent stock performance can be used on its own to predict future stock performance.  Regardless of how much we believe that to be true, we should not trade based on this belief until we have evidence.  This chapter will explore several options for using this hypothesis to make trades, and give a foundation in how we may test and determine whether this is an idea worth keeping.

# ## The Data

# ### Load data

# First let's take a look at the data we will be using and talk a bit about it.  We can load it in with pandas.

# In[3]:


raw = pd.read_csv(path/'eod-quotemedia.csv',parse_dates=['date'])
raw.head(3)


# :::{note} A ticker is a symbol associated with a company.  For example Apple has the ticker `AAPL`.  To buy shares in Apple you would buy `AAPL`.

# We have a dataframe that contains the `adjusted close price` for each day for each ticker in our universe.  After every transaction, the price of a stock changes slightly.  The `adjusted close price` is the last stock price of the day.  While this is not as detailed as having the price at a more granular level (second, minute, hour, etc.), called `tick` data, we can use daily close price to test many types of strategies.

# A good first step is to use pandas' describe method.  As we do this we see a few good pieces of information to keep in mind:
# + Overall size of dataset - 409K rows
# + Very big range in values (~1 - ~1K), which most of them before $100

# In[4]:


raw.describe().transpose()


# ### Null Values

# Let's take a look and make sure we don't have any null values to handle.  This is one of those things you should do with every dataset.  This is a great opportunity to show how you can add in simple tests into your code as you go, which will help you catch issues as you iterate and change things.

# In[5]:


assert np.array([o==0 for o in raw.isnull().sum()]).all() == True


# We also want to take a quick look at the non numberic columns to get an idea of what time frame we have and how many tickers.  This is often known from the dataset, but it is good practice to look at the dataset and ensure that your understanding of the dataset aligns with what you see in the data. 

# In[6]:


print(f"Date column contains dates from {raw.date.min().date()} to {raw.date.max().date()}")


# ### Lookahead bias

# Let's see if all tickers in the dataset have the same start and end date.

# In[7]:


ticker_cnt = len(raw.ticker.unique())

_min = raw[['ticker','date']].groupby('ticker').min()
_min = _min[_min.date != '2013-07-01'].count().date

_max = raw[['ticker','date']].groupby('ticker').max()
_max = _max[_max.date != '2017-06-30'].count().date

print(f'''Out of {ticker_cnt} tickers:
  + 20 do do not start on 2013-07-01
  + 0 do not have an entry for 2017-06-30.''')


# Ok good thing we checked!  Let's think through what these data points mean:
# + Not all the tickers have the same start date.  This makes some intuitive sense because some of the companies may not have been founded until after the start date of the dataset.  They also may not have fit the criteria for the ticker universe (ie too small) until after the start date.
# + All of the tickers have an entry for 2017-06-30.  While it's not definitive proof of an issue, it is cause for concern.  This dataset may have a lookahead bias built in.

# :::{note} Investopedia says "Look-ahead bias occurs by using information or data in a study or simulation that would not have been known or available during the period being analyzed."

# The fact that every ticker still has a close price on the last day, means that as of the end of the dataset none of the companies in the dataset went out of business or were taken private.  A common reason this occurs in datasets is when a dataset is defined using future information.
# 
# For example if I look at the S&P 500 companies today and build a dataset of their stock prices over the last 5 years, every model I build will show better results than in reality.  By setting up the dataset using what is known on the last day of the period (all active S&P 500 companies), we are filtering out all companies that were in the S&P 500 but performed poorly they dropped out of the S&P 500.  We used our knowledge from today to create a historical dataset, which created bias.
# 
# When we see all tickers in the universe have a stock price on the last day, it's important to verify that this did not happen in your dataset.  When we talk about testing later, we will talk about how we can test to ensure we have accurate results.

# ### Reformat

# Now that we have an basic idea of what's in our data we can reformat it to a format that will be easier to use for analysis.  For what we are doing we will be applying things based on ticker, so let's give each ticker it's own column.

# In[8]:


df = raw.pivot(index='date', columns='ticker',values='adj_close')
df.iloc[:,:5].head(3)


# We can use the same describe as above to see statistics about each ticker.

# In[9]:


df.iloc[:,:5].describe()


# ## Models

# ### Basic Momentum

# ### Regression Momentum

# ### Bollinger Band

# The idea of a bollinger band is to use a rolling standard deviation to determine when the stock price is unusually high or low.  In theory if the price is doing something unexpected we can capitalize on that.
# 
# Let's walk through graphing this on a few tickers so we understand what's going on.  Then we can test some strategies using this concept and see how they perform on this dataset.

# In[10]:


def calculate_bollinger(df, tickers=['AAPL','MSFT'],window_sz=28,band_sz=2):
    out = {}
    for ticker in tickers:
        raw = df.loc[:,ticker] 
        _mean = raw.rolling(window_sz).mean()
        _std = raw.rolling(window_sz).std()

        upper_band = _mean + (band_sz*_std) 
        lower_band = _mean - (band_sz*_std)
        
        _out = pd.concat([lower_band, raw, upper_band, ],axis=1)
        _out.columns = ['lower_band','raw','upper_band']
        _out['lower_limit'] = _out.raw < _out.lower_band
        _out['upper_limit'] = _out.raw > _out.upper_band

        out[ticker] = _out
    return out
calculate_bollinger(df,['AAPL','MSFT','GOOG','AMZN'])['AAPL'].sample(3)


# In[11]:


def plot_bollinger(data,min_date,plt_cols=2):
    rows = int(len(data.keys())/plt_cols)
    fig, ax = plt.subplots(rows,plt_cols,figsize=(20,8*rows))
    fig.suptitle("Bollinger Bands",fontsize=50)

    for i,(ticker,df) in enumerate(data.items()):
        row_num = int(i / plt_cols) if len(data.keys()) > 2 else i
        col_num = i - (row_num * plt_cols)
        
        _d = data[ticker].loc[df.index>=min_date]

        if plt_cols >2: _tmp = ax[row_num,col_num]
        else: _tmp = ax[row_num]
        _tmp.set_title(ticker,fontsize=18)
        _tmp.plot(_d[['lower_band','raw','upper_band']])
        _tmp.scatter(_d[_d.lower_limit].index,_d[_d.lower_limit].raw,c='red')
        _tmp.scatter(_d[_d.upper_limit].index,_d[_d.upper_limit].raw,c='red')

plot_bollinger(calculate_bollinger(df),min_date='2016-01-01')


# ## Testing

# ### Train vs Valid vs Test

# ### Returns

# ### Statistical Tests

# In[ ]:




