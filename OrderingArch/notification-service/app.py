from flask import Flask, jsonify, request, render_template
import os
import py_eureka_client.eureka_client as eureka_client

# Get the Eureka URL from the environment
EUREKA_URL = os.getenv("EUREKA_URL", "http://eureka-server:8761/eureka")

# Flask app
app = Flask(__name__)
notifications = []

# Health check endpoint
@app.route('/health')
def health():
    return "OK", 200

# Notification endpoint
@app.route('/notify', methods=['POST'])
def notify():
    data = request.json
    notifications.append(data['message'])
    print(f"🔔 Notification sent: {data['message']}")
    return jsonify({"status": "Notification sent"}), 200

# HTML view
@app.route('/')
def index():
    return render_template("notifications.html", messages=notifications)

# -------------------
# Eureka Registration
# -------------------

def register_to_eureka():
    instance_host = "notification-service"  # docker-compose service name

    eureka_client.init(
        eureka_server=EUREKA_URL,
        app_name="notification-service",
        instance_host=instance_host,
        instance_port=5004,
        health_check_url=f"http://localhost:5004/health",
        home_page_url=f"http://localhost:5004/",
        status_page_url=f"http://localhost:5004/"
    )


# Initialize Eureka registration immediately
register_to_eureka()

# Start the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)
