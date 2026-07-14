/* Reusable shell: each medicine database supplies only its title, source page and links. */
(() => {
  'use strict';
  const config = window.MEDICINE_EXPLORER_CONFIG;
  const $ = (selector) => document.querySelector(selector);
  const result = $('#medicineExplorerResult');
  const state = { mode: 'indication', indication: '', ingredient: '', search: '', page: 1, filters: {} };
  let data, products, ingredientByName, indicationByName;
  const esc = (value = '') => String(value).replace(/[&<>'"]/g, (character) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[character]));
  const unique = (items) => [...new Set(items.filter(Boolean))];
  const sorted = (items) => [...items].sort((a, b) => String(a).localeCompare(String(b), 'en'));
  const optionList = (items, selected, placeholder) => `<option value="">${esc(placeholder)}</option>${sorted(items).map((item) => `<option value="${esc(item)}"${item === selected ? ' selected' : ''}>${esc(item)}</option>`).join('')}`;

  function setupDatabaseSwitcher() {
    const select = $('#databaseSelect');
    select.innerHTML = config.databases.map((database) => `<option value="${esc(database.href)}"${database.name === config.databaseName ? ' selected' : ''}>${esc(database.name)}</option>`).join('');
    select.addEventListener('change', () => { window.location.href = select.value; });
  }

  async function loadData() {
    const response = await fetch(config.sourcePage, { cache: 'no-cache' });
    if (!response.ok) throw new Error(`無法載入資料（${response.status}）`);
    const source = await response.text();
    const match = source.match(/window\.EXPLORER_DATA=(\{[\s\S]*?\});\s*\nconst /);
    if (!match) throw new Error('找不到既有外用藥膏資料。');
    data = JSON.parse(match[1]);
    products = Object.entries(data.products).map(([license, product]) => ({ ...product, license }));
    ingredientByName = new Map(data.ingredients.map((ingredient) => [ingredient.ingredient, ingredient]));
    indicationByName = new Map(data.indications.map((indication) => [indication.displayName, indication]));
  }

  function renderModeButtons() {
    const modes = [{id:'indication',label:'依適應症'},{id:'ingredient',label:'依成分'},{id:'product',label:'搜尋產品'}];
    $('#modeButtons').innerHTML = modes.map((mode) => `<button type="button" class="me-button" data-mode="${mode.id}" aria-pressed="${state.mode === mode.id}">${mode.label}</button>`).join('');
    $('#modeButtons').querySelectorAll('button').forEach((button) => button.addEventListener('click', () => {
      state.mode = button.dataset.mode; state.page = 1; render();
    }));
  }

  function renderPrimaryControl() {
    const box = $('#primaryControl');
    if (state.mode === 'indication') {
      box.innerHTML = `<label for="primarySelect">適應症</label><select id="primarySelect">${optionList(data.indications.map((item) => item.displayName), state.indication, '請選擇適應症')}</select>`;
      $('#primarySelect').addEventListener('change', (event) => { state.indication = event.target.value; state.ingredient = ''; state.page = 1; render(); });
    } else if (state.mode === 'ingredient') {
      box.innerHTML = `<label for="primarySelect">有效成分</label><select id="primarySelect">${optionList(data.ingredients.map((item) => item.ingredient), state.ingredient, '請選擇有效成分')}</select>`;
      $('#primarySelect').addEventListener('change', (event) => { state.ingredient = event.target.value; state.indication = ''; state.page = 1; render(); });
    } else {
      box.innerHTML = `<label for="productSearch">搜尋產品</label><input id="productSearch" type="search" value="${esc(state.search)}" placeholder="商品名、藥證字號、有效成分或適應症">`;
      $('#productSearch').addEventListener('input', (event) => { state.search = event.target.value; state.page = 1; renderResult(); });
    }
  }

  function scopedProducts() {
    if (state.mode === 'indication' && state.indication) return productSet(indicationByName.get(state.indication)?.productLicenses || []);
    if (state.mode === 'ingredient' && state.ingredient) return products.filter((product) => product.ingredients.includes(state.ingredient));
    return state.mode === 'product' ? products : [];
  }
  function productSet(licenses) { const allowed = new Set(licenses); return products.filter((product) => allowed.has(product.license)); }
  function filterProducts(items) {
    const text = state.mode === 'product' ? state.search.trim().toLocaleLowerCase() : '';
    return items.filter((product) => {
      if (text && ![product.name, product.englishName, product.license, product.ingredientText, product.indicationSummary, product.fullIndication].join(' ').toLocaleLowerCase().includes(text)) return false;
      if (state.filters.dosageForm && product.dosageForm !== state.filters.dosageForm) return false;
      if (state.filters.drugClass && product.drugClass !== state.filters.drugClass) return false;
      if (state.filters.isValid && product.isValid !== state.filters.isValid) return false;
      if (state.filters.ingredientClass && !product.ingredients.some((name) => ingredientByName.get(name)?.ingredientClass === state.filters.ingredientClass)) return false;
      return true;
    });
  }
  function renderFilters(items) {
    const fields = [
      ['ingredientClass', '成分類別', unique(items.flatMap((product) => product.ingredients.map((name) => ingredientByName.get(name)?.ingredientClass)))],
      ['dosageForm', '劑型', unique(items.map((product) => product.dosageForm))],
      ['drugClass', '法律分類', unique(items.map((product) => product.drugClass))],
      ['isValid', '藥證狀態', unique(items.map((product) => product.isValid))]
    ];
    $('#moreFilters').innerHTML = fields.map(([key, label, values]) => `<div class="me-filter"><label for="filter-${key}">${label}</label><select id="filter-${key}" data-filter="${key}">${optionList(values, state.filters[key] || '', '不限')}</select></div>`).join('');
    $('#moreFilters').querySelectorAll('select').forEach((select) => select.addEventListener('change', () => { state.filters[select.dataset.filter] = select.value; state.page = 1; renderResult(); }));
  }
  function bars(title, items, total, onClick) {
    if (!items.length) return `<section class="me-card"><h3>${esc(title)}</h3><p class="me-summary">沒有可顯示的關聯資料。</p></section>`;
    const max = Math.max(...items.map((item) => item.count));
    return `<section class="me-card"><h3>${esc(title)}</h3><div class="me-bars">${items.slice(0, 12).map((item) => `<button type="button" class="me-bar-button" data-query="${esc(onClick)}" data-name="${esc(item.name)}"><span class="me-bar-name">${esc(item.name)}</span><span class="me-bar-track"><span class="me-bar-fill" style="width:${Math.max(3, item.count / max * 100)}%"></span></span><span class="me-bar-value">${item.count} 筆・${total ? (item.count / total * 100).toFixed(1) : 0}%</span></button>`).join('')}</div></section>`;
  }
  function bindBars() { result.querySelectorAll('.me-bar-button').forEach((button) => button.addEventListener('click', () => { if (button.dataset.query === 'ingredient') { state.mode = 'ingredient'; state.ingredient = button.dataset.name; state.indication = ''; } else { state.mode = 'indication'; state.indication = button.dataset.name; state.ingredient = ''; } state.page = 1; render(); })); }
  function counts(items, selector) { const count = new Map(); items.forEach((item) => selector(item).forEach((name) => count.set(name, (count.get(name) || 0) + 1))); return [...count].map(([name, count]) => ({name, count})).sort((a,b) => b.count - a.count || a.name.localeCompare(b.name)); }
  function indicationRelations(items) { return counts(items, (product) => product.ingredients); }
  function ingredientRelations(items) {
    const current = new Set(items.map((product) => product.license));
    return data.indications.map((indication) => ({ name: indication.displayName, count: indication.productLicenses.filter((license) => current.has(license)).length })).filter((item) => item.count).sort((a,b) => b.count - a.count || a.name.localeCompare(b.name));
  }
  function coIngredients(items) { return counts(items, (product) => product.ingredients.filter((name) => name !== state.ingredient)); }
  function renderProducts(items) {
    const pageSize = 20, pageCount = Math.max(1, Math.ceil(items.length / pageSize));
    state.page = Math.min(state.page, pageCount);
    const pageItems = items.slice((state.page - 1) * pageSize, state.page * pageSize);
    const cards = pageItems.map((product) => `<article class="me-product"><div class="me-product-title">${esc(product.name || '未提供商品名')}</div><div class="me-product-line"><strong>有效成分：</strong>${esc(product.ingredientText || product.ingredients.join('；'))}</div><div class="me-product-line"><strong>劑型：</strong>${esc(product.dosageForm || '未提供')}　<strong>適應症：</strong>${esc(product.indicationSummary || '待確認')}</div><details><summary>查看完整藥證與適應症</summary><div class="me-product-line"><strong>藥證：</strong>${esc(product.license)}</div><div class="me-product-line"><strong>完整適應症：</strong>${esc(product.fullIndication || product.indicationSummary || '待確認')}</div></details></article>`).join('');
    return `<section class="me-card"><h3>產品</h3>${cards || '<p class="me-summary">沒有符合條件的產品。</p>'}${items.length ? `<div class="me-pagination"><button class="me-button" type="button" data-page="prev" ${state.page === 1 ? 'disabled' : ''}>上一頁</button><span>第 ${state.page} / ${pageCount} 頁</span><button class="me-button" type="button" data-page="next" ${state.page === pageCount ? 'disabled' : ''}>下一頁</button></div>` : ''}</section>`;
  }
  function bindPagination() { result.querySelectorAll('[data-page]').forEach((button) => button.addEventListener('click', () => { state.page += button.dataset.page === 'next' ? 1 : -1; renderResult(); window.scrollTo({top:0, behavior:'smooth'}); })); }
  function renderResult() {
    const base = scopedProducts(); renderFilters(base); const visible = filterProducts(base);
    if ((state.mode === 'indication' && !state.indication) || (state.mode === 'ingredient' && !state.ingredient)) { result.innerHTML = `<div class="me-empty">請從左側選擇${state.mode === 'indication' ? '適應症' : '有效成分'}，即可查看關聯資料與產品。</div>`; return; }
    const selected = state.mode === 'indication' ? state.indication : state.mode === 'ingredient' ? state.ingredient : (state.search ? `產品搜尋：${state.search}` : '全部外用藥膏產品');
    const description = state.mode === 'indication' ? '顯示此適應症的常見有效成分；點選成分可繼續限縮產品。' : state.mode === 'ingredient' ? '顯示此成分的常見相關適應症與常一起出現的有效成分。' : '可依商品名、藥證字號、有效成分或適應症搜尋。';
    let relations = '';
    if (state.mode === 'indication') relations = `<div class="me-grid">${bars('常見有效成分', indicationRelations(visible), visible.length, 'ingredient')}</div>`;
    if (state.mode === 'ingredient') relations = `<div class="me-grid">${bars('常見相關適應症', ingredientRelations(visible), visible.length, 'indication')}${bars('常一起出現的有效成分', coIngredients(visible), visible.length, 'ingredient')}</div>`;
    result.innerHTML = `<section class="me-card"><h2>${esc(selected)}</h2><p class="me-summary">${description}</p><span class="me-count">符合 ${visible.length} 個不重複藥證產品</span></section>${relations}${renderProducts(visible)}`;
    bindBars(); bindPagination();
  }
  function render() { renderModeButtons(); renderPrimaryControl(); renderResult(); }
  async function init() { setupDatabaseSwitcher(); try { await loadData(); render(); } catch (error) { result.innerHTML = `<div class="me-empty">${esc(error.message)} 請確認以網站預覽方式開啟本頁。</div>`; } }
  init();
})();
