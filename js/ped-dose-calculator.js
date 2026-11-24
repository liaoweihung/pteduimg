(function () {
  'use strict';

  var DATA_URL = './data/ped-dose.json?v=20261124';
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
  // months only matter under 3 years: show the field when years is 0-2
  function monthHidden() { return $('month-field').hidden; }
  function toggleMonth() {
    var ys = $('age-y').value.trim();
    var show = ys !== '' && Number(ys) >= 0 && Number(ys) < 3;
    $('month-field').hidden = !show;
    $('age-grid').classList.toggle('no-month', !show);
    if (!show) $('age-m').value = '';
  }
  function readInputs() {
    var yEl = $('age-y'), mEl = $('age-m'), wEl = $('weight');
    var errors = [];
    [yEl, mEl, wEl].forEach(function (el) { el.removeAttribute('aria-invalid'); });
    var ys = yEl.value.trim(), ms = mEl.value.trim(), ws = wEl.value.trim();
    var age = null, kg = null;
    if (ys !== '' || ms !== '') {
      var y = ys === '' ? 0 : Number(ys), m = (ms === '' || monthHidden()) ? 0 : Number(ms);
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

  function numericRule(rule, drug, kg) {
    var n = computeRule(rule, drug, kg);
    return n.num;
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
    return { main: main, extra: extra, num: { lo: lo, hi: hi, unit: unit, per: rule.per, isMax: !!rule.isMax, divide: rule.divide } };
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
      if (mode === 'pharmacist' && kg != null && !r.stop) { var eq = doseEquiv(drug, r.dose, kg); if (eq) sub.push(eq); }
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
    {
      var same = sameIngredient(drug);
      if (same.length) {
        html += '<p class="same-ing"><strong>同成分：</strong>' + same.map(function (d) {
          return '<button type="button" class="link-btn" data-goto="' + esc(d.id) + '">' + esc(d.name) + '（' + esc(d.ingredient) + '）</button>';
        }).join('、') + '</p>';
      }
    }
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
    renderRx();
  }

  // ---------- pharmacist: prescription check ----------
  function baseIngredient(d) {
    if (!d.mgPerMl && !d.mcgPerMl) return null;
    if (/、/.test(d.ingredient)) return null;
    return d.ingredient.split(' ')[0].toLowerCase();
  }
  function sameIngredient(drug) {
    var key = baseIngredient(drug);
    if (!key) return [];
    return drugs.filter(function (d) { return d.id !== drug.id && baseIngredient(d) === key; });
  }
  function parseDose(text) {
    // returns {per:'dose'|'day', lo, hi, dayMax}
    var m = /([\d.]+)(?:\s*～\s*([\d.]+))?\s*mL/.exec(text);
    if (!m) return null;
    var before = text.slice(0, m.index);
    var per = /每次/.test(before) || !/每日|每天/.test(before) ? 'dose' : 'day';
    var out = { per: per, lo: Number(m[1]), hi: Number(m[2] || m[1]) };
    var mx = /每日最多\s*([\d.]+)\s*mL/.exec(text);
    if (mx) out.dayMax = Number(mx[1]);
    return out;
  }
  function doseEquiv(drug, text, kg) {
    var p = parseDose(text);
    if (!p) return '';
    var conc = drug.mgPerMl || drug.mcgPerMl;
    if (!conc) return '';
    var u = drug.mgPerMl ? 'mg' : 'μg';
    return '≈ ' + range(p.lo * conc / kg, p.hi * conc / kg, u + '/kg') + (p.per === 'day' ? '／天' : '／次') + '（以 ' + fmt(kg) + ' kg 換算）';
  }
  function verdict(v, lo, hi, maxOnly) {
    var t = 0.03;
    if (!maxOnly && v < lo * (1 - t)) return ['low', '低於'];
    if (v > hi * (1 + t)) return ['high', '高於'];
    return ['ok', maxOnly ? '未超過' : '範圍內'];
  }
  function rxRow(label, v, lo, hi, unit, maxOnly, what) {
    var vd = verdict(v, lo, hi, maxOnly);
    return '<li class="rx-' + vd[0] + '"><span class="rx-mark">' + vd[1] + '</span><span>' + label +
      '<small>' + what + ' ' + (maxOnly ? '上限 ' + fmt(hi) + ' ' + unit : range(lo, hi, unit)) + '；處方 ' + fmt(v) + ' ' + unit + '</small></span></li>';
  }

  function renderRx() {
    var card = $('rx-card');
    var drug = drugs.filter(function (d) { return d.id === selectedId; })[0];
    if (!drug) { card.hidden = true; return; }
    card.hidden = false;
    var unit = drug.unit === 'mg' ? 'mg' : (drug.form === '粉劑' ? '包' : 'mL');
    $('rx-unit').textContent = unit;
    var out = $('rx-out');
    var input = readInputs();
    var age = input.age, kg = input.kg;
    var dose = parseFloat($('rx-dose').value), times = parseInt($('rx-times').value, 10);
    if (!(dose > 0)) { out.innerHTML = '<p class="prompt">輸入處方每次的量（和每日次數），換算 mg/kg 並比對下方各項參考範圍。</p>'; return; }
    var hasTimes = times > 0 && times <= 8;
    var day = hasTimes ? dose * times : null;
    var html = '<div class="rx-sum">';
    var conc = unit === 'mL' ? (drug.mgPerMl || drug.mcgPerMl) : (unit === 'mg' ? 1 : null);
    var cu = drug.mcgPerMl && unit === 'mL' ? 'μg' : 'mg';
    if (conc) {
      html += '<p><strong>每次</strong> ' + fmt(dose) + ' ' + unit + (unit === 'mL' ? ' ＝ ' + fmt(dose * conc) + ' ' + cu : '') +
        (kg != null ? ' ＝ <b>' + fmt(dose * conc / kg) + ' ' + cu + '/kg</b>' : '') + '</p>';
      if (hasTimes) html += '<p><strong>每天</strong> ' + fmt(day) + ' ' + unit + (unit === 'mL' ? ' ＝ ' + fmt(day * conc) + ' ' + cu : '') +
        (kg != null ? ' ＝ <b>' + fmt(day * conc / kg) + ' ' + cu + '/kg/day</b>' : '') + '</p>';
    } else {
      html += '<p><strong>每次</strong> ' + fmt(dose) + ' ' + unit + (hasTimes ? '，每天 ' + fmt(day) + ' ' + unit : '') + '</p>';
    }
    if (kg == null) html += '<p class="sub-note">輸入體重才能換算 mg/kg 並比對體重劑量。</p>';
    html += '</div>';

    var rows = [];
    var TAG = { public: '仿單', doctor: '醫師分享', pharmacist: '藥師參考' };
    matchRows(drug, age, kg).forEach(function (h) {
      if (h.row.stop) return;
      var pd = parseDose(h.row.dose);
      if (!pd || unit !== 'mL') return;
      var lbl = '仿單表：' + esc(h.row.label);
      if (pd.per === 'dose') rows.push(rxRow(lbl, dose, pd.lo, pd.hi, 'mL', false, '每次'));
      else if (hasTimes) rows.push(rxRow(lbl, day, pd.lo, pd.hi, 'mL', false, '每天'));
      if (pd.dayMax && hasTimes) rows.push(rxRow(lbl + '（每日上限）', day, pd.dayMax, pd.dayMax, 'mL', true, '每天'));
    });
    if (kg != null) {
      (drug.weight || []).forEach(function (rule) {
        if (ruleApplies(rule, age, kg) === false) return;
        var n = numericRule(rule, drug, kg);
        if (n.unit !== unit) return;
        var lbl = TAG[rule.audience] + '：' + esc(rule.label);
        if (n.per === 'dose') rows.push(rxRow(lbl, dose, n.lo, n.hi, unit, false, '每次'));
        else if (hasTimes) {
          var maxOnly = n.isMax && Math.abs(n.lo - n.hi) < 0.005;
          rows.push(rxRow(lbl, day, n.lo, n.hi, unit, maxOnly, '每天'));
        }
      });
    }
    if (rows.length) html += '<ul class="rx-list">' + rows.join('') + '</ul>';
    else html += '<p class="sub-note">' + (hasTimes ? '這支藥在目前的年齡／體重下沒有可比對的數值範圍。' : '填上每日次數，可以比對每日總量。') + '</p>';
    if (!hasTimes && rows.length) html += '<p class="sub-note">填上每日次數，可以再比對每日總量與上限。</p>';
    out.innerHTML = html;
  }

  var BY_KEY = 'pedDoseBy';
  var by = 'symptom';

  function ingredientNames(d) {
    return d.ingredient.split('、').map(function (part) {
      return part.replace(/（.*?）/g, '').trim().split(/\s+[\d.]/)[0].trim();
    }).filter(function (n) { return n && !/^[\d.]/.test(n); });
  }
  function ingredientIndex() {
    var map = {};
    drugs.forEach(function (d) {
      ingredientNames(d).forEach(function (n) { (map[n] = map[n] || []).push(d); });
    });
    return map;
  }
  function drugsFor(value) {
    if (by === 'name') return drugs.slice();
    if (value === '' || value == null) return [];
    if (by === 'symptom') {
      var terms = SYMPTOMS[Number(value)][1];
      return drugs.filter(function (d) { return (d.uses || []).some(function (u) { return terms.indexOf(u) >= 0; }); });
    }
    return ingredientIndex()[value] || [];
  }

  function renderBySelect() {
    Array.prototype.forEach.call(document.querySelectorAll('.by-tab'), function (t) {
      var on = t.getAttribute('data-by') === by;
      t.setAttribute('aria-selected', String(on));
      t.classList.toggle('is-active', on);
    });
    var field = $('by-field'), sel = $('by-select');
    if (by === 'name') { field.hidden = true; renderDrugSelect(); return; }
    field.hidden = false;
    if (by === 'symptom') {
      $('by-label').textContent = '症狀';
      sel.innerHTML = '<option value="">請選擇症狀</option>' + SYMPTOMS.map(function (sy, i) {
        return '<option value="' + i + '">' + esc(sy[0]) + '（' + drugsForSym(i) + '）</option>';
      }).join('');
    } else {
      $('by-label').textContent = '成分';
      var idx = ingredientIndex();
      var names = Object.keys(idx).sort(function (a, b) { return a.localeCompare(b, 'zh-Hant'); });
      sel.innerHTML = '<option value="">請選擇成分</option>' + names.map(function (n) {
        return '<option value="' + esc(n) + '">' + esc(n) + '（' + idx[n].length + '）</option>';
      }).join('');
    }
    renderDrugSelect();
  }
  function drugsForSym(i) {
    var terms = SYMPTOMS[i][1];
    return drugs.filter(function (d) { return (d.uses || []).some(function (u) { return terms.indexOf(u) >= 0; }); }).length;
  }

  function renderDrugSelect() {
    var list = drugsFor($('by-select').value);
    var field = $('drug-field'), sel = $('drug-select');
    if (by !== 'name' && !list.length) { field.hidden = true; return; }
    field.hidden = false;
    var groups = {};
    list.forEach(function (d) { (groups[d.group] = groups[d.group] || []).push(d); });
    var order = GROUP_ORDER.concat(Object.keys(groups).filter(function (g) { return GROUP_ORDER.indexOf(g) < 0; }));
    var html = '<option value="">請選擇藥水（' + list.length + ' 種）</option>';
    order.forEach(function (g) {
      if (!groups[g]) return;
      html += '<optgroup label="' + esc(g) + '">' + groups[g].map(function (d) {
        return '<option value="' + esc(d.id) + '">' + esc(d.name) + '</option>';
      }).join('') + '</optgroup>';
    });
    sel.innerHTML = html;
    sel.value = list.some(function (d) { return d.id === selectedId; }) ? selectedId : '';
  }

  function setBy(v, keep) {
    by = ['symptom', 'ingredient', 'name'].indexOf(v) >= 0 ? v : 'symptom';
    try { localStorage.setItem(BY_KEY, by); } catch (e) {}
    $('by-select').value = '';
    renderBySelect();
  }

  function selectDrug(id, opts) {
    if (id !== selectedId) { $('rx-dose').value = ''; $('rx-times').value = ''; }
    selectedId = id;
    renderResult();
    if ($('drug-select').value !== id) { setBy('name'); $('drug-select').value = id; }
    try {
      var u = new URL(location.href);
      u.searchParams.set('drug', id);
      history.replaceState(null, '', u.toString());
    } catch (e) {}
    if (opts && opts.scroll) $('dose-result').scrollIntoView({ behavior: 'smooth', block: 'start' });
    track('ped_dose_select', { drug_id: id, mode: mode, source: (opts && opts.source) || 'list' });
  }

  function init() {
    document.querySelector('.by-tabs').addEventListener('click', function (e) {
      var t = e.target.closest('[data-by]');
      if (t) { setBy(t.getAttribute('data-by')); track('ped_dose_by', { by: by }); }
    });
    $('by-select').addEventListener('change', function () {
      renderDrugSelect();
      if (this.value !== '') track('ped_dose_filter', { by: by, value: this.value });
    });
    $('drug-select').addEventListener('change', function () {
      if (this.value) selectDrug(this.value, { source: by });
    });
    ['rx-dose', 'rx-times'].forEach(function (id) { $(id).addEventListener('input', renderRx); });
    $('age-y').addEventListener('input', toggleMonth);
    ['age-y', 'age-m', 'weight'].forEach(function (id) { $(id).addEventListener('input', renderResult); });
    $('dose-result').addEventListener('click', function (e) {
      var g = e.target.closest('[data-goto]');
      if (g) { selectDrug(g.getAttribute('data-goto'), { source: 'same_ingredient' }); return; }
      var a = e.target.closest('[data-track]');
      if (a) track('ped_dose_card_click', { drug_id: selectedId, link: a.getAttribute('data-track') });
    });

    var params = new URLSearchParams(location.search);

    fetch(DATA_URL).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    }).then(function (json) {
      data = json;
      drugs = json.drugs || [];
      $('data-date').textContent = '資料整理日期：' + (json.updated || '');
      var savedBy = null;
      try { savedBy = localStorage.getItem(BY_KEY); } catch (e) {}
      setBy(savedBy || 'symptom');
      var want = params.get('drug');
      if (want && drugs.some(function (d) { return d.id === want; })) {
        selectedId = want;
        selectDrug(want, { source: 'link' });
      }
    }).catch(function () {
      $('drug-msg').textContent = '藥品資料載入失敗，請重新整理頁面。';
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
