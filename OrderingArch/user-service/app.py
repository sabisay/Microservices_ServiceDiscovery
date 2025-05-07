import sqlite3
from flask import Flask, jsonify, request, render_template, redirect, url_for
from kazoo.client import KazooClient
from kazoo.exceptions import NodeExistsError
import socket
import atexit

# Zookeeper bağlantısı
zk = KazooClient(hosts='zookeeper:2181')
zk.start()

# Servis bilgisi
service_name = "user-service"
service_port = "5001"
service_address = socket.gethostbyname(socket.gethostname())

# Zookeeper kaydı
zk.ensure_path(f"/services/{service_name}")
node_path = f"/services/{service_name}/{service_address}:{service_port}"
try:
    zk.create(node_path, ephemeral=True, makepath=True)
    print(f"✅ Registered {service_name} at {node_path}")
except NodeExistsError:
    print(f"⚠️ Node already exists at {node_path}, skipping create.")

# Çıkışta Zookeeper bağlantısını kes
atexit.register(zk.stop)

# Veritabanı dosyasının adı
DATABASE = 'users.db'

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

init_db()

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

if __name__ == '__main__':
    print("🔥 This is the running user-service app.py")
    app.run(debug=True, host='0.0.0.0', port=int(service_port), use_reloader=False)
