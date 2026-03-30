const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const Store = require('electron-store');
const modManager = require('./mod-manager');
const updater = require('./updater');

const store = new Store({
  defaults: {
    modsPath: null,
    autoUpdate: true,
    theme: 'dark',
    firstRun: true,
    installedMods: {}
  }
});

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1100,
    height: 750,
    minWidth: 900,
    minHeight: 600,
    frame: false,
    titleBarStyle: 'hidden',
    trafficLightPosition: { x: 16, y: 16 },
    backgroundColor: '#0d1117',
    webPreferences: {
      preload: path.join(__dirname, '..', 'preload', 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    },
    show: false
  });

  mainWindow.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    if (store.get('autoUpdate')) {
      updater.checkForUpdates();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// ── IPC Handlers ────────────────────────────────────────────────────────────

// Window controls
ipcMain.on('window:minimize', () => mainWindow?.minimize());
ipcMain.on('window:maximize', () => {
  if (mainWindow?.isMaximized()) mainWindow.unmaximize();
  else mainWindow?.maximize();
});
ipcMain.on('window:close', () => mainWindow?.close());

// Settings
ipcMain.handle('settings:get', (_, key) => store.get(key));
ipcMain.handle('settings:set', (_, key, value) => {
  store.set(key, value);
  return true;
});
ipcMain.handle('settings:getAll', () => store.store);

// Mod detection
ipcMain.handle('mods:detectPath', () => modManager.detectModsPath());
ipcMain.handle('mods:browsePath', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory'],
    title: 'Select Sims 4 Mods Folder'
  });
  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0];
  }
  return null;
});

// Mod operations
ipcMain.handle('mods:getAvailable', () => modManager.getAvailableMods());
ipcMain.handle('mods:getInstalled', (_, modsPath) => modManager.getInstalledMods(modsPath || store.get('modsPath')));
ipcMain.handle('mods:install', async (_, modId, modsPath) => {
  return modManager.installMod(modId, modsPath || store.get('modsPath'), (progress) => {
    mainWindow?.webContents.send('mods:installProgress', { modId, progress });
  });
});
ipcMain.handle('mods:uninstall', (_, modId, modsPath) => {
  return modManager.uninstallMod(modId, modsPath || store.get('modsPath'));
});
ipcMain.handle('mods:enableScriptMods', (_, modsPath) => {
  return modManager.enableScriptMods(modsPath || store.get('modsPath'));
});

// Update checker
ipcMain.handle('updates:check', () => updater.checkForUpdates());
ipcMain.handle('updates:checkMods', () => modManager.checkModUpdates());

// Shell
ipcMain.handle('shell:openExternal', (_, url) => shell.openExternal(url));
ipcMain.handle('shell:openPath', (_, p) => shell.openPath(p));

// App info
ipcMain.handle('app:getVersion', () => app.getVersion());
ipcMain.handle('app:getPlatform', () => process.platform);
