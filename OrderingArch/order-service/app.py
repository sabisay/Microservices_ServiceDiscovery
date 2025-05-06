from flask import Flask, jsonify, render_template, request, redirect, url_for
import requests
from kazoo.client import KazooClient
import socket
import atexit

# Zookeeper ayarı
zk = KazooClient(hosts='zookeeper:2181')
zk.start()

# Servis bilgisi
service_name = "order-service"
service_port = "5003"
service_address = socket.gethostbyname(socket.gethostname())

# Zookeeper'a kayıt
zk.ensure_path(f"/services/{service_name}")
zk.create(f"/services/{service_name}/{service_address}:{service_port}", ephemeral=True, makepath=True)

# Uygulama kapanınca Zookeeper bağlantısını kapat
atexit.register(zk.stop)

# Flask app
app = Flask(__name__)

USER_SERVICE_URL = "http://user-service:5001"
PRODUCT_SERVICE_URL = "http://product-service:5002"
NOTIFICATION_SERVICE_URL = "http://notification-service:5004"

@app.route('/')
def index():
    users = requests.get(f"{USER_SERVICE_URL}/users").json()
    products = requests.get(f"{PRODUCT_SERVICE_URL}/products").json()
    return render_template("index.html", users=users, products=products["products"])

@app.route('/order', methods=['POST'])
def create_order():
    user_id = int(request.form.get("user_id"))
    product_id = int(request.form.get("product_id"))

    users = requests.get(f"{USER_SERVICE_URL}/users").json()
    user = next((u for u in users if u['id'] == user_id), None)
    if user is None:
        return "User not found", 404

    products = requests.get(f"{PRODUCT_SERVICE_URL}/products").json()["products"]
    product = next((p for p in products if p["id"] == product_id), None)
    if product is None:
        return "Product not found", 404

    notification_data = {
        "message": f"📦 Order created for {user['name']} with product {product['name']}"
    }
    requests.post(f"{NOTIFICATION_SERVICE_URL}/notify", json=notification_data)

    return redirect(url_for('index'))

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(service_port))
