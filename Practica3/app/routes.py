from flask import Flask, render_template, send_from_directory, request, session, redirect, url_for, make_response
import json
import os
import sys
import random
import hashlib
import re
from datetime import datetime
from app import app, database, errors

DATA_FOLDER = os.path.join(app.root_path,'data/')

def __getUser__():
	if 'user' in session:
		return session['user']
	return None

def __isUser__(name):
	folder = os.path.join(app.root_path,'usuarios/'+name)
	if os.path.isdir(folder):
		return True
	return False

def __getCatalogue__():
	with open(os.path.join(app.root_path,'data/catalogue.json'), encoding="utf-8") as f:
		catalogue_data = f.read()
		return json.loads(catalogue_data)

def __getBasket__():
	# session['basket'] stores a list of Films stored as in data/catalogue.json
	if 'shopping_cart' not in session:
		session['shopping_cart'] = []
		session.modified=True

	return session['shopping_cart']

def __addToBasket__(item):
	if 'shopping_cart' not in session:
		session['shopping_cart'] = [item]
		session['shopping_cart'][0]['quantity'] = 1
		session.modified=True
	else:
		flag = 0
		items = session['shopping_cart']
		for i in range(len(items)):
			if items[i]['id'] == item['id']:
				items[i]['quantity'] += 1
				flag = 1
				break
		if flag == 0:
			items.append(item)
			items[len(items)-1]['quantity'] = 1
		session['shopping_cart'] = items
		session.modified=True

def __removeFromBasket__(item):
	if 'shopping_cart' not in session:
		session['shopping_cart'] = []
		session.modified=True
	else:
		basket = session['shopping_cart']
		for i in range(len(basket)):
			if basket[i]['id'] == item:
				del basket[i]
				break

		session['shopping_cart'] = basket
		session.modified=True

def __removeOneFromBasket__(item):
	if 'shopping_cart' not in session:
		session['shopping_cart'] = []
		session.modified=True
	else:
		basket = session['shopping_cart']
		for i in range(len(basket)):
			if basket[i]['id'] == item:
				if basket[i]['quantity'] == 1:
					del basket[i]
				else:
					basket[i]['quantity'] -= 1
				break

		session['shopping_cart'] = basket
		session.modified=True

def __getUserHistory__(username):
	if not __isUser__(username):
		return []

	catalogue_data = __getCatalogue__()
	# Leemos el historial del usuario
	folder = os.path.join(app.root_path,'usuarios/'+username)
	print(os.path.join(folder, 'history.json'))
	try:
		with open(os.path.join(folder, 'history.json'), encoding="utf-8") as f:
			date_history = {}
			user_history = f.read()
			return json.loads(user_history)

	except Exception as e:
		# Si el fichero no existe, el usuario no tiene nada en el historial
		# Imprimimos por si acaso es otro tipo de error
		print('Excepcion en __getUserHistory__:\n{}'.format(e))
		return []

def __getUserHistoryFormatted__(username):
	# Un diccionario en el que agrupamos según
	# la fecha, los articulos que se han comprado en dicha fecha
	if not __isUser__(username):
		return []

	catalogue_data = __getCatalogue__()
	# Leemos el historial del usuario
	folder = os.path.join(app.root_path,'usuarios/'+username)
	print(os.path.join(folder, 'history.json'))
	try:
		with open(os.path.join(folder, 'history.json'), encoding="utf-8") as f:
			date_history = {}
			user_history = f.read()
			user_history = json.loads(user_history)
			# Cada elemento de user_history contiene el id de la pelicula, la fecha de compra
			# y el precio de compra. Cambiamos el id de la pelicula por la pelicula
			# en sí.
			for item in user_history:
				filmID = item['filmId']
				for film in catalogue_data:
					if film['id'] == filmID:
						item['film'] = film
						break

				if item['date'] not in date_history:
					date_history[item['date']] = []
				date_history[item['date']].append(item)


			return date_history
	except Exception as e:
		# Si el fichero no existe, el usuario no tiene nada en el historial
		# Imprimimos por si acaso es otro tipo de error
		print('Excepcion en __getUserHistoryFormatted__:\n{}'.format(e))
		return []

@app.route("/")
def index():
	message = None
	if 'message' in request.args:
		message = request.args.get('message')
	categories_data = database.db_getCategories()
	recommended_films = database.db_getRecommendedFilms()
	best_seller_films = database.db_getTopVentasFilms()
	return render_template('home.html', user=__getUser__(), basket=__getBasket__(),
							recommended_films=recommended_films,
							best_seller_films=best_seller_films,
							categories_data=categories_data,
							message=message)

