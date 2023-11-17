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
from setLogger import get_logger

logger = get_logger(__name__)



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

# df = pd.read_csv('data.csv')
# print(df.tail())
# period = 6
# peaks, valleys = will_frac(df, period=period)
# df['peaks'] = df.high[peaks]
# df['valleys'] = df.low[valleys]
# valleys = df.valleys.dropna()
# peaks = df.peaks.dropna()
# print(peaks)


def find_zigzag(df, period, Xmin, Xmax):
    try:

        def temp(p0, p1, v0, v1, p0_value, p1_value, v0_value, v1_value):
            cond1 = p0_value > p1_value and p0_value > v0_value
            cond2 = p1_value > v0_value and p1_value > v1_value
            cond3 = v0_value > v1_value
            cond4 = p0 > v0 and v0 > p1 and p1 > v1

            if not ( cond1 and cond2 and cond3 and cond4):
                return None
            
            X_distance = v0 - v1 -1 # number of kline between vo and v1
            cond1 = (df.index[-1] - v0 -1) == X_distance * (6/5)
            cond2 = (v0 + X_distance/2 <= p0) and (p0 <= v0 + X_distance*(4/5))

            N_index = int(v0 + X_distance / 2)
            P_index = int(v0 + X_distance*(4/5))
            R_index = int(v0 + X_distance)
            S_index = int(v0 + X_distance *(6/5))

            if (R_index > df.index[-1]) or (S_index > df.index[-1]):
                return None
            
            cond3 = df['low'].loc[R_index] > v0_value and df['low'].loc[R_index] < p0_value
            
            a = min([float(df.low.values[ind-1]) for ind in range(int(P_index), int(R_index)+1)])
            b = max([float(df.high.values[ind-1]) for ind in range(int(P_index), int(R_index)+1)])
            c = min([float(df.low.values[ind-1]) for ind in range(int(R_index), int(S_index)+1)])
            d = max([float(df.high.values[ind-1]) for ind in range(int(R_index), int(S_index)+1)])
            cond4 = c >= a and d >= b
            cond5 = (X_distance>Xmin) and (X_distance<Xmax)
            logger.info(f"{cond1}, {cond2}, {cond3}, {cond4}, {cond5}")


            if  not(cond1 and cond2 and cond3 and cond4 and cond5):
                return None

            x1 = df.time.iloc[v1]
            x2 = df.time.iloc[p1]
            x3 = df.time.iloc[v0]
            x4 = df.time.iloc[p0]
            x5 = df.time.iloc[R_index]
            x6 = df.time.iloc[S_index]
            N_x = df.time.iloc[N_index]
            P_x = df.time.iloc[P_index]
            
            y1 = df.valleys.iloc[v1]
            y2 = df.peaks.iloc[p1]
            y3 = df.valleys.iloc[v0]
            y4 = df.peaks.iloc[p0] 
            y5 = df.close.iloc[R_index]
            y6 = float(df.close.iloc[S_index])
            N_y = df.close.iloc[N_index]
            P_y = df.close.iloc[P_index]

            logger.info(f"{x1}, {x2}, {x3}, {x4}, {x5}, {x6}")
            logger.info(f"{y1}, {y2}, {y3}, {y4}, {y5}, {y6}")

            return [(x1,x2,x3,x4,x5,x6), (y1,y2,y3,y4,y5,y6), (N_x, P_x, x6), (N_y, P_y, y6)]
    

        peaks, valleys = will_frac(df, period=period)
        df['peaks'] = df.high[peaks]
        df['valleys'] = df.low[valleys]
        valleys = df.valleys.dropna()
        peaks = df.peaks.dropna()

        # peaks_index_temp = [p_index for p_index in peaks.index if p_index > v1 and p_index < v0]
        # if peaks_index_temp:
        #     p1 = max(list(map(lambda p_index: peaks.iloc[peaks.index==p_index].index[0], peaks_index_temp)))

        for p in peaks.index[::-1]:
            p0 = p
            p0_value = peaks.loc[p]
            for p in peaks[:-1].index[::-1]:
                p1 = p
                p1_value = peaks.loc[p]
                for v in valleys.index[::-1]:
                    v0 = v
                    v0_value = valleys.loc[v]
                    for v in valleys[:-1].index[::-1]:
                        v1 = v
                        v1_value = valleys.loc[v]
                        # logger.debug(f"{p0}, {p0_value}, {p1}, {p1_value}, {v0}, {v0_value}, {v1}, {v1_value}")
                        return temp(p0, p1, v0, v1, p0_value, p1_value, v0_value, v1_value)
    
    except Exception as e:
            logger.exception(str(e))



