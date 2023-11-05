
from database import SessionLocal
from models import Symbols


def add_symbols():
    with open('symbols.txt') as f:
        symbols = f.readlines()

    symbols = [symbol.split("\n")[0].upper()+"-USDT" for symbol in symbols ]
    # print(symbols)


    db = SessionLocal()
    db_symbols = db.query(Symbols).all()
    db_symbols = [symbol.symbol for symbol in db_symbols]

    for symbol in symbols:
        if  symbol not in db_symbols:
            sym = Symbols()
            sym.symbol = symbol
            sym.active = True
            db.add(sym)
            db.commit()
            db.close()