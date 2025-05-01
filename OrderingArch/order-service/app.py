from flask import Flask, jsonify, render_template, request, redirect, url_for
import requests
from service_registery import register_service, discover_service



app = Flask(__name__)

# USER_SERVICE_URL = "http://user-service:5001"
# PRODUCT_SERVICE_URL = "http://product-service:5002"
# NOTIFICATION_SERVICE_URL = "http://notification-service:5004"

#Service Discvoery

# USER_SERVICE_URL = discover_service("user-service")
# PRODUCT_SERVICE_URL = discover_service("product-service")
# NOTIFICATION_SERVICE_URL = discover_service("notification-service")

register_service("order-service", "order-service", 5003)

@app.route('/')
def index():
    # Kullanıcı ve ürün verilerini al
    users = requests.get(f"{discover_service('user-service')}/users").json()
    products = requests.get(f"{discover_service('product-service')}/products").json()
    return render_template("index.html", users=users, products=products["products"])

@app.route('/order', methods=['POST'])
def create_order():
    user_id = int(request.form.get("user_id"))
    product_id = int(request.form.get("product_id"))

    # Kullanıcıyı al
    users = requests.get(f"{discover_service('user-service')}/users").json()
    user = next((u for u in users if u['id'] == user_id), None)
    if user is None:
        return "User not found", 404

    # Ürünü al
    products = requests.get(f"{discover_service('product-service')}/products").json()["products"]
    product = next((p for p in products if p["id"] == product_id), None)
    if product is None:
        return "Product not found", 404

    # Bildirim gönder
    notification_data = {
        "message": f"📦 Order created for {user['name']} with product {product['name']}"
    }
    requests.post(f"{discover_service('notification-service')}/notify", json=notification_data)

    return redirect(url_for('index'))


@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
