"""
download_cards.py

Descarga el "bulk data" de cartas de Scryfall (Oracle Cards: una entrada
por cada carta única, sin reimpresiones duplicadas) y las guarda en una
base de datos SQLite local (mtg_cards.db).

Ejecutar una sola vez para poblar la base de datos:
    python download_cards.py

Scryfall pide que las descargas de bulk data se hagan como mucho una vez
al día, así que no lo ejecutes en un bucle ni lo llames por cada búsqueda.
Más info: https://scryfall.com/docs/api/bulk-data
"""

import json
import sqlite3
import time
import urllib.request

DB_PATH = "mtg_cards.db"
BULK_DATA_INFO_URL = "https://api.scryfall.com/bulk-data/oracle-cards"
USER_AGENT = "MTGWikiApp/1.0 (proyecto personal educativo)"


def obtener_url_descarga():
    """Pregunta a Scryfall dónde está el archivo actual de oracle-cards."""
    req = urllib.request.Request(BULK_DATA_INFO_URL, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req) as resp:
        info = json.loads(resp.read().decode("utf-8"))
    return info["download_uri"]


def descargar_cartas(url):
    print(f"Descargando cartas desde {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    print(f"Descargadas {len(data)} cartas.")
    return data


def crear_tablas(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cartas (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            coste_mana TEXT,
            cmc REAL,
            tipo TEXT,
            texto TEXT,
            poder TEXT,
            resistencia TEXT,
            colores TEXT,
            identidad_color TEXT,
            rareza TEXT,
            set_code TEXT,
            set_nombre TEXT,
            imagen_url TEXT,
            legalidades TEXT
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_nombre ON cartas (nombre)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tipo ON cartas (tipo)")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS mazos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            formato TEXT,
            creado_en TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS mazo_cartas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mazo_id INTEGER NOT NULL,
            carta_id TEXT NOT NULL,
            cantidad INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (mazo_id) REFERENCES mazos (id) ON DELETE CASCADE,
            FOREIGN KEY (carta_id) REFERENCES cartas (id)
        )
    """)
    conn.commit()


def extraer_imagen(carta):
    # Algunas cartas (doble cara) no tienen image_uris en el nivel superior,
    # sino dentro de card_faces.
    if "image_uris" in carta:
        return carta["image_uris"].get("normal", "")
    if "card_faces" in carta and carta["card_faces"]:
        primera = carta["card_faces"][0]
        if "image_uris" in primera:
            return primera["image_uris"].get("normal", "")
    return ""


def insertar_cartas(conn, cartas):
    filas = []
    for c in cartas:
        # Ignoramos tokens, arte no oficial, etc. Solo cartas "normales" jugables.
        if c.get("layout") in ("token", "double_faced_token", "emblem", "art_series"):
            continue

        filas.append((
            c.get("id"),
            c.get("name", ""),
            c.get("mana_cost", ""),
            c.get("cmc", 0),
            c.get("type_line", ""),
            c.get("oracle_text", ""),
            c.get("power", ""),
            c.get("toughness", ""),
            ",".join(c.get("colors", [])),
            ",".join(c.get("color_identity", [])),
            c.get("rarity", ""),
            c.get("set", ""),
            c.get("set_name", ""),
            extraer_imagen(c),
            json.dumps(c.get("legalities", {})),
        ))

    conn.executemany("""
        INSERT OR REPLACE INTO cartas (
            id, nombre, coste_mana, cmc, tipo, texto, poder, resistencia,
            colores, identidad_color, rareza, set_code, set_nombre, imagen_url, legalidades
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, filas)
    conn.commit()
    print(f"Insertadas/actualizadas {len(filas)} cartas en la base de datos.")


def main():
    inicio = time.time()
    url = obtener_url_descarga()
    cartas = descargar_cartas(url)

    conn = sqlite3.connect(DB_PATH)
    crear_tablas(conn)
    insertar_cartas(conn, cartas)
    conn.close()

    print(f"Listo en {time.time() - inicio:.1f} segundos. Base de datos: {DB_PATH}")


if __name__ == "__main__":
    main()
