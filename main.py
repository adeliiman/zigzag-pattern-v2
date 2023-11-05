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


def main_job(symbol):
    print(symbol)
    min_ = time.gmtime(time.time()).tm_min
    #print("min_  ", min_)
    settings = Bingx.settings

    for setting in settings:
        print(setting.timeframe)
        if setting.timeframe == "3min" and (min_ % 3 == 0):
            try:
                zigzag(symbol=symbol, interval='3m', exchange=setting.exchange, Xmin=setting.Xmin, Xmax=setting.Xmax)
            except Exception as e:
                print(e)
        elif setting.timeframe == "5min" and (min_ % 5 == 0):
            try:
                zigzag(symbol=symbol, interval='5m', exchange=setting.exchange, Xmin=setting.Xmin, Xmax=setting.Xmax)
            except Exception as e:
                print(e)
        elif setting.timeframe == "15min" and (min_ % 15 == 0):
            try:
                zigzag(symbol=symbol, interval='15m', exchange=setting.exchange, Xmin=setting.Xmin, Xmax=setting.Xmax)
            except Exception as e:
                print(e)
        elif setting.timeframe == "30min" and (min_ % 30 == 0):
            try:
                zigzag(symbol=symbol, interval='30m', exchange=setting.exchange, Xmin=setting.Xmin, Xmax=setting.Xmax)
            except Exception as e:
                print(e)


def my_job():
    symbols = Bingx.symbols
    print(symbols)
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(symbols)+1) as executor:
        executor.map(main_job, symbols)



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


