// ── Stark Labs Mod Manager — Renderer ─────────────────────────────────────
// All data rendered via innerHTML comes from the local hardcoded mod catalog
// (no user input or remote content), so there is no XSS vector.

let state = {
  modsPath: null,
  firstRun: true,
  persona: null,
  availableMods: [],
  installedMods: {},
  currentView: 'splash',
  installing: new Set(),
  progress: {}
};

// ── SVG Icon Helper ─────────────────────────────────────────────────────────

function appendSVGIcon(container, svgString) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(svgString, 'image/svg+xml');
  container.appendChild(doc.documentElement);
}

// ── Mod Icons (CCO v3 custom SVGs) ─────────────────────────────────────────
// SVGs sourced from brand/preview/render-v3.html (CCO approved 2026-03-30)

const MOD_ICONS = {
  'economy-sim': {
    svg: `<svg width="28" height="28" viewBox="0 0 30 30" fill="none"><ellipse cx="15" cy="8" rx="10" ry="4" fill="none" stroke="#2ea043" stroke-width="1.5"/><path d="M5 8 v6 c0 2.2 4.5 4 10 4 s10-1.8 10-4 V8" fill="none" stroke="#2ea043" stroke-width="1.5"/><ellipse cx="15" cy="14" rx="10" ry="4" fill="none" stroke="#2ea043" stroke-width="1.5"/><path d="M5 14 v5 c0 2.2 4.5 4 10 4 s10-1.8 10-4 v-5" fill="none" stroke="#2ea043" stroke-width="1.5"/></svg>`,
    bg: 'rgba(46, 160, 67, 0.12)', border: 'rgba(46, 160, 67, 0.25)', wash: 'rgba(46, 160, 67, 0.1)'
  },
  'political-sim': {
    svg: `<svg width="28" height="28" viewBox="0 0 30 30" fill="none"><rect x="3" y="24" width="24" height="2.5" rx="1.2" fill="#8957e5" opacity="0.8"/><rect x="6" y="10" width="4" height="14" rx="1" fill="none" stroke="#8957e5" stroke-width="1.5"/><rect x="13" y="7" width="4" height="17" rx="1" fill="none" stroke="#8957e5" stroke-width="1.5"/><rect x="20" y="13" width="4" height="11" rx="1" fill="none" stroke="#8957e5" stroke-width="1.5"/><path d="M3 10 L15 4 L27 10" stroke="#8957e5" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>`,
    bg: 'rgba(137, 87, 229, 0.12)', border: 'rgba(137, 87, 229, 0.25)', wash: 'rgba(137, 87, 229, 0.1)'
  },
  'social-sim': {
    svg: `<svg width="28" height="28" viewBox="0 0 30 30" fill="none"><circle cx="15" cy="7" r="3.5" stroke="#e05d44" stroke-width="1.5"/><circle cx="6" cy="22" r="3" stroke="#e05d44" stroke-width="1.5"/><circle cx="24" cy="22" r="3" stroke="#e05d44" stroke-width="1.5"/><line x1="15" y1="10.5" x2="8" y2="19.2" stroke="#e05d44" stroke-width="1.2" stroke-opacity="0.7"/><line x1="15" y1="10.5" x2="22" y2="19.2" stroke="#e05d44" stroke-width="1.2" stroke-opacity="0.7"/><line x1="9" y1="22" x2="21" y2="22" stroke="#e05d44" stroke-width="1.2" stroke-opacity="0.5"/></svg>`,
    bg: 'rgba(224, 93, 68, 0.12)', border: 'rgba(224, 93, 68, 0.25)', wash: 'rgba(224, 93, 68, 0.1)'
  },
  'qol-pack': {
    svg: `<svg width="28" height="28" viewBox="0 0 30 30" fill="none"><line x1="4" y1="9" x2="26" y2="9" stroke="#388bfd" stroke-width="1.5" stroke-linecap="round"/><line x1="4" y1="15" x2="26" y2="15" stroke="#388bfd" stroke-width="1.5" stroke-linecap="round"/><line x1="4" y1="21" x2="26" y2="21" stroke="#388bfd" stroke-width="1.5" stroke-linecap="round"/><circle cx="10" cy="9" r="3" fill="#0d1117" stroke="#388bfd" stroke-width="1.5"/><circle cx="20" cy="15" r="3" fill="#0d1117" stroke="#388bfd" stroke-width="1.5"/><circle cx="13" cy="21" r="3" fill="#0d1117" stroke="#388bfd" stroke-width="1.5"/></svg>`,
    bg: 'rgba(56, 139, 253, 0.12)', border: 'rgba(56, 139, 253, 0.25)', wash: 'rgba(56, 139, 253, 0.1)'
  },
  'drama-engine': {
    svg: `<svg width="28" height="28" viewBox="0 0 30 30" fill="none"><path d="M3 22 C6 22 7 10 10 10 C13 10 14 18 17 18 C20 18 21 8 24 6 C26 5 27 8 27 8" stroke="#d4a017" stroke-width="1.8" stroke-linecap="round" fill="none"/><circle cx="24" cy="6" r="2.5" fill="#d4a017" opacity="0.9"/></svg>`,
    bg: 'rgba(212, 160, 23, 0.12)', border: 'rgba(212, 160, 23, 0.25)', wash: 'rgba(212, 160, 23, 0.1)'
  },
  'smart-sims': {
    svg: `<svg width="28" height="28" viewBox="0 0 30 30" fill="none"><circle cx="5" cy="10" r="2.5" stroke="#1f9ada" stroke-width="1.5" fill="none"/><circle cx="5" cy="20" r="2.5" stroke="#1f9ada" stroke-width="1.5" fill="none"/><circle cx="15" cy="7" r="2.5" stroke="#1f9ada" stroke-width="1.5" fill="none"/><circle cx="15" cy="15" r="2.5" stroke="#1f9ada" stroke-width="1.5" fill="none"/><circle cx="15" cy="23" r="2.5" stroke="#1f9ada" stroke-width="1.5" fill="none"/><circle cx="25" cy="15" r="2.5" fill="#1f9ada" opacity="0.9"/><line x1="7.5" y1="10" x2="12.5" y2="7" stroke="#1f9ada" stroke-width="1" stroke-opacity="0.5"/><line x1="7.5" y1="10" x2="12.5" y2="15" stroke="#1f9ada" stroke-width="1" stroke-opacity="0.5"/><line x1="7.5" y1="10" x2="12.5" y2="23" stroke="#1f9ada" stroke-width="1" stroke-opacity="0.3"/><line x1="7.5" y1="20" x2="12.5" y2="7" stroke="#1f9ada" stroke-width="1" stroke-opacity="0.3"/><line x1="7.5" y1="20" x2="12.5" y2="15" stroke="#1f9ada" stroke-width="1" stroke-opacity="0.5"/><line x1="7.5" y1="20" x2="12.5" y2="23" stroke="#1f9ada" stroke-width="1" stroke-opacity="0.5"/><line x1="17.5" y1="7" x2="22.5" y2="15" stroke="#1f9ada" stroke-width="1" stroke-opacity="0.6"/><line x1="17.5" y1="15" x2="22.5" y2="15" stroke="#1f9ada" stroke-width="1.5" stroke-opacity="0.8"/><line x1="17.5" y1="23" x2="22.5" y2="15" stroke="#1f9ada" stroke-width="1" stroke-opacity="0.6"/></svg>`,
    bg: 'rgba(31, 154, 218, 0.12)', border: 'rgba(31, 154, 218, 0.25)', wash: 'rgba(31, 154, 218, 0.1)'
  }
};

