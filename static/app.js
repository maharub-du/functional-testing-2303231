/**
 * Functional Testing Dashboard — Client Logic
 * Handles: function execution via /api/execute, health polling,
 * result rendering, input parsing, search, and category filtering.
 */

// ---- Stats tracking ----
let stats = { total: 0, success: 0, error: 0 };

function updateStats() {
    document.getElementById('totalExecutions').textContent = stats.total;
    document.getElementById('successCount').textContent = stats.success;
    document.getElementById('errorCount').textContent = stats.error;
}

// ---- Input Parsers ----
function parseNum(val) {
    const trimmed = String(val).trim();
    const n = Number(trimmed);
    if (trimmed === '' || isNaN(n)) {
        throw new Error(`Expected a valid number, got: "${val}"`);
    }
    return Number.isInteger(n) ? n : n;
}

function parseNumList(val) {
    const trimmed = String(val).trim();
    if (trimmed === '') return [];
    return trimmed.split(',').map(s => {
        const item = s.trim();
        const n = Number(item);
        if (isNaN(n)) throw new Error(`Invalid number in list: "${item}"`);
        return n;
    });
}

function parseBool(val) {
    const t = String(val).trim().toLowerCase();
    if (t === 'true') return true;
    if (t === 'false') return false;
    throw new Error(`Expected true or false, got: "${val}"`);
}

// ---- Result Rendering ----
function showResult(funcName, data, durationMs = null) {
    const box = document.getElementById(`result-${funcName}`);
    const card = document.getElementById(`card-${funcName}`);
    stats.total++;

    const latencyText = durationMs !== null ? `${Math.round(durationMs)}ms` : '';

    if (data.success) {
        stats.success++;
        let displayVal = JSON.stringify(data.result);
        const typeName = typeof data.result === 'object' && Array.isArray(data.result)
            ? 'list'
            : typeof data.result;

        if (typeof data.result === 'object' && data.result !== null) {
            displayVal = JSON.stringify(data.result, null, 2);
        }

        box.innerHTML = `
            <div class="result-content result-success">
                <span class="result-label">Result (${typeName})</span>
                <span class="result-value">${escapeHtml(String(displayVal))}</span>
                ${latencyText ? `<div class="result-meta">Latency: ${latencyText} &bull; HTTP 200</div>` : ''}
            </div>
        `;
        card.style.borderColor = 'var(--success-border)';
    } else {
        stats.error++;
        box.innerHTML = `
            <div class="result-content result-error">
                <span class="result-label">${escapeHtml(data.type || 'Error')}</span>
                <span class="result-value">${escapeHtml(data.error)}</span>
                ${latencyText ? `<div class="result-meta">Caught &bull; ${latencyText}</div>` : ''}
            </div>
        `;
        card.style.borderColor = 'var(--error-border)';
    }

    updateStats();

    setTimeout(() => {
        card.style.borderColor = '';
    }, 2500);
}

function showClientError(funcName, message) {
    const box = document.getElementById(`result-${funcName}`);
    stats.total++;
    stats.error++;
    box.innerHTML = `
        <div class="result-content result-error">
            <span class="result-label">Validation Error</span>
            <span class="result-value">${escapeHtml(message)}</span>
        </div>
    `;
    updateStats();
}

function showLoading(funcName) {
    const box = document.getElementById(`result-${funcName}`);
    box.innerHTML = `
        <div class="result-content" style="background-color: var(--bg-subtle); color: var(--text-muted);">
            <span class="result-value"><span class="loading-spinner"></span> Executing...</span>
        </div>
    `;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}

// ---- Generic Function Execution ----
async function runFunction(funcName, inputIds, parsers) {
    showLoading(funcName);
    const start = performance.now();

    try {
        const args = inputIds.map((id, i) => {
            const el = document.getElementById(id);
            return parsers[i](el ? el.value : '');
        });

        const resp = await fetch('/api/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ function: funcName, args }),
        });

        const data = await resp.json();
        const duration = performance.now() - start;
        showResult(funcName, data, duration);
    } catch (err) {
        showClientError(funcName, err.message);
    }
}

// ---- Specialized Function Runners ----

async function runGreet() {
    showLoading('greet');
    const start = performance.now();
    try {
        const val = document.getElementById('input-greet').value;
        const args = val.trim() === '' ? [null] : [val];
        const resp = await fetch('/api/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ function: 'greet', args }),
        });
        const data = await resp.json();
        showResult('greet', data, performance.now() - start);
    } catch (err) {
        showClientError('greet', err.message);
    }
}

async function runGetPrice() {
    showLoading('get_price');
    const start = performance.now();
    try {
        const dictStr = document.getElementById('input-get_price_dict').value;
        const item = document.getElementById('input-get_price_item').value.trim();
        const prices = JSON.parse(dictStr);
        const resp = await fetch('/api/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ function: 'get_price', args: [prices, item] }),
        });
        const data = await resp.json();
        showResult('get_price', data, performance.now() - start);
    } catch (err) {
        showClientError('get_price', err.message);
    }
}

