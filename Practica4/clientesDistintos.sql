-- Creamos los tres indices que serian mas eficientes
CREATE INDEX test_1 ON orders(date_part('year', orderdate));
CREATE INDEX test_2 ON orders(date_part('m', orderdate));
CREATE INDEX test_3 ON orders(totalamount);

-- Query pedido
SELECT COUNT(DISTINCT customerid)
FROM orders
WHERE date_part('year', orderdate) = 2015 AND date_part('month', orderdate) = 4 AND totalamount > 100;
