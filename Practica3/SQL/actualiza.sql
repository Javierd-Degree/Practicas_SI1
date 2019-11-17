-- Antes de nada, añadimos la columna useremail a la tabla orders
ALTER TABLE orders ADD COLUMN useremail CHARACTER VARYING(50);
UPDATE orders o SET useremail=c.email FROM customers c WHERE o.customerid=c.customerid;

-- ===== CUSTOMERS =====
-- Cambiamos la clave primaria
ALTER TABLE customers DROP CONSTRAINT IF EXISTS customers_pkey;
ALTER TABLE customers ADD CONSTRAINT customers_pkey PRIMARY KEY(email);


-- Borramos columnas innecesarias
ALTER TABLE customers DROP COLUMN IF EXISTS customerid;
ALTER TABLE customers DROP COLUMN IF EXISTS gender;
ALTER TABLE customers DROP COLUMN IF EXISTS income;
ALTER TABLE customers DROP COLUMN IF EXISTS firstname;
ALTER TABLE customers DROP COLUMN IF EXISTS lastname;
ALTER TABLE customers DROP COLUMN IF EXISTS address1;
ALTER TABLE customers DROP COLUMN IF EXISTS address2;
ALTER TABLE customers DROP COLUMN IF EXISTS city;
ALTER TABLE customers DROP COLUMN IF EXISTS state;
ALTER TABLE customers DROP COLUMN IF EXISTS zip;
ALTER TABLE customers DROP COLUMN IF EXISTS country;
ALTER TABLE customers DROP COLUMN IF EXISTS region;
ALTER TABLE customers DROP COLUMN IF EXISTS phone;

-- Creamos columna para el cash
ALTER TABLE customers ADD COLUMN cash INTEGER NOT NULL DEFAULT 0;
-- Creamos la base de datos para las tarjetas y la rellenamos
CREATE TABLE creditcard (creditcard CHARACTER VARYING(50) PRIMARY KEY,
	creditcardtype CHARACTER VARYING(10),
	creditcardexpiration CHARACTER VARYING(50));
INSERT INTO creditcard SELECT creditcard, creditcardtype, creditcardexpiration FROM customers;
-- Eliminamos las filas creditcardtype, creditcardexpiration de consumer y hacemos que creditcard sea FK
ALTER TABLE customers DROP COLUMN IF EXISTS creditcardtype;
ALTER TABLE customers DROP COLUMN IF EXISTS creditcardexpiration;
ALTER TABLE customers ADD CONSTRAINT creditcard_fkey FOREIGN KEY (creditcard)
	REFERENCES creditcard (creditcard) MATCH SIMPLE;

-- ===== ORDERDETAIL =====
-- Renombramos la tabla para crear una nueva igual, pero sin repeticiones en el par
-- orderid, prod_id
ALTER TABLE orderdetail RENAME TO  orderdetailaux;
CREATE TABLE orderdetail(
  orderid integer NOT NULL,
  prod_id integer NOT NULL,
  price numeric,
  quantity integer NOT NULL
);
INSERT INTO orderdetail SELECT orderid, prod_id, MIN(price), SUM(quantity)
	FROM orderdetailaux GROUP BY orderid, prod_id;
-- Borramos la base de datos auxiliar
DROP TABLE orderdetailaux;
-- Establecer orderid, prod_id como PK
ALTER TABLE orderdetail ADD CONSTRAINT orderdetail_pkey PRIMARY KEY (orderid, prod_id);
-- Establecer orderid como FK y usarlo como index
ALTER TABLE orderdetail ADD CONSTRAINT orderid_fkey FOREIGN KEY (orderid)
	REFERENCES orders (orderid) MATCH SIMPLE;
-- Establecer prod_id como FK
ALTER TABLE orderdetail ADD CONSTRAINT prod_id_fkey FOREIGN KEY (prod_id)
	REFERENCES products (prod_id) MATCH SIMPLE;

-- ===== INVENTORY =====
-- Establecer la columna prod_id como una foreign key
ALTER TABLE inventory ADD CONSTRAINT prod_id_fkey FOREIGN KEY (prod_id)
	REFERENCES products (prod_id) MATCH SIMPLE;

-- ===== ORDERS =====
-- Establecer la columna useremail como una foreign key y borrar consumerid
ALTER TABLE orders ADD CONSTRAINT useremail_fkey FOREIGN KEY (useremail)
	REFERENCES customers (email);
ALTER TABLE orders DROP COLUMN IF EXISTS customerid;

