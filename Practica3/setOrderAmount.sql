
WITH total_prices AS (SELECT orderdetail.orderid AS orderid, SUM(orderdetail.price) AS price FROM orderdetail WHERE orderdetail.orderid=orderid GROUP BY orderid)

UPDATE orders o SET netamount=p.price FROM total_prices p WHERE o.orderid=p.orderid;

UPDATE orders o SET totalamount=o.netamount+o.netamount*o.tax/100;
