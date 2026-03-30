// Auto-updater for the Electron app itself (not mods)
// Uses electron-updater to check GitHub Releases for new app versions

let autoUpdater;

try {
  const { autoUpdater: au } = require('electron-updater');
  autoUpdater = au;
} catch {
  // electron-updater not available in dev mode
  autoUpdater = null;
}

function checkForUpdates() {
  if (!autoUpdater) {
    console.log('[updater] electron-updater not available (dev mode)');
    return Promise.resolve({ updateAvailable: false });
  }

  return new Promise((resolve) => {
    autoUpdater.autoDownload = false;
    autoUpdater.autoInstallOnAppQuit = true;

    autoUpdater.on('update-available', (info) => {
      resolve({ updateAvailable: true, version: info.version, releaseNotes: info.releaseNotes });
    });

    autoUpdater.on('update-not-available', () => {
      resolve({ updateAvailable: false });
    });

    autoUpdater.on('error', (err) => {
      console.error('[updater] Error:', err.message);
      resolve({ updateAvailable: false, error: err.message });
    });

    autoUpdater.checkForUpdates().catch(() => {
      resolve({ updateAvailable: false });
    });
  });
}

module.exports = { checkForUpdates };
