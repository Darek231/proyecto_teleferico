import csv 
from collections import defaultdict

class Grafo:
    def __init__(self, dirigido: bool = False):
        self.dirigido = dirigido
        self.vertices = {} #es como un diccionario donde guarda {"V01": {"nombre": "Central",ect,etc}}
        self.adyacencia = defaultdict(dict) #esto ya es para ver cada esatcion osea con quien esta conectada y su costo en este caso el tiempo 

#toda esta seccion es para los vertices 

    # antes de agregra revisa que tenga id y nombre y que no exista
    def agregar_vertice(self, id_v, nombre, descripcion="", ciudad=""):
        id_v = str(id_v).strip()
        if not id_v or not nombre:
            raise ValueError("El id y el nombre del vertice son obligatorios")
        if id_v in self.vertices:
            raise ValueError(f"El vertice '{id_v}' ya existe")
        self.vertices[id_v] = {
            "nombre": nombre,
            "descripcion": descripcion,
            "ciudad": ciudad,
        }
        _ = self.adyacencia[id_v]  

    #modifica datos de una estacion existente
    def modificar_vertice(self, id_v, nombre=None, descripcion=None, ciudad=None):
        self._verificar_vertice(id_v)
        if nombre is not None:
            self.vertices[id_v]["nombre"] = nombre
        if descripcion is not None:
            self.vertices[id_v]["descripcion"] = descripcion
        if ciudad is not None:
            self.vertices[id_v]["ciudad"] = ciudad

    #borra la estación y también borra todas sus conexiones
    def eliminar_vertice(self, id_v):
        self._verificar_vertice(id_v)
        del self.vertices[id_v]
        self.adyacencia.pop(id_v, None)
        for vecinos in self.adyacencia.values():
            vecinos.pop(id_v, None)

    #función interna que verifica que el id exista
    def _verificar_vertice(self, id_v):
        if id_v not in self.vertices:
            raise ValueError(f"El vertice '{id_v}' no existe")

# toda esta seccion pertenece a las aristas
    def agregar_arista(self, origen, destino, peso, unidad="minutos", linea=""):
        self._verificar_vertice(origen)
        self._verificar_vertice(destino)
        if origen == destino:
            raise ValueError("No se permiten bucles (origen == destino)")
        try:
            peso = float(peso)
        except (TypeError, ValueError):
            raise ValueError("El peso debe ser numerico")
        if peso < 0:
            raise ValueError("El peso no puede ser negativo")
        if destino in self.adyacencia[origen]:
            raise ValueError(f"La arista {origen}-{destino} ya existe (duplicada)")

        datos = {"peso": peso, "unidad": unidad, "linea": linea}
        self.adyacencia[origen][destino] = datos
        if not self.dirigido:
            self.adyacencia[destino][origen] = dict(datos)

    def eliminar_arista(self, origen, destino):
        self._verificar_vertice(origen)
        self._verificar_vertice(destino)
        if destino not in self.adyacencia[origen]:
            raise ValueError(f"La arista {origen}-{destino} no existe")
        del self.adyacencia[origen][destino]
        if not self.dirigido:
            self.adyacencia[destino].pop(origen, None)

    def modificar_peso(self, origen, destino, nuevo_peso):
        self._verificar_vertice(origen)
        self._verificar_vertice(destino)
        if destino not in self.adyacencia[origen]:
            raise ValueError(f"La arista {origen}-{destino} no existe")
        nuevo_peso = float(nuevo_peso)
        if nuevo_peso < 0:
            raise ValueError("El peso no puede ser negativo")
        self.adyacencia[origen][destino]["peso"] = nuevo_peso
        if not self.dirigido:
            self.adyacencia[destino][origen]["peso"] = nuevo_peso

    # carga de archivos desde el archivo csv

    def cargar_desde_csv(self, ruta_vertices, ruta_aristas):
        with open(ruta_vertices, encoding="utf-8-sig", newline="") as f:
            for fila in csv.DictReader(f):
                self.agregar_vertice(
                    fila["id"].strip(),
                    fila["nombre"].strip(),
                    fila.get("descripcion", "").strip(),
                    fila.get("ciudad", "").strip(),
                )
        with open(ruta_aristas, encoding="utf-8-sig", newline="") as f:
            for fila in csv.DictReader(f):
                origen, destino = fila["origen"].strip(), fila["destino"].strip()
                # si la arista ya existe (por duplicado accidental en el CSV) se ignora
                if destino in self.adyacencia.get(origen, {}):
                    continue
                self.agregar_arista(
                    origen,
                    destino,
                    fila["peso"],
                    fila.get("unidad", "minutos").strip(),
                    fila.get("linea", "").strip(),
                )

    #(representacion) esta seccion nos sirve para traducir el grafo a distintos formatos
    #formato para leer/imprimir fácilmente
    def lista_adyacencia(self):
        return {
            u: [(v, d["peso"], d.get("linea", "")) for v, d in vecinos.items()]
            for u, vecinos in self.adyacencia.items()
        }
    #formato de tabla cuadrada
    def matriz_adyacencia(self):
        ids = sorted(self.vertices.keys())
        indice = {v: i for i, v in enumerate(ids)}
        n = len(ids)
        m = [[0.0 for _ in range(n)] for _ in range(n)]
        for u in ids:
            for v, d in self.adyacencia[u].items():
                m[indice[u]][indice[v]] = d["peso"]
        return ids, m
    #nos ayuda a saber con cuantas estaciones se conecta directamente
    def grado(self, v):
        self._verificar_vertice(v)
        return len(self.adyacencia[v])
    
    def num_vertices(self):
        return len(self.vertices)

    def num_aristas(self):
        if self.dirigido:
            return sum(len(v) for v in self.adyacencia.values())
        total = sum(len(v) for v in self.adyacencia.values())
        return total // 2
    #nos da la lista de conexiones sin datos duplicados
    def todas_las_aristas(self):
        vistas = set()
        resultado = []
        for u, vecinos in self.adyacencia.items():
            for v, d in vecinos.items():
                clave = (u, v) if self.dirigido else tuple(sorted((u, v)))
                if clave in vistas:
                    continue
                vistas.add(clave)
                resultado.append((u, v, d["peso"], d.get("linea", "")))
        return resultado
    #esto para grafos no dirigidos
    def es_conexo(self):
        if not self.vertices:
            return True
        inicio = next(iter(self.vertices))
        visitados = {inicio}
        pila = [inicio]
        while pila:
            nodo = pila.pop()
            for vecino in self.adyacencia[nodo]:
                if vecino not in visitados:
                    visitados.add(vecino)
                    pila.append(vecino)
        return len(visitados) == len(self.vertices)

    def componentes_conexas(self):
        no_vistos = set(self.vertices.keys())
        componentes = []
        while no_vistos:
            inicio = next(iter(no_vistos))
            visitados = {inicio}
            pila = [inicio]
            while pila:
                nodo = pila.pop()
                for vecino in self.adyacencia[nodo]:
                    if vecino not in visitados:
                        visitados.add(vecino)
                        pila.append(vecino)
            componentes.append(sorted(visitados))
            no_vistos -= visitados
        return componentes
    #esto es para que index pueda graficar el mapa 
    def to_dict(self):
        return {
            "dirigido": self.dirigido,
            "vertices": [
                {"id": vid, **datos} for vid, datos in self.vertices.items()
            ],
            "aristas": [
                {"origen": u, "destino": v, "peso": p, "linea": l}
                for u, v, p, l in self.todas_las_aristas()
            ],
        }