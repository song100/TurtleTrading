import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(r'AUDUSD1440.csv')
df['date'] = pd.to_datetime(df['date'])
df.set_index("date",inplace=True)
np.save('C:/Users/SONG100/PycharmProjects/invest/AUDUSD1440',df)

N1 = 42
N2 = 21
#use rolling_max() culcate the high price in N1 days
df['n1_high'] = df['high'].rolling(window=N1,center=False).max()
# print(df.head(43))

# 用pd.expanding_max()从第一个开始依次寻找目前出现过的最大值
# 实例如下
# demo_list = np.array([1,2,1,1,500,100])
# pd.expanding_max(demo_list)
# array([   1.,    2.,    2.,    2.,  500.,  500.])

expan_max = pd.expanding_max(df['close'])
#fillna() 将NaN替换为当前的序列
df['n1_high'].fillna(value=expan_max, inplace=True)
# print(df.head(43))

df['n2_low'] = df['low'].rolling(window=N2,center=False).min()
expan_min = pd.expanding_min(df['close'])
df['n2_low'].fillna(value=expan_min, inplace=True)
# print(df.head(22))

##做空的序列
df['n1_low'] = df['low'].rolling(window=N1,center=False).min()
df['n1_low'].fillna(value=expan_min, inplace=True)

df['n2_high'] = df['high'].rolling(window=N2,center=False).max()
df['n2_high'].fillna(value=expan_max, inplace=True)


#接下来根据突破的定义来构建signal列
#当天收盘价格超过N天最高或最低价，超过最高价是作为买入信号
#buy_index=行的索引，本例中就是日期，而且是满足close大于n1_high的情况下的索引
buy_index_in = df[df['close'] > df['n1_high'].shift(1)].index  #shift 是移动序列，即将整个n1_high列都下移一格
df.loc[buy_index_in, 'signal'] = 1  #loc 是用行索引定位到某行

sell_index_in = df[df['close'] < df['n1_low'].shift(1)].index  #shift 是移动序列，即将整个n1_high列都下移一格
df.loc[sell_index_in, 'signal_short'] = 1  #loc 是用行索引定位到某行,signal_short为做空的标记

#当天收盘价格超过N天最高或最低价，超过最低价是作为卖出信号
sell_index_out = df[df['close'] < df['n2_low'].shift(1)].index
df.loc[sell_index_out, 'signal'] = 0

buy_index_out = df[df['close'] > df['n2_high'].shift(1)].index
df.loc[buy_index_out, 'signal_short'] = 0

# print(df.head())

# df.signal.value_counts().plot(kind='pie', figsize=(5,5))
# plt.show()

"""
将信号操作序列移动一个单位，代表第二天在执行操作信号，转换为持仓状态
"""
df['keep'] = df['signal'].shift(1)
df['keep'].fillna(method='ffill',inplace=True)
# print(df['keep'].head(50))

df['keep_short'] = df['signal_short'].shift(1)
df['keep_short'].fillna(method='ffill',inplace=True)

#计算基准收益
df['benchmark_profit'] = df['close']/df['close'].shift(1)-1
df['benchmark_profit_short'] = df['close'].shift(1)/df['close']-1

#计算使用海龟交易法的收益
df['trend_profit'] = df['keep']*df['benchmark_profit']
df['trend_profit_short'] = df['keep_short']*df['benchmark_profit_short']

# print(sell_index_in)
# 可视化收益情况对比
df[['benchmark_profit', 'trend_profit','benchmark_profit_short', 'trend_profit_short']].cumsum().plot(grid=True,figsize=(14,7))
plt.show()