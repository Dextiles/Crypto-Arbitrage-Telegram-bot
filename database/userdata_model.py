from peewee import SqliteDatabase, Model, CharField, IntegerField, DateTimeField, FloatField
from datetime import datetime
import json
from database.default_values_config.default_getter import GetDefaultValues

db = SqliteDatabase('database/userdata.sql')


class Users(Model):
    """
        Represents the users in the system.

        Attributes:
        - user_id: IntegerField - the unique identifier of the user
        - username: CharField - the username of the user
        - first_name: CharField - the first name of the user
        - last_surname: CharField (nullable) - the last surname of the user
        - reg_date: DateTimeField - the date of registration of the user
        - bad_list_currency: CharField - the list of bad currencies
        - default_profit: IntegerField - the default profit for the user
        - work_exchanges: CharField - the list of working exchanges
        - last_request: DateTimeField - the last request time
        - work_symbols: CharField - the list of working symbols
        - work_symbols_date_analysis: DateTimeField - the date of the last analysis of the symbols
        """
    user_id = IntegerField(primary_key=True)
    username = CharField()
    first_name = CharField()
    last_surname = CharField(null=True)
    reg_date = DateTimeField(default=datetime.now())
    bad_list_currency = CharField(default=json.dumps([]))
    default_profit = FloatField(default=GetDefaultValues().profit)
    work_exchanges = CharField(default=json.dumps(GetDefaultValues().exchanges), null=False)
    last_request = DateTimeField(default=datetime.now())

    class Meta:
        database = db


class WorkDirectory(Model):
    work_symbols_date_analysis = DateTimeField(null=True)
    allowed_symbols = CharField(null=True)

    class Meta:
        database = db


WorkDirectory.create_table()
Users.create_table()