-- ===== IMDB_MOVIES =====
-- Añadimos una columna llamada image y la rellenamos con la dirección una imagen por defecto
ALTER TABLE imdb_movies ADD COLUMN image CHARACTER VARYING(256) NOT NULL CONSTRAINT df_movies_image DEFAULT 'default.jpg';

-- ===== IMDB_ACTORMOVIES =====
-- Hacemos que actorid y movieid sean FKs
ALTER TABLE imdb_actormovies ADD CONSTRAINT actorid_fkey FOREIGN KEY (actorid)
	REFERENCES imdb_actors (actorid);
ALTER TABLE imdb_actormovies ADD CONSTRAINT movieid_fkey FOREIGN KEY (movieid)
	REFERENCES imdb_movies (movieid);
-- Crear un primary key con la tupla (movieid, actorid, character)
ALTER TABLE imdb_actormovies ADD CONSTRAINT triple_pkey PRIMARY KEY(movieid, actorid, character);

-- ===== imdb_moviecountries =====
-- Creamos una tabla con id que actua como PK y el pais
CREATE TABLE countries (countryid SERIAL PRIMARY KEY, name CHARACTER VARYING(32) UNIQUE NOT NULL);
INSERT INTO countries(name) SELECT DISTINCT(country) from imdb_moviecountries;
-- Modificamos la tabla imdb_moviecountries para añadir un countryid y eliminar country
ALTER TABLE imdb_moviecountries ADD COLUMN countryid INTEGER;
UPDATE imdb_moviecountries t1 SET countryid=t2.countryid FROM countries t2 WHERE t1.country=t2.name;
ALTER TABLE imdb_moviecountries ADD CONSTRAINT countryid_fkey FOREIGN KEY (countryid)
	REFERENCES countries (countryid);
ALTER TABLE imdb_moviecountries DROP COLUMN country;


-- ===== imdb_moviegenres =====
-- Creamos una tabla con id que actua como PK y el genero
CREATE TABLE genres (genreid SERIAL PRIMARY KEY, name CHARACTER VARYING(32) UNIQUE NOT NULL);
INSERT INTO genres(genreid, name) VALUES (0, 'All categories');
INSERT INTO genres(name) SELECT DISTINCT(genre) from imdb_moviegenres;
-- Modificamos la tabla imdb_moviegenres para añadir un genreid y eliminar genre
ALTER TABLE imdb_moviegenres ADD COLUMN genreid INTEGER;
UPDATE imdb_moviegenres t1 SET genreid=t2.genreid FROM genres t2 WHERE t1.genre=t2.name;
ALTER TABLE imdb_moviegenres ADD CONSTRAINT genreid_fkey FOREIGN KEY (genreid)
	REFERENCES genres (genreid);
ALTER TABLE imdb_moviegenres DROP COLUMN genre;

-- ===== imdb_movielanguages =====
-- Creamos una tabla con id que actua como PK y el language
CREATE TABLE languages (languageid SERIAL PRIMARY KEY, name CHARACTER VARYING(32) UNIQUE NOT NULL);
INSERT INTO languages(name) SELECT DISTINCT(language) from imdb_movielanguages;
-- Modificamos la tabla imdb_movielanguages para añadir un languageid y eliminar language
ALTER TABLE imdb_movielanguages ADD COLUMN languageid INTEGER;
UPDATE imdb_movielanguages t1 SET languageid=t2.languageid FROM languages t2 WHERE t1.language=t2.name;
ALTER TABLE imdb_movielanguages ADD CONSTRAINT languageid_fkey FOREIGN KEY (languageid)
	REFERENCES languages (languageid);
ALTER TABLE imdb_movielanguages DROP COLUMN language;

-- ===== ALERTAS =====
-- Creamos una nueva tabla llamada alertas
CREATE TABLE alertas (alertid SERIAL PRIMARY KEY, descripcion CHARACTER VARYING(256) NOT NULL, alertdate TIMESTAMP);

-- ===== VIEWS =====
-- Vista usada por getTopVentas
CREATE VIEW getTopVentasView AS (SELECT prod_id, DATE_PART('year', orderdate) as date, quantity FROM orderdetail NATURAL JOIN orders);
-- Vista usada por setOrderAmount
CREATE VIEW setOrderAmountView AS (SELECT orderdetail.orderid AS orderid, SUM(orderdetail.price*orderdetail.quantity) AS price FROM orderdetail WHERE orderdetail.orderid=orderid GROUP BY orderid);
