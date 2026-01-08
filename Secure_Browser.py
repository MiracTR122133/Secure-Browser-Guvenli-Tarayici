# ==========================================
# Secure Browser – Open Source Edition
# Author: Mirac Gültepe
# License: MIT
# Copyright (c) 2026 Mirac Gültepe
# All rights reserved.
#
# Project: Secure Browser (Privacy-focused Desktop Browser)
# ==========================================

import sys
import os
import subprocess
import threading
import time
import json
import csv
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox

# ==========================================
# AUTO PIP (OPTIONAL)
# ==========================================
def ensure(pkg, imp=None):
    try:
        __import__(imp or pkg)
    except:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        except:
            pass

ensure("pywebview", "webview")
ensure("mitmproxy")

import webview
from mitmproxy.tools.dump import DumpMaster
from mitmproxy import options, http

# ==========================================
# GLOBAL STATE
# ==========================================
APP_NAME = "Secure Browser"
SETTINGS_FILE = "settings.json"
LICENSE_SIGNATURE = "MiracGultepe111"

proxy_enabled = True
dark_mode = False
silent_mode = False
premium_enabled = False
premium_features = []

SEARCH_ENGINES = {
    "DuckDuckGo": "https://duckduckgo.com",
    "Google": "https://www.google.com",
    "Startpage": "https://www.startpage.com"
}

current_engine = "DuckDuckGo"

# ==========================================
# SETTINGS
# ==========================================
def load_settings():
    global current_engine, dark_mode, silent_mode
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                current_engine = data.get("search_engine", current_engine)
                dark_mode = data.get("dark_mode", False)
                silent_mode = data.get("silent_mode", False)
        except:
            pass

def save_settings():
    data = {
        "search_engine": current_engine,
        "dark_mode": dark_mode,
        "silent_mode": silent_mode,
        "premium_enabled": premium_enabled,
        "premium_features": premium_features
    }
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except:
        pass

# ==========================================
# LICENSE SYSTEM (CSV – SIMPLE SIGNATURE)
# ==========================================
def load_license():
    global premium_enabled, premium_features

    path = filedialog.askopenfilename(
        title="Select License CSV",
        filetypes=[("CSV Files", "*.csv")]
    )
    if not path:
        return

    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            row = next(reader)

        if row.get("signature") != LICENSE_SIGNATURE:
            messagebox.showerror("License Error", "Invalid license signature.")
            return

        expires = datetime.date.fromisoformat(row.get("expires_at"))
        if expires < datetime.date.today():
            messagebox.showerror("License Error", "License expired.")
            return

        premium_features = [x.strip() for x in row.get("features", "").split(",")]
        premium_enabled = True
        save_settings()

        messagebox.showinfo(
            "Premium Activated",
            f"Premium enabled!\nFeatures:\n- " + "\n- ".join(premium_features)
        )

    except Exception as e:
        messagebox.showerror("License Error", str(e))

# ==========================================
# PROXY
# ==========================================
BLOCKED = ["ads", "analytics", "doubleclick", "facebook"]

class BasicProxy:
    def request(self, flow: http.HTTPFlow):
        if not proxy_enabled:
            return

        host = flow.request.host.lower()
        if any(b in host for b in BLOCKED):
            flow.response = http.Response.make(403, b"Blocked")
            return

        flow.request.headers.pop("Cookie", None)
        flow.request.headers["User-Agent"] = "Mozilla/5.0 SecureBrowser"

def start_proxy():
    opts = options.Options(listen_host="127.0.0.1", listen_port=8080)
    m = DumpMaster(opts, with_termlog=False, with_dumper=False)
    m.addons.add(BasicProxy())
    m.run()

threading.Thread(target=start_proxy, daemon=True).start()

os.environ["HTTP_PROXY"] = "http://127.0.0.1:8080"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:8080"

# ==========================================
# UI FUNCTIONS
# ==========================================
def toggle_proxy():
    global proxy_enabled
    proxy_enabled = not proxy_enabled
    update_indicator()

def toggle_dark():
    global dark_mode
    dark_mode = not dark_mode
    css = "html{filter:invert(1) hue-rotate(180deg)}" if dark_mode else ""
    window.evaluate_js(
        f"""
        document.getElementById('dm')?.remove();
        document.head.insertAdjacentHTML('beforeend',
        '<style id="dm">{css}</style>');
        """
    )
    save_settings()

def toggle_silent():
    global silent_mode
    silent_mode = not silent_mode
    save_settings()

def change_engine(name):
    global current_engine
    current_engine = name
    window.load_url(SEARCH_ENGINES[name])
    save_settings()

def panic():
    try:
        paths = [
            r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        ]
        for p in paths:
            if os.path.exists(p):
                subprocess.Popen([p])
                break
    except:
        pass

    try:
        window.destroy()
    except:
        pass

    os._exit(0)

def update_indicator():
    color = "lime" if proxy_enabled else "red"
    window.evaluate_js(
        f"document.getElementById('px').style.background='{color}';"
    )

# ==========================================
# WINDOW
# ==========================================
load_settings()

window = webview.create_window(
    APP_NAME,
    SEARCH_ENGINES[current_engine],
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
        load_license
    )

    window.evaluate_js("""
    document.addEventListener('keydown', e=>{
        if(e.ctrlKey && e.shiftKey && e.key==='X'){ panic(); }
    });

    document.head.insertAdjacentHTML('beforeend',`
    <style>
    #ui{
        position:fixed;
        top:10px;
        right:10px;
        z-index:9999;
        display:flex;
        gap:6px;
        background:#000a;
        padding:8px;
        border-radius:12px;
        font-family:sans-serif
    }
    #px{
        width:14px;
        height:14px;
        border-radius:50%;
        background:lime;
        margin-top:6px
    }
    button,select{
        border:none;
        border-radius:6px;
        padding:4px 8px;
        cursor:pointer
    }
    button:hover{opacity:.85}
    </style>

    <div id="ui">
      <div id="px" title="Proxy Status"></div>
      <select onchange="change_engine(this.value)" title="Search Engine">
        <option>DuckDuckGo</option>
        <option>Google</option>
        <option>Startpage</option>
      </select>
      <button onclick="toggle_dark()" title="Dark Mode">🌙</button>
      <button onclick="toggle_silent()" title="Silent Mode">🔇</button>
      <button onclick="toggle_proxy()" title="Proxy Toggle">🛡</button>
      <button onclick="load_license()" title="Load Premium License">⭐</button>
      <button onclick="panic()" title="Panic Button" style="background:red;color:white">PANIC</button>
    </div>
    `);
    """)

    update_indicator()

webview.start(on_load)
