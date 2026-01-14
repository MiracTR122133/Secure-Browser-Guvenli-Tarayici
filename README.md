# Secure Browser

Secure Browser, Python ile geliştirilmiş, gizlilik ve bütünlük odaklı, açık kaynak bir masaüstü tarayıcı prototipidir.  
Proje, kullanıcı trafiğini yerel olarak denetlemeyi ve temel gizlilik ihlallerini azaltmayı amaçlar.

**Not:** İlk çalıştırmada uygulamayı **yönetici olarak** açarsanız gerekli Python kütüphaneleri otomatik olarak `pip` ile kurulabilir.  
Yönetici olarak çalıştırılmazsa, kütüphanelerin sistemde önceden yüklü olması gerekir.

---

## 🚀 Özellikler
- Dahili HTTP/HTTPS proxy (**mitmproxy**, zorunlu ve kapatılamaz)
- Reklam ve temel takip alan adı engelleme
- Çerez (Cookie) temizleme
- Sabit User-Agent kullanımı
- Dark Mode
- Panic butonu (**anında uygulama kapatma**)
- Dahili log sistemi (salt okunur)
- **Kriptografik Premium Lisans Sistemi (Ed25519 + CSV)**
- Ayarların yerel olarak saklanması (`settings.json`)
- Tek dosya mimarisi

---

## 🔐 Güvenlik Tasarımı
- Proxy kullanıcı tarafından **devre dışı bırakılamaz**
- Web içeriklerinin Python API çağırması **yetkilendirme token’ı ile korunur**
- JS → Python yetkisiz erişim engellenmiştir
- Harici tarayıcı açma / kaçış davranışı yoktur
- Lisans doğrulama yalnızca **public key** ile yapılır
- Lisans süresi ve imza bütünlüğü kontrol edilir

---

## 🧰 auto-py-to-exe ile EXE Oluşturma

### Kurulum (Install)
```bash
pip install auto-py-to-exe
```

### Çalıştırma (Run)
```bash
auto-py-to-exe
```

### Ayarlar (Configuration)
- Script Location: `Secure_Browser.py`
- Console Window: ❌ Disabled
- Onefile: ❌ (isteğe bağlı)
- Icon: kendi `.ico` dosyan
- Additional Files: `settings.json` (opsiyonel)

### Derleme
- **Convert** butonuna bas

---

## ⚠️ Önemli Notlar
- Cloudflare / CAPTCHA **bypass edilmez**
- VPN, DNS veya sistem seviyesi anonimlik sağlamaz
- Amaç **tam anonimlik değil**, gizliliği artırmaktır
- Bu yazılım bir “tam sınav tarayıcısı” değildir

---

## ⚖️ Yasal Açıklama
Bu yazılım:
- Eğitim ve kişisel kullanım amaçlıdır
- Kullanıcı, yerel yasalar ve hizmet şartlarından kendisi sorumludur
- Geliştirici, kötüye kullanımdan sorumlu tutulamaz

---

## 📌 Lisans
MIT License

---

Bu proje **~MiracTR** tarafından geliştirilmiştir.  
Menşei: Türkiye 🇹🇷

---

# -- English --

# Secure Browser

Secure Browser is an open-source, privacy- and integrity-focused desktop browser prototype developed in Python.  
It is designed to locally control web traffic and reduce common privacy risks.

**Note:** If the application is run as **administrator** on first launch, required Python libraries can be installed automatically via `pip`.  
Otherwise, dependencies must already be installed.

---

## 🚀 Features
- Built-in HTTP/HTTPS proxy (**mitmproxy**, mandatory and non-disableable)
- Ad and basic tracker domain blocking
- Cookie stripping
- Fixed User-Agent
- Dark Mode
- Panic button (**instant application exit**)
- Internal log system (read-only)
- **Cryptographic Premium License System (Ed25519 + CSV)**
- Local settings storage (`settings.json`)
- Single-file architecture

---

## 🔐 Security Design
- Proxy cannot be disabled by the user
- Web content → Python API calls are protected by an authorization token
- Unauthorized JS → Python access is blocked
- No external browser launch or escape behavior
- License verification uses **public-key cryptography only**
- License expiration and signature integrity are enforced

---

## 🧰 Creating an EXE with auto-py-to-exe

### Install
```bash
pip install auto-py-to-exe
```

### Run
```bash
auto-py-to-exe
```

### Configuration
- Script Location: `Secure_Browser.py`
- Console Window: Disabled
- Onefile: Optional
- Icon: your custom `.ico` file
- Additional Files: `settings.json` (optional)

### Build
- Click **Convert**

---

## ⚠️ Important Notes
- Cloudflare / CAPTCHA is NOT bypassed
- Does not provide VPN, DNS, or OS-level anonymity
- The goal is privacy improvement, not rule circumvention
- This is not a full lockdown exam browser

---

## ⚖️ Legal Disclaimer
This software is intended for **educational and personal use only**.  
Users are responsible for compliance with local laws and service terms.

---

## 📌 License
MIT License

---

This project was developed by **~MiracTR**  
Country of origin: Türkiye 🇹🇷
