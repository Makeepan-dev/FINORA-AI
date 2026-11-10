# FINORA — Phase 4: Windows Runtime & Installer Verification Report

**Test Timestamp:** November 10, 2026  
**Installer Tested:** `D:\FINORA\installer_output\FINORA Setup.exe`  
**Installed Executable Tested:** `C:\Users\tmage\AppData\Local\Programs\FINORA\FINORA.exe`  
**Portable Executable Tested:** `D:\FINORA\installer_output\FINORA Portable.exe`  
**Automated Verification Harness:** [`desktop/verify_packaged_runtime.py`](file:///d:/FINORA/desktop/verify_packaged_runtime.py)  
**Overall Runtime Verdict:** **`PASS (16/16 Local Packaged Checks Passed; Clean-Machine Test Honestly Marked NOT VERIFIED)`**

---

## 1. Packaged Windows Application Runtime Test Matrix (16 Checks)

All 16 checks were executed against the compiled Windows installer (`FINORA Setup.exe`), the installed desktop binary (`FINORA.exe`), the standalone portable binary (`FINORA Portable.exe`), and the uninstaller (`FINORA Uninstall.exe`) with Python and Node.js stripped from `PATH` (`PATH=C:\Windows\System32;C:\Windows;...`):

| # | Test Case | Status | Measured Runtime Evidence |
| :---: | :--- | :---: | :--- |
| **01** | **Fresh installation and first launch** | **`PASS`** | `FINORA Setup.exe /S /DIR="C:\Users\tmage\AppData\Local\Programs\FINORA"` exited `0`; verified `FINORA.exe`, `FINORA Uninstall.exe`, Start Menu shortcut (`FINORA.lnk`), Desktop shortcut (`FINORA.lnk`), and Registry key `HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\FINORA`. |
| **02** | **Window opens & bundled React SPA serves** | **`PASS`** | Launched installed `FINORA.exe`; verified active `FINORA` Windows process (`PID=25564`) and `GET http://127.0.0.1:8000/` returned `HTTP 200` (`1,162 bytes` bundled React SPA `index.html` with `<div id="root"></div>`). |
| **03** | **Backend starts automatically without terminal** | **`PASS`** | Bundled FastAPI + Uvicorn server started automatically inside `FINORA.exe` (`--noconsole`) on `http://127.0.0.1:8000` with `database_file=C:\Users\tmage\AppData\Roaming\FINORA\finora.db`. |
| **04** | **Health check, API communication & Single-Instance Mutex** | **`PASS`** | `GET http://127.0.0.1:8000/health` returned `HTTP 200` (`{"status": "healthy"}`). Launching a second instance of `FINORA.exe` detected the Win32 mutex `Local\FINORA_DESKTOP_SINGLE_INSTANCE_V1` and exited cleanly with `ExitCode=0` without spawning a second backend. |
| **05** | **Dashboard loads unified Demo Mode metrics** | **`PASS`** | `POST /api/demo-data/reset` and `GET /api/analytics/dashboard?user_id=usr_alex_chen&data_scope=demo` returned `Income=$7,050.00`, `Expenses=$1,200.51`, `Remaining=$5,849.49`, `Subscriptions=$126.47/mo`, and `Potential Savings=$115.77/mo`. |
| **06** | **AI Advisor grounded financial reasoning** | **`PASS`** | `POST /api/guardian/chat` (`"Help me save $100 this month"`, `data_scope="demo"`) returned `HTTP 200` with structured recommendations grounded in the `$115.77/month` savings math. |
| **07** | **Transactions screen & manual entry** | **`PASS`** | `GET /api/transactions?user_id=usr_alex_chen&data_scope=demo` returned `25` demo transactions; `POST /api/transactions` created personal transaction `Whole Foods Market ($54.25)` in `personal` scope (`tx_0330b5c4bd`). |
| **08** | **CSV preview and import** | **`PASS`** | `POST /api/transactions/import-csv/preview` with 2 valid rows (`Trader Joes $42.10`, `Shell Oil $35.00`) and 1 malformed row (`bad-date`, `not-a-number`) returned `valid_count=2`, `invalid_count=1`; `POST /api/transactions/import-csv/confirm` imported `2` personal rows without contaminating demo data. |
| **09** | **Savings calculations match verified backend results** | **`PASS`** | `GET /api/savings/dashboard?user_id=usr_alex_chen&data_scope=demo` returned `potential_monthly_savings=$115.77`, `potential_annual_savings=$1,389.24`, and `verified_realized_savings=$0.00`. |
| **10** | **Nearby services & transport-adjusted geolocation savings** | **`PASS`** | `POST /api/location/permission` (`San Francisco`, `37.7749, -122.4194`), `GET /api/location/nearby?category=fitness` returned `4` nearby options, and `GET /api/location/gym-scenario` verified `$25.00/mo` gross difference and `$20.71/mo` net savings after `$4.29/mo` transport cost. |
| **11** | **Location permission revocation** | **`PASS`** | `POST /api/location/permission` (`is_granted=False`) immediately cleared coordinates (`latitude=None`, `longitude=None`, `location_source="revoked"`) and `GET /api/location/nearby` returned `0` automatic results (`[]`). |
| **12** | **PayPal Sandbox workflow & cross-user ownership protection** | **`PASS`** | `GET /api/payments/config-status` confirmed `mode="sandbox"`; `POST /api/payments/create-order` (`sav_gym_planet_20`) created Sandbox order `SANDBOX-ORD-5F34E95BE065` (`$20.00`); cross-user capture attempt (`usr_sarah_jenkins`) was blocked with `HTTP 403 Forbidden`. |
| **13** | **SQLite data persists across shutdown and restart** | **`PASS`** | Shut down `FINORA.exe` completely, verified zero running processes, relaunched `FINORA.exe`, and queried `GET /api/transactions?user_id=usr_alex_chen&data_scope=personal`: all `3` personal transactions (`Whole Foods Market`, `Trader Joes`, `Shell Oil`) persisted in `C:\Users\tmage\AppData\Roaming\FINORA\finora.db` (`225,280 bytes`). |
| **14** | **No duplicate or orphan backend processes remain on exit** | **`PASS`** | Verified via `Get-Process 'FINORA*'` after closing the application: `RemainingFinoraProcesses=0`. |
| **15** | **Application launches cleanly a second time after closing** | **`PASS`** | Relaunched `FINORA.exe` (`FirstPID=25564` -> `SecondPID=29260`) and `FINORA Portable.exe`: both bound cleanly to `http://127.0.0.1:8000` and served the persisted `%APPDATA%\FINORA\finora.db` database. |
| **16** | **Uninstall removes app & shortcuts while preserving user DB** | **`PASS`** | Executed `FINORA Uninstall.exe /S`: removed `C:\Users\tmage\AppData\Local\Programs\FINORA`, Start Menu shortcut, Desktop shortcut, and Registry entry (`ExitCode=0`), while preserving `C:\Users\tmage\AppData\Roaming\FINORA\finora.db` intact. Re-installed via `FINORA Setup.exe /S` afterward. |

---

## 2. Clean-Machine Verification Disclosure

| Environment | Status | Notes |
| :--- | :---: | :--- |
| **Local Self-Contained Execution (`PATH` stripped of Python & Node.js)** | **`PASS`** | Executed `FINORA.exe` and `FINORA Portable.exe` with `PATH` restricted strictly to `C:\Windows\System32;C:\Windows;...` so neither system Python nor Node.js could be invoked. Both binaries ran using only their bundled PyInstaller `_internal` Python 3.12 runtime and bundled `frontend_dist` assets. |
| **Separate Physical/VM Windows Machine Without Python or Node.js Installed** | **`NOT VERIFIED`** | Only the single development workstation (`Windows 11 build 26200`) was available during this session; testing on a separate physical machine or clean VM without Python/Node installed could not be performed. |

---

## 3. Existing Application Regression Checks (Dev Mode)

- **Backend Automated Pytest Suite (`pytest -q`):** **`124 passed` (`0 failed`)**.
- **Frontend TypeScript Check (`npx tsc --noEmit`):** **`PASS` (Exit Code `0`)**.
- **Frontend Vite Production Build (`npx vite build`):** **`PASS` (Exit Code `0`, `dist/index.html`, `dist/assets/*.css`, `dist/assets/*.js`)**.
