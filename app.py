from fastapi import FastAPI , Request, Response, Depends
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks
import uvicorn
from models import  SettingAdmin, SymbolAdmin, Symbols, ReportView, ConfigAdmin, Setting
from database import init_db, engine
from database import get_db
from sqladmin import Admin
import threading
from setLogger import get_logger
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
# from fastapi.concurrency import run_in_threadpool
from main import Bingx, job
from get_symbols import add_symbols




logger = get_logger(__name__)


# Base.metadata.create_all(bind=engine)


app = FastAPI()
admin = Admin(app, engine)

@app.on_event("startup")
async def startup():
    init_db()
    print("done")

admin.add_view(ConfigAdmin)
admin.add_view(SettingAdmin)
admin.add_view(SymbolAdmin)
admin.add_view(ReportView)






@app.get('/run')
async def run(tasks: BackgroundTasks, db: Session = Depends(get_db)):
    add_symbols()
    
    symbols = db.query(Symbols).all()
    ids = [symbol.id for symbol in symbols]
    actives = [symbol.active for symbol in symbols]
    symbols = [symbol.symbol for symbol in symbols if symbol.active]
    Bingx.symbols = symbols

    settings = db.query(Setting).all()
    Bingx.settings = settings
    

    tasks.add_task(job)
    Bingx.bot = "Run"

    return  RedirectResponse(url="/admin/home")

@app.get('/stop')
def stop():
    Bingx.bot = "Stop"
    print("Bingx stoped. ................")
    return  RedirectResponse(url="/admin/home")



@app.get('/')
def index():
     return  RedirectResponse(url="/admin/home")




# @app.on_event("startup")
# async def startup_event():
#     threading.Thread(target=handle_ws).start()



if __name__ == '__main__':
	uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)



