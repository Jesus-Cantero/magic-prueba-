"""
database.py

Funciones de acceso a la base de datos SQLite (mtg_cards.db).
Toda la lógica de consultas SQL vive aquí para mantener app.py limpio.
"""

import sqlite3

DB_PATH = "mtg_cards.db"


def obtener_conexion():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # nos permite acceder a columnas por nombre
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------- Cartas ----------

def buscar_cartas(texto="", tipo="", color="", pagina=1, por_pagina=24):
    conn = obtener_conexion()
    condiciones = []
    parametros = []

    if texto:
        condiciones.append("(nombre LIKE ? OR texto LIKE ?)")
        parametros.extend([f"%{texto}%", f"%{texto}%"])
    if tipo:
        condiciones.append("tipo LIKE ?")
        parametros.append(f"%{tipo}%")
    if color:
        # color es una letra: W, U, B, R, G, o "C" para incoloras
        if color == "C":
            condiciones.append("colores = ''")
        else:
            condiciones.append("colores LIKE ?")
            parametros.append(f"%{color}%")

    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
    offset = (pagina - 1) * por_pagina

    total = conn.execute(f"SELECT COUNT(*) FROM cartas {where}", parametros).fetchone()[0]
    filas = conn.execute(
        f"SELECT * FROM cartas {where} ORDER BY nombre LIMIT ? OFFSET ?",
        parametros + [por_pagina, offset]
    ).fetchall()
    conn.close()
    return filas, total


def obtener_carta(carta_id):
    conn = obtener_conexion()
    fila = conn.execute("SELECT * FROM cartas WHERE id = ?", (carta_id,)).fetchone()
    conn.close()
    return fila


# ---------- Mazos ----------

def crear_mazo(nombre, formato):
    conn = obtener_conexion()
    cur = conn.execute("INSERT INTO mazos (nombre, formato) VALUES (?, ?)", (nombre, formato))
    conn.commit()
    mazo_id = cur.lastrowid
    conn.close()
    return mazo_id


def listar_mazos():
    conn = obtener_conexion()
    filas = conn.execute("SELECT * FROM mazos ORDER BY creado_en DESC").fetchall()
    conn.close()
    return filas


def obtener_mazo(mazo_id):
    conn = obtener_conexion()
    mazo = conn.execute("SELECT * FROM mazos WHERE id = ?", (mazo_id,)).fetchone()
    cartas = conn.execute("""
        SELECT c.*, mc.cantidad
        FROM mazo_cartas mc
        JOIN cartas c ON c.id = mc.carta_id
        WHERE mc.mazo_id = ?
        ORDER BY c.nombre
    """, (mazo_id,)).fetchall()
    conn.close()
    return mazo, cartas


def anadir_carta_a_mazo(mazo_id, carta_id, cantidad=1):
    conn = obtener_conexion()
    existente = conn.execute(
        "SELECT id, cantidad FROM mazo_cartas WHERE mazo_id = ? AND carta_id = ?",
        (mazo_id, carta_id)
    ).fetchone()
    if existente:
        conn.execute(
            "UPDATE mazo_cartas SET cantidad = ? WHERE id = ?",
            (existente["cantidad"] + cantidad, existente["id"])
        )
    else:
        conn.execute(
            "INSERT INTO mazo_cartas (mazo_id, carta_id, cantidad) VALUES (?, ?, ?)",
            (mazo_id, carta_id, cantidad)
        )
    conn.commit()
    conn.close()


def quitar_carta_de_mazo(mazo_id, carta_id):
    conn = obtener_conexion()
    conn.execute("DELETE FROM mazo_cartas WHERE mazo_id = ? AND carta_id = ?", (mazo_id, carta_id))
    conn.commit()
    conn.close()


def eliminar_mazo(mazo_id):
    conn = obtener_conexion()
    conn.execute("DELETE FROM mazo_cartas WHERE mazo_id = ?", (mazo_id,))
    conn.execute("DELETE FROM mazos WHERE id = ?", (mazo_id,))
    conn.commit()
    conn.close()
