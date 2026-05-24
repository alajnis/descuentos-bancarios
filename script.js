/**
 * PORTAL DESCUENTOS BANCARIOS — ARGENTINA
 * script.js · Versión 1.0
 *
 * Estructura:
 *  1. CONFIG & STATE
 *  2. DATA LOADER
 *  3. FILTERS ENGINE
 *  4. CALENDAR RENDERER
 *  5. CARDS RENDERER
 *  6. PAGINATION ENGINE
 *  7. SIDEBAR TOGGLE (mobile)
 *  8. EVENT LISTENERS
 *  9. INIT
 */

'use strict';

/* ============================================================
   1. CONFIG & STATE
   ============================================================ */
const CONFIG = {
  ITEMS_PER_PAGE: 12,
  DATA_URL: 'data.json',
  DAYS_ORDER: ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'],
  DAYS_SHORT:  ['Lun',  'Mar',   'Mié',      'Jue',   'Vie',    'Sáb',   'Dom'],
  DAYS_FULL:   ['Lunes','Martes','Miércoles', 'Jueves','Viernes','Sábado','Domingo'],
};

/** Color accent por banco (debe matchear las CSS vars) */
const BANK_COLORS = {
  'Santander':   '#ec0000',
  'BBVA':        '#004481',
  'Galicia':     '#c8102e',
  'Itaú':        '#ec7000',
  'Banco Nación':'#003082',
  'Banco Macro': '#f5a800',
  'Supervielle': '#00a0df',
  'Credicoop':   '#009640',
  'ICBC':        '#c0272d',
  'MercadoPago': '#009ee3',
  'Modo':        '#201f3b',
};

/** Gradientes por banco para la card */
const BANK_GRADIENTS = {
  'Santander':   'linear-gradient(135deg, #ec0000, #ff5252)',
  'BBVA':        'linear-gradient(135deg, #004481, #1a73e8)',
  'Galicia':     'linear-gradient(135deg, #c8102e, #e53935)',
  'Itaú':        'linear-gradient(135deg, #ec7000, #ffa040)',
  'Banco Nación':'linear-gradient(135deg, #003082, #0044cc)',
  'Banco Macro': 'linear-gradient(135deg, #f5a800, #ffcc44)',
  'Supervielle': 'linear-gradient(135deg, #00a0df, #40c4ff)',
  'Credicoop':   'linear-gradient(135deg, #009640, #43a047)',
  'ICBC':        'linear-gradient(135deg, #c0272d, #e53935)',
  'MercadoPago': 'linear-gradient(135deg, #009ee3, #00bcd4)',
  'Modo':        'linear-gradient(135deg, #201f3b, #5c6bc0)',
};

const state = {
  allData:     [],       // todos los descuentos del JSON
  filtered:    [],       // descuentos tras aplicar filtros
  currentPage: 1,
  totalPages:  1,
  filters: {
    bancos:   [],
    rango:    '',
    metodos:  [],
    dias:     [],
  },
  sort: 'porcentaje_desc',
};

/* ============================================================
   2. DATA LOADER
   ============================================================ */
async function loadData() {
  try {
    showSkeletons();
    const res = await fetch(CONFIG.DATA_URL);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const json = await res.json();

    // Validación básica de estructura
    if (!json || !Array.isArray(json.descuentos)) {
      throw new Error('data.json inválido: falta la clave "descuentos" o no es un array.');
    }

    // Validar campos obligatorios en cada entrada
    const requiredFields = ['id','banco','metodo_pago','comercio','porcentaje','dias_vigencia','fecha_fin'];
    json.descuentos.forEach((d, i) => {
      requiredFields.forEach(field => {
        if (d[field] === undefined || d[field] === null) {
          console.warn(`[data.json] Descuento #${i+1} (id:${d.id}) le falta el campo "${field}".`);
        }
      });
    });

    state.allData = json.descuentos;
    state.filtered = [...state.allData];

    updateBankCounts();
    renderCalendar();
    applyFilters();
    updateLastUpdated();
    updateFooterYear();

  } catch (err) {
    showError(err.message);
    console.error('[Portal Descuentos]', err);
  }
}

