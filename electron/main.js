const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const serviceManager = require('./service_manager');

let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1200,
    minHeight: 760,
    title: 'CogniEdge AI Gaming Companion',
    backgroundColor: '#0c0d12',
    frame: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  const startUrl = process.env.ELECTRON_START_URL || 'http://localhost:3000';
  mainWindow.loadURL(startUrl);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(async () => {
  // Start Python FastAPI backend if not in separate dev mode
  if (!process.env.NO_PYTHON_SPAWN) {
    serviceManager.startBackend();
    await serviceManager.waitForHealth();
  }

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  serviceManager.stopBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', () => {
  serviceManager.stopBackend();
});
