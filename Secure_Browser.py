# ============================================================
# Secure Browser v2 (Rebuilt Clean Architecture)
# ============================================================

import os
import sys
import json
import time
import asyncio
import secrets
import threading
import subprocess
import datetime

# ============================================================
# AUTO INSTALL
# ============================================================

def ensure(pkg, imp=None):
    try:
        __import__(imp or pkg)
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pkg]
        )

ensure("pywebview", "webview")
ensure("mitmproxy")

# ============================================================
# IMPORTS
# ============================================================

import webview
from mitmproxy.tools.dump import DumpMaster
from mitmproxy import options, http

# ============================================================
# CONSTANTS
# ============================================================

SETTINGS_FILE = "settings.json"

SEARCH_ENGINES = {
    "DuckDuckGo": "https://duckduckgo.com",
    "Google": "https://www.google.com",
    "Startpage": "https://www.startpage.com"
}

BLOCKED_DOMAINS = {
    "doubleclick.net",
    "google-analytics.com",
    "facebook.com",
    "facebook.net",
    "ads-twitter.com"
}

TRACKING_COOKIES = {
    "_ga",
    "_gid",
    "_fbp"
}

# ============================================================
# PROXY ADDON
# ============================================================

class SecureProxy:

    def __init__(self, browser):
        self.browser = browser

    def request(self, flow: http.HTTPFlow):

        host = flow.request.host.lower()

        # --------------------------------
        # BLOCK TRACKERS
        # --------------------------------

        if (
            host in BLOCKED_DOMAINS
            or any(host.endswith("." + d) for d in BLOCKED_DOMAINS)
        ):
            flow.response = http.Response.make(
                403,
                b"Blocked by Secure Browser"
            )

            self.browser.log(f"Blocked: {host}")
            return

        # --------------------------------
        # REMOVE TRACKING COOKIES
        # --------------------------------

        cookies = flow.request.cookies.copy()

        for c in TRACKING_COOKIES:
            cookies.pop(c, None)

        flow.request.cookies = cookies

        # --------------------------------
        # HARDEN HEADERS
        # --------------------------------

        flow.request.headers["User-Agent"] = (
            "Mozilla/5.0 SecureBrowser/2.0"
        )

        flow.request.headers.pop("Referer", None)

# ============================================================
# MAIN CLASS
# ============================================================

