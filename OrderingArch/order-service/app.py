from flask import Flask, jsonify, render_template, request, redirect, url_for
import requests
import py_eureka_client.eureka_client as eureka_client
import os
import time

# Get Eureka URL
EUREKA_URL = os.getenv("EUREKA_URL", "http://eureka-server:8761/eureka")

app = Flask(__name__)

# Eureka Client global variables
USER_SERVICE_URL = None
PRODUCT_SERVICE_URL = None
NOTIFICATION_SERVICE_URL = None

# -------------------
# Eureka Registration
# -------------------

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


# -------------------
# Discover other services
# -------------------

def discover_services():
    global USER_SERVICE_URL, PRODUCT_SERVICE_URL, NOTIFICATION_SERVICE_URL

    try:
        user_instance = eureka_client.do_service("user-service")
        USER_SERVICE_URL = f"http://{user_instance.ipAddr}:{user_instance.port.port}"
        print(f"Discovered user-service at {USER_SERVICE_URL}")
    except Exception as e:
        print(f"Failed to discover user-service: {e}")

    try:
        product_instance = eureka_client.do_service("product-service")
        PRODUCT_SERVICE_URL = f"http://{product_instance.ipAddr}:{product_instance.port.port}"
        print(f"Discovered product-service at {PRODUCT_SERVICE_URL}")
    except Exception as e:
        print(f"Failed to discover product-service: {e}")

    try:
        notification_instance = eureka_client.do_service("notification-service")
        NOTIFICATION_SERVICE_URL = f"http://{notification_instance.ipAddr}:{notification_instance.port.port}"
        print(f"Discovered notification-service at {NOTIFICATION_SERVICE_URL}")
    except Exception as e:
        print(f"Failed to discover notification-service: {e}")

# -------------------
# Startup
# -------------------

discover_services()

# Wait a bit and then discover services (because they might not be up instantly)
time.sleep(5)

# Register to Eureka immediately
register_to_eureka()

# -------------------
# Routes
# -------------------

@app.route('/health')
def health():
    return "OK", 200

@app.route('/')
def index():
    if not USER_SERVICE_URL or not PRODUCT_SERVICE_URL:
        return "Services not discovered yet. Please try again later.", 503

    users = requests.get(f"{USER_SERVICE_URL}/users").json()
    products = requests.get(f"{PRODUCT_SERVICE_URL}/products").json()
    return render_template("index.html", users=users, products=products["products"])

@app.route('/order', methods=['POST'])
def create_order():
    if not USER_SERVICE_URL or not PRODUCT_SERVICE_URL or not NOTIFICATION_SERVICE_URL:
        return "Services not discovered yet. Please try again later.", 503

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

# -------------------
# Run
# -------------------

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
