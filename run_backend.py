"""Run the local Flask backend and serve the compiled frontend."""

from __future__ import annotations

import os
import logging
import sqlite3
import sys
import threading
from pathlib import Path

from flask import Flask, abort, jsonify, send_file
from wsgiref.simple_server import make_server


def application_root() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


def load_django_application():
    django_root = application_root() / "Hotel"
    if str(django_root) not in sys.path:
        sys.path.insert(0, str(django_root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    os.environ["DESKTOP_MODE"] = "1"
    log_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "HotelSistema"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=log_dir / "backend.log", level=logging.ERROR)

    import django
    from django.core.management import call_command

    django.setup()
    call_command("migrate", interactive=False, verbosity=0)

    from config.wsgi import application

    return application


def user_data_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    data_dir = Path(local_app_data) / "HotelSistema" if local_app_data else Path.home() / ".hotel_sistema"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def initialize_database(database_path: Path) -> None:
    """Create the desktop database and its initial schema if needed."""
    with sqlite3.connect(database_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS app_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            INSERT OR IGNORE INTO app_metadata (key, value)
            VALUES ('schema_version', '1');
            """
        )


def find_frontend_build() -> Path:
    root = application_root()
    candidates = (root / "frontend_build", root / "frontend" / "build")
    for candidate in candidates:
        if (candidate / "index.html").is_file():
            return candidate
    # TODO: Confirm the production frontend output directory if it is not one of these paths.
    return candidates[0]


def create_app() -> Flask:
    frontend_dir = find_frontend_build()
    index_file = frontend_dir / "index.html"
    app = Flask(__name__, static_folder=None)

    database_path = user_data_dir() / "hotel.db"
    initialize_database(database_path)

    # TODO: Replace this Flask entrypoint with the existing Django/ORM entrypoint when its
    # desktop-compatible SQLite configuration and API integration are confirmed.
    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/", defaults={"requested_path": ""})
    @app.route("/<path:requested_path>")
    def frontend(requested_path: str):
        if not index_file.is_file():
            abort(500, description=f"No se encontró el frontend en {index_file}")

        requested_file = (frontend_dir / requested_path).resolve() if requested_path else index_file
        if requested_path and frontend_dir.resolve() not in requested_file.parents:
            abort(404)
        if requested_path and requested_file.is_file():
            return send_file(requested_file)
        return send_file(index_file)

    return app


class DesktopApplication:
    """Serve the frontend with Flask and the Django API in the same process."""

    def __init__(self, frontend_app: Flask, django_app):
        self.frontend_app = frontend_app
        self.django_app = django_app

    def __call__(self, environ, start_response):
        if environ.get("PATH_INFO", "").startswith("/api/"):
            return self.django_app(environ, start_response)
        return self.frontend_app(environ, start_response)


def start_backend(port: int) -> threading.Thread:
    application = DesktopApplication(create_app(), load_django_application())

    def serve():
        server = make_server("127.0.0.1", port, application)
        server.serve_forever()

    server_thread = threading.Thread(target=serve, daemon=True)
    server_thread.start()
    return server_thread


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python run_backend.py PORT")
    try:
        port = int(sys.argv[1])
    except ValueError as exc:
        raise SystemExit("PORT debe ser un número entero") from exc

    os.environ["DESKTOP_MODE"] = "1"
    start_backend(port)
    threading.Event().wait()


if __name__ == "__main__":
    main()