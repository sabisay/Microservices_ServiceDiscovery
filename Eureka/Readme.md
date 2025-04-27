
Eureka için önce Spring initializr üzerinden gerekli ayarları belirleyip (Spring Web ve Eureka Server dependencilerini ekle.) servis templatini indir. 

ardından main içerisindeki ...Application.java dosyasında okuma yaparak gerekli dependenciler eklenmiş mi kontrol et

ardından servisi klasörüne ayıklayarak "./gradlew build" komutu ile build al.

aldığın buildin ardından build klasörün ve Dockerfile için gerekli dosyalaar oluşturulmuş olacaktır. ve eureka servisin kullanılmaya ahzır.

properties klasöründe gerekli düzenlemeleri yap. port numarasını girip, fetch registery ve register with eureka yı false yap. bu şu anlama gelir:
register-with-eureka=false:
➔ This Eureka server will NOT register itself to another Eureka.
(It’s standalone.)

fetch-registry=false:
➔ This Eureka server will NOT fetch service info from another Eureka.
(It doesn’t act as a client.)


yazdığımız servisler python dilinde ama eureka java dilinde olduğu için aralarında gerekli iletişiimin sağlanabilmesi için:
pip install py_eureka_client
install ediyoruz. bunun için de öncesinde bir venv oluşturmak daha sağlıklı olur.

flask ile yazdığımız kodların eurekaya gradle ile register olması mümkün olmadığı için venv kurup gerekli kütüphaneyii ekledikten sonra, requirements dosyasına da kütüphaneyi ekliyoruz.
