### Customer
- Establecer nickname como primary key, eliminano repetidos
- Eliminar columnas innecesarias
- 

### Ventajas y desventajas del diseño dado
- imdb_moviecountries, imdb_moviegenres e imdb_movielanguages están representados como atributos múltiples y vamos a crear tres tablas de países, géneros e idiomas indexados por un id y luego una relación entre cada una de las tablas y la película a través de moieid.
- la tabla customers no está indexada por el nombre de usuario que es lo que nosotros empleamos en la aplicación por lo que vamos a tener que cambiarlo. Sin embargo es una buena decisión de diseño ya que te permite cambiar el nombre de usuario y el email pero necesitas recorrer toda la tala para logear al usuario.
- las tablas imdb_actormovies y orderdetail no tienen primary key