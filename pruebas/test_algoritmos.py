# -*- coding: utf-8 -*-
import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))

import algoritmo
from grafo import Grafo

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
RUTA_VERTICES = os.path.join(BASE_DIR, "datos", "vertices.csv")
RUTA_ARISTAS = os.path.join(BASE_DIR, "datos", "aristas.csv")


def construir_grafo():
    g = Grafo(dirigido=False)
    g.cargar_desde_csv(RUTA_VERTICES, RUTA_ARISTAS)
    return g


class TestGrafoBasico(unittest.TestCase):
    def test_carga_csv(self):
        g = construir_grafo()
        self.assertGreaterEqual(g.num_vertices(), 10)
        self.assertGreaterEqual(g.num_aristas(), 15)

    def test_no_permite_arista_duplicada(self):
        g = construir_grafo()
        with self.assertRaises(ValueError):
            g.agregar_arista("V01", "V02", 5.5)

    def test_no_permite_peso_negativo(self):
        g = construir_grafo()
        g.agregar_vertice("VX", "Extra")
        g.agregar_vertice("VY", "Extra2")
        with self.assertRaises(ValueError):
            g.agregar_arista("VX", "VY", -3)

    def test_grafo_conexo(self):
        g = construir_grafo()
        self.assertTrue(g.es_conexo())


class TestRecorridos(unittest.TestCase):
    def test_dfs_alcanza_todo_en_grafo_conexo(self):
        g = construir_grafo()
        res = algoritmo.dfs(g, "V01")
        self.assertEqual(len(res["orden"]), g.num_vertices())
        self.assertEqual(res["no_alcanzables"], [])

    def test_bfs_niveles_no_negativos(self):
        g = construir_grafo()
        res = algoritmo.bfs(g, "V01")
        self.assertTrue(all(n >= 0 for n in res["nivel"].values()))


class TestDijkstra(unittest.TestCase):
    def test_distancia_a_si_mismo_es_cero(self):
        g = construir_grafo()
        res = algoritmo.dijkstra(g, "V01", "V01")
        self.assertEqual(res["costo"], 0)

    def test_camino_existe_entre_estaciones_conectadas(self):
        g = construir_grafo()
        res = algoritmo.dijkstra(g, "V01", "V03")
        self.assertIsNotNone(res["camino"])
        self.assertEqual(res["camino"][0], "V01")
        self.assertEqual(res["camino"][-1], "V03")

    def test_pesos_negativos_lanzan_error(self):
        g = construir_grafo()
        g.agregar_vertice("VX", "Extra")
        g.adyacencia["V01"]["VX"] = {"peso": -1, "unidad": "minutos", "linea": ""}
        with self.assertRaises(algoritmo.PesoNegativoError):
            algoritmo.dijkstra(g, "V01")


class TestArbolExpansionMinima(unittest.TestCase):
    def test_kruskal_y_prim_coinciden_en_costo(self):
        g = construir_grafo()
        k = algoritmo.kruskal(g)
        p = algoritmo.prim(g, "V01")
        self.assertAlmostEqual(k["costo_total"], p["costo_total"], places=6)

    def test_kruskal_arbol_tiene_n_menos_1_aristas(self):
        g = construir_grafo()
        k = algoritmo.kruskal(g)
        self.assertEqual(len(k["aceptadas"]), g.num_vertices() - 1)


if __name__ == "__main__":
    unittest.main()
