# Microservices Backend Mimarisi & Consul Entegrasyonu

---

## 1. Genel Mimari

Bu projede 4 ana microservice bulunur:

* **User Service:** Kullanıcı işlemleri
* **Product Service:** Ürün işlemleri
* **Order Service:** Sipariş işlemleri
* **Notification Service:** Bildirim işlemleri

Servisler **bağımsızdır**, kendi başlarına ayağa kalkabilirler ve dış dünya ile REST API üzerinden konuşurlar.

---

## 2. Servislerin Klasör Yapısı

```
OrderingArch/
  |-- docker-compose.yml
  |-- user-service/
  |-- product-service/
  |-- order-service/
  |-- notification-service/
```

Her bir servis şu dosyalara sahip:

* `app.py`           → Servisin ana uygulaması (API endpoint’leri burada)
* `service_registery.py`  → Consul ile servis kaydı ve keşfi
* `Dockerfile`        → Container için yapılandırma
* `requirements.txt`  → Python bağımlılıkları

---

## 3. Servisler Nasıl Haberleşiyor?

Servisler birbirlerini **doğrudan hostname ve port ile değil**, Consul üzerinden bulur. Böylece dinamik olarak scale edilebilir, portu değişse bile diğer servisler anında yeni adresi öğrenir!

Örneğin:

* `order-service`, bir sipariş oluştururken `user-service` ve `product-service`’den veri ister.
* `notification-service`, sipariş oluştuğunda tetiklenir ve bildirim yollar.

---

## 4. Consul Nedir ve Ne İşe Yarar?

* Consul, **service discovery** sağlar: Servisler başlarken Consul’a “ben buradayım” der.
* Başka bir servis, ihtiyaç duyduğunda Consul’a sorar: “Bana çalışan product-service’leri söyle.” Consul ona adresleri ve portları söyler.
* Ayrıca health check, key-value store ve configuration management sağlar.

---

## 5. Consul Entegrasyonu: Adım Adım

Her serviste `service_registery.py` dosyası bulunur. Bu dosyada:

* Servisin adı, adresi, portu ve health check bilgisi tanımlanır.
* Uygulama başlatılırken Consul’a “register” edilir.
* Kapanınca “deregister” işlemi yapılır.

### Örnek Kod Parçası (service\_registery.py):

```python
import requests

def register_service(service_name, service_id, address, port):
    url = "http://consul:8500/v1/agent/service/register"
    payload = {
        "Name": service_name,
        "ID": service_id,
        "Address": address,
        "Port": port,
        "Check": {
            "HTTP": f"http://{address}:{port}/health",
            "Interval": "10s"
        }
    }
    requests.put(url, json=payload)
```

Her servis, `app.py` içinde bu fonksiyonu çağırarak Consul’a kendini kaydeder.

---

## 6. Docker-Compose ile Her Şeyin Ayağa Kaldırılması

`docker-compose.yml` dosyasında:

* Consul servis olarak tanımlı.
* Diğer tüm microservisler de tanımlı ve başlarken Consul ile entegre oluyorlar.

```yaml
services:
  consul:
    image: consul
    ports:
      - "8500:8500"
  user-service:
    build: ./user-service
    depends_on:
      - consul
  # diğer servisler de benzer şekilde...
```

---

## 7. Servisler Arası İletişim Şeması

Aşağıdaki şemada, servislerin birbirleriyle nasıl konuştuğunu ve Consul’ün ortadaki merkezi rolünü görebilirsin:

```
      +--------------------------------+
      |              Consul            |
      |        (Service Registry)      |
      +--------------------------------+
             ^      ^      ^         ^
             |      |      |         |
             |      |      |         |
             |      |      |         | 
+------------+   +--------------+   +------------------+
|User Service|   |Product Service|  |Notification Srv. |
+------------+   +--------------+   +------------------+
    \                /                 /
     \              /                 /
      +------------+-----------------+
                   |
            +--------------+
            |Order Service |
            +--------------+
```

* Tüm servisler **Consul'a kaydolur**.
* Birbirlerine erişmek istediklerinde **Consul üzerinden adres/port alırlar**.

---

## 8. Consul UI ile Takip

Consul’un web arayüzü sayesinde ([http://localhost:8500](http://localhost:8500)), hangi servisler ayakta, hangileri çökmüş, anlık görebilirsin.

---

## 9. Sık Sorulan Sorular

* **Neden Consul?**

  * Otomatik servis keşfi, hızlı scale etme, port çakışmasından kurtulma, servislerin anlık durumunu izleme.
* **Consul olmasa ne olurdu?**

  * Servis adresleri statik olurdu, dinamik yapılamazdı, sistem büyüdükçe kabus olurdu.
* **Consul down olursa?**

  * Servis keşfi geçici olarak yapılamaz; HA için cluster kurulmalı.

---

Tüm ekip arkadaşlarına ve gelecek nesillere hayırlı olsun!
