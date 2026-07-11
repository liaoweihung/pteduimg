const state = {
  data: null,
  entry: "indication",
  query: "",
  selectedId: null,
};

const els = {
  updatedAt: document.querySelector("#updatedAt"),
  productCount: document.querySelector("#productCount"),
  activeCount: document.querySelector("#activeCount"),
  inactiveCount: document.querySelector("#inactiveCount"),
  preservativeRate: document.querySelector("#preservativeRate"),
  excipientRate: document.querySelector("#excipientRate"),
  searchLabel: document.querySelector("#searchLabel"),
  searchInput: document.querySelector("#searchInput"),
  entrySelectLabel: document.querySelector("#entrySelectLabel"),
  entrySelect: document.querySelector("#entrySelect"),
  quickResultCount: document.querySelector("#quickResultCount"),
  jumpToResults: document.querySelector("#jumpToResults"),
  dosageFilter: document.querySelector("#dosageFilter"),
  legalFilter: document.querySelector("#legalFilter"),
  therapyFilter: document.querySelector("#therapyFilter"),
  preservativeFilter: document.querySelector("#preservativeFilter"),
  comboFilter: document.querySelector("#comboFilter"),
  pfFilter: document.querySelector("#pfFilter"),
  includeInactive: document.querySelector("#includeInactive"),
  results: document.querySelector("#results"),
  resultSummary: document.querySelector("#resultSummary"),
  resultList: document.querySelector("#resultList"),
  emptyState: document.querySelector("#emptyState"),
  errorState: document.querySelector("#errorState"),
  detailEmpty: document.querySelector("#detailEmpty"),
  detailView: document.querySelector("#detailView"),
  formulationPanel: document.querySelector("#formulationPanel"),
  preservativeStats: document.querySelector("#preservativeStats"),
  preservativeFreeList: document.querySelector("#preservativeFreeList"),
  excipientStats: document.querySelector("#excipientStats"),
  functionStats: document.querySelector("#functionStats"),
  dosageComposition: document.querySelector("#dosageComposition"),
};

const entryConfig = {
  indication: {
    label: "輸入適應症關鍵字",
    selectLabel: "或從適應症清單選擇",
    placeholder: "例如：青光眼、乾眼、感染",
  },
  ingredient: {
    label: "輸入有效成分",
    selectLabel: "或從有效成分清單選擇",
    placeholder: "例如：TIMOLOL、DEXAMETHASONE",
  },
  class: {
    label: "輸入藥品分類",
    selectLabel: "或從藥品分類清單選擇",
    placeholder: "例如：人工淚液、抗感染、timolol",
  },
  product: {
    label: "輸入商品名、英文品名或藥證字號",
    selectLabel: "或從商品／藥證清單選擇",
    placeholder: "例如：眼藥水、衛署藥製字、商品名",
  },
  formulation: {
    label: "輸入保存劑、賦形劑或製劑功能",
    selectLabel: "或從製劑資訊清單選擇",
    placeholder: "例如：BENZALKONIUM、黏度調節劑、無保存劑",
  },
};

function text(value) {
  return value == null || value === "" ? "資料不足" : String(value);
}

function pct(value) {
  return `${Math.round((Number(value) || 0) * 100)}%`;
}

function optionList(select, values, labelFor = (v) => v) {
  select.innerHTML = `<option value="">全部</option>${values
    .map((value) => `<option value="${escapeAttr(value)}">${escapeHtml(labelFor(value))}</option>`)
    .join("")}`;
}

function uniqueSorted(values) {
  return [...new Set(values.filter((value) => value && String(value).trim()))].sort((a, b) => String(a).localeCompare(String(b), "zh-Hant"));
}

function productChoiceLabel(product) {
  return `${product.chinese_name}｜${product.license_number}`;
}

function entryChoices(entry) {
  const products = state.data.products.filter((product) => els.includeInactive?.checked || product.status_group === "active");
  if (entry === "indication") return state.data.facets.indications;
  if (entry === "ingredient") return state.data.facets.active_ingredients;
  if (entry === "class") {
    const values = products.flatMap((product) => [
      product.therapeutic_class,
      ...product.drug_classes.map((item) => item.class_name || item.code),
    ]);
    return uniqueSorted(values);
  }
  if (entry === "product") {
    return products
      .slice()
      .sort((a, b) => productChoiceLabel(a).localeCompare(productChoiceLabel(b), "zh-Hant"))
      .map((product) => ({
        value: product.license_number,
        label: productChoiceLabel(product),
      }));
  }
  if (entry === "formulation") {
    const values = [
      ...state.data.facets.preservatives,
      "明確無保存劑",
      "確認含保存劑",
      "資料不足",
      ...Object.keys(state.data.analyses.excipients.by_role),
    ];
    return uniqueSorted(values);
  }
  return [];
}

