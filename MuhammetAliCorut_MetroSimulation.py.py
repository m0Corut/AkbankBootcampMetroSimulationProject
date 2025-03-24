# ---------------------------
# Gerekli Kütüphaneler
# ---------------------------
import tkinter as tk  # Arayüz (GUI) oluşturmak için
from tkinter import ttk, messagebox  # Gelişmiş tkinter bileşenleri ve uyarı kutuları için
import json  # JSON dosyalarını okuma/yazma işlemleri için
import requests  # API'den veri çekmek için (şu anda kullanılmıyor)
from collections import deque  # BFS için kuyruk yapısı
import networkx as nx  # Network (graf) yapısı oluşturmak için
import matplotlib.pyplot as plt  # Grafik çizimleri için
from matplotlib.offsetbox import AnnotationBbox, TextArea  # Harita üzerine kutular eklemek için
import contextily as ctx  # Harita arka planı (tile layer) için
from pyproj import Transformer  # Koordinat sistemleri dönüşümü için
from typing import List, Tuple, Dict  # Tip ipuçları için

# ---------------------------
# İstasyon Sınıfı
# ---------------------------
class Istasyon:
    def __init__(self, idx: str, ad: str, hat: str):
        self.idx = idx  # İstasyonun benzersiz kimliği
        self.ad = ad  # İstasyonun adı
        self.hat = hat  # Hangi hatta bulunduğu
        self.komsular: List[Tuple['Istasyon', int]] = []  # Komşular ve aradaki süre (dakika)

    def komsu_ekle(self, istasyon: 'Istasyon', sure: int):
        # Komşu istasyonları ve sürelerini listeye ekler
        self.komsular.append((istasyon, sure))

    def __str__(self):
        # Yazdırıldığında istasyonun adı görünür
        return self.ad

    def __lt__(self, other: 'Istasyon'):
        # Sıralama işlemleri için istasyon adı baz alınır
        return self.ad < other.ad

# ---------------------------
# Metro Ağı Sınıfı
# ---------------------------
class MetroAgi:
    def __init__(self):
        self.istasyonlar: Dict[str, Istasyon] = {}  # İstasyon adı: Istasyon nesnesi
        self.koordinatlar: Dict[str, Tuple[float, float]] = {}  # İstasyon adı: (lat, lon)

    def istasyon_ekle(self, idx: str, ad: str, hat: str, lat=None, lon=None):
        # Yeni istasyon ekle veya mevcutsa geç
        if ad not in self.istasyonlar:
            self.istasyonlar[ad] = Istasyon(idx, ad, hat)
        if lat and lon and ad not in self.koordinatlar:
            self.koordinatlar[ad] = (float(lat), float(lon))  # Koordinatlar atanır

    def baglanti_ekle(self, ad1: str, ad2: str, sure: int):
        # İki istasyonu karşılıklı komşu olarak bağla
        ist1 = self.istasyonlar.get(ad1)
        ist2 = self.istasyonlar.get(ad2)
        if ist1 and ist2:
            ist1.komsu_ekle(ist2, sure)
            ist2.komsu_ekle(ist1, sure)

# ---------------------------
# JSON'dan Metro Ağı Yükleme
# ---------------------------
def tum_hatlari_yukle_dosyadan(dosya_yolu="veriler/metro_ag.json"):
    # JSON dosyasından metro ağı yüklenir
    metro = MetroAgi()
    try:
        with open(dosya_yolu, "r", encoding="utf-8") as f:
            data = json.load(f)
            for istasyon in data["istasyonlar"]:
                metro.istasyon_ekle(
                    idx=istasyon.get("id", istasyon["ad"]),
                    ad=istasyon["ad"],
                    hat=istasyon.get("hat", ""),
                    lat=istasyon["lat"],
                    lon=istasyon["lon"]
                )
            for baglanti in data["baglantilar"]:
                metro.baglanti_ekle(baglanti["kaynak"], baglanti["hedef"], baglanti["sure"])
        print(f"[DEBUG] JSON'dan yüklendi - İstasyon sayısı: {len(metro.istasyonlar)}")
    except Exception as e:
        print("[HATA] JSON dosyasından yüklenemedi:", e)
    return metro

