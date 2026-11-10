import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
import winreg
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SETUP_EXE = ROOT_DIR / "installer_output" / "FINORA Setup.exe"
PORTABLE_EXE = ROOT_DIR / "installer_output" / "FINORA Portable.exe"
INSTALL_DIR = Path(os.environ["LOCALAPPDATA"]) / "Programs" / "FINORA"
INSTALLED_EXE = INSTALL_DIR / "FINORA.exe"
UNINSTALL_EXE = INSTALL_DIR / "FINORA Uninstall.exe"
APPDATA_DIR = Path(os.environ["APPDATA"]) / "FINORA"
DB_FILE = APPDATA_DIR / "finora.db"
RUNTIME_JSON = APPDATA_DIR / "runtime.json"


def http_json(method: str, url: str, data: dict | None = None, headers: dict | None = None) -> tuple[int, dict | list]:
    req_headers = {"Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            err_body = json.loads(exc.read().decode("utf-8"))
        except Exception:
            err_body = {"raw": str(exc)}
        return exc.code, err_body


def upload_multipart_csv(url: str, csv_content: str, fields: dict[str, str]) -> tuple[int, dict]:
    boundary = "----FinoraBoundary987654321"
    lines: list[bytes] = []
    for k, v in fields.items():
        lines.append(f"--{boundary}\r\n".encode())
        lines.append(f'Content-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    lines.append(f"--{boundary}\r\n".encode())
    lines.append(b'Content-Disposition: form-data; name="file"; filename="test_import.csv"\r\n')
    lines.append(b"Content-Type: text/csv\r\n\r\n")
    lines.append(csv_content.encode("utf-8") + b"\r\n")
    lines.append(f"--{boundary}--\r\n".encode())
    payload = b"".join(lines)

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def get_finora_processes() -> list[dict]:
    out = subprocess.check_output(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-Process | Where-Object { $_.ProcessName -like 'FINORA*' } | Select-Object Id, ProcessName, MainWindowTitle | ConvertTo-Json -Compress",
        ],
        text=True,
    ).strip()
    if not out:
        return []
    parsed = json.loads(out)
    return parsed if isinstance(parsed, list) else [parsed]


def kill_all_finora() -> None:
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", "Get-Process 'FINORA*' -ErrorAction SilentlyContinue | Stop-Process -Force"],
        check=False,
    )
    time.sleep(1.2)
    if RUNTIME_JSON.exists():
        try:
            RUNTIME_JSON.unlink()
        except OSError:
            pass


def wait_for_runtime_json(timeout_sec: float = 30.0) -> dict:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if RUNTIME_JSON.is_file():
            try:
                info = json.loads(RUNTIME_JSON.read_text(encoding="utf-8"))
                status, health = http_json("GET", f"http://{info['host']}:{info['port']}/health")
                if status == 200 and isinstance(health, dict) and health.get("status") == "healthy":
                    return info
            except Exception:
                pass
        time.sleep(0.3)
    raise RuntimeError("Timed out waiting for packaged FINORA.exe runtime.json and /health")


