## Transacciones y deadlocks

Para este apartado, desactivamos las restricciones *ON DELETE CASCADE* referentes al cliente y sus
pedidos, manteniendo las foreign keys, y desarrollamos la función *delCustomer* cuya estructura se aporta en el fichero *database.py*. Además, programamos el script *updPromo.sql* con las condiciones pedidas.

### Apartados F.h - F.k

Para probar los bloqueos, insertamos los siguientes comandos en la shell de postgresql para modificar algunas orders y ponerlas con status NULL, de forma que se comporten como carritos:

```sql
UPDATE orders SET status=NULL where orderid=108;
UPDATE orders SET status=NULL where orderid=114;
UPDATE orders SET status=NULL where orderid=120;
UPDATE orders SET status=NULL where orderid=131;
UPDATE orders SET status=NULL where orderid=155;
```

Esto implica que hemos definido un carrito para los usuarios con customerid 1, 2, 3, 4 y 5.

Una vez hecho esto, accedemos a la página para borrar el cliente con customerid 1, y simultáneamente hacemos un update de su columna promo. Esto nos permite confirmar que durante el sleep los cambios hechos (más allá de la actualización de la columna promo del usuario) no son visibles pues el trigger está bloqueado y no ha podido hacer ningún cambio, y como la pagina web utiliza una transacción, y esta no ha finalizado, sus cambios tampoco son visibles.

Si llamamos primero desde la pagina web a eliminar un usuario, y acto seguido actualizamos el campo promo del usuario, al iniciar desde Python una transacción que modifica las entradas orderdetail del usuario, estas se bloquean, de forma que el trigger tiene que esperar a que la transacción finalice para poder ejecutarse. Esto deja un rastro en postgresql en forma de bloqueo, que se puede apreciar en la siguiente captura:

![](deadlock.png)

El tiempo que duerme el trigger está establecido por defecto en 20 segundos, si a la página web se le hace dormir unos segundos de más, el deadlock aparece también al ejecutar en primer lugar el update de la columna promo de customers, y en segundo lugar la petición a la web. Esto se debe a que una vez el trigger haya ejecutado el primer update, duerme los veinte segundos, en los cuales el servidor inicia la transacción bloqueando las filas de la tabla orders asociadas al usuario, y no las suelta hasta el final (por tener transacciones con aislamiento de nivel tres), para lo cual el servidor tendrá que dormir el tiempo indicado por el usuario. Una vez el servidor libere los locks, el trigger podrá finalizar.

Para solucionarlo, podríamos reducir el grado de aislamiento de las transacciones, sin embargo, esto quita gran parte del sentido, pues provocaría posibles fallos e inconsistencias en la base de datos.