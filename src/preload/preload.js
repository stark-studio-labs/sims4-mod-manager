const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  // Window controls
  minimize: () => ipcRenderer.send('window:minimize'),
  maximize: () => ipcRenderer.send('window:maximize'),
  close: () => ipcRenderer.send('window:close'),

  // Settings
  getSetting: (key) => ipcRenderer.invoke('settings:get', key),
  setSetting: (key, value) => ipcRenderer.invoke('settings:set', key, value),
  getAllSettings: () => ipcRenderer.invoke('settings:getAll'),

  // Mod path detection
  detectModsPath: () => ipcRenderer.invoke('mods:detectPath'),
  browseModsPath: () => ipcRenderer.invoke('mods:browsePath'),

  // Mod operations
  getAvailableMods: () => ipcRenderer.invoke('mods:getAvailable'),
  getInstalledMods: (modsPath) => ipcRenderer.invoke('mods:getInstalled', modsPath),
  installMod: (modId, modsPath) => ipcRenderer.invoke('mods:install', modId, modsPath),
  uninstallMod: (modId, modsPath) => ipcRenderer.invoke('mods:uninstall', modId, modsPath),
  enableScriptMods: (modsPath) => ipcRenderer.invoke('mods:enableScriptMods', modsPath),

  // Progress listener
  onInstallProgress: (callback) => {
    ipcRenderer.on('mods:installProgress', (_, data) => callback(data));
  },
  removeInstallProgress: () => {
    ipcRenderer.removeAllListeners('mods:installProgress');
  },

  // Updates
  checkForUpdates: () => ipcRenderer.invoke('updates:check'),
  checkModUpdates: () => ipcRenderer.invoke('updates:checkMods'),

  // Shell
  openExternal: (url) => ipcRenderer.invoke('shell:openExternal', url),
  openPath: (p) => ipcRenderer.invoke('shell:openPath', p),

  // App info
  getVersion: () => ipcRenderer.invoke('app:getVersion'),
  getPlatform: () => ipcRenderer.invoke('app:getPlatform')
});
