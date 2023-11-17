import ccxt
import pandas as pd


def getKlines(exchange, symbol, timeframe, limit):
    if exchange == "BingX":
        bingx = ccxt.bingx()
        # bingx = ccxt.bingx({'proxies': {'http': '127.0.0.1:2081','https': '127.0.0.1:2081'}})
        res = bingx.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
        res = res[:-1] # last kline isnt closed.
        df = pd.DataFrame(res)
        df[0] = pd.to_datetime(df[0] * 1000000)
        df.columns = ["time", "open", "high", "low", "close", "volume"]
        # print(df)
    
    elif exchange == "Kucoin":
        sym = symbol.split("-")
        if sym[0] == "BTC":
            symbol = "XBTUSDTM"
        else:
            symbol = sym[0] + "USDTM"
        kucoin = ccxt.kucoinfutures()
        res = kucoin.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
        res = res[:-1] # last kline isnt closed.
        df = pd.DataFrame(res)
        df[0] = pd.to_datetime(df[0] * 1000000)
        df.columns = ["time", "open", "high", "low", "close", "volume"]
        print(df)
        
    elif exchange == "Binance":
        symbol = symbol.split("-")[0] + symbol.split("-")[1]
        binance = ccxt.binance()
        # binance = ccxt.binance({'proxies': {'http': '127.0.0.1:2081','https': '127.0.0.1:2081'}})
        res = binance.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(res)
        df[0] = pd.to_datetime(df[0] * 1000000)
        df.columns = ["time", "open", "high", "low", "close", "volume"]

    
    elif exchange == "Gateio":
        symbol = symbol.split("-")[0] + "_" + symbol.split("-")[1]
        gateio = ccxt.gateio()
        res = gateio.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
        res = res[:-1] # last kline isnt closed.
        df = pd.DataFrame(res)
        df[0] = pd.to_datetime(df[0] * 1000000)
        df.columns = ["time", "open", "high", "low", "close", "volume"]

    
    elif exchange == "Coinex":
        symbol = symbol.split("-")[0] + symbol.split("-")[1]
        coinex = ccxt.coinex()
        # coinex = ccxt.coinex({'proxies': {'http': '127.0.0.1:44129','https': '127.0.0.1:44129'}})
        res = coinex.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
        res = res[:-1] # last kline isnt closed.
        df = pd.DataFrame(res)
        df[0] = pd.to_datetime(df[0] * 1000000)
        df.columns = ["time", "open", "high", "low", "close", "volume"]


    elif exchange == "Bybit":
        bybit = ccxt.bybit()
        # bybit = ccxt.bybit({'proxies': {'http': '127.0.0.1:44129','https': '127.0.0.1:44129'}})
        res = bybit.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
        res = res[:-1] # last kline isnt closed.
        df = pd.DataFrame(res)
        df[0] = pd.to_datetime(df[0] * 1000000)
        df.columns = ["time", "open", "high", "low", "close", "volume"]


    return df


# getKlines(exchange="BingX", symbol="ETH-USDT", timeframe="4h", limit=200)
# getKlines(exchange="Kucoin", symbol="ETH-USDT", timeframe="4h", limit=200)
# getKlines(exchange="Binance", symbol="ETH-USDT", timeframe="1h", limit=200)
# getKlines(exchange="Gateio", symbol="ETH-USDT", timeframe="1m", limit=200)
# getKlines(exchange="Coinex", symbol="ETH-USDT", timeframe="1m", limit=200)
# getKlines(exchange="Bybit", symbol="ETH-USDT", timeframe="1m", limit=200)