(() => {
  "use strict";

  const $ = (selector) => document.querySelector(selector);
  const PAGE_SIZE = 25;
  const labels = {
    ready_to_use: "開瓶可直接使用",
    requires_reconstitution: "需要加水配製",
    syrup: "糖漿",
    oral_solution: "口服溶液",
    oral_suspension: "口服懸液",
    oral_drops: "口服滴劑",
    oral_emulsion: "口服乳劑",
    powder_for_oral_suspension: "乾粉懸液",
    granules_for_oral_suspension: "顆粒懸液",
    powder_for_oral_solution: "口服溶液用粉",
    other_ready_to_use_oral_liquid: "其他即用型口服液",
    other_reconstituted_oral_liquid: "其他需配製口服液",
  };
  const state = { preparation: "", form: "", therapeuticClass: "", indication: "", ingredient: "", concentration: "", query: "", page: 1, expanded: false };
  let products = [];
  let ingredientNames = new Map();

  const esc = (value) => String(value ?? "").replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
  const unique = (items) => [...new Set(items.filter(Boolean))].sort((a, b) => a.localeCompare(b, "zh-Hant"));
  const activeKey = (active) => active.substance_id;
  const activeLabel = (id) => ingredientNames.get(id) || id;
  const text = (product) => [product.chinese_name, product.english_name, product.license_number, product.indication, ...product.active_ingredients.flatMap((active) => [active.name, active.display_concentration, active.strength_raw])].join(" ").toLowerCase();
  const isComparableDisplay = (active) => Boolean(active.display_concentration && /\/\s*(?:\d+(?:\.\d+)?\s*)?mL$/i.test(active.display_concentration));
  const formCategory = (group) => {
    if (["powder_for_oral_suspension", "granules_for_oral_suspension"].includes(group)) return "reconstituted_suspension";
    if (["syrup", "oral_solution", "oral_suspension", "oral_drops", "oral_emulsion"].includes(group)) return group;
    return "other";
  };
  const preparationLabel = (value) => labels[value] || value;
  const formLabel = (value) => labels[value] || value;
  const resetPage = () => { state.page = 1; };

  function primaryFiltered({ ignoreIngredient = false, ignoreConcentration = false } = {}) {
    const query = state.query.toLowerCase();
    return products.filter((product) => {
      if (state.preparation && product.preparation_type !== state.preparation) return false;
      if (state.form && formCategory(product.dosage_form_group) !== state.form) return false;
      if (state.therapeuticClass && !product.therapeutic_classes.includes(state.therapeuticClass)) return false;
      if (state.indication && product.indication_category !== state.indication) return false;
      if (!ignoreIngredient && state.ingredient && !product.active_ingredients.some((active) => activeKey(active) === state.ingredient)) return false;
      if (!ignoreConcentration && state.concentration) {
        const selected = product.active_ingredients.filter((active) => activeKey(active) === state.ingredient);
        if (state.concentration === "__pending") {
          if (!selected.some((active) => active.normalization_status === "unresolved")) return false;
        } else if (!selected.some((active) => active.display_concentration === state.concentration && isComparableDisplay(active))) return false;
      }
      return !query || text(product).includes(query);
    });
  }

  function selectedFilters() {
    return [
      ["配製方式", preparationLabel(state.preparation)],
      ["劑型", state.form ? ({ reconstituted_suspension: "乾粉／顆粒懸液", other: "其他正式劑型" }[state.form] || formLabel(state.form)) : ""],
      ["治療分類", state.therapeuticClass],
      ["適應症", state.indication],
      ["有效成分", activeLabel(state.ingredient)],
      ["濃度", state.concentration === "__pending" ? "濃度待確認" : state.concentration],
      ["搜尋", state.query],
    ].filter(([, value]) => value);
  }

  function activeStats(current) {
    const countByIngredient = new Map();
    current.forEach((product) => {
      new Set(product.active_ingredients.map(activeKey)).forEach((id) => countByIngredient.set(id, (countByIngredient.get(id) || 0) + 1));
    });
    return [...countByIngredient.entries()].sort((a, b) => b[1] - a[1] || activeLabel(a[0]).localeCompare(activeLabel(b[0]), "zh-Hant"));
  }

  function renderCommonIngredients(current) {
    const panel = $("#commonIngredients");
    const shouldShow = Boolean(state.preparation || state.form || state.therapeuticClass || state.indication);
    panel.hidden = !shouldShow;
    if (!shouldShow) return;
    const stats = activeStats(current);
    const shown = state.expanded ? stats : stats.slice(0, 10);
    panel.innerHTML = `<h2>目前條件下的常見有效成分</h2><p>僅統計 confirmed active；同一產品的同一成分只計一次。</p><div>${shown.map(([id, count]) => `<button class="ingredient ${state.ingredient === id ? "active" : ""}" data-ingredient="${esc(id)}" type="button">${esc(activeLabel(id))}<span>${count} 項（${current.length ? (count / current.length * 100).toFixed(1) : "0.0"}%）</span></button>`).join("")}</div>${stats.length > 10 ? `<button class="more" id="ingredientMore" type="button">${state.expanded ? "收合" : "展開全部"}</button>` : ""}`;
    panel.querySelectorAll("[data-ingredient]").forEach((button) => {
      button.addEventListener("click", () => {
        state.ingredient = state.ingredient === button.dataset.ingredient ? "" : button.dataset.ingredient;
        state.concentration = "";
        $("#ingredientFilter").value = state.ingredient;
        resetPage();
        render();
      });
    });
    const more = $("#ingredientMore");
    if (more) more.addEventListener("click", () => { state.expanded = !state.expanded; render(); });
  }

  function renderConcentrationGroups() {
    const panel = $("#concentrationGroups");
    panel.hidden = !state.ingredient;
    if (!state.ingredient) return;
    const current = primaryFiltered({ ignoreConcentration: true });
    const groups = new Map();
    const pendingProducts = new Set();
    current.forEach((product) => {
      product.active_ingredients.filter((active) => activeKey(active) === state.ingredient).forEach((active) => {
        if (isComparableDisplay(active)) {
          if (!groups.has(active.display_concentration)) groups.set(active.display_concentration, new Set());
          groups.get(active.display_concentration).add(product.product_id);
        }
        if (active.normalization_status === "unresolved") pendingProducts.add(product.product_id);
      });
    });
    const sorted = [...groups.entries()].sort((a, b) => b[1].size - a[1].size || a[0].localeCompare(b[0]));
    const buttons = sorted.map(([display, ids]) => `<button class="concentration ${state.concentration === display ? "active" : ""}" data-concentration="${esc(display)}" type="button">${esc(display)}：${ids.size} 項產品</button>`);
    if (pendingProducts.size) buttons.push(`<button class="concentration pending ${state.concentration === "__pending" ? "active" : ""}" data-concentration="__pending" type="button">濃度待確認：${pendingProducts.size} 項產品</button>`);
    panel.innerHTML = `<h2>此成分的常見濃度／規格</h2><p>依官方顯示濃度分組；每瓶、每包總量不會列入濃度篩選。${pendingProducts.size ? "未能可靠解析者標示為濃度待確認。" : ""}</p><div>${buttons.join("") || "<span class=\"muted\">目前結果沒有可比較的官方濃度。</span>"}</div>`;
    panel.querySelectorAll("[data-concentration]").forEach((button) => {
      button.addEventListener("click", () => {
        state.concentration = state.concentration === button.dataset.concentration ? "" : button.dataset.concentration;
        resetPage();
        render();
      });
    });
  }

  function renderSummary(current) {
    const preparations = { ready_to_use: 0, requires_reconstitution: 0 };
    current.forEach((product) => { preparations[product.preparation_type] += 1; });
    const activeKinds = new Set(current.flatMap((product) => product.active_ingredients.map(activeKey)));
    const withConcentration = current.filter((product) => product.has_display_concentration).length;
    $("#count").textContent = current.length;
    $("#preparationSummary").textContent = `即用型 ${preparations.ready_to_use}／需配製 ${preparations.requires_reconstitution}`;
    $("#activeCount").textContent = activeKinds.size;
    $("#concentrationCount").textContent = withConcentration;
    const chips = selectedFilters();
    $("#applied").innerHTML = chips.length ? chips.map(([label, value]) => `<span class="chip">${esc(label)}：${esc(value)}</span>`).join("") : "<span>未套用條件</span>";
  }

  function concentrationText(active) {
    const base = active.display_concentration || (active.normalization_status === "unresolved" ? "濃度待確認" : active.strength_raw || "官方規格未列出");
    const normalized = active.normalized_value_per_ml && active.normalized_unit_per_ml ? `；比較值 ${esc(active.normalized_value_per_ml)} ${esc(active.normalized_unit_per_ml)}` : "";
    return `${esc(base)}${normalized}`;
  }

  function productCard(product) {
    const activeNames = product.active_ingredients.map((active) => active.name).join("、");
    const officialConcentrations = unique(product.active_ingredients.map((active) => active.display_concentration)).join("、");
    const classes = product.therapeutic_classes.map((name) => `<span class="pill">${esc(name)}</span>`).join("");
    const activeDetails = product.active_ingredients.map((active) => `<div><strong>${esc(active.name)}</strong><br>${concentrationText(active)}</div>`).join("");
    const route = product.route_raw && !["請詳見仿單", "詳如仿單", "詳見仿單"].includes(product.route_raw) ? `<dt>官方用法用量</dt><dd>${esc(product.route_raw)}</dd>` : "";
    const indicationRelations = product.indication_relations.length ? product.indication_relations.map((item) => item.indication_raw).filter((value, index, values) => values.indexOf(value) === index).join("；") : "";
    return `<details class="card"><summary><div class="title"><div><h3>${esc(product.chinese_name || product.english_name)}</h3>${product.english_name ? `<p class="english">${esc(product.english_name)}</p>` : ""}</div><p class="license">${esc(product.license_number)}</p></div><div class="meta"><span class="pill">${esc(product.dosage_form_raw || formLabel(product.dosage_form_group))}</span><span class="pill ${product.preparation_type === "requires_reconstitution" ? "reconstitution" : ""}">${esc(preparationLabel(product.preparation_type))}</span>${product.concentration_pending ? "<span class=\"pill pending\">濃度待確認</span>" : ""}${classes}</div><p><strong>有效成分：</strong>${esc(activeNames)}</p><p><strong>官方濃度：</strong>${esc(officialConcentrations || (product.concentration_pending ? "濃度待確認" : "官方規格未列出"))}</p><p><strong>適應症：</strong>${esc(product.indication.length > 120 ? `${product.indication.slice(0, 120)}…` : product.indication)}</p></summary><div class="detail"><dl><dt>完整適應症原文</dt><dd>${esc(product.indication)}</dd>${indicationRelations ? `<dt>關聯適應症資料</dt><dd>${esc(indicationRelations)}</dd>` : ""}<dt>每項有效成分及官方濃度</dt><dd class="ingredient-detail">${activeDetails}</dd><dt>藥證年份與狀態</dt><dd>${esc(product.license_year)}；${esc(product.license_status)}${product.license_expiry_date ? `；有效至 ${esc(product.license_expiry_date)}` : ""}</dd><dt>法律分類</dt><dd>${esc(product.legal_category || "官方資料未列出")}</dd><dt>申請商／製造商</dt><dd>${esc(product.applicant || "官方資料未列出")}／${esc(product.manufacturer || "官方資料未列出")}</dd>${route}<dt>官方來源</dt><dd>${esc(product.source_id)}；資料確認：${esc(product.verified_at)}</dd><dt>收錄依據與其他可取得資料</dt><dd>${esc(product.inclusion_evidence)}</dd></dl></div></details>`;
  }

  function renderList(current) {
    const pages = Math.max(1, Math.ceil(current.length / PAGE_SIZE));
    state.page = Math.min(state.page, pages);
    const start = (state.page - 1) * PAGE_SIZE;
    const shown = current.slice(start, start + PAGE_SIZE);
    $("#listHeading").textContent = `查詢結果（${current.length} 項）`;
    $("#list").innerHTML = shown.length ? shown.map(productCard).join("") : "<div class=\"empty\">沒有符合條件的正式產品。</div>";
    $("#pageInfo").textContent = `第 ${state.page}／${pages} 頁`;
    $("#prevPage").disabled = state.page <= 1;
    $("#nextPage").disabled = state.page >= pages;
    $("#pager").hidden = !current.length;
  }

  function render() {
    const current = primaryFiltered();
    renderSummary(current);
    renderCommonIngredients(current);
    renderConcentrationGroups();
    renderList(current);
  }

  function addOptions(selector, values, label = (value) => value) {
    const element = $(selector);
    values.forEach((value) => element.insertAdjacentHTML("beforeend", `<option value="${esc(value)}">${esc(label(value))}</option>`));
  }

  function bind() {
    [["#preparationFilter", "preparation"], ["#formFilter", "form"], ["#classFilter", "therapeuticClass"], ["#indicationFilter", "indication"], ["#ingredientFilter", "ingredient"]].forEach(([selector, key]) => {
      $(selector).addEventListener("change", (event) => { state[key] = event.target.value; state.concentration = ""; state.expanded = false; resetPage(); render(); });
    });
    $("#query").addEventListener("input", (event) => { state.query = event.target.value.trim(); resetPage(); render(); });
    $("#clear").addEventListener("click", () => {
      Object.assign(state, { preparation: "", form: "", therapeuticClass: "", indication: "", ingredient: "", concentration: "", query: "", page: 1, expanded: false });
      document.querySelectorAll("select,input").forEach((element) => { element.value = ""; });
      render();
    });
    $("#prevPage").addEventListener("click", () => { state.page -= 1; render(); window.scrollTo({ top: 0, behavior: "smooth" }); });
    $("#nextPage").addEventListener("click", () => { state.page += 1; render(); window.scrollTo({ top: 0, behavior: "smooth" }); });
  }

  async function init() {
    const response = await fetch("data/oral_liquid_meds_rebuild_20260714/final/oral_liquid_meds_final.json", { cache: "no-cache" });
    if (!response.ok) throw new Error(`資料載入失敗（${response.status}）`);
    const payload = await response.json();
    if (payload.product_count !== 1034 || payload.products.length !== 1034 || payload.summary.ready_to_use !== 963 || payload.summary.requires_reconstitution !== 71 || payload.summary.concentration_pending_products !== 88) throw new Error("正式資料完整性驗證失敗");
    products = payload.products;
    products.flatMap((product) => product.active_ingredients).forEach((active) => ingredientNames.set(activeKey(active), active.name));
    addOptions("#classFilter", unique(products.flatMap((product) => product.therapeutic_classes)));
    addOptions("#indicationFilter", unique(products.map((product) => product.indication_category)));
    addOptions("#ingredientFilter", [...ingredientNames.keys()].sort((a, b) => activeLabel(a).localeCompare(activeLabel(b), "zh-Hant")), activeLabel);
    bind();
    render();
    if ("serviceWorker" in navigator) navigator.serviceWorker.register("./sw.js").catch(() => {});
  }

  init().catch((error) => { $("#list").innerHTML = `<div class="empty">${esc(error.message)}</div>`; $("#pager").hidden = true; });
})();
