from flask import Flask, render_template, send_from_directory, request, session
import json
import os
import sys
import random
import hashlib
import re

app = Flask(__name__)
# TODO Eliminar esta ultima linea
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = '\x18\x19\xc3q\xfa\xb8\x80v\x1abf\xd8\xfd%(G\x95\xd7\xae\x9bv\xb0d\xf4'
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

def __getCategories__():
	with open(os.path.join(app.root_path,'data/categories.json'), encoding="utf-8") as f:
		categories_data = f.read()
		return json.loads(categories_data)

def __getBasket__():
	# session['basket'] stores a list of Films stored as in data/catalogue.json
	if 'shopping_cart' not in session:
		session['shopping_cart'] = []
	return session['shopping_cart']

def __addToBasket__(item):
	if 'shopping_cart' not in session:
		session['shopping_cart'] = [item]
	else:
		items = session['shopping_cart']
		items.append(item)
		session['shopping_cart'] = items

def __removeFromBasket__(item):
	if 'shopping_cart' not in session:
		session['shopping_cart'] = []
	else:
		basket = session['shopping_cart']
		for i in range(len(basket)):
			if basket[i]['id'] == item:
				del basket[i]
				break

		session['shopping_cart'] = basket

def __getUserHistory__(username):
	if not __isUser__(username):
		return []

	catalogue_data = __getCatalogue__()
	# Leemos el historial del usuario
	folder = os.path.join(app.root_path,'usuarios/'+username)
	print(os.path.join(folder, 'history.json'))
	try:
		with open(os.path.join(folder, 'history.json'), encoding="utf-8") as f:
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
			return user_history
	except Exception as e:
		# Si el fichero no existe, el usuario no tiene nada en el historial
		# Imprimimos por si acaso es otro tipo de error
		print('Excepcion en __getUserHistory__:\n{}'.format(e))
		return []

@app.route("/")
def index():
	catalogue_data = __getCatalogue__()
	categories_data = __getCategories__()
	recommended_films = catalogue_data
	best_seller_films = catalogue_data
	return render_template('home.html', user=__getUser__(), basket=__getBasket__(), recommended_films=recommended_films, best_seller_films=best_seller_films, categories_data=categories_data)

@app.route("/search",methods=['GET', 'POST'])
def search():
	catalogue_data = __getCatalogue__()
	categories_data = __getCategories__()

	term = None
	if 'term' in request.args:
		term = request.args.get('term')

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
			category = None
		else:
			l = list(filter(lambda x: x['id'] == category, categories_data))
			category = l[0]



	sFilter = lambda x: True
	if category != None and term != None:
		categoryFilter = lambda x: x['category'] == category['id']
		termFilter = lambda x: term.lower() in x['title'].lower()
		sFilter = lambda x: termFilter(x) and categoryFilter(x)
	elif category != None:
		sFilter = lambda x: x['category'] == category['id']
	elif term != None:
		sFilter = lambda x: term.lower() in x['title'].lower()

	catalogue_data = list(filter(sFilter, catalogue_data))

	return render_template('search.html', user=__getUser__(), basket=__getBasket__(), term=term, category=category, results=catalogue_data, categories_data=categories_data)

@app.route("/detail/<int:id>")
def detail(id):
	# Leer todo el catalogo, buscar la pelicula con id=id en el catalogo,
	# y pasar la pelicula a la plantilla para que esta muestre la informacion

	dFilter = lambda x: x['id'] == id

	catalogue_data = __getCatalogue__()
	categories_data = __getCategories__()

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
		return render_template('register.html')
	else:
		if 'name' in request.form and 'password' in request.form and \
			'mail' in request.form and 'creditCard' in request.form:
			# TODO Validar los datos
			name = request.form.get('name')
			password = request.form.get('password')
			mail = request.form.get('mail')
			creditCard = request.form.get('creditCard')
			cash = random.randint(0, 100)

			if __isUser__(name):
				error = 'User already exists'
				return render_template('register.html', basket=__getBasket__(), name=name, password=password,
										mail=mail, creditCard=creditCard, error=error)
			elif len(password) < 8:
				error = 'Password is too short.'
				return render_template('register.html', basket=__getBasket__(), name=name, password=password,
										mail=mail, creditCard=creditCard, error=error)
			elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', mail):
				error = 'Invalid e-mail.'
				return render_template('register.html', basket=__getBasket__(), name=name, password=password,
										mail=mail, creditCard=creditCard, error=error)


			folder = os.path.join(app.root_path,'usuarios/'+name)
			os.mkdir(folder)
			password = hashlib.md5(password.encode('utf-8')).hexdigest()

			user = {}
			user['name'] = name
			user['password'] = password
			user['mail'] = mail
			user['creditCard'] = creditCard
			user['cash'] = cash

			with open(os.path.join(folder, name+'.json'), 'w+', encoding="utf-8") as f:
				json.dump(user, f)

			session['user'] = user
			return index()

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
		return render_template('login.html')
	else:
		if 'name' in request.form and 'password' in request.form:
			name = request.form.get('name')
			password = request.form.get('password')
			if not __isUser__(name):
				return render_template('login.html', error='User does not exists', basket=__getBasket__())

			folder = os.path.join(app.root_path,'usuarios/'+name)
			user = None
			user_data = open(os.path.join(folder, name+'.json'), encoding="utf-8").read()
			user = json.loads(user_data)
			hashPassword = hashlib.md5(password.encode('utf-8')).hexdigest()
			if user['password'] != hashPassword:
				# La contraseña no es correcta
				print('{}, {}'.format(user['password'], hashPassword))
				return render_template('login.html', error='Incorrect password', basket=__getBasket__())

			session['user'] = user
			return index()
		else:
			return render_template('login.html', error='Not enough information', basket=__getBasket__())

@app.route("/addToBasket/<int:id>", methods=['GET', 'POST'])
def addToBasket(id):
	# TODO: Avisar sutilmente de que se ha añadido a la cesta
	dFilter = lambda x: x['id'] == id

	catalogue_data = __getCatalogue__()

	l = list(filter(dFilter, catalogue_data))
	film = l[0]
	__addToBasket__(film)
	return index()

@app.route("/removeFromBasket/<int:id>", methods=['GET', 'POST'])
def removeFromBasket(id):
	# TODO: Avisar sutilmente de que se ha añadido a la cesta
	__removeFromBasket__(id)

	return basket()


@app.route("/basket", methods=['GET', 'POST'])
def basket():
	return render_template('basket.html', user=__getUser__(), basket=__getBasket__())

@app.route("/logout", methods=['GET', 'POST'])
def logout():
	session['user'] = None
	return index()

@app.route("/history", methods=['GET'])
def history():
	return render_template('history.html',
	 						user=__getUser__(),
							history=__getUserHistory__(session['user']['name']))



#
#
@app.route("/data/<path:filename>")
def data(filename):
	return send_from_directory(DATA_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
	app.run(debug=True)
