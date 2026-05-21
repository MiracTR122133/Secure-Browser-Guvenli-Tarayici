# ============================================================
# Secure Browser (Clean Fixed Version)
# Author: MiracTR
# Disclaimer: This is a prototype of a project. Author is not responsable with errors and security problems. Look at codes first.
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
API_TOKEN = secrets.token_hex(32)

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
# PROXY
# =======================
BLOCKED = ["ads", "analytics", "doubleclick", "facebook"]

class SecureProxy:
    def request(self, flow: http.HTTPFlow):
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
# SECURITY API
# =======================
def auth(token):
    return token == API_TOKEN

def toggle_dark(token):
    if not auth(token):
        return

    state["dark"] = not state["dark"]

    css = "html{filter:invert(1) hue-rotate(180deg)}" if state["dark"] else ""

    window.evaluate_js(f"""
document.getElementById('dm')?.remove();
document.head.insertAdjacentHTML('beforeend','<style id=dm>{css}</style>');
""")

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

    js = f"""
const TOKEN = "{API_TOKEN}";

document.addEventListener('keydown', function(e) {{
    if(e.ctrlKey && e.shiftKey && e.key === 'X') panic(TOKEN);
}});

document.head.insertAdjacentHTML('beforeend', `
<style>
#ui{{
position:fixed;
top:10px;
right:10px;
z-index:9999;
display:flex;
gap:6px;
background:#000a;
padding:8px;
border-radius:10px
}}

button,select{{
border:none;
border-radius:6px;
padding:4px 8px
}}
</style>

<div id="ui">
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
"""

    window.evaluate_js(js)

webview.start(on_load)