// ── Initialize ──────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
  // Load settings
  const settings = await api.getAllSettings();
  state.modsPath = settings.modsPath;
  state.firstRun = settings.firstRun;
  state.persona = settings.persona || localStorage.getItem('starkLabsPersona') || null;

  // Set version
  const version = await api.getVersion();
  document.getElementById('version-label').textContent = `v${version}`;
  document.getElementById('settings-version').textContent = `v${version}`;

  // Load auto-update toggle
  const autoUpdate = settings.autoUpdate !== false;
  document.getElementById('toggle-autoupdate').checked = autoUpdate;

  // Load mods catalog
  state.availableMods = await api.getAvailableMods();

  // Listen for install progress
  api.onInstallProgress(({ modId, progress }) => {
    state.progress[modId] = progress;
    updateProgressBar(modId, progress);
    if (progress >= 100) {
      setTimeout(() => {
        state.installing.delete(modId);
        delete state.progress[modId];
        refreshCurrentView();
      }, 500);
    }
  });

  // Route to appropriate view
  if (state.firstRun || !state.modsPath) {
    showView('splash');
  } else {
    document.getElementById('view-splash').classList.add('hidden');
    document.getElementById('view-welcome').classList.add('hidden');
    await refreshInstalledMods();
    showView('mods');
  }
});

