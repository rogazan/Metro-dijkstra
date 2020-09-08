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
