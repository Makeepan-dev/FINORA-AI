const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("finoraDesktop", {
  isDesktopApp: true,
  platform: process.platform,
  version: "1.0.0"
});