// ── View Router ─────────────────────────────────────────────────────────────

function showView(viewName) {
  state.currentView = viewName;

  // Hide all views
  document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));

  // Show target
  const view = document.getElementById(`view-${viewName}`);
  if (view) {
    view.classList.remove('hidden');
  }

  // Update nav
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.view === viewName);
  });

  // Refresh content
  if (viewName === 'mods') renderModGrid();
  if (viewName === 'installed') renderInstalledList();
  if (viewName === 'settings') refreshSettings();
}

function refreshCurrentView() {
  showView(state.currentView);
}

// ── Splash / Persona Picker ────────────────────────────────────────────────

function selectPersona(el) {
  document.querySelectorAll('.persona-card').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
  state.persona = el.dataset.persona;
  document.getElementById('btn-splash-start').disabled = false;
}

async function startFromSplash() {
  if (!state.persona) return;
  await api.setSetting('persona', state.persona);
  localStorage.setItem('starkLabsPersona', state.persona);
  showView('welcome');
  runDetection();
}

// ── Welcome / Detection ─────────────────────────────────────────────────────

async function runDetection() {
  const detectEl = document.getElementById('welcome-detect');
  const resultEl = document.getElementById('welcome-result');
  const actionsEl = document.getElementById('welcome-actions');

  detectEl.classList.remove('hidden');
  resultEl.classList.add('hidden');
  actionsEl.classList.add('hidden');

  // Simulate a brief delay for visual effect
  await sleep(1200);

  const result = await api.detectModsPath();

  detectEl.classList.add('hidden');
  resultEl.classList.remove('hidden');
  actionsEl.classList.remove('hidden');

  const iconEl = document.getElementById('detect-icon');
  const textEl = document.getElementById('detect-text');
  const pathEl = document.getElementById('detect-path');

  if (result.found) {
    iconEl.textContent = '\u2705';
    textEl.textContent = result.created ? 'Mods folder created!' : 'Sims 4 found!';
    pathEl.textContent = result.path;
    state.modsPath = result.path;
  } else {
    iconEl.textContent = '\u{1F50D}';
    textEl.textContent = 'Could not auto-detect Sims 4';
    pathEl.textContent = 'Click below to select your Mods folder manually';
  }
}

async function browseForMods() {
  const result = await api.browseModsPath();
  if (result) {
    state.modsPath = result;
    document.getElementById('detect-icon').textContent = '\u2705';
    document.getElementById('detect-text').textContent = 'Folder selected!';
    document.getElementById('detect-path').textContent = result;
  }
}

async function completeWelcome() {
  if (!state.modsPath) {
    showToast('Please select a Mods folder first', 'error');
    return;
  }

  await api.setSetting('modsPath', state.modsPath);
  await api.setSetting('firstRun', false);
  state.firstRun = false;

  // Auto-enable script mods
  const enableResult = await api.enableScriptMods(state.modsPath);
  if (enableResult.success && enableResult.modified) {
    showToast('Script mods enabled in Options.ini', 'success');
  }

  await refreshInstalledMods();
  showView('mods');
}

// ── Mod Grid (Catalog) ─────────────────────────────────────────────────────

