import os
import time
import psycopg2 
from psycopg2 import OperationalError
from flask import Flask, jsonify, request

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "mydb")
DB_USER = os.getenv("DB_USER", "myuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mypassword")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def wait_for_db(max_attempts=20, delay=2):
    for attempt in range(1, max_attempts+1):
        try:
            print(f'[INFO] Проверка PostgreSQL ({attempt}/{max_attempts})...')
            conn = get_connection()
            conn.close()
            print(f'[INFO] PostgreSQL доступен')
            return 
        except OperationalError as e:
            print(f'[WARN] PostgreSQL ещё не готов: {e}')
            time.sleep(delay)
    raise RuntimeError('PostgreSQL не стал доступен за отведённое время')

@app.route('/health')
def health():
    try:
        conn = get_connection()
        conn.close()
        return jsonify({"status": "ok", "db": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "error", "db": str(e)}), 500

@app.route("/api/users", methods=["GET"])
def list_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, created_at FROM users ORDER BY id;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    users = [
        {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "created_at": row[3].isoformat() if row[3] else None,
        }
        for row in rows
    ]
    return jsonify(users), 200

@app.route("/api/users", methods=["POST"])
def add_user():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()

    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400

    conn = get_connection()
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id, name, email;",
            (name, email),
        )
        new_id, new_name, new_email = cur.fetchone()
        return jsonify({"id": new_id, "name": new_name, "email": new_email}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    wait_for_db()
    app.run(host="0.0.0.0", port=5000)