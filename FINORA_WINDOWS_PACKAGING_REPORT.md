# FINORA — Phase 3: Windows Desktop Packaging Report

**Build Timestamp:** November 10, 2026  
**Target Platform:** Windows 10 / 11 (x64)  
**Primary Deliverable:** `D:\FINORA\installer_output\FINORA Setup.exe`  
**Optional Deliverable:** `D:\FINORA\installer_output\FINORA Portable.exe`  
**Build Status:** **`SUCCESS`**

---

## 1. Packaging Architecture

FINORA's Windows desktop distribution combines three self-contained components built deterministically via [`desktop/build_windows_packages.py`](file:///d:/FINORA/desktop/build_windows_packages.py):

1. **Bundled Production Frontend (`frontend/dist` -> `frontend_dist`):**
   - Compiled with TypeScript (`tsc --noEmit`) and Vite (`vite build`).
   - Served on the exact same local origin (`http://127.0.0.1:<port>/`) by FastAPI in [`backend/app/main.py`](file:///d:/FINORA/backend/app/main.py#L49-L97), eliminating cross-origin asset or relative API path mismatch.
2. **Packaged Desktop Application Engine ([`backend/finora_desktop_app.py`](file:///d:/FINORA/backend/finora_desktop_app.py)):**
   - Built with **PyInstaller 6.22.3** (`--noconsole`, `--icon=desktop/icon.ico`, bundling Python 3.12, FastAPI, Uvicorn, SQLAlchemy, Pydantic, `pywebview`, and all FINORA domain modules).
   - Enforces a Windows Named Mutex (`Local\FINORA_DESKTOP_SINGLE_INSTANCE_V1`) via Win32 `CreateMutexW` so launching a second instance focuses the existing FINORA window rather than spawning duplicate backend servers.
   - Starts the FastAPI + Uvicorn server in-process on a background daemon thread bound to `127.0.0.1:<free_port>` (default `8000`) and polls `GET /health` until `"status": "healthy"` before opening the native Windows UI window (`pywebview` Edge WebView2 host with automatic Edge `--app` fallback).
   - Shuts down Uvicorn (`server.should_exit = True`) immediately when the desktop window closes, leaving zero orphan processes.
3. **Native Windows GUI Installer & Uninstaller ([`desktop/installer/Program.cs`](file:///d:/FINORA/desktop/installer/Program.cs) & [`desktop/installer/UninstallProgram.cs`](file:///d:/FINORA/desktop/installer/UninstallProgram.cs)):**
   - Compiled with the built-in Windows .NET compiler (`csc.exe /target:winexe`) embedding the compressed `FINORA` application bundle (`FINORA.payload.zip`).
   - Supports both interactive Windows Setup Wizard GUI (customizable installation path defaulting to `%LOCALAPPDATA%\Programs\FINORA`, Start Menu shortcut, Desktop shortcut, and post-install launch) and unattended silent installation (`/S`, `/DIR="<path>"`, `/LAUNCH`).
   - Registers `HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\FINORA` and bundles `FINORA Uninstall.exe`, which cleanly removes installed application binaries and shortcuts while preserving `%APPDATA%\FINORA\finora.db` user data by default.

---

## 2. Database & User Data Persistence (`%APPDATA%\FINORA`)

 verified in [`backend/app/core/config.py`](file:///d:/FINORA/backend/app/core/config.py#L7-L38):
- Whenever `IS_DESKTOP_MODE` is active (`sys.frozen` or `FINORA_DESKTOP_MODE=1`), FINORA resolves its persistent user data directory to:
  - `%APPDATA%\FINORA\` (e.g., `C:\Users\<User>\AppData\Roaming\FINORA\`, or `FINORA_DATA_DIR` if explicitly overridden).
- **Persistent SQLite Database:** `%APPDATA%\FINORA\finora.db` — never stored inside temporary PyInstaller `_MEI*` extraction directories, never overwritten on application upgrade, and never deleted on standard uninstall.
- **Zero Personal Data or Secrets Bundled:** [`desktop/build_windows_packages.py`](file:///d:/FINORA/desktop/build_windows_packages.py#L97-L106) enforces a build-time guard that raises a `RuntimeError` if any `.env`, `.db`, `.sqlite`, or `.sqlite3` file exists in the bundle directory. On first launch, FINORA creates `%APPDATA%\FINORA\.env.example` with blank placeholder keys so users can optionally configure their own Gemini or PayPal Sandbox keys locally.

---

## 3. Generated Build Artifacts

| Artifact | Path | Size (Bytes) | Size (MB) | SHA-256 Checksum |
| :--- | :--- | :---: | :---: | :--- |
| **Windows Installer** | `D:\FINORA\installer_output\FINORA Setup.exe` | `25,450,496` | `24.27 MB` | `074B4D3C66B2E5EF94A7DE87C07DB0C512FBA659CDE5C21FA86B3B1E1E4A11A7` |
| **Portable Executable** | `D:\FINORA\installer_output\FINORA Portable.exe` | `25,557,396` | `24.37 MB` | `49B532276492E058C7C541230B1CC672AD94BA172C7B7D35DAE87AE4E669F253` |
