from flask import Flask, render_template, send_from_directory
import json
import os
import sys

app = Flask(__name__)
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

#
#
@app.route("/data/<path:filename>")
def data(filename):
    return send_from_directory(DATA_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
