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

def db_incrementUserCash(mail, quantity):
	# Solo debe llamarse una vez estamos seguros de que el usuario existe
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()

		# Buscamos el usuario por su email y devolvemos el nombre
		query = "UPDATE customers SET cash=cash+{} WHERE email='{}'".format(quantity, mail)
		db_conn.execute(query)
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

def db_getUserBasket(mail):
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()

		# En primer lugar, comprobamos si tiene una entrada de carrito (con status==NULL) en la base de datos, si no, la creamos
		query = "SELECT * FROM orders WHERE useremail='{}' AND status IS NULL".format(mail)
		cursor = db_conn.execute(query)
		if len(cursor.fetchall()) == 0:
			print('No hay una entrada de carrito para el usuario')
			# TODO No deberia hacer falta eso para establecer el orderid, se deberia hacer solo
			query = "INSERT INTO orders(useremail, status, orderdate) VALUES ('{}', NULL, NOW())".format(mail)
			db_conn.execute(query)


		query = "SELECT prod_id, quantity FROM orders NATURAL JOIN orderdetail WHERE useremail='{}' AND status IS NULL".format(mail)
		cursor = db_conn.execute(query)
		results = cursor.fetchall()

		if len(results) == 0:
			return []

		films = []
		for result in results:
			film = db_getFilmInfo(result[0])
			if film is None:
				continue

			film['quantity'] = result[1]
			films.append(film)

		db_conn.close()
		return films

	except:
		if db_conn is not None:
			db_conn.close()
		print("Exception in DB access:")
		print("-"*60)
		traceback.print_exc(file=sys.stderr)
		print("-"*60)

		return None

def db_addToUserBasket(mail, prod_id, quantity=1):
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()

		# En primer lugar, comprobamos si el producto ya está en el carrito del usuario
		query = "SELECT quantity, orderid FROM orders NATURAL JOIN orderdetail WHERE prod_id={} AND useremail='{}' AND status IS NULL".format(prod_id, mail)
		cursor = db_conn.execute(query)
		result = cursor.fetchone()
		if result:
			print('Ya añadido, sumamos')
			# Ya está añadido, sumamos
			query = "UPDATE orderdetail SET quantity=quantity+{} WHERE orderid={} AND prod_id={}".format(quantity, result[1], prod_id)
			db_conn.execute(query)
		else:
			print('No añadido, añadimos')
			# Añadimos el elemento a la tabla. Para ello, cogemos en primer lugar el orderid
			query = "SELECT orderid FROM orders WHERE useremail='{}' AND status IS NULL".format(mail)
			cursor = db_conn.execute(query)
			result = cursor.fetchone()
			if not result:
				print('Error al añadir: '+query)
				return errors.ERROR_INTERNAL_BASKET

			query = "INSERT INTO orderdetail VALUES ({}, {}, (SELECT price FROM products WHERE prod_id={} LIMIT 1),{})".format(result[0], prod_id, prod_id, quantity)
			db_conn.execute(query)


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


def db_completePurchase(mail):
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()

		# Calculamos el precio total de la compra, y comprobamos que sea superior al saldo del usuario
		user = db_getUserDict(mail)
		if user is None:
			return errors.ERROR_PURCHASE_NOT_LOGGED
		cash = user['cash']

		# Leemos el pecio total del pedido
		query = "SELECT totalamount FROM orders WHERE useremail='{}' AND status IS NULL".format(mail)
		cursor = db_conn.execute(query)
		result = cursor.fetchone()
		if not result or not result[0]:
			db_conn.close()
			print('El pedido no tiene precio')
			return errors.ERROR

		price = result[0]
		if cash < price:
			db_conn.close()
			return errors.ERROR_PURCHASE_NOT_ENOUGH_CASH

		# Marcamos el la entrada de orders como PAID y restamos el precio total del saldo del usuario
		query = "UPDATE orders SET status='PAID' WHERE useremail='{}' AND status IS NULL".format(mail)
		cursor = db_conn.execute(query)
		query = "UPDATE customers SET cash=cash-{} WHERE email='{}'".format(price, mail)
		cursor = db_conn.execute(query)

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

def db_setQuantityUserBasket(mail, prod_id, quantity):
		try:
			# Conexion a la base de datos
			db_conn = None
			db_conn = db_engine.connect()

			# En primer lugar, comprobamos si el producto ya está en el carrito del usuario
			query = "SELECT quantity, orderid FROM orders NATURAL JOIN orderdetail WHERE prod_id={} AND useremail='{}' AND status IS NULL".format(prod_id, mail)
			cursor = db_conn.execute(query)
			result = cursor.fetchone()
			if result:
				# Ya está añadido, modificamos la cantidad
				query = "UPDATE orderdetail SET quantity={} WHERE orderid={} AND prod_id={}".format(quantity, result[1], prod_id)
				db_conn.execute(query)
			else:
				# Añadimos el elemento a la tabla. Para ello, cogemos en primer lugar el orderid
				query = "SELECT orderid FROM orders WHERE useremail='{}' AND status IS NULL".format(mail)
				cursor = db_conn.execute(query)
				result = cursor.fetchone()
				if not result:
					return errors.ERROR_INTERNAL_BASKET

				query = "INSERT INTO orderdetail VALUES ({}, {}, (SELECT price FROM products WHERE prod_id={} LIMIT 1),{})".format(orderid, prod_id, prod_id, quantity)
				db_conn.execute(query)


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

