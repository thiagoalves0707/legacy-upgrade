"""Locadora API - legacy (written for Flask 1.1, Python 3.x)."""
import datetime
import sqlite3
from decimal import Decimal, ROUND_HALF_UP

from flask import Flask, jsonify, request, abort
from flask.json.provider import DefaultJSONProvider


def legacy_json_default(o):
    """Mobile app expects prices as numbers and dates as dd/mm/YYYY."""
    if isinstance(o, Decimal):
        return float(o)
    if isinstance(o, datetime.date):
        return o.strftime("%d/%m/%Y")
    return DefaultJSONProvider.default(o)


class LegacyJSONProvider(DefaultJSONProvider):
    # Replaces app.json_encoder (removed in Flask 2.3). Must keep the exact
    # output of the old LegacyEncoder: the mobile app depends on it.
    default = staticmethod(legacy_json_default)


def strtobool(value):
    """Same behavior as the removed distutils.util.strtobool (gone in Python 3.12)."""
    value = value.lower()
    if value in ("y", "yes", "t", "true", "on", "1"):
        return 1
    if value in ("n", "no", "f", "false", "off", "0"):
        return 0
    raise ValueError(f"invalid truth value {value!r}")


app = Flask(__name__)
app.json = LegacyJSONProvider(app)

SEED = [
    (1, "Cidade de Deus", "9.90", 1, "2002-08-30"),
    (2, "Central do Brasil", "7.50", 1, "1998-04-03"),
    (3, "Tropa de Elite", "12.00", 0, "2007-10-05"),
    (4, "O Auto da Compadecida", "8.25", 1, "2000-09-10"),
]


def get_db():
    if not hasattr(app, "_db"):
        db = sqlite3.connect(":memory:", check_same_thread=False)
        db.execute("CREATE TABLE movies (id INTEGER PRIMARY KEY, title TEXT, daily_price TEXT, available INTEGER, released TEXT)")
        db.execute("CREATE TABLE rentals (id INTEGER PRIMARY KEY AUTOINCREMENT, movie_id INTEGER, customer TEXT, start TEXT, days INTEGER, total TEXT)")
        db.executemany("INSERT INTO movies VALUES (?,?,?,?,?)", SEED)
        db.commit()
        app._db = db
    return app._db


def movie_to_dict(row):
    return {
        "id": row[0],
        "title": row[1],
        "daily_price": Decimal(row[2]),
        "available": bool(row[3]),
        "released": datetime.date.fromisoformat(row[4]),
    }


def rental_total(price, days):
    total = price * days
    if days >= 7:
        total = total * Decimal("0.9")
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@app.errorhandler(404)
def not_found(_):
    return jsonify(error="not found"), 404


@app.route("/movies")
def list_movies():
    rows = get_db().execute("SELECT * FROM movies ORDER BY id").fetchall()
    movies = [movie_to_dict(r) for r in rows]
    only = request.args.get("available")
    if only is not None:
        movies = [m for m in movies if m["available"] == bool(strtobool(only))]
    return jsonify(movies=movies, count=len(movies))


@app.route("/movies/<int:movie_id>")
def get_movie(movie_id):
    row = get_db().execute("SELECT * FROM movies WHERE id=?", (movie_id,)).fetchone()
    if row is None:
        abort(404)
    return jsonify(movie_to_dict(row))


@app.route("/rentals", methods=["POST"])
def create_rental():
    # Old web form posts form-encoded data; mobile app posts JSON.
    # Werkzeug >= 2.1 raises on get_json() for non-JSON requests; Flask 1 returned
    # None. is_json keeps the old behavior (malformed JSON still returns 400).
    data = (request.get_json() if request.is_json else None) or request.form
    try:
        movie_id = int(data["movie_id"])
        days = int(data["days"])
        customer = data["customer"]
    except (KeyError, ValueError, TypeError):
        return jsonify(error="invalid rental"), 422
    row = get_db().execute("SELECT * FROM movies WHERE id=?", (movie_id,)).fetchone()
    if row is None:
        abort(404)
    movie = movie_to_dict(row)
    if not movie["available"]:
        return jsonify(error="movie not available"), 409
    start = datetime.date(2024, 1, 15) if data.get("start") is None else datetime.date.fromisoformat(data["start"])
    total = rental_total(movie["daily_price"], days)
    db = get_db()
    cur = db.execute("INSERT INTO rentals (movie_id, customer, start, days, total) VALUES (?,?,?,?,?)",
                     (movie_id, customer, start.isoformat(), days, str(total)))
    db.commit()
    return jsonify(id=cur.lastrowid, movie_id=movie_id, customer=customer, start=start,
                   due=start + datetime.timedelta(days=days), days=days, total=total), 201


if __name__ == "__main__":
    import sys
    app.run(port=int(sys.argv[1]) if len(sys.argv) > 1 else 5000)
