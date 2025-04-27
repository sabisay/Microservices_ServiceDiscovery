from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
import py_eureka_client.eureka_client as eureka_client
import os
import socket

app = Flask(__name__)
DATABASE = 'products.db'

EUREKA_URL = os.getenv("EUREKA_URL", "http://eureka-server:8761/eureka")

# -------------------
# Database
# -------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)')
    conn.commit()
    conn.close()

# Initialize DB immediately
init_db()

# -------------------
# Eureka Registration
# -------------------

def register_to_eureka():
    instance_host = "product-service"  # docker-compose service name

    eureka_client.init(
        eureka_server=EUREKA_URL,
        app_name="product-service",
        instance_host=instance_host,
        instance_port=5002,
        health_check_url=f"http://{instance_host}:5002/health",
        home_page_url=f"http://{instance_host}:5002/",
        status_page_url=f"http://{instance_host}:5002/"
    )


# Register immediately at startup
register_to_eureka()

# -------------------
# Routes
# -------------------

@app.route('/health')
def health():
    return "OK", 200

@app.route('/')
def home():
    conn = get_db()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template('products.html', products=products)

@app.route('/products')
def get_products():
    conn = get_db()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return jsonify({"products": [dict(row) for row in products]})

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    if name:
        conn = get_db()
        conn.execute("INSERT INTO products (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
    return redirect(url_for('home'))

# -------------------
# Run
# -------------------

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
