import pandas as pd
import numpy as np
from scipy.stats import linregress
import math
import matplotlib.pyplot as plt
import glob
import time
import decimal

start_date = '2012-1-1'

data1_reg_loop_limit = 5

lowtrenderror = []

def calculate_angle(stock):
    data = pd.read_csv("./data/yahoo_price/" + stock + ".csv", delimiter=',')
    data = data.dropna(how='any',axis=0) # BAZI DATALAR NULL onları yoktmek

    data0 = data.copy()
    data0['Date'] = pd.to_datetime(data0['Date'], errors='coerce')

    # date filter
    data0 = data0[data0.Date > start_date]


    data0['date_id'] = ((data0['Date'] - data0['Date'].min())).astype('timedelta64[D]')
    data0['date_id'] = data0['date_id'] + 1
    data0['Adj Close'] = data0['Adj Close'].astype(np.double)

    # low trend line
    # lower points are returned
    df_low = data0.copy()
    while len(df_low)>5:
        slope, intercept, r_value, p_value, std_err = linregress(x=df_low['date_id'], y=df_low['Adj Close'])
        df_low = df_low.loc[df_low['Adj Close'] < slope * df_low['date_id'] + intercept]

    if len(df_low) >= 2:
        slope, intercept, r_value, p_value, std_err = linregress(x=df_low['date_id'], y=df_low['Adj Close'])
        data0['lowtrend'] = slope * data0['date_id'] + intercept

        
        trend_low_min = min(data0['Adj Close'])
        trend_low_max = max(data0['Adj Close'])
        trend_low_count = max(data0['date_id']) - min(data0['date_id'])

        # negative or positive trend
        if data0["Adj Close"].iloc[0] > data0["Adj Close"].iloc[-1]:
            trend_low_positive = "false"
        else:
            trend_low_positive = "true"

        # eliminate minus figures
        if trend_low_min < 0:
            trend_low_min = trend_low_min + (trend_low_min * -1) + 1
            trend_low_max = trend_low_max + + (trend_low_min * -1) + 1

        
        trend_low_angle = np.rad2deg(np.arctan2(trend_low_max - trend_low_min, trend_low_count))

        change = trend_low_max / trend_low_min

        # distance to trend line
        
        kapanis = (data0["Adj Close"].iloc[-1])
        son_lowtrend = (data0["lowtrend"].iloc[-1])
        fark_trendlow = kapanis - son_lowtrend #
        fark_trendlow_yuzde = (kapanis / son_lowtrend) - 1 # yüzde kaçı


        print(stock, '== min: ', trend_low_min, ' max: ', trend_low_max, ' count: ', trend_low_count, ' angle: ',
            trend_low_angle, ' fark_trendlow: ', fark_trendlow_yuzde)

        return stock, trend_low_min, trend_low_max, trend_low_count, trend_low_angle, change, fark_trendlow_yuzde, trend_low_positive

    else:
        print(stock, ": low trend tespit edilemedi.")
        lowtrenderror.append(stock)

##########################################################################################################################

def plot(stock, rating):
    data = pd.read_csv("./data/yahoo_price/" + stock + ".csv", delimiter=',')
    data = data.dropna(how='any',axis=0) # BAZI DATALAR NULL onları yoktmek

    data0 = data.copy()
    data0['Date'] = pd.to_datetime(data0['Date'], errors='coerce')

    # date filter
    data0 = data0[data0.Date > start_date]


    data0['date_id'] = ((data0['Date'] - data0['Date'].min())).astype('timedelta64[D]')
    data0['date_id'] = data0['date_id'] + 1
    data0['Adj Close'] = data0['Adj Close'].astype(np.double)

    # low trend line
    df_low = data0.copy()
    while len(df_low)>5:
        slope, intercept, r_value, p_value, std_err = linregress(x=df_low['date_id'], y=df_low['Adj Close'])
        df_low = df_low.loc[df_low['Adj Close'] < slope * df_low['date_id'] + intercept]


    slope, intercept, r_value, p_value, std_err = linregress(x=df_low['date_id'], y=df_low['Adj Close'])
    data0['lowtrend'] = slope * data0['date_id'] + intercept

    # draw the closing price and related trendlines (uptrend and downtrend)
    filename = str(rating) + "." + stock + '.png'

    fig, ax1 = plt.subplots(figsize=(15,10))

    color = 'tab:green'
    xdate = [x.date() for x in data0.Date]
    ax1.set_xlabel('Date', color=color)
    ax1.plot(xdate, data0["Adj Close"], label="adj close", color=color)
    ax1.tick_params(axis='x', labelcolor=color)
    ax1.legend()
    plt.title(stock, fontsize=30)

    ax2 = ax1.twiny() # ax2 and ax1 will have common y axis and different x axis, twiny
    # ax2.plot(data0.Number, data0.Uptrend, label="uptrend")
    ax2.plot(data0.Date, data0.lowtrend, label="low trend")

    plt.legend()
    plt.grid()
    plt.savefig('./output/trend_low/'+filename)
    # plt.show()
    
    return filename, stock

########################################################################################################################

df_output = pd.DataFrame(columns=['Stock', "trend_low_min", "trend_low_max", "trend_low_count", 'trend_low_angle', 'fark_trendlow', 'trend_low_positive'])

path = './data/yahoo/'
files = [f for f in glob.glob(path + "**/*.csv", recursive=True)]


counter = 0
for f in files:
    counter = counter + 1
    StockName = f.replace("./data/yahoo\\", "")
    StockName = StockName.replace('.csv', "")

    print(counter, "/", len(files), " -- ", StockName)
    try:
        stock, trend_low_min, trend_low_max, trend_low_count, trend_low_angle, change, fark_trendlow, trend_low_positive = calculate_angle(StockName)

        df_output = df_output.append({'Stock': stock,
                                  "trend_low_min": trend_low_min,
                                  "trend_low_max": trend_low_max,
                                  "trend_low_count": trend_low_count,
                                  'trend_low_angle': trend_low_angle,
                                  'change_percentage': change,
                                  'fark_trendlow': fark_trendlow,
                                  'trend_low_positive': trend_low_positive
                                  },
                                 ignore_index=True)
    except:
        print("An exception occurred: ", StockName)

    




# only positive trends
df_output = df_output[df_output.trend_low_positive == "true"]

# filter against to minus values
df_output = df_output[df_output.fark_trendlow > 0]

# filter acording trend line angle
df_output = df_output[df_output.trend_low_angle > 0.01]

# sorting
df_output_sort = df_output.sort_values(by=['fark_trendlow'], ascending= True) 

pd.set_option('display.max_rows', 150)
pd.set_option('display.max_columns', 10)
print(df_output_sort.head(20))
print("unable to find low trend for: ", lowtrenderror)




for i in range(40):
    try:
        filename, stock = plot(df_output_sort.iloc[i, 0], i)
        print("figure created for: ", stock)
    except:
        print("stock adı yok: ", stock)

# f.close()
