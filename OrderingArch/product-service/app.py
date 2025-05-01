from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
from service_registery import register_service, discover_service

app = Flask(__name__)

register_service("product-service", "product-service", 5002)

DATABASE = 'products.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

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

@app.route('/health')
def health():
    return "OK", 200

def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)')
    conn.commit()
    conn.close()

init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
