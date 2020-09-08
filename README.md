# Metro-dijkstra
Implantacion de algoritmo dijkstra para obtener el camino mínimo aplicado a infraestructuras de metro de diversas cuidades

### Objetivo:
Se pretende construir una herramienta que calcule rutas óptimas de metro entre un origen y un destino a partir de la carga un fichero mapa de la red de suburbano en formato texto.

### Introducción:
Empezaré diciendo que NO soy especialista en materia de suburbanos y dispongo de otra información sobre ello que la que he encontrado buscando en internet. No me obliga ningún trabajo concreto ni propongo ninguna modelo de solución, tan solo me mueve mi interés por la automatización, la aplicación de algoritmos a los problemas del mundo real, la admiración que me producen los mapas de metro y el deseo de compartirlo con otras personas a las que este trabajo pueda ayudar en su actividad profesional, formativa, o que simplemente, como yo, sientan curiosidad por el desarrollo de soluciones programáticas.
A lo largo del texto haré referencia a diversas instalaciones de metro de ciudades del mundo e incluiré mis propios mapas de algunas de ellas. Algunas las conozco como “usuario avanzado” (Madrid o Paris), otras sólo circunstancialmente como “turista” (Londres, New York, Barcelona,…) y otras no las conozco más allá de la información publicada (la mayoría), por tanto ruego al lector que sea indulgente con las imprecisiones o errores que haya podido cometer en la interpretación de la información publicada y de sus casuísticas particulares.

