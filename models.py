
from sqlalchemy import Column,Integer,Numeric,String, DateTime, Boolean, Float
from database import Base
from sqladmin import Admin, ModelView
from sqladmin import BaseView, expose
import wtforms


class Config(Base):
    __tablename__ = "config"
    id = Column(Integer,primary_key=True)
    telegramID = Column(String)
    telegramToken = Column(String)

class ConfigAdmin(ModelView, model=Config):
    column_list = [Config.telegramID, Config.telegramToken]
    icon = "fa-solid fa-user"
    name_plural = "Config"



class Setting(Base):
    __tablename__ = "setting"
    id = Column(Integer,primary_key=True)  
    timeframe = Column(String)
    exchange = Column(String)
    Xmin = Column(Integer)
    Xmax = Column(Integer)


class SettingAdmin(ModelView, model=Setting):
    #form_columns = [User.name]
    column_list = [Setting.id, Setting.timeframe, Setting.exchange, Setting.Xmin, Setting.Xmax]
    name = "Setting"
    name_plural = "Setting"
    icon = "fa-solid fa-user"
    form_args = dict(timeframe=dict(default="5min", choices=["5min", "3min", "15min", "30min", "1hour", "4hour", "1min"]), 
                     exchange=dict(default="BingX", choices=["BingX", "Kucoin", "Binance", "Bybit", "Coinex", "Gateio"])
                     )
    form_overrides =  dict(timeframe=wtforms.SelectField, exchange=wtforms.SelectField)

    async def on_model_change(self, data, model, is_created):
        # Perform some other action
        #print(data)
        pass

    async def on_model_delete(self, model):
        # Perform some other action
        pass


class Symbols(Base):
    __tablename__ = "symbols"
    id = Column(Integer,primary_key=True)
    symbol = Column(String)
    active = Column(Boolean)


class SymbolAdmin(ModelView, model=Symbols):

    column_list = [Symbols.id, Symbols.symbol, Symbols.active]
    name = "Symbol"
    name_plural = "Symbol"
    icon = "fa-sharp fa-solid fa-bitcoin-sign"
    form_overrides = dict(symbol=wtforms.StringField)
    
    form_args = dict(symbol=dict(validators=[wtforms.validators.regexp('.+[A-Z]-USDT')], label="symbol(BTC-USDT)"),
                    active=dict(label="Active?",default=True))
    

class ReportView(BaseView):
    name = "Home"
    icon = "fas fa-house-user"

    @expose("/home", methods=["GET"])
    def report_page(self, request):
        from main import Bingx
        return self.templates.TemplateResponse("base1.html", context={"request":request, "status":Bingx.bot})