/* ============================================================
   3. FILTERS ENGINE
   ============================================================ */

/** Lee el estado actual de todos los controles de filtro */
function readFilters() {
  state.filters.bancos  = getCheckedValues('banco');
  state.filters.rango   = getRadioValue('rango');
  state.filters.metodos = getCheckedValues('metodo');
  state.filters.dias    = getCheckedValues('dia');
}

function getCheckedValues(name) {
  return Array.from(document.querySelectorAll(`input[name="${name}"]:checked`))
    .map(el => el.value);
}

function getRadioValue(name) {
  const el = document.querySelector(`input[name="${name}"]:checked`);
  return el ? el.value : '';
}

/** Aplica filtros al allData y actualiza state.filtered */
function applyFilters() {
  readFilters();

  let result = state.allData.filter(d => {
    // --- Bancos (OR) ---
    if (state.filters.bancos.length > 0) {
      if (!state.filters.bancos.includes(d.banco)) return false;
    }

    // --- Rango de descuento ---
    if (state.filters.rango) {
      const pct = d.porcentaje;
      switch (state.filters.rango) {
        case '0-10':  if (pct > 10)  return false; break;
        case '10-25': if (pct <= 10 || pct > 25) return false; break;
        case '25-50': if (pct <= 25 || pct > 50) return false; break;
        case '50+':   if (pct <= 50) return false; break;
      }
    }

    // --- Métodos de pago (OR) ---
    if (state.filters.metodos.length > 0) {
      if (!state.filters.metodos.includes(d.metodo_pago)) return false;
    }

    // --- Días (OR) ---
    if (state.filters.dias.length > 0) {
      const diasNorm = normalizeDays(d.dias_vigencia);
      const hasMatch = state.filters.dias.some(dia => diasNorm.includes(dia));
      if (!hasMatch) return false;
    }

    return true;
  });

  // Ordenamiento
  result = sortData(result, state.sort);

  state.filtered = result;
  state.currentPage = 1;

  renderResults();
  updateFilterCounts();
}

/** Normaliza el array dias_vigencia, expandiendo "todos" a todos los días */
function normalizeDays(dias) {
  if (!Array.isArray(dias)) return [];
  const todosExpanded = CONFIG.DAYS_ORDER;
  return dias.flatMap(d => {
    const lower = d.toLowerCase().trim();
    return lower === 'todos' ? todosExpanded : [lower];
  });
}

/** Ordena los datos según criterio */
function sortData(data, criterion) {
  return [...data].sort((a, b) => {
    switch (criterion) {
      case 'porcentaje_desc': return b.porcentaje - a.porcentaje;
      case 'porcentaje_asc':  return a.porcentaje - b.porcentaje;
      case 'fecha_fin_asc':   return new Date(a.fecha_fin) - new Date(b.fecha_fin);
      default: return 0;
    }
  });
}

/** Actualiza los contadores junto a cada banco en el sidebar */
function updateBankCounts() {
  const bankList = ['Santander','BBVA','Galicia','Itaú','Banco Nación','Banco Macro',
                    'Supervielle','Credicoop','ICBC','MercadoPago','Modo'];
  const idMap = {
    'Santander':   'count-banco-santander',
    'BBVA':        'count-banco-bbva',
    'Galicia':     'count-banco-galicia',
    'Itaú':        'count-banco-itau',
    'Banco Nación':'count-banco-nacion',
    'Banco Macro': 'count-banco-macro',
    'Supervielle': 'count-banco-supervielle',
    'Credicoop':   'count-banco-credicoop',
    'ICBC':        'count-banco-icbc',
    'MercadoPago': 'count-banco-mercadopago',
    'Modo':        'count-banco-modo',
  };
  bankList.forEach(banco => {
    const count = state.allData.filter(d => d.banco === banco).length;
    const el = document.getElementById(idMap[banco]);
    if (el) el.textContent = count;
  });
}

