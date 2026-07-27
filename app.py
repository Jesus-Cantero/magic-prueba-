"""
app.py

Aplicación Flask: wiki de cartas de Magic the Gathering + creador de mazos.
Ejecutar con:
    python app.py
y abrir http://127.0.0.1:5000 en el navegador.

Requiere que ya se haya ejecutado antes:
    python download_cards.py
para tener la base de datos mtg_cards.db poblada.
"""

import os

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

import database as db

app = Flask(__name__)
app.secret_key = "cambia-esto-por-una-clave-secreta-en-produccion"


@app.route("/")
def index():
    texto = request.args.get("q", "")
    tipo = request.args.get("tipo", "")
    color = request.args.get("color", "")
    pagina = int(request.args.get("pagina", 1))

    if not os.path.exists(db.DB_PATH):
        flash("Todavía no hay base de datos de cartas. Ejecuta 'python download_cards.py' primero.")
        return render_template("index.html", cartas=[], total=0, texto=texto, tipo=tipo, color=color, pagina=1, total_paginas=1)

    cartas, total = db.buscar_cartas(texto, tipo, color, pagina)
    total_paginas = max(1, (total + 23) // 24)

    return render_template(
        "index.html",
        cartas=cartas,
        total=total,
        texto=texto,
        tipo=tipo,
        color=color,
        pagina=pagina,
        total_paginas=total_paginas,
    )


@app.route("/carta/<carta_id>")
def carta_detalle(carta_id):
    carta = db.obtener_carta(carta_id)
    if carta is None:
        flash("No se encontró esa carta.")
        return redirect(url_for("index"))
    mazos = db.listar_mazos()
    return render_template("card_detail.html", carta=carta, mazos=mazos)


@app.route("/mazos")
def listar_mazos():
    mazos = db.listar_mazos()
    return render_template("my_decks.html", mazos=mazos)


@app.route("/mazos/nuevo", methods=["POST"])
def crear_mazo():
    nombre = request.form.get("nombre", "").strip()
    formato = request.form.get("formato", "").strip()
    if not nombre:
        flash("El mazo necesita un nombre.")
        return redirect(url_for("listar_mazos"))
    mazo_id = db.crear_mazo(nombre, formato)
    return redirect(url_for("ver_mazo", mazo_id=mazo_id))


@app.route("/mazos/<int:mazo_id>")
def ver_mazo(mazo_id):
    mazo, cartas = db.obtener_mazo(mazo_id)
    if mazo is None:
        flash("No se encontró ese mazo.")
        return redirect(url_for("listar_mazos"))
    total_cartas = sum(c["cantidad"] for c in cartas)
    return render_template("deck_builder.html", mazo=mazo, cartas=cartas, total_cartas=total_cartas)


@app.route("/mazos/<int:mazo_id>/eliminar", methods=["POST"])
def eliminar_mazo(mazo_id):
    db.eliminar_mazo(mazo_id)
    flash("Mazo eliminado.")
    return redirect(url_for("listar_mazos"))


# ---------- Endpoints usados por JavaScript (AJAX) ----------

@app.route("/api/mazos/<int:mazo_id>/anadir", methods=["POST"])
def api_anadir_carta(mazo_id):
    data = request.get_json()
    carta_id = data.get("carta_id")
    cantidad = int(data.get("cantidad", 1))
    db.anadir_carta_a_mazo(mazo_id, carta_id, cantidad)
    return jsonify({"ok": True})


@app.route("/api/mazos/<int:mazo_id>/quitar", methods=["POST"])
def api_quitar_carta(mazo_id):
    data = request.get_json()
    carta_id = data.get("carta_id")
    db.quitar_carta_de_mazo(mazo_id, carta_id)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True)
