# -*- coding: utf-8 -*-

import os
import sys, traceback
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.sql import select
import errors

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False)
db_meta = MetaData(bind=db_engine)
# cargar una tabla
db_table_users = Table('customers', db_meta, autoload=True, autoload_with=db_engine)
db_table_creditCard = Table('creditcard', db_meta, autoload=True, autoload_with=db_engine)


def db_registerUser(name, password, mail, creditCard, cash):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        
        # Seleccionar las peliculas del anno 1949
        db_result = db_conn.execute(db_table_creditCard.insert(), creditcard = creditCard)
        if db_result.is_insert() == False:
            return errors.ERROR_CREDITCARD

        db_result = db_conn.execute(db_table_users.insert(), username = name, password = password, email = email, creditcard = creditCard, cash = cash)
        if db_result.is_insert() == False:
            return errors.ERROR_EMAIL_USED
        
        db_conn.close()
        
        return  errors.OK

    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return errors.ERROR

def db_login(mail, password):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        
        # Seleccionar las peliculas del anno 1949
        select_user = db_table_users.select([username, password]).where(db_table_users.c.email == mail)
        db_result = db_conn.execute(select_user)
        results = db_result.fetchall()
        if len(results) == 0:
            return errors.ERROR_USER_NOT_EXIST

        if results[1] != password:
            return errors.ERROR_INCORRECT_PASSWORD
        
        db_conn.close()
        
        return  errors.OK

    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return errors.ERROR
