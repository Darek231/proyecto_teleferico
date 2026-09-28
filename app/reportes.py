# -*- coding: utf-8 -*-
from datetime import datetime


def _linea(txt="", ancho=70, relleno="-"):
    if not txt:
        return relleno * ancho
    return f" {txt} ".center(ancho, relleno)


def reporte_ruta_dijkstra(grafo, resultado):
    origen = resultado["origen"]
    destino = resultado["destino"]
    camino = resultado.get("camino")
    costo = resultado.get("costo")

    partes = [_linea("RUTA MAS RAPIDA (DIJKSTRA)")]
    o_nombre = grafo.vertices[origen]["nombre"]
    d_nombre = grafo.vertices[destino]["nombre"]
    partes.append(f"Origen : {origen} - {o_nombre}")
    partes.append(f"Destino: {destino} - {d_nombre}")

    if not camino:
        partes.append("No existe un camino disponible entre estas estaciones.")
        return "\n".join(partes)

    partes.append(f"Tiempo total estimado: {costo:.1f} minutos")
    partes.append("Recorrido:")
    for i, nodo in enumerate(camino, start=1):
        nombre = grafo.vertices[nodo]["nombre"]
        partes.append(f"  {i}. {nodo} - {nombre}")
    return "\n".join(partes)


def reporte_comparacion_mst(kruskal_res, prim_res):
    partes = [_linea("COMPARACION KRUSKAL VS PRIM")]
    partes.append(f"Costo total Kruskal : {kruskal_res['costo_total']:.1f} minutos")
    partes.append(f"Costo total Prim    : {prim_res['costo_total']:.1f} minutos")
    partes.append(f"N. aristas Kruskal  : {len(kruskal_res['aceptadas'])}")
    partes.append(f"N. aristas Prim     : {len(prim_res['aristas'])}")
    if abs(kruskal_res["costo_total"] - prim_res["costo_total"]) < 1e-6:
        partes.append("Ambos algoritmos coinciden en el costo total (correcto).")
    else:
        partes.append(
            "ADVERTENCIA: los costos difieren, revisar la implementacion "
            "(en un grafo conexo ambos deben coincidir)."
        )
    return "\n".join(partes)


def generar_reporte_completo(grafo, resultados: dict, recomendaciones=None):
    """resultados: dict opcional con claves 'dfs', 'bfs', 'dijkstra',
    'kruskal', 'prim', cada una con el resultado de su algoritmo."""
    partes = [
        _linea("REPORTE - SISTEMA DE ANALISIS DE RED DE TELEFERICOS"),
        f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Vertices: {grafo.num_vertices()}  Aristas: {grafo.num_aristas()}",
        f"Tipo de grafo: {'dirigido' if grafo.dirigido else 'no dirigido'}, ponderado",
        "",
    ]

    if "dijkstra" in resultados:
        partes.append(reporte_ruta_dijkstra(grafo, resultados["dijkstra"]))
        partes.append("")

    if "kruskal" in resultados and "prim" in resultados:
        partes.append(reporte_comparacion_mst(resultados["kruskal"], resultados["prim"]))
        partes.append("")

    if recomendaciones:
        partes.append(_linea("RECOMENDACIONES"))
        for r in recomendaciones:
            partes.append(f"- {r}")

    return "\n".join(partes)
