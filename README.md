# Secure Browser

Secure Browser, Python ile geliştirilmiş, gizlilik odaklı ve açık kaynak bir masaüstü tarayıcı prototipidir.

## 🚀 Özellikler
- Dahili HTTP/HTTPS proxy (mitmproxy)
- Reklam ve temel takip engelleme
- Dark Mode
- Panic butonu (anında kapatma + Chrome açma)
- Hata / log görüntüleme
- Opsiyonel VirusTotal entegrasyonu
- Opsiyonel ChatGPT entegrasyonu
- **Opsiyonel Premium Lisans Sistemi (CSV + Kriptografik Doğrulama)**
- Ayarların yerel olarak saklanması (`settings.json`)
- Tek dosya mimarisi

## 🔐 Premium Lisans Sistemi (CSV)
Premium sistem **zorunlu değildir**. Uygulama lisanssız da çalışır.

**Mantık:**
- Lisanslar **CSV dosyası** olarak dağıtılır.
- CSV içeriği **şifreli + imzalı** bir `license_blob` içerir.
- Uygulama yalnızca **public key** ile doğrulama yapar.
- Sahte veya değiştirilmiş CSV **çalışmaz**.

**Premium ile açılabilecek örnek özellikler:**
- Turbo Mode (performans optimizasyonları)
- Advanced Privacy ayarları
- Bulut profil senkronizasyonu (opsiyonel)

## 📦 Lisans Yükleme Akışı
1. Uygulamada **Premium → Lisans Yükle** seçilir
2. Kullanıcı CSV dosyasını seçer
3. Uygulama:
   - İmzayı doğrular
   - Tarihi kontrol eder
   - (Opsiyonel) cihaz eşleşmesini kontrol eder
4. Geçerliyse premium aktif olur

## 🧰 auto-py-to-exe ile EXE Oluşturma
1. Kurulum:
   `pip install auto-py-to-exe`
2. Çalıştır:
   `auto-py-to-exe`
3. Ayarlar:
   - Script Location: `Secure_Browser.py`
   - Console Window: Disabled
   - Onefile: İsteğe bağlı
   - Icon: kendi `.ico` dosyan
   - Additional Files: `settings.json` (opsiyonel)
4. Convert

## ⚠️ Önemli Notlar
- Cloudflare / CAPTCHA **bypass edilmez**
- Amaç gizliliği artırmaktır
- Yasadışı kullanım amaçlanmaz

## ⚖️ Yasal Açıklama
Bu yazılım eğitim ve kişisel kullanım içindir.
Kullanıcı yerel yasalardan sorumludur.

## 📌 Lisans
MIT License

---
Bu proje ~MiracTR adlı kullanıcı tarafından yapıldı.  
Menşei: Türkiye 🇹🇷
