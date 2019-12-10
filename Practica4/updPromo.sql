ALTER TABLE customers ADD COLUMN promo NUMERIC;

-- Consideramos que el porcentaje se guarda como un numero de 0 a 100, por ejemplo, 50%, no 0.5
CREATE OR REPLACE FUNCTION actualizar_promo() RETURNS TRIGGER AS $actualizar_promo$
	DECLARE
	BEGIN


		UPDATE orderdetail o1
		SET price=p.price*(1 - NEW.promo/100.0)
		FROM products p
		WHERE o1.prod_id=p.prod_id AND orderid IN (SELECT orderid FROM orders WHERE customerid=NEW.customerid AND status IS NULL);

		-- Dormimos 40 segundos
        RAISE NOTICE 'Dormimos';
		PERFORM pg_sleep(20);
        RAISE NOTICE 'Despertamos';

		UPDATE orders
		SET netamount=t.price
		FROM
			(SELECT orderid, SUM(price) as price FROM orderdetail
				WHERE orderid IN (SELECT orderid FROM orders WHERE customerid=NEW.customerid AND status IS NULL)
				GROUP BY orderid
			) t;

		RETURN NEW;
	END;
$actualizar_promo$ LANGUAGE plpgsql;

CREATE TRIGGER actualizar_promo AFTER UPDATE
    ON customers FOR EACH ROW
		WHEN (OLD.promo != NEW.promo OR OLD.promo IS NULL) 
    EXECUTE PROCEDURE actualizar_promo();
