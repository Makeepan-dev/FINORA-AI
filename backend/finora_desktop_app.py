import argparse
import ctypes
import json
import logging
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

# 1. Force desktop mode BEFORE importing FINORA backend modules
os.environ.setdefault("FINORA_DESKTOP_MODE", "1")


def _configure_stdio_and_logging(data_dir: Path) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    log_path = data_dir / "backend.log"
    log_file = open(log_path, "a", encoding="utf-8", buffering=1)
    if sys.stdout is None:
        sys.stdout = log_file
    if sys.stderr is None:
        sys.stderr = log_file
    logging.basicConfig(
        filename=str(log_path),
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    return log_path


def _resolve_initial_data_dir() -> Path:
    custom = os.environ.get("FINORA_DATA_DIR")
    if custom:
        return Path(custom)
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "FINORA"
    return Path.home() / "AppData" / "Roaming" / "FINORA"


_DATA_DIR = _resolve_initial_data_dir()
_LOG_PATH = _configure_stdio_and_logging(_DATA_DIR)

# Explicit imports for PyInstaller bundling
import sqlalchemy.dialects.sqlite  # noqa: F401, E402
import uvicorn  # noqa: E402
import uvicorn.lifespan.on  # noqa: F401, E402
import uvicorn.logging  # noqa: F401, E402
import uvicorn.loops.auto  # noqa: F401, E402
import uvicorn.protocols.http.auto  # noqa: F401, E402
import uvicorn.protocols.websockets.auto  # noqa: F401, E402

from app.core.config import get_desktop_data_dir  # noqa: E402
import app.models.db_models  # noqa: F401, E402
from app.main import app as fastapi_app  # noqa: E402


_ENV_TEMPLATE = """# FINORA Desktop User Configuration (%APPDATA%\\FINORA\\.env)
# Copy this file to .env in this folder to configure optional live integrations.
# Never commit real credentials to version control.

AI_PRIMARY_PROVIDER=gemini
AI_MODEL=gemini-flash-lite-latest
ALLOW_PAID_MODELS=False
MAX_API_SPEND_USD=0.0
GEMINI_API_KEY=

PAYPAL_MODE=sandbox
PAYPAL_API_BASE=https://api.sandbox.paypal.com
PAYPAL_CLIENT_ID=
PAYPAL_CLIENT_SECRET=
PAYPAL_WEBHOOK_ID=
PAYPAL_REQUIRE_WEBHOOK_VERIFICATION=True
"""


def _ensure_appdata_env_template() -> None:
    data_dir = get_desktop_data_dir()
    example_file = data_dir / ".env.example"
    if not example_file.exists():
        try:
            example_file.write_text(_ENV_TEMPLATE, encoding="utf-8")
        except OSError:
            pass


def _acquire_single_instance_mutex(mutex_name: str = "Local\\FINORA_DESKTOP_SINGLE_INSTANCE_V1"):
    if sys.platform != "win32":
        return object()
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32
    handle = kernel32.CreateMutexW(None, False, mutex_name)
    last_error = kernel32.GetLastError()
    if last_error == 183:  # ERROR_ALREADY_EXISTS
        hwnd = user32.FindWindowW(None, "FINORA — AI Financial Intelligence Assistant")
        if hwnd:
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            user32.SetForegroundWindow(hwnd)
        return None
    return handle


def _show_error_dialog(title: str, message: str) -> None:
    logging.error("%s: %s", title, message)
    if sys.platform == "win32" and os.environ.get("FINORA_SUPPRESS_DIALOGS") != "1":
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x00000010)


def _find_available_port(preferred: int = 8000) -> int:
    for candidate in range(preferred, preferred + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", candidate))
                return candidate
            except OSError:
                continue
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_health(port: int, timeout_sec: float = 25.0) -> dict | None:
    deadline = time.time() + timeout_sec
    url = f"http://127.0.0.1:{port}/health"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.5) as resp:
                if resp.status == 200:
                    payload = json.loads(resp.read().decode("utf-8"))
                    if payload.get("status") == "healthy":
                        return payload
        except (urllib.error.URLError, TimeoutError, ValueError, OSError):
            pass
        time.sleep(0.25)
    return None