function renderEntrySelect() {
  const choices = entryChoices(state.entry);
  const options = choices.map((choice) => {
    const value = typeof choice === "string" ? choice : choice.value;
    const label = typeof choice === "string" ? choice : choice.label;
    return `<option value="${escapeAttr(value)}">${escapeHtml(label)}</option>`;
  });
  els.entrySelect.innerHTML = `<option value="">請選擇，或保留空白自行輸入</option>${options.join("")}`;
  els.entrySelect.value = choices.some((choice) => (typeof choice === "string" ? choice : choice.value) === state.query) ? state.query : "";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttr(value) {
  return escapeHtml(value);
}

function normalized(value) {
  return String(value || "").toLowerCase().trim();
}

function productMatchesEntry(product, q) {
  if (!q) return true;
  if (state.entry === "indication") {
    return normalized(product.indication_raw).includes(q)
      || product.standardized_indications.some((i) => normalized(`${i.name_zh} ${i.name_en} ${i.evidence_text}`).includes(q));
  }
  if (state.entry === "ingredient") {
    return product.active_ingredients.some((s) => normalized(`${s.base_substance_group} ${s.standardized_name} ${s.chinese_name} ${s.english_name} ${s.raw_name}`).includes(q));
  }
  if (state.entry === "class") {
    return normalized(product.therapeutic_class).includes(q)
      || product.drug_classes.some((c) => normalized(`${c.code} ${c.class_name} ${c.classification_system}`).includes(q));
  }
  if (state.entry === "formulation") {
    return normalized(product.preservative_free_label).includes(q)
      || product.preservatives.some((s) => normalized(`${s.base_substance_group} ${s.standardized_name} ${s.formulation_function}`).includes(q))
      || product.excipients.some((s) => normalized(`${s.base_substance_group} ${s.standardized_name} ${s.role_label} ${s.formulation_function}`).includes(q));
  }
  return normalized(product.search_text).includes(q);
}

function activeIngredientMode(product) {
  return product.active_ingredients.length <= 1 ? "single" : "combo";
}

function passesFilters(product) {
  if (!els.includeInactive.checked && product.status_group !== "active") return false;
  if (els.dosageFilter.value && product.dosage_form !== els.dosageFilter.value) return false;
  if (els.legalFilter.value && product.legal_category !== els.legalFilter.value) return false;
  if (els.therapyFilter.value && product.therapeutic_class !== els.therapyFilter.value) return false;
  if (els.pfFilter.value && product.preservative_free_status !== els.pfFilter.value) return false;
  if (els.comboFilter.value && activeIngredientMode(product) !== els.comboFilter.value) return false;
  if (els.preservativeFilter.value) {
    const hit = product.preservatives.some((s) => (s.base_substance_group || s.standardized_name) === els.preservativeFilter.value);
    if (!hit) return false;
  }
  return productMatchesEntry(product, normalized(state.query));
}

function getFilteredProducts() {
  return state.data.products.filter(passesFilters);
}

function renderSummary() {
  const s = state.data.summary;
  els.updatedAt.textContent = `更新：${s.source_date_range.to}，版本 ${s.version}`;
  els.productCount.textContent = `共 ${s.product_count} 項局部眼用藥證產品`;
  els.activeCount.textContent = s.active_product_count;
  els.inactiveCount.textContent = s.inactive_product_count;
  els.preservativeRate.textContent = pct(s.preservative_completion.rate);
  els.excipientRate.textContent = pct(s.excipient_completion.rate);
}

function renderFilters() {
  const { facets, dosage_labels: dosageLabels } = state.data;
  optionList(els.dosageFilter, facets.dosage_forms, (v) => dosageLabels[v] || v);
  optionList(els.legalFilter, facets.legal_categories);
  optionList(els.therapyFilter, facets.therapeutic_classes);
  optionList(els.preservativeFilter, facets.preservatives);
}

function renderResults() {
  const products = getFilteredProducts();
  els.resultSummary.textContent = `顯示 ${products.length} 項；預設只顯示有效藥證。`;
  els.quickResultCount.textContent = `目前 ${products.length} 筆結果`;
  els.emptyState.hidden = products.length !== 0;
  els.resultList.innerHTML = products.slice(0, 250).map(productCard).join("");
  els.results.setAttribute("aria-busy", "false");
  els.resultList.querySelectorAll("button[data-product-id]").forEach((button) => {
    button.addEventListener("click", () => selectProduct(button.dataset.productId));
  });
  if (!state.selectedId && products[0]) selectProduct(products[0].product_id);
  if (state.selectedId && !products.some((p) => p.product_id === state.selectedId)) {
    if (products[0]) selectProduct(products[0].product_id);
    else clearDetail();
  }
}

function scrollToResults() {
  els.results.scrollIntoView({ behavior: "smooth", block: "start" });
}

function productCard(product) {
  const statusClass = product.status_group === "active" ? "status-active" : "status-inactive";
  const actives = product.active_ingredients.slice(0, 3).map((s) => `<span class="tag active">${escapeHtml(s.base_substance_group || s.standardized_name)}</span>`).join("");
  const preservative = product.preservatives[0]
    ? `<span class="tag preservative">${escapeHtml(product.preservatives[0].base_substance_group || product.preservatives[0].standardized_name)}</span>`
    : `<span class="tag preservative">${escapeHtml(product.preservative_free_label)}</span>`;
  return `
    <button class="product-card" type="button" data-product-id="${escapeAttr(product.product_id)}">
      <span class="product-title">
        <span>${escapeHtml(product.chinese_name)}</span>
        <span class="${statusClass}">${escapeHtml(product.license_status)}</span>
      </span>
      <span class="product-meta">
        <span>${escapeHtml(product.license_number)}</span>
        <span>${escapeHtml(product.dosage_form_label)}</span>
        <span>${escapeHtml(product.legal_category)}</span>
      </span>
      <span class="tag-row">${actives}${preservative}</span>
    </button>
  `;
}

function selectProduct(productId) {
  state.selectedId = productId;
  const product = state.data.products.find((p) => p.product_id === productId);
  if (!product) return clearDetail();
  els.detailEmpty.hidden = true;
  els.detailView.hidden = false;
  els.detailView.innerHTML = detailHtml(product);
}

function clearDetail() {
  state.selectedId = null;
  els.detailEmpty.hidden = false;
  els.detailView.hidden = true;
  els.detailView.innerHTML = "";
}

function detailHtml(product) {
  const statusClass = product.status_group === "active" ? "status-active" : "status-inactive";
  return `
    <h2>${escapeHtml(product.chinese_name)}</h2>
    <p>${escapeHtml(product.english_name || "英文品名資料不足")}</p>
    <div class="tag-row">
      <span class="tag active">有效成分 ${product.active_ingredients.length}</span>
      <span class="tag preservative">${escapeHtml(product.preservative_free_label)}</span>
      <span class="tag excipient">賦形劑 ${product.excipients.length}</span>
      <span class="${statusClass}">${escapeHtml(product.license_status)}</span>
    </div>

    <section class="detail-section">
      <dl class="detail-grid">
        ${detailItem("藥證字號", product.license_number)}
        ${detailItem("劑型與使用途徑", `${product.dosage_form_label}；${product.route_raw || product.route}`)}
        ${detailItem("法規分類", product.legal_category)}
        ${detailItem("治療分類", product.therapeutic_class)}
        ${detailItem("申請商", product.applicant)}
        ${detailItem("製造商", product.manufacturer)}
        ${detailItem("藥證效期", product.license_expiry_date)}
        ${detailItem("確認日期", product.verified_at)}
      </dl>
    </section>

    ${substanceSection("有效成分及含量", product.active_ingredients, "active")}
    ${substanceSection("保存劑", product.preservatives, "preservative")}
    ${substanceSection("其他賦形劑及製劑功能", product.excipients, "excipient")}

    <section class="detail-section">
      <h3>適應症</h3>
      <p><strong>原始核准適應症：</strong>${escapeHtml(text(product.indication_raw))}</p>
      <p><strong>標準化適應症：</strong>${escapeHtml(product.standardized_indications.map((i) => i.name_zh).join("、") || "資料不足")}</p>
    </section>

    <section class="detail-section">
      <h3>資料來源</h3>
      <p>${escapeHtml(product.source.title || product.source_id)}；藥證狀態查核日 ${escapeHtml(text(product.status_checked_at))}</p>
      <p><strong>局部眼用收錄依據：</strong>${escapeHtml(text(product.ophthalmic_inclusion_evidence))}</p>
    </section>
  `;
}

function detailItem(label, value) {
  return `<div><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(text(value))}</dd></div>`;
}

function substanceSection(title, rows, kind) {
  const empty = `<div class="state">此欄位資料不足。</div>`;
  const body = rows.length ? rows.map((s) => `
    <div class="substance-item">
      <strong>${escapeHtml(s.base_substance_group || s.standardized_name || s.raw_name)}</strong>
      <span>${escapeHtml(s.raw_name)}；${escapeHtml(s.amount_raw || [s.amount, s.unit].filter(Boolean).join(" "))}</span>
      <span class="tag ${kind}">${escapeHtml(s.role_label)}${s.confirmed ? "" : "／待確認"}</span>
    </div>
  `).join("") : empty;
  return `<section class="detail-section"><h3>${escapeHtml(title)}</h3><div class="substance-list">${body}</div></section>`;
}

function renderFormulation() {
  const analyses = state.data.analyses;
  els.preservativeStats.innerHTML = statRows(analyses.preservatives.overall.slice(0, 12));
  els.preservativeFreeList.innerHTML = analyses.preservatives.confirmed_preservative_free_products.length
    ? analyses.preservatives.confirmed_preservative_free_products.map((p) => `<button class="product-card" type="button" data-product-id="${escapeAttr(p.product_id)}">${escapeHtml(p.chinese_name)}<span class="product-meta">${escapeHtml(p.license_number)}</span></button>`).join("")
    : `<div class="state">目前無明確無保存劑產品。</div>`;
  els.excipientStats.innerHTML = statRows(Object.entries(analyses.excipients.by_role).flatMap(([role, rows]) => rows.slice(0, 4).map((row) => ({ ...row, name: `${role}：${row.name}` }))).slice(0, 18));
  els.functionStats.innerHTML = Object.keys(analyses.excipients.by_role).map((role) => `<span class="tag excipient">${escapeHtml(role)}</span>`).join("");
  els.dosageComposition.innerHTML = Object.entries(analyses.excipients.by_dosage_form).map(([dosage, rows]) => `
    <div class="substance-item">
      <strong>${escapeHtml(state.data.dosage_labels[dosage] || dosage)}</strong>
      <span>${escapeHtml(rows.slice(0, 8).map((r) => `${r.name} (${r.count})`).join("、") || "資料不足")}</span>
    </div>
  `).join("");
  els.preservativeFreeList.querySelectorAll("button[data-product-id]").forEach((button) => {
    button.addEventListener("click", () => selectProduct(button.dataset.productId));
  });
}

function statRows(rows) {
  const max = Math.max(1, ...rows.map((r) => r.product_count || r.count || 0));
  return rows.map((row) => {
    const count = row.product_count || row.count || 0;
    return `
      <div class="stat-row">
        <strong>${escapeHtml(row.name)}</strong>
        <span>${count}</span>
        <div class="bar" aria-hidden="true"><span style="width:${Math.max(4, Math.round(count / max * 100))}%"></span></div>
      </div>
    `;
  }).join("");
}

function setEntry(entry) {
  state.entry = entry;
  const config = entryConfig[entry];
  els.searchLabel.textContent = config.label;
  els.entrySelectLabel.textContent = config.selectLabel;
  els.searchInput.placeholder = config.placeholder;
  els.formulationPanel.hidden = entry !== "formulation";
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("is-active", tab.dataset.entry === entry);
  });
  renderEntrySelect();
  renderResults();
}