def find_zigzag_bearish(df, period, Xmin, Xmax):
    try:

        def temp(p0, p1, v0, v1, p0_value, p1_value, v0_value, v1_value):
            cond1 = p0_value < p1_value
            cond2 = p0_value > v0_value
            cond3 = p0 > v0 and v0 > p1 and p1 > v1
            cond4 = v0_value < v1_value and v0_value < v1_value and p1_value > v1_value

            if not ( cond1 and cond2 and cond3 and cond4):
                return None
            
            X_distance = v0 - v1 -1 # number of kline between vo and v1
            cond1 = (df.index[-1] - v0 -1) == X_distance * (6/5)
            cond2 = (v0 + X_distance/2 < p0) and (p0 < v0 + X_distance*(4/5))

            N_index = int(v0 + X_distance / 2)
            P_index = int(v0 + X_distance*(4/5))
            R_index = int(v0 + X_distance)
            S_index = int(v0 + X_distance *(6/5))

            if (R_index > df.index[-1]) or (S_index > df.index[-1]):
                return None
            cond3 = df['low'].loc[R_index] < v0_value and df['low'].loc[R_index] < p0_value
            
            a = min([float(df.low.values[ind-1]) for ind in range(int(P_index), int(R_index)+1)])
            b = max([float(df.high.values[ind-1]) for ind in range(int(P_index), int(R_index)+1)])
            c = min([float(df.low.values[ind-1]) for ind in range(int(R_index), int(S_index)+1)])
            d = max([float(df.high.values[ind-1]) for ind in range(int(R_index), int(S_index)+1)])
            cond4 = c >= a and d >= b
            cond5 = (X_distance>Xmin) and (X_distance<Xmax)
            logger.info(f"{cond1}, {cond2}, {cond3}, {cond4}, {cond5}")


            if  not(cond1 and cond2 and cond3 and cond4 and cond5):
                return None

            x1 = df.time.iloc[v1]
            x2 = df.time.iloc[p1]
            x3 = df.time.iloc[v0]
            x4 = df.time.iloc[p0]
            x5 = df.time.iloc[R_index]
            x6 = df.time.iloc[S_index]
            N_x = df.time.iloc[N_index]
            P_x = df.time.iloc[P_index]
            
            y1 = df.valleys.iloc[v1]
            y2 = df.peaks.iloc[p1]
            y3 = df.valleys.iloc[v0]
            y4 = df.peaks.iloc[p0] 
            y5 = df.close.iloc[R_index]
            y6 = float(df.close.iloc[S_index])
            N_y = df.close.iloc[N_index]
            P_y = df.close.iloc[P_index]

            logger.info(f"{x1}, {x2}, {x3}, {x4}, {x5}, {x6}")
            logger.info(f"{y1}, {y2}, {y3}, {y4}, {y5}, {y6}")

            return [(x1,x2,x3,x4,x5,x6), (y1,y2,y3,y4,y5,y6), (N_x, P_x, x6), (N_y, P_y, y6)]
    

        peaks, valleys = will_frac(df, period=period)
        df['peaks'] = df.high[peaks]
        df['valleys'] = df.low[valleys]
        valleys = df.valleys.dropna()
        peaks = df.peaks.dropna()


        for p in peaks.index[::-1]:
            p0 = p
            p0_value = peaks.loc[p]
            for p in peaks[:-1].index[::-1]:
                p1 = p
                p1_value = peaks.loc[p]
                for v in valleys.index[::-1]:
                    v0 = v
                    v0_value = valleys.loc[v]
                    for v in valleys[:-1].index[::-1]:
                        v1 = v
                        v1_value = valleys.loc[v]
                        return temp(p0, p1, v0, v1, p0_value, p1_value, v0_value, v1_value)
    
    except Exception as e:
            logger.exception(str(e))




def get_candlestick_chart(df: pd.DataFrame, symbol, interval, X, Y, XX, YY):

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
                go.Scatter(x=X, y=Y),
            #     go.Scatter(x=[XX[0], XX[0]], y=[YY[0]*0.98, YY[0]*1.02]),
            #     go.Scatter(x=[XX[1], XX[1]], y=[YY[1]*0.98, YY[1]*1.02]),
            #     go.Scatter(x=[XX[2], XX[2]], y=[YY[2]*0.98, YY[2]*1.02]),
            #     go.Scatter(x=[X[1], X[1]], y=[Y[1]*0.98, Y[1]*1.02]),
            #     go.Scatter(x=[X[3], X[3]], y=[Y[3]*0.98, Y[3]*1.02]),
            #     go.Scatter(x=[X[5], X[5]], y=[Y[5]*0.98, Y[5]*1.02]),
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


def zigzag(symbol, interval, period=6, exchange="BingX", Xmin=10, Xmax=100):
    df = getKlines(exchange, symbol, timeframe=interval, limit=200)
    # df = pd.read_csv('data.csv')
    for period in [3,4,5,6,7,8,9,10]:

        res = find_zigzag(df, period=period, Xmin=Xmin, Xmax=Xmax)
        if res:
            X = res[0]
            Y = res[1]
            XX = res[2]
            YY = res[3]
            fig = None
            fig = get_candlestick_chart(df, symbol, interval, X, Y, XX, YY)
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

        res = find_zigzag_bearish(df, period=period, Xmin=Xmin, Xmax=Xmax)
        if res:
            X = res[0]
            Y = res[1]
            XX = res[2]
            YY = res[3]
            fig = None
            fig = get_candlestick_chart(df, symbol, interval, X, Y, XX, YY)
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