function renderModGrid() {
  const grid = document.getElementById('mod-grid');

  // Update path badge
  if (state.modsPath) {
    const shortPath = state.modsPath.replace(/^\/Users\/[^/]+/, '~');
    document.getElementById('mods-path-text').textContent = shortPath;
  }

  // Clear and rebuild using DOM methods for catalog data (all from local hardcoded catalog)
  grid.textContent = '';

  state.availableMods.forEach(mod => {
    const installed = state.installedMods[mod.id];
    const isInstalling = state.installing.has(mod.id);
    const icon = MOD_ICONS[mod.id] || { bg: 'rgba(255,255,255,0.05)', border: 'rgba(255,255,255,0.1)', wash: 'transparent' };

    const card = document.createElement('div');
    card.className = 'mod-card';
    card.style.setProperty('--card-accent', mod.color);
    card.style.setProperty('--card-wash', icon.wash || 'transparent');

    // Header
    const header = document.createElement('div');
    header.className = 'mod-card-header';

    const iconEl = document.createElement('div');
    iconEl.className = 'mod-card-icon';
    iconEl.style.background = icon.bg;
    iconEl.style.border = `1px solid ${icon.border}`;
    if (icon.svg) appendSVGIcon(iconEl, icon.svg);

    const titleGroup = document.createElement('div');
    titleGroup.className = 'mod-card-title-group';

    const nameEl = document.createElement('div');
    nameEl.className = 'mod-card-name';
    nameEl.textContent = mod.name;

    const versionEl = document.createElement('div');
    versionEl.className = 'mod-card-version';
    versionEl.textContent = `v${mod.version}`;

    titleGroup.appendChild(nameEl);
    titleGroup.appendChild(versionEl);
    header.appendChild(iconEl);
    header.appendChild(titleGroup);

    // Description
    const desc = document.createElement('div');
    desc.className = 'mod-card-desc';
    desc.textContent = mod.description;

    // Meta
    const meta = document.createElement('div');
    meta.className = 'mod-card-meta';

    const sizeSpan = document.createElement('span');
    sizeSpan.textContent = mod.size;

    meta.appendChild(sizeSpan);

    if (mod.hasScript) {
      const scriptSpan = document.createElement('span');
      scriptSpan.textContent = '\u26A1 Script mod';
      meta.appendChild(scriptSpan);
    }

    // Tags
    const tags = document.createElement('div');
    tags.className = 'mod-card-tags';
    mod.tags.forEach(t => {
      const tag = document.createElement('span');
      tag.className = 'tag';
      tag.textContent = t;
      tags.appendChild(tag);
    });

    // Footer
    const footer = document.createElement('div');
    footer.className = 'mod-card-footer';

    const status = document.createElement('div');
    status.className = `mod-status ${installed ? 'installed' : 'not-installed'}`;

    const dot = document.createElement('span');
    dot.className = 'status-dot';
    status.appendChild(dot);

    const statusText = document.createTextNode(installed ? ' Installed' : ' Not installed');
    status.appendChild(statusText);

    const btn = document.createElement('button');
    if (isInstalling) {
      btn.className = 'btn btn-secondary btn-sm';
      btn.disabled = true;
      btn.textContent = 'Installing...';
    } else if (installed) {
      btn.className = 'btn btn-danger btn-sm';
      btn.textContent = 'Uninstall';
      btn.addEventListener('click', () => uninstallMod(mod.id));
    } else {
      btn.className = 'btn btn-primary btn-sm';
      btn.textContent = 'Install';
      btn.addEventListener('click', () => installMod(mod.id));
    }

    footer.appendChild(status);
    footer.appendChild(btn);

    // Assemble card
    card.appendChild(header);
    card.appendChild(desc);
    card.appendChild(meta);
    card.appendChild(tags);
    card.appendChild(footer);

    // Progress bar
    if (isInstalling) {
      const progressContainer = document.createElement('div');
      progressContainer.className = 'progress-bar-container';

      const progressBar = document.createElement('div');
      progressBar.className = 'progress-bar';
      progressBar.id = `progress-${mod.id}`;
      progressBar.style.width = `${state.progress[mod.id] || 0}%`;

      progressContainer.appendChild(progressBar);
      card.appendChild(progressContainer);
    }

    grid.appendChild(card);
  });
}

function updateProgressBar(modId, progress) {
  const bar = document.getElementById(`progress-${modId}`);
  if (bar) {
    bar.style.width = `${Math.min(progress, 100)}%`;
  }
}

// ── Mod Operations ──────────────────────────────────────────────────────────

async function installMod(modId) {
  if (state.installing.has(modId)) return;

  state.installing.add(modId);
  state.progress[modId] = 0;
  renderModGrid();

  try {
    const result = await api.installMod(modId, state.modsPath);
    if (result.success) {
      showToast(`${getModName(modId)} installed successfully!`, 'success');
      await refreshInstalledMods();
    }
  } catch (err) {
    showToast(`Failed to install: ${err.message}`, 'error');
  } finally {
    state.installing.delete(modId);
    delete state.progress[modId];
    refreshCurrentView();
  }
}

async function uninstallMod(modId) {
  try {
    const result = await api.uninstallMod(modId, state.modsPath);
    if (result.success) {
      showToast(`${getModName(modId)} uninstalled`, 'info');
      await refreshInstalledMods();
      refreshCurrentView();
    }
  } catch (err) {
    showToast(`Failed to uninstall: ${err.message}`, 'error');
  }
}

async function refreshInstalledMods() {
  if (state.modsPath) {
    state.installedMods = await api.getInstalledMods(state.modsPath);
  }
}

function getModName(modId) {
  const mod = state.availableMods.find(m => m.id === modId);
  return mod ? mod.name : modId;
}

// ── Installed View ──────────────────────────────────────────────────────────