class SecureBrowser:

    def __init__(self):

        # --------------------------------
        # STATE
        # --------------------------------

        self.state = {
            "dark": False,
            "proxy": True,
            "engine": "DuckDuckGo"
        }

        self.logs = []

        self.api_token = secrets.token_hex(32)

        self.window = None
        self.proxy_master = None

        self.load_settings()

    # ========================================================
    # SETTINGS
    # ========================================================

    def load_settings(self):

        if not os.path.exists(SETTINGS_FILE):
            return

        try:
            with open(
                SETTINGS_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

                if isinstance(data, dict):
                    self.state.update(data)

        except Exception as e:
            print("Settings load error:", e)

    def save_settings(self):

        try:
            with open(
                SETTINGS_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    self.state,
                    f,
                    indent=2
                )

        except Exception as e:
            print("Settings save error:", e)

    # ========================================================
    # LOGGER
    # ========================================================

    def log(self, message):

        ts = datetime.datetime.now().strftime("%H:%M:%S")

        line = f"[{ts}] {message}"

        self.logs.append(line)

        print(line)

    # ========================================================
    # AUTH
    # ========================================================

    def auth(self, token):
        return token == self.api_token

    # ========================================================
    # PROXY
    # ========================================================

    async def proxy_loop(self):

        opts = options.Options(
            listen_host="127.0.0.1",
            listen_port=8080
        )

        self.proxy_master = DumpMaster(
            opts,
            with_termlog=False,
            with_dumper=False
        )

        self.proxy_master.addons.add(
            SecureProxy(self)
        )

        self.log("Proxy started")

        await self.proxy_master.run()

    def start_proxy(self):

        def runner():
            asyncio.run(self.proxy_loop())

        threading.Thread(
            target=runner,
            daemon=True
        ).start()

    def apply_proxy(self):

        if self.state["proxy"]:

            os.environ["HTTP_PROXY"] = (
                "http://127.0.0.1:8080"
            )

            os.environ["HTTPS_PROXY"] = (
                "http://127.0.0.1:8080"
            )

            self.log("Proxy enabled")

        else:

            os.environ.pop("HTTP_PROXY", None)
            os.environ.pop("HTTPS_PROXY", None)

            self.log("Proxy disabled")

    # ========================================================
    # EXPOSED API
    # ========================================================

    def toggle_dark(self, token):

        if not self.auth(token):
            return

        self.state["dark"] = not self.state["dark"]

        css = ""

        if self.state["dark"]:
            css = """
html {
    background:#111 !important;
    color-scheme:dark !important;
}
"""

        import json as _json

        js = f"""
document.getElementById('secure-darkmode')?.remove();

document.head.insertAdjacentHTML(
    'beforeend',
    {_json.dumps(f"<style id='secure-darkmode'>{css}</style>")}
);
"""

        if self.window:
            self.window.evaluate_js(js)

        self.save_settings()

    def change_engine(self, token, name):

        if not self.auth(token):
            return

        if name not in SEARCH_ENGINES:
            return

        self.state["engine"] = name

        self.save_settings()

        if self.window:
            self.window.load_url(
                SEARCH_ENGINES[name]
            )

        self.log(f"Engine changed: {name}")

    def toggle_proxy(self, token):

        if not self.auth(token):
            return

        self.state["proxy"] = not self.state["proxy"]

        self.apply_proxy()

        self.save_settings()

    def show_logs(self, token):

        if not self.auth(token):
            return

        safe = "\n".join(
            self.logs[-100:]
        ).replace("`", "'")

        js = f"alert(`{safe}`)"

        if self.window:
            self.window.evaluate_js(js)

    def panic(self, token):

        if not self.auth(token):
            return

        self.log("PANIC EXIT")

        self.save_settings()

        try:
            if self.window:
                self.window.destroy()

        finally:
            sys.exit(0)

    # ========================================================
    # JS UI
    # ========================================================

    def inject_ui(self):

        time.sleep(0.5)

        js = f"""
const TOKEN = "{self.api_token}";

document.addEventListener('keydown', e => {{

    if(
        e.ctrlKey &&
        e.shiftKey &&
        e.key === 'X'
    ) {{
        pywebview.api.panic(TOKEN);
    }}

}});

document.head.insertAdjacentHTML('beforeend', `
<style>

#secure-ui {{
    position: fixed;
    top: 12px;
    right: 12px;
    z-index: 999999;

    display: flex;
    gap: 8px;

    background: rgba(0,0,0,0.7);

    padding: 10px;

    border-radius: 12px;

    backdrop-filter: blur(10px);
}}

#secure-ui button,
#secure-ui select {{

    border: none;

    border-radius: 8px;

    padding: 6px 10px;

    font-size: 14px;

    cursor: pointer;
}}

#secure-ui button:hover {{
    opacity: 0.9;
}}

</style>

<div id="secure-ui">

<select onchange="pywebview.api.change_engine(TOKEN,this.value)">
    <option>DuckDuckGo</option>
    <option>Google</option>
    <option>Startpage</option>
</select>

<button onclick="pywebview.api.toggle_dark(TOKEN)">
🌙
</button>

<button onclick="pywebview.api.toggle_proxy(TOKEN)">
🛡️
</button>

<button onclick="pywebview.api.show_logs(TOKEN)">
📜
</button>

<button
style="background:red;color:white"
onclick="pywebview.api.panic(TOKEN)"
>
PANIC
</button>

</div>
`);
"""

        if self.window:
            self.window.evaluate_js(js)

    # ========================================================
    # START
    # ========================================================

    def start(self):

        # --------------------------------
        # START PROXY
        # --------------------------------

        self.start_proxy()

        # --------------------------------
        # APPLY PROXY
        # --------------------------------

        self.apply_proxy()

        # --------------------------------
        # CREATE WINDOW
        # --------------------------------

        self.window = webview.create_window(
            title="Secure Browser v2",
            url=SEARCH_ENGINES[self.state["engine"]],
            width=1200,
            height=800,
            private_mode=True
        )

        # --------------------------------
        # EXPOSE PY API
        # --------------------------------

        self.window.expose(
            self.toggle_dark,
            self.change_engine,
            self.toggle_proxy,
            self.show_logs,
            self.panic
        )

        # --------------------------------
        # START WEBVIEW
        # --------------------------------

        webview.start(
            self.inject_ui,
            debug=False
        )

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    browser = SecureBrowser()

    browser.start()
