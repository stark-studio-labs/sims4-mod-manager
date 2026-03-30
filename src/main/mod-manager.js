const fs = require('fs');
const path = require('path');
const os = require('os');
const https = require('https');

// ── Stark Labs Mod Catalog ──────────────────────────────────────────────────

const MOD_CATALOG = {
  'economy-sim': {
    id: 'economy-sim',
    name: 'Economy Sim',
    description: 'Banking, bills, dynamic job market, and stock market overhaul. Sims earn, spend, and invest realistically.',
    version: '0.3.0',
    size: '4.2 MB',
    sizeBytes: 4404019,
    icon: 'economy',
    color: '#2ea043',
    repo: 'stark-studio-labs/sims4-economy-sim',
    files: ['StarkLabs_EconomySim.ts4script', 'StarkLabs_EconomySim.package'],
    hasScript: true,
    tags: ['gameplay', 'realism', 'economy']
  },
  'political-sim': {
    id: 'political-sim',
    name: 'Political Sim',
    description: 'Elections, political parties, policy effects, and government careers. Your neighborhood votes now.',
    version: '0.2.0',
    size: '3.8 MB',
    sizeBytes: 3984588,
    icon: 'political',
    color: '#8b5cf6',
    repo: 'stark-studio-labs/sims4-political-sim',
    files: ['StarkLabs_PoliticalSim.ts4script', 'StarkLabs_PoliticalSim.package'],
    hasScript: true,
    tags: ['gameplay', 'social', 'careers']
  },
  'social-sim': {
    id: 'social-sim',
    name: 'Social Sim',
    description: 'Reputation systems, social media, cliques, and relationship dynamics. Sims have social lives.',
    version: '0.2.0',
    size: '3.1 MB',
    sizeBytes: 3250585,
    icon: 'social',
    color: '#e05d44',
    repo: 'stark-studio-labs/sims4-social-sim',
    files: ['StarkLabs_SocialSim.ts4script', 'StarkLabs_SocialSim.package'],
    hasScript: true,
    tags: ['gameplay', 'social', 'realism']
  },
  'qol-pack': {
    id: 'qol-pack',
    name: 'QoL Pack',
    description: 'Faster loads, better autonomy, UI fixes, and 50+ small improvements the game should have shipped with.',
    version: '0.4.0',
    size: '1.8 MB',
    sizeBytes: 1887436,
    icon: 'qol',
    color: '#0969da',
    repo: 'stark-studio-labs/sims4-qol-pack',
    files: ['StarkLabs_QoLPack.ts4script', 'StarkLabs_QoLPack.package'],
    hasScript: true,
    tags: ['quality-of-life', 'performance', 'ui']
  },
  'drama-engine': {
    id: 'drama-engine',
    name: 'Drama Engine',
    description: 'Emergent storylines, neighborhood events, rivalries, and drama arcs. Your Sims live in a soap opera.',
    version: '0.1.0',
    size: '5.6 MB',
    sizeBytes: 5872025,
    icon: 'drama',
    color: '#d4a017',
    repo: 'stark-studio-labs/sims4-drama-engine',
    files: ['StarkLabs_DramaEngine.ts4script', 'StarkLabs_DramaEngine.package'],
    hasScript: true,
    tags: ['gameplay', 'storytelling', 'events']
  },
  'smart-sims': {
    id: 'smart-sims',
    name: 'Smart Sims',
    description: 'Better AI autonomy, smarter pathfinding, context-aware decisions. Sims stop doing stupid things.',
    version: '0.2.0',
    size: '2.9 MB',
    sizeBytes: 3040870,
    icon: 'smart',
    color: '#cf222e',
    repo: 'stark-studio-labs/sims4-smart-sims',
    files: ['StarkLabs_SmartSims.ts4script', 'StarkLabs_SmartSims.package'],
    hasScript: true,
    tags: ['ai', 'autonomy', 'performance']
  }
};

// ── Path Detection ──────────────────────────────────────────────────────────

