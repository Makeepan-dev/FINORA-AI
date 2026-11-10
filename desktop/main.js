const { app, BrowserWindow, shell, session, dialog } = require("electron");
const path = require("path");
const fs = require("fs");
const net = require("net");
const http = require("http");
const { spawn, execFileSync } = require("child_process");

let mainWindow = null;
let backendProcess = null;
let backendPort = 8000;
let isQuitting = false;

const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  app.quit();
} else {
  app.on("second-instance", () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

function getAppDataFinoraDir() {
  const base = process.env.FINORA_DATA_DIR || path.join(app.getPath("appData"), "FINORA");
  if (!fs.existsSync(base)) {
    fs.mkdirSync(base, { recursive: true });
  }
  return base;
}

function findAvailablePort(startPort = 8000) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.unref();
    server.on("error", () => {
      resolve(findAvailablePort(startPort + 1));
    });
    server.listen(startPort, "127.0.0.1", () => {
      const { port } = server.address();
      server.close(() => resolve(port));
    });
  });
}

function resolveBackendExecutable() {
  if (app.isPackaged) {
    const packagedExe = path.join(process.resourcesPath, "backend", "finora-backend.exe");
    if (fs.existsSync(packagedExe)) {
      return { cmd: packagedExe, args: [], cwd: path.dirname(packagedExe) };
    }
  }
  const localDistExe = path.join(__dirname, "backend_dist", "finora-backend", "finora-backend.exe");
  if (fs.existsSync(localDistExe)) {
    return { cmd: localDistExe, args: [], cwd: path.dirname(localDistExe) };
  }
  const venvPython = path.resolve(__dirname, "..", "backend", ".venv", "Scripts", "python.exe");
  const scriptPath = path.resolve(__dirname, "..", "backend", "run_desktop_backend.py");
  return { cmd: venvPython, args: [scriptPath], cwd: path.resolve(__dirname, "..", "backend") };
}

function stopBackendProcess() {
  if (!backendProcess) return;
  const pid = backendProcess.pid;
  backendProcess = null;
  if (!pid) return;

  try {
    if (process.platform === "win32") {
      execFileSync("taskkill", ["/PID", String(pid), "/T", "/F"], {
        windowsHide: true,
        stdio: "ignore"
      });
    } else {
      process.kill(pid, "SIGTERM");
    }
  } catch (_) {
    // Process already exited
  }
}

function waitForBackendHealth(port, timeoutMs = 30000) {
  const start = Date.now();
  return new Promise((resolve, reject) => {
    const check = () => {
      if (!backendProcess && Date.now() - start > 1500) {
        return reject(new Error("Backend process exited prematurely."));
      }
      const req = http.get(`http://127.0.0.1:${port}/health`, (res) => {
        let body = "";
        res.on("data", (chunk) => (body += chunk));
        res.on("end", () => {
          if (res.statusCode === 200) {
            try {
              const parsed = JSON.parse(body);
              if (parsed && parsed.status === "healthy") {
                return resolve(parsed);
              }
            } catch (_) {}
          }
          retry();
        });
      });
      req.on("error", retry);
      req.setTimeout(1500, () => {
        req.destroy();
        retry();
      });
    };

    const retry = () => {
      if (Date.now() - start >= timeoutMs) {
        reject(new Error(`Timed out after ${timeoutMs}ms waiting for /health on port ${port}`));
      } else {
        setTimeout(check, 350);
      }
    };

    check();
  });
}

async function startBackend() {
  backendPort = await findAvailablePort(8000);
  const dataDir = getAppDataFinoraDir();
  const logFile = path.join(dataDir, "backend.log");
  const logStream = fs.createWriteStream(logFile, { flags: "a" });

  const { cmd, args, cwd } = resolveBackendExecutable();
  const spawnArgs = [...args, "--host", "127.0.0.1", "--port", String(backendPort)];

  logStream.write(`\n[${new Date().toISOString()}] Starting backend: ${cmd} ${spawnArgs.join(" ")}\n`);

  backendProcess = spawn(cmd, spawnArgs, {
    cwd,
    windowsHide: true,
    stdio: ["ignore", "pipe", "pipe"],
    env: {
      ...process.env,
      FINORA_DESKTOP_MODE: "1",
      FINORA_DATA_DIR: dataDir,
      FINORA_PORT: String(backendPort)
    }
  });

  backendProcess.stdout.on("data", (chunk) => logStream.write(chunk));
  backendProcess.stderr.on("data", (chunk) => logStream.write(chunk));
  backendProcess.on("exit", (code, signal) => {
    logStream.write(`[${new Date().toISOString()}] Backend exited (code=${code}, signal=${signal})\n`);
    if (!isQuitting) {
      backendProcess = null;
    }
  });

  await waitForBackendHealth(backendPort, 35000);
}

async function createMainWindow() {
  session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
    if (permission === "geolocation") {
      callback(true);
    } else {
      callback(false);
    }
  });

  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    title: "FINORA — AI Financial Intelligence Assistant",
    backgroundColor: "#020617",
    icon: path.join(__dirname, "icon.ico"),
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  });

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith("https://") || url.startsWith("http://")) {
      if (!url.startsWith(`http://127.0.0.1:${backendPort}`)) {
        shell.openExternal(url);
        return { action: "deny" };
      }
    }
    return { action: "allow" };
  });

  await mainWindow.loadFile(path.join(__dirname, "splash.html"));

  try {
    await startBackend();
    await mainWindow.loadURL(`http://127.0.0.1:${backendPort}/`);
  } catch (err) {
    await mainWindow.loadFile(path.join(__dirname, "error.html"));
    dialog.showErrorBox(
      "FINORA Backend Startup Error",
      `Failed to start the bundled FINORA backend service:\n${err.message}\n\nLogs are saved at:\n${path.join(getAppDataFinoraDir(), "backend.log")}`
    );
  }

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

app.whenReady().then(createMainWindow);

app.on("before-quit", () => {
  isQuitting = true;
  stopBackendProcess();
});

app.on("will-quit", () => {
  isQuitting = true;
  stopBackendProcess();
});

app.on("window-all-closed", () => {
  isQuitting = true;
  stopBackendProcess();
  app.quit();
});

process.on("exit", () => {
  stopBackendProcess();
});
