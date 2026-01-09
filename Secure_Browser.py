# ============================================================
# Secure Browser
#
# Author: Mirac Gültepe
# License: MIT
# Copyright (c) 2026 Mirac Gültepe
# All rights reserved.
#
# Menşei/Country of origin: Türkiye
# ============================================================

import os
import sys
import json
import csv
import base64
import hashlib
import datetime
import subprocess
import threading
import time

# =======================
# AUTO PIP
# =======================
def ensure(pkg, imp=None):
    try:
        __import__(imp or pkg)
    except Exception:
        subprocess.call([sys.executable, "-m", "pip", "install", pkg])

ensure("pywebview", "webview")
ensure("mitmproxy")
ensure("cryptography")

import webview
from mitmproxy.tools.dump import DumpMaster
from mitmproxy import options, http
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

# =======================
# CONSTANTS
# =======================
SETTINGS_FILE = "settings.json"

PUBLIC_KEY_BASE64 = "zbUL0WrFbdNsRrDY0yerwLLG6D/vnX/LCyhE9PTeelw="

SEARCH_ENGINES = {
    "DuckDuckGo": "https://duckduckgo.com",
    "Google": "https://www.google.com",
    "Startpage": "https://www.startpage.com"
}

# =======================
# GLOBAL STATE
# =======================
state = {
    "proxy": True,
    "dark": False,
    "silent": True,
    "premium": False,
    "engine": "DuckDuckGo"
}

logs = []

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
# PREMIUM LICENSE VERIFY
# =======================
def verify_license(csv_path):
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            row = next(reader)

        payload = f"{row['license_id']}|{row['expires_at']}"
        signature = base64.b64decode(row["signature"])

        pub = Ed25519PublicKey.from_public_bytes(
            base64.b64decode(PUBLIC_KEY_BASE64)
        )

        pub.verify(signature, payload.encode())

        exp = datetime.datetime.fromisoformat(row["expires_at"])
        if exp < datetime.datetime.utcnow():
            log("License expired")
            return False

        log("Premium license valid")
        return True

    except InvalidSignature:
        log("Invalid license signature")
        return False
    except Exception as e:
        log(f"License error: {e}")
        return False

# =======================
# PROXY
# =======================
BLOCKED = ["ads", "analytics", "doubleclick", "facebook"]

class SecureProxy:
    def request(self, flow: http.HTTPFlow):
        if not state["proxy"]:
            return

        host = flow.request.host.lower()
        if any(b in host for b in BLOCKED):
            flow.response = http.Response.make(403, b"Blocked")
            log(f"Blocked: {host}")
            return

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
# UI ACTIONS
# =======================
def toggle_proxy():
    state["proxy"] = not state["proxy"]
    save_settings()

def toggle_dark():
    state["dark"] = not state["dark"]
    css = "html{filter:invert(1) hue-rotate(180deg)}" if state["dark"] else ""
    window.evaluate_js(
        f"document.getElementById('dm')?.remove();"
        f"document.head.insertAdjacentHTML('beforeend','<style id=dm>{css}</style>');"
    )
    save_settings()

def toggle_silent():
    state["silent"] = not state["silent"]
    save_settings()

def change_engine(name):
    state["engine"] = name
    save_settings()
    window.load_url(SEARCH_ENGINES[name])

def panic():
    try:
        subprocess.Popen("start chrome", shell=True)
    except:
        pass
    window.destroy()
    os._exit(0)

def load_license():
    path = window.create_file_dialog(webview.OPEN_DIALOG)
    if path:
        if verify_license(path[0]):
            state["premium"] = True
            save_settings()
            window.evaluate_js("alert('Premium Activated')")
        else:
            window.evaluate_js("alert('Invalid License')")

def show_logs():
    text = "\\n".join(logs[-200:])
    window.evaluate_js(f"alert(`{text}`)")

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
        toggle_proxy,
        toggle_dark,
        toggle_silent,
        change_engine,
        panic,
        load_license,
        show_logs
    )

    window.evaluate_js("""
    document.addEventListener('keydown', e=>{
        if(e.ctrlKey && e.shiftKey && e.key==='X'){ panic(); }
    });

    document.head.insertAdjacentHTML('beforeend',`
    <style>
    #ui{position:fixed;top:10px;right:10px;z-index:9999;
    display:flex;gap:6px;background:#000a;padding:8px;border-radius:10px}
    button,select{border:none;border-radius:6px;padding:4px 8px}
    </style>
    <div id=ui>
      <select onchange="change_engine(this.value)">
        <option>DuckDuckGo</option>
        <option>Google</option>
        <option>Startpage</option>
      </select>
      <button onclick="toggle_dark()">🌙</button>
      <button onclick="toggle_silent()">🔇</button>
      <button onclick="toggle_proxy()">🛡</button>
      <button onclick="load_license()">⭐ Premium</button>
      <button onclick="show_logs()">📜 Logs</button>
      <button onclick="panic()" style="background:red;color:white">PANIC</button>
    </div>
    `);
    """)

webview.start(on_load)
