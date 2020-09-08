# Metro-dijkstra
Implantacion de algoritmo dijkstra para obtener el camino mínimo aplicado a infraestructuras de metro de diversas cuidades

### Objetivo:
Se pretende construir una herramienta que calcule rutas óptimas de metro entre un origen y un destino a partir de la carga un fichero mapa de la red de suburbano en formato texto.

### Introducción:
Empezaré diciendo que NO soy especialista en materia de suburbanos ni dispongo de otra información sobre ello que la que se puede encontrar buscando en internet. No me obliga ningún trabajo concreto ni que pretendo proponer un método de caracter general, tan solo me mueve mi interés particular por la automatización, la aplicación de algoritmos a los problemas del mundo real, la admiración que me producen los mapas de metro y el deseo de compartirlo con otras personas a las que este trabajo pueda ayudar en su actividad profesional, formativa, o que simplemente tambien sientan curiosidad por el desarrollo de soluciones programáticas.

A lo largo del texto haré referencia a diversas instalaciones de metro de ciudades del mundo e incluiré mis propios mapas de algunas de ellas. Algunas las conozco como “usuario amas o menos vanzado” (Madrid, Paris o Nueva York), otras sólo circunstancialmente como “turista” (Londres, Barcelona,…) y otras no las conozco más allá de la información publicada (la mayoría). Por ello ruego al lector que sea indulgente con las imprecisiones o errores que haya podido cometer en la interpretación de la información publicada y de sus casuísticas particulares.

