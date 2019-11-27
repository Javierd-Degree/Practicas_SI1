-- Al añadir/actualizar/eliminar una fila orderdetail tenemos qe coger el orderid
-- y cambiar orderdate, netamount y totalamount de la tabla order.
-- Ademas, aprovechamos para cargar el precio del producto en orderdetail.

CREATE OR REPLACE FUNCTION actualizar_carrito() RETURNS TRIGGER AS $actualizar_carrito$
	DECLARE
	orderid_val orders.orderid%TYPE;
	BEGIN


		IF (TG_OP = 'INSERT') THEN
			NEW.price = (SELECT price FROM products WHERE prod_id=NEW.prod_id);
			orderid_val = NEW.orderid;
			-- Actualizamos el precio y la fecha
			UPDATE orders SET orderdate=NOW(), netamount=(netamount+NEW.price*NEW.quantity) WHERE orderid=NEW.orderid;
			

		ELSEIF (TG_OP = 'UPDATE') THEN
			NEW.price = (SELECT price FROM products WHERE prod_id=NEW.prod_id);
			orderid_val = OLD.orderid;
			-- Actualizamos el precio y la fecha
			UPDATE orders SET orderdate=NOW(), netamount=(netamount+NEW.price*NEW.quantity-OLD.price*OLD.quantity) WHERE orderid=OLD.orderid;

		ELSEIF (TG_OP = 'DELETE') THEN
			orderid_val = OLD.orderid;
			-- Actualizamos el precio y la fecha
			UPDATE orders SET orderdate=NOW(), netamount=(netamount-OLD.price*OLD.quantity) WHERE orderid=OLD.orderid;

			-- Volvemos a calcular el precio con impuestos
			UPDATE orders SET totalamount=ROUND((netamount+netamount*tax/100)::numeric, 2) WHERE orderid=orderid_val;
			-- Devolvemos OLD para asegurar que las filas se borran
			RETURN OLD;
		END IF;

		-- En cualquiera de los casos, volvemos a calcular el precio con impuestos
		UPDATE orders SET totalamount=ROUND((netamount+netamount*tax/100)::numeric, 2) WHERE orderid=orderid_val;

		RETURN NEW;
	END;
$actualizar_carrito$ LANGUAGE plpgsql;

CREATE TRIGGER actualizar_carrito BEFORE INSERT OR UPDATE OR DELETE
    ON orderdetail FOR EACH ROW 
    EXECUTE PROCEDURE actualizar_carrito();