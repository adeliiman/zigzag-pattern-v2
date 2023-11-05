from typing import Tuple
from api import getKlines
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from telegram_ import sendPhoto
from send_email import send_gmail
import plotly.io as pio
import plotly.graph_objects as go
pio.renderers.default='browser'
from database import SessionLocal
from models import Config
import math


# df.to_csv('data.csv')


def will_frac(df: pd.DataFrame, period: int = 6) -> Tuple[pd.Series, pd.Series]:
    """Indicate bearish and bullish fractal patterns using shifted Series.
    :param df: OHLC data
    :param period: number of lower (or higher) points on each side of a high (or low)
    :return: tuple of boolean Series (bearish, bullish) where True marks a fractal pattern
    """
    periods = [p for p in range(-period, period + 1) if p != 0] # default [-2, -1, 1, 2]

    highs = [df['high'] > df['high'].shift(p) for p in periods]
    bears = pd.Series(np.logical_and.reduce(highs), index=df.index)

    lows = [df['low'] < df['low'].shift(p) for p in periods]
    bulls = pd.Series(np.logical_and.reduce(lows), index=df.index)

    return bears, bulls



def find_zigzag(df, period, Xmin, Xmax):
    x1,x2,x3,x4,x5,y1,y2,y3,y4,y5 = 0,0,0,0,0,0,0,0,0,0
    try:
        peaks, valleys = will_frac(df, period=period)
        df['peaks'] = df.high[peaks]
        df['valleys'] = df.low[valleys]
        valleys = df.valleys.dropna()
        peaks = df.peaks.dropna()
        print(df.head(3))
        print(peaks, valleys)
        
        cond1 = peaks.iloc[-1] > peaks.iloc[-2]
        cond2 = peaks.index[-1] > valleys.index[-1]

        if ( (peaks.iloc[-1] > valleys.iloc[-1]) and cond1 and cond2):

            peaks_index = [peaks.index[-1]]
            valleys_index = [valleys.index[-1]]
            #
            if valleys.values[-1] > valleys.values[-2]:
                p0 = peaks.values[-1]
                v0 = valleys.index[-1]
                v1 = valleys.index[-2]
                X_distance = v0 - v1
                Y_distance = df.index[-1] - v0
                CD = peaks.index[-1] - v0
                #E = df.low.iloc[-1] #########
                E_index = v0 - X_distance # E_index >= 0, 1, ...
                E = df.low.iloc[E_index]
                P_index = E_index + math.ceil(X_distance/5)
                S_index = E_index - math.ceil(X_distance/5)
                a = min([df.low.index[ind] for ind in range(P_index, E_index+1)])
                b = max([df.high.index[ind] for ind in range(P_index, E_index+1)])
                c = min([df.low.index[ind] for ind in range(E_index, S_index+1)])
                d = max([df.high.index[ind] for ind in range(E_index, S_index+1)])

                print("X_distance:", X_distance, "|Y_distance:", Y_distance, "|CD:", CD, "|E:", E)

                # if 2>1:
                if X_distance == Y_distance and CD > 0.5* Y_distance and (CD<4*Y_distance/5) and E > v0 and E < p0 and (X_distance>Xmin) and (X_distance<Xmax):
                    peaks_index_temp = [p_index for p_index in peaks.index if p_index > v1 and p_index < v0]
                    
                    if peaks_index_temp:
                        maxi = max(list(map(lambda p_index: peaks.iloc[peaks.index==p_index].values[0], peaks_index_temp)))
                        if peaks.values[-1] > peaks.loc[peaks.values==maxi].values[0]:
                            peaks_index.append(peaks.loc[peaks.values==maxi].index[0])
                            valleys_index.append(v1)

                            print(peaks_index, valleys_index, "*"*10)
                            if c>a and d>b:
                                x1 = df.time.loc[valleys_index[1]]
                                x2 = df.time.loc[peaks_index[1]]
                                x3 = df.time.loc[valleys_index[0]]
                                x4 = df.time.loc[peaks_index[0]]
                                x5 = df.time.loc[-1]
                                
                                y1 = df.valleys.loc[valleys_index[1]]
                                y2 = df.peaks.loc[peaks_index[1]]
                                y3 = df.valleys.loc[valleys_index[0]]
                                y4 = df.peaks.loc[peaks_index[0]] 
                                y5 = df.close.loc[-1]

    except Exception as e:
        print(e)

    return (x1,x2,x3,x4,x5), (y1,y2,y3,y4,y5)



