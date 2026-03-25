// 更新時間戳記，強迫重新整理
const CACHE_NAME = 'pharmacist-edu-202603250912'; 

const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon.png',
  './qrious.min.js',
  
  // 眼藥膏
  './img/eye_1.png', './img/eye_2.png', './img/eye_3.png', './img/eye_4.png', './img/eye_5.png', './img/eye_6.png',
  // 肛門塞劑
  './img/rec_1.png', './img/rec_2.png', './img/rec_3.png', './img/rec_4.png', './img/rec_5.png', './img/rec_6.png', './img/rec_7.png', './img/rec_8.png',
  // 耳滴劑
  './img/ear_1.png', './img/ear_2.png', './img/ear_3.png', './img/ear_4.png', './img/ear_5.png', './img/ear_6.png',
  // 鼻噴劑
  './img/nasal_1.png', './img/nasal_2.png', './img/nasal_3.png', './img/nasal_4.png', './img/nasal_5.png',
  // NTG舌下
  './img/NTG_1.png', './img/NTG_2.png', './img/NTG_3.png',
  // 陰道塞劑
  './img/vag_1.png', './img/vag_2.png', './img/vag_3.png', './img/vag_4.png',
  // 陰道軟膏
  './img/vag_oint_1.png', './img/vag_oint_2.png', './img/vag_oint_3.png', './img/vag_oint_4.png', './img/vag_oint_5.png', './img/vag_oint_6.png',
  // 痔瘡軟膏 內痔
  './img/hem_oint_1.png', './img/hem_oint_2.png', './img/hem_oint_3.png', './img/hem_oint_4.png', './img/hem_oint_5.png', './img/hem_oint_6.png',
  // 多國語言圖
  './img/lan_1.png'
];

// === 安裝階段 ===
self.addEventListener('install', (e) => {
  // 👇 關鍵 1：跳過等待，強制成為最新版
  self.skipWaiting(); 
  
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('開始逐一快取檔案...');
      // 防彈寫法：即使某個檔案找不到，也不會中斷其他檔案的下載
      return Promise.all(
        ASSETS.map(url => {
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
  // 👇 關鍵 2：立刻接管目前所有打開的頁面
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
  e.respondWith(
    caches.match(e.request).then(res => {
      // 如果快取裡有就給快取，沒有再去網路抓
      return res || fetch(e.request);
    })
  );
});