# ---------------------------
# En Az Aktarma Rota (BFS)
# ---------------------------
def en_az_aktarma_bul(metro: MetroAgi, baslangic_ad: str, hedef_ad: str):
    # Breadth-First Search (BFS) ile en az durak geçilen rota bulunur
    if baslangic_ad not in metro.istasyonlar or hedef_ad not in metro.istasyonlar:
        print(f"[HATA] '{baslangic_ad}' veya '{hedef_ad}' istasyonu bulunamadı.")
        return None
    ziyaret = set()
    kuyruk = deque([(metro.istasyonlar[baslangic_ad], [baslangic_ad])])
    while kuyruk:
        istasyon, rota = kuyruk.popleft()
        if istasyon.ad == hedef_ad:
            return rota
        ziyaret.add(istasyon.ad)
        for komsu, _ in istasyon.komsular:
            if komsu.ad not in ziyaret:
                kuyruk.append((komsu, rota + [komsu.ad]))
    return None

# ---------------------------
# En Kısa Süreli Rota (Dijkstra)
# ---------------------------
def en_kisa_sure_bul(metro: MetroAgi, baslangic_ad: str, hedef_ad: str):
    # Dijkstra algoritması kullanılarak en kısa süreli rota hesaplanır
    import heapq
    if baslangic_ad not in metro.istasyonlar or hedef_ad not in metro.istasyonlar:
        print(f"[HATA] '{baslangic_ad}' veya '{hedef_ad}' istasyonu bulunamadı.")
        return None, float('inf')
    baslangic = metro.istasyonlar[baslangic_ad]
    hedef = metro.istasyonlar[hedef_ad]
    kuyruk = [(0, baslangic, [baslangic.ad])]
    ziyaret = set()
    while kuyruk:
        sure, istasyon, rota = heapq.heappop(kuyruk)
        if istasyon.ad == hedef.ad:
            return rota, sure
        if istasyon.ad in ziyaret:
            continue
        ziyaret.add(istasyon.ad)
        for komsu, gecis_sure in istasyon.komsular:
            if komsu.ad not in ziyaret:
                heapq.heappush(kuyruk, (sure + gecis_sure, komsu, rota + [komsu.ad]))
    return None, float('inf')

# ---------------------------
# Rota Görselleştirme (Matplotlib + NetworkX + Contextily)
# ---------------------------
secilen_noktalar = []
press_coords = None

