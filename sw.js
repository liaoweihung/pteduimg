// 更新時間戳記，強迫重新整理
const CACHE_NAME = 'pharmacist-edu-202603160046'; 

const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon.png',
  // ⚠️ 已經把外部的 QR Code 網址移除了，確保本地圖片能順利下載！
  
  // 眼藥膏
  './img/eye_1.png', './img/eye_2.png', './img/eye_3.png', './img/eye_4.png', './img/eye_5.png', './img/eye_6.png',
  // 肛門塞劑
  './img/rec_1.png', './img/rec_2.png', './img/rec_3.png', './img/rec_4.png',
  // 耳滴劑
  './img/ear_1.png', './img/ear_2.png', './img/ear_3.png', './img/ear_4.png', './img/ear_5.png', './img/ear_6.png',
  // 鼻噴劑
  './img/nasal_1.png', './img/nasal_2.png', './img/nasal_3.png', './img/nasal_4.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('正在快取本地圖片...');
      return cache.addAll(ASSETS);
    })
  );
});

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
