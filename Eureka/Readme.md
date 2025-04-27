# ☁️ Microservices Architecture with Eureka Service Discovery

Bu proje, Java tabanlı **Eureka Server** kullanılarak, Python/Flask ile geliştirilen mikroservislerin merkezi bir yapıda haberleşmesini sağlar.

---

## 📦 Proje Kurulum Rehberi

### 1. Eureka Sunucusu Oluşturma

#### 🔹 Spring Initializr Ayarları

Spring Initializr üzerinden aşağıdaki bağımlılıklarla bir proje oluşturun:

| Dependency      | Açıklama                              |
|:----------------|:--------------------------------------|
| Spring Web      | Web uygulaması çatısı                 |
| Eureka Server   | Service Discovery Server kurulumu    |

<pre>Not: Proje tipi Gradle olarak seçilmelidir.</pre>

> **Build Tool:** Gradle  
> **Language:** Java

---
#### 🔹 Proje Yapılandırması

İndirilen proje dosyası içinde `...Application.java` dosyasını açarak gerekli anotasyonları eklediğinizden emin olun:

java
<pre>@EnableEurekaServer
@SpringBootApplication
public class EurekaServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(EurekaServerApplication.class, args);
    }
}
</pre>

Terminal üzerinden proje klasörüne gidin ve aşağıdaki komut ile build alın:
bash
<pre>./gradlew build</pre>

✅ Build sonrası build/ klasörü oluşacak ve Dockerfile gibi gerekli dosyalar hazır hale gelecektir.

`src/main/resources/application.properties` dosyasını şu şekilde güncelleyin:
<pre>server.port=8761

eureka.client.register-with-eureka=false
eureka.client.fetch-registry=false
</pre>

| Parametre     | Açıklama                              |
|:----------------|:--------------------------------------|
| egister-with-eureka=false     | Eureka sunucusu kendisini başka bir Eurekaya kayıt etmeyecek.                 |
| fetch-registry=false  | Başka bir Eureka sunucusundan bilgi çekilmeyecek (standalone mod).   |

### 2. Python Mikroservislerinin Eureka'ya Kaydedilmesi

2. Python Mikroservislerinin Eureka'ya Kaydedilmesi
####🔹 Sanal Ortam (Virtual Environment) Oluşturma

Öncelikle bir venv oluşturup aktif edin:

bash
<pre>
python3 -m venv venv
source venv/bin/activate
 </pre>

####🔹 Gerekli Kütüphanelerin Kurulumu

py_eureka_client kütüphanesini kurun:

bash
<pre>
pip install py_eureka_client
</pre>

Ardından requirements.txt dosyasına ekleyin:

<pre>
flask
py_eureka_client
</pre>

####🔹 Mikroservislerde Eurekaya Kayıt

Her Flask servisine aşağıdaki kayıt metodunu ekleyin:

python
<pre>import py_eureka_client.eureka_client as eureka_client

eureka_client.init(
    eureka_server="http://localhost:8761/eureka/",
    app_name="your-service-name",
    instance_port=5000
)
</pre>

`Önemli: Servis adınız <pre>app_name</pre> ile birebir uyumlu olmalıdır.`

### 🕸️ Servis Başlatma Sıralaması
#### 🔹 Mikroservislerin doğru çalışabilmesi için servislerin aşağıdaki sırayla başlatılması gerekir:

| Sıra | Servis           | Açıklama                                             |
| :---: | :---------------- | :--------------------------------------------------- |
| 1    | User Service      | Order servisi, User servisine ihtiyaç duyar.        |
| 2    | Product Service   | Order servisi, Product servisine ihtiyaç duyar.     |
| 3    | Order Service     | Bağımlı olduğu servisler (User/Product) çalışıyor olmalı. |

---

### ⚙️ Özet ve Ekstra Bilgiler

| Bileşen               | Teknoloji              |
| :--------------------- | :--------------------- |
| Service Discovery      | Spring Boot Eureka Server |
| Mikroservisler         | Flask (Python)         |
| İletişim Sağlama       | py_eureka_client       |
| Yapılandırma Aracı     | Gradle                 |
| API Gateway (Opsiyonel)| [Opsiyonel olarak eklenebilir] |


`Docker üzerinden Eureka Server'ı konteynerize etmek için hazır hale gelinmiştir.
İlerleyen adımlarda API Gateway (Spring Cloud Gateway) veya Circuit Breaker (Resilience4j) entegre edilebilir.
📢 Projenin sorunsuz ilerleyebilmesi için port çakışmalarına ve mikroservisler arasındaki bağımlılıklara dikkat edilmelidir!`
