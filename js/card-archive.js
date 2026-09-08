(() => {
  const search = document.getElementById('archive-search');
  if (search) {
    const records = [...document.querySelectorAll('.archive-record')];
    const clear = document.getElementById('clear-search');
    function filter() {
      const words = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      let count = 0;
      records.forEach(record => {
        record.hidden = !words.every(word => record.dataset.search.toLocaleLowerCase().includes(word));
        if (!record.hidden) count++;
      });
      document.getElementById('archive-count').textContent = words.length ? `${count} 筆符合搜尋，共 ${records.length} 筆退出紀錄` : `共 ${records.length} 筆退出紀錄`;
      document.getElementById('no-results').hidden = count !== 0;
      clear.hidden = words.length === 0;
    }
    search.addEventListener('input', filter);
    clear.addEventListener('click', () => { search.value = ''; filter(); search.focus(); });
  }
  if ('serviceWorker' in navigator) {
    const root = new URL('../', document.currentScript ? document.currentScript.src : new URL('js/card-archive.js', document.baseURI));
    const button = document.getElementById('archive-update');
    navigator.serviceWorker.register(new URL('sw.js', root).href).then(reg => {
      const show = () => { if (navigator.serviceWorker.controller) button.hidden = false; };
      if (reg.waiting) show();
      reg.addEventListener('updatefound', () => {
        const worker = reg.installing;
        worker?.addEventListener('statechange', () => { if (worker.state === 'installed') show(); });
      });
      // Match the existing site: a newly installed worker lights the update
      // control, and the user chooses when to reload the current page.
      button.addEventListener('click', () => location.reload());
    }).catch(() => {});
  }
})();
