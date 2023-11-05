from fastapi import FastAPI , Request
from starlette.background import BackgroundTasks
import uvicorn
from models import  SettingAdmin, SymbolAdmin, Symbols, ReportView, ConfigAdmin
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



db = get_db()


@app.get('/run')
async def run(tasks: BackgroundTasks):
    add_symbols()
    tasks.add_task(job)
    Bingx.bot = "Run"
    #await run_in_threadpool(handle_schedule)
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



