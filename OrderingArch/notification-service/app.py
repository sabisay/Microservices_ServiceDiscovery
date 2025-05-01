from flask import Flask, jsonify, request, render_template
from service_registery import register_service, discover_service

app = Flask(__name__)

register_service("notification-service", "notification-service", 5004)

notifications = []

@app.route('/notify', methods=['POST'])
def notify():
    data = request.json
    notifications.append(data['message'])
    print(f"🔔 Notification sent: {data['message']}")
    return jsonify({"status": "Notification sent"}), 200

@app.route('/')
def index():
    return render_template("notifications.html", messages=notifications)

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)