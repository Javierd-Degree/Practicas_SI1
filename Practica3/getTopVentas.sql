CREATE OR REPLACE FUNCTION getTopVentas(minDate NUMERIC)
    RETURNS TABLE(Año DOUBLE PRECISION, Pelicula VARCHAR, Ventas BIGINT)
AS $$
    DECLARE
    BEGIN
        CREATE OR REPLACE TEMPORARY VIEW orders_join AS (SELECT prod_id, DATE_PART('year', orderdate) as date, quantity FROM orderdetail NATURAL JOIN orders);

        RETURN QUERY (SELECT date, movietitle, sales FROM 
            products NATURAL JOIN imdb_movies NATURAL JOIN 
            (SELECT z.date, z.prod_id, z.sales
            FROM 
                (
                    SELECT date, max(sales) as top_sales
                    FROM (
                            SELECT date, prod_id, SUM(quantity) AS sales
                            FROM orders_join
                            GROUP BY date, prod_id
                        ) x
                    GROUP BY
                        date
                ) y
            JOIN
                (
                    SELECT date, prod_id, SUM(quantity) AS sales
                    FROM orders_join
                    GROUP BY date, prod_id
                ) z
            ON  y.date = z.date AND y.top_sales = z.sales
            WHERE z.date >= minDate) aux);

    END;
$$ LANGUAGE plpgsql;



