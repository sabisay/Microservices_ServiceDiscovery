from flask import Flask, jsonify, request, render_template
from kazoo.client import KazooClient
from kazoo.exceptions import NodeExistsError
import socket
import atexit

# Zookeeper bağlantısı
zk = KazooClient(hosts='zookeeper:2181')
zk.start()

# Servis bilgisi
service_name = "notification-service"
service_port = "5004"
service_address = socket.gethostbyname(socket.gethostname())

# Zookeeper'a kayıt (güvenli)
zk.ensure_path(f"/services/{service_name}")
node_path = f"/services/{service_name}/{service_address}:{service_port}"
try:
    zk.create(node_path, ephemeral=True, makepath=True)
except NodeExistsError:
    print(f"⚠️ Node already exists at {node_path}, skipping create.")

# Çıkışta bağlantıyı kapat
atexit.register(zk.stop)

# Flask uygulaması
app = Flask(__name__)
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
    app.run(debug=True, host='0.0.0.0', port=int(service_port))
