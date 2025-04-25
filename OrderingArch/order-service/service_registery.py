# service_registry.py

import requests
import random

CONSUL_HOST = "http://consul:8500"

def discover_service(service_name):
    try:
        url = f"{CONSUL_HOST}/v1/health/service/{service_name}?passing=true"
        response = requests.get(url)
        response.raise_for_status()
        services = response.json()
        if not services:
            raise Exception(f"No healthy services found for {service_name}")
        service = random.choice(services)
        address = service["Service"]["Address"]
        port = service["Service"]["Port"]
        return f"http://{address}:{port}"
    except Exception as e:
        raise Exception(f"Service discovery failed for {service_name}: {str(e)}")