### Planteamiento:
Plantearé el problema a partir de un fichero de texto plano que contenga la información necesaria, al que definiremos ficheros de mapa. Este fichero contendrá el listado de los nombres de estaciones en el mismo orden en que se encuentran en el mapa y agrupadas por líneas (con las particularidades que se indicarán a lo largo del presente texto). Cada línea se identificará con un indicador de comienzo de línea (“#”) acopañado del nombre de la  línea, encabezando la lista de estaciones que la forman. Un mismo nombre de estación en dos líneas diferentes se interpreta como un transbordo bidireccional entre ambas líneas. Además, como ya se ha mencionado, los ficheros de los planos de metro se construirán exclusivamente con información pública, (planos oficiales, descripciones de líneas y estaciones que se encuentran en las webs específicas de cada servicio de metropolitano y en otras fuentes públicas de uso común, tipo Wikipedia). A continuación se muestra un ejemplo esquematizado de fichero de un mapa realizado con este criterio:

![imagen1](https://github.com/rogazan/Metro-dijkstra/blob/master/images/image1.jpg)

El proceso de lectura del plano trasladará su información a la estructura de datos necesaria para generar un grafo tratable por algortimo de Dijkstra (descrito por primera vez por Edsger Dijkstra, en 1.959).

A partir del grafo, el software debe ser capaz de encontrar el camino óptimo entre cualquier par de estaciones de una red de metro.

Si bien esta es una aproximación válida, la intención es ir más allá y construir una implantación más próxima a la realidad de las redes de metro buscando la manera de 
automatizar las diversas particularidades que se encuentran en las redes de metropolitano de ciudades del mundo y aplicar criterio mas humanos a la elección del camino óptimo.

Una vez expuesto el concepto básico, comenzamos a expandirlo con las particularidades encontradas en los planos reales y el tratamiento diseñado para cada una de ellas.

#### Estaciones. Visión básica
Con este planteamiento, cada estación se traducirá en un nodo único con dos atributos: Uno será el “Nombre” y otro será una lista de nodos “vecinos” con los que tiene tramos comunes. Por ejemplo, una instancia de nodo estación podría definirse como:

    {nombre: ”Gran Vía”, vecinos: [“Tribunal”, “Sol”, “Callao”, “Chueca”]}

Este es un ejemplo real del metro de Madrid. Los dos primeros vecinos pertenecen a la línea 1 (Celeste), y los dos últimos pertenecen a la línea 5 (Verde). Nótese que en la información del nodo NO se especifica la línea a la que pertenece la estación ni sus estaciones vecinas, lo único que aquí importa es que el nodo indica que desde “Gran Vía” podemos desplazarnos en un único salto a cualquiera de las cuatro estaciones vecinas. En este punto de la aproximación el concepto de línea no sirve para nada más que para interpretar secuencialmente el fichero de mapa, entendiendo que cada estación tiene por vecinas la anterior y la posterior de todas las líneas que concurren en ella (salvo la excepción del comienzo y final de línea, que solo tendrán una único vecina). Una vez aplicado este razonamiento, podemos olvidar el concepto línea para buscar rutas, lo que puede resultar chocante pero así de simple queda la cosa en este punto.


#### Estaciones. revisión compleja y transbordos
Si establecemos cada estación como un nodo del grafo y damos un peso similar a todos los tramos que enlazan las estaciones, estaremos ignorando el coste que suponen los incómodos transbordos que todos sufrimos.

Imaginemos un trazado similar al del gráfico siguiente y que el peso del tramo (entendido como el tiempo que invierte el metro en recorrer el trayecto entre dos estaciones) es igual en todos los casos:

![imagen2](https://github.com/rogazan/Metro-dijkstra/blob/master/images/image2.jpg)

Si solo contemplamos los enlaces entre las estaciones sin más consideración, un trayecto desde “Estación 1” a “Estación 5” se podrá calcular como una ruta en la secuencia:

    1 > 2 > 3 > 4 >  5 (4 tramos de igual peso), 

Pero también podrá calcularse como otra ruta en la secuencia:

    1 > 2 > 7 > 4 > 5 (igualmente 4 tramos del mismo peso).

De esta manera se obtienen dos trayectos de peso idéntico, dado que el trayecto se está calculando exclusivamente en función del número de estaciones recorridas:

    Trayecto = f(num_estaciones)

Pero cualquier persona que haya usado el metro sabe que hay una enorme diferencia entre hacer un recorrido de 4 estaciones sin cambiar de línea que hacer el mismo viaje, con el mismo número de tramos pero con dos trasbordos en el medio, es decir, que un trayecto optimo adaptado al viajero “humano” debería replantearse como:

    trayecto = f(num_estaciones, num_transbordos).

Una primera idea puede llevar a pensar en gestionar los pesos de los enlaces, pero se descarta inmediatamente dado que el peso entre dos nodos del grafo debe ser estático “per se” y no cabe ninguna revaloración en base a lo que se haya hecho antes o lo que se hará después de recorrer el tramo.

Para dar solución al tema de los transbordos se redefine el concepto de “Estación” a otro más complejo, de modo que ya no se tratará de un nodo único sino que pasará a ser un conjunto de nodos con enlaces internos entre ellos. Así, una estación tendrá un nodo que podemos denominar “vestíbulo”, cuyo nombre será el de la propia estación, y N nodos que podemos denominar “andenes” (tantos como líneas pasen por la estación), El nombre de un andén estará formado por la concatenación del nombre de la estación y de la línea a la que da servicio. En cuanto a los enlaces internos, el nodo vestíbulo contará con enlaces bidireccionales con todos los andenes, pero no existirá ningún enlace entre los distintos andenes de la misma estación. Se sintetiza en el gráfico siguiente en el que se ve una estación en la que convergen dos líneas:

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

Esto se ajusta razonablemente al entendimiento de usuario de lo que significa un transbordo y de la forma en que se accede y se abandona el sistema de metro. Con este planteamiento, y dado su peso elevado, el sistema sólo recurrirá a los transbordos cuando no haya otra solución (o cuando en número de estaciones recorridas con menos transbordos sea significativamente superior al del recorrido con mas transbordos).

Nótese que este tratamiento se hace “por software”, y no implica ningún cambio en la codificación del fichero de mapa.

NOTA SOBRE RENDIMIENTO:
El número de nodos y de enlaces por estación se incrementa notablemente frente a la visión simplista de un nodo único por estación::

    Inc(Num_nodos_Estación) = Num_lineas

y el número de enlaces añadidos a cada estación se verá incrementado en:

    Inc(Num_enlaces_Estación) = 2 * Num_lineas
    
Este incremento en el número de nodos y enlaces tiene su lado negativo en el orden de complejidad del algoritmo de referencia, que se establece en: 
    
    O(V ^ 2), o bien O(E Log V) si se utiliza una lista priorizada (V = Num. Vertices, E = Num. Aristas)


#### Pasarelas entre estaciones:
los transbordos siempre se realizan entre andenes de una misma estación, pero aún podemos ver que existe otra clase de transbordos que se hacen entre estaciones de nombres diferentes, (lo podemos ver en el metro de Madrid entre las estaciones de Embajadores y Acacias, en el de Barcelona entre Provença y Diagonal y muchísimos más. Los más complejos, como Nueva York o Moscú tienen montones de ellos). Aquí definiremos un concepto que denominaremos “pasarela” y que trataremos exactamente igual que una línea de metro que solo tenga dos estaciones en su recorrido. La única diferencia en su tratamiento radica en la posibilidad de asignar un peso particular para estos recorridos, para lo que añadiremos un identificador de pasarela "@" al nombre la linea.

![imagen4](https://github.com/rogazan/Metro-dijkstra/blob/master/images/image4.jpg)

Nótese que el uso de una pasarela es relativamente costoso. En el gráfico anterior vemos que una parte de un recorrido que incluya transbordo por la pasarela desde la línea azul a la línea roja implicará, siendo Pp el peso propio del tramo pasarela:

    Azul-a-Roja = Pav + Pav + Pp + Pav + Pav
    Azul-a-Roja = 4 * Pav + Pp

#### Líneas circulares:
Existen líneas que son circulares, esto es, que establecida una estación cualquiera como principio de línea y otra de fin de línea, aún existe un tramo bidireccional que une ambas. En el metro de Madrid podemos ver ejemplos en la linea 6 (gris) y en la Metrosur (verde oliva). La propia explicación sugiere la solución: En la descripción de la línea en el fichero de mapa pondremos una referencia adicional tras la última estación con el nombre de la primera, con lo que quedará definido correctamente: 

![imagen5](https://github.com/rogazan/Metro-dijkstra/blob/master/images/image5.jpg)

#### Línea parcialmente circular:
Es un caso poco frecuente donde solamente es circular una parte de un extremo de la línea. Ejemplo de ello se puede encontrar en la línea 7bis del metro de París:

![imagen6](https://github.com/rogazan/Metro-dijkstra/blob/master/images/image6.jpg)

La solución es similar a la de la línea circular, pero cerrando sobre la estación en la que converge el segmento circular en lugar de hacerlo sobre la primera, lo que traducido al fichero de mapa, dejaría la cosa como se muestra a continuación:

![imagen7](https://github.com/rogazan/Metro-dijkstra/blob/master/images/image7.jpg)

#### Tramos:
En condiciones normales una línea se describe como una relación de estaciones en secuencia desde la primera a la última, pero hay situaciones, como veremos más adelante, en las que conviene fraccionar la línea en tramos para gestionar algunas particularidades. La descripción de un tramo se hace dentro del contexto de la línea con un indicador de comienzo de tramo (">") en el que recibe un nombre único dentro de la línea y se extenderá hasta el siguiente inicio de tramo o hasta el final de la línea. Si no se especifica un tramo tras la identificación de la línea se entenderá que implícitamente existe un tramo primero que se extiende desde la identificación de la línea hasta la identificación de un tramo o hasta el final de la línea, lo que supone la existencia de un primer (y tal vez único) tramo que coincide con la propia línea. Por último, la conexión de un tramo con el resto de la línea se resuelve teniendo al menos una estación en común con el resto de la línea. El siguiente ejemplo muestra esta particularidad:

![imagen8](https://github.com/rogazan/Metro-dijkstra/blob/master/images/image8.jpg)

#### Tramos unidireccionales:
Hasta ahora hemos supuesto que los enlaces entre dos estaciones contiguas de un misma línea son siempre bidireccionales, pero se dan casos en lo que esta suposición NO es cierta. Si observamos el recorte del plano de metro de París mostrado en la particularidad de líneas parcialmente circulares, podemos observar que en ese anillo se circula en una única dirección. Para resolver esto mantendremos la bidireccionalidad como acción por defecto entre todas las estaciones y anotaremos la excepción de unidireccionalidad sólo para aquellas estaciones afectadas por ello, agregando al nombre de la estación el modificador “| U”, lo que indicará que la circulación entre la estación PREVIA y la que contiene el modificador se produce en una única dirección (de la PREVIA a la que contiene el modificador). El ejemplo en la línea 7bis de París quedará como se muestra a continuación:

![imagen9](https://github.com/rogazan/Metro-dijkstra/blob/master/images/image9.jpg)

En el ejemplo previo puede verse que todo el recorrido circular que comienza y finaliza en Botzaris es de sentido unidireccional.

El caso previo se da al final de una línea, pero podemos encontrar otros casos en que la unidireccionalidad se da en el medio de la línea (La ida viaja parcialmente por un camino y la vuelta por otro). Nuevamente podemos recurrir al metro de París para ver un ejemplo en la línea 10:

![imagen10](https://github.com/rogazan/Metro-dijkstra/blob/master/images/image10.jpg)

En este caso recurriremos al modificador de unidireccionalidad (“| U”) y a la definición de tramos, que podemos aplicar de distintas maneras, aunque el resultado de todas ellas repercutirá de la misma manera en el grafo. Por ejemplo podemos definir la línea de principio a fin incluyendo el recorrido de ida de la bifurcación y especificando los enlaces unidireccionales de la sección bifurcada y agregaremos un tramo que refleje sólo el recorrido bifurcado de vuelta:
    
    # Linea 10
    …
    Javel André Citroën
    Église d’Auteuil | U
    Michel Ange Auteuil | U
    Porte d’Auteuil | U
    Boulogne Jean Jaurès | U
    …

    > Tramo retorno L10
    Boulogne Jean Jaurès
    Michel Ange Molitor | U
    Chardon Lagache | U
    Mirabeau | U
    Javel André Citroën | U
    
Los tramos ayudan a definirlo de varias maneras. Por ejemplo, otra alternativa sería definir un tramo desde el inicio de línea hasta el comienzo de la sección bifurcada, otro tramo desde el fin de la sección bifurcada hasta el fin de la línea y otros dos tramos para la sección bifurcada: uno con el recorrido de ida en esa sección indicando la unidireccionalidad de los enlaces entre estaciones y otro con el recorrido de vuelta de la misma sección, indicando igualmente la unidireccionalidad de estos enlaces.

