### Descripción de los archivos de entrega

A la hora de diseñar la página web, como el header, footer y la barra lateral no varían ningún momento (únicamente el header al logearse o cerrar sesión el usuario), hemos decidido usar un iframe para mostrar el contenido de cada página.

De esta forma, tenemos dos ficheros principales, *index.html* e *index_logged.html* que son los que almacenan el header (con el usuario logeado o no), el footer, la barra lateral y el iframe, mientras que el resto de ficheros almacenan únicamente el contenido a mostrar en el iframe. Esto permite que la navegación entre páginas sea mucho más cómoda para el usuario, y mucho más rápida, pues evitamos tener que recargar innecesariamente elementos que no han cambiado.

Para mejorar la experiencia de usuario, nos hemos encargado de añadir también algunas animaciones simples que permiten al usuario recibir un feedback cuando el puntero pasa por encima de un botón, o acciones similares.