def _launch_ui_window(url: str, data_dir: Path) -> None:
    title = "FINORA — AI Financial Intelligence Assistant"
    try:
        import webview  # type: ignore

        storage_dir = data_dir / "webview_storage"
        storage_dir.mkdir(parents=True, exist_ok=True)
        webview.create_window(
            title,
            url,
            width=1400,
            height=900,
            min_size=(1024, 700),
            background_color="#020617",
            text_select=True,
        )
        webview.start(private_mode=False, storage_path=str(storage_dir))
        return
    except Exception as exc:
        logging.warning("pywebview fallback triggered: %s", exc)

    # Fallback: launch dedicated Edge App Window and wait for it to close
    edge_candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    edge_exe = next((p for p in edge_candidates if os.path.isfile(p)), None)
    if edge_exe:
        profile_dir = data_dir / "edge_app_profile"
        profile_dir.mkdir(parents=True, exist_ok=True)
        proc = subprocess.Popen(
            [
                edge_exe,
                f"--app={url}",
                f"--user-data-dir={profile_dir}",
                "--window-size=1400,900",
                "--no-first-run",
                "--no-default-browser-check",
            ]
        )
        proc.wait()
    else:
        import webbrowser

        webbrowser.open(url)


def main() -> int:
    parser = argparse.ArgumentParser(description="FINORA Windows Desktop Application")
    parser.add_argument("--host", default=os.environ.get("FINORA_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("FINORA_PORT", "0")))
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run backend server only without opening GUI window (for service/runtime testing)",
    )
    args = parser.parse_args()

    mutex_handle = _acquire_single_instance_mutex()
    if mutex_handle is None and not args.headless:
        logging.info("Another FINORA desktop instance is already running; focusing existing window.")
        return 0

    _ensure_appdata_env_template()
    data_dir = get_desktop_data_dir()

    port = args.port if args.port > 0 else _find_available_port(8000)
    os.environ["FINORA_PORT"] = str(port)

    runtime_info_file = data_dir / "runtime.json"
    config = uvicorn.Config(
        fastapi_app,
        host=args.host,
        port=port,
        interface="asgi3",
        log_config=None,
        access_log=False,
    )
    server = uvicorn.Server(config)

    server_thread = threading.Thread(target=server.run, name="FinoraFastAPIServer", daemon=True)
    server_thread.start()

    health = _wait_for_health(port, timeout_sec=30.0)
    if not health:
        server.should_exit = True
        _show_error_dialog(
            "FINORA Startup Error",
            f"FINORA could not start its local financial intelligence engine on port {port}.\n\n"
            f"Diagnostic log: {_LOG_PATH}",
        )
        return 1

    try:
        runtime_info_file.write_text(
            json.dumps(
                {
                    "pid": os.getpid(),
                    "host": args.host,
                    "port": port,
                    "url": f"http://{args.host}:{port}/",
                    "data_dir": str(data_dir),
                    "database_file": str(data_dir / "finora.db"),
                    "started_at": time.time(),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    except OSError:
        pass

    logging.info("FINORA Desktop ready at http://%s:%d/ (PID=%d)", args.host, port, os.getpid())

    try:
        if args.headless:
            while server_thread.is_alive() and not server.should_exit:
                time.sleep(0.3)
        else:
            _launch_ui_window(f"http://{args.host}:{port}/", data_dir)
    except KeyboardInterrupt:
        pass
    finally:
        logging.info("Shutting down FINORA Desktop backend (PID=%d)...", os.getpid())
        server.should_exit = True
        server_thread.join(timeout=5.0)
        try:
            if runtime_info_file.exists():
                runtime_info_file.unlink()
        except OSError:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