def rota_ciz(metro, rota: List[str], cmb_baslangic=None, cmb_hedef=None, txt_sonuc=None):
    global secilen_noktalar, press_coords
    secilen_noktalar = []

    # Graf yapısı oluştur
    G = nx.Graph()
    for istasyon in metro.istasyonlar.values():
        for komsu, sure in istasyon.komsular:
            G.add_edge(istasyon.ad, komsu.ad, weight=sure)

    # Koordinat dönüşümü (EPSG:4326 -> EPSG:3857)
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
    pos = {ad: transformer.transform(lon, lat) for ad, (lat, lon) in metro.koordinatlar.items()}

    fig, ax = plt.subplots(figsize=(12, 8))

    # Hat renklerini oku
    with open("veriler/hat_listesi.json", "r", encoding="utf-8") as f:
        hat_verileri = json.load(f)

    hat_renkleri = {}
    for hat in hat_verileri:
        hat_kodu = hat.get("Code", "")
        color_val = hat.get("Color", "skyblue")
        if isinstance(color_val, dict):
            renk = '#{0:02x}{1:02x}{2:02x}'.format(color_val.get("R", 135), color_val.get("G", 206), color_val.get("B", 235))
        else:
            renk = str(color_val).lower()
        if hat_kodu:
            hat_renkleri[hat_kodu] = renk

    # Düğümleri renklendir
    node_colors = []
    for ist in G.nodes():
        istasyon = metro.istasyonlar.get(ist)
        renk = hat_renkleri.get(istasyon.hat, 'skyblue') if istasyon else 'skyblue'
        node_colors.append(renk)

    # Ana grafiği çiz
    nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=125, font_size=6, ax=ax)

    # Rota varsa vurgula
    if rota:
        edges_in_path = list(zip(rota, rota[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=edges_in_path, edge_color='red', width=2, ax=ax)
        nx.draw_networkx_nodes(G, pos, nodelist=rota, node_color='red', ax=ax)

    # Harita katmanı ekle
    try:
        ctx.add_basemap(ax, crs="epsg:3857", source=ctx.providers.OpenStreetMap.Mapnik)
    except Exception as e:
        print("Harita yüklenemedi:", e)

    # Tıklama ile istasyon seçme
    def tiklama_olayi(event):
        global press_coords
        if press_coords is None:
            return
        dx = abs(event.x - press_coords[0])
        dy = abs(event.y - press_coords[1])
        if dx > 5 or dy > 5 or event.button != 1 or event.inaxes != ax:
            return

        # En yakın istasyonu bul
        from math import hypot
        en_yakin = None
        min_mesafe = float('inf')
        for ist, (x, y) in pos.items():
            mesafe = hypot(event.xdata - x, event.ydata - y)
            if mesafe < min_mesafe:
                en_yakin = ist
                min_mesafe = mesafe

        if en_yakin:
            secilen_noktalar.append(en_yakin)
            nx.draw_networkx_nodes(G, pos, nodelist=[en_yakin], node_color='lime', node_size=200, ax=ax)
            fig.canvas.draw_idle()

        # İki istasyon seçildiyse rota çiz
        if len(secilen_noktalar) == 2:
            baslangic, hedef = secilen_noktalar
            yol, sure = en_kisa_sure_bul(metro, baslangic, hedef)
            if txt_sonuc:
                txt_sonuc.delete('1.0', tk.END)
                txt_sonuc.insert(tk.END, f"En kısa süreli rota ({sure} dk):\n" + " -> ".join(yol))
            plt.close()
            if cmb_baslangic and cmb_hedef:
                cmb_baslangic.set(baslangic)
                cmb_hedef.set(hedef)
            rota_ciz(metro, yol, cmb_baslangic, cmb_hedef, txt_sonuc)

    # Zoom işlemleri
    def mouse_zoom(event):
        base_scale = 1.1
        scale_factor = 1 / base_scale if event.button == 'up' else base_scale if event.button == 'down' else None
        if scale_factor is None:
            return
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        xdata, ydata = event.xdata, event.ydata
        if xdata is None or ydata is None:
            return
        ax.set_xlim([xdata - (xdata - xlim[0]) * scale_factor, xdata + (xlim[1] - xdata) * scale_factor])
        ax.set_ylim([ydata - (ydata - ylim[0]) * scale_factor, ydata + (ylim[1] - ydata) * scale_factor])
        fig.canvas.draw_idle()

    # Event bağlantıları
    fig.canvas.mpl_connect('button_press_event', lambda e: globals().update(press_coords=(e.x, e.y)))
    fig.canvas.mpl_connect('button_release_event', tiklama_olayi)
    fig.canvas.mpl_connect('scroll_event', mouse_zoom)
    plt.title("Metro Rota Görselleştirme")
    plt.tight_layout()
    plt.show()

# ---------------------------
# Hat Bilgilerini JSON'dan Al
# ---------------------------
def istasyonlara_hat_bilgisi_ekle(metro, hat_json_path="veriler/hat_istasyonlari.json") -> List[str]:
    atanamayanlar = []
    try:
        with open(hat_json_path, "r", encoding="utf-8") as f:
            hat_istasyonlari = json.load(f)

        # JSON'daki hatlara göre istasyonlara hat ataması yapılır
        for hat_kodu, istasyon_listesi in hat_istasyonlari.items():
            for ad in istasyon_listesi:
                for istasyon in metro.istasyonlar.values():
                    if istasyon.ad.strip().lower() == ad.strip().lower():
                        istasyon.hat = hat_kodu
                        break

        # Hat atanmayanları listele
        for istasyon in metro.istasyonlar.values():
            if not istasyon.hat:
                atanamayanlar.append(istasyon.ad)

        if atanamayanlar:
            print("[UYARI] Hat bilgisi atanamayan istasyonlar:")
            for ist in atanamayanlar:
                print("  -", ist)
    except Exception as e:
        print("[HATA] Hat bilgisi eşleştirilemedi:", e)

    return atanamayanlar

# ---------------------------
# Uygulama Başlat
# ---------------------------
def uygulamayi_baslat():
    from tkinter import StringVar
    metro = tum_hatlari_yukle_dosyadan()
    atanamayanlar = istasyonlara_hat_bilgisi_ekle(metro)

    # Tkinter arayüzü oluştur
    pencere = tk.Tk()
    pencere.title("İstanbul Metro Rota Bulucu")
    pencere.geometry("600x600")

    # Hat seçimi
    ttk.Label(pencere, text="Hat Filtrele:").pack(pady=5)
    cmb_hat_filtre = ttk.Combobox(pencere, state="readonly")
    cmb_hat_filtre.pack(pady=5)

    # Başlangıç ve hedef istasyon
    ttk.Label(pencere, text="Başlangıç İstasyonu:").pack(pady=5)
    cmb_baslangic = ttk.Combobox(pencere, state="readonly")
    cmb_baslangic.pack(pady=5)

    ttk.Label(pencere, text="Hedef İstasyonu:").pack(pady=5)
    cmb_hedef = ttk.Combobox(pencere, state="readonly")
    cmb_hedef.pack(pady=5)

    # İstasyonları listele
    tum_istasyonlar = sorted(metro.istasyonlar.keys())
    cmb_baslangic["values"] = tum_istasyonlar
    cmb_hedef["values"] = tum_istasyonlar

    mevcut_hatlar = sorted(set(ist.hat for ist in metro.istasyonlar.values() if ist.hat))
    cmb_hat_filtre["values"] = ["Tümü"] + mevcut_hatlar
    cmb_hat_filtre.set("Tümü")

    # Hat filtreleme işlemi
    def hat_filtrele(*args):
        secili = cmb_hat_filtre.get()
        if secili == "Tümü":
            cmb_baslangic["values"] = tum_istasyonlar
            cmb_hedef["values"] = tum_istasyonlar
        else:
            filtreli = [ist.ad for ist in metro.istasyonlar.values() if ist.hat == secili]
            cmb_baslangic["values"] = filtreli
            cmb_hedef["values"] = filtreli

    cmb_hat_filtre.bind("<<ComboboxSelected>>", hat_filtrele)

    # Rota türü seçimi (süre / aktarma)
    rota_turu = StringVar(value="sure")
    ttk.Radiobutton(pencere, text="En Kısa Süre", variable=rota_turu, value="sure").pack()
    ttk.Radiobutton(pencere, text="En Az Aktarma", variable=rota_turu, value="aktarma").pack()

    # Sonuç metin kutusu
    txt_sonuc = tk.Text(pencere, height=10, width=60)
    txt_sonuc.pack(pady=10)

    # Rota hesapla butonu
    def rota_hesapla():
        baslangic = cmb_baslangic.get()
        hedef = cmb_hedef.get()
        yontem = rota_turu.get()
        if baslangic == "" or hedef == "" or baslangic == hedef:
            messagebox.showwarning("Uyarı", "Başlangıç ve hedef istasyonları farklı seçmelisiniz.")
            return

        if yontem == "sure":
            rota, sure = en_kisa_sure_bul(metro, baslangic, hedef)
            if rota:
                txt_sonuc.delete("1.0", tk.END)
                txt_sonuc.insert(tk.END, f"En kısa süreli rota ({sure} dk):" + " -> ".join(rota))
                rota_ciz(metro, rota, cmb_baslangic, cmb_hedef, txt_sonuc)
            else:
                txt_sonuc.insert(tk.END, "Rota bulunamadı.")
        else:
            rota = en_az_aktarma_bul(metro, baslangic, hedef)
            if rota:
                txt_sonuc.delete("1.0", tk.END)
                txt_sonuc.insert(tk.END, f"En az aktarmalı rota ({len(rota)-1} durak):" + " -> ".join(rota))
                rota_ciz(metro, rota, cmb_baslangic, cmb_hedef, txt_sonuc)
            else:
                txt_sonuc.insert(tk.END, "Rota bulunamadı.")

    # Butonlar
    ttk.Button(pencere, text="Rota Hesapla", command=rota_hesapla).pack(pady=10)
    ttk.Button(pencere, text="Haritadan Seç", command=lambda: rota_ciz(metro, [], cmb_baslangic, cmb_hedef, txt_sonuc)).pack(pady=5)

    pencere.mainloop()

# ---------------------------
# Ana Giriş Noktası
# ---------------------------
if __name__ == "__main__":
    uygulamayi_baslat()
