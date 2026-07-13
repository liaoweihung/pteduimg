(function () {
  "use strict";

  const DATA_URL = "./data/eye_meds_rebuild_20260711/final/eye_meds_final.json?v=20260714";
  const PAGE_SIZE = 24;

  const state = {
    products: [],
    filtered: [],
    selectedId: "",
    page: 1,
    query: "",
    activeIngredientFilter: "",
    showAllIngredientStats: false,
    filters: {
      dosage: "",
      className: "",
      indication: "",
      year: "",
      status: "",
      ingredient: "",
    },
  };

  const els = {};

  document.addEventListener("DOMContentLoaded", init);

  async function init() {
    bindElements();
    bindEvents();
    await loadData();
  }

  function bindElements() {
    [
      "searchInput",
      "clearButton",
      "filterToggle",
      "filters",
      "dosageFilter",
      "classFilter",
      "indicationFilter",
      "yearFilter",
      "statusFilter",
      "ingredientFilter",
      "resultCount",
      "totalCount",
      "activeFilters",
      "ingredientStats",
      "listHeading",
      "resultList",
      "detailPanel",
      "prevPage",
      "nextPage",
      "pageInfo",
    ].forEach((id) => {
      els[id] = document.getElementById(id);
    });
  }

  function bindEvents() {
    els.searchInput.addEventListener("input", () => {
      state.query = els.searchInput.value.trim().toLowerCase();
      state.page = 1;
      applyFilters();
    });
    els.clearButton.addEventListener("click", clearFilters);
    els.filterToggle.addEventListener("click", () => {
      const open = els.filters.classList.toggle("open");
      els.filterToggle.setAttribute("aria-expanded", String(open));
    });
    [
      ["dosageFilter", "dosage"],
      ["classFilter", "className"],
      ["indicationFilter", "indication"],
      ["yearFilter", "year"],
      ["statusFilter", "status"],
      ["ingredientFilter", "ingredient"],
    ].forEach(([elementId, filterKey]) => {
      els[elementId].addEventListener("change", () => {
        state.filters[filterKey] = els[elementId].value;
        state.activeIngredientFilter = "";
        state.showAllIngredientStats = false;
        state.page = 1;
        applyFilters();
      });
    });
    els.prevPage.addEventListener("click", () => {
      state.page = Math.max(1, state.page - 1);
      renderResults();
    });
    els.nextPage.addEventListener("click", () => {
      const maxPage = Math.max(1, Math.ceil(state.filtered.length / PAGE_SIZE));
      state.page = Math.min(maxPage, state.page + 1);
      renderResults();
    });
  }

  async function loadData() {
    try {
      const response = await fetch(DATA_URL, { cache: "no-cache" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      state.products = (data.products || []).map(normalizeProduct);
      buildFilters();
      applyFilters();
      const first = state.filtered[0];
      if (first) selectProduct(first.product_id);
    } catch (error) {
      els.resultList.innerHTML = `<div class="empty-results">資料載入失敗：${escapeHtml(error.message)}</div>`;
      els.totalCount.textContent = "/ 0 筆正式產品";
    }
  }

  function normalizeProduct(product) {
    const substances = product.substances || [];
    const active = substances.filter((item) =>
      item.substance_role === "active" && item.confirmed_status === "confirmed"
    );
    const nonActive = substances.filter((item) => item.substance_role !== "active");
    const indications = product.indications || [];
    const classes = product.classes || [];
    const confirmedActiveNames = unique(
      active.map((item) => item.substance_normalized || item.substance_raw).filter(Boolean)
    );
    const indicationCategoryNames = unique(indications.map((item) => item.indication_category).filter(Boolean));
    const searchable = [
      product.chinese_name,
      product.english_name,
      product.license_number,
      product.indication_raw,
      product.drug_class,
      product.dosage_form_raw,
      product.dosage_form_normalized,
      ...active.map((item) => `${item.substance_raw} ${item.substance_normalized}`),
      ...indications.map((item) => item.indication_category),
    ].join(" ").toLowerCase();
    return {
      ...product,
      activeIngredients: active,
      confirmedActiveNames,
      nonActiveSubstances: nonActive,
      indicationCategories: indications,
      indicationCategoryNames,
      classItems: classes,
      searchable,
      hasConfirmedActive: active.length > 0,
    };
  }

  function buildFilters() {
    fillSelect(els.dosageFilter, "全部劑型", unique(state.products.map((p) => p.dosage_form_normalized)));
    fillSelect(els.classFilter, "全部分類", unique(state.products.map((p) => p.drug_class)));
    fillSelect(
      els.indicationFilter,
      "全部適應症大類",
      unique(state.products.flatMap((p) => p.indicationCategoryNames)).sort((a, b) =>
        displayIndicationCategory(a).localeCompare(displayIndicationCategory(b), "zh-Hant")
      ),
      displayIndicationCategory
    );
    fillSelect(els.yearFilter, "全部年份", unique(state.products.map((p) => p.license_year)).sort((a, b) => b.localeCompare(a)));
    fillSelect(els.statusFilter, "全部狀態", unique(state.products.map((p) => p.license_status)));
    els.totalCount.textContent = `/ ${state.products.length} 筆正式產品`;
  }

  function fillSelect(select, label, values, formatter = displayValue) {
    select.innerHTML = "";
    select.append(new Option(label, ""));
    values.filter(Boolean).forEach((value) => select.append(new Option(formatter(value), value)));
  }

  function applyFilters() {
    state.filtered = state.products.filter((product) => {
      if (state.query && !product.searchable.includes(state.query)) return false;
      if (state.filters.dosage && product.dosage_form_normalized !== state.filters.dosage) return false;
      if (state.filters.className && product.drug_class !== state.filters.className) return false;
      if (state.filters.indication && !product.indicationCategoryNames.includes(state.filters.indication)) return false;
      if (state.filters.year && product.license_year !== state.filters.year) return false;
      if (state.filters.status && product.license_status !== state.filters.status) return false;
      if (state.filters.ingredient === "confirmed" && !product.hasConfirmedActive) return false;
      if (state.filters.ingredient === "pending" && product.hasConfirmedActive) return false;
      if (state.activeIngredientFilter && !product.confirmedActiveNames.includes(state.activeIngredientFilter)) return false;
      return true;
    });
    if (!state.filtered.some((product) => product.product_id === state.selectedId)) {
      state.selectedId = state.filtered[0] ? state.filtered[0].product_id : "";
    }
    renderActiveFilters();
    renderIngredientStats();
    renderResults();
    renderDetail();
  }

  function renderActiveFilters() {
    const chips = [];
    if (state.query) chips.push(`搜尋：${state.query}`);
    if (state.filters.dosage) chips.push(`劑型：${displayValue(state.filters.dosage)}`);
    if (state.filters.className) chips.push(`分類：${state.filters.className}`);
    if (state.filters.indication) chips.push(`適應症：${displayIndicationCategory(state.filters.indication)}`);
    if (state.filters.year) chips.push(`年份：${state.filters.year}`);
    if (state.filters.status) chips.push(`狀態：${state.filters.status}`);
    if (state.filters.ingredient) chips.push(state.filters.ingredient === "confirmed" ? "有 confirmed active" : "有效成分待確認");
    if (state.activeIngredientFilter) chips.push(`有效成分：${state.activeIngredientFilter}`);
    els.activeFilters.innerHTML = chips.map((chip) => `<span class="filter-chip">${escapeHtml(chip)}</span>`).join("");
  }

  function renderIngredientStats() {
    const category = state.filters.indication;
    if (!category) {
      els.ingredientStats.hidden = true;
      els.ingredientStats.innerHTML = "";
      return;
    }

    const baseProducts = productsForIngredientStats();
    const denominator = baseProducts.length;
    const rows = ingredientStatsRows(baseProducts);
    const displayRows = state.showAllIngredientStats ? rows : rows.slice(0, 10);
    const categoryLabel = displayIndicationCategory(category);
    const activeName = state.activeIngredientFilter;

    els.ingredientStats.hidden = false;
    els.ingredientStats.innerHTML = `
      <div class="ingredient-stats-header">
        <div>
          <h2>${escapeHtml(categoryLabel)}類常見有效成分</h2>
          <p>共 ${denominator} 項產品，包含 ${rows.length} 種已確認有效成分</p>
        </div>
        ${activeName ? `<button class="secondary-button clear-ingredient-filter" type="button">清除成分條件</button>` : ""}
      </div>
      ${
        rows.length
          ? `<div class="ingredient-stat-list">
              ${displayRows.map((row) => renderIngredientStatRow(row, denominator, activeName)).join("")}
            </div>`
          : '<div class="empty-results">此適應症大類尚無已確認有效成分可統計。</div>'
      }
      ${
        rows.length > 10
          ? `<button class="secondary-button stats-toggle" type="button">${state.showAllIngredientStats ? "收合" : "顯示全部"}</button>`
          : ""
      }
    `;

    els.ingredientStats.querySelectorAll("[data-stat-ingredient]").forEach((button) => {
      button.addEventListener("click", () => toggleStatIngredient(button.dataset.statIngredient));
    });
    const clearButton = els.ingredientStats.querySelector(".clear-ingredient-filter");
    if (clearButton) clearButton.addEventListener("click", () => toggleStatIngredient(activeName));
    const toggleButton = els.ingredientStats.querySelector(".stats-toggle");
    if (toggleButton) {
      toggleButton.addEventListener("click", () => {
        state.showAllIngredientStats = !state.showAllIngredientStats;
        renderIngredientStats();
      });
    }
  }

  function productsForIngredientStats() {
    return state.products.filter((product) => {
      if (state.query && !product.searchable.includes(state.query)) return false;
      if (state.filters.dosage && product.dosage_form_normalized !== state.filters.dosage) return false;
      if (state.filters.className && product.drug_class !== state.filters.className) return false;
      if (state.filters.indication && !product.indicationCategoryNames.includes(state.filters.indication)) return false;
      if (state.filters.year && product.license_year !== state.filters.year) return false;
      if (state.filters.status && product.license_status !== state.filters.status) return false;
      if (state.filters.ingredient === "confirmed" && !product.hasConfirmedActive) return false;
      if (state.filters.ingredient === "pending" && product.hasConfirmedActive) return false;
      return true;
    });
  }

  function ingredientStatsRows(products) {
    const counts = new Map();
    products.forEach((product) => {
      new Set(product.confirmedActiveNames).forEach((name) => {
        counts.set(name, (counts.get(name) || 0) + 1);
      });
    });
    return Array.from(counts, ([name, count]) => ({ name, count })).sort((a, b) => {
      if (b.count !== a.count) return b.count - a.count;
      return a.name.localeCompare(b.name, "en", { sensitivity: "base" });
    });
  }

  function renderIngredientStatRow(row, denominator, activeName) {
    const percent = denominator ? (row.count / denominator) * 100 : 0;
    const isActive = row.name === activeName ? " active" : "";
    return `
      <button class="ingredient-stat${isActive}" type="button" data-stat-ingredient="${escapeAttr(row.name)}">
        <span class="stat-name">${escapeHtml(row.name)}</span>
        <span class="stat-count">${row.count} 項產品（${percent.toFixed(1)}%）</span>
        <span class="stat-bar" aria-hidden="true"><span style="width: ${percent.toFixed(1)}%"></span></span>
      </button>
    `;
  }

  function toggleStatIngredient(name) {
    state.activeIngredientFilter = state.activeIngredientFilter === name ? "" : name;
    state.page = 1;
    applyFilters();
  }

  function renderResults() {
    const maxPage = Math.max(1, Math.ceil(state.filtered.length / PAGE_SIZE));
    state.page = Math.min(state.page, maxPage);
    const start = (state.page - 1) * PAGE_SIZE;
    const visible = state.filtered.slice(start, start + PAGE_SIZE);

    els.resultCount.textContent = String(state.filtered.length);
    els.listHeading.textContent = resultHeading();
    els.pageInfo.textContent = `${state.page} / ${maxPage}`;
    els.prevPage.disabled = state.page <= 1;
    els.nextPage.disabled = state.page >= maxPage;

    if (!visible.length) {
      els.resultList.innerHTML = '<div class="empty-results">沒有符合條件的產品。</div>';
      return;
    }

    els.resultList.innerHTML = visible.map(renderCard).join("");
    els.resultList.querySelectorAll(".result-card").forEach((button) => {
      button.addEventListener("click", () => selectProduct(button.dataset.id));
    });
  }

  function resultHeading() {
    if (!state.filters.indication) return `查詢結果：${state.filtered.length} 項產品`;
    const category = displayIndicationCategory(state.filters.indication);
    if (state.activeIngredientFilter) {
      return `${category}／${state.activeIngredientFilter}：${state.filtered.length} 項產品`;
    }
    return `${category}：${state.filtered.length} 項產品`;
  }

  function renderCard(product) {
    const activeText = activeIngredientText(product);
    const indicationText = summarize(product.indication_raw, 96);
    const isActive = product.product_id === state.selectedId ? " active" : "";
    return `
      <button class="result-card${isActive}" type="button" data-id="${escapeAttr(product.product_id)}">
        <div class="card-title">
          <div>
            <h2>${escapeHtml(product.chinese_name || "未命名產品")}</h2>
            <p class="english">${escapeHtml(product.english_name || "")}</p>
          </div>
          <span class="license">${escapeHtml(product.license_number)}</span>
        </div>
        <div class="meta-row">
          <span class="pill">${escapeHtml(displayValue(product.dosage_form_normalized))}</span>
          <span class="pill">${escapeHtml(product.drug_class || "未分類")}</span>
          <span class="pill">${escapeHtml(product.license_year || "年份未列")}</span>
        </div>
        <p class="ingredient-line">${activeText}</p>
        <p class="indication-line">${escapeHtml(indicationText)}</p>
      </button>
    `;
  }

  function selectProduct(productId) {
    state.selectedId = productId;
    renderResults();
    renderDetail();
  }

  function renderDetail() {
    const product = state.products.find((item) => item.product_id === state.selectedId);
    if (!product) {
      els.detailPanel.innerHTML = '<div class="empty-detail">沒有可顯示的產品。</div>';
      return;
    }
    const active = product.activeIngredients;
    const preservatives = product.nonActiveSubstances.filter((item) => item.substance_role === "preservative");
    const excipients = product.nonActiveSubstances.filter((item) => !["preservative", "unknown"].includes(item.substance_role));
    const unknowns = product.nonActiveSubstances.filter((item) => item.substance_role === "unknown");
    const sources = product.sources || [];
    els.detailPanel.innerHTML = `
      <h2>${escapeHtml(product.chinese_name || "未命名產品")}</h2>
      <p class="english">${escapeHtml(product.english_name || "")}</p>
      <div class="detail-section">
        <h3>藥證與製劑</h3>
        <dl class="detail-list">
          ${detailRow("藥證字號", product.license_number)}
          ${detailRow("藥證狀態", product.license_status)}
          ${detailRow("藥證年份", product.license_year)}
          ${detailRow("原始劑型", product.dosage_form_raw)}
          ${detailRow("標準劑型", tagButton(product.dosage_form_normalized, "dosage", displayValue(product.dosage_form_normalized)))}
          ${detailRow("分類", tagButton(product.drug_class, "class"))}
        </dl>
      </div>
      <div class="detail-section">
        <h3>有效成分</h3>
        ${active.length ? substanceList(active, "ingredient") : '<p><span class="pending">有效成分待確認</span></p>'}
      </div>
      <div class="detail-section">
        <h3>適應症原文</h3>
        <p>${escapeHtml(product.indication_raw || "資料未提供")}</p>
        <div class="meta-row">
          ${(product.indications || []).map((item) => `<span class="pill">${escapeHtml(item.indication_category)}</span>`).join("")}
        </div>
      </div>
      <div class="detail-section">
        <h3>保存劑</h3>
        ${preservatives.length ? substanceList(preservatives) : '<p>資料未提供</p>'}
      </div>
      <div class="detail-section">
        <h3>其他賦形劑</h3>
        ${excipients.length ? substanceList(excipients) : '<p>資料未提供</p>'}
      </div>
      ${unknowns.length ? `<div class="detail-section"><h3>待確認成分</h3>${substanceList(unknowns)}</div>` : ""}
      <div class="detail-section">
        <h3>來源資訊</h3>
        ${sources.length ? sources.slice(0, 8).map((source) => `<p class="source-note">${escapeHtml(source.source_type)}：${escapeHtml(source.status || source.source_detail || "已記錄")}</p>`).join("") : '<p>資料未提供</p>'}
      </div>
    `;
    els.detailPanel.querySelectorAll("[data-filter-type]").forEach((button) => {
      button.addEventListener("click", () => applyLinkedFilter(button.dataset.filterType, button.dataset.value));
    });
  }

  function substanceList(items, mode) {
    return `
      <ul class="substance-list">
        ${items.map((item) => {
          const name = item.substance_normalized || item.substance_raw || "未命名成分";
          const strength = [item.strength, item.unit].filter(Boolean).join(" ");
          const label = mode === "ingredient" ? tagButton(name, "ingredient") : escapeHtml(name);
          return `
            <li>
              <strong>${label}</strong>
              ${item.substance_raw && item.substance_raw !== name ? `<div class="source-note">原始名稱：${escapeHtml(item.substance_raw)}</div>` : ""}
              <div class="source-note">角色：${escapeHtml(roleLabel(item.substance_role))}${strength ? `；含量：${escapeHtml(strength)}` : ""}</div>
              <div class="source-note">確認狀態：${escapeHtml(item.confirmed_status || "資料未提供")}</div>
            </li>
          `;
        }).join("")}
      </ul>
    `;
  }

  function tagButton(value, type, label) {
    if (!value) return "資料未提供";
    return `<button class="tag-button" type="button" data-filter-type="${escapeAttr(type)}" data-value="${escapeAttr(value)}">${escapeHtml(label || value)}</button>`;
  }

  function applyLinkedFilter(type, value) {
    if (type === "ingredient") {
      els.searchInput.value = value;
      state.query = value.toLowerCase();
      state.activeIngredientFilter = "";
    }
    if (type === "class") {
      state.filters.className = value;
      els.classFilter.value = value;
    }
    if (type === "dosage") {
      state.filters.dosage = value;
      els.dosageFilter.value = value;
    }
    state.page = 1;
    applyFilters();
  }

  function clearFilters() {
    state.query = "";
    state.activeIngredientFilter = "";
    state.showAllIngredientStats = false;
    state.filters = { dosage: "", className: "", indication: "", year: "", status: "", ingredient: "" };
    els.searchInput.value = "";
    els.dosageFilter.value = "";
    els.classFilter.value = "";
    els.indicationFilter.value = "";
    els.yearFilter.value = "";
    els.statusFilter.value = "";
    els.ingredientFilter.value = "";
    state.page = 1;
    applyFilters();
  }

  function activeIngredientText(product) {
    if (!product.activeIngredients.length) return '<span class="pending">有效成分待確認</span>';
    return `有效成分：${escapeHtml(product.activeIngredients.map((item) => item.substance_normalized || item.substance_raw).join("、"))}`;
  }

  function detailRow(label, value) {
    return `<div><dt>${escapeHtml(label)}</dt><dd>${typeof value === "string" ? value || "資料未提供" : value}</dd></div>`;
  }

  function unique(values) {
    return Array.from(new Set(values.filter(Boolean)));
  }

  function summarize(text, maxLength) {
    const value = text || "適應症資料未提供";
    return value.length > maxLength ? `${value.slice(0, maxLength)}…` : value;
  }

  function displayValue(value) {
    const labels = {
      ophthalmic_solution: "點眼液／眼用溶液",
      ophthalmic_ointment: "眼藥膏",
      ophthalmic_suspension: "眼用懸液",
      ophthalmic_gel: "眼用凝膠",
      ophthalmic_emulsion: "眼用乳劑",
      ophthalmic_other: "其他眼用製劑",
      active: "有效成分",
      preservative: "保存劑",
      vehicle: "溶媒／基劑",
      buffer: "緩衝劑",
      tonicity_agent: "等張調節劑",
      viscosity_agent: "黏度調節劑",
      chelator: "螯合劑",
      surfactant: "界面活性劑",
      antioxidant: "抗氧化劑",
      ph_adjuster: "酸鹼調節劑",
      ointment_base: "眼藥膏基劑",
      other_excipient: "其他賦形劑",
      unknown: "角色待確認",
    };
    return labels[value] || value || "資料未提供";
  }

  function displayIndicationCategory(value) {
    const labels = {
      "細菌感染": "抗菌",
    };
    return labels[value] || value || "資料未提供";
  }

  function roleLabel(role) {
    return displayValue(role);
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function escapeAttr(value) {
    return escapeHtml(value);
  }
})();
