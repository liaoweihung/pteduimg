// 1. 更新時間戳記，強迫手機下載最新版
const CACHE_NAME = 'pharmacist-edu-202603161240'; 

const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon.png',
  
  // 👇 新增：將 QR Code 套件加入離線快取清單 👇
  'https://cdnjs.cloudflare.com/ajax/libs/qrious/4.0.2/qrious.min.js',
  
  // 眼藥膏
  './img/eye_1.png', './img/eye_2.png', './img/eye_3.png', './img/eye_4.png', './img/eye_5.png', './img/eye_6.png',
  // 肛門塞劑
  './img/rec_1.png', './img/rec_2.png', './img/rec_3.png', './img/rec_4.png',
  // 耳滴劑
  './img/ear_1.png', './img/ear_2.png', './img/ear_3.png', './img/ear_4.png', './img/ear_5.png', './img/ear_6.png',
  // 鼻噴劑
  '.img/nasal_1.png','./img/nasal_2.png','./img/nasal_3.png','./img/nasal_4.png','./img/nasal_5.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('正在快取所有資源...');
      return cache.addAll(ASSETS);
    })
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then(res => {
      // 如果快取裡有，就直接回傳快取；沒有就透過網路抓
      return res || fetch(e.request);
    })
  );
});

// 自動清理舊版本的快取，釋放手機空間
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keyList => {
      return Promise.all(keyList.map(key => {
        if (key !== CACHE_NAME) {
          console.log('清除舊快取:', key);
          return caches.delete(key);
        }
      }));
    })
  );
});
