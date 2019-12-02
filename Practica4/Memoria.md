*Javier López Cano y Javier Delgado del Cerro*

# Practica 4 - Memoria

### A

Sin índices: 40msec

![](/home/javi/Documentos/Practicas_SI1/Practica4/A_a.png)

1- Indice en orderdate: 38msec

![](/home/javi/Documentos/Practicas_SI1/Practica4/A_c1.png)

2- Indice en orderdate y otro en totalamount: 32msec

![](/home/javi/Documentos/Practicas_SI1/Practica4/A_c2.png)

3- Dos indices, en date_part('year', orderdate) y en date_part('month', orderdate): 15msec

![](/home/javi/Documentos/Practicas_SI1/Practica4/A_c3.png)

4- Los dos anteriores y otro en totalamount: 15msec, no mejora

![](/home/javi/Documentos/Practicas_SI1/Practica4/A_c4.png)

El índice óptimo es el del apartado 3.

Al observar los planes de ejecución se observa que al introducir el índice en orderdate, el plan de ejecución no varía ya que el índice no se emplea, por lo que no existe una mejora notable de rendimiento.

Al añadir el de totalamount, este si se emplea mejorando ligeramente la eficiencia de la consulta como se observa en la disminución del coste de esta,aunque esta mejora es muy leve.

Por último, al emplear los índices sobre date_part, se ve que ambos se emplean directamente provocando una enorme bajada del coste de la consulta y aumentando notablemente su rendimiento. Al añadir ademas de los índices sobre date_part el índice en totalamount se observa que el plan de ejecución de la consulta no varía, ya que este índice no se emplea, lo que explica que el tiempo de ejecución de la query no cambie, y por tanto hace que este índice sea completamente inútil.


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
	
Observando los resultados se puede ver que lo que más aumenta el rendimiento de la query es el uso de índices. Las estadísticas aumentan el rendimiento notablemente también pero solo en el caso en el que ya se estan empleando índices. Esto puede deberse a que las estadísticas generadas son mucho más eficientes sobre tablas indexadas que si se realizan sobre tablas sin ningún tipo de índice.
Se observa que el caso en que el PREPARE empeora el rendimiento es el caso más rápido, esto puede ser debido a que en los casos en los que la consulta ya de por sí es muy rápida (en nuestro caso cuando se usan los índices y las estadísticas a la vez), es mayor el tiempo de ejecución del PREPARE que la mejora que se produce en la ejecución de la consulta cuando se usa este, haciendo que el tiempo total sea mayor.
Por este motivo el PREPARE puede ser conrtraproducente en los casos en que la consulta a realizar ya sea muy rápida.


### C
Primer Query: tarda unos 115msec. Se pueden mostrar poco a poco porque se asegura que el customerid no este en la tabla auxiliar creada, esto se observa en el plan de ejecución ya que a cada fila del "Subplan1" se le aplica el filtro y según este es aplicado se puede ir imprimiendo el resultado antes de seguir aplicando el filtro a las filas siguientes.. No se puede hacer en paralelo.

![](/home/javi/Documentos/Practicas_SI1/Practica4/C_1.png)



Segundo Query: ~130msec. No se puede mostrar poco porque el having se hace en todos a la vez, no poco a poco. Se puede hacer en paralelo ya que, como se obbserva en el plan de ejecución existen 2 sequential queries que se ejecutan en el mismo nivel de profundidad y son independientesentre sí, por lo que en caso de paralelizarse el proceso podrían ejecutarse al mimso tiempo sin problemas mejorando el tiempo de ejecución de la consulta.

![](/home/javi/Documentos/Practicas_SI1/Practica4/C_2.png)



Tercer Query: ~130msec. No se puede mostrar poco a poco porque hay que hacer el except, que requiere computar una tabla menos la otra. Se puede ejecutar en paralelo porque se calculan ambas tablas y luego el except, como se observa en el plan de ejecución del mismo modo que en la consulta anterior.

![](/home/javi/Documentos/Practicas_SI1/Practica4/C_3.png)



### D

Sentencia 1 sin index: 52msec

![D_1_sinAnalyze](/home/javi/Documentos/Practicas_SI1/Practica4/D_1_sinAnalyze.png)

Sentencia 2 sin index: 62msec

![D_2_sinAnalyze](/home/javi/Documentos/Practicas_SI1/Practica4/D_2_sinAnalyze.png)

Sentencia 1 con index: 58msec

![D_1IndexsinAnalyze](/home/javi/Documentos/Practicas_SI1/Practica4/D_1IndexsinAnalyze.png)

Sentencia 2 con index: 62msec

![D_2IndexsinAnalyze](/home/javi/Documentos/Practicas_SI1/Practica4/D_2IndexsinAnalyze.png)



CON ANALYZE:

Sentencia 1 con index: 14msec

![D_1ANALYZE](/home/javi/Documentos/Practicas_SI1/Practica4/D_1ANALYZE.png)

Sentencia 2 con index: 104msec

![D_2ANALYZE](/home/javi/Documentos/Practicas_SI1/Practica4/D_2ANALYZE.png)

Sentencia 3 con index: 32msec

![D_3ANALYZE](/home/javi/Documentos/Practicas_SI1/Practica4/D_3ANALYZE.png)

Sentencia 4 con index: 44msec

![](/home/javi/Documentos/Practicas_SI1/Practica4/D_4ANALYZE.png)

Se observa claramente que si no empleamos estadísticas, el uso de los índices no genera ninguna mejora apreciable en el rendimiento de la consulta. Sin embargo, al usar estadísticas, se observa que los índices comienzan a tener repercusión.

Sorprende que en la primera consulta el uso de estadísticas mejor anotablemente el rendimiento mientras que en la segundael rendimiento empeora considerablemente. Esto se debe a que ANALYZE colecciona estadísticas sobre las tablas de la base de datos para que luego sean consultadas para que la consulta se realice de forma más eficiente. Si los datos de la tabla generan unas estadísticas que faciliten la consulta a realizar la eficiencia mejorará, sin embargo en caso de que estas estadísticas no proporcionen datos relevantes, el tiempo de ejecución de la consulta puede aumentar debido al tiempo extra que lleva la consulta de las propias estadísticas recolectadas.

En los casos de las otras 2 consultas proporcionadas se observa que son rápidas con el uso de estadísticas pero menos qe la consulta 1, esto puede debere a que las estadísticas recolectadas en el ANALYZE para estas 2 consultas (los valores de status Paid y status Processed) sean menos resolutorias y por tato, aunque ayuden a mejorar la eficiencia de la consulta, no sean capaces de mejorarla hasta el mismo punto que la primera consulta.

El plan de ejecución de las 2 primeras consultas es el mismo hasta que se ejecuta el analyze ya que ambas consultas comprueban las mismas columnas de las mismas tablas, y lo hacen en el mismo orden al estas escritas de forma prácticamente idéntica. Sin embargo esto varía al generar las estadísticas ya que, aunque las consultas siguen siendo las mismas, las estadísticas generadas para el caso en el que el status es NULL o el status es Paid serán distintas, haciendo que tras consultar las estadísticas se optimize la consulta modificando su plan de ejecución, y, por tanto, los planes de ejecución de las consultas tras el analyze son diferentes.