async function runCommonItems() {
    showLoading('common_items');
    const start = performance.now();
    try {
        const a = parseNumList(document.getElementById('input-common_items_a').value);
        const b = parseNumList(document.getElementById('input-common_items_b').value);
        const resp = await fetch('/api/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ function: 'common_items', args: [a, b] }),
        });
        const data = await resp.json();
        showResult('common_items', data, performance.now() - start);
    } catch (err) {
        showClientError('common_items', err.message);
    }
}

async function runToInt() {
    showLoading('to_int');
    const start = performance.now();
    try {
        const raw = document.getElementById('input-to_int').value.trim();
        let val;
        if (raw.toLowerCase() === 'true') val = true;
        else if (raw.toLowerCase() === 'false') val = false;
        else if (!isNaN(Number(raw)) && raw !== '') val = Number(raw);
        else val = raw;

        const resp = await fetch('/api/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ function: 'to_int', args: [val] }),
        });
        const data = await resp.json();
        showResult('to_int', data, performance.now() - start);
    } catch (err) {
        showClientError('to_int', err.message);
    }
}

// ---- Quick Fill & Run Helpers ----
function fillAndRun(funcName, value) {
    const input = document.getElementById(`input-${funcName}`);
    if (input) input.value = value;

    const card = document.getElementById(`card-${funcName}`);
    const runBtn = card ? card.querySelector('.btn-run') : null;
    if (runBtn) runBtn.click();
}

function fillAndRunGreet(value) {
    document.getElementById('input-greet').value = value;
    runGreet();
}

function fillAndRunToInt(value) {
    document.getElementById('input-to_int').value = value;
    runToInt();
}

// ---- Search & Filter Helpers ----
let currentCategory = 'all';

function setCategoryFilter(category, buttonElement) {
    currentCategory = category;
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    if (buttonElement) buttonElement.classList.add('active');
    applyFilters();
}

function handleSearch() {
    applyFilters();
}

function applyFilters() {
    const query = (document.getElementById('searchInput').value || '').toLowerCase().trim();
    const cards = document.querySelectorAll('.func-card');

    let visibleDataCount = 0;
    let visibleMathCount = 0;

    cards.forEach(card => {
        const cat = card.getAttribute('data-category');
        const name = (card.getAttribute('data-name') || '').toLowerCase();
        const text = card.textContent.toLowerCase();

        const matchesCategory = currentCategory === 'all' || cat === currentCategory;
        const matchesQuery = query === '' || name.includes(query) || text.includes(query);

        if (matchesCategory && matchesQuery) {
            card.style.display = '';
            if (cat === 'data') visibleDataCount++;
            if (cat === 'math') visibleMathCount++;
        } else {
            card.style.display = 'none';
        }
    });

    const dataSection = document.getElementById('section-data');
    const mathSection = document.getElementById('section-math');

    if (dataSection) {
        dataSection.style.display = visibleDataCount > 0 ? '' : 'none';
    }
    if (mathSection) {
        mathSection.style.display = visibleMathCount > 0 ? '' : 'none';
    }
}

// ---- Batch Quick Verification ----
async function runQuickVerification() {
    const runButtons = document.querySelectorAll('.func-card:not([style*="display: none"]) .btn-run');
    for (const btn of runButtons) {
        btn.click();
        await new Promise(r => setTimeout(r, 60));
    }
}

// ---- Health Check ----
async function checkHealth() {
    const badge = document.getElementById('healthBadge');
    const text = badge.querySelector('.health-text');
    const footerDot = document.getElementById('footerDot');
    const footerStatus = document.getElementById('footerStatus');

    try {
        const resp = await fetch('/health');
        const data = await resp.json();

        badge.className = 'health-badge online';
        text.textContent = `Online • ${data.commit.substring(0, 8)}`;
        footerDot.className = 'footer-dot online';
        footerStatus.textContent = `Service healthy • ${data.commit}`;

        const commitEl = document.getElementById('commitSha');
        if (commitEl) commitEl.textContent = data.commit;
    } catch (err) {
        badge.className = 'health-badge offline';
        text.textContent = 'API Offline';
        footerDot.className = 'footer-dot offline';
        footerStatus.textContent = 'API unreachable';
    }
}

// ---- Init & Keyboard Shortcuts ----
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    setInterval(checkHealth, 30000);

    // Allow pressing Enter in any card input to trigger its Run button
    document.querySelectorAll('.func-card input').forEach(input => {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const card = input.closest('.func-card');
                if (card) {
                    const btn = card.querySelector('.btn-run');
                    if (btn) btn.click();
                }
            }
        });
    });
});
