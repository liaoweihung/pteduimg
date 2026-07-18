(() => {
  'use strict';
  const base = 'data/tcm_formula_explorer/';
  const state = { index: [], formulas: {}, analysis: {}, mode: 'product', query: '', legal: '', confidence: '', page: 1, chunks: new Map() };
  const $ = (s, root = document) => root.querySelector(s);
  const esc = (value) => String(value ?? '').replace(/[&<>'"]/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;' })[c]);
  const unique = values => [...new Set(values.filter(Boolean))].sort((a,b) => String(a).localeCompare(String(b), 'zh-Hant'));
  const confidenceLabel = value => ({ high:'高', medium:'中', low:'低' })[value] || '待確認';
  const formulaFor = item => state.formulas[item.formulaId] || null;

  function app() {
    document.body.innerHTML = `
      <a class="me-return" href="calc.html">← 工具首頁</a>
      <button class="me-db-pill" id="tcmMenuButton" type="button">🌿 <span>藥品資料庫</span></button>
      <nav class="me-db-menu" id="tcmMenu" hidden></nav>
      <main class="me-shell" style="--me-accent:#4b7f42">
        <header class="me-heading"><h1>🌿 中成藥母方查詢</h1><p>依產品名稱、藥證字號、推測母方或母方藥材，查閱官方產品資訊與組成相似度推測。</p>
        <section class="me-data-note tcm-note"><strong>重要說明</strong><br>母方關係與加減藥材是 AI 依商品名及處方組成相似度所做的推測，非歷史源流或製造商聲明；請以官方處方自行判斷。官方適應症與處方均依原文呈現。</section></header>
        <section class="me-query-card"><div class="me-mode" id="tcmModes"><button class="active" data-mode="product">母方／產品</button><button data-mode="category">適應症大類</button><button data-mode="ingredient">藥材查詢</button></div><div class="me-primary"><label id="tcmSearchLabel">搜尋商品名、藥證字號、推測母方或母方藥材<input id="tcmSearch" type="search" placeholder="例如：知柏地黃丸、衛署成製字、熟地黃"></label></div>
        <details class="me-more"><summary>篩選條件</summary><div class="me-filter-grid tcm-filter-grid"><label>法規分類<select id="tcmLegal"></select></label><label>AI 推測信心<select id="tcmConfidence"><option value="">全部</option><option value="high">高</option><option value="medium">中</option><option value="low">低</option><option value="none">待確認／無可靠候選</option></select></label></div></details>
        <button class="me-clear" id="tcmClear" type="button">清除條件</button></section><section id="tcmResults" aria-live="polite"></section>
      </main><footer class="me-footer">資料為中成藥產品與傳統成方的組成對照工具，不能取代專業診療或官方核准資料。</footer>`;
    const menu = $('#tcmMenu');
    const links = window.MedicineExplorerLinks || [];
    menu.innerHTML = links.map(([key, url]) => `<a class="tcm-nav-link ${key === 'tcm' ? 'current' : ''}" href="${esc(url)}">${esc(window.MedicineExplorerConfigs?.[key]?.icon || '•')} ${esc(window.MedicineExplorerConfigs?.[key]?.name || key)}</a>`).join('');
    $('#tcmMenuButton').onclick = e => { e.stopPropagation(); menu.hidden = !menu.hidden; };
    document.addEventListener('click', () => { menu.hidden = true; });
    $('#tcmSearch').oninput = e => { state.query = e.target.value.trim().toLowerCase(); state.page = 1; render(); };
    $('#tcmModes').querySelectorAll('button').forEach(b=>b.onclick=()=>{state.mode=b.dataset.mode;state.query='';state.page=1;render();});
    $('#tcmLegal').onchange = e => { state.legal = e.target.value; state.page = 1; render(); };
    $('#tcmConfidence').onchange = e => { state.confidence = e.target.value; state.page = 1; render(); };
    $('#tcmClear').onclick = () => { state.query = state.legal = state.confidence = ''; state.page = 1; render(); };
  }

  function matches(item) {
    if (state.legal && item.class !== state.legal) return false;
    if (state.confidence && (state.confidence === 'none' ? !!item.confidence : item.confidence !== state.confidence)) return false;
    if (!state.query) return true;
    const formula = formulaFor(item);
    return [item.name, item.license, item.formula, formula?.name, formula?.ingredients].filter(Boolean).join(' ').toLowerCase().includes(state.query);
  }

  function render() {
    $('#tcmModes').querySelectorAll('button').forEach(b=>b.classList.toggle('active',b.dataset.mode===state.mode));
    $('#tcmSearchLabel').childNodes[0].textContent=state.mode==='product'?'搜尋商品名、藥證字號、推測母方或母方藥材':state.mode==='ingredient'?'搜尋或點選藥材':'搜尋適應症大類';
    $('#tcmSearch').placeholder=state.mode==='ingredient'?'例如：熟地黃、甘草':state.mode==='category'?'例如：婦科、消化、感冒':'例如：知柏地黃丸、衛署成製字、熟地黃';
    if(state.mode==='category'){ $('#tcmLegal').closest('details').hidden=true; renderCategories(); return; }
    if(state.mode==='ingredient'){ $('#tcmLegal').closest('details').hidden=true; renderIngredients(); return; }
    $('#tcmLegal').closest('details').hidden=false;
    const legal = $('#tcmLegal');
    legal.innerHTML = `<option value="">全部</option>${unique(state.index.map(x => x.class)).map(x => `<option value="${esc(x)}" ${x === state.legal ? 'selected' : ''}>${esc(x)}</option>`).join('')}`;
    $('#tcmSearch').value = state.query;
    $('#tcmConfidence').value = state.confidence;
    const rows = state.index.filter(matches); const pages = Math.max(1, Math.ceil(rows.length / 20)); state.page = Math.min(state.page, pages);
    const shown = rows.slice((state.page - 1) * 20, state.page * 20);
    $('#tcmResults').innerHTML = `<section class="me-card me-result-title"><h2>查詢結果</h2><p>結果先顯示索引摘要；展開時才下載產品詳細分檔。</p><strong>${rows.length.toLocaleString()} 項產品</strong></section><section class="me-card"><div class="me-products">${shown.map(card).join('') || '<p class="me-summary">沒有符合的產品。</p>'}</div>${pager(pages)}</section>`;
    $('#tcmResults').querySelectorAll('[data-open]').forEach(button => button.onclick = () => loadDetail(button));
    $('#tcmResults').querySelectorAll('[data-page]').forEach(button => button.onclick = () => { state.page += Number(button.dataset.page); render(); window.scrollTo({top:0, behavior:'smooth'}); });
  }

  function bars(items, label='項') { const max=Math.max(1,...items.map(x=>x.count)); return `<div class="me-bars">${items.map(x=>`<button type="button" data-value="${esc(x.name)}"><span>${esc(x.name)}</span><i><b style="width:${x.count/max*100}%"></b></i><em>${x.count} ${label}</em></button>`).join('')}</div>`; }
  function renderCategories(){ const q=state.query; const rows=Object.entries(state.analysis.categories||{}).filter(([k])=>!q||k.toLowerCase().includes(q)); $('#tcmResults').innerHTML=`<section class="me-card me-result-title"><h2>適應症大類</h2><p>大類依官方適應症原文以公開關鍵字規則整理，不取代官方適應症。</p><strong>${rows.length} 個大類</strong></section>${rows.map(([name,x])=>`<section class="me-card"><h2>${esc(name)}</h2><p class="me-summary">產品 ${x.productCount} 項・推測母方 ${x.formulaCount} 個</p><h3>常見藥材</h3>${bars(x.ingredients)}<h3>常見藥材組合</h3>${bars(x.combinations)}<h3>官方適應症原文代表例</h3>${x.evidence.map(e=>`<details><summary>${esc(e.name)}（${esc(e.license)}）</summary><p class="tcm-raw">${esc(e.indications)}</p></details>`).join('')}</section>`).join('')||'<section class="me-empty">沒有符合的大類。</section>'}`; }
  function renderIngredients(){ const q=state.query; const rows=Object.entries(state.analysis.ingredients||{}).filter(([k])=>!q||k.toLowerCase().includes(q)).sort((a,b)=>b[1].productCount-a[1].productCount).slice(0,q?50:30); $('#tcmResults').innerHTML=`<section class="me-card me-result-title"><h2>藥材關聯</h2><p>以母方組成或產品實際處方中可辨識藥材計算；已排除常見賦形劑。名稱正規化僅用於統計，官方原文仍保留在產品詳情。</p><strong>${rows.length} 項藥材</strong></section>${rows.map(([name,x])=>`<section class="me-card"><h2>${esc(name)}</h2><p class="me-summary">相關產品 ${x.productCount} 項・母方 ${x.formulaCount} 個</p><h3>最常出現的適應症大類</h3>${bars(x.categories)}<h3>共現藥材</h3>${bars(x.cooccurring)}<h3>官方適應症原文代表例</h3>${x.evidence.map(v=>`<p class="tcm-raw">${esc(v)}</p>`).join('')}<h3>代表中成藥／母方</h3>${x.representatives.map(v=>`<p>${esc(v.name)}（${esc(v.license)}）${v.formula?`・${esc(v.formula)}`:''}</p>`).join('')}</section>`).join('')||'<section class="me-empty">沒有符合的藥材。</section>'}`; $('#tcmResults').querySelectorAll('[data-value]').forEach(b=>b.onclick=()=>{state.query=b.dataset.value;render();}); }

  function card(item) {
    const formula = formulaFor(item); const candidate = item.formula || '無可靠候選';
    return `<article class="me-products details tcm-product" data-license="${esc(item.license)}"><div class="me-product-title">${esc(item.name)}</div><div class="me-product-line">藥證：${esc(item.license)}</div><div class="tcm-result-meta"><span class="tcm-pill">${esc(item.class || '待確認')}</span><span class="tcm-pill ${item.confidence ? '' : 'warn'}">AI 信心：${esc(confidenceLabel(item.confidence))}</span></div><div class="me-product-line">推測母方：<b>${esc(candidate)}</b></div>${formula?.ingredients ? `<div class="me-product-line">母方藥材：${esc(formula.ingredients)}</div>` : ''}<div class="tcm-product-actions"><button class="tcm-open" type="button" data-open data-chunk="${item.chunk}" data-license="${esc(item.license)}">展開官方原文與推測依據</button></div><div class="tcm-detail" hidden></div></article>`;
  }
  function pager(pages) { return pages > 1 ? `<nav class="me-pager"><button data-page="-1" ${state.page === 1 ? 'disabled' : ''}>上一頁</button><span>第 ${state.page} / ${pages} 頁</span><button data-page="1" ${state.page === pages ? 'disabled' : ''}>下一頁</button></nav>` : ''; }
  async function loadDetail(button) {
    const container = button.closest('.tcm-product').querySelector('.tcm-detail'); button.disabled = true; button.textContent = '載入詳細資料…';
    try {
      const chunk = Number(button.dataset.chunk); let products = state.chunks.get(chunk);
      if (!products) { const response = await fetch(`${base}products-${String(chunk).padStart(2, '0')}.json`); if (!response.ok) throw Error(`讀取失敗（${response.status}）`); products = (await response.json()).products; state.chunks.set(chunk, products); }
      const product = products.find(x => x.license === button.dataset.license); if (!product) throw Error('找不到該產品的詳細資料');
      container.innerHTML = detail(product, formulaFor({formulaId: product.formulaId})); container.hidden = false; button.remove();
    } catch (error) { button.disabled = false; button.textContent = '重新載入詳細資料'; container.innerHTML = `<p class="tcm-error">${esc(error.message)}</p>`; container.hidden = false; }
  }
  function section(title, value, raw = false) { return value ? `<h3>${title}</h3><p${raw ? ' class="tcm-raw"' : ''}>${esc(value)}</p>` : ''; }
  function detail(product, formula) {
    const formulaSection = formula ? `${section('母方名稱', formula.name)}${section('母方來源', formula.source)}${section('母方處方', formula.prescription)}${section('母方藥材', formula.ingredients)}${section('母方功能／適應症', formula.functions)}` : '<h3>推測母方</h3><p>此產品目前沒有可靠候選母方；不強行指定。</p>';
    return `${section('官方適應症（原文）', product.indications, true)}${section('官方產品處方（原文）', product.prescription, true)}<h3>AI 組成相似度推測</h3><p>推測母方：${esc(product.formula || '無可靠候選')}；關係：${esc(product.relationship || '待確認')}；信心：${esc(confidenceLabel(product.confidence))}；比對依據：${esc(product.basis || '待確認')}</p><div class="tcm-diff"><div><b>增加藥材</b>${esc(product.added || '無')}</div><div><b>減少藥材</b>${esc(product.removed || '無')}</div><div><b>規格差異</b>${esc(product.specDiff || '無')}</div></div>${section('製劑材料（非加味藥材）', product.nonmed)}${section('待釐清成分', product.unresolved)}${formulaSection}${section('替代候選', product.alternatives)}${section('AI 推測警示', product.cautions)}<h3>解讀提醒</h3><p>母方關係與加減藥材是 AI 依商品名及處方組成相似度所做的推測，非歷史源流或製造商聲明；請以官方處方自行判斷。</p>`;
  }
  async function init() {
    try {
      const [indexResponse, formulaResponse, analysisResponse] = await Promise.all([fetch(`${base}index.json`), fetch(`${base}formulas.json`), fetch(`${base}relationship_analysis.json`)]);
      if (!indexResponse.ok || !formulaResponse.ok || !analysisResponse.ok) throw Error('索引、母方或關聯分析資料無法載入');
      const [index, formulas, analysis] = await Promise.all([indexResponse.json(), formulaResponse.json(), analysisResponse.json()]);
      if (index.productCount !== 21196 || index.products?.length !== 21196 || Object.keys(formulas.formulas || {}).length !== 204) throw Error('資料筆數驗證失敗');
      state.index = index.products; state.formulas = formulas.formulas; state.analysis = analysis; app(); render();
      if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
    } catch (error) { document.body.innerHTML = `<main class="me-shell"><section class="me-empty">資料載入失敗：${esc(error.message)}</section></main>`; }
  }
  init();
})();
