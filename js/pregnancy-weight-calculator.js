(() => {
  const DAY = 86400000;
  const SECOND_TRIMESTER_START_DAYS = 91; // 13 週 0 天
  const TERM_DAYS = 280; // 40 週
  const MAX_GESTATION_DAYS = 294; // 42 週 0 天起不計算
  // 國民健康署《孕媽咪衛教手冊》「孕媽咪體重增加建議」表（與 113 年 3 月版《孕婦衛教手冊》第 31 頁相同）
  const TABLE = {
    underweight: { label: 'BMI < 18.5', single: [12.5, 18], twin: null, weekly: 0.5 },
    normal: { label: '18.5～24.9', single: [11.5, 16], twin: [16.8, 24.5], weekly: 0.5 },
    overweight: { label: '25.0～29.9', single: [7, 11.5], twin: [14.1, 22.7], weekly: 0.3 },
    obese: { label: '30.0 以上', single: [5, 9], twin: [11.4, 19.1], weekly: 0.25 }
  };

  const toDate = value => { if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '')) return null; const [y, m, d] = value.split('-').map(Number); const r = new Date(y, m - 1, d); return r.getFullYear() === y && r.getMonth() === m - 1 && r.getDate() === d ? r : null; };
  const addDays = (date, days) => { const d = new Date(date); d.setDate(d.getDate() + days); return d; };
  const diffDays = (a, b) => Math.round((a - b) / DAY);
  const round1 = x => Math.round(x * 10 + 1e-9) / 10;
  const fmt = x => x.toFixed(1);
  const num = (v, min, max) => { if (v === '' || v === null || v === undefined) return null; const n = Number(v); return Number.isFinite(n) && n >= min && n <= max ? n : null; };

  function bmiGroup(bmi) {
    if (bmi < 18.5) return 'underweight';
    if (bmi <= 24.9) return 'normal';
    if (bmi <= 29.9) return 'overweight';
    return 'obese';
  }

  // 快速結論：依序判斷，P（推估到 40 週總增重）等於上下限屬範圍內
  function conclude(r, range, weekly, days, fetus) {
    if (r.gain < 0) return { code: 'below_pre', tone: 'yellow' };
    if (range && r.gain > range[1]) return { code: 'over_max', tone: 'red', max: range[1] };
    if (!range) return { code: 'no_range', tone: 'neutral' };
    if (fetus === 'twin') return { code: 'twin_no_weekly', tone: 'neutral', max: range[1] };
    if (days < SECOND_TRIMESTER_START_DAYS) return { code: 'first_trimester', tone: 'neutral', max: range[1] };
    const projected = round1(r.gain + weekly * Math.max(0, TERM_DAYS - days) / 7);
    const base = { projected, rate: weekly, min: range[0], max: range[1] };
    if (projected > range[1]) return { code: 'proj_over', tone: 'yellow', ...base };
    if (projected < range[0]) return { code: 'proj_under', tone: 'yellow', ...base };
    return { code: 'proj_within', tone: 'green', ...base };
  }

  const ADVICE_TYPE = { over_max: 'over', proj_over: 'over', proj_under: 'under', below_pre: 'under', proj_within: 'general', first_trimester: 'general', twin_no_weekly: 'general', no_range: 'general' };

  // 純計算函式：輸入字串／數字，回傳結果物件或 { error }
  function compute(input, todayDate) {
    const height = num(input.height, 120, 200);
    if (height === null) return { error: '請輸入 120～200 公分之間的身高。', field: 'height' };
    const pre = num(input.preWeight, 30, 200);
    if (pre === null) return { error: '請輸入 30～200 公斤之間的孕前體重。', field: 'preWeight' };
    const current = num(input.currentWeight, 30, 250);
    if (current === null) return { error: '請輸入 30～250 公斤之間的目前體重。', field: 'currentWeight' };
    if (input.fetus !== 'single' && input.fetus !== 'twin') return { error: '請選擇胎數。', field: 'fetus' };

    let start = null;
    const due = toDate(input.dueDate);
    if (due) {
      start = addDays(due, -280);
      if (start > todayDate) return { error: '產檢確認預產期推算的懷孕起算日不可晚於今天。', field: 'dueDate' };
    } else {
      const lmp = toDate(input.lmp);
      if (!lmp || lmp > todayDate) return { error: '請輸入最後一次月經第一天，或填寫產檢確認預產期。', field: 'lmp' };
      start = lmp;
    }
    const days = diffDays(todayDate, start);
    if (days >= MAX_GESTATION_DAYS) return { error: '已超過本工具計算範圍，請依產檢醫師評估。', field: due ? 'dueDate' : 'lmp', gestationDays: days };

    const bmi = round1(pre * 10000 / (height * height));
    const group = bmiGroup(bmi);
    const row = TABLE[group];
    const gain = (Math.round(current * 10) - Math.round(pre * 10)) / 10;
    const result = {
      bmi, group, groupLabel: row.label, gestationDays: days,
      weeks: Math.floor(days / 7), dayRem: days % 7, basis: due ? 'dueDate' : 'lmp',
      gain, fetus: input.fetus, total: null, totalNote: null, reference: null, referenceNote: null, weekly: null
    };
    const range = input.fetus === 'twin' ? row.twin : row.single;
    if (range) result.total = range;
    else result.totalNote = '手冊未提供孕前 BMI 低於 18.5 的雙胞胎建議增重量，請與產檢醫師討論。';

    if (days < SECOND_TRIMESTER_START_DAYS) {
      result.referenceNote = '目前在第一期（未滿 13 週）。手冊未提供第一期的建議增重值，請依產檢醫師建議。';
    } else if (input.fetus === 'twin') {
      result.referenceNote = '手冊未提供雙胞胎每週增重值，請依產檢醫師建議。';
    } else {
      result.weekly = row.weekly;
      result.reference = round1(row.weekly * (days - SECOND_TRIMESTER_START_DAYS) / 7);
    }
    result.conclusion = conclude(result, range, row.weekly, days, input.fetus);
    result.conclusion.advice = ADVICE_TYPE[result.conclusion.code];
    return result;
  }

  window.PregnancyWeightCalc = { compute };

  if (typeof document === 'undefined' || !document.getElementById('gwg-form')) return;
  const $ = id => document.getElementById(id);
  const fieldIds = { height: 'gwg-height', preWeight: 'gwg-pre-weight', currentWeight: 'gwg-current-weight', fetus: 'gwg-fetus', lmp: 'gwg-lmp', dueDate: 'gwg-due-date' };
  const track = (name, params) => { if (typeof trackCalculatorEvent === 'function') trackCalculatorEvent(name, Object.assign({ calculator: 'pregnancy_weight' }, params)); };
  const now = () => { const d = new Date(); return new Date(d.getFullYear(), d.getMonth(), d.getDate()); };

  $('gwg-form').addEventListener('submit', event => {
    event.preventDefault();
    Object.values(fieldIds).forEach(id => $(id).removeAttribute('aria-invalid'));
    const r = compute({
      height: $('gwg-height').value, preWeight: $('gwg-pre-weight').value, currentWeight: $('gwg-current-weight').value,
      fetus: $('gwg-fetus').value, lmp: $('gwg-lmp').value, dueDate: $('gwg-due-date').value
    }, now());
    const resultCard = $('gwg-result');
    if (r.error) {
      $('gwg-error').textContent = r.error;
      if (r.field) $(fieldIds[r.field]).setAttribute('aria-invalid', 'true');
      resultCard.hidden = true;
      track('calculator_validation_error', { field: r.field || 'unknown' });
      return;
    }
    $('gwg-error').textContent = '';
    $('out-gestation').textContent = `${r.weeks} 週 ${r.dayRem} 天`;
    $('out-gestation-basis').textContent = r.basis === 'dueDate' ? '依產檢確認預產期推算' : '依最後一次月經推算';
    $('out-bmi').textContent = fmt(r.bmi);
    $('out-group').textContent = `屬「${r.groupLabel}」組`;
    $('out-total').textContent = r.total ? `${r.total[0]}～${r.total[1]} 公斤` : '無建議值';
    $('out-total-note').textContent = r.total ? `${r.fetus === 'twin' ? '雙胞胎' : '單胞胎'}，整個孕期建議增加的範圍。` : r.totalNote;
    const sign = r.gain > 0 ? '+' : r.gain < 0 ? '−' : '';
    $('out-gain').textContent = `${sign}${fmt(Math.abs(r.gain))} 公斤`;
    $('out-gain-note').textContent = '目前體重減去孕前體重。';
    if (r.reference !== null) {
      $('out-reference').textContent = `約 ${fmt(r.reference)} 公斤`;
      $('out-reference-note').textContent = `依手冊中、後期每週約 ${r.weekly} 公斤推估，從 13 週到現在的增重（不含第一期增加的體重）。此數字只供對照，實際增重請與產檢醫師討論。`;
    } else {
      $('out-reference').textContent = '不計算';
      $('out-reference-note').textContent = r.referenceNote;
    }
    const c = r.conclusion, kg = x => `${x} 公斤`;
    const texts = {
      below_pre: ['體重低於孕前', '目前體重低於孕前。手冊指出懷孕期間不適於減重，建議和產檢醫師討論。'],
      over_max: ['已超過建議上限', `已超過整個孕期建議增重上限（${kg(c.max)}）。建議和產檢醫師或營養師討論飲食與體重安排。`],
      proj_within: ['推估落在建議範圍內', `若照手冊每週約 ${c.rate} 公斤增加，到 40 週約增加 ${c.projected !== undefined ? fmt(c.projected) : ''} 公斤，落在建議範圍內（${c.min}～${c.max} 公斤）。`],
      proj_over: ['推估會超過建議範圍', `若照手冊每週約 ${c.rate} 公斤增加，到 40 週約增加 ${c.projected !== undefined ? fmt(c.projected) : ''} 公斤，會超過建議範圍（${c.min}～${c.max} 公斤），建議和產檢醫師討論。`],
      proj_under: ['推估會低於建議範圍', `若照手冊每週約 ${c.rate} 公斤增加，到 40 週約增加 ${c.projected !== undefined ? fmt(c.projected) : ''} 公斤，會低於建議範圍（${c.min}～${c.max} 公斤），建議和產檢醫師討論。`],
      first_trimester: ['尚未超過建議上限', `目前尚未超過整個孕期建議上限（${kg(c.max)}）。手冊沒有提供第一期（未滿 13 週）的每週建議，請依產檢醫師建議。`],
      twin_no_weekly: ['尚未超過建議上限', `目前尚未超過整個孕期建議上限（${kg(c.max)}）。手冊沒有提供雙胞胎的每週建議，請依產檢醫師建議。`],
      no_range: ['手冊無建議值', '手冊未提供孕前 BMI 低於 18.5 的雙胞胎建議增重量，請與產檢醫師討論。']
    }[c.code];
    const box = $('gwg-conclusion');
    box.className = `conclusion tone-${c.tone}`;
    $('conclusion-title').textContent = texts[0];
    $('conclusion-text').textContent = texts[1];
    document.querySelectorAll('[data-advice]').forEach(ul => { ul.hidden = ul.dataset.advice !== c.advice; });
    $('gwg-advice').open = false;
    resultCard.hidden = false;
    const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    resultCard.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    track('pregnancy_weight_calculate', { date_basis: r.basis === 'dueDate' ? 'due_date' : 'lmp' });
  });

  $('gwg-form').addEventListener('reset', () => { $('gwg-error').textContent = ''; $('gwg-result').hidden = true; track('calculator_reset', {}); });

  // 只記錄操作，不送出任何身高、體重、BMI、胎數或孕週
  document.querySelectorAll('[data-jump]').forEach(a => a.addEventListener('click', () => {
    track('conclusion_link_click', { target: a.dataset.jump });
    if (a.dataset.jump === 'faq') { const q = document.querySelector('[data-faq="q1"]'); if (q) q.open = true; }
  }));
  $('gwg-advice').addEventListener('toggle', () => {
    if (!$('gwg-advice').open) return;
    const shown = document.querySelector('[data-advice]:not([hidden])');
    track('advice_open', { type: shown ? shown.dataset.advice : 'none' });
  });
  document.querySelectorAll('.faq-item').forEach(item => item.addEventListener('toggle', () => { if (item.open) track('faq_open', { question: item.dataset.faq }); }));
  document.querySelectorAll('[data-track-source]').forEach(a => a.addEventListener('click', () => track('source_link_click', { source: a.dataset.trackSource })));
  document.querySelectorAll('[data-track-link]').forEach(a => a.addEventListener('click', () => track('related_link_click', { target: a.dataset.trackLink })));
})();

function trackFeedbackClick() {
  if (typeof shouldTrackAnalytics === 'function' && shouldTrackAnalytics()) gtag('event', 'click_feedback', { source_app: 'pteduimg' });
}