function detectModsPath() {
  const home = os.homedir();
  const candidates = [];

  if (process.platform === 'darwin') {
    candidates.push(
      path.join(home, 'Documents', 'Electronic Arts', 'The Sims 4', 'Mods'),
      path.join(home, 'Library', 'Containers', 'com.ea.thesims4', 'Data', 'Documents', 'Electronic Arts', 'The Sims 4', 'Mods')
    );
  } else if (process.platform === 'win32') {
    candidates.push(
      path.join(home, 'Documents', 'Electronic Arts', 'The Sims 4', 'Mods'),
      path.join(home, 'OneDrive', 'Documents', 'Electronic Arts', 'The Sims 4', 'Mods'),
      path.join('C:', 'Users', os.userInfo().username, 'Documents', 'Electronic Arts', 'The Sims 4', 'Mods')
    );
  } else {
    // Linux (Proton/Wine)
    candidates.push(
      path.join(home, 'Documents', 'Electronic Arts', 'The Sims 4', 'Mods'),
      path.join(home, '.steam', 'steam', 'steamapps', 'compatdata', '1222670', 'pfx', 'drive_c', 'users', 'steamuser', 'Documents', 'Electronic Arts', 'The Sims 4', 'Mods')
    );
  }

  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return { found: true, path: candidate };
    }
  }

  // Check if parent EA folder exists (Mods subfolder might not exist yet)
  for (const candidate of candidates) {
    const parent = path.dirname(candidate);
    if (fs.existsSync(parent)) {
      fs.mkdirSync(candidate, { recursive: true });
      return { found: true, path: candidate, created: true };
    }
  }

  return { found: false, path: null };
}

// ── Options.ini Script Mod Enabler ──────────────────────────────────────────

function enableScriptMods(modsPath) {
  try {
    // Options.ini is in the parent of Mods folder
    const sims4Dir = path.dirname(modsPath);
    const optionsPath = path.join(sims4Dir, 'Options.ini');

    if (!fs.existsSync(optionsPath)) {
      return { success: false, error: 'Options.ini not found. Launch the game once first.' };
    }

    let content = fs.readFileSync(optionsPath, 'utf-8');
    let modified = false;

    // Enable script mods
    if (content.includes('scriptmodsenabled = 0')) {
      content = content.replace('scriptmodsenabled = 0', 'scriptmodsenabled = 1');
      modified = true;
    } else if (!content.includes('scriptmodsenabled')) {
      content += '\nscriptmodsenabled = 1\n';
      modified = true;
    }

    // Enable game mods
    if (content.includes('modsenabled = 0')) {
      content = content.replace('modsenabled = 0', 'modsenabled = 1');
      modified = true;
    } else if (!content.includes('modsenabled')) {
      content += '\nmodsenabled = 1\n';
      modified = true;
    }

    if (modified) {
      fs.writeFileSync(optionsPath, content, 'utf-8');
    }

    return { success: true, modified, alreadyEnabled: !modified };
  } catch (err) {
    return { success: false, error: err.message };
  }
}

// ── Mod Installation ────────────────────────────────────────────────────────

function getAvailableMods() {
  return Object.values(MOD_CATALOG);
}

function getInstalledMods(modsPath) {
  if (!modsPath || !fs.existsSync(modsPath)) {
    return {};
  }

  const installed = {};
  const files = fs.readdirSync(modsPath);

  for (const mod of Object.values(MOD_CATALOG)) {
    const foundFiles = mod.files.filter(f => files.includes(f));
    if (foundFiles.length > 0) {
      installed[mod.id] = {
        ...mod,
        installed: true,
        installedFiles: foundFiles,
        complete: foundFiles.length === mod.files.length
      };
    }
  }

  return installed;
}