### Planteamiento:
Plantearé los ficheros de mapa como listados de nombres de estaciones en el mismo orden en que se encuentran en el mapa y agrupadas por líneas (con las particularidades que se indicarán a lo largo del presente texto). El modelo básico de un plano contendrá una relación secuencial de estaciones dentro de cada línea, con una estación de inicio y otra de final. Cada línea se identificará con un indicador de comienzo de línea (“#”) y el nombre de la  línea encabezando la lista de estaciones que la forman. Un mismo nombre de estación en dos líneas diferentes se interpreta como un transbordo bidireccional entre ambas líneas. Además, como ya se ha mencionado, los ficheros de los planos de metro se construirán exclusivamente con información pública, (planos oficiales, descripciones de líneas y estaciones que se encuentran en las webs específicas de cada servicio de metropolitano y en otras fuentes públicas de uso común, tipo Wikipedia). A continuación se muestra un ejemplo esquematizado de fichero de mapa realizado con esta descripción:

![imagen1](https://github.com/rogazan/Metro-dijkstra/blob/master/images/image1.jpg)

El proceso de lectura del plano trasladará su información a la estructura de datos necesaria para generar un grafo tratable por algortimo de Dijkstra (descrito por primera vez por Edsger Dijkstra, en 1.959).

Si bien esta es una aproximación válida, la intención es ir un poco más allá y construir una implantación más próxima a la realidad de las redes de metro buscando la manera de 
automatizar las diversas particularidades que se encuentran en las redes de metropolitano de ciudades del mundo.

Con este planteamiento, cada estación se traducirá en un nodo único con dos atributos: Uno será el “Nombre” y otro será una lista de nodos “vecinos” con los que tiene tramos comunes. Por ejemplo, una instancia de nodo estación podría definirse como:

    {nombre: ”Gran Vía”, vecinos: [“Tribunal”, “Sol”, “Callao”, “Chueca”]}

Este es un ejemplo real del metro de Madrid. Los dos primeros vecinos pertenecen a la línea 1 (Celeste), y los dos últimos pertenecen a la línea 5 (Verde). Nótese que en la información del nodo NO se especifica la línea a la que pertenece la estación ni sus vecinos, lo único que aquí importa es que el nodo informa de que desde “Gran Vía” podemos desplazarnos en un único salto a cualquiera de los cuatro vecinos. En este punto de la aproximación el concepto de línea no sirve para nada más que para interpretar el fichero de mapa, entendiendo que cada estación tiene por vecinos al anterior y al posterior de todas las líneas que concurren en la estación (salvo la excepción del comienzo y final de línea, que solo tendrán un vecino). Una vez aplicado ese razonamiento, podemos olvidar el concepto línea para buscar rutas, lo que puede resultar chocante pero así de simple queda la cosa.

Y una vez expuesto el concepto básico, comenzamos a expandirlo con las particularidades del tratamiento encontradas:

#### Transbordos:
Si establecemos cada estación como un nodo del grafo y damos un peso similar a todos los tramos que enlazan las estaciones, estaremos ignorando el coste que suponen los incómodos transbordos que todos sufrimos.

Imaginemos un trazado similar al del gráfico siguiente y que el peso del tramo (entendido como el tiempo que invierte el metro en recorrer el trayecto entre dos estaciones) es igual en todos los casos:

![imagen2](https://github.com/rogazan/Metro-dijkstra/blob/master/images/image2.jpg)

Si solo contemplamos los enlaces entre las estaciones sin más consideración, un trayecto desde “Estación 1” a “Estación 5” se podrá calcular como una ruta en la secuencia:

    1 > 2 > 3 > 4 >  5 (4 tramos de igual peso), 

Pero también podrá calcularse como otra ruta en la secuencia:

    1 > 2 > 7 > 4 > 5 (igualmente 4 tramos del mismo peso).

De esta manera se obtienen dos trayectos de peso idéntico dado que el trayecto se está calculando en función exclusiva del número de estaciones recorridas:

    Trayecto = f(num_estaciones)

Pero cualquier persona que haya usado el metro sabe que no es lo mismo hacer un recorrido de 4 estaciones sin cambiar de línea que hacer el mismo viaje con el mismo número de tramos pero haciendo dos trasbordos, es decir, que un trayecto optimo adaptado al viajero “humano” debería replantearse como:

    trayecto = f(num_estaciones, num_transbordos).

Una primera idea puede llevar a pensar en gestionar los pesos de los enlaces, pero se descarta inmediatamente dado que el peso entre dos nodos debe ser estático “per se” y no cabe ninguna revaloración en base a lo que se haya hecho antes o lo que se hará después de recorrer el tramo.

Para dar solución al tema de los transbordos se redefine el concepto de “Estación” a otro más complejo, de modo que ya no se tratará de un nodo único sino que pasará a ser un conjunto de nodos con enlaces internos entre ellos. Así, una estación tendrá un nodo que podemos denominar “vestíbulo”, cuyo nombre será el de la propia estación, y N nodos que podemos denominar “andenes” (tantos como líneas pasen por la estación), cuyos nombres estarán formados por una concatenación del nombre de la estación y de la línea a la que sirven. En cuanto a los enlaces, el nodo vestíbulo contará con enlaces bidireccionales con todos los andenes, pero no existirán enlaces entre los distintos andenes de la misma estación. Se sintetiza en el gráfico siguiente:

![imagen3](https://github.com/rogazan/Metro-dijkstra/blob/master/images/image3.jpg)

Con esta interpretación, una lista de los nodos directamente asociados a la estación quedará así:

    {Nombre: “Estacion2”, Vecinos : [“Estacion2-Roja”, “Estacion2-Azul”]},
    {Nombre: “Estacion2-Roja”, Vecinos : [“Estacion2”, “Estacion1-Roja”, “Estacion3-Roja”]},
    {Nombre: “Estacion2-Azul”, Vecinos : [“Estacion2”, “Estacion1-Azul”, “Estacion3-Azul”]}

Se debe considerar que el viajero siempre accede a la red de metro a través del vestíbulo de la estación de origen y lo abandona a través del vestíbulo de la estación de destino y además debe especificarse un peso diferente para los tramos Vestíbulo–andén (los que se recorren caminando) y para los tramos de metro entre andenes de estaciones contiguas (los que se recorren en tren). Considerando las siguientes abreviaturas:

    E = Estación
    V = Vestíbulo
    A = azul
    R = rojo
    Pva = Peso para los tramos Vestíbulo-Andén
    Paa = Peso para los tramos de metro entre andenes de estaciones contiguas.

En el ejemplo primero, el sistema contemplaría el primer camino así:

    Camino1 = E1V > E1A > E2A > E3A > E4A > E5A > E5V 
    Camino1 = 2 * Pva + 4 * Paa

Mientras que el segundo camino será:

    Camino2 = E1V > E1A > E2A > E2V > E2R > E7R > 44R > E4V > E4A > E5A > E5V
    Camino2 = 6 * Pva + 4 * Paa

Es evidente que el algoritmo decidirá el Camino1 como el adecuado por su peso inferior al del Camino2, con

    diferencia = 4 * Pva

Que es justamente el peso que asignamos a los dos transbordos (2 * Pva por cada transbordo)
Con carácter general tendremos un cálculo para cualquier camino X:

    CaminoX = entrada + salida + suma(Transbordos) + suma(Recorridos en trenes)
    CaminoX = (2 * Pav) + (2 * Pav * num_transbordos) + ((num_estaciones – 1) * Paa) 
    CaminoX = (2 * Pav) * (1 + num_transbordos) + Paa * (num_estaciones – 1)

    Siendo num_estaciones el número de estaciones por las que se pasa, incluidas la de origen, la de destino y las de transbordos.

Esto se ajusta con una razonablemente al entendimiento “humano” de lo que significa un transbordo y de la forma en que se accede y se abandona el sistema de metro. Con este planteamiento el sistema sólo recurrirá a los transbordos cuando no haya otra solución (o cuando en número de estaciones sin transbordos sea significativamente superior al del recorrido con transbordos).

Nótese que este tratamiento se hace “por software”, y no implica ningún cambio en la codificación del fichero de mapa.
