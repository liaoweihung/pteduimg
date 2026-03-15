const CACHE_NAME = 'pharmacist-edu-v2';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  // 請確保以下路徑與您的圖檔名稱一致
  './img/eye_1.png', './img/eye_2.png', './img/eye_3.png',
  './img/rec_1.png', './img/rec_2.png', './img/rec_3.png',
  './img/ear_1.png', './img/ear_2.png', './img/ear_3.png',
  './icon.png' 
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS)));
});

self.addEventListener('fetch', (e) => {
  e.respondWith(caches.match(e.request).then(res => res || fetch(e.request)));
});