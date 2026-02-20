from __future__ import annotations

import socket
import subprocess
import sys
import webbrowser
from pathlib import Path

import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem as Item

from app.settings import get_settings

settings = get_settings()
PORT = settings.port
URL = f"http://localhost:{PORT}"
ROOT = Path(__file__).resolve().parents[1]
SERVER_ENTRY = ROOT / "run_server.py"

server_process: subprocess.Popen | None = None


def is_port_busy(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def notify(text: str) -> None:
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(0, text, "KitoDan", 0x40)
    except Exception:
        print(text)


def start_server(icon=None, item=None):
    global server_process
    if server_process and server_process.poll() is None:
        notify(f"KitoDan is already running on {URL}")
        return
    if is_port_busy(PORT):
        notify(f"Port {PORT} is already in use. Change PORT in %APPDATA%\\KitoDan\\server.env")
        return

    creationflags = 0x08000000  # CREATE_NO_WINDOW
    server_process = subprocess.Popen(
        [sys.executable, str(SERVER_ENTRY)],
        cwd=str(ROOT),
        creationflags=creationflags,
    )


def stop_server(icon=None, item=None):
    global server_process
    if server_process and server_process.poll() is None:
        server_process.terminate()
        server_process.wait(timeout=5)
        server_process = None


def open_kito(icon=None, item=None):
    webbrowser.open(URL)


def status(icon=None, item=None):
    running = is_port_busy(PORT)
    notify(f"Status: {'Running' if running else 'Stopped'}\nPort: {PORT}")


def on_exit(icon, item):
    stop_server()
    icon.stop()


def create_icon() -> Image.Image:
    img = Image.new("RGB", (64, 64), color=(22, 22, 35))
    draw = ImageDraw.Draw(img)
    draw.ellipse((8, 8, 56, 56), fill=(107, 70, 255))
    draw.text((22, 21), "K", fill="white")
    return img


def run() -> None:
    start_server()
    icon = pystray.Icon(
        "KitoDan",
        create_icon(),
        "KitoDan",
        menu=pystray.Menu(
            Item("Open KitoDan", open_kito),
            Item("Start", start_server),
            Item("Stop", stop_server),
            Item("Status", status),
            Item("Exit", on_exit),
        ),
    )
    icon.run()


if __name__ == "__main__":
    run()
