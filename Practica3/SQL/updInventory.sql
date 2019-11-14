-- Al añadir/actualizar/eliminar una fila orderdetail tenemos qe coger el orderid
-- y cambiar orderdate, netamount y totalamount de la tabla order.
-- Ademas, aprovechamos para cargar el precio del producto en orderdetail.

CREATE OR REPLACE FUNCTION actualizar_inventario() RETURNS TRIGGER AS $actualizar_inventario$
	DECLARE
	_prod_id orderdetail.prod_id%TYPE;
	_quantity orderdetail.quantity%TYPE;
	BEGIN
		-- Solo actualizamos cuando el cambio ha sido en el estado

		-- Para cada elemento de orderdetail con orderid=NEW.orderid
		-- Restar del inventario la cantidad de dicho elemento
		-- Usamos un LOOP porque tenemos que comprobar si es 0
		-- para guardar la alerta en ese caso

		FOR _prod_id, _quantity IN
			(SELECT prod_id, quantity FROM orderdetail WHERE orderid=NEW.orderid)
		LOOP
			UPDATE inventory SET stock=stock-_quantity WHERE prod_id=_prod_id;
			IF ((SELECT stock FROM inventory WHERE prod_id=_prod_id) <= 0) THEN
				INSERT INTO alertas(descripcion, alertdate) VALUES(CONCAT('Product with id ', _prod_id, ' has no items left.'), NOW());
			END IF;
		END LOOP;

		RETURN NEW;
	END;
$actualizar_inventario$ LANGUAGE plpgsql;

CREATE TRIGGER actualizar_inventario BEFORE UPDATE
    ON orders FOR EACH ROW
		WHEN (OLD.status IS NULL AND NEW.status = 'Paid')
    EXECUTE PROCEDURE actualizar_inventario();
