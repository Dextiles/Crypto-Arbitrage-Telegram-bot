from peewee import SqliteDatabase, Model, CharField, IntegerField, DateTimeField
from datetime import datetime
import json

db = SqliteDatabase('database/userdata.sql')


class Users(Model):
    user_id = IntegerField(primary_key=True)
    username = CharField()
    first_name = CharField()
    last_surname = CharField(null=True)
    reg_date = DateTimeField(default=datetime.now())
    bad_list_currency = CharField(default=json.dumps([]))
    default_profit = IntegerField(default=5)
    work_exchanges = CharField(default=json.dumps([
    "binance", "bybit", "okx", "kucoin",
    "upbit", "gateio", "gemini",
    "coinbase", "cryptocom"]), null=False)
    last_request = DateTimeField(default=datetime.now())
    work_symbols = CharField(default=json.dumps([]))
    work_symbols_date_analysis = DateTimeField(default=datetime.now())

    class Meta:
        database = db


Users.create_table()
