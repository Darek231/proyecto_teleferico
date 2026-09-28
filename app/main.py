# -*- coding: utf-8 -*-
import os
import sys

from flask import Flask, jsonify, render_template, request

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import algoritmo
import validaciones
from grafo import Grafo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_VERTICES = os.path.join(BASE_DIR, "datos", "vertices.csv")
RUTA_ARISTAS = os.path.join(BASE_DIR, "datos", "aristas.csv")

app = Flask(__name__)

grafo = Grafo(dirigido=False)


def cargar_grafo_inicial():
    global grafo
    grafo = Grafo(dirigido=False)
    grafo.cargar_desde_csv(RUTA_VERTICES, RUTA_ARISTAS)

cargar_grafo_inicial()

def error_json(mensaje, codigo=400):
    return jsonify({"ok": False, "error": mensaje}), codigo

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/grafo")
def api_grafo():
    return jsonify({"ok": True, "grafo": grafo.to_dict()})


@app.route("/api/matriz")
def api_matriz():
    ids, m = grafo.matriz_adyacencia()
    return jsonify({"ok": True, "ids": ids, "matriz": m})


@app.route("/api/lista_adyacencia")
def api_lista_adyacencia():
    return jsonify({"ok": True, "lista": grafo.lista_adyacencia()})


@app.route("/api/reiniciar", methods=["POST"])
def api_reiniciar():
    cargar_grafo_inicial()
    return jsonify({"ok": True, "grafo": grafo.to_dict()})

#CRUD 
@app.route("/api/vertices", methods=["POST"])
def api_agregar_vertice():
    datos = request.get_json(force=True)
    try:
        id_v = validaciones.validar_id_vertice(datos.get("id"))
        nombre = validaciones.validar_nombre(datos.get("nombre"))
        grafo.agregar_vertice(
            id_v, nombre, datos.get("descripcion", ""), datos.get("ciudad", "")
        )
    except ValueError as e:
        return error_json(str(e))
    return jsonify({"ok": True, "grafo": grafo.to_dict()})

@app.route("/api/vertices/<id_v>", methods=["PUT"])
def api_modificar_vertice(id_v):
    datos = request.get_json(force=True)
    try:
        grafo.modificar_vertice(
            id_v,
            nombre=datos.get("nombre"),
            descripcion=datos.get("descripcion"),
            ciudad=datos.get("ciudad"),
        )
    except ValueError as e:
        return error_json(str(e))
    return jsonify({"ok": True, "grafo": grafo.to_dict()})

@app.route("/api/vertices/<id_v>", methods=["DELETE"])
def api_eliminar_vertice(id_v):
    try:
        grafo.eliminar_vertice(id_v)
    except ValueError as e:
        return error_json(str(e))
    return jsonify({"ok": True, "grafo": grafo.to_dict()})

@app.route("/api/aristas", methods=["POST"])
def api_agregar_arista():
    datos = request.get_json(force=True)
    try:
        origen = validaciones.validar_id_vertice(datos.get("origen"))
        destino = validaciones.validar_id_vertice(datos.get("destino"))
        validaciones.validar_no_bucle(origen, destino)
        validaciones.validar_vertice_existe(grafo, origen)
        validaciones.validar_vertice_existe(grafo, destino)
        validaciones.validar_arista_no_duplicada(grafo, origen, destino)
        peso = validaciones.validar_peso(datos.get("peso"))
        grafo.agregar_arista(
            origen, destino, peso, datos.get("unidad", "minutos"), datos.get("linea", "")
        )
    except ValueError as e:
        return error_json(str(e))
    return jsonify({"ok": True, "grafo": grafo.to_dict()})


@app.route("/api/aristas", methods=["DELETE"])
def api_eliminar_arista():
    datos = request.get_json(force=True)
    try:
        grafo.eliminar_arista(datos.get("origen"), datos.get("destino"))
    except ValueError as e:
        return error_json(str(e))
    return jsonify({"ok": True, "grafo": grafo.to_dict()})


@app.route("/api/aristas/peso", methods=["PUT"])
def api_modificar_peso():
    datos = request.get_json(force=True)
    try:
        peso = validaciones.validar_peso(datos.get("peso"))
        grafo.modificar_peso(datos.get("origen"), datos.get("destino"), peso)
    except ValueError as e:
        return error_json(str(e))
    return jsonify({"ok": True, "grafo": grafo.to_dict()})

@app.route("/api/dfs")
def api_dfs():
    inicio = request.args.get("inicio")
    try:
        validaciones.validar_vertice_existe(grafo, inicio)
        resultado = algoritmo.dfs(grafo, inicio)
    except ValueError as e:
        return error_json(str(e))
    return jsonify({"ok": True, "resultado": resultado})

@app.route("/api/bfs")
def api_bfs():
    inicio = request.args.get("inicio")
    try:
        validaciones.validar_vertice_existe(grafo, inicio)
        resultado = algoritmo.bfs(grafo, inicio)
    except ValueError as e:
        return error_json(str(e))
    return jsonify({"ok": True, "resultado": resultado})

@app.route("/api/dijkstra")
def api_dijkstra():
    origen = request.args.get("origen")
    destino = request.args.get("destino")
    try:
        validaciones.validar_vertice_existe(grafo, origen)
        validaciones.validar_vertice_existe(grafo, destino)
        validaciones.validar_grafo_para_dijkstra(grafo)
        resultado = algoritmo.dijkstra(grafo, origen, destino)
    except (ValueError, algoritmo.PesoNegativoError) as e:
        return error_json(str(e))
    return jsonify({"ok": True, "resultado": resultado})

@app.route("/api/kruskal")
def api_kruskal():
    try:
        validaciones.validar_grafo_para_arbol_expansion(grafo)
        resultado = algoritmo.kruskal(grafo)
    except ValueError as e:
        return error_json(str(e))
    return jsonify({"ok": True, "resultado": resultado})

@app.route("/api/prim")
def api_prim():
    inicio = request.args.get("inicio")
    try:
        validaciones.validar_vertice_existe(grafo, inicio)
        validaciones.validar_grafo_para_arbol_expansion(grafo)
        resultado = algoritmo.prim(grafo, inicio)
    except ValueError as e:
        return error_json(str(e))
    return jsonify({"ok": True, "resultado": resultado})

@app.route("/api/reporte")
def api_reporte():
    origen = request.args.get("origen")
    destino = request.args.get("destino")
    resultados = {}
    recomendaciones = []
    try:
        if origen and destino:
            validaciones.validar_vertice_existe(grafo, origen)
            validaciones.validar_vertice_existe(grafo, destino)
            validaciones.validar_grafo_para_dijkstra(grafo)
            resultados["dijkstra"] = algoritmo.dijkstra(grafo, origen, destino)
            if resultados["dijkstra"]["camino"]:
                recomendaciones.append(
                    "Usar la ruta calculada minimiza el tiempo de viaje entre "
                    "las estaciones seleccionadas."
                )
        if grafo.es_conexo():
            resultados["kruskal"] = algoritmo.kruskal(grafo)
            resultados["prim"] = algoritmo.prim(grafo, next(iter(grafo.vertices)))
            recomendaciones.append(
                "El arbol de expansion minima muestra el conjunto de tramos que, "
                "de mantenerse operativos, conectan toda la red con el menor "
                "tiempo acumulado (util para priorizar mantenimiento)."
            )
    except ValueError as e:
        return error_json(str(e))

    texto = reportes.generar_reporte_completo(grafo, resultados, recomendaciones)
    return jsonify({"ok": True, "reporte": texto})


if __name__ == "__main__":
    app.run(debug=True, port=5011)
