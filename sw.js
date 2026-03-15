// 更新時間戳記，強迫重新整理
const CACHE_NAME = 'pharmacist-edu-202603160113'; 

const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon.png',
 // 👇 把本地的 QR Code 產生器加入快取 👇
  './qrious.min.js',
  
  // 眼藥膏
  './img/eye_1.png', './img/eye_2.png', './img/eye_3.png', './img/eye_4.png', './img/eye_5.png', './img/eye_6.png',
  // 肛門塞劑
  './img/rec_1.png', './img/rec_2.png', './img/rec_3.png', './img/rec_4.png',
  // 耳滴劑
  './img/ear_1.png', './img/ear_2.png', './img/ear_3.png', './img/ear_4.png', './img/ear_5.png', './img/ear_6.png',
  // 鼻噴劑
  './img/nasal_1.png', './img/nasal_2.png', './img/nasal_3.png', './img/nasal_4.png'
];

// ... 上面的 CACHE_NAME 和 ASSETS 清單維持您原本的寫法 ...

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('開始逐一快取檔案...');
      // 💡 防彈寫法：逐一快取檔案，即使某個檔案找不到，也不會中斷其他檔案的下載
      return Promise.all(
        ASSETS.map(url => {
          return cache.add(url).catch(err => {
            console.error('⚠️ 這支檔案找不到，請檢查 GitHub 檔名是否完全一致：', url);
          });
        })
      );
    })
  );
});

// ... 下面的 fetch 和 activate 事件維持您原本的寫法 ...


self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then(res => {
      return res || fetch(e.request);
    })
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keyList => {
      return Promise.all(keyList.map(key => {
        if (key !== CACHE_NAME) {
          return caches.delete(key);
        }
      }));
    })
  );
});