function renderInstalledList() {
  const list = document.getElementById('installed-list');
  const installed = Object.values(state.installedMods);

  list.textContent = '';

  if (installed.length === 0) {
    const emptyState = document.createElement('div');
    emptyState.className = 'empty-state';

    const emptyIcon = document.createElement('div');
    emptyIcon.textContent = '\u{1F4E6}';
    emptyIcon.style.fontSize = '48px';
    emptyIcon.style.opacity = '0.4';

    const emptyText = document.createElement('p');
    emptyText.textContent = 'No Stark Labs mods installed yet';

    const browseBtn = document.createElement('button');
    browseBtn.className = 'btn btn-primary';
    browseBtn.textContent = 'Browse Catalog';
    browseBtn.addEventListener('click', () => showView('mods'));

    emptyState.appendChild(emptyIcon);
    emptyState.appendChild(emptyText);
    emptyState.appendChild(browseBtn);
    list.appendChild(emptyState);
    return;
  }

  installed.forEach(mod => {
    const icon = MOD_ICONS[mod.id] || { bg: 'rgba(255,255,255,0.05)', border: 'rgba(255,255,255,0.1)' };

    const item = document.createElement('div');
    item.className = 'installed-item';

    const itemIcon = document.createElement('div');
    itemIcon.className = 'installed-item-icon';
    itemIcon.style.background = icon.bg;
    itemIcon.style.border = `1px solid ${icon.border}`;
    itemIcon.style.borderRadius = '8px';
    if (icon.svg) appendSVGIcon(itemIcon, icon.svg);

    const info = document.createElement('div');
    info.className = 'installed-item-info';

    const name = document.createElement('div');
    name.className = 'installed-item-name';
    name.textContent = mod.name;

    const version = document.createElement('div');
    version.className = 'installed-item-version';
    version.textContent = `v${mod.version}`;

    const files = document.createElement('div');
    files.className = 'installed-item-files';
    files.textContent = mod.installedFiles.join(', ');

    info.appendChild(name);
    info.appendChild(version);
    info.appendChild(files);

    const btn = document.createElement('button');
    btn.className = 'btn btn-danger btn-sm';
    btn.textContent = 'Uninstall';
    btn.addEventListener('click', () => uninstallMod(mod.id));

    item.appendChild(itemIcon);
    item.appendChild(info);
    item.appendChild(btn);
    list.appendChild(item);
  });
}

// ── Updates ─────────────────────────────────────────────────────────────────

async function checkUpdates() {
  const container = document.getElementById('updates-content');
  container.textContent = '';

  const checking = document.createElement('div');
  checking.className = 'checking-updates';

  const spinner = document.createElement('div');
  spinner.className = 'detect-spinner';

  const label = document.createElement('span');
  label.textContent = 'Checking for updates...';

  checking.appendChild(spinner);
  checking.appendChild(label);
  container.appendChild(checking);

  try {
    const updates = await api.checkModUpdates();
    const entries = Object.entries(updates);

    container.textContent = '';

    if (entries.length === 0) {
      const emptyState = document.createElement('div');
      emptyState.className = 'empty-state';

      const checkIcon = document.createElement('div');
      checkIcon.textContent = '\u2705';
      checkIcon.style.fontSize = '48px';
      checkIcon.style.opacity = '0.6';

      const msg = document.createElement('p');
      msg.textContent = 'All mods are up to date!';

      emptyState.appendChild(checkIcon);
      emptyState.appendChild(msg);
      container.appendChild(emptyState);
    } else {
      entries.forEach(([modId, info]) => {
        const mod = state.availableMods.find(m => m.id === modId);
        const modName = mod ? mod.name : modId;

        const card = document.createElement('div');
        card.className = 'update-card';

        const cardInfo = document.createElement('div');
        cardInfo.className = 'update-card-info';

        const cardName = document.createElement('div');
        cardName.className = 'update-card-name';
        cardName.textContent = modName;

        const versions = document.createElement('div');
        versions.className = 'update-card-versions';
        versions.textContent = `${info.current} \u2192 `;

        const newVer = document.createElement('span');
        newVer.className = 'new-version';
        newVer.textContent = info.latest;
        versions.appendChild(newVer);

        cardInfo.appendChild(cardName);
        cardInfo.appendChild(versions);

        const btn = document.createElement('button');
        btn.className = 'btn btn-primary btn-sm';
        btn.textContent = 'View Release';
        btn.addEventListener('click', () => api.openExternal(info.url));

        card.appendChild(cardInfo);
        card.appendChild(btn);
        container.appendChild(card);
      });
    }
  } catch (err) {
    container.textContent = '';
    const emptyState = document.createElement('div');
    emptyState.className = 'empty-state';
    const msg = document.createElement('p');
    msg.textContent = 'Could not check for updates. Are you online?';
    emptyState.appendChild(msg);
    container.appendChild(emptyState);
  }
}