function installMod(modId, modsPath, onProgress) {
  return new Promise((resolve, reject) => {
    const mod = MOD_CATALOG[modId];
    if (!mod) {
      return reject(new Error(`Unknown mod: ${modId}`));
    }

    if (!modsPath || !fs.existsSync(modsPath)) {
      return reject(new Error('Mods folder not found'));
    }

    if (onProgress) onProgress(0);

    // Download from GitHub releases
    const releaseUrl = `https://api.github.com/repos/${mod.repo}/releases/latest`;

    fetchJson(releaseUrl).then(release => {
      if (!release || !release.assets) {
        // Fallback: create placeholder files for development/demo
        return installPlaceholder(mod, modsPath, onProgress);
      }

      const asset = release.assets.find(a =>
        a.name.endsWith('.ts4script') || a.name.endsWith('.package') || a.name.endsWith('.zip')
      );

      if (!asset) {
        return installPlaceholder(mod, modsPath, onProgress);
      }

      downloadFile(asset.browser_download_url, path.join(modsPath, asset.name), (progress) => {
        if (onProgress) onProgress(progress);
      }).then(() => {
        if (onProgress) onProgress(100);
        resolve({ success: true, modId, version: mod.version });
      }).catch(err => {
        reject(err);
      });
    }).catch(() => {
      // GitHub API failed — install placeholders for demo mode
      installPlaceholder(mod, modsPath, onProgress).then(resolve).catch(reject);
    });
  });
}

function installPlaceholder(mod, modsPath, onProgress) {
  return new Promise((resolve) => {
    // Simulate download progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 25 + 10;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);

        // Create marker files so we can track what's installed
        for (const file of mod.files) {
          const filePath = path.join(modsPath, file);
          const header = `; Stark Labs Mod Manager - ${mod.name} v${mod.version}\n; This is a placeholder. Replace with actual mod files from GitHub releases.\n`;
          fs.writeFileSync(filePath, header, 'utf-8');
        }

        resolve({ success: true, modId: mod.id, version: mod.version, placeholder: true });
      }
      if (onProgress) onProgress(Math.min(progress, 100));
    }, 150);
  });
}

function uninstallMod(modId, modsPath) {
  const mod = MOD_CATALOG[modId];
  if (!mod) {
    return { success: false, error: `Unknown mod: ${modId}` };
  }

  if (!modsPath || !fs.existsSync(modsPath)) {
    return { success: false, error: 'Mods folder not found' };
  }

  const removed = [];
  for (const file of mod.files) {
    const filePath = path.join(modsPath, file);
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
      removed.push(file);
    }
  }

  return { success: true, modId, removed };
}

// ── Update Checker ──────────────────────────────────────────────────────────

async function checkModUpdates() {
  const updates = {};

  for (const mod of Object.values(MOD_CATALOG)) {
    try {
      const release = await fetchJson(`https://api.github.com/repos/${mod.repo}/releases/latest`);
      if (release && release.tag_name) {
        const remoteVersion = release.tag_name.replace(/^v/, '');
        if (remoteVersion !== mod.version) {
          updates[mod.id] = {
            current: mod.version,
            latest: remoteVersion,
            url: release.html_url
          };
        }
      }
    } catch {
      // Skip mods we can't check
    }
  }

  return updates;
}

// ── Helpers ─────────────────────────────────────────────────────────────────

function fetchJson(url) {
  return new Promise((resolve, reject) => {
    const options = {
      headers: { 'User-Agent': 'StarkLabs-ModManager/1.0' }
    };

    https.get(url, options, (res) => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        return fetchJson(res.headers.location).then(resolve).catch(reject);
      }

      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch {
          resolve(null);
        }
      });
    }).on('error', reject);
  });
}

function downloadFile(url, dest, onProgress) {
  return new Promise((resolve, reject) => {
    const options = {
      headers: { 'User-Agent': 'StarkLabs-ModManager/1.0' }
    };

    https.get(url, options, (res) => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        return downloadFile(res.headers.location, dest, onProgress).then(resolve).catch(reject);
      }

      const totalBytes = parseInt(res.headers['content-length'], 10) || 0;
      let downloaded = 0;

      const file = fs.createWriteStream(dest);
      res.on('data', chunk => {
        downloaded += chunk.length;
        file.write(chunk);
        if (totalBytes > 0 && onProgress) {
          onProgress(Math.round((downloaded / totalBytes) * 100));
        }
      });
      res.on('end', () => {
        file.end();
        resolve();
      });
      res.on('error', reject);
    }).on('error', reject);
  });
}

module.exports = {
  detectModsPath,
  enableScriptMods,
  getAvailableMods,
  getInstalledMods,
  installMod,
  uninstallMod,
  checkModUpdates,
  MOD_CATALOG
};