@app.route("/search",methods=['GET', 'POST'])
def search():
	categories_data = database.db_getCategories()

	term = None
	if 'term' in request.args:
		term = request.args.get('term')
		if term == '':
			term = None

	category = None
	# Si no se ha indicado una nueva categoria, mantenemos la anterior
	if 'prev_category' in request.args and not ('category' in request.args):
		category = int(request.args.get('prev_category'))
	# Si se ha indicado una nueva, actualizamos
	if 'category' in request.args:
		category = int(request.args.get('category'))
	# Cargamos la categoria que corresponda
	if 'prev_category' in request.args or 'category' in request.args:
		if category == 0:
			print(category)
			category = None
		else:
			l = list(filter(lambda x: x['id'] == category, categories_data))
			category = l[0]


	if category != None and term != None:
		catalogue_data = database.db_getFilmsByTitleAndCategoryId(term, category['id'])
	elif category != None:
		catalogue_data = database.db_getFilmsByCategoryId(category['id'])
	elif term != None:
		catalogue_data = database.db_getFilmsByTitle(term)
	else:
		return redirect(url_for('index'))

	return render_template('search.html', user=__getUser__(), basket=__getBasket__(), term=term, category=category, results=catalogue_data, categories_data=categories_data)

@app.route("/detail/<int:id>")
def detail(id):
	# Leer todo el catalogo, buscar la pelicula con id=id en el catalogo,
	# y pasar la pelicula a la plantilla para que esta muestre la informacion

	dFilter = lambda x: x['id'] == id

	catalogue_data = __getCatalogue__()
	categories_data = database.db_getCategories()

	l = list(filter(dFilter, catalogue_data))
	film = l[0]

	dCatFilter = lambda x: x['id'] == film['category']

	l = list(filter(dCatFilter, categories_data))
	category = l[0]

	return render_template('detail.html', user=__getUser__(), basket=__getBasket__(), film=film, category=category)

@app.route("/register", methods=['GET', 'POST'])
def register():
	if request.method == 'GET':
		# Si el usuario va a la pagina de registrarse, se deslogea
		session['user'] = None
		session.modified=True
		return render_template('register.html', basket=__getBasket__())
	else:
		if 'name' in request.form and 'password' in request.form and \
			'mail' in request.form and 'creditCard' in request.form:

			name = request.form.get('name')
			password = request.form.get('password')
			mail = request.form.get('mail')
			creditCard = request.form.get('creditCard')
			cash = random.randint(0, 100)

			if len(password) < 8:
				error = 'Password is too short.'
				return render_template('register.html', basket=__getBasket__(), name=name, password=password,
										mail=mail, creditCard=creditCard, error=error)
			elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', mail):
				error = 'Invalid e-mail.'
				return render_template('register.html', basket=__getBasket__(), name=name, password=password,
										mail=mail, creditCard=creditCard, error=error)

			# Registramos al usuario en nuestra base de datos
			res = database.db_registerUser(name, password, mail, creditCard, cash)
			if res != errors.OK:
				return render_template('register.html', basket=__getBasket__(), name=name, password=password,
										mail=mail, creditCard=creditCard, error=errors.errorToString(res))

			user = {}
			user['name'] = name
			user['mail'] = mail
			user['creditCard'] = creditCard
			user['cash'] = cash

			session['user'] = user
			session.modified=True
			return redirect(url_for('index'))

		else:
			# Devolvemos el formulario con la informacion disponible
			error = 'Must complete all fields.'
			name = None

			if 'name' in request.form:
				name = request.form.get('name')
			password = None
			if 'password' in request.form:
				password = request.form.get('password')
			mail = None
			if 'mail' in request.form:
				mail = request.form.get('mail')
			creditCard = None
			if 'creditCard' in request.form:
				creditCard = request.form.get('creditCard')

			return render_template('register.html', basket=__getBasket__(), name=name, mail=mail,
									creditCard=creditCard, error=error)


