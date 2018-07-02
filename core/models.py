from peewee import *
from playhouse.db_url import connect

import os
from datetime import datetime, date

db = connect(os.getenv('DATABASE_URL', 'postgres://postgres:postgres@localhost:5432/bank'));

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    id = PrimaryKeyField(index=True)
    first_name = CharField()
    middle_name = CharField()
    last_name = CharField()
    email_address = CharField(unique=True)
    phone_number = CharField()
    address = CharField()
    birth_date = DateField()
    password = CharField()
    type = IntegerField(default=9)
    deleted = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(default=datetime.now())

    class Meta:
        table_name = 'users'

class Account(BaseModel):
    id = PrimaryKeyField(index=True)
    user_id = ForeignKeyField(User)
    account_number = CharField(index=True, unique=True)
    pin = CharField()
    balance = DecimalField(decimal_places=2)
    time_deposit = DecimalField(decimal_places=2, default=0.0)
    deleted = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(default=datetime.now())

    class Meta:
        table_name = 'accounts'

class TimeDeposit(BaseModel):
    id = PrimaryKeyField(index=True)
    account_number = CharField()
    amount = DecimalField(decimal_places=2)
    interest = DoubleField()
    terminal_date = DateTimeField()
    deleted = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now())

    class Meta:
        table_name = 'time_deposits'

class Transaction(BaseModel):
    id = PrimaryKeyField(index=True)
    account_number = CharField()
    amount = DecimalField(decimal_places=2)
    type = CharField()
    reference_number = CharField()
    created_at = DateTimeField(default=datetime.now())

    class Meta:
        table_name = 'transactions'

class Log(BaseModel):
    id = PrimaryKeyField(index=True)
    user_id = ForeignKeyField(User)
    action = CharField()
    created_at = DateTimeField(default=datetime.now())

def connect_db():
    db.connect(reuse_if_open=True)
    db.create_tables([User, Account, Transaction, TimeDeposit, Log])

def close_db():
    if not db.is_closed():
        db.close()