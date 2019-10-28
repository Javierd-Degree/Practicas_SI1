## Memoria

### Estructura de la práctica

Hemos intentado organizar la práctica de la forma más estructurada y simple posible, de forma que en el archivo .zip entregado tenemos:

- El archivo *server.py* que contiene el código Python del servidor Flask implementado.
- La carpeta *data*, que incluye la información correspondiente a la base de datos de películas, es decir, un fichero .json que contiene el catálogo de películas, otro fichero .json que almacena la lista de categorías de películas disponibles, y una carpeta donde almacenar las carátulas de cada una de las películas de la base de datos.
- En la carpeta *static* guardamos los documentos css y las imágenes correspondientes a la página web en sí.
- En la carpeta *templates* almacenamos los documentos html de cada de una de las páginas.
- Por último, en la carpeta *usuarios* es donde almacenamos toda la información correspondiente a los usuarios del sistema, de forma que cada usuario tiene una carpeta con su nick, donde se guarda su historial etc. Comentar que la práctica se entrega con un usuario con nombre `Javier` y contraseña `12345678` que permite facilitar las pruebas en el sistema.

### Detalles de la implementación

En nuestro caso, habíamos implementado en la práctica anterior todas las páginas mediante un iframe embebido en un documento html que incluía las barras superior, inferior y lateral. En esta práctica, al usar *Jinja2* para generar las plantillas, hemos podido simplificar nuestro diseño considerablemente, usando bloques en la plantilla principal que luego podíamos sobreescribir.

De esta forma, todas páginas 'heredan' del fichero `index.html` en el que se encuentran las tres barras indicadas anteriormente.

#### Flask

Hemos desarrollado todo el servidor mediante Python3 y la librería Flask, que permite crear un servidor web básico con muchísima facilidad.

session para almacenar el carrito y la informacion del usuario loggeado

cookies para almacenar el nombre del ultimo usuario que se ha loggeado y poderlo devolver la proxima vez que queramos mostrar la pantalla de login

ACABAR

#### JQuery

Uno de los requisitos pedidos en el enunciado era la utilización de JQuery para implementar algunas funcionalidades.

En nuestro caso, hemos decidido enlazar JQuery a la última versión librería hosteada por Google, pues es bastante probable que ya esté en la caché del navegador usado por el usuario, permitiéndonos así agilizar la carga de la web.

Hemos usado la librería para tres cosas:

- Implementar en la página de registro, un medidor de fortaleza de la contraseña, que permite al usuario conocer posibles problemas de seguridad asociados a dicha contraseña.
- Permitir ocultar y mostrar en la pantalla Historial las compras hechas en un determinado día, empleando animaciones fluidas, de forma que el usuario no se satura de información al cargar la página web.
- Mostrar un aviso al usuario cuando se completa una compra con éxito o se añade un elemento al carrito de la compra, permitiendo a éste tener un feedback.

#### Ajax

Tal y como se pedía en el enunciado, hacemos uso de la AJAX para tener información continua del tráfico de usuarios en la web (generada de manera aleatoria realmente), que se recarga cada tres segundos. Esta información aparece en la barra superior de la web, justo debajo del nombre.

### Resultados