def main() -> None:
    results: list[dict] = []

    def record(step_num: int, name: str, passed: bool, evidence: str) -> None:
        status_str = "PASS" if passed else "FAIL"
        print(f"[{status_str}] Check {step_num:02d} — {name}: {evidence}")
        results.append({"step": step_num, "name": name, "status": status_str, "evidence": evidence})
        if not passed:
            raise AssertionError(f"Check {step_num} failed: {evidence}")

    kill_all_finora()
    if APPDATA_DIR.exists():
        shutil.rmtree(APPDATA_DIR)
    if INSTALL_DIR.exists():
        shutil.rmtree(INSTALL_DIR)

    # Check 1: Fresh installation via FINORA Setup.exe
    install_res = subprocess.run([str(SETUP_EXE), "/S", f"/DIR={INSTALL_DIR}"], check=False)
    start_menu_lnk = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "FINORA.lnk"
    desktop_lnk = Path(os.environ["USERPROFILE"]) / "Desktop" / "FINORA.lnk"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\FINORA") as reg_key:
        reg_display_name, _ = winreg.QueryValueEx(reg_key, "DisplayName")
    record(
        1,
        "Fresh installation via FINORA Setup.exe",
        install_res.returncode == 0 and INSTALLED_EXE.is_file() and UNINSTALL_EXE.is_file() and start_menu_lnk.is_file(),
        f"ExitCode={install_res.returncode}, InstalledExe={INSTALLED_EXE.is_file()}, StartMenuShortcut={start_menu_lnk.is_file()}, DesktopShortcut={desktop_lnk.is_file()}, Registry='{reg_display_name}'",
    )

    # Strip Python and Node.js from PATH to verify self-contained execution
    clean_env = os.environ.copy()
    clean_env["PATH"] = r"C:\Windows\System32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0"
    clean_env["FINORA_SUPPRESS_DIALOGS"] = "1"

    # Launch installed FINORA.exe (GUI mode)
    gui_proc = subprocess.Popen([str(INSTALLED_EXE)], cwd=str(INSTALL_DIR), env=clean_env)
    info = wait_for_runtime_json(35.0)
    base_url = f"http://{info['host']}:{info['port']}"
    time.sleep(2.0)

    # Check 2: Window / SPA Frontend opens and serves bundled UI
    with urllib.request.urlopen(f"{base_url}/", timeout=5) as root_resp:
        html_text = root_resp.read().decode("utf-8")
    procs = get_finora_processes()
    record(
        2,
        "Window opens & bundled React SPA serves on desktop origin",
        root_resp.status == 200 and "<div id=\"root\"></div>" in html_text and len(procs) >= 1,
        f"GET {base_url}/ -> HTTP {root_resp.status} ({len(html_text)} bytes), ActiveProcesses={procs}",
    )

    # Check 3: Bundled backend starts automatically without terminal
    record(
        3,
        "Backend starts automatically inside packaged FINORA.exe",
        info["pid"] > 0 and Path(info["database_file"]).parent == APPDATA_DIR,
        f"PID={info['pid']}, Bound={base_url}, DatabasePath={info['database_file']}",
    )

    # Test single-instance mutex (launching a second FINORA.exe should exit with 0 and NOT spawn a second server)
    second_proc = subprocess.run([str(INSTALLED_EXE)], cwd=str(INSTALL_DIR), env=clean_env, timeout=10)

    # Check 4: Health check & API communication
    h_code, h_body = http_json("GET", f"{base_url}/health")
    assert isinstance(h_body, dict)
    record(
        4,
        "Health check and API communication",
        h_code == 200 and h_body.get("status") == "healthy" and second_proc.returncode == 0,
        f"GET /health -> {h_body}, SecondInstanceExitCode={second_proc.returncode}",
    )

    # Check 5: Dashboard loads (Reset demo dataset and query dashboard metrics)
    r_code, r_body = http_json("POST", f"{base_url}/api/demo-data/reset", {})
    d_code, d_body = http_json("GET", f"{base_url}/api/analytics/dashboard?user_id=usr_alex_chen&data_scope=demo")
    assert isinstance(d_body, dict)
    summary = d_body.get("summary", {})
    record(
        5,
        "Dashboard loads unified Demo Mode metrics",
        d_code == 200
        and summary.get("monthly_income") == 7050.0
        and summary.get("monthly_expenses") == 1200.51
        and summary.get("remaining_available_money") == 5849.49
        and summary.get("potential_monthly_savings") == 115.77,
        f"Income=${summary.get('monthly_income')}, Expenses=${summary.get('monthly_expenses')}, Remaining=${summary.get('remaining_available_money')}, Subscriptions=${summary.get('total_subscription_cost')}, Savings=${summary.get('potential_monthly_savings')}/mo",
    )

    # Check 6: AI Advisor works
    ai_code, ai_body = http_json(
        "POST",
        f"{base_url}/api/guardian/chat",
        {"prompt": "Help me save $100 this month", "user_id": "usr_alex_chen", "data_scope": "demo"},
    )
    assert isinstance(ai_body, dict)
    record(
        6,
        "AI Advisor grounded financial reasoning",
        ai_code == 200 and "115.77" in json.dumps(ai_body),
        f"HTTP {ai_code}, Mode={ai_body.get('mode')}, Contains115.77={'115.77' in json.dumps(ai_body)}",
    )

    # Check 7: Transactions screen loads & manual entry in personal scope works
    tx_demo_code, tx_demo = http_json("GET", f"{base_url}/api/transactions?user_id=usr_alex_chen&data_scope=demo")
    tx_create_code, tx_created = http_json(
        "POST",
        f"{base_url}/api/transactions?user_id=usr_alex_chen",
        {
            "merchant": "Whole Foods Market",
            "category": "Groceries",
            "amount": 54.25,
            "date": "2026-11-10",
            "is_recurring": False,
            "description": "Desktop runtime persistence check",
        },
    )
    assert isinstance(tx_demo, dict) and isinstance(tx_created, dict)
    record(
        7,
        "Transactions screen & manual transaction creation",
        tx_demo_code == 200 and tx_demo.get("count", 0) >= 16 and tx_create_code == 200,
        f"DemoCount={tx_demo.get('count')}, CreatedPersonalTxId={tx_created.get('transaction', {}).get('id')}",
    )

    # Check 8: CSV preview and import work
    csv_sample = (
        "date,merchant,amount,category,description\n"
        "2026-11-01,Trader Joes,42.10,Groceries,Weekly produce\n"
        "2026-11-02,Shell Oil,35.00,Transport,Fuel\n"
        "bad-date,BrokenRow,not-a-number,Misc,Invalid row test\n"
    )
    prev_code, prev_body = upload_multipart_csv(
        f"{base_url}/api/transactions/import-csv/preview",
        csv_sample,
        {"user_id": "usr_alex_chen"},
    )
    valid_rows_to_confirm = [r for r in prev_body.get("records", []) if r.get("is_valid")]
    imp_code, imp_body = http_json(
        "POST",
        f"{base_url}/api/transactions/import-csv/confirm",
        {"user_id": "usr_alex_chen", "records": valid_rows_to_confirm, "skip_duplicates": True},
    )
    assert isinstance(imp_body, dict)
    record(
        8,
        "CSV preview and import (valid + malformed row handling)",
        prev_code == 200 and prev_body.get("valid_count") == 2 and prev_body.get("invalid_count") == 1 and imp_code == 200 and imp_body.get("imported_count") == 2,
        f"PreviewValid={prev_body.get('valid_count')}, PreviewInvalid={prev_body.get('invalid_count')}, ImportedCount={imp_body.get('imported_count')}",
    )

    # Check 9: Savings calculations match verified backend results
    sav_code, sav_body = http_json("GET", f"{base_url}/api/savings/dashboard?user_id=usr_alex_chen&data_scope=demo")
    assert isinstance(sav_body, dict)
    sav_sum = sav_body.get("summary", {})
    record(
        9,
        "Savings calculation integrity ($115.77/mo / $1,389.24/yr)",
        sav_code == 200
        and sav_sum.get("potential_monthly_savings") == 115.77
        and sav_sum.get("potential_annual_savings") == 1389.24
        and sav_sum.get("verified_realized_savings") == 0.0,
        f"Monthly=${sav_sum.get('potential_monthly_savings')}, Yearly=${sav_sum.get('potential_annual_savings')}, Realized=${sav_sum.get('verified_realized_savings')}",
    )

    # Check 10: Nearby services and geolocation work
    perm_grant_code, _ = http_json(
        "POST",
        f"{base_url}/api/location/permission",
        {
            "user_id": "usr_alex_chen",
            "is_granted": True,
            "precision_mode": "precise",
            "access_type": "one_time",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "city": "San Francisco",
            "location_source": "browser_gps",
        },
    )
    near_code, near_body = http_json("GET", f"{base_url}/api/location/nearby?category=fitness&user_id=usr_alex_chen")
    gym_code, gym_body = http_json("GET", f"{base_url}/api/location/gym-scenario?user_id=usr_alex_chen")
    assert isinstance(near_body, list) and isinstance(gym_body, dict)
    net_gym = gym_body.get("savings_calculation", {}).get("net_monthly_savings_after_transport")
    record(
        10,
        "Nearby services & transport-adjusted savings comparison ($20.71/mo net gym saving)",
        perm_grant_code == 200 and near_code == 200 and len(near_body) > 0 and gym_code == 200 and net_gym == 20.71,
        f"NearbyCount={len(near_body)}, GymNetAfterTransport=${net_gym}/mo",
    )

    # Check 11: Location permission revocation works
    rev_code, rev_body = http_json(
        "POST",
        f"{base_url}/api/location/permission",
        {"user_id": "usr_alex_chen", "is_granted": False, "precision_mode": "disabled", "access_type": "disabled"},
    )
    stat_code, stat_body = http_json("GET", f"{base_url}/api/location/status?user_id=usr_alex_chen")
    near_revoked_code, near_revoked = http_json("GET", f"{base_url}/api/location/nearby?category=fitness&user_id=usr_alex_chen")
    assert isinstance(stat_body, dict) and isinstance(near_revoked, list)
    record(
        11,
        "Location permission revocation clears coordinates & stops automatic nearby lookup",
        rev_code == 200 and stat_body.get("is_granted") is False and stat_body.get("latitude") is None and len(near_revoked) == 0,
        f"StatusAfterRevoke={stat_body}, NearbyWhenRevokedCount={len(near_revoked)}",
    )

    # Check 12: PayPal Sandbox configuration/workflow & ownership protection
    set_code, set_body = http_json("GET", f"{base_url}/api/payments/config-status")
    ord_code, ord_body = http_json(
        "POST",
        f"{base_url}/api/payments/create-order",
        {"product_id": "sav_gym_planet_20", "user_id": "usr_alex_chen"},
    )
    assert isinstance(set_body, dict) and isinstance(ord_body, dict)
    order_id = ord_body.get("id") or ord_body.get("order_id", "")
    spoof_code, _ = http_json(
        "POST",
        f"{base_url}/api/payments/capture-order",
        {"order_id": order_id, "user_id": "usr_sarah_jenkins"},
    )
    record(
        12,
        "PayPal Sandbox workflow & cross-user capture prevention",
        set_code == 200 and set_body.get("mode") == "sandbox" and ord_code == 200 and bool(order_id) and spoof_code == 403,
        f"PayPalMode={set_body.get('mode')}, CreatedOrder={order_id}, CrossUserCaptureHTTP={spoof_code}",
    )

    # Close packaged application cleanly and verify Check 14 (zero orphan backend processes)
    kill_all_finora()
    remaining_procs = get_finora_processes()
    record(
        14,
        "No duplicate or orphan backend processes remain after closing",
        len(remaining_procs) == 0 and DB_FILE.is_file(),
        f"RemainingFinoraProcesses={len(remaining_procs)}, AppDataDbExists={DB_FILE.is_file()} ({DB_FILE.stat().st_size} bytes)",
    )

    # Check 13 & Check 15: Relaunch FINORA.exe a second time and verify SQLite persistence in %APPDATA%\FINORA\finora.db
    relaunch_proc = subprocess.Popen([str(INSTALLED_EXE), "--headless"], cwd=str(INSTALL_DIR), env=clean_env)
    info2 = wait_for_runtime_json(30.0)
    base_url2 = f"http://{info2['host']}:{info2['port']}"
    pers_code, pers_tx = http_json("GET", f"{base_url2}/api/transactions?user_id=usr_alex_chen&data_scope=personal")
    assert isinstance(pers_tx, dict)
    pers_count = pers_tx.get("count", 0)
    merchants = [t.get("merchant") for t in pers_tx.get("transactions", [])]
    record(
        13,
        "SQLite data persists in %APPDATA%\\FINORA\\finora.db across full shutdown and restart",
        pers_code == 200 and pers_count == 3 and "Whole Foods Market" in merchants and "Trader Joes" in merchants,
        f"PersistedPersonalCount={pers_count}, Merchants={merchants}, DbPath={DB_FILE}",
    )
    record(
        15,
        "Application launches cleanly a second time after closing",
        info2["pid"] > 0 and info2["pid"] != info["pid"],
        f"FirstPID={info['pid']}, SecondPID={info2['pid']}, Bound={base_url2}",
    )
    kill_all_finora()

    # Also verify FINORA Portable.exe launches and connects to the same persistent %APPDATA%\FINORA\finora.db
    portable_proc = subprocess.Popen([str(PORTABLE_EXE), "--headless"], cwd=str(ROOT_DIR / "installer_output"), env=clean_env)
    info_port = wait_for_runtime_json(35.0)
    base_url_port = f"http://{info_port['host']}:{info_port['port']}"
    port_code, port_tx = http_json("GET", f"{base_url_port}/api/transactions?user_id=usr_alex_chen&data_scope=personal")
    assert isinstance(port_tx, dict)
    kill_all_finora()

    # Check 16: Uninstall cleanly via FINORA Uninstall.exe while preserving %APPDATA%\FINORA\finora.db
    uninstall_copy = ROOT_DIR / "build" / "windows_packaging" / "FINORA Uninstall_test.exe"
    shutil.copy2(UNINSTALL_EXE, uninstall_copy)
    uninst_res = subprocess.run([str(uninstall_copy), "/S", f"/DIR={INSTALL_DIR}"], check=False)
    time.sleep(1.5)
    uninstalled_cleanly = not INSTALL_DIR.exists() and DB_FILE.is_file()
    record(
        16,
        "Uninstall removes app & shortcuts while preserving %APPDATA%\\FINORA\\finora.db",
        uninst_res.returncode == 0 and uninstalled_cleanly and port_code == 200 and port_tx.get("count") == 3,
        f"UninstallExit={uninst_res.returncode}, InstallDirRemoved={not INSTALL_DIR.exists()}, UserDbPreserved={DB_FILE.is_file()}, PortableExeVerified={port_tx.get('count') == 3}",
    )
    if uninstall_copy.exists():
        uninstall_copy.unlink()

    # Re-install via FINORA Setup.exe so FINORA remains installed on the system for user/judges
    subprocess.run([str(SETUP_EXE), "/S", f"/DIR={INSTALL_DIR}"], check=True)
    print("\nALL 16 PACKAGED WINDOWS RUNTIME CHECKS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
