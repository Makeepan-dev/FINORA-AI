import hashlib
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "installer_output"
REPO = "Makeepan-dev/FINORA-AI"
TAG = "v1.0.0"


def get_github_token() -> str:
    proc = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True,
        text=True,
        check=True,
    )
    for line in proc.stdout.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("No GitHub credential token returned by git credential fill")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def github_api(method: str, url: str, token: str, payload: dict | bytes | None = None, content_type: str = "application/json") -> tuple[int, dict]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "FINORA-Release-Publisher",
    }
    data = None
    if isinstance(payload, dict):
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = content_type
    elif isinstance(payload, bytes):
        data = payload
        headers["Content-Type"] = content_type

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        try:
            err = json.loads(exc.read().decode("utf-8"))
        except Exception:
            err = {"message": str(exc)}
        return exc.code, err


def main() -> int:
    setup_exe = OUTPUT_DIR / "FINORA Setup.exe"
    portable_exe = OUTPUT_DIR / "FINORA Portable.exe"
    if not setup_exe.is_file():
        print("Missing FINORA Setup.exe", file=sys.stderr)
        return 1

    setup_sha = sha256_of(setup_exe)
    portable_sha = sha256_of(portable_exe) if portable_exe.is_file() else "N/A"

    token = get_github_token()

    release_body = (
        "## FINORA v1.0.0 — AI-Powered Personal Financial Intelligence & Money-Saving Assistant\n\n"
        "Standalone Windows Desktop Release for the **PayPal AI Hackathon 2026**.\n\n"
        "### Included Windows Deliverables\n"
        f"- **`FINORA Setup.exe`** ({setup_exe.stat().st_size:,} bytes) — Windows GUI & Silent Installer (`%LOCALAPPDATA%\\Programs\\FINORA`, Start Menu & Desktop shortcuts, Windows Uninstaller registration)\n"
        f"  - **SHA-256:** `{setup_sha}`\n"
        f"- **`FINORA Portable.exe`** ({portable_exe.stat().st_size:,} bytes) — Single-file portable Windows executable\n"
        f"  - **SHA-256:** `{portable_sha}`\n\n"
        "### Runtime & Data Architecture\n"
        "- Automatically launches the bundled FastAPI + SQLite engine on `127.0.0.1` and opens the FINORA desktop interface.\n"
        "- Stores persistent user data in `%APPDATA%\\FINORA\\finora.db` (preserved across upgrades and standard uninstalls).\n"
        "- Optional Gemini API or PayPal Sandbox keys can be configured in `%APPDATA%\\FINORA\\.env` (see `%APPDATA%\\FINORA\\.env.example`).\n"
    )

    # Check if release v1.0.0 already exists
    code, rel = github_api("GET", f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}", token)
    if code == 404:
        code, rel = github_api(
            "POST",
            f"https://api.github.com/repos/{REPO}/releases",
            token,
            {
                "tag_name": TAG,
                "target_commitish": "main",
                "name": "FINORA v1.0.0 — Windows Desktop Installer & Portable Release",
                "body": release_body,
                "draft": False,
                "prerelease": False,
            },
        )
    if code not in (200, 201):
        print(f"Release creation returned HTTP {code}: {rel.get('message')}")
        return 2

    release_id = rel["id"]
    html_url = rel["html_url"]
    print(f"Release ready: {html_url} (id={release_id})")

    # Delete existing assets with same name if re-running
    for asset in rel.get("assets", []):
        if asset.get("name") in ("FINORA Setup.exe", "FINORA Portable.exe", "FINORA-Setup.exe", "FINORA-Portable.exe"):
            github_api("DELETE", f"https://api.github.com/repos/{REPO}/releases/assets/{asset['id']}", token)

    for file_path in (setup_exe, portable_exe):
        if not file_path.is_file():
            continue
        encoded_name = urllib.parse.quote(file_path.name)
        upload_url = f"https://uploads.github.com/repos/{REPO}/releases/{release_id}/assets?name={encoded_name}"
        print(f"Uploading {file_path.name} ({file_path.stat().st_size:,} bytes)...")
        up_code, up_res = github_api(
            "POST",
            upload_url,
            token,
            payload=file_path.read_bytes(),
            content_type="application/vnd.microsoft.portable-executable",
        )
        if up_code not in (200, 201):
            print(f"Failed uploading {file_path.name}: HTTP {up_code} {up_res.get('message')}")
            return 3
        print(f"Uploaded asset: {up_res.get('name')} -> {up_res.get('browser_download_url')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
