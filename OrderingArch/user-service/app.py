import sqlite3
from flask import Flask, jsonify, request, render_template, redirect, url_for
import py_eureka_client.eureka_client as eureka_client
import os
import socket

# Get Eureka server URL
EUREKA_URL = os.getenv("EUREKA_URL", "http://eureka-server:8761/eureka")

# Database file
DATABASE = 'users.db'

# -------------------
# Database
# -------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)')
    try:
        c.execute("SELECT COUNT(*) FROM users")
        if c.fetchone()['COUNT(*)'] == 0:
            print("Initializing database with default users...")
            c.execute('INSERT INTO users (name) VALUES (?)', ("Alice",))
            c.execute('INSERT INTO users (name) VALUES (?)', ("Bob",))
            conn.commit()
            print("Default users added.")
        else:
            print("Database already contains users.")
    except sqlite3.Error as e:
        print(f"Database error during init: {e}")
    finally:
        conn.close()

# Initialize database immediately
init_db()

# -------------------
# Flask app
# -------------------

app = Flask(__name__, template_folder='templates')

@app.route('/users')
def get_users_api():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, name FROM users')
    users = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(users)

@app.route('/')
def home():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, name FROM users')
    users = [dict(row) for row in c.fetchall()]
    conn.close()
    return render_template('users.html', users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('name')
    if name:
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute('INSERT INTO users (name) VALUES (?)', (name,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding user: {e}")
        finally:
            if conn:
                conn.close()
    return redirect(url_for('home'))

@app.route('/users/<int:user_id>')
def get_user_by_id(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, name FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/health')
def health():
    return "OK", 200

# -------------------
# Eureka Registration
# -------------------

def register_to_eureka():
    instance_host = "user-service"  # docker-compose service name

    eureka_client.init(
        eureka_server=EUREKA_URL,
        app_name="user-service",
        instance_host=instance_host,
        instance_port=5001,
        health_check_url=f"http://{instance_host}:5001/health",
        home_page_url=f"http://{instance_host}:5001/",
        status_page_url=f"http://{instance_host}:5001/"
    )


# Register to Eureka immediately
register_to_eureka()

# -------------------
# Run
# -------------------

if __name__ == '__main__':
    print("🔥 This is the running user-service app.py")
    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)