/** Actualiza contadores de filtros según los resultados actuales */
function updateFilterCounts() {
  // No recomputamos los bank counts dinámicamente, solo indicamos si hay filtros activos
  const hasActive = state.filters.bancos.length > 0 ||
                    state.filters.rango !== '' ||
                    state.filters.metodos.length > 0 ||
                    state.filters.dias.length > 0;

  const btnClear = document.getElementById('btnClearFilters');
  if (btnClear) {
    btnClear.style.opacity = hasActive ? '1' : '0.5';
    btnClear.style.pointerEvents = hasActive ? 'auto' : 'none';
  }
}

/** Limpia todos los filtros */
function clearFilters() {
  document.querySelectorAll('input[name="banco"], input[name="metodo"], input[name="dia"]')
    .forEach(el => { el.checked = false; });
  const todosRadio = document.querySelector('input[name="rango"][value=""]');
  if (todosRadio) todosRadio.checked = true;
  applyFilters();
}

/* ============================================================
   4. CALENDAR RENDERER
   ============================================================ */
function renderCalendar() {
  const container = document.getElementById('calendarGrid');
  if (!container) return;

  const today = new Date();
  const todayDayIndex = (today.getDay() + 6) % 7; // 0=Lunes

  // Contar promos por día
  const countsByDay = CONFIG.DAYS_ORDER.map(day =>
    state.allData.filter(d => normalizeDays(d.dias_vigencia).includes(day)).length
  );
  const maxCount = Math.max(...countsByDay);

  container.innerHTML = CONFIG.DAYS_ORDER.map((day, i) => {
    const isToday = i === todayDayIndex;
    const isTopDay = countsByDay[i] === maxCount && maxCount > 0;
    const classes = ['calendar-day', isToday ? 'today' : '', isTopDay ? 'top-day' : ''].filter(Boolean).join(' ');

    return `
      <div class="${classes}" role="listitem" aria-label="${CONFIG.DAYS_FULL[i]}: ${countsByDay[i]} descuentos">
        ${isToday ? '<span class="calendar-today-badge">Hoy</span>' : ''}
        <span class="calendar-day-name">${CONFIG.DAYS_SHORT[i]}</span>
        <span class="calendar-day-count">${countsByDay[i]}</span>
        <span class="calendar-day-label">promos</span>
      </div>
    `;
  }).join('');
}

/* ============================================================
   5. CARDS RENDERER
   ============================================================ */

/** Formatea fecha DD/MM/YYYY */
function formatDate(isoStr) {
  if (!isoStr) return '—';
  const [y, m, d] = isoStr.split('-');
  return `${d}/${m}/${y}`;
}

/** Formatea pesos con separador de miles */
function formatPesos(num) {
  if (!num) return null;
  return `$${Number(num).toLocaleString('es-AR')}`;
}

/** Genera los chips de días para la card */
function renderDayChips(diasVigencia) {
  const normalized = normalizeDays(diasVigencia);
  const isAllDays = CONFIG.DAYS_ORDER.every(d => normalized.includes(d));

  if (isAllDays) {
    return `<span class="day-chip all-days">Todos los días</span>`;
  }

  const today = new Date();
  const todayIndex = (today.getDay() + 6) % 7;
  const todayName = CONFIG.DAYS_ORDER[todayIndex];

  return CONFIG.DAYS_ORDER
    .filter(d => normalized.includes(d))
    .map(d => {
      const isToday = d === todayName;
      return `<span class="day-chip ${isToday ? 'today-chip' : ''}" title="${d}">${d.charAt(0).toUpperCase() + d.slice(1, 3)}</span>`;
    }).join('');
}

/** Genera el fallback del logo si la imagen falla */
function getBankInitials(banco) {
  return banco.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase();
}

