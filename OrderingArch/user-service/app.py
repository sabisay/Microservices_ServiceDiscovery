import sqlite3
import socket

from flask import Flask, jsonify, request, render_template, redirect, url_for
from service_registery import register_service


app = Flask(__name__, template_folder='templates')

register_service("user-service", socket.gethostname(), 5001)

# Veritabanı dosyasının adı
DATABASE = 'users.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    # Tabloyu oluştur (IF NOT EXISTS ile)
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)')
    # Başlangıç kullanıcılarını ekle (varsa görmezden gel) - ID'yi otomatik artan yapalım
    try:
        # Var olup olmadığını kontrol etmeden eklemek yerine, belki de sadece ilk çalıştırmada eklemek daha mantıklı olabilir.
        # Ama basitlik adına, mevcut kullanıcılar yoksa ekleyelim.
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
        print(f"Database error during init: {e}") # Hata olursa yazdır
    finally:
        conn.close()

# Uygulama başlamadan önce veritabanını başlat
init_db()



# API endpoint: JSON olarak kullanıcı listesi döner
@app.route('/users')
def get_users_api():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, name FROM users')
    # fetchall()'dan dönen Row nesnelerini dict'e çevir
    users = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(users)

# Ana sayfa: Kullanıcıları listeleyen HTML sayfasını render eder
@app.route('/')
def home():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, name FROM users')
    # fetchall()'dan dönen Row nesnelerini doğrudan şablona gönderebiliriz (row_factory sayesinde)
    # ya da güvenli tarafta kalıp dict'e çevirebiliriz:
    users = [dict(row) for row in c.fetchall()]
    conn.close()
    # users değişkenini şablona gönder
    return render_template('users.html', users=users)

# Yeni kullanıcı ekleme endpoint'i (POST metodu ile)
@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('name') # form'dan 'name' alanını al
    if name: # İsim boş değilse
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute('INSERT INTO users (name) VALUES (?)', (name,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding user: {e}") # Hata olursa yazdır
        finally:
            if conn:
                conn.close()
    # İşlem bittikten sonra ana sayfaya yönlendir
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


# Sağlık kontrolü endpoint'i
@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    # 0.0.0.0: Konteyner dışından erişim için
    # debug=True: Geliştirme sırasında hataları görmek için (üretimde False olmalı)
    # port=5001: User service'in çalışacağı port
    print("🔥 This is the running user-service app.py")
    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)