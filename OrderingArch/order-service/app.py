from flask import Flask, jsonify, render_template, request, redirect, url_for
import requests
import os
import py_eureka_client.eureka_client as eureka_client  # <<< ekle

app = Flask(__name__)

# Eureka URL'yi environment'dan al
EUREKA_URL = os.getenv("EUREKA_URL", "http://eureka-server:8761/eureka")

# Servislerin adreslerini tanımlama (Eureka'dan çekmek istiyorsak bunu ileride değiştireceğiz)
USER_SERVICE_URL = "http://user-service:5001"
PRODUCT_SERVICE_URL = "http://product-service:5002"
NOTIFICATION_SERVICE_URL = "http://notification-service:5004"

# --- Eureka Register ---
def register_to_eureka():
    instance_host = "order-service"  # docker-compose service name

    eureka_client.init(
        eureka_server=EUREKA_URL,
        app_name="order-service",
        instance_host=instance_host,
        instance_port=5003,
        health_check_url=f"http://localhost:5003/health",
        home_page_url=f"http://localhost:5003/",
        status_page_url=f"http://localhost:5003/"
    )

register_to_eureka()
# ------------------------

@app.route('/')
def index():
    # Kullanıcı ve ürün verilerini al
    users = requests.get(f"{USER_SERVICE_URL}/users").json()
    products = requests.get(f"{PRODUCT_SERVICE_URL}/products").json()
    return render_template("index.html", users=users, products=products["products"])

@app.route('/order', methods=['POST'])
def create_order():
    user_id = int(request.form.get("user_id"))
    product_id = int(request.form.get("product_id"))

    # Kullanıcıyı al
    users = requests.get(f"{USER_SERVICE_URL}/users").json()
    user = next((u for u in users if u['id'] == user_id), None)
    if user is None:
        return "User not found", 404

    # Ürünü al
    products = requests.get(f"{PRODUCT_SERVICE_URL}/products").json()["products"]
    product = next((p for p in products if p["id"] == product_id), None)
    if product is None:
        return "Product not found", 404

    # Bildirim gönder
    notification_data = {
        "message": f"📦 Order created for {user['name']} with product {product['name']}"
    }
    requests.post(f"{NOTIFICATION_SERVICE_URL}/notify", json=notification_data)

    return redirect(url_for('index'))

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