/** Construye el HTML de una card */
function buildCardHTML(d, index) {
  const bankColor    = BANK_COLORS[d.banco]    || '#2d6ef6';
  const bankGradient = BANK_GRADIENTS[d.banco] || 'linear-gradient(135deg, #2d6ef6, #7c3aed)';
  const initials     = getBankInitials(d.banco);
  const logoId       = `logo-${d.id}`;
  const tope         = formatPesos(d.tope_reintegro);
  const metodoFull   = d.tarjeta_marca ? `${d.metodo_pago} · ${d.tarjeta_marca}` : d.metodo_pago;

  // Animación con delay escalonado
  const delay = (index % CONFIG.ITEMS_PER_PAGE) * 40;

  return `
    <article class="discount-card" role="listitem"
             style="--card-accent-color: ${bankGradient}; animation-delay: ${delay}ms;">

      <!-- HEADER -->
      <div class="card-header">
        <div class="card-bank-info">
          <div class="card-logo-wrapper">
            ${d.logo_url
              ? `<img id="${logoId}" src="${d.logo_url}" alt="Logo ${d.banco}"
                      loading="lazy"
                      onerror="this.style.display='none'; this.parentElement.querySelector('.card-logo-fallback').style.display='flex';" />`
              : ''}
            <div class="card-logo-fallback" style="background:${bankColor}; display:${d.logo_url ? 'none' : 'flex'};">
              ${initials}
            </div>
          </div>
          <div>
            <div class="card-bank-name">${d.banco}</div>
            <div class="card-method">${metodoFull}</div>
          </div>
        </div>

        <div class="card-discount-badge" style="background: ${bankGradient};">
          <span class="card-discount-number">${d.porcentaje}</span>
          <span class="card-discount-percent">% OFF</span>
        </div>
      </div>

      <!-- BODY -->
      <div class="card-body">
        <div class="card-commerce">
          <span class="card-commerce-name">${d.comercio}</span>
          <span class="card-category-badge">${d.categoria || ''}</span>
        </div>

        <div class="card-meta">
          ${tope ? `
          <div class="card-meta-row">
            <span class="card-meta-icon">🏷️</span>
            <span>Tope de reintegro: <strong>${tope}</strong></span>
          </div>` : `
          <div class="card-meta-row">
            <span class="card-meta-icon">✨</span>
            <span style="color:var(--color-success); font-weight:600;">Sin tope de reintegro</span>
          </div>`}
        </div>

        <div class="card-days">
          ${renderDayChips(d.dias_vigencia)}
        </div>
      </div>

      <!-- FOOTER -->
      <div class="card-footer">
        <div class="card-vigencia">
          📅 Vigente hasta <span>${formatDate(d.fecha_fin)}</span>
        </div>
        <a href="${d.link_detalle || '#'}"
           target="_blank"
           rel="noopener noreferrer"
           class="btn-ver-detalle"
           aria-label="Ver detalle de ${d.porcentaje}% en ${d.comercio} con ${d.banco}">
          Ver detalle
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
        </a>
      </div>

    </article>
  `;
}

/** Renderiza las cards de la página actual */
function renderCards() {
  const container = document.getElementById('cardsGrid');
  const emptyState = document.getElementById('emptyState');
  const pagination = document.getElementById('paginationContainer');

  if (!container) return;

  if (state.filtered.length === 0) {
    container.innerHTML = '';
    emptyState.hidden = false;
    pagination.hidden = true;
    return;
  }

  emptyState.hidden = true;
  pagination.hidden = false;

  const start = (state.currentPage - 1) * CONFIG.ITEMS_PER_PAGE;
  const end   = start + CONFIG.ITEMS_PER_PAGE;
  const page  = state.filtered.slice(start, end);

  container.innerHTML = page.map((d, i) => buildCardHTML(d, i)).join('');
}