def find_zigzag_bearish(df, period, Xmin, Xmax):
    x1,x2,x3,x4,x5,y1,y2,y3,y4,y5 = 0,0,0,0,0,0,0,0,0,0
    try:
        peaks, valleys = will_frac(df, period=period)
        df['peaks'] = df.high[peaks]
        df['valleys'] = df.low[valleys]
        valleys = df.valleys.dropna()
        peaks = df.peaks.dropna()
        print(df.head(3))
        print(peaks, valleys)
        
        cond1 = peaks.iloc[-1] < peaks.iloc[-2]
        cond2 = peaks.index[-1] > valleys.index[-1]

        if ( (peaks.iloc[-1] < valleys.iloc[-1]) and cond1 and cond2):

            peaks_index = [peaks.index[-1]]
            valleys_index = [valleys.index[-1]]
            #
            if valleys.values[-1] < valleys.values[-2]:
                p0 = peaks.values[-1]
                v0 = valleys.index[-1]
                v1 = valleys.index[-2]
                X_distance = v0 - v1
                Y_distance = df.index[-1] - v0
                CD = peaks.index[-1] - v0
                #E = df.low.iloc[-1]  ########
                E_index = v0 - X_distance # E_index >= 0, 1, ...
                E = df.high.iloc[E_index]
                P_index = E_index + math.ceil(X_distance/5)
                S_index = E_index - math.ceil(X_distance/5)
                a = min([df.low.index[ind] for ind in range(P_index, E_index+1)])
                b = max([df.high.index[ind] for ind in range(P_index, E_index+1)])
                c = min([df.low.index[ind] for ind in range(E_index, S_index+1)])
                d = max([df.high.index[ind] for ind in range(E_index, S_index+1)])

                print("X_distance:", X_distance, "|Y_distance:", Y_distance, "|CD:", CD, "|E:", E)

                # if 2>1:
                if X_distance == Y_distance and CD > 0.5* Y_distance and (CD<4*Y_distance/5) and E > v0 and E < p0 and (X_distance>Xmin) and (X_distance<Xmax):
                    peaks_index_temp = [p_index for p_index in peaks.index if p_index > v1 and p_index < v0]
                    
                    if peaks_index_temp:
                        maxi = max(list(map(lambda p_index: peaks.iloc[peaks.index==p_index].values[0], peaks_index_temp)))
                        if peaks.values[-1] < peaks.loc[peaks.values==maxi].values[0]:
                            peaks_index.append(peaks.loc[peaks.values==maxi].index[0])
                            valleys_index.append(v1)

                            print(peaks_index, valleys_index, "*"*10)
                            if c>a and d>b:
                                x1 = df.time.loc[valleys_index[1]]
                                x2 = df.time.loc[peaks_index[1]]
                                x3 = df.time.loc[valleys_index[0]]
                                x4 = df.time.loc[peaks_index[0]]
                                x5 = df.time.loc[-1]
                                
                                y1 = df.valleys.loc[valleys_index[1]]
                                y2 = df.peaks.loc[peaks_index[1]]
                                y3 = df.valleys.loc[valleys_index[0]]
                                y4 = df.peaks.loc[peaks_index[0]] 
                                y5 = df.close.loc[-1]

    except Exception as e:
        print(e)

    return (x1,x2,x3,x4,x5), (y1,y2,y3,y4,y5)




def get_candlestick_chart(df: pd.DataFrame, symbol, interval, X, Y):

    layout = go.Layout(
        title = symbol + "    " + interval,
        xaxis = {'title': 'Date'},
        yaxis = {'title': 'Price'},
        legend = {'orientation': 'h', 'x': 0, 'y': 1.075},
        # width = 700,
        # height = 700,
    ) 
    if X[1]:
        print(X[1], "///////////////")
        fig = go.Figure(
            layout=layout,
            data=[
                go.Candlestick(
                    x = df['time'],
                    open = df['open'], 
                    high = df['high'],
                    low = df['low'],
                    close = df['close'],
                    showlegend=False,
                ),
                go.Scatter(x = df.time, y=df.peaks.values, mode="markers", marker_color="red", marker_size=13),
                go.Scatter(x = df.time, y=df.valleys.values, mode="markers", marker_color="green", marker_size=13),
                go.Scatter(x=X, y=Y)
            ]
        )
        fig.update_xaxes(rangeslider_visible = False,)
        return fig
    elif 2<1:
        fig = go.Figure(
            layout=layout,
            data=[
                go.Candlestick(
                    x = df['time'],
                    open = df['open'], 
                    high = df['high'],
                    low = df['low'],
                    close = df['close'],
                    showlegend=False,
                ),
                go.Scatter(x = df.time, y=df.peaks.values, mode="markers", marker_color="red", marker_size=13),
                go.Scatter(x = df.time, y=df.valleys.values, mode="markers", marker_color="green", marker_size=13),
            ]
        )
        fig.update_xaxes(rangeslider_visible = False,)
        return fig


def zigzag(symbol="BTC-USDT", interval='3m', period=6, exchange="BingX", Xmin=10, Xmax=30):
    df = getKlines(exchange, symbol, timeframe=interval, limit=200)
    # df = pd.read_csv('data.csv')
    X, Y = find_zigzag(df, period=period, Xmin=Xmin, Xmax=Xmax)
    fig = None
    fig = get_candlestick_chart(df, symbol, interval, X, Y)
    if fig:
        fig.show()
        file = "./pics/" + exchange + '_' + symbol +'_'+ interval
        pio.write_image(fig, file=file, format='png')
        db = SessionLocal()
        configs = db.query(Config).all()
        for config in configs:
            sendPhoto(file, config.telegramToken, config.telegramID)
        #
        send_gmail(file)

    X, Y = find_zigzag_bearish(df, period=period, Xmin=Xmin, Xmax=Xmax)
    fig = None
    fig = get_candlestick_chart(df, symbol, interval, X, Y)
    if fig:
        fig.show()
        file = "./pics/" + exchange + '_' + symbol +'_'+ interval
        pio.write_image(fig, file=file, format='png')
        db = SessionLocal()
        configs = db.query(Config).all()
        for config in configs:
            sendPhoto(file, config.telegramToken, config.telegramID)
        #
        send_gmail(file)


# zigzag()
