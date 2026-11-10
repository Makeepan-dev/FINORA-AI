import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
DESKTOP_DIR = ROOT_DIR / "desktop"
INSTALLER_SRC_DIR = DESKTOP_DIR / "installer"
BUILD_WORK_DIR = ROOT_DIR / "build" / "windows_packaging"
OUTPUT_DIR = ROOT_DIR / "installer_output"
PYTHON_EXE = BACKEND_DIR / ".venv" / "Scripts" / "python.exe"
ICON_PATH = DESKTOP_DIR / "icon.ico"
CSC_EXE = Path(r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe")


def run_cmd(cmd: list[str], cwd: Path) -> None:
    print(f"\n>>> Running: {' '.join(str(c) for c in cmd)} (in {cwd})")
    subprocess.run([str(c) for c in cmd], cwd=str(cwd), check=True)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_WORK_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Ensure icon exists
    if not ICON_PATH.is_file():
        run_cmd([str(PYTHON_EXE), str(DESKTOP_DIR / "generate_icon.py")], DESKTOP_DIR)

    # 2. Ensure frontend production build is fresh
    frontend_dist = FRONTEND_DIR / "dist"
    if not (frontend_dist / "index.html").is_file():
        run_cmd(["npx.cmd", "vite", "build"], FRONTEND_DIR)

    common_pyi_args = [
        str(PYTHON_EXE),
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--noconsole",
        f"--icon={ICON_PATH}",
        f"--paths={BACKEND_DIR}",
        f"--add-data={frontend_dist};frontend_dist",
        "--collect-submodules=app",
        "--collect-submodules=uvicorn",
        "--collect-submodules=webview",
        "--hidden-import=sqlalchemy.dialects.sqlite",
    ]

    # 3. Build directory-mode FINORA.exe for the installer payload
    pyi_dist_dir = BUILD_WORK_DIR / "dist_dir"
    pyi_work_dir = BUILD_WORK_DIR / "work_dir"
    pyi_spec_dir = BUILD_WORK_DIR / "spec_dir"
    app_bundle_dir = pyi_dist_dir / "FINORA"

    for d in (pyi_dist_dir, pyi_work_dir, pyi_spec_dir):
        if d.exists():
            shutil.rmtree(d)
    run_cmd(
        common_pyi_args
        + [
            "--onedir",
            "--name=FINORA",
            f"--distpath={pyi_dist_dir}",
            f"--workpath={pyi_work_dir}",
            f"--specpath={pyi_spec_dir}",
            str(BACKEND_DIR / "finora_desktop_app.py"),
        ],
        BACKEND_DIR,
    )

    shutil.copy2(ICON_PATH, app_bundle_dir / "icon.ico")

    # 4. Compile FINORA Uninstall.exe using built-in Windows .NET csc.exe
    uninstall_exe = app_bundle_dir / "FINORA Uninstall.exe"
    run_cmd(
        [
            str(CSC_EXE),
            "/nologo",
            "/optimize+",
            "/target:winexe",
            f"/win32icon:{ICON_PATH}",
            f"/out:{uninstall_exe}",
            str(INSTALLER_SRC_DIR / "UninstallProgram.cs"),
        ],
        INSTALLER_SRC_DIR,
    )

    # 5. Create payload.zip from app_bundle_dir (strictly excluding any .db or .env files)
    payload_zip = INSTALLER_SRC_DIR / "payload.zip"
    if payload_zip.exists():
        payload_zip.unlink()

    print(f"\n>>> Compressing {app_bundle_dir} -> {payload_zip}")
    with zipfile.ZipFile(payload_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for file_path in app_bundle_dir.rglob("*"):
            if file_path.is_file():
                lower_name = file_path.name.lower()
                if lower_name == ".env" or lower_name.endswith((".db", ".sqlite", ".sqlite3")):
                    raise RuntimeError(f"Refusing to bundle database or .env file: {file_path}")
                rel_path = file_path.relative_to(app_bundle_dir)
                zf.write(file_path, arcname=str(rel_path))

    # 6. Compile FINORA Setup.exe embedding payload.zip
    final_setup_exe = OUTPUT_DIR / "FINORA Setup.exe"
    run_cmd(
        [
            str(CSC_EXE),
            "/nologo",
            "/optimize+",
            "/target:winexe",
            f"/win32icon:{ICON_PATH}",
            "/r:System.IO.Compression.dll",
            "/r:System.IO.Compression.FileSystem.dll",
            f"/resource:{payload_zip},FINORA.payload.zip",
            f"/out:{final_setup_exe}",
            str(INSTALLER_SRC_DIR / "Program.cs"),
        ],
        INSTALLER_SRC_DIR,
    )
    print(f"Created installer: {final_setup_exe} ({final_setup_exe.stat().st_size:,} bytes)")

    if payload_zip.exists():
        payload_zip.unlink()

    # 7. Build FINORA Portable.exe (--onefile standalone portable executable)
    pyi_portable_work = BUILD_WORK_DIR / "work_portable"
    pyi_portable_spec = BUILD_WORK_DIR / "spec_portable"
    for d in (pyi_portable_work, pyi_portable_spec):
        if d.exists():
            shutil.rmtree(d)

    run_cmd(
        common_pyi_args
        + [
            "--onefile",
            "--name=FINORA Portable",
            f"--distpath={OUTPUT_DIR}",
            f"--workpath={pyi_portable_work}",
            f"--specpath={pyi_portable_spec}",
            str(BACKEND_DIR / "finora_desktop_app.py"),
        ],
        BACKEND_DIR,
    )

    final_portable_exe = OUTPUT_DIR / "FINORA Portable.exe"
    print(f"Created portable executable: {final_portable_exe} ({final_portable_exe.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
