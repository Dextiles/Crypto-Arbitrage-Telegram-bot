from peewee import SqliteDatabase, Model, CharField, IntegerField, DateTimeField
from config_data.config import ADDRESS_db
from datetime import datetime
import json

default_exchanges = ['binance', 'bybit', 'okx', 'kucoin',
                     'kraken', 'bitstamp', 'bitfinex',
                     'upbit', 'gateio', 'gemini',
                     'coinbase', 'cryptocom', 'bitget', 'mexc', 'zonda', 'tokocrypto', 'probit', 'yobit']
default_profit_value = 10

db = SqliteDatabase(ADDRESS_db)


class Users(Model):
    user_id = IntegerField(primary_key=True)
    username = CharField()
    first_name = CharField()
    last_surname = CharField(null=True)
    reg_date = DateTimeField(default=datetime.now())
    bad_list_currency = CharField(null=True)
    default_profit = IntegerField(default=default_profit_value)
    work_exchanges = CharField(default=json.dumps(default_exchanges), null=False)

    class Meta:
        database = db


Users.create_table()
