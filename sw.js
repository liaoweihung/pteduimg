// 更新時間戳記，強迫重新整理
const CACHE_NAME = 'pwa-cache-v202604271035-round-logo';

// 👇 這裡從 ASSETS 改成了 urlsToCache，這樣 Python 管家才找得到！
const urlsToCache = [
  './',
  './index.html',
  './icon.png',
  './img/nasal_4.png',
  './img/acne.png',
  './img/AugmentinSyrup.png',
  './img/rec_1.png',
  './img/lan_2.png',
  './img/rec_8.png',
  './img/hem_oint_1.png',
  './img/eye_4.png',
  './img/MDI_3.png',
  './img/Ps_hair_wash.png',
  './img/NTG_1.png',
  './img/oneFTU.png',
  './img/hem_oint_6.png',
  './img/MDI_7.png',
  './img/Wet_Wrap.png',
  './img/rec_3.png',
  './img/nasal_5.png',
  './img/over_one_oint_04.png',
  './img/MDI_4.png',
  './img/vag_oint_3.png',
  './img/eye_6.png',
  './img/thin_skin_part.png',
  './img/ear_4.png',
  './img/over_one_oint_02.png',
  './img/nasal_2.png',
  './img/eye_5.png',
  './img/Nicotine_1.png',
  './img/ear_1.png',
  './img/ear_6.png',
  './img/DM_damage.png',
  './img/ear_5.png',
  './img/MDI_1.png',
  './img/Neupro.png',
  './img/vag_1.png',
  './img/vag_oint_5.png',
  './img/eye_3.png',
  './img/vag_3.png',
  './img/MDI_2.png',
  './img/Ped_abx_susp_7.png',
  './img/vag_4.png',
  './img/prevent_scar.png',
  './img/over_one_onit_02.png',
  './img/ear_3.png',
  './img/NTG_3.png',
  './img/slipped_fall_wound.png',
  './img/Ped_abx_susp_6.png',
  './img/Ped_abx_susp_5.png',
  './img/lan_1.png',
  './img/eye_2.png',
  './img/vag_oint_1.png',
  './img/eye_1.png',
  './img/rec_2.png',
  './img/over_one_oint_01.png',
  './img/vag_oint_2.png',
  './img/rec_6.png',
  './img/Ped_abx_susp_3.png',
  './img/MDI_5.png',
  './img/vag_oint_6.png',
  './img/Ped_abx_susp_8.png',
  './img/rec_5.png',
  './img/oint_choose.png',
  './img/Ped_abx_susp_1.png',
  './img/vag_2.png',
  './img/hem_oint_4.png',
  './img/hem_oint_5.png',
  './img/hem_oint_3.png',
  './img/MDI_6.png',
  './img/Ped_abx_susp_4.png',
  './img/Ped_abx_susp_2.png',
  './img/ZithromaxPOS.png',
  './img/rec_4.png',
  './img/NTG_2.png',
  './img/wound_oint.png',
  './img/hem_oint_2.png',
  './img/nasal_1.png',
  './img/ear_2.png',
  './img/over_one_oint_03.png',
  './img/rec_7.png',
  './img/over_one_onit_03.png',
  './img/vag_oint_4.png',
  './img/nasal_3.png',
  './img/Lidopat_1.png',
  './img/artficial_vs_paraffin.png'
];

// === 安裝階段 ===
self.addEventListener('install', (e) => {
  // 關鍵 1：跳過等待，強制成為最新版
  self.skipWaiting(); 
  
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('開始逐一快取檔案...');
      // 防彈寫法：即使某個檔案找不到，也不會中斷其他檔案的下載
      return Promise.all(
        urlsToCache.map(url => { // 👈 這裡也對應改成了 urlsToCache
          return cache.add(url).catch(err => {
            console.error('⚠️ 這支檔案找不到，請檢查 GitHub 檔名：', url);
          });
        })
      );
    })
  );
});

// === 啟動階段 ===
self.addEventListener('activate', (e) => {
  // 關鍵 2：立刻接管目前所有打開的頁面
  e.waitUntil(clients.claim()); 

  e.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          // 如果快取名稱跟最新的不一樣，就刪除舊的
          if (cacheName !== CACHE_NAME) {
            console.log('🧹 刪除舊快取：', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// === 攔截請求階段 ===
self.addEventListener('fetch', (e) => {
  const request = e.request;
  const url = new URL(request.url);
  const isFreshAsset = request.mode === 'navigate' || /\.(html|css|js|json)$/i.test(url.pathname);

  if (isFreshAsset) {
    e.respondWith(
      fetch(request).then(response => {
        const copy = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
        return response;
      }).catch(() => caches.match(request))
    );
    return;
  }

  e.respondWith(
    caches.match(request).then(res => res || fetch(request))
  );
});
