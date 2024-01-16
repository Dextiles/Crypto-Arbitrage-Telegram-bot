from peewee import SqliteDatabase, Model, CharField, IntegerField, DateTimeField
from config_data.config import ADDRESS_db
from datetime import datetime
import json


db = SqliteDatabase(ADDRESS_db)


class Users(Model):
    user_id = IntegerField(primary_key=True)
    username = CharField()
    first_name = CharField()
    last_surname = CharField(null=True)
    reg_date = DateTimeField(default=datetime.now())
    bad_list_currency = CharField(null=True)
    default_profit = IntegerField(default=5)
    work_exchanges = CharField(default=json.dumps([
    "binance", "bybit", "okx", "kucoin",
    "kraken",
    "upbit", "gateio", "gemini",
    "coinbase", "cryptocom"]), null=False)

    class Meta:
        database = db


Users.create_table()
