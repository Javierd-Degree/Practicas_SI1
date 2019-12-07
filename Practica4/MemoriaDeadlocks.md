#### Bloqueos
Para probar los bloqueos, insertamos los siguientes comandos en la shell de postgresql para modificar algunas orders y ponerlas con status NULL, de forma que se comporten como carritos:

```
UPDATE orders SET status=NULL where orderid=108;
UPDATE orders SET status=NULL where orderid=114;
UPDATE orders SET status=NULL where orderid=120;
UPDATE orders SET status=NULL where orderid=131;
UPDATE orders SET status=NULL where orderid=155;
```sql

Esto implica que hemos definido un carrito para los usuarios con customerid 1, 2, 3, 4 y 5.

Si llamamos primero desde la pagina web a eliminar un usuario, y acto seguido actualizamos el campo promo del usuario, al iniciar desde python una transaccion que modifica las entradas orderdetail del usuario, estas se bloquean, de forma que el trigger tiene que esperar a que la transaccion finalice (cosa que tarda mas de 40 segundos por el sleep) para poder ejecutarse

Como contestación al apartado h, durante el sleep los cambios hechso no son visibles pues el trigger está bloqueado y no ha podido hacer ningun cambio, y como la pagina web utiliza una transaccion, y esta no ha finalizado, sus cambios tampoco son visibles.

MIRAR EN PGAdmin el interbloqueo 
