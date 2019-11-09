SELECT DATE_PART('year', orderdate) as year, DATE_PART('month', orderdate) as month, SUM(quantity) as productos, SUM(price) as importe 
FROM orderdetail NATURAL JOIN orders
GROUP BY year, month
HAVING SUM(quantity)>10000 OR SUM(price)>100000;