@app.route("/login", methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		useremail = request.cookies.get('useremail')
		return render_template('login.html', useremail=useremail, basket=__getBasket__())
	else:
		if 'email' in request.form and 'password' in request.form:
			email = request.form.get('email')
			password = request.form.get('password')
			
			res = database.db_login(email, password)
			if res != errors.OK:
				return render_template('login.html', error=errors.errorToString(res), basket=__getBasket__())


			session['user'] = database.db_getUserDict(email)
			session.modified=True
			# Add a cookie to store the last logged users' email
			resp = make_response(redirect(url_for('index')))
			resp.set_cookie('useremail', email)
			return resp
		else:
			return render_template('login.html', error='Not enough information', basket=__getBasket__())

@app.route("/addToBasket/<int:id>", methods=['GET', 'POST'])
def addToBasket(id):
	dFilter = lambda x: x['id'] == id

	catalogue_data = __getCatalogue__()

	l = list(filter(dFilter, catalogue_data))
	film = l[0]
	__addToBasket__(film)
	return redirect(url_for('index', message='Item added'))

@app.route("/removeFromBasket/<int:id>", methods=['GET', 'POST'])
def removeFromBasket(id):
	__removeFromBasket__(id)
	return redirect(url_for('basket'))

@app.route("/incCount/<int:id>", methods=['GET', 'POST'])
def incCount(id):
	dFilter = lambda x: x['id'] == id

	catalogue_data = __getCatalogue__()

	l = list(filter(dFilter, catalogue_data))
	film = l[0]
	__addToBasket__(film)
	return redirect(url_for('basket'))

@app.route("/change_quant/<int:id>", methods=['GET', 'POST'])
def change_quant(id):
	if 'quant' in request.args:
		quant = request.args.get('quant')
		quant = int(quant)
		if quant == 0:
			__removeFromBasket__(id)
		else:
			basket = session['shopping_cart']
			for i in range(len(basket)):
				if basket[i]['id'] == id:
					basket[i]['quantity'] = quant
					session['shopping_cart'] = basket
					session.modified=True
					break
			print(basket[i]['id'])
	return redirect(url_for('basket'))

@app.route("/decCount/<int:id>", methods=['GET', 'POST'])
def decCount(id):
	__removeOneFromBasket__(id)
	return redirect(url_for('basket'))


@app.route("/basket", methods=['GET', 'POST'])
def basket():
	price = 0
	if request.method == 'GET':
		for film in session['shopping_cart']:
			price += film['price']*film['quantity']
			price = round(price, 2)
		return render_template('basket.html', user=__getUser__(), basket=__getBasket__(), price=price)

	if request.method == 'POST':
		user = session['user']
		name = user['name']
		history = __getUserHistory__(name)

		for film in session['shopping_cart']:
			price += film['price']*film['quantity']

		if price > user['cash']:
			cash_r = round(__getUser__()['cash'], 2)
			error = 'Not enough cash in your acount ({}$)'.format(cash_r)
			return render_template('basket.html', user=__getUser__(), basket=__getBasket__(), price=price, error=error)

		else:
			user['cash'] -= price
			user['cash'] = round(user['cash'], 2)
			for film in session['shopping_cart']:
				film_data = {}
				film_data['filmId'] = film['id']
				film_data['price'] = film['price']*film['quantity']
				film_data['quantity'] = film['quantity']
				film_data['date'] = datetime.now().strftime("%m/%d/%Y")
				film_data['time'] = datetime.now().strftime("%H:%M:%S")
				history.append(film_data)


			session['shopping_cart'] = []
			session.modified=True
			folder = os.path.join(app.root_path,'usuarios/'+name)
			with open(os.path.join(folder, 'datos.dat'), 'w', encoding='utf-8') as f:
				json.dump(user, f)
			with open(os.path.join(folder, 'history'+'.json'), 'w', encoding='utf-8') as f:
				json.dump(history, f)

			return redirect(url_for('index', message='Purchase completed'))

@app.route("/cash/", methods=['GET', 'POST'])
def cash():
	cash = request.form.get('cash')
	user = __getUser__()
	user['cash'] += float(cash)
	# Redondeamos a dos decimales
	user['cash'] = round(user['cash'], 2)
	session['user'] = user
	session.modified=True

	folder = os.path.join(app.root_path,'usuarios/'+user['name'])
	with open(os.path.join(folder, 'datos.dat'), 'w', encoding='utf-8') as f:
		json.dump(user, f)

	return redirect(url_for('history'))

@app.route("/logout", methods=['GET', 'POST'])
def logout():
	session['user'] = None
	session.modified=True
	return redirect(url_for('index'))

@app.route("/history", methods=['GET'])
def history():
	return render_template('history.html',
	 						user=__getUser__(),
							history=__getUserHistoryFormatted__(session['user']['name']),
							basket=__getBasket__())

# Devolvemos un numero aleatorio de usuarios logeados en la plataforma
@app.route("/numUsers", methods=['GET', 'POST'])
def numUsers():
	return str(random.randint(0, 100))


#
#
@app.route("/data/<path:filename>")
def data(filename):
	return send_from_directory(DATA_FOLDER, filename, as_attachment=True)
