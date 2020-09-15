from miDijkstra  import Grafo
from random      import sample
from unicodedata import normalize

# Pesos de los distintos tipos de enlaces
PESO_ESTACION       = 2
PESO_TRASBORDO      = 3
PESO_PASARELA       = 4

# Caracteres de control del fichero de mapa
CARACTER_PASARELA   = "@"
CARACTER_LINEA      = "#"
CARACTER_TRAMO      = ">"
CARACTER_COMENTARIO = "!"


class errorMapa(Exception):
    pass


class _Nodo():

    def __init__(self, nombre):
        self.nombre  = nombre
        self.vecinos = []

    def agregaVecino(self, vecino, linea):
        self.vecinos.append([vecino, linea])


class miGrafo():

    def __init__ (self, fichero):
        self.fichero = fichero
        self.miGrafo, self.lineas = _cargaMapa(fichero)


    def infoGrafo(self):
        retorno = {}
        retorno["Mapa"]           = self.fichero
        retorno["Num Lineas"]     = len(self.listaLineas("L"))
        retorno["Num Pasarelas"]  = len(self.listaLineas("P"))
        retorno["Num Estaciones"] = len(self.listaEstaciones())
        retorno["Num Tramos"]     = len([linea["tramos"] for linea in self.lineas])
        retorno["Num. Nodos"]     = self.numNodos()
        retorno["Num. Enlaces"]   = self.numEnlaces()
        return retorno

    def estacionesComunes(self, lineas):
        retorno = []
        if len(lineas) > 1:
            retorno = set(self.infoLinea(lineas[0], True)["estaciones"])
            for linea in range(1, len(lineas)):
                retorno.intersection_update(self.infoLinea(lineas[linea], True)["estaciones"])
        return list(retorno)


    def buscaRuta (self, origen, destino):
        retorno = miRuta(self.miGrafo.buscaCamino(origen, destino))
        return retorno


    def buscaAleatorio (self):
        return sample(self.listaEstaciones(), 1)[0]


    def infoLinea (self, linea, listaEstaciones=False, ordenado=True):
        i = 0
        retorno = {}
        while i < len(self.lineas):
            if self.lineas[i]["linea"] == linea:
                totEstaciones = set()
                retorno = {"linea": linea, "totEstaciones" : 0, "tramos" : []}
                for tramo in self.lineas[i]["tramos"]:
                    estaciones = (set(tramo["estaciones"]))
                    totEstaciones.update(estaciones)
                    retorno["tramos"].append({"tramo": tramo["tramo"], "numEstaciones" : len(estaciones)})
                retorno["totEstaciones"] += len(totEstaciones)
                if listaEstaciones:
                    if ordenado:
                        retorno["estaciones"] = sorted(list(totEstaciones), key=lambda x: normalize("NFD", x))
                    else:
                        retorno["estaciones"] = (list(totEstaciones))
                break
            i += 1
        return retorno


    def infoTramo (self, linea, miTramo, listaEstaciones=False, ordenado=True):
        i = 0
        retorno = {}
        while i < len(self.lineas):
            if self.lineas[i]["linea"] == linea:
                for tramo in self.lineas[i]["tramos"]:
                    if tramo["tramo"] == miTramo:
                        estaciones = list(set(tramo["estaciones"]))
                        retorno = {"linea"         : linea,
                                   "tramo"         : miTramo,
                                   "numEstaciones" : len(estaciones)}
                        if listaEstaciones:
                            if ordenado:
                                retorno["estaciones"]  = sorted(estaciones, key=lambda x: normalize("NFD", x))
                            else:
                                retorno["estaciones"]  = estaciones
            i += 1
        return retorno


    def infoEstacion(self, estacion):
        i = 0
        lineas = []
        retorno = {}
        while i < len(self.lineas):
            j = 0
            while j < len(self.lineas[i]["tramos"]):
                if estacion in self.lineas[i]["tramos"][j]["estaciones"]:
                    lineas.append(self.lineas[i]["linea"])
                j += 1
            i += 1
        if len(lineas):
            retorno["estacion"] = estacion
            retorno["lineas"]   = lineas
        return retorno


    def listaLineas(self, tipo="T"):
        enumerador = None
        retorno = []
        if   tipo == "T":
            enumerador = (linea for linea in self.lineas)
        elif tipo == "L":
            enumerador = (linea for linea in self.lineas if linea["linea"][0] != "@")
        elif tipo == "P":
            enumerador = (linea for linea in self.lineas if linea["linea"][0] == "@")
        if enumerador:
            retorno = [{"linea": linea["linea"], "numTramos": len(linea["tramos"])} for linea in enumerador]
        return retorno


    def listaTramos(self, linea):
        retorno = []
        lin = 0
        encontrado = False
        while lin < len(self.lineas) and not encontrado:
            if self.lineas[lin]["linea"] == linea:
                encontrado = True
                for tramo in self.lineas[lin]["tramos"]:
                    retorno.append(tramo["tramo"])
            lin += 1
        return retorno


    def listaEstaciones(self, ordenado=False):
        lista = set()
        for linea in self.lineas:
            for tramo in linea['tramos']:
                lista.update(tramo['estaciones'])
        lista = list(lista)
        if ordenado:
            lista = sorted(lista, key=lambda x: normalize("NFD", x))
        return lista


    def numEnlaces(self):
        retorno = self.miGrafo.cuentaEnlaces()
        return retorno


    def numNodos(self):
        retorno = self.miGrafo.cuentaNodos()
        return retorno


