# Secure_Browser.py
# Open-source Secure Browser Prototype
# Author: MiracTR (Türkiye)
# License: MIT
# Copyright (c) 2026 Mirac Gültepe
# All Rights Reserved
# Use Python 3.10+

import os
import sys
import json
import uuid
import time
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# =====================
# OPTIONAL IMPORTS
# =====================
try:
    import requests
except ImportError:
    requests = None

try:
    from supabase import create_client
except ImportError:
    create_client = None

# =====================
# FILES
# =====================
SETTINGS_FILE = "settings.json"
PROFILES_FILE = "profiles.json"
DEVICE_FILE = "device.id"
LOG_FILE = "browser.log"

# =====================
# DEFAULT SETTINGS
# =====================
DEFAULT_SETTINGS = {
    "virustotal_enabled": False,
    "virustotal_api_key": "",
    "chatgpt_enabled": False,
    "use_cloud": False,
    "supabase_url": "",
    "supabase_anon_key": "",
    "dark_mode": True,
    "fps_boost": False,
    "low_ram_mode": False
}

# =====================
# LOG SYSTEM
# =====================
def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# =====================
# DEVICE ID
# =====================
def get_device_id():
    if os.path.exists(DEVICE_FILE):
        return open(DEVICE_FILE).read().strip()
    did = str(uuid.uuid4())
    open(DEVICE_FILE, "w").write(did)
    return did

# =====================
# SETTINGS
# =====================
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    return json.load(open(SETTINGS_FILE, "r", encoding="utf-8"))

def save_settings(data):
    json.dump(data, open(SETTINGS_FILE, "w", encoding="utf-8"), indent=2)

# =====================
# PROFILES (LOCAL)
# =====================
def load_profiles():
    if not os.path.exists(PROFILES_FILE):
        json.dump({}, open(PROFILES_FILE, "w"))
    return json.load(open(PROFILES_FILE, "r", encoding="utf-8"))

def save_profiles(data):
    json.dump(data, open(PROFILES_FILE, "w", encoding="utf-8"), indent=2)

# =====================
# SUPABASE (OPTIONAL)
# =====================
def get_supabase_client(settings):
    if not settings.get("use_cloud"):
        return None
    if not create_client:
        log("Supabase library not installed")
        return None
    if not settings["supabase_url"] or not settings["supabase_anon_key"]:
        return None
    return create_client(settings["supabase_url"], settings["supabase_anon_key"])

def sync_profiles_cloud(settings, profiles):
    sb = get_supabase_client(settings)
    if not sb:
        return profiles

    device_id = get_device_id()

    try:
        res = sb.table("profiles").select("data").eq("device_id", device_id).execute()
        if res.data:
            log("Profiles loaded from cloud")
            save_profiles(res.data[0]["data"])
            return res.data[0]["data"]
        else:
            sb.table("profiles").insert({
                "device_id": device_id,
                "data": profiles
            }).execute()
            log("Profiles uploaded to cloud")
    except Exception as e:
        log(f"Cloud sync error: {e}")

    return profiles

# =====================
# VIRUSTOTAL (OPTIONAL)
# =====================
def virustotal_scan(url, api_key):
    if not requests:
        return "Requests module missing"

    headers = {"x-apikey": api_key}
    data = {"url": url}

    try:
        r = requests.post(
            "https://www.virustotal.com/api/v3/urls",
            headers=headers,
            data=data,
            timeout=15
        )
        return r.status_code
    except Exception as e:
        return str(e)

# =====================
# MAIN UI
# =====================
class SecureBrowser(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure Browser")
        self.geometry("1000x700")

        self.settings = load_settings()
        self.profiles = load_profiles()
        self.profiles = sync_profiles_cloud(self.settings, self.profiles)

        self.create_ui()
        log("Browser started")

    # -----------------
    def create_ui(self):
        self.style = ttk.Style()
        if self.settings["dark_mode"]:
            self.configure(bg="#1e1e1e")

        top = ttk.Frame(self)
        top.pack(fill="x")

        ttk.Button(top, text="🌐 Open URL", command=self.open_url).pack(side="left")
        ttk.Button(top, text="🛡 VT Scan", command=self.toggle_vt).pack(side="left")
        ttk.Button(top, text="👤 Profile", command=self.profile_menu).pack(side="left")
        ttk.Button(top, text="⚙ Advanced", command=self.advanced_menu).pack(side="left")
        ttk.Button(top, text="💬 ChatGPT", command=self.chatgpt_ui).pack(side="left")
        ttk.Button(top, text="💥 Panic", command=self.panic).pack(side="right")

        self.logbox = tk.Text(self, height=12)
        self.logbox.pack(fill="both", expand=True)
        self.refresh_logs()

    # -----------------
    def refresh_logs(self):
        if os.path.exists(LOG_FILE):
            self.logbox.delete("1.0", "end")
            self.logbox.insert("end", open(LOG_FILE).read())
        self.after(2000, self.refresh_logs)

    # -----------------
    def open_url(self):
        url = simpledialog.askstring("Open URL", "Enter URL:")
        if not url:
            return

        if self.settings["virustotal_enabled"]:
            res = virustotal_scan(url, self.settings["virustotal_api_key"])
            messagebox.showinfo("VirusTotal", f"Scan result: {res}")

        webbrowser.open(url)

    # -----------------
    def toggle_vt(self):
        self.settings["virustotal_enabled"] = not self.settings["virustotal_enabled"]
        save_settings(self.settings)
        messagebox.showinfo(
            "VirusTotal",
            f"VirusTotal {'enabled' if self.settings['virustotal_enabled'] else 'disabled'}"
        )

    # -----------------
    def profile_menu(self):
        name = simpledialog.askstring("Profile", "Profile name:")
        if not name:
            return
        self.profiles[name] = {"created": time.time()}
        save_profiles(self.profiles)
        messagebox.showinfo("Profile", f"Profile '{name}' saved")

    # -----------------
    def advanced_menu(self):
        win = tk.Toplevel(self)
        win.title("Advanced")

        def toggle(key):
            self.settings[key] = not self.settings[key]
            save_settings(self.settings)

        ttk.Checkbutton(win, text="FPS Boost", command=lambda: toggle("fps_boost")).pack(anchor="w")
        ttk.Checkbutton(win, text="Low RAM Mode", command=lambda: toggle("low_ram_mode")).pack(anchor="w")
        ttk.Checkbutton(win, text="Cloud Sync (Supabase)", command=lambda: toggle("use_cloud")).pack(anchor="w")

    # -----------------
    def chatgpt_ui(self):
        if not self.settings["chatgpt_enabled"]:
            messagebox.showwarning("ChatGPT", "ChatGPT integration is disabled")
            return
        messagebox.showinfo("ChatGPT", "Chat window placeholder")

    # -----------------
    def panic(self):
        webbrowser.open("https://www.google.com")
        self.destroy()

# =====================
# RUN
# =====================
if __name__ == "__main__":
    try:
        app = SecureBrowser()
        app.mainloop()
    except Exception as e:
        log(f"Fatal error: {e}")
