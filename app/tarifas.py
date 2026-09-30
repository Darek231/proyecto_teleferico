# -*- coding: utf-8 -*-
"""
tarifas.py

Calcula el costo en bolivianos de un viaje, segun las reglas reales del
Teleferico de La Paz / El Alto:

- Tarifa NORMAL: 3 Bs por la primera linea que usas. Si tu viaje requiere
  transbordo (cambiar de linea), cada linea adicional cuesta 2 Bs mas
  (no se vuelve a cobrar el pasaje completo).
- Tarifa PREFERENCIAL (estudiante / adulto mayor): 1.50 Bs la primera
  linea, cada transbordo adicional cuesta 1 Bs mas.

El costo depende de cuantas LINEAS distintas (colores) se usan en el
camino, no de cuantas estaciones tiene — dos estaciones seguidas de la
misma linea no generan cobro extra; solo un cambio de linea lo hace.
"""

TARIFAS = {
    "normal":        {"base": 3.0, "transbordo": 2.0},
    "preferencial":  {"base": 1.5, "transbordo": 1.0},
}

TIPOS_VALIDOS = tuple(TARIFAS.keys())


def lineas_del_camino(grafo, camino):
    """Dada una lista de ids de vertices en orden (un camino), devuelve
    la lista de lineas usadas, en el orden en que aparecen, sin repetir
    una linea si el tramo siguiente sigue siendo la misma (solo cuenta
    cuando efectivamente cambia)."""
    lineas = []
    for i in range(len(camino) - 1):
        u, v = camino[i], camino[i + 1]
        if v not in grafo.adyacencia.get(u, {}):
            raise ValueError(f"No existe el tramo {u}-{v} en el grafo")
        linea = grafo.adyacencia[u][v].get("linea") or "(sin nombre)"
        if not lineas or lineas[-1] != linea:
            lineas.append(linea)
    return lineas


def calcular_tarifa(grafo, camino, tipo_pasajero="normal"):
    """Calcula el costo de un camino (lista de ids de vertices, en el
    orden recorrido) para el tipo de pasajero indicado ('normal' o
    'preferencial'). Devuelve un diccionario con el desglose completo."""
    if tipo_pasajero not in TARIFAS:
        raise ValueError(
            f"tipo_pasajero debe ser uno de {TIPOS_VALIDOS}, se recibio '{tipo_pasajero}'"
        )

    if not camino or len(camino) < 2:
        return {
            "tipo_pasajero": tipo_pasajero,
            "lineas_usadas": [],
            "num_lineas": 0,
            "num_transbordos": 0,
            "tarifa": 0.0,
        }

    lineas = lineas_del_camino(grafo, camino)
    num_transbordos = max(0, len(lineas) - 1)
    tarifas = TARIFAS[tipo_pasajero]
    costo = tarifas["base"] + num_transbordos * tarifas["transbordo"]

    return {
        "tipo_pasajero": tipo_pasajero,
        "lineas_usadas": lineas,
        "num_lineas": len(lineas),
        "num_transbordos": num_transbordos,
        "tarifa": round(costo, 2),
    }


def calcular_todas_las_tarifas(grafo, camino):
    """Atajo para obtener normal y preferencial de una sola vez (lo que
    usa la interfaz web, para mostrar ambas)."""
    return {tipo: calcular_tarifa(grafo, camino, tipo) for tipo in TARIFAS}
