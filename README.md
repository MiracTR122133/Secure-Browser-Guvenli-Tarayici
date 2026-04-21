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

Source Code to copy-paste/kopyala yapıştır yapmak için kaynak kodu:
´´´bash
# ============================================================
# Secure Browser (Security Hardened - Premium Removed)
# ============================================================

import os, sys, json, datetime, subprocess, threading, secrets

# =======================
# AUTO PIP
# =======================
def ensure(pkg, imp=None):
    try:
        __import__(imp or pkg)
    except:
        subprocess.call([sys.executable, "-m", "pip", "install", pkg])

ensure("pywebview", "webview")
ensure("mitmproxy")

import webview
from mitmproxy.tools.dump import DumpMaster
from mitmproxy import options, http

# =======================
# CONSTANTS
# =======================
SETTINGS_FILE = "settings.json"

SEARCH_ENGINES = {
    "DuckDuckGo": "https://duckduckgo.com",
    "Google": "https://www.google.com",
    "Startpage": "https://www.startpage.com"
}

# =======================
# STATE
# =======================
state = {
    "proxy": True,
    "dark": False,
    "silent": True,
    "engine": "DuckDuckGo"
}

logs = []
API_TOKEN = secrets.token_hex(32)  # 🔒 JS ↔ Python auth

# =======================
# SETTINGS
# =======================
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                state.update(json.load(f))
        except:
            pass

def save_settings():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

load_settings()

# =======================
# LOGGER
# =======================
def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    logs.append(entry)
    print(entry)

# =======================
# PROXY (LOCKED)
# =======================
BLOCKED = ["ads", "analytics", "doubleclick", "facebook"]

class SecureProxy:
    def request(self, flow: http.HTTPFlow):
        host = flow.request.host.lower()

        if any(b in host for b in BLOCKED):
            flow.response = http.Response.make(403, b"Blocked")
            log(f"Blocked: {host}")
            return

        # Remove tracking headers
        flow.request.headers.pop("Cookie", None)
        flow.request.headers["User-Agent"] = "Mozilla/5.0 SecureBrowser"

def start_proxy():
    opts = options.Options(listen_host="127.0.0.1", listen_port=8080)
    m = DumpMaster(opts, with_termlog=False, with_dumper=False)
    m.addons.add(SecureProxy())
    m.run()

threading.Thread(target=start_proxy, daemon=True).start()

os.environ["HTTP_PROXY"] = "http://127.0.0.1:8080"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:8080"

# =======================
# SECURE UI API
# =======================
def auth(token):
    return token == API_TOKEN

def toggle_dark(token):
    if not auth(token): 
        return

    state["dark"] = not state["dark"]

    css = "html{filter:invert(1) hue-rotate(180deg)}" if state["dark"] else ""

    window.evaluate_js(
        f"document.getElementById('dm')?.remove();"
        f"document.head.insertAdjacentHTML('beforeend','<style id=dm>{css}</style>');"
    )

    save_settings()

def change_engine(token, name):
    if not auth(token): 
        return

    if name in SEARCH_ENGINES:
        state["engine"] = name
        save_settings()
        window.load_url(SEARCH_ENGINES[name])

def panic(token):
    if not auth(token): 
        return

    window.destroy()
    os._exit(0)

def show_logs(token):
    if not auth(token): 
        return

    safe = "\\n".join(logs[-100:]).replace("`", "'")
    window.evaluate_js(f"alert(`{safe}`)")

# =======================
# WINDOW
# =======================
window = webview.create_window(
    "Secure Browser",
    SEARCH_ENGINES[state["engine"]],
    width=1100,
    height=700,
    private_mode=True
)

def on_load():
    window.expose(
        toggle_dark,
        change_engine,
        panic,
        show_logs
    )

    window.evaluate_js(f"""
    const TOKEN = "{API_TOKEN}";

    document.addEventListener('keydown', e=>{
        if(e.ctrlKey && e.shiftKey && e.key==='X') panic(TOKEN);
    });

    document.head.insertAdjacentHTML('beforeend',`
    <style>
    #ui{{position:fixed;top:10px;right:10px;z-index:9999;
    display:flex;gap:6px;background:#000a;padding:8px;border-radius:10px}}
    button,select{{border:none;border-radius:6px;padding:4px 8px}}
    </style>
    <div id=ui>
      <select onchange="change_engine(TOKEN,this.value)">
        <option>DuckDuckGo</option>
        <option>Google</option>
        <option>Startpage</option>
      </select>
      <button onclick="toggle_dark(TOKEN)">🌙</button>
      <button onclick="show_logs(TOKEN)">📜</button>
      <button onclick="panic(TOKEN)" style="background:red;color:white">PANIC</button>
    </div>
    `);
    """)

webview.start(on_load)
´´´
