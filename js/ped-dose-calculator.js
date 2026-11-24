(function () {
  'use strict';

  var DATA_URL = './data/ped-dose.json?v=20261124';
  var MODE_KEY = 'pedDoseMode';
  var GROUP_ORDER = ['退燒止痛', '感冒綜合', '止咳化痰', '鼻塞流鼻水', '過敏止癢', '氣喘', '腸胃', '類固醇'];
  var SYMPTOMS = [
    ['發燒／疼痛', ['發燒', '退燒', '疼痛', '頭痛', '牙痛', '喉嚨痛']],
    ['咳嗽', ['咳嗽', '止咳']],
    ['有痰', ['有痰', '化痰', '祛痰']],
    ['流鼻水／鼻塞', ['流鼻水', '鼻塞', '打噴嚏', '鼻炎', '過敏性鼻炎']],
    ['過敏／癢', ['過敏', '癢', '皮膚癢', '蕁麻疹', '眼癢', '鼻癢']],
    ['氣喘', ['氣喘', '喘', '喘鳴']],
    ['嘔吐', ['嘔吐', '噁心', '想吐']],
    ['腹瀉', ['腹瀉', '拉肚子', '止瀉']]
  ];

  var data = null;
  var drugs = [];
  var mode = 'public';
  var selectedId = null;
  var activeChip = null;

  function $(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function fmt(n) { return String(Math.round(n * 100) / 100); }
  function range(a, b, unit) {
    return (Math.abs(a - b) < 0.005 ? fmt(a) : fmt(a) + '～' + fmt(b)) + ' ' + unit;
  }
  function inAge(age, from, to) { return age >= (from || 0) && (to == null || age < to); }
  function ageLabel(m) {
    var y = Math.floor(m / 12), r = m % 12;
    if (y === 0) return r + ' 個月';
    return y + ' 歲' + (r ? ' ' + r + ' 個月' : '');
  }
  function track(name, params) {
    if (typeof window.trackCalculatorEvent === 'function') window.trackCalculatorEvent(name, params);
  }

  // ---------- inputs ----------
  function readInputs() {
    var yEl = $('age-y'), mEl = $('age-m'), wEl = $('weight');
    var errors = [];
    [yEl, mEl, wEl].forEach(function (el) { el.removeAttribute('aria-invalid'); });
    var ys = yEl.value.trim(), ms = mEl.value.trim(), ws = wEl.value.trim();
    var age = null, kg = null;
    if (ys !== '' || ms !== '') {
      var y = ys === '' ? 0 : Number(ys), m = ms === '' ? 0 : Number(ms);
      if (!isFinite(y) || y < 0 || y > 18 || Math.floor(y) !== y) { errors.push('年齡請填 0～18 的整數歲。'); yEl.setAttribute('aria-invalid', 'true'); }
      else if (!isFinite(m) || m < 0 || m > 11 || Math.floor(m) !== m) { errors.push('月數請填 0～11。'); mEl.setAttribute('aria-invalid', 'true'); }
      else age = y * 12 + m;
    }
    if (ws !== '') {
      var w = Number(ws);
      if (!isFinite(w) || w < 2 || w > 100) { errors.push('體重請填 2～100 公斤。'); wEl.setAttribute('aria-invalid', 'true'); }
      else kg = w;
    }
    $('input-error').textContent = errors.join(' ');
    return { age: age, kg: kg };
  }

  // ---------- matching ----------
  function kgCondition(row, kg) {
    // returns true / false / null (unknown)
    var has = row.kgFrom != null || row.kgFromExcl != null || row.kgTo != null;
    if (!has) return true;
    if (kg == null) return null;
    if (row.kgFrom != null && kg < row.kgFrom) return false;
    if (row.kgFromExcl != null && kg <= row.kgFromExcl) return false;
    if (row.kgTo != null) {
      if (row.kgToIncl ? kg > row.kgTo : kg >= row.kgTo) return false;
    }
    return true;
  }

  function matchRows(drug, age, kg) {
    var table = drug.age;
    if (!table) return [];
    var hits = [];
    table.rows.forEach(function (row) {
      if (table.rowMatch === 'kgFirst' && kg != null && row.kgFrom != null) {
        if (kgCondition(row, kg)) {
          hits.push({ row: row, mismatch: age != null && !inAge(age, row.from, row.to) });
        }
        return;
      }
      if (table.rowMatch === 'kgFirst' && kg != null && row.kgFrom == null && age == null) return;
      if (age == null) return;
      if (!inAge(age, row.from, row.to)) return;
      var kc = table.rowMatch === 'kgFirst' ? true : kgCondition(row, kg);
      if (kc === false) return;
      hits.push({ row: row, maybe: kc === null });
    });
    return hits;
  }

  function condState(c, age, kg) {
    var states = [];
    if (c.ageFrom != null || c.ageTo != null) states.push(age == null ? null : inAge(age, c.ageFrom, c.ageTo));
    if (c.kgTo != null) states.push(kg == null ? null : kg < c.kgTo);
    if (states.indexOf(false) >= 0) return false;
    if (states.indexOf(null) >= 0) return null;
    return true;
  }

  function ruleApplies(rule, age, kg) {
    var own = condState(rule, age, kg);
    if (own === false) return false;
    if (!rule.anyOf) return own;
    var any = rule.anyOf.map(function (c) { return condState(c, age, kg); });
    if (any.indexOf(true) >= 0) return own;
    if (any.indexOf(null) >= 0) return null;
    return false;
  }

  function computeRule(rule, drug, kg) {
    var lo, hi, unit = 'mL', capped = false;
    if (rule.mlPerKg) { lo = kg * rule.mlPerKg[0]; hi = kg * rule.mlPerKg[1]; }
    else if (rule.mgPerKg) {
      lo = kg * rule.mgPerKg[0]; hi = kg * rule.mgPerKg[1];
      if (drug.mgPerMl && drug.unit !== 'mg') { lo /= drug.mgPerMl; hi /= drug.mgPerMl; }
      else unit = 'mg';
    }
    if (rule.maxDoseMl != null && unit === 'mL' && hi > rule.maxDoseMl) { hi = rule.maxDoseMl; lo = Math.min(lo, hi); capped = true; }
    if (rule.maxDoseMg != null && unit === 'mg' && hi > rule.maxDoseMg) { hi = rule.maxDoseMg; lo = Math.min(lo, hi); capped = true; }

    var main, extra = [];
    if (rule.per === 'dose') main = '每次 ' + range(lo, hi, unit);
    else if (rule.isMax && Math.abs(lo - hi) < 0.005) main = '一天最多 ' + range(lo, hi, unit);
    else main = '一天總量 ' + range(lo, hi, unit);
    if (rule.per === 'day' && rule.divide) {
      main += '，分 ' + (rule.divide[0] === rule.divide[1] ? rule.divide[0] : rule.divide[0] + '～' + rule.divide[1]) + ' 次';
      extra.push('每次約 ' + range(lo / rule.divide[1], hi / rule.divide[0], unit));
    }
    if (capped) extra.push('已達每次上限');
    if (mode === 'pharmacist' && unit === 'mL') {
      if (drug.mgPerMl) extra.push('＝ ' + range(lo * drug.mgPerMl, hi * drug.mgPerMl, 'mg') + (rule.per === 'day' ? '／天' : ''));
      if (drug.mcgPerMl) extra.push('＝ ' + range(lo * drug.mcgPerMl, hi * drug.mcgPerMl, 'μg'));
    }
    return { main: main, extra: extra };
  }

  // ---------- rendering ----------
  function answer(cls, title, big, sub) {
    return '<div class="answer ' + cls + '"><h3>' + title + '</h3><p class="big">' + esc(big) + '</p>' +
      (sub ? '<p class="sub">' + sub + '</p>' : '') + '</div>';
  }

  function renderResult() {
    var box = $('dose-result');
    var drug = drugs.filter(function (d) { return d.id === selectedId; })[0];
    if (!drug) { box.hidden = true; box.innerHTML = ''; return; }
    var input = readInputs();
    var age = input.age, kg = input.kg;
    var cardUrl = './cards/' + drug.id + '.html';
    var badge = drug.rx === true ? '<span class="badge rx">處方藥</span>' : drug.rx === false ? '<span class="badge otc">指示藥</span>' : '';
    var html = '<div class="result-head"><div style="flex:1;min-width:0">' +
      '<h2 id="result-title">' + esc(drug.name) + badge + '</h2>' +
      '<p class="result-meta">' + esc(drug.ingredient) + '・' + esc(drug.form) + '</p>' +
      '</div><a class="card-thumb" href="' + cardUrl + '" data-track="card_thumb"><img src="./' + esc(drug.image) + '" alt="' + esc(drug.name) + ' 衛教圖卡" loading="lazy">看圖卡 ›</a></div>';

    var stopped = false;
    var blocks = '';

    if (age == null && kg == null) {
      blocks += '<p class="prompt">輸入上方的年齡或體重，就會標出對應的用量。</p>';
    }

    if (drug.ageRange && age != null && !inAge(age, drug.ageRange.from, drug.ageRange.to)) {
      stopped = true;
      blocks += answer('stop', '年齡 ' + ageLabel(age), drug.ageRange.outside, '');
    }

    var hits = matchRows(drug, age, kg);
    hits.forEach(function (h) {
      var r = h.row;
      if (r.stop) stopped = true;
      var cls = r.stop ? 'stop' : (r.caution ? 'caution' : '');
      var sub = [];
      if (h.maybe) sub.push('這一列要看體重，填上體重會更準確。');
      if (h.mismatch) sub.push('孩子的年齡和體重落在仿單不同組，請照藥袋或問醫師藥師。');
      if (r.caution) sub.push(esc(r.caution));
      if (r.note) sub.push(esc(r.note));
      blocks += answer(cls, '<span class="tag">' + esc(drug.age.source) + '</span>' + esc(r.label), r.dose, sub.join('<br>'));
    });
    if (drug.age && (age != null || kg != null) && hits.length === 0) {
      blocks += answer('', '依年齡', drug.age.otherwise || '表上沒有對應的年齡組，請照藥袋或問藥師。', '');
    }
    if (drug.noAgeTable && (age != null || kg != null)) {
      blocks += '<p class="prompt">' + esc(drug.noAgeTable) + '</p>';
    }

    var RANK = { public: 0, doctor: 1, pharmacist: 2 };
    (drug.weight || []).slice().sort(function (a, b) { return RANK[a.audience] - RANK[b.audience]; }).forEach(function (rule) {
      var isPharm = rule.audience === 'pharmacist';
      var isDoctor = rule.audience === 'doctor';
      if (isPharm && mode !== 'pharmacist') return;
      if (stopped && !isDoctor && mode !== 'pharmacist') return;
      var applies = ruleApplies(rule, age, kg);
      if (applies === false) return;
      var tagText = isPharm ? '藥師參考' : isDoctor ? '醫師分享劑量' : '依體重（仿單）';
      var tag = '<span class="tag">' + tagText + '</span>' + esc(rule.label);
      var sub = [];
      var big;
      if (kg == null) {
        big = '輸入體重可以算出 ' + (drug.unit === 'mg' ? 'mg' : 'mL');
      } else {
        var c = computeRule(rule, drug, kg);
        big = c.main;
        sub = sub.concat(c.extra);
      }
      if (applies === null) sub.push('適用條件見上方說明，請確認孩子的年齡或體重符合。');
      if (isDoctor) sub.push('仿單以外、醫師開藥時常用的參考量；請依醫師處方，藥袋不同時以藥袋為準。');
      else if (stopped) sub.push('⚠ 此年齡仿單不建議自行使用，以上僅供藥師核對處方。');
      sub.push((isDoctor ? '分享者：' : '依據：') + esc(rule.source));
      blocks += answer(isPharm ? 'pharm' : isDoctor ? 'doctor' : '', tag, big, sub.join('<br>'));
    });

    html += blocks;
    if (drug.frequency) html += '<p class="freq"><strong>多久一次：</strong>' + esc(drug.frequency) + '</p>';

    if (drug.age && drug.age.rows.length > 1) {
      var hitRows = hits.map(function (h) { return h.row; });
      html += '<table class="dose-table"><caption>仿單用量表（' + esc(drug.age.source) + '）</caption><thead><tr><th scope="col">年齡／體重</th><th scope="col">用量</th></tr></thead><tbody>';
      drug.age.rows.forEach(function (r) {
        html += '<tr' + (hitRows.indexOf(r) >= 0 ? ' class="hit"' : '') + '><td>' + esc(r.label) + '</td><td>' + esc(r.dose) + '</td></tr>';
      });
      html += '</tbody></table>';
    }

    if (drug.notes && drug.notes.length) {
      html += '<ul class="info-list">' + drug.notes.map(function (n) { return '<li>' + esc(n) + '</li>'; }).join('') + '</ul>';
    }
    html += '<p class="bag-note">藥袋寫的用量和這裡不同時，請照藥袋給；有疑問先問開藥的醫師或藥師。</p>';
    html += '<p class="card-link-row"><a class="card-link" href="' + cardUrl + '" data-track="card_button">看「' + esc(drug.name) + '」圖卡與完整說明 ›</a></p>';
    if (drug.refs && drug.refs.length) {
      html += '<div class="ref-block"><h3>出處</h3><ul class="ref-list">' + drug.refs.map(function (r) {
        return '<li><a href="' + esc(r.url) + '" target="_blank" rel="noopener">' + esc(r.title) + '</a></li>';
      }).join('') + '</ul></div>';
    }

    box.innerHTML = html;
    box.hidden = false;
  }

  function matchesQuery(d, q) {
    if (!q) return true;
    var hay = [d.name, d.ingredient, d.group, d.form].concat(d.aliases || [], d.uses || []).join(' ').toLowerCase();
    return q.toLowerCase().split(/\s+/).every(function (t) { return !t || hay.indexOf(t) >= 0; });
  }

  function renderList() {
    var q = $('drug-search').value.trim();
    var chipTerms = activeChip != null ? SYMPTOMS[activeChip][1] : null;
    var list = drugs.filter(function (d) {
      if (!matchesQuery(d, q)) return false;
      if (chipTerms) return (d.uses || []).some(function (u) { return chipTerms.indexOf(u) >= 0; });
      return true;
    });
    var box = $('drug-list');
    if (!list.length) { box.innerHTML = '<p class="empty-note">找不到符合的藥水。可以換個寫法，或用成分名（例如 Ibuprofen）找。</p>'; return; }
    var groups = {};
    list.forEach(function (d) { (groups[d.group] = groups[d.group] || []).push(d); });
    var order = GROUP_ORDER.concat(Object.keys(groups).filter(function (g) { return GROUP_ORDER.indexOf(g) < 0; }));
    box.innerHTML = order.filter(function (g) { return groups[g]; }).map(function (g) {
      return '<div class="drug-group"><h3>' + esc(g) + '</h3><div class="drug-buttons">' + groups[g].map(function (d) {
        return '<button type="button" class="drug-btn" data-id="' + esc(d.id) + '"' + (d.id === selectedId ? ' aria-current="true"' : '') + '>' +
          esc(d.name) + '<small>' + esc(d.ingredient.split('（')[0]) + '</small></button>';
      }).join('') + '</div></div>';
    }).join('');
  }

  function selectDrug(id, opts) {
    selectedId = id;
    renderResult();
    renderList();
    try {
      var u = new URL(location.href);
      u.searchParams.set('drug', id);
      history.replaceState(null, '', u.toString());
    } catch (e) {}
    if (opts && opts.scroll) $('dose-result').scrollIntoView({ behavior: 'smooth', block: 'start' });
    track('ped_dose_select', { drug_id: id, mode: mode, source: (opts && opts.source) || 'list' });
  }

  function setMode(m) {
    mode = m === 'pharmacist' ? 'pharmacist' : 'public';
    document.body.classList.toggle('is-pharmacist', mode === 'pharmacist');
    Array.prototype.forEach.call(document.querySelectorAll('.mode-btn'), function (b) {
      b.setAttribute('aria-checked', String(b.getAttribute('data-mode') === mode));
    });
    $('mode-hint').textContent = mode === 'pharmacist'
      ? '藥師版：另外顯示藥師參考範圍與 mg 換算，供核對處方。'
      : '民眾版：顯示仿單用量，以及醫師分享的參考劑量。';
    try { localStorage.setItem(MODE_KEY, mode); } catch (e) {}
    renderResult();
  }

  function init() {
    var chips = $('symptom-chips');
    chips.innerHTML = SYMPTOMS.map(function (s, i) {
      return '<button type="button" class="chip" data-chip="' + i + '" aria-pressed="false">' + esc(s[0]) + '</button>';
    }).join('');
    chips.addEventListener('click', function (e) {
      var b = e.target.closest('[data-chip]');
      if (!b) return;
      var i = Number(b.getAttribute('data-chip'));
      activeChip = activeChip === i ? null : i;
      Array.prototype.forEach.call(chips.children, function (c, j) { c.setAttribute('aria-pressed', String(j === activeChip)); });
      renderList();
      if (activeChip != null) track('ped_dose_symptom', { symptom: SYMPTOMS[i][0] });
    });
    $('drug-list').addEventListener('click', function (e) {
      var b = e.target.closest('[data-id]');
      if (b) selectDrug(b.getAttribute('data-id'), { scroll: true });
    });
    $('drug-search').addEventListener('input', renderList);
    ['age-y', 'age-m', 'weight'].forEach(function (id) { $(id).addEventListener('input', renderResult); });
    document.querySelector('.mode-switch').addEventListener('click', function (e) {
      var b = e.target.closest('[data-mode]');
      if (b) { setMode(b.getAttribute('data-mode')); track('ped_dose_mode', { mode: mode }); }
    });
    $('dose-result').addEventListener('click', function (e) {
      var a = e.target.closest('[data-track]');
      if (a) track('ped_dose_card_click', { drug_id: selectedId, link: a.getAttribute('data-track') });
    });

    var params = new URLSearchParams(location.search);
    var savedMode = null;
    try { savedMode = localStorage.getItem(MODE_KEY); } catch (e) {}
    setMode(params.get('mode') || savedMode || 'public');

    fetch(DATA_URL).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    }).then(function (json) {
      data = json;
      drugs = json.drugs || [];
      $('data-date').textContent = '資料整理日期：' + (json.updated || '');
      renderList();
      var want = params.get('drug');
      if (want && drugs.some(function (d) { return d.id === want; })) {
        selectDrug(want, { source: 'link' });
      }
    }).catch(function () {
      $('drug-list').innerHTML = '<p class="empty-note">藥品資料載入失敗，請重新整理頁面。</p>';
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
