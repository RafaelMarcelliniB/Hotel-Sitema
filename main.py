"""Launch the local web application inside a native desktop window."""

from __future__ import annotations

import socket
import sys
import threading
import time
import urllib.error
import urllib.request
import base64
from pathlib import Path


def find_free_port() -> int:
    """Ask Windows for an available local TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_for_server(url: str, timeout: float = 30) -> None:
    """Wait until the backend responds or fail."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status < 500:
                    return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.2)
    raise TimeoutError(f"El backend no respondió a tiempo en {url}.")


def main() -> None:
    from run_backend import load_django_application, start_backend

    if "--migrate" in sys.argv:
        load_django_application()
        return

    import webview

    class DesktopApi:
        def save_download(self, filename: str, content_base64: str) -> str:
            downloads_dir = Path.home() / "Downloads" / "Hotel Venecia"
            downloads_dir.mkdir(parents=True, exist_ok=True)
            safe_name = Path(filename).name
            output_path = downloads_dir / safe_name
            output_path.write_bytes(base64.b64decode(content_base64))
            return str(output_path)

    port = find_free_port()
    url = f"http://127.0.0.1:{port}"
    start_backend(port)

    try:
        wait_for_server(f"{url}/health")
        webview.create_window(
            "Hotel Venecia",
            url,
            width=1280,
            height=800,
            min_size=(960, 640),
            js_api=DesktopApi(),
        )
        webview.start()
    finally:
        # El backend vive en el mismo proceso; al cerrar la ventana se finaliza la app.
        pass


if __name__ == "__main__":
    main()