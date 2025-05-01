import requests
import random
import socket

CONSUL_HOST = "http://consul:8500"

def register_service(name, service_id, port):
    # Container içindeki hostname adres olarak kullanılır (örn: user-service)
    address = socket.gethostname()
    url = f"{CONSUL_HOST}/v1/agent/service/register"
    payload = {
        "Name": name,
        "ID": service_id,
        "Address": address,
        "Port": port,
        "Check": {
            "HTTP": f"http://{address}:{port}/health",
            "Interval": "10s",
            "Timeout": "1s"
        }
    }
    try:
        requests.put(url, json=payload)
        print(f"✅ {name} Consul'a kaydedildi")
    except Exception as e:
        print(f"❌ Consul register hatası: {e}")

def discover_service(service_name):
    url = f"{CONSUL_HOST}/v1/health/service/{service_name}?passing=true"
    try:
        res = requests.get(url)
        data = res.json()
        if not data:
            raise Exception(f"🔍 {service_name} için kayıt bulunamadı")

        # Load balancing: rastgele bir instance seç
        service = random.choice(data)["Service"]
        address = service["Address"]
        port = service["Port"]
        return f"http://{address}:{port}"
    except Exception as e:
        print(f"❌ Service discovery hatası: {e}")
        return None
