import heapq as hq


class ErrorNoRuta(Exception):
    pass


class Grafo():

    def __init__(self):
        self._datos = {}

    def __getitem__(self, nodo):
        return self._datos[nodo]

    def __iter__(self):
        return iter(self._datos)

    def creaEnlace(self, nodo, vecino, enlace=None):
        if nodo in self._datos:
            vecinos = self._datos[nodo]
            vecinos[vecino] = enlace
        else:
            self._datos[nodo] = {vecino: enlace}
        return enlace

    def cuentaNodos(self):
        return len(self._datos)

    def cuentaEnlaces(self):
        return sum(len(vecino) for vecino in self._datos.values())

    def buscaCamino(self, origen, destino):
        costes = {origen: 0}
        predecesores = {origen: (None)}
        colaVisitas = [(0, origen)]
        visitados = set()
        while colaVisitas:
            costeOD, nodo = hq.heappop(colaVisitas)
            if nodo == destino:
                break
            if not nodo in visitados:
                visitados.add(nodo)
                vecinos = self[nodo] if nodo in self else None
                for vecino in vecinos:
                    if not vecino in visitados:
                        costeAct = costeOD + vecinos[vecino]
                        if vecino not in costes or costes[vecino] > costeAct:
                            costes[vecino] = costeAct
                            predecesores[vecino] = (nodo)
                            hq.heappush(colaVisitas, (costeAct, vecino))
        if destino is not None and destino not in costes:
            raise ErrorNoRuta("No existe camino de %s a %s" % (origen, destino))
        nodos = [destino]
        nodo = predecesores[destino]
        while nodo is not None:
            nodos.append(nodo)
            nodo = predecesores[nodo]
        nodos.reverse()
        return nodos
