const CACHE_NAME = 'pharmacist-edu-202603151145';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon.png',
  // 列出所有圖片路徑
  './img/eye_1.png', './img/eye_2.png', './img/eye_3.png', './img/eye_4.png', './img/eye_5.png', './img/eye_6.png',
  './img/rec_1.png', './img/rec_2.png', './img/rec_3.png', './img/rec_4.png',
  './img/ear_1.png', './img/ear_2.png', './img/ear_3.png', './img/ear_4.png', './img/ear_5.png', './img/ear_6.png',
  './img/nasal_1.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS)));
});

self.addEventListener('fetch', (e) => {
  e.respondWith(caches.match(e.request).then(res => res || fetch(e.request)));
});
