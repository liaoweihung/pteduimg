(() => {
  const $ = id => document.getElementById(id);
  const DAY = 86400000;
  const toDate = value => { if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '')) return null; const [y,m,d] = value.split('-').map(Number); const result = new Date(y,m-1,d); return result.getFullYear() === y && result.getMonth() === m-1 && result.getDate() === d ? result : null; };
  const today = () => { const d = new Date(); return new Date(d.getFullYear(), d.getMonth(), d.getDate()); };
  const addDays = (date, days) => { const d = new Date(date); d.setDate(d.getDate() + days); return d; };
  const diffDays = (a,b) => Math.round((a - b) / DAY);
  const showDate = date => `${date.getFullYear()}/${String(date.getMonth()+1).padStart(2,'0')}/${String(date.getDate()).padStart(2,'0')}`;
  const showShortDate = date => `${date.getMonth()+1} 月 ${date.getDate()} 日`;
  const set = (id, value) => $(id).textContent = value;
  const ageText = days => `${Math.floor(days / 7)} 週 ${days % 7} 天`;

  function basicData() {
    const lmp = toDate($('lmp').value); const cycle = Number($('cycle-length').value);
    if (!lmp) return { error:'請選擇最後一次月經第一天。' };
    if (lmp > today()) return { error:'最後一次月經第一天不可晚於今天。' };
    if (!Number.isInteger(cycle) || cycle < 21 || cycle > 45) return { error:'平均月經週期請輸入 21～45 天的整數。' };
    return { lmp, cycle, next:addDays(lmp,cycle), ovulation:addDays(lmp,cycle-14) };
  }
  function updateInduce() {
    const start = toDate($('induce-start').value); const custom = $('induce-days').value === 'custom'; $('custom-days-wrap').hidden = !custom;
    const days = custom ? Number($('custom-days').value) : Number($('induce-days').value);
    $('induce-message').textContent = '';
    if (!start) { set('induce-course','請選擇療程開始日'); set('withdrawal-bleed','--'); return; }
    if (!Number.isInteger(days) || days <= 0) { set('induce-course','--'); set('withdrawal-bleed','--'); $('induce-message').textContent='療程天數須大於 0。'; return; }
    const last = addDays(start,days-1); set('induce-course',`${showDate(start)} ～ ${showDate(last)}`); set('withdrawal-bleed',`約 ${showDate(addDays(last,3))} ～ ${showDate(addDays(last,7))}`);
  }
  function updatePregnancy(data) {
    const now = today(); $('pregnancy-message').textContent = '';
    if (data.error) { set('lmp-due-date','請先輸入日期'); set('gestational-age','--'); set('gestation-on-result','--'); }
    else { const due = addDays(data.lmp,280); set('lmp-due-date',showDate(due)); set('gestational-age',ageText(diffDays(now,data.lmp))); const chosen = toDate($('gestation-on-date').value); if (chosen) { const d = diffDays(chosen,data.lmp); if (d < 0) { set('gestation-on-result','指定日期不可早於最後一次月經。'); $('pregnancy-message').textContent='指定日期不可早於最後一次月經第一天。'; } else set('gestation-on-result',`${showDate(chosen)}：${ageText(d)}`); } }
    const conception = toDate($('conception-date').value); set('conception-due-date',conception ? showDate(addDays(conception,266)) : '--');
    const confirmed = toDate($('confirmed-due-date').value); if (confirmed) { const d = diffDays(now,addDays(confirmed,-280)); set('confirmed-gestation', d < 0 ? '尚未到推估懷孕起算日' : ageText(d)); } else set('confirmed-gestation','--');
  }
  function updateAll() {
    const data = basicData(); $('basic-message').textContent = data.error || '';
    if (data.error) { ['next-period','ovulation-date','delay-start','lmp-due-date'].forEach(id=>set(id,'請先輸入日期')); ['cycle-day','following-period','period-countdown','fertile-window','ovulation-countdown','delay-period','delay-stop','delay-bleed','delay-status','late-period'].forEach(id=>set(id,'--')); updatePregnancy(data); updateInduce(); return; }
    const now = today(), following = addDays(data.next,data.cycle), cycleDay = diffDays(now,data.lmp) + 1, daysToPeriod = diffDays(data.next,now), daysToOvulation = diffDays(data.ovulation,now);
    set('next-period',showShortDate(data.next)); set('following-period',showDate(following)); set('cycle-day', cycleDay > 0 ? cycleDay : '--'); set('period-countdown', daysToPeriod >= 0 ? `距離預估月經還有 ${daysToPeriod} 天` : `預估月經已過 ${Math.abs(daysToPeriod)} 天`);
    set('ovulation-date',showShortDate(data.ovulation)); set('fertile-window',`${showDate(addDays(data.ovulation,-5))} ～ ${showDate(addDays(data.ovulation,1))}`); set('ovulation-countdown',daysToOvulation >= 0 ? `距離預估排卵日還有 ${daysToOvulation} 天` : `預估排卵日已過 ${Math.abs(daysToOvulation)} 天`);
    const delayUntil = toDate($('delay-until').value);
    const crossesNextCycle = delayUntil && delayUntil >= following;
    const delayBase = crossesNextCycle ? following : data.next;
    const delayStart = addDays(delayBase,-5);
    set('delay-start',showShortDate(delayStart)); set('delay-period',showDate(delayBase));
    const timingStatus = now >= delayBase ? '月經已開始後，不屬於一般延經開始時機。' : diffDays(delayBase,now) >= 3 ? '尚在一般延經開始評估時間內。' : '距離預估月經時間較短，延經效果可能較不穩定。';
    if (delayUntil) { if (delayUntil < data.next) { set('delay-stop','--'); set('delay-bleed','--'); set('delay-status','希望延經日期不可早於預估月經日。'); } else { set('delay-stop',showDate(delayUntil)); set('delay-bleed',`約 ${showDate(addDays(delayUntil,2))} ～ ${showDate(addDays(delayUntil,3))}`); set('delay-status',crossesNextCycle ? `希望延經日已到下一個週期，已以下個週期第一天 ${showDate(following)} 作為計算基準。${timingStatus}` : timingStatus); } } else { set('delay-stop','請選擇希望延經日期'); set('delay-bleed','--'); set('delay-status',timingStatus); }
    set('late-period',daysToPeriod > 0 ? `預估月經：${showDate(data.next)}（尚有 ${daysToPeriod} 天）` : `預估月經：${showDate(data.next)}（晚約 ${Math.abs(daysToPeriod)} 天）`);
    updatePregnancy(data); updateInduce();
  }
  ['lmp','cycle-length','delay-until','induce-start','induce-dose','induce-days','custom-days','conception-date','confirmed-due-date','gestation-on-date'].forEach(id => $(id).addEventListener('input',updateAll));
  $('induce-days').addEventListener('change',updateAll); updateAll();
  const dateInputCounts = {};
  ['lmp','delay-until','induce-start','conception-date','confirmed-due-date','gestation-on-date'].forEach(id => {
    $(id).addEventListener('change', () => {
      if (!$(id).value) return;
      dateInputCounts[id] = (dateInputCounts[id] || 0) + 1;
      trackCalculatorEvent('calculator_date_input', { field: id, session_input_count: dateInputCounts[id] });
    });
  });
  const cards = [...document.querySelectorAll('.feature-card')];
  const allCardsButton = $('toggle-all-cards');
  function setCardExpanded(card, expanded) {
    card.classList.toggle('is-collapsed', !expanded);
    card.querySelector('.card-heading').setAttribute('aria-expanded', String(expanded));
  }
  function updateAllCardsButton() {
    const allExpanded = cards.every(card => !card.classList.contains('is-collapsed'));
    allCardsButton.textContent = allExpanded ? '全部收合' : '全部展開';
    allCardsButton.setAttribute('aria-expanded', String(allExpanded));
  }
  cards.forEach(card => card.querySelector('.card-heading').addEventListener('click', () => {
    const expanded = card.classList.contains('is-collapsed');
    setCardExpanded(card, expanded);
    trackCalculatorEvent('calculator_card_toggle', { card: card.id.replace('-card', ''), action: expanded ? 'expand' : 'collapse' });
    updateAllCardsButton();
  }));
  allCardsButton.addEventListener('click', () => {
    const expand = cards.some(card => card.classList.contains('is-collapsed'));
    cards.forEach(card => setCardExpanded(card, expand));
    trackCalculatorEvent('calculator_card_toggle', { card: 'all_cards', action: expand ? 'expand' : 'collapse' });
    updateAllCardsButton();
  });
  updateAllCardsButton();
  if ('serviceWorker' in navigator) window.addEventListener('load', () => navigator.serviceWorker.register('./sw.js').catch(() => {}));
})();