class miRuta():

    def __init__(self, ruta):
        self.origen = ruta[0]
        self.destino = ruta[len(ruta) - 1]
        self.ruta = ruta
        self.lineas = []
        self.estaciones = []
        transbordo = False
        for nodo in range(1, len(ruta) - 1):
            dato = ruta[nodo]
            if nodo == 1:
                self.lineas.append(dato[dato.find(" L-") + 3:])
            if transbordo:
                transbordo = False
                self.lineas.append(dato[dato.find(" L-") + 3:])
            if dato.find(" L-") > -1:
                self.estaciones.append(dato[:dato.find(" L-")])
            else:
                transbordo = True
        self.estaciones = list(set(self.estaciones))
        self.tiempo  = 2 * PESO_TRASBORDO
        self.tiempo += (len(self.estaciones) - 1) * PESO_ESTACION
        if len(self.lineas) > 1:
            for linea in range(1, len(self.lineas)):
                if self.lineas[linea][0] == CARACTER_PASARELA:
                    self.tiempo += 2 * PESO_TRASBORDO + PESO_PASARELA - PESO_ESTACION
                else:
                    self.tiempo += 2 * PESO_TRASBORDO


    def infoRuta(self, ruta=False):
        retorno = dict()
        retorno["origen"]         = self.origen
        retorno["destino"]        = self.destino
        retorno["numTransbordos"] = len(self.lineas) - 1
        retorno["numLineas"]      = len(self.lineas)
        retorno["numEstaciones"]  = len(self.estaciones)
        retorno["Duracion"]       = self.tiempo
        if ruta:
            retorno ["ruta"]      = self.ruta
        return retorno


    def format(self, largo=True, indent=4):
        retorno = ""
        if not largo:
            indent = 0
        transbordo = False
        for nodo in range(1, len(self.ruta) - 1):
            dato = self.ruta[nodo]
            if nodo == 1:
                if largo:
                    retorno += " " * indent + "INICIO en linea %s" % dato[dato.find(" L-") + 3:] + "\n"
            if transbordo:
                if largo:
                    retorno += " " * indent + "TRANSBORDO a linea %s" % dato[dato.find(" L-") + 3:] + "\n"
                transbordo = False
            if dato.find(" L-") > -1:
                retorno += " " * (2 * indent) + dato[:dato.find(" L-")]
                if not largo:
                    retorno += " (" + dato[dato.find(" L-") + 3:] + ")"
                retorno += "\n"
            else:
                transbordo = True
        return retorno


def _cargaMapa(fichero):
    # Carga array con la información extraida del mapa
    linea = ""
    tramo = ""
    lista = []
    lineas = []
    tramos = []
    mapa = open(fichero, "r", encoding="utf-8")
    previo = None
    actual = None
    comienzaLinea  = True
    numEstaciones  = 0
    numEstacionesT = 0
    estTramo = []
    i = 0
    for reg in mapa:
        reg = reg.strip()
        if reg == "":
            continue
        if reg[0] == CARACTER_COMENTARIO:
            continue
        if reg[0] == CARACTER_LINEA:
            if numEstaciones:
                _resumenTramo (tramos, tramo, estTramo)
                _resumenLinea (lineas, linea, tramos)
                estTramo = []
                tramos = []
                numEstaciones = 0
                comienzaLinea = True
            previo = None
            actual = None
            numEstacionesT = 0
            linea = reg.split(" ", 1)[1].strip()
            tramo = linea
            continue
        if reg[0] == CARACTER_TRAMO:
            if numEstacionesT:
                _resumenTramo (tramos, tramo, estTramo)
            previo = None
            actual = None
            tramo = reg.split(" ", 1)[1].strip()
            estTramo = []
            numEstacionesT = 0
            continue
        desc = reg.split("|")
        bidir = True
        if len(desc) > 1:
            if desc[1].strip().upper() == "U":
                bidir = False
                reg = desc[0]
        numEstaciones += 1
        numEstacionesT += 1
        previo = actual
        actual = _Nodo(reg.strip())
        if comienzaLinea:
            comienzaLinea = False
        if actual.nombre not in estTramo:
            estTramo.append(actual.nombre)
        yaExiste = False
        for j in range(i):
            if actual.nombre == lista[j].nombre:
                actual = lista[j]
                yaExiste = True
                break
        if previo != None:
            if bidir:
                actual.agregaVecino(previo.nombre, linea)
            previo.agregaVecino(actual.nombre, linea)
        if not yaExiste:
            lista.append(actual)
            i += 1
    if numEstaciones:
        _resumenTramo (tramos, tramo, estTramo)
        _resumenLinea (lineas, linea, tramos)
    mapa.close()
    if len(lista) == 0:
        raise errorMapa("error en la carga del mapa. No hay registros")
    miGrafo = Grafo()
    # Carga todos los tramos entre nodos en el objeto Grafo
    for estacion in lista:
        for enlace in range(len(estacion.vecinos)):
            nomEst = estacion.nombre
            peso = PESO_PASARELA if estacion.vecinos[enlace][1][0] == CARACTER_PASARELA else PESO_ESTACION
            origen = nomEst + " L-" + estacion.vecinos[enlace][1]
            destino = estacion.vecinos[enlace][0] + " L-" + estacion.vecinos[enlace][1]
            miGrafo.creaEnlace(nomEst, origen, PESO_TRASBORDO)
            miGrafo.creaEnlace(origen, nomEst, PESO_TRASBORDO)
            miGrafo.creaEnlace(origen, destino, peso)
    return miGrafo, lineas


def _resumenLinea (lineas, linea, tramos):
        lineas.append({"linea"        : linea,
                       "numTramos"    : len(tramos),
                       "tramos"       : tramos})


def _resumenTramo (tramos, tramo, estTramo):
        tramos.append({"tramo"        : tramo,
                       "numEstaciones": len(set(estTramo)),
                       "estaciones"   : list(set(estTramo))})