/** Actualiza el contador de resultados */
function renderResultsCount() {
  const el = document.getElementById('resultsCount');
  if (!el) return;
  const start = (state.currentPage - 1) * CONFIG.ITEMS_PER_PAGE + 1;
  const end   = Math.min(state.currentPage * CONFIG.ITEMS_PER_PAGE, state.filtered.length);
  const total = state.filtered.length;

  if (total === 0) {
    el.innerHTML = 'Sin resultados';
  } else {
    el.innerHTML = `Mostrando <strong>${start}–${end}</strong> de <strong>${total}</strong> descuentos`;
  }
}

/* ============================================================
   6. PAGINATION ENGINE
   ============================================================ */
function renderPagination() {
  state.totalPages = Math.ceil(state.filtered.length / CONFIG.ITEMS_PER_PAGE);
  const cp = state.currentPage;
  const tp = state.totalPages;

  const btnPrev = document.getElementById('btnPrev');
  const btnNext = document.getElementById('btnNext');
  const pages   = document.getElementById('paginationPages');

  if (!btnPrev || !btnNext || !pages) return;

  btnPrev.disabled = cp <= 1;
  btnNext.disabled = cp >= tp;

  // Generar botones de página con elipsis
  pages.innerHTML = buildPageButtons(cp, tp);
}

function buildPageButtons(cp, tp) {
  if (tp <= 1) return '';
  const buttons = [];

  const range = (start, end) => {
    const arr = [];
    for (let i = start; i <= end; i++) arr.push(i);
    return arr;
  };

  let pagesToShow = [];
  if (tp <= 7) {
    pagesToShow = range(1, tp);
  } else {
    if (cp <= 4) {
      pagesToShow = [...range(1, 5), '...', tp];
    } else if (cp >= tp - 3) {
      pagesToShow = [1, '...', ...range(tp - 4, tp)];
    } else {
      pagesToShow = [1, '...', cp - 1, cp, cp + 1, '...', tp];
    }
  }

  return pagesToShow.map(p => {
    if (p === '...') return `<span class="page-ellipsis" role="separator">…</span>`;
    return `<button class="page-btn ${p === cp ? 'active' : ''}"
                    onclick="goToPage(${p})"
                    aria-label="Página ${p}"
                    aria-current="${p === cp ? 'page' : 'false'}"
                    role="listitem">${p}</button>`;
  }).join('');
}

