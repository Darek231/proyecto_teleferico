# -*- coding: utf-8 -*-

import heapq
from collections import deque


# ----------------------------------------------------------------------
# DFS - Busqueda en profundidad
# ----------------------------------------------------------------------
def dfs(grafo, inicio):
    grafo._verificar_vertice(inicio)
    visitados = []
    visitado_set = set()
    aristas_usadas = []
    padre = {inicio: None}

    def _dfs_rec(nodo):
        visitado_set.add(nodo)
        visitados.append(nodo)
        for vecino in sorted(grafo.adyacencia[nodo].keys()):
            if vecino not in visitado_set:
                aristas_usadas.append((nodo, vecino))
                padre[vecino] = nodo
                _dfs_rec(vecino)

    _dfs_rec(inicio)

    return {
        "orden": visitados,
        "aristas": aristas_usadas,
        "alcanzables": visitados,
        "no_alcanzables": [v for v in grafo.vertices if v not in visitado_set],
    }


# ----------------------------------------------------------------------
# BFS - Busqueda en amplitud
# ----------------------------------------------------------------------
def bfs(grafo, inicio):
    grafo._verificar_vertice(inicio)
    visitado_set = {inicio}
    orden = [inicio]
    cola = deque([inicio])
    padre = {inicio: None}
    nivel = {inicio: 0}
    estados_cola = []  # foto de la cola en cada paso, para mostrar en el reporte

    while cola:
        estados_cola.append(list(cola))
        nodo = cola.popleft()
        for vecino in sorted(grafo.adyacencia[nodo].keys()):
            if vecino not in visitado_set:
                visitado_set.add(vecino)
                padre[vecino] = nodo
                nivel[vecino] = nivel[nodo] + 1
                orden.append(vecino)
                cola.append(vecino)

    return {
        "orden": orden,
        "padre": padre,
        "nivel": nivel,
        "estados_cola": estados_cola,
        "no_alcanzables": [v for v in grafo.vertices if v not in visitado_set],
    }


def reconstruir_camino(padre, origen, destino):
    if destino not in padre:
        return None
    if padre.get(destino) is None and destino != origen:
        return None
    camino = [destino]
    actual = destino
    while actual != origen:
        actual = padre[actual]
        if actual is None:
            return None
        camino.append(actual)
    camino.reverse()
    return camino


def camino_minimo_aristas(grafo, origen, destino):
    """Numero minimo de aristas entre origen y destino, usando BFS
    (valido porque, en este grafo, cada arista representa un tramo,
    todas con 'costo topologico' igual a 1 salto)."""
    resultado = bfs(grafo, origen)
    if destino not in resultado["nivel"]:
        return None, None
    camino = reconstruir_camino(resultado["padre"], origen, destino)
    return resultado["nivel"][destino], camino


# ----------------------------------------------------------------------
# Dijkstra - camino de costo minimo
# ----------------------------------------------------------------------
class PesoNegativoError(ValueError):
    pass


def dijkstra(grafo, origen, destino=None):
    grafo._verificar_vertice(origen)
    if destino is not None:
        grafo._verificar_vertice(destino)

    for u, vecinos in grafo.adyacencia.items():
        for v, d in vecinos.items():
            if d["peso"] < 0:
                raise PesoNegativoError(
                    f"Dijkstra no es aplicable: la arista {u}-{v} tiene peso negativo"
                )

    dist = {v: float("inf") for v in grafo.vertices}
    padre = {v: None for v in grafo.vertices}
    visitado = set()
    dist[origen] = 0.0
    heap = [(0.0, origen)]

    while heap:
        d_actual, u = heapq.heappop(heap)
        if u in visitado:
            continue
        visitado.add(u)
        for v, datos in grafo.adyacencia[u].items():
            nueva_dist = d_actual + datos["peso"]
            if nueva_dist < dist[v]:
                dist[v] = nueva_dist
                padre[v] = u
                heapq.heappush(heap, (nueva_dist, v))

    resultado = {"distancias": dist, "predecesores": padre, "origen": origen}
    if destino is not None:
        resultado["destino"] = destino
        resultado["costo"] = dist[destino]
        resultado["camino"] = (
            reconstruir_camino(padre, origen, destino)
            if dist[destino] != float("inf")
            else None
        )
    return resultado


# ----------------------------------------------------------------------
# Kruskal - arbol de expansion minima (union-find)
# ----------------------------------------------------------------------
class UnionFind:
    def __init__(self, elementos):
        self.padre = {e: e for e in elementos}
        self.rango = {e: 0 for e in elementos}

    def encontrar(self, x):
        while self.padre[x] != x:
            self.padre[x] = self.padre[self.padre[x]]
            x = self.padre[x]
        return x

    def unir(self, x, y):
        rx, ry = self.encontrar(x), self.encontrar(y)
        if rx == ry:
            return False
        if self.rango[rx] < self.rango[ry]:
            rx, ry = ry, rx
        self.padre[ry] = rx
        if self.rango[rx] == self.rango[ry]:
            self.rango[rx] += 1
        return True


def kruskal(grafo):
    if grafo.dirigido:
        raise ValueError("Kruskal requiere un grafo no dirigido")
    if not grafo.es_conexo():
        raise ValueError("Kruskal requiere un grafo conexo")

    aristas = sorted(grafo.todas_las_aristas(), key=lambda e: e[2])
    uf = UnionFind(grafo.vertices.keys())
    aceptadas, rechazadas = [], []
    costo_total = 0.0

    for u, v, peso, linea in aristas:
        if uf.unir(u, v):
            aceptadas.append({"origen": u, "destino": v, "peso": peso, "linea": linea})
            costo_total += peso
        else:
            rechazadas.append(
                {"origen": u, "destino": v, "peso": peso, "linea": linea,
                 "motivo": "genera ciclo"}
            )

    return {
        "aristas_ordenadas": [
            {"origen": u, "destino": v, "peso": p, "linea": l} for u, v, p, l in aristas
        ],
        "aceptadas": aceptadas,
        "rechazadas": rechazadas,
        "costo_total": costo_total,
    }


# ----------------------------------------------------------------------
# Prim - arbol de expansion minima (heap de aristas candidatas)
# ----------------------------------------------------------------------
def prim(grafo, inicio):
    if grafo.dirigido:
        raise ValueError("Prim requiere un grafo no dirigido")
    grafo._verificar_vertice(inicio)
    if not grafo.es_conexo():
        raise ValueError("Prim requiere un grafo conexo")

    visitados = {inicio}
    aristas_arbol = []
    iteraciones = []
    costo_total = 0.0
    heap = []
    for v, d in grafo.adyacencia[inicio].items():
        heapq.heappush(heap, (d["peso"], inicio, v, d.get("linea", "")))

    while heap and len(visitados) < len(grafo.vertices):
        peso, u, v, linea = heapq.heappop(heap)
        if v in visitados:
            continue
        visitados.add(v)
        aristas_arbol.append({"origen": u, "destino": v, "peso": peso, "linea": linea})
        iteraciones.append(
            {"arista": (u, v), "peso": peso, "nodos_incluidos": sorted(visitados)}
        )
        costo_total += peso
        for w, d in grafo.adyacencia[v].items():
            if w not in visitados:
                heapq.heappush(heap, (d["peso"], v, w, d.get("linea", "")))

    return {
        "nodo_inicial": inicio,
        "aristas": aristas_arbol,
        "iteraciones": iteraciones,
        "costo_total": costo_total,
        "nodos_incluidos": sorted(visitados),
    }
