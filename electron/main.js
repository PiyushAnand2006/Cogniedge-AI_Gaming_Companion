const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow = null;
let overlayProcess = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 960,
    minWidth: 1024,
    minHeight: 700,
    title: 'CogniEdge — On-Device NPU Intelligence Hub',
    icon: path.join(__dirname, '../assets/cogniedge_logo.png'),
    backgroundColor: '#0f131c',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  const isDev = process.env.NODE_ENV !== 'production';
  const startUrl = isDev ? 'http://localhost:3000' : `file://${path.join(__dirname, '../out/index.html')}`;

  mainWindow.loadURL(startUrl);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function spawnPyQtOverlay() {
  if (overlayProcess && !overlayProcess.killed) {
    console.log('[CogniEdge Electron] PyQt Gaming HUD overlay is already running.');
    return;
  }

  const overlayScript = path.join(__dirname, '../overlay/hud_overlay.py');
  console.log('[CogniEdge Electron] Spawning PyQt Gaming HUD overlay:', overlayScript);

  overlayProcess = spawn('python', [overlayScript], {
    cwd: path.join(__dirname, '..'),
    detached: false,
    stdio: 'inherit',
  });

  overlayProcess.on('error', (err) => {
    console.error('[CogniEdge Electron] Failed to spawn PyQt overlay process:', err);
  });

  overlayProcess.on('exit', (code, signal) => {
    console.log(`[CogniEdge Electron] PyQt overlay exited with code ${code}, signal ${signal}`);
    overlayProcess = null;
  });
}

ipcMain.on('launch-hud-overlay', () => {
  spawnPyQtOverlay();
});

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (overlayProcess && !overlayProcess.killed) {
      overlayProcess.kill();
    }
    app.quit();
  }
});
