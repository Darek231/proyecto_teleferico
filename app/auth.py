# -*- coding: utf-8 -*-
"""
auth.py

Autenticacion simple basada en sesion de Flask, con dos roles:
- "admin": puede editar la red (agregar/quitar vertices y aristas, reiniciar)
- "usuario": solo puede consultar (rutas, DFS/BFS, Kruskal/Prim, reportes)

Los usuarios se guardan en datos/usuarios.json con la contraseña
hasheada (nunca en texto plano). Si ese archivo no existe todavia,
se crea automaticamente con dos usuarios de ejemplo la primera vez
que se ejecuta el servidor (ver USUARIOS_POR_DEFECTO abajo).
"""

import json
import os

from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_USUARIOS = os.path.join(BASE_DIR, "datos", "usuarios.json")

# Usuarios de ejemplo, solo para la primera vez que se corre el proyecto.
# IMPORTANTE: cambia estas contrasenas (o los usuarios) antes de usarlo
# en un contexto real / de entregar el proyecto en produccion.
USUARIOS_POR_DEFECTO = [
    {"usuario": "admin", "contrasena": "admin123", "rol": "admin"},
    {"usuario": "invitado", "contrasena": "invitado123", "rol": "usuario"},
]


def _asegurar_archivo_usuarios():
    if os.path.exists(RUTA_USUARIOS):
        return
    datos = [
        {
            "usuario": u["usuario"],
            "hash": generate_password_hash(u["contrasena"]),
            "rol": u["rol"],
        }
        for u in USUARIOS_POR_DEFECTO
    ]
    with open(RUTA_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def cargar_usuarios():
    _asegurar_archivo_usuarios()
    with open(RUTA_USUARIOS, encoding="utf-8") as f:
        return json.load(f)


def guardar_usuarios(usuarios):
    with open(RUTA_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=2)


def verificar_login(usuario, contrasena):
    """Devuelve el rol ('admin' / 'usuario') si las credenciales son
    correctas, o None si no lo son."""
    for u in cargar_usuarios():
        if u["usuario"] == usuario:
            if check_password_hash(u["hash"], contrasena):
                return u["rol"]
            return None
    return None


def crear_usuario(usuario, contrasena, rol="usuario"):
    """Util para agregar usuarios nuevos (ej. desde una consola de Python),
    no expuesto todavia por la interfaz web."""
    usuarios = cargar_usuarios()
    if any(u["usuario"] == usuario for u in usuarios):
        raise ValueError(f"El usuario '{usuario}' ya existe")
    usuarios.append(
        {"usuario": usuario, "hash": generate_password_hash(contrasena), "rol": rol}
    )
    guardar_usuarios(usuarios)
