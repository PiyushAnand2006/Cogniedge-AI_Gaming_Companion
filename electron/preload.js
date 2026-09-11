const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  launchOverlay: () => ipcRenderer.send('launch-hud-overlay'),
  getHardwareStats: () => ipcRenderer.invoke('get-hardware-stats'),
});
