from flask import Flask, render_template, send_from_directory, request
import json
import os
import sys

app = Flask(__name__)
# TODO Eliminar esta ultima linea
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
DATA_FOLDER = os.path.join(app.root_path,'data/')

@app.route("/")
def index():
	return render_template('index.html')

@app.route("/home")
def home():
	catalogue_data = open(os.path.join(app.root_path,'data/catalogue.json'), encoding="utf-8").read()
	categories_data = open(os.path.join(app.root_path,'data/categories.json'), encoding="utf-8").read()
	catalogue_data = json.loads(catalogue_data)
	categories_data = json.loads(categories_data)
	recommended_films = catalogue_data
	best_seller_films = catalogue_data
	return render_template('home.html', recommended_films=recommended_films, best_seller_films=best_seller_films, categories_data=categories_data)


@app.route("/search",methods=['GET', 'POST'])
def search():
	catalogue_data = open(os.path.join(app.root_path,'data/catalogue.json'), encoding="utf-8").read()
	categories_data = open(os.path.join(app.root_path,'data/categories.json'), encoding="utf-8").read()
	catalogue_data = json.loads(catalogue_data)
	categories_data = json.loads(categories_data)

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
		print(category)



	sFilter = lambda x: True
	if category != None and term != None:
		print('Category and results')
		categoryFilter = lambda x: x['category'] == category['id']
		termFilter = lambda x: term.lower() in x['title'].lower()
		sFilter = lambda x: termFilter(x) and categoryFilter(x)
	elif category != None:
		print('Category')
		sFilter = lambda x: x['category'] == category['id']
	elif term != None:
		print('Results')
		sFilter = lambda x: term.lower() in x['title'].lower()
		
	catalogue_data = open(os.path.join(app.root_path,'data/catalogue.json'), encoding="utf-8").read()
	categories_data = open(os.path.join(app.root_path,'data/categories.json'), encoding="utf-8").read()
	catalogue_data = json.loads(catalogue_data)
	categories_data = json.loads(categories_data)

	catalogue_data = list(filter(sFilter, catalogue_data))

	return render_template('search.html', term=term, category=category, results=catalogue_data, categories_data=categories_data)

@app.route("/detail/<int:id>")
def detail(id):
	# TODO Leer todo el catalogo, buscar la pelicula con id=id en el catalogo,
	# y pasar la pelicula a la plantilla para que esta muestre la informacion

	dFilter = lambda x: x['id'] == id

	catalogue_data = open(os.path.join(app.root_path,'data/catalogue.json'), encoding="utf-8").read()
	catalogue_data = json.loads(catalogue_data)

	l = list(filter(dFilter, catalogue_data))
	film = l[0]

	dCatFilter = lambda x: x['id'] == film['category']

	categories_data = open(os.path.join(app.root_path,'data/categories.json'), encoding="utf-8").read()
	categories_data = json.loads(categories_data)

	l = list(filter(dCatFilter, categories_data))
	category = l[0]

	return render_template('detail.html', film=film, category=category)

#
#
@app.route("/data/<path:filename>")
def data(filename):
	return send_from_directory(DATA_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
	app.run(debug=True)
