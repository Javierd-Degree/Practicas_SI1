### A
a) 40msec
c) 1- Indice en orderdate. 32msec
   2- Indice en orderdate y otro en totalamount. 32msec
   3- Dos indices, en date_part('year', orderdate) y en date_part('month', orderdate) 15msec
   4- Los dos anteriores y otro en totalamount 15msec, no mejora

   El índice óptimo es el del apartado 4. Comparar las planificaciones


### B

c)	sin prepare: 237msec
	con prepare: 220msec

d)	sin estadísticas:
		con índices:
			sin prepare: 158msec
			con prepare: 144msec

	con estadísticas en orders:
		con índices:
			sin prepare: 54msec
			con prepare: 78msec
		sin índices:
			sin prepare: 242msec
			con prepare: 224msec

	Se observa que el caso en que el PREPARE empeora el rendimiento es el caso más rápido, esto puede ser debido a que en los casos en los que la consulta ya de por sí es muy rápida (en nuestro caso cuando se usan los índices y las estadísticas a la vez), es mayor el tiempo de ejecución del PREPARE que la mejora que se produce en la ejecución de la consulta cuando se usa este, haciendo que el tiempo total sea mayor.
	Por este motivo el PREPARE puede ser conrtraproducente en los casos en que la consulta a realizar ya sea muy rápida.


### C
Primer Query: tarda unos 115msec. Se pueden mostrar poco a poco porque se asegura que el customerid no este en la tabla auxiliar creada. No se puede hacer en paralelo.
Segundo Query: ~130msec. No se puede mostrar poco porque el having se hace en todos a la vez, no poco a poco. Se puede hacer en paralelo.
Tercer Query: ~130msec. No se puede mostrar poco a poco porque hay que hacer el except, que requiere computar una tabla menos la otra. Se puede ejecutar en paralelo porque se calculan ambas tablas y luego el except.


### D
Sentencia 1 sin index: 52msec
Sentencia 2 sin index: 62msec

Sentencia 1 con index: 58msec
Sentencia 2 con index: 62msec

CON ANALYZE:

Sentencia 1 con index: 14msec
Sentencia 2 con index: 104msec

Sentencia 3 con index: 32msec
Sentencia 4 con index: 44msec

TODO:COMENTAR


