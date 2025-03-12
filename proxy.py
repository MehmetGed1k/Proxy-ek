from playwright.sync_api import sync_playwright
import os
import time

# Proxy listesi alınacak web sitesi
URL = "https://spys.one/en/socks-proxy-list/"
OUTPUT_DIR = r"C:\Users\alone\Desktop\proxler"

# Proxy listesini saklamak için
all_proxies = []
us_proxies = []
us_variations = ["united states", "usa", "u.s.", "america", "United State"]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=["--start-maximized"])
    page = browser.new_page()
    page.set_viewport_size({"width": 1366, "height": 768})  # Normal bir kullanıcı gibi görün
    
    # Siteye git
    print("🔄 Siteye gidiliyor...")
    page.goto(URL)
    page.wait_for_load_state("networkidle")  # Sayfanın tamamen yüklenmesini bekle

    try:
        # 500 seçeneğini tekrar tekrar seç, eğer site tekrar 30'a düşürüyorsa düzelt
        print("⚙ Proxy liste uzunluğu 500 olarak ayarlanıyor...")
        for _ in range(3):  # 3 kez dene, eğer site geri 30'a çekerse tekrar düzelt
            page.select_option("select[name='xpp']", "5")
            time.sleep(5)  # Seçim sonrası bekle
            current_value = page.evaluate("document.querySelector('select[name=\"xpp\"]').value")
            if current_value == "5":
                print("✅ 500 proxy gösterimi aktif!")
                break
            print("⚠ Site tekrar 30'a çekti, yeniden ayarlanıyor...")

        time.sleep(10)  # Sayfanın tamamen yüklenmesi için ekstra bekleme süresi
        page.wait_for_load_state("networkidle")  # Seçim sonrası sayfanın tamamen yüklenmesini bekle
        
        # Sayfanın en altına kadar kaydırarak tüm proxy'leri yükle
        for _ in range(10):
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            time.sleep(2)  # Scroll işlemi sonrası bekle
        page.wait_for_selector("tr.spy1, tr.spy1x", timeout=60000)
    except Exception as e:
        print(f"⚠ Gösterim sayısı değiştirilemedi: {e}")

    print("📡 Proxy'ler çekiliyor...")

    # Tüm proxy listesini al
    rows = page.query_selector_all("tr.spy1, tr.spy1x")
    if not rows:
        print("⚠ Proxy listesi bulunamadı!")
    else:
        for row in rows:
            try:
                cells = row.query_selector_all("td")
                if len(cells) > 3:
                    proxy_info = cells[0].inner_text().strip()
                    country = cells[3].inner_text().strip().lower()
                    if ":" in proxy_info:
                        # Yalnızca IP ve port'u alıyoruz
                        proxy_parts = proxy_info.split(":")
                        if len(proxy_parts) == 2:
                            ip = proxy_parts[0].strip()
                            port = proxy_parts[1].strip()
                            formatted_proxy = f"{ip}:{port}"
                            all_proxies.append(formatted_proxy)
                            if any(variant in country for variant in us_variations):
                                us_proxies.append(formatted_proxy)
                            print(f"🌍 {formatted_proxy} - {country}")
            except Exception as e:
                print(f"⚠ Hata: {e}")

    browser.close()

# Proxy listesini dosyaya kaydet
os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(os.path.join(OUTPUT_DIR, "all_proxies.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(all_proxies))
with open(os.path.join(OUTPUT_DIR, "us_proxies.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(us_proxies))

print(f"✅ {len(all_proxies)} adet proxy kaydedildi.")
