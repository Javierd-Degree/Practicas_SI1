### A
a) 40msec
c) 1- Indice en orderdate. 32msec
   2- Indice en orderdate y otro en totalamount. 32msec
   3- Dos indices, en date_part('year', orderdate) y en date_part('month', orderdate) 15msec
   4- Los dos anteriores y otro en totalamount 15msec, no mejora

   El índice óptimo es el del apartado 4. Comparar las planificaciones

### B


### C
Primer Query: tarda unos 115msec. Se pueden mostrar poco a poco porque se asegura que el customerid no este en la tabla auxiliar creada. No se puede hacer en paralelo.
Segundo Query: ~130msec. No se puede mostrar poco porque el having se hace en todos a la vez, no poco a poco. Se puede hacer en paralelo.
Tercer Query: ~130msec. No se puede mostrar poco a poco porque hay que hacer el except, que requiere computar una tabla menos la otra. Se puede ejecutar en paralelo porque se calculan ambas tablas y luego el except.
