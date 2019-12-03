ALTER TABLE customers ADD COLUMN promo NUMERIC;


-- Consideramos que el porcentaje se guarda como un numero de 0 a 100, por ejemplo, 50%, no 0.5
CREATE OR REPLACE FUNCTION actualizar_carrito() RETURNS TRIGGER AS $actualizar_carrito$
	DECLARE
	BEGIN
		UPDATE orderdetail
		SET price=p.price*(1 - NEW.promo/100)
		FROM orderdetail o INNER JOIN products p ON o.prod_id=p.prod_id
		WHERE orderid IN (SELECT orderid FROM orders WHERE customerid=OLD.customerid AND status is NULL);
		

		RETURN NEW;
	END;
$actualizar_carrito$ LANGUAGE plpgsql;

CREATE TRIGGER actualizar_carrito AFTER UPDATE
    ON customers FOR EACH ROW
		WHEN (OLD.promo != NEW.promo)
    EXECUTE PROCEDURE actualizar_carrito();