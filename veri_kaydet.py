import requests
import json
"""
def get_hatlar():
    url = "https://api.ibb.gov.tr/MetroIstanbul/api/MetroMobile/V2/GetLines"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["Data"]

def veriyi_kaydet(dosya_yolu="veriler/metro_ag.json"):
    hatlar = get_hatlar()
    istasyonlar = []
    baglantilar = []
    eklenen = set()

    for hat in hatlar:
        line_id = hat["Id"]
        try:
            url = f"https://api.ibb.gov.tr/MetroIstanbul/api/MetroMobile/V2/GetStationById/{line_id}"
            response = requests.get(url)
            response.raise_for_status()
            stations = response.json()["Data"]

            for i in range(len(stations)):
                s = stations[i]
                ad = s["Description"]
                lat = s["DetailInfo"]["Latitude"]
                lon = s["DetailInfo"]["Longitude"]

                if ad not in eklenen:
                    istasyonlar.append({
                        "ad": ad,
                        "lat": lat,
                        "lon": lon
                    })
                    eklenen.add(ad)

                if i < len(stations) - 1:
                    hedef = stations[i + 1]["Description"]
                    baglantilar.append({
                        "kaynak": ad,
                        "hedef": hedef,
                        "sure": 2
                    })

        except Exception as e:
            print(f"[HATA] Hat ID {line_id}: {e}")

    with open(dosya_yolu, "w", encoding="utf-8") as f:
        json.dump({"istasyonlar": istasyonlar, "baglantilar": baglantilar}, f, ensure_ascii=False, indent=2)
        print(f"[✓] Veriler başarıyla kaydedildi → {dosya_yolu}")

if __name__ == "__main__":
    veriyi_kaydet()


def hatlari_apiden_cek_kaydet(dosya_yolu="veriler/hat_listesi.json"):
    url = "https://api.ibb.gov.tr/MetroIstanbul/api/MetroMobile/V2/GetLines"
    try:
        response = requests.get(url)
        response.raise_for_status()
        hatlar = response.json().get("Data", [])

        with open(dosya_yolu, "w", encoding="utf-8") as f:
            json.dump(hatlar, f, ensure_ascii=False, indent=4)

        print(f"[INFO] {len(hatlar)} hat başarıyla '{dosya_yolu}' dosyasına kaydedildi.")
    except Exception as e:
        print("[HATA] Hat bilgileri API'den alınamadı:", e)


import os
os.makedirs("veriler", exist_ok=True)
hatlari_apiden_cek_kaydet()
"""

import json
import os

# Örnek hatlara göre istasyon eşleşmeleri (elle hazırlanmış)
hat_istasyonlari_ornek = {
    "M1": [
        "Yenikapı", "Aksaray", "Emniyet-Fatih", "Topkapı-Ulubatlı", "Bayrampaşa-Maltepe",
        "Sağmalcılar", "Kocatepe", "Otogar", "Terazidere", "Davutpaşa-YTÜ", "Merter",
        "Zeytinburnu", "Bakırköy-İncirli", "Bahçelievler", "Ataköy-Şirinevler", "Yenibosna",
        "DTM-İstanbul Fuar Merkezi", "Atatürk Havalimanı"
    ],
    "M2": [
        "Hacıosman", "Darüşşafaka", "Atatürk Oto Sanayi", "İTÜ-Ayazağa", "Seyrantepe",
        "Sanayi Mahallesi", "4.Levent", "Levent", "Gayrettepe", "Şişli-Mecidiyeköy",
        "Osmanbey", "Taksim", "Şişhane", "Haliç", "Vezneciler-İstanbul Ü.", "Yenikapı"
    ],
    "M4": [
        "Kadıköy", "Ayrılık Çeşmesi", "Acıbadem", "Ünalan", "Göztepe", "Yenisahra",
        "Kozyatağı", "Bostancı", "Küçükyalı", "Maltepe", "Huzurevi", "Gülsuyu", "Esenkent",
        "Hastane-Adliye", "Soğanlık", "Kartal", "Pendik", "Tavşantepe", "Sabiha Gökçen Havalimanı"
    ]
}

# Kaydetme işlemi
os.makedirs("veriler", exist_ok=True)
with open("veriler/hat_istasyonlari.json", "w", encoding="utf-8") as f:
    json.dump(hat_istasyonlari_ornek, f, ensure_ascii=False, indent=4)

print("[INFO] Örnek hat_istasyonlari.json başarıyla oluşturuldu.")