function goToPage(page) {
  state.currentPage = page;
  renderResults();
  // Scroll suave al inicio del grid
  document.getElementById('cardsGrid')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/** Renderiza todo el bloque de resultados */
function renderResults() {
  renderCards();
  renderPagination();
  renderResultsCount();
}

/* ============================================================
   7. SIDEBAR TOGGLE (mobile)
   ============================================================ */
function openSidebar() {
  const sidebar  = document.getElementById('sidebar');
  const overlay  = document.getElementById('sidebarOverlay');
  const btnOpen  = document.getElementById('btnMobileFilters');

  sidebar.classList.add('open');
  overlay.classList.add('visible');
  btnOpen.setAttribute('aria-expanded', 'true');
  document.body.style.overflow = 'hidden';
}

function closeSidebar() {
  const sidebar  = document.getElementById('sidebar');
  const overlay  = document.getElementById('sidebarOverlay');
  const btnOpen  = document.getElementById('btnMobileFilters');

  sidebar.classList.remove('open');
  overlay.classList.remove('visible');
  btnOpen.setAttribute('aria-expanded', 'false');
  document.body.style.overflow = '';
}

/* ============================================================
   8. HELPERS / UI
   ============================================================ */
function showSkeletons() {
  const container = document.getElementById('cardsGrid');
  if (!container) return;
  const count = 6;
  container.innerHTML = Array.from({ length: count }, () =>
    `<div class="skeleton skeleton-card" role="presentation"></div>`
  ).join('');
}

function showError(message) {
  const container = document.getElementById('cardsGrid');
  if (!container) return;
  container.innerHTML = `
    <div style="grid-column:1/-1; text-align:center; padding:3rem; color:var(--color-danger);">
      <div style="font-size:2.5rem; margin-bottom:1rem;">⚠️</div>
      <h3 style="margin-bottom:.5rem;">Error al cargar los datos</h3>
      <p style="color:var(--color-text-secondary); font-size:.9rem;">${escapeHTML(message)}</p>
      <p style="color:var(--color-text-muted); font-size:.8rem; margin-top:1rem;">
        Verificá que el archivo <code>data.json</code> existe y es válido, y que estás abriendo la página a través de un servidor local.
      </p>
    </div>
  `;
}

function escapeHTML(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function updateLastUpdated() {
  const el = document.getElementById('lastUpdated');
  if (!el) return;

  const dates = state.allData
    .map(d => d.ultima_actualizacion ? new Date(d.ultima_actualizacion) : null)
    .filter(Boolean);

  if (dates.length === 0) {
    el.textContent = 'Sin fecha';
    return;
  }

  const latest = new Date(Math.max(...dates));
  el.textContent = `Actualizado: ${latest.toLocaleDateString('es-AR', {
    day:'2-digit', month:'2-digit', year:'numeric'
  })}`;
}

function updateFooterYear() {
  const el = document.getElementById('footerYear');
  if (el) el.textContent = new Date().getFullYear();
}

/* ─── Accordion de grupos de filtros ─── */
function toggleFilterGroup(btn) {
  const target = document.getElementById(btn.getAttribute('aria-controls'));
  if (!target) return;
  const isExpanded = btn.getAttribute('aria-expanded') === 'true';
  btn.setAttribute('aria-expanded', String(!isExpanded));
  target.classList.toggle('collapsed', isExpanded);
}

/* ============================================================
   9. EVENT LISTENERS
   ============================================================ */
function bindEvents() {
  // Filtros: cualquier cambio en checkbox o radio
  document.querySelectorAll('input[name="banco"], input[name="rango"], input[name="metodo"], input[name="dia"]')
    .forEach(el => el.addEventListener('change', applyFilters));

  // Limpiar filtros
  document.getElementById('btnClearFilters')?.addEventListener('click', clearFilters);
  document.getElementById('btnClearFiltersEmpty')?.addEventListener('click', clearFilters);

  // Ordenamiento
  document.getElementById('sortSelect')?.addEventListener('change', e => {
    state.sort = e.target.value;
    state.filtered = sortData(state.filtered, state.sort);
    state.currentPage = 1;
    renderResults();
  });

  // Paginación: anterior / siguiente
  document.getElementById('btnPrev')?.addEventListener('click', () => {
    if (state.currentPage > 1) goToPage(state.currentPage - 1);
  });
  document.getElementById('btnNext')?.addEventListener('click', () => {
    if (state.currentPage < state.totalPages) goToPage(state.currentPage + 1);
  });

  // Mobile sidebar
  document.getElementById('btnMobileFilters')?.addEventListener('click', openSidebar);
  document.getElementById('btnCloseSidebar')?.addEventListener('click', closeSidebar);
  document.getElementById('sidebarOverlay')?.addEventListener('click', closeSidebar);

  // Cerrar sidebar con ESC
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeSidebar();
  });

  // Accordion de grupos de filtros
  document.querySelectorAll('.filter-group-header').forEach(btn => {
    btn.addEventListener('click', () => toggleFilterGroup(btn));
  });

  // Cerrar sidebar si el ancho cambia a desktop
  window.addEventListener('resize', () => {
    if (window.innerWidth > 768) closeSidebar();
  });
}

/* ============================================================
   INIT
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {
  // Inicializar radio "Todos" como seleccionado
  const todosRadio = document.querySelector('input[name="rango"][value=""]');
  if (todosRadio) todosRadio.checked = true;

  bindEvents();
  loadData();
});

// Exponer goToPage globalmente (usado en innerHTML onclick)
window.goToPage = goToPage;
