# -*- coding: utf-8 -*-

#aqui se va a validar la informacion antes de ingresar a las funciones
def validar_id_vertice(id_v):
    id_v = (id_v or "").strip()
    if not id_v:
        raise ValueError("El id del vertice no puede estar vacio")
    return id_v


def validar_nombre(nombre):
    nombre = (nombre or "").strip()
    if not nombre:
        raise ValueError("El nombre no puede estar vacio")
    return nombre


def validar_peso(valor):
    try:
        peso = float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"'{valor}' no es un peso numerico valido")
    if peso < 0:
        raise ValueError("El peso de la arista no puede ser negativo")
    return peso


def validar_vertice_existe(grafo, id_v):
    if id_v not in grafo.vertices:
        raise ValueError(f"El vertice '{id_v}' no existe en el grafo")


def validar_arista_no_duplicada(grafo, origen, destino):
    if destino in grafo.adyacencia.get(origen, {}):
        raise ValueError(f"La arista {origen}-{destino} ya existe")


def validar_no_bucle(origen, destino):
    if origen == destino:
        raise ValueError("No se permiten aristas de un vertice hacia si mismo")


def validar_grafo_para_dijkstra(grafo):
    negativas = [
        (u, v)
        for u, vecinos in grafo.adyacencia.items()
        for v, d in vecinos.items()
        if d["peso"] < 0
    ]
    if negativas:
        raise ValueError(
            "Dijkstra no es aplicable: existen pesos negativos en "
            + ", ".join(f"{u}-{v}" for u, v in negativas)
        )


def validar_grafo_para_arbol_expansion(grafo):
    if grafo.dirigido:
        raise ValueError("Kruskal/Prim requieren un grafo no dirigido")
    if not grafo.es_conexo():
        componentes = grafo.componentes_conexas()
        raise ValueError(
            "El grafo no es conexo, existen "
            f"{len(componentes)} componentes: {componentes}"
        )


def validar_fila_csv_vertice(fila):
    columnas = {"id", "nombre"}
    faltantes = columnas - set(fila.keys())
    if faltantes:
        raise ValueError(f"Faltan columnas en vertices.csv: {faltantes}")
    validar_id_vertice(fila["id"])
    validar_nombre(fila["nombre"])


def validar_fila_csv_arista(fila):
    columnas = {"origen", "destino", "peso"}
    faltantes = columnas - set(fila.keys())
    if faltantes:
        raise ValueError(f"Faltan columnas en aristas.csv: {faltantes}")
    validar_id_vertice(fila["origen"])
    validar_id_vertice(fila["destino"])
    validar_peso(fila["peso"])