// ── FAQ Accordion ───────────────────────────────────────────────────────────

function toggleFaq(button) {
  const item = button.parentElement;
  const isOpen = item.classList.contains('open');

  // Close all items
  document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));

  // Toggle the clicked one
  if (!isOpen) {
    item.classList.add('open');
  }
}

// ── Settings ────────────────────────────────────────────────────────────────

function refreshSettings() {
  if (state.modsPath) {
    document.getElementById('settings-mods-path').textContent = state.modsPath;
  }

  // Update persona selector active state
  const currentPersona = state.persona || localStorage.getItem('starkLabsPersona');
  document.querySelectorAll('.persona-option').forEach(opt => {
    opt.classList.toggle('active', opt.dataset.persona === currentPersona);
  });
}

async function setPersona(persona) {
  state.persona = persona;
  localStorage.setItem('starkLabsPersona', persona);
  await api.setSetting('persona', persona);

  // Update UI
  document.querySelectorAll('.persona-option').forEach(opt => {
    opt.classList.toggle('active', opt.dataset.persona === persona);
  });

  showToast(`Experience level set to ${persona === 'beginner' ? 'Casual' : persona === 'intermediate' ? 'Standard' : 'Power User'}`, 'success');
}

async function changeModsPath() {
  const result = await api.browseModsPath();
  if (result) {
    state.modsPath = result;
    await api.setSetting('modsPath', result);
    await refreshInstalledMods();
    refreshSettings();
    showToast('Mods folder updated', 'success');
  }
}

async function enableScripts() {
  if (!state.modsPath) {
    showToast('Set your Mods folder first', 'error');
    return;
  }
  const result = await api.enableScriptMods(state.modsPath);
  if (result.success) {
    if (result.alreadyEnabled) {
      showToast('Mod support already enabled!', 'info');
    } else {
      showToast('Mod support enabled in Options.ini', 'success');
    }
  } else {
    showToast(result.error || 'Failed to enable mod support', 'error');
  }
}

async function toggleAutoUpdate(enabled) {
  await api.setSetting('autoUpdate', enabled);
}

// ── Helpers ─────────────────────────────────────────────────────────────────

function openModsFolder() {
  if (state.modsPath) {
    api.openPath(state.modsPath);
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ── Toasts ──────────────────────────────────────────────────────────────────

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  const iconSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  iconSvg.setAttribute('class', 'toast-icon');
  iconSvg.setAttribute('viewBox', '0 0 24 24');
  iconSvg.setAttribute('fill', 'none');
  iconSvg.setAttribute('stroke-width', '2');

  const colors = { success: '#4ade80', error: '#f85149', info: '#58a6ff' };
  iconSvg.setAttribute('stroke', colors[type] || colors.info);

  const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  circle.setAttribute('cx', '12');
  circle.setAttribute('cy', '12');
  circle.setAttribute('r', '10');
  iconSvg.appendChild(circle);

  if (type === 'success') {
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', 'M9 12l2 2 4-4');
    iconSvg.appendChild(path);
  } else if (type === 'error') {
    const line1 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line1.setAttribute('x1', '15'); line1.setAttribute('y1', '9');
    line1.setAttribute('x2', '9'); line1.setAttribute('y2', '15');
    const line2 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line2.setAttribute('x1', '9'); line2.setAttribute('y1', '9');
    line2.setAttribute('x2', '15'); line2.setAttribute('y2', '15');
    iconSvg.appendChild(line1);
    iconSvg.appendChild(line2);
  } else {
    const line1 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line1.setAttribute('x1', '12'); line1.setAttribute('y1', '16');
    line1.setAttribute('x2', '12'); line1.setAttribute('y2', '12');
    const line2 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line2.setAttribute('x1', '12'); line2.setAttribute('y1', '8');
    line2.setAttribute('x2', '12.01'); line2.setAttribute('y2', '8');
    iconSvg.appendChild(line1);
    iconSvg.appendChild(line2);
  }

  const span = document.createElement('span');
  span.textContent = message;

  toast.appendChild(iconSvg);
  toast.appendChild(span);
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'fadeOut 300ms ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
