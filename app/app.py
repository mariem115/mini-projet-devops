import os
import time

from flask import Flask, jsonify, request

app = Flask(__name__)

_tasks = []
_next_id = 1


def reset_tasks():
    global _next_id
    _tasks.clear()
    _next_id = 1


def _db_host():
    return os.environ.get("DB_HOST", "").strip()


def _connect():
    import psycopg

    return psycopg.connect(
        host=_db_host(),
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ.get("DB_NAME", "campus"),
        user=os.environ.get("DB_USER", "campus"),
        password=os.environ.get("DB_PASSWORD", ""),
    )


def init_db():
    if not _db_host():
        return
    last_error = None
    for _ in range(15):
        try:
            with _connect() as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS tasks ("
                    "id SERIAL PRIMARY KEY, title TEXT NOT NULL)"
                )
            return
        except Exception as exc:
            last_error = exc
            time.sleep(1)
    raise last_error


def _read_title():
    data = request.get_json(silent=True) or {}
    return str(data.get("title", "")).strip()


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/tasks")
def list_tasks():
    if not _db_host():
        return jsonify(tasks=_tasks)
    with _connect() as conn:
        rows = conn.execute("SELECT id, title FROM tasks ORDER BY id").fetchall()
    return jsonify(tasks=[{"id": row[0], "title": row[1]} for row in rows])


@app.post("/tasks")
def create_task():
    global _next_id
    title = _read_title()
    if not title:
        return jsonify(error="titre requis"), 400
    if not _db_host():
        task = {"id": _next_id, "title": title}
        _next_id += 1
        _tasks.append(task)
        return jsonify(task), 201
    with _connect() as conn:
        row = conn.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title",
            (title,),
        ).fetchone()
    return jsonify({"id": row[0], "title": row[1]}), 201


if __name__ == "__main__":
    init_db()
    host = os.environ.get("APP_HOST", "0.0.0.0")
    port = int(os.environ.get("APP_PORT", "8080"))
    app.run(host=host, port=port)
