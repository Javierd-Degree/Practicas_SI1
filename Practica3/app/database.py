# -*- coding: utf-8 -*-

import os
import sys, traceback
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
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
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()
		
		# Guardamos la tarjeta de credito. Avisamos si esa tarjeta ya esta añadida
		try:
			db_conn.execute(db_table_creditCard.insert(), creditcard = creditCard)
		except IntegrityError:
			return errors.ERROR_CREDITCARD

		# Guardamos el usuario en la base de datos. Avisamos si ya hay un usuario dicho email
		try:
			db_result = db_conn.execute(db_table_users.insert(), username = name, password = password, email = mail, creditcard = creditCard, cash = cash)
		except IntegrityError:
			# Eliminamos la tarjeta de credito guardada anteriormente
			delete_ccard = db_table_creditCard.delete().where(db_table_creditCard.c.creditcard == creditCard)
			delete_ccard.execute()
			return errors.ERROR_EMAIL_USED
		
		db_conn.close()
		
		return errors.OK

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
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()
		
		# Buscamos el usuario por su email y comprobamos la contraseña
		select_user = select([db_table_users.c.password]).where(db_table_users.c.email == mail)
		db_result = db_conn.execute(select_user)
		results = db_result.fetchall()
		if len(results) == 0:
			return errors.ERROR_USER_NOT_EXIST

		if results[0][1] != password:
			return errors.ERROR_INCORRECT_PASSWORD
		
		db_conn.close()
		
		return errors.OK

	except:
		if db_conn is not None:
			db_conn.close()
		print("Exception in DB access:")
		print("-"*60)
		traceback.print_exc(file=sys.stderr)
		print("-"*60)

		return errors.ERROR

def db_getUsername(mail):
	# Solo debe llamarse una vez estamos seguros de que el usuario existe
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()
		
		# Buscamos el usuario por su email y devolvemos el nombre
		select_user = select([db_table_users.c.username]).where(db_table_users.c.email == mail)
		db_result = db_conn.execute(select_user)
		results = db_result.fetchall()
		if len(results) == 0:
			return None

		name = results[0][0]
		
		db_conn.close()
		
		return name

	except:
		if db_conn is not None:
			db_conn.close()
		print("Exception in DB access:")
		print("-"*60)
		traceback.print_exc(file=sys.stderr)
		print("-"*60)

		return None