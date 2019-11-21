CREATE OR REPLACE FUNCTION getTopVentas(minDate NUMERIC)
    RETURNS TABLE(prod_id INTEGER, description VARCHAR, price NUMERIC, movierelease VARCHAR, image VARCHAR, Año DOUBLE PRECISION, movietitle VARCHAR, Ventas BIGINT)
AS $$
    DECLARE
    BEGIN
        RETURN QUERY (SELECT p.prod_id, p.description, p.price, m.movierelease, m.image, date, m.movietitle, sales FROM
            products p NATURAL JOIN imdb_movies m NATURAL JOIN
            (SELECT z.date, z.prod_id, z.sales
            FROM
                (
                    SELECT date, max(sales) as top_sales
                    FROM (
                            SELECT t.date, t.prod_id, SUM(t.quantity) AS sales
                            FROM getTopVentasView t
                            GROUP BY date, t.prod_id
                        ) x
                    GROUP BY
                        date
                ) y
            JOIN
                (
                    SELECT t.date, t.prod_id, SUM(t.quantity) AS sales
                    FROM getTopVentasView t
                    GROUP BY date, t.prod_id
                ) z
            ON  y.date = z.date AND y.top_sales = z.sales
            WHERE z.date >= minDate) aux);

    END;
$$ LANGUAGE plpgsql;
