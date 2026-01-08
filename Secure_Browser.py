# ==========================================
# Secure Browser – Open Source Edition
# Author: MiracTR
# License: MIT
# Copyright (c) 2026 Mirac Gültepe
# ==========================================

import sys, os, subprocess, threading, json, time
import tkinter as tk
from tkinter import messagebox, simpledialog

# ==========================================
# AUTO PIP
# ==========================================
def ensure(pkg, imp=None):
    try:
        __import__(imp or pkg)
    except Exception:
        subprocess.call([sys.executable, "-m", "pip", "install", pkg])

ensure("pywebview", "webview")
ensure("mitmproxy")
ensure("requests")

import webview
import requests
from mitmproxy.tools.dump import DumpMaster
from mitmproxy import options, http

# ==========================================
# SETTINGS
# ==========================================
SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "language": "tr",
    "proxy_enabled": True,
    "dark_mode": False,
    "gamer_mode": False,
    "use_virustotal": False,
    "virustotal_key": "",
    "use_chatgpt": False,
    "openai_key": ""
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()

def save_settings():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

settings = load_settings()

# ==========================================
# STARTUP WIZARD (NO HARDCODED KEYS)
# ==========================================
def startup_wizard():
    root = tk.Tk()
    root.withdraw()

    if messagebox.askyesno(
        "VirusTotal",
        "Dosya indirmelerinde VirusTotal taraması açılsın mı?"
    ):
        key = simpledialog.askstring(
            "VirusTotal API",
            "VirusTotal API anahtarını gir:",
            show="*"
        )
        if key:
            settings["use_virustotal"] = True
            settings["virustotal_key"] = key

    if messagebox.askyesno(
        "ChatGPT",
        "ChatGPT entegrasyonu açılsın mı?"
    ):
        key = simpledialog.askstring(
            "OpenAI API",
            "OpenAI API anahtarını gir:",
            show="*"
        )
        if key:
            settings["use_chatgpt"] = True
            settings["openai_key"] = key

    save_settings()

startup_wizard()

# ==========================================
# LOG SYSTEM
# ==========================================
logs = []

def log(msg):
    ts = time.strftime("%H:%M:%S")
    logs.append(f"[{ts}] {msg}")
    if len(logs) > 300:
        logs.pop(0)

def get_logs():
    return "\n".join(logs)

# ==========================================
# PROXY (LEGAL PRIVACY IMPROVEMENTS)
# ==========================================
BLOCKED_KEYWORDS = [
    "doubleclick",
    "googlesyndication",
    "adsystem",
    "analytics",
    "tracker",
    "facebook"
]

proxy_enabled = settings["proxy_enabled"]

class PrivacyProxy:
    def request(self, flow: http.HTTPFlow):
        global proxy_enabled
        if not proxy_enabled:
            return

        host = flow.request.host.lower()

        if any(k in host for k in BLOCKED_KEYWORDS):
            flow.response = http.Response.make(
                403, b"Blocked by Secure Browser"
            )
            log(f"Blocked: {host}")
            return

        flow.request.headers.pop("Cookie", None)
        flow.request.headers["User-Agent"] = "Mozilla/5.0"

        if "cloudflare" in host:
            log("Cloudflare algılandı (bypass yok)")

def start_proxy():
    opts = options.Options(
        listen_host="127.0.0.1",
        listen_port=8080
    )
    m = DumpMaster(
        opts,
        with_termlog=False,
        with_dumper=False
    )
    m.addons.add(PrivacyProxy())
    m.run()

threading.Thread(
    target=start_proxy,
    daemon=True
).start()

os.environ["HTTP_PROXY"] = "http://127.0.0.1:8080"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:8080"

# ==========================================
# OPTIONAL: VIRUSTOTAL
# ==========================================
def virustotal_scan(file_path):
    if not settings["use_virustotal"]:
        return "VirusTotal kapalı"

    try:
        headers = {"x-apikey": settings["virustotal_key"]}
        with open(file_path, "rb") as f:
            r = requests.post(
                "https://www.virustotal.com/api/v3/files",
                headers=headers,
                files={"file": f}
            )
        return f"VT Status: {r.status_code}"
    except Exception as e:
        return f"VT Error: {e}"

# ==========================================
# OPTIONAL: CHATGPT
# ==========================================
def chatgpt_request(prompt):
    if not settings["use_chatgpt"]:
        return "ChatGPT kapalı"

    try:
        import openai
        openai.api_key = settings["openai_key"]
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"ChatGPT Error: {e}"

# ==========================================
# UI FUNCTIONS
# ==========================================
def toggle_proxy():
    global proxy_enabled
    proxy_enabled = not proxy_enabled
    settings["proxy_enabled"] = proxy_enabled
    save_settings()
    log(f"Proxy {'Açık' if proxy_enabled else 'Kapalı'}")

def toggle_dark():
    settings["dark_mode"] = not settings["dark_mode"]
    save_settings()
    css = (
        "html{filter:invert(1) hue-rotate(180deg)}"
        if settings["dark_mode"] else ""
    )
    window.evaluate_js(
        f"document.getElementById('dm')?.remove();"
        f"document.head.insertAdjacentHTML("
        f"'beforeend','<style id=dm>{css}</style>');"
    )

def panic():
    log("PANIC tetiklendi")
    try:
        subprocess.Popen("start chrome", shell=True)
    except Exception:
        pass
    os._exit(0)

def show_logs():
    return get_logs()

# ==========================================
# WINDOW
# ==========================================
SEARCH_URL = "https://duckduckgo.com"

window = webview.create_window(
    "Secure Browser",
    SEARCH_URL,
    width=1200,
    height=750,
    private_mode=True
)

def on_load():
    window.expose(
        toggle_proxy,
        toggle_dark,
        panic,
        show_logs
    )

    window.evaluate_js("""
    const panel = document.createElement('div');
    panel.innerHTML = `
    <style>
      #sb-panel{
        position:fixed;
        top:10px;
        right:10px;
        z-index:99999;
        background:#111;
        color:#fff;
        padding:10px;
        border-radius:12px;
        display:flex;
        gap:6px
      }
      #sb-panel button{
        border:none;
        border-radius:6px;
        padding:6px 8px;
        cursor:pointer;
        background:#222;
        color:white
      }
      #sb-panel button:hover::after{
        content:attr(data-tip);
        position:absolute;
        top:42px;
        background:black;
        color:white;
        padding:4px 6px;
        border-radius:6px;
        font-size:12px;
        white-space:nowrap
      }
    </style>
    <div id="sb-panel">
      <button data-tip="Proxy Aç/Kapat" onclick="toggle_proxy()">🛡</button>
      <button data-tip="Dark Mode" onclick="toggle_dark()">🌙</button>
      <button data-tip="Loglar / Hatalar" onclick="alert(show_logs())">📜</button>
      <button data-tip="PANIC" style="background:red" onclick="panic()">PANIC</button>
    </div>
    `;
    document.body.appendChild(panel);
    """)

webview.start(on_load)
