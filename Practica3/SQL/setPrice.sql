-- Hacemos un join de orders, orderdetail y products
-- Calculamos la diferencia de años entre la fecha actual y la del order, llamemosla n
-- El precio del producto habrá incrementado en un factor 1.02 cada año => 1.02^n
-- El precio inicial es products.price/(1.02^n)
-- Actualizamos la tabla
WITH current_prices AS (
	SELECT products.price/(1.02^(DATE_PART('year', NOW()) - DATE_PART('year', orderdate))) AS price, orderdetail.orderid AS orderid, orderdetail.prod_id AS prod_id 
	FROM
		orders 
		NATURAL JOIN (orderdetail INNER JOIN products ON orderdetail.prod_id=products.prod_id)
	)


UPDATE orderdetail o 
SET price=ROUND(c.price::numeric,2) 
FROM current_prices c 
WHERE o.prod_id=c.prod_id AND o.orderid=c.orderid;
