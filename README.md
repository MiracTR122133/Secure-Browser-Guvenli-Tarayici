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

## ---------------------

# Secure Browser

Secure Browser is a **privacy-focused, open-source desktop browser prototype** developed in Python.

## 🚀 Features
- Built-in HTTP/HTTPS proxy (mitmproxy)
- Ad and basic tracker blocking
- Dark Mode
- Panic button (instant close + launch Chrome)
- Error / log monitoring
- Optional VirusTotal integration
- Optional ChatGPT integration
- **Optional Premium License System (CSV + Cryptographic Verification)**
- Local settings storage (`settings.json`)
- Single-file architecture

## 🔐 Premium License System (CSV)
The premium system is **optional**.  
The application works fully without a license.

### Concept
- Licenses are distributed as **CSV files**
- The CSV contains an **encrypted and signed** `license_blob`
- The application verifies licenses using a **public key only**
- Fake or modified CSV files **will not work**

### Example Premium Features
- Turbo Mode (performance optimizations)
- Advanced privacy controls
- Cloud profile synchronization (optional)

## 📦 License Activation Flow
1. In the application, select **Premium → Load License**
2. The user selects a CSV file
3. The application:
   - Verifies the digital signature
   - Checks the expiration date
   - (Optional) Verifies device binding
4. If valid, premium features are enabled

## 🧰 Creating an EXE with auto-py-to-exe
1. Install:
   `pip install auto-py-to-exe`
2. Run:
   `auto-py-to-exe`
3. Configuration:
   - Script Location: `Secure_Browser.py`
   - Console Window: Disabled
   - Onefile: Optional
   - Icon: your custom `.ico` file
   - Additional Files: `settings.json` (optional)
4. Convert

## ⚠️ Important Notes
- Cloudflare / CAPTCHA **is not bypassed**
- The goal is to improve user privacy
- No illegal usage is intended

## ⚖️ Legal Disclaimer
This software is intended for educational and personal use only.  
Users are responsible for complying with local laws.

## 📌 License
MIT License

---

This project was created by the user **~MiracTR**.  
Origin: Türkiye 🇹🇷

