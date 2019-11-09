WITH ventas AS (SELECT movieid, SUM(quantity) AS quantity FROM orderdetail INNER JOIN products ON products.prod_id=orderdetail.prod_id GROUP BY movieid)


WITH ventas_prod AS (SELECT SUM(t1.quantity) AS sales, t1.prod_id AS prod_id, t2.orderdate AS date FROM orderdetail t1 NATURAL JOIN
  (SELECT orderid, DATE_PART('year', orderdate) AS orderdate FROM orders) t2 
    WHERE t2.orderdate>=2015 GROUP BY t1.prod_id, t2.orderdate)

SELECT * FROM ventas_prod NATURAL JOIN products NATURAL JOIN imdb_movies;

SELECT v.date, string_agg(m.movietitle), MAX(v.sales) FROM ventas_prod v NATURAL JOIN products p NATURAL JOIN imdb_movies m GROUP BY v.date;

(SELECT SUM(t1.quantity) AS quantity, t2.date AS date, prod_id FROM orderdetail t1 NATURAL JOIN (SELECT orderid, DATE_PART('year', orderdate) AS date FROM orders) t2 NATURAL JOIN products p NATURAL JOIN imdb_movies m
GROUP BY t2.date, prod_id)

--- Lo mejor hasta ahora
--- Coger la tabla con el numero de unidades vendidas de cada prod_id en cada año
SELECT prod_id, DATE_PART('year', orderdate) as date, SUM(quantity) as sales FROM orderdetail NATURAL JOIN orders GROUP BY date, prod_id;

SELECT movietitle, date, sales FROM products NATURAL JOIN imdb_movies NATURAL JOIN (SELECT prod_id, DATE_PART('year', orderdate) as date, SUM(quantity) as sales FROM orderdetail NATURAL JOIN orders GROUP BY date, prod_id) aux;

-- No se si el MAX(prod_id esta bien)
SELECT date, MAX(sales) AS sales, MAX(prod_id) AS prod_id FROM (SELECT prod_id, DATE_PART('year', orderdate) as date, SUM(quantity) as sales FROM orderdetail NATURAL JOIN orders GROUP BY date, prod_id) aux  GROUP BY date;

SELECT movietitle, DATE_PART('year', orderdate) as date, SUM(quantity) AS sales FROM
	orders NATURAL JOIN orderdetail INNER JOIN products ON orderdetail.prod_id=products.prod_id NATURAL JOIN imdb_movies



WITH orders_join AS (SELECT prod_id, DATE_PART('year', orderdate) as date, quantity FROM orderdetail NATURAL JOIN orders WHERE status='Paid')

--- https://stackoverflow.com/questions/48133947/sql-select-most-popular-items-in-each-store
SELECT prod_id, date, SUM(quantity) AS sales
	FROM orders_join o
	GROUP BY date, prod_id
	HAVING SUM(quantity) = (SELECT SUM(quantity) AS sales_aux
						FROM orders_join
						WHERE date=o.date
						GROUP BY date, prod_id
						ORDER BY sales_aux DESC
						LIMIT 1)

	