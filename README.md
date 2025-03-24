# AkbankBootcampMetroSimulationProject
1. Proje Başlığı ve Kısa Açıklama

Bu proje, İstanbul'daki metro ağı üzerinde en az aktarma veya en kısa süreli rotayı bulan ve bu rotayı harita üzerinde görselleştiren bir masaüstü uygulamasıdır. Kullanıcılar, başlangıç ve hedef istasyon seçimini hem combobox hem de interaktif harita üzerinden yapabilir.

2. Kullanılan Teknolojiler ve Kütüphaneler

🖥️ Masaüstü Arayüz

tkinter: Python’un yerleşik GUI kütüphanesidir. ComboBox, TextBox, Butonlar ve kullanıcı arayüzünü oluşturmak için kullanıldı.

🌍 Harita ve Görselleştirme

matplotlib: Grafikleri çizmek ve ağ yapısını görsel olarak göstermek için kullanıldı. Özellikle networkx ile birlikte çalıştı.

networkx: Metro istasyonları arasındaki bağlantıları modellemek için kullanılan graf kütüphanesi. BFS ve A* gibi algoritmaları bu yapı üzerinde çalıştırdık.

contextily: Harita zeminine OpenStreetMap gibi harita sağlayıcılarından taban harita eklemeye yarar.

pyproj: WGS84 (EPSG:4326) koordinatlarını Web Mercator (EPSG:3857) sistemine dönüştürmek için kullanıldı. Böylece harita üstüne doğru yerleştirme sağlandı.

📦 Veri İşleme ve Yardımcı Kütüphaneler

json: İstasyon ve bağlantı verilerini saklamak ve yüklemek için kullanıldı.

requests: İstanbul Büyükşehir Belediyesi’nin Metro API’lerinden veri çekmek için HTTP istekleri gönderdi.

📚 Veri Yapıları

collections.deque: BFS algoritması için kullanılan verimli bir çift yönlü kuyruk veri yapısı.

heapq: A* algoritması için kullanılan öncelikli kuyruk veri yapısı. Her zaman en kısa süresi olan düğüm öne alınır.

3. Algoritmaların Çalışma Mantığı

🔍 BFS (Breadth-First Search)

Amaç: En az aktarma yaparak hedef istasyona ulaşmak.

İlk olarak başlangıç düğümü bir kuyruğa alınır.

Her adımda kuyruğun başından bir düğüm çıkarılır ve bu düğüme komşu olan istasyonlar kuyruğa eklenir.

Ziyaret edilen istasyonlar bir set ile takip edilir.

Hedef istasyona ulaşıldığında, o ana kadar gelen yol döndürülür.

En erken varılan yol en az aktarma yapılan yoldur çünkü BFS katman katman ilerler.

✨ A* (A Star) Algoritması

Amaç: Gerçek süreye göre en hızlı rotayı bulmak.

Her adımda, şu ana kadar geçen süreye (g) ve hedefe olan tahmini mesafeye (h) göre toplam maliyet f = g + h hesaplanır.

heapq modülü kullanılarak, en düşük f değerine sahip düğüm öncelikli olarak işlenir.

Koşul sağlandığında hedefe giden en kısa süredeki yol bulunmuş olur.

Bizim uygulamamızda heuristik (h) fonksiyonu kullanılmadan sadece geçiş süresi toplandı (Dijkstra'nın özelleşmiş hali gibi).

⚙️ Neden Bu Algoritmalar?

BFS algoritması, istasyon sayısı az ve aktarma sayısı kullanıcı için önemliyse oldukça etkilidir.

A* algoritması (veya ağırlıklı kısa yol arama algoritmaları), zaman açısından daha verimli bir rota bulmak için tercih edilir.

Kullanıcıya bu iki algoritmayı seçme şansı vererek esneklik sağlandı.

4. Örnek Kullanım ve Test Sonuçları

🔹 Arayüzden Kullanım

Başlangıç: "Taksim"

Hedef: "Kadıköy"

Yöntem: "En Az Aktarma"

Çıktı: "Taksim -> Şişhane -> Haliç -> Vezneciler -> ... -> Kadıköy"

🔹 Haritadan Seçim

Harita üzerinden istasyonlara tıklanarak rota hesaplanabilir.

Önceki seçimler temizlenir, yeni rota hesaplanır.

Harita zoom ve kaydırma desteklidir.

5. Projeyi Geliştirme Fikirleri

🌐 Gerçek zamanlı sefer saatleri ve yoğunluk verisiyle rota güncelleme

🚷 Engelli kullanıcılar için erişilebilir durakları filtreleme (asansör/lift vb.)

📍 GPS konumu ile en yakın istasyona yönlendirme

🧭 Farklı ulaşım türleri (otobüs, metrobüs, vapur) ile entegre ulaşım ağı

💾 Kullanıcının favori rotalarını kaydetme ve paylaşma

💻 Web sürümü (Flask/Django + React ile)

