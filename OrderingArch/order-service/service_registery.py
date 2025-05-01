import requests
from threading import Lock

# Tüm servislerin round robin index'ini tutar
round_robin_indices = {}
lock = Lock()

def register_service(service_name, service_id, service_port):
    payload = {
        "Name": service_name,
        "ID": service_id,
        "Address": service_id,  # hostname (container adı)
        "Port": service_port,
        "Check": {
            "HTTP": f"http://{service_id}:{service_port}/health",
            "Interval": "10s"
        }
    }
    try:
        res = requests.put("http://consul:8500/v1/agent/service/register", json=payload)
        print(f"[Service Register] {service_name} ({service_id}) registered with status code {res.status_code}")
    except Exception as e:
        print(f"[Service Register Error] {e}")

def discover_service(service_name):
    try:
        res = requests.get(f"http://consul:8500/v1/health/service/{service_name}?passing=true")
        services = res.json()
        if not services:
            raise Exception("No healthy service found")
        
        with lock:
            index = round_robin_indices.get(service_name, 0)
            selected = services[index % len(services)]
            round_robin_indices[service_name] = (index + 1) % len(services)
        
        address = selected['Service']['Address']
        port = selected['Service']['Port']
        return f"http://{address}:{port}"
    
    except Exception as e:
        print(f"[Service Discovery Error] {e}")
        return None
