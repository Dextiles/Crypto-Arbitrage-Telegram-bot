from peewee import SqliteDatabase, Model, CharField, IntegerField, DateField
from config_data import config
from datetime import datetime


db = SqliteDatabase(config.ADDRESS_db)


class User(Model):
    user_id = IntegerField(primary_key=True)
    username = CharField()
    first_name = CharField()
    last_surname = CharField(null=True)
    reg_date = DateField(default=datetime.now())

    class Meta:
        database = db


User.create_table()

