"""
CogniPulse - Main Entrypoint & Launcher
"""

import sys
import webbrowser
import threading
import time
from server import start_server

def open_browser_delayed(url: str, delay: float = 1.0):
    time.sleep(delay)
    print(f"[CogniPulse] Launching CogniPulse Studio in your browser: {url}")
    try:
        webbrowser.open(url)
    except Exception:
        pass

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    studio_url = f"http://127.0.0.1:{port}"
    
    # Auto launch browser in background
    threading.Thread(target=open_browser_delayed, args=(studio_url,), daemon=True).start()
    
    # Start web server
    start_server(port)
