# -*- coding: utf-8 -*-

import os
import sys, traceback
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
import datetime
from app import errors

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False)
db_meta = MetaData(bind=db_engine)

# cargar una tabla
db_table_users = Table('customers', db_meta, autoload=True, autoload_with=db_engine)
db_table_creditCard = Table('creditcard', db_meta, autoload=True, autoload_with=db_engine)
db_table_genres = Table('genres', db_meta, autoload=True, autoload_with=db_engine)
db_table_movies = Table('imdb_movies', db_meta, autoload=True, autoload_with=db_engine)


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

		if results[0][0] != password:
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

def db_getUserDict(mail):
	# Solo debe llamarse una vez estamos seguros de que el usuario existe
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()
		
		# Buscamos el usuario por su email y devolvemos el nombre
		select_user = select([db_table_users.c.username, db_table_users.c.email, db_table_users.c.creditcard, db_table_users.c.cash]).where(db_table_users.c.email == mail)
		db_result = db_conn.execute(select_user)
		results = db_result.fetchall()
		if len(results) == 0:
			return None

		user = {}
		user['name'] = results[0][0]
		user['mail'] = results[0][1]
		user['creditCard'] = results[0][2]
		user['cash'] = results[0][3]
		
		db_conn.close()
		
		return user

	except:
		if db_conn is not None:
			db_conn.close()
		print("Exception in DB access:")
		print("-"*60)
		traceback.print_exc(file=sys.stderr)
		print("-"*60)

		return None


def db_getCategories():
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()
		
		# Buscamos el usuario por su email y devolvemos el nombre
		get_categories = select([db_table_genres.c.genreid, db_table_genres.c.name])
		db_result = db_conn.execute(get_categories)
		results = db_result.fetchall()
		
		categories = []
		for cat in results:
			categories.append({'id': cat[0], 'name': cat[1]})
		
		db_conn.close()
		
		return categories

	except:
		if db_conn is not None:
			db_conn.close()
		print("Exception in DB access:")
		print("-"*60)
		traceback.print_exc(file=sys.stderr)
		print("-"*60)

		return []

def __filmsToArray__(cursor):
	# Pasamos a un diccionario para facilitar la carga de las peliculas
	results = [{column:value for column, value in result.items()} for result in cursor]
	films = []
	for result in results:
		film = {}
		film['id'] = result['movieid']
		film['title'] = result['movietitle']
		film['image'] = result['image']
		film['year'] = result.get('year')
		film['synopsis'] = result['movierelease']
		films.append(film)

	return films

def db_getTopVentasFilms():
	# TODO: limit the amount of films we return
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()
		
		# Cargamos todas las peliculas de dicha categoria
		query = 'SELECT * FROM getTopVentas({})'.format(datetime.datetime.now().year-3)
		results = db_conn.execute(query)
		films = __filmsToArray__(results)
		
		db_conn.close()
		return films

	except:
		if db_conn is not None:
			db_conn.close()
		print("Exception in DB access:")
		print("-"*60)
		traceback.print_exc(file=sys.stderr)
		print("-"*60)

def db_getRecommendedFilms():
	# TODO: limit the amount of films we return
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()
		
		# Cargamos todas las peliculas de dicha categoria
		query = 'SELECT * FROM imdb_movies ORDER BY year DESC LIMIT 10'
		results = db_conn.execute(query)
		films = __filmsToArray__(results)
		
		db_conn.close()
		return films

	except:
		if db_conn is not None:
			db_conn.close()
		print("Exception in DB access:")
		print("-"*60)
		traceback.print_exc(file=sys.stderr)
		print("-"*60)



def db_getFilmsByCategoryId(categoryid):
	# TODO: limit the amount of films we return
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()
		
		# Cargamos todas las peliculas de dicha categoria
		query = 'SELECT * FROM genres NATURAL JOIN imdb_movies WHERE genreid = {} LIMIT 50'.format(categoryid)
		results = db_conn.execute(query)
		films = __filmsToArray__(results)
		
		db_conn.close()
		return films

	except:
		if db_conn is not None:
			db_conn.close()
		print("Exception in DB access:")
		print("-"*60)
		traceback.print_exc(file=sys.stderr)
		print("-"*60)

		return []

def db_getFilmsByTitle(title):
	# TODO: limit the amount of films we return
	# TODO: indicar que usamos full-text de postgres para que las búsquedas sean lo mejor posible
	# TODO Solucionat error nombre repetido: si buscas lion, por ejemplo, la pelicula está asociada a 27 categorias, con lo que sale 27 veces
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()
		
		# Cargamos todas las peliculas de dicha categoria
		query = "SELECT * FROM imdb_movies WHERE movietitle @@ to_tsquery('{}') LIMIT 50".format(title)
		results = db_conn.execute(query)
		films = __filmsToArray__(results)
		
		db_conn.close()
		return films

	except:
		if db_conn is not None:
			db_conn.close()
		print("Exception in DB access:")
		print("-"*60)
		traceback.print_exc(file=sys.stderr)
		print("-"*60)

		return []

def db_getFilmsByTitleAndCategoryId(title, categoryid):
	# TODO: limit the amount of films we return
	# TODO: indicar que usamos full-text de postgres para que las búsquedas sean lo mejor posible
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()
		
		# Cargamos todas las peliculas de dicha categoria
		query = "SELECT * FROM genres NATURAL JOIN imdb_movies WHERE movietitle @@ to_tsquery('{}') AND genreid = {} LIMIT 50".format(title, categoryid)
		results = db_conn.execute(query)
		films = __filmsToArray__(results)
		
		db_conn.close()
		return films

	except:
		if db_conn is not None:
			db_conn.close()
		print("Exception in DB access:")
		print("-"*60)
		traceback.print_exc(file=sys.stderr)
		print("-"*60)

		return []

def db_getFilmInfo(filmid):
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()
		
		# Cargamos todas las peliculas de dicha categoria
		query = "SELECT * FROM imdb_movies WHERE movieid = {} LIMIT 50".format(filmid)
		results = db_conn.execute(query)
		film = __filmsToArray__(results)[0] # Solo hay uno por ser movieid PK

		# Tres actores principales
		subquery = "SELECT * FROM imdb_actormovies NATURAL JOIN imdb_actors WHERE movieid = {} ORDER BY creditsposition LIMIT 3".format(filmid)
		query = "SELECT string_agg(actorname, '. ') FROM ({}) aux GROUP BY movieid".format(subquery)
		results = db_conn.execute(query).fetchone()
		film['actors'] = results[0] if results is not None else 'No info available'

		# Tres directores
		subquery = "SELECT * FROM imdb_directormovies NATURAL JOIN imdb_directors WHERE movieid = {} LIMIT 3".format(filmid)
		query = "SELECT string_agg(directorname, '. ') FROM ({}) aux GROUP BY movieid".format(subquery)
		results = db_conn.execute(query).fetchone()
		film['director'] = results[0] if results is not None else 'No info available'

		# Tres categorias
		subquery = "SELECT * FROM imdb_moviegenres NATURAL JOIN genres WHERE movieid = {} LIMIT 3".format(filmid)
		query = "SELECT string_agg(name, ', ') FROM ({}) aux GROUP BY movieid".format(subquery)
		results = db_conn.execute(query).fetchone()
		film['categories'] = results[0] if results is not None else 'No info available'


		# COMPROBAR
		film['price'] = -1
		print(film)
		
		db_conn.close()
		return film

	except:
		if db_conn is not None:
			db_conn.close()
		print("Exception in DB access:")
		print("-"*60)
		traceback.print_exc(file=sys.stderr)
		print("-"*60)

		return None