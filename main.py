import time
import schedule
import concurrent.futures
from utils import zigzag
from sqlalchemy.orm import Session
from database import SessionLocal
from database import get_db
from fastapi import Depends
from models import Symbols, Setting

class BingX:
	def __init__(self):
		self.bot = 'Stop' # 'Run'
		self.settings = []
		self.symbols = []


Bingx = BingX()


def main_job(items):
    symbol = items[0]
    interval = items[1]
    exchange = items[2]
    Xmin = items[3]
    Xmax = items[4]
    try:
        zigzag(symbol=symbol, interval=interval, exchange=exchange, Xmin=Xmin, Xmax=Xmax)
    except Exception as e:
        print(e)



def my_job():
    symbols = Bingx.symbols
    min_ = time.gmtime(time.time()).tm_min

    settings = Bingx.settings
    for setting in settings:
        exchange = setting.exchange
        Xmin = setting.Xmin
        Xmax = setting.Xmax
        tf = None
        
        if setting.timeframe == "3min" and (min_ % 3 == 0):
            tf = '3m'
        elif setting.timeframe == "5min" and (min_ % 5 == 0):
            tf = '5m'
        elif setting.timeframe == "15min" and (min_ % 15 == 0):
            tf = '15m'
        elif setting.timeframe == "30min" and (min_ % 30 == 0):
            tf = '30m'
        elif setting.timeframe == "1hour" and (min_ == 0):
            tf = '1h'
        elif setting.timeframe == "4hour" and (min_ == 0):
            tf = '4h'

        if tf:
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(symbols)+1) as executor:
                items = [(sym, tf, exchange, Xmin, Xmax) for sym in symbols]
                executor.map(main_job, items)


def job():
    schedule.every(1).minutes.at(":02").do(job_func=my_job)

    while True:
        if Bingx.bot == "Stop":
            #schedule.cancel_job(my_job)
            schedule.clear()
            break
        schedule.run_pending()
        print(time.ctime(time.time()))
        time.sleep(1)
        
        