def db_removeFromUserBasket(mail, prod_id):
		try:
			# Conexion a la base de datos
			db_conn = None
			db_conn = db_engine.connect()

			query = "DELETE FROM orderdetail WHERE prod_id={} AND orderid IN (SELECT orderid FROM orders WHERE useremail='{}' AND status IS NULL)".format(prod_id, mail)
			cursor = db_conn.execute(query)

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

def db_removeOneFromUserBasket(mail, prod_id):
		try:
			# Conexion a la base de datos
			db_conn = None
			db_conn = db_engine.connect()
			# Comprobamos si la cantidad es 1 (en este caso, habría que eliminar el artículo de la cesta) o superior (decrementar)
			query = "SELECT quantity, orderid FROM orders NATURAL JOIN orderdetail WHERE prod_id={} AND useremail='{}' AND status IS NULL".format(prod_id, mail)
			cursor = db_conn.execute(query)
			result = cursor.fetchone()
			if not result:
				return errors.ERROR_INTERNAL_BASKET

			res = errors.OK
			if result[0] == 1:
				res = db_removeFromUserBasket(mail, prod_id)
			else:
				query = "UPDATE orderdetail SET quantity=quantity-1 WHERE prod_id = {} AND orderid={}".format(prod_id, result[1])
				cursor = db_conn.execute(query)

			db_conn.close()
			return res

		except:
			if db_conn is not None:
				db_conn.close()
			print("Exception in DB access:")
			print("-"*60)
			traceback.print_exc(file=sys.stderr)
			print("-"*60)
			return errors.ERROR

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

def __filmsToArray__(cursor=None, results=None):
	# Pasamos a un diccionario para facilitar la carga de las peliculas
	if not results:
		results = [{column:value for column, value in result.items()} for result in cursor]
	films = []
	for result in results:
		film = {}
		film['id'] = result.get('prod_id')
		film['price'] = result.get('price')
		if film['price']:
			film['price'] = float(film['price'])
		film['title'] = result.get('movietitle')
		film['image'] = result.get('image')
		film['year'] = result.get('year')
		film['synopsis'] = result.get('movierelease')
		film['product_desc'] = result.get('description')
		if film['product_desc']:
			film['title'] += ' ({})'.format(film['product_desc'])
		films.append(film)

	return films

def db_getTopVentasFilms():
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
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()

		# Cargamos todas las peliculas de dicha categoria
		query = 'SELECT * FROM imdb_movies NATURAL JOIN products ORDER BY year DESC LIMIT 6'
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
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()

		# Cargamos todas las peliculas de dicha categoria
		query = 'SELECT * FROM genres NATURAL JOIN imdb_movies NATURAL JOIN products WHERE genreid = {} LIMIT 50'.format(categoryid)
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
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()

		# Cargamos todas las peliculas de dicha categoria
		query = "SELECT * FROM imdb_movies NATURAL JOIN products WHERE movietitle @@ to_tsquery('{}') LIMIT 50".format(title)
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
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()

		# Cargamos todas las peliculas de dicha categoria
		query = "SELECT * FROM genres NATURAL JOIN imdb_movies NATURAL JOIN products WHERE movietitle @@ to_tsquery('{}') AND genreid = {} LIMIT 50".format(title, categoryid)
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

def db_getFilmInfo(prodid):
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()

		# Cargamos todas las peliculas de dicha categoria
		query = "SELECT * FROM imdb_movies NATURAL JOIN products WHERE prod_id = {} LIMIT 50".format(prodid)
		cursor = db_conn.execute(query)
		# En este caso, necesitamos saber el id de pelicula, no solo del producto
		results = [{column:value for column, value in result.items()} for result in cursor]
		filmid = results[0]['movieid']
		film = __filmsToArray__(results=results)[0] # Solo hay uno por ser movieid PK

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

def db_getUserHistory(mail):
	try:
		# Conexion a la base de datos
		db_conn = None
		db_conn = db_engine.connect()


		# Leemos todos los pedidos completados del usuario
		query = "SELECT orderid, prod_id, price, quantity FROM orderdetail WHERE orderid IN (SELECT orderid FROM orders WHERE useremail='{}' AND status IS NOT NULL) ORDER BY orderid DESC".format(mail)
		cursor = db_conn.execute(query)
		results = cursor.fetchall()
		
		history = {}
		for order in results:
			item = {}
			item['price'] = order[2]
			item['quantity'] = order[3]

			query = "SELECT movietitle, image, description FROM products NATURAL JOIN imdb_movies WHERE prod_id={}".format(order[1])
			cursor = db_conn.execute(query)
			result = cursor.fetchone()
			if result is None:
				continue

			title = '{} ({})'.format(result[0], result[2])
			item['film'] = {'id': order[1], 'title': title, 'image': result[1]}
			if order[0] not in history:
				history[order[0]] = []

			history[order[0]].append(item)

		db_conn.close()
		return history

	except:
		if db_conn is not None:
			db_conn.close()
		print("Exception in DB access:")
		print("-"*60)
		traceback.print_exc(file=sys.stderr)
		print("-"*60)
		return None

# cabral.jungle@jmail.com