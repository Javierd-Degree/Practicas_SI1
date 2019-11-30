
CREATE INDEX status_index ON orders(status);

ANALYZE orders;


SELECT COUNT(*)
FROM orders
WHERE status is NULL;

SELECT COUNT(*)
FROM orders
WHERE status ='Shipped';

SELECT COUNT(*)
FROM orders
WHERE status ='Paid';

SELECT COUNT(*)
FROM orders
WHERE status ='Processed';