function bindEvents() {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => setEntry(tab.dataset.entry));
  });
  els.searchInput.addEventListener("input", () => {
    state.query = els.searchInput.value;
    els.entrySelect.value = "";
    renderResults();
  });
  els.entrySelect.addEventListener("change", () => {
    state.query = els.entrySelect.value;
    els.searchInput.value = els.entrySelect.value;
    renderResults();
    scrollToResults();
  });
  els.jumpToResults.addEventListener("click", scrollToResults);
  [
    els.dosageFilter,
    els.legalFilter,
    els.therapyFilter,
    els.preservativeFilter,
    els.comboFilter,
    els.pfFilter,
    els.includeInactive,
  ].forEach((control) => control.addEventListener("change", () => {
    if (control === els.includeInactive) renderEntrySelect();
    renderResults();
  }));
}

async function init() {
  try {
    const response = await fetch("data/eye_meds/site_data.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    state.data = await response.json();
    renderSummary();
    renderFilters();
    renderFormulation();
    bindEvents();
    setEntry("indication");
  } catch (error) {
    els.results.setAttribute("aria-busy", "false");
    els.errorState.hidden = false;
    els.errorState.textContent = `${els.errorState.textContent}（${location.protocol}；${error.message}）`;
    els.resultSummary.textContent = "載入錯誤";
    console.error(error);
  }
}

init();
