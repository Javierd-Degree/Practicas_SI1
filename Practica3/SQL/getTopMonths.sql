CREATE OR REPLACE FUNCTION getTopMonths(minQuantity NUMERIC, minPrice NUMERIC)
    RETURNS TABLE(year DOUBLE PRECISION, month DOUBLE PRECISION, productos BIGINT, importe NUMERIC)
AS $$
    DECLARE
    BEGIN


        RETURN QUERY SELECT DATE_PART('year', orderdate) as year, DATE_PART('month', orderdate) as month, SUM(quantity) as productos, SUM(price) as importe 
            FROM orderdetail NATURAL JOIN orders
            GROUP BY year, month
            HAVING SUM(quantity)>=minQuantity OR SUM(price)>=minPrice
            ORDER BY year, month;
    END;
$$ LANGUAGE plpgsql;
