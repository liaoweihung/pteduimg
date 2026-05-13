// ?湔???唾?嚗撥餈恍??唳??
const CACHE_NAME = 'pwa-cache-v202605130248';

// ?? ?ㄐ敺?ASSETS ?寞?鈭?urlsToCache嚗見 Python 蝞∪振?敺嚗?
const urlsToCache = [
  "./",
  "./index.html",
  "./public.html",
  "./icon.png",
  "./404.html",
  "./img/5_ways_stomatch.webp",
  "./img/AugmentinSyrup.png",
  "./img/Champix.webp",
  "./img/DM_damage.webp",
  "./img/EnteroVirus_vaccine.webp",
  "./img/Exame_Hpylore.webp",
  "./img/Hantaviridae_01.webp",
  "./img/Hantaviridae_02.webp",
  "./img/Lidopat_1.webp",
  "./img/MDI_1.png",
  "./img/MDI_2.png",
  "./img/MDI_3.png",
  "./img/MDI_4.png",
  "./img/MDI_5.png",
  "./img/MDI_6.png",
  "./img/MDI_7.png",
  "./img/NTG_1.png",
  "./img/NTG_2.png",
  "./img/NTG_3.webp",
  "./img/Neupro.webp",
  "./img/Nicotine_1.webp",
  "./img/Osteo_tooth_01.webp",
  "./img/Osteo_tooth_03.webp",
  "./img/Osteo_tooth_04.webp",
  "./img/Ped_abx_susp_1.png",
  "./img/Ped_abx_susp_2.png",
  "./img/Ped_abx_susp_3.png",
  "./img/Ped_abx_susp_4.png",
  "./img/Ped_abx_susp_5.png",
  "./img/Ped_abx_susp_6.png",
  "./img/Ped_abx_susp_7.png",
  "./img/Ped_abx_susp_8.png",
  "./img/Prevent_Enterovirus.webp",
  "./img/Ps_hair_wash.webp",
  "./img/Res3_ABCovid_1.webp",
  "./img/Res3_ABCovid_2.webp",
  "./img/Res3_ABCovid_3.webp",
  "./img/Res3_ABCovid_4.webp",
  "./img/Wash_hands_five_steps.webp",
  "./img/Wet_Wrap.webp",
  "./img/ZithromaxPOS.webp",
  "./img/acne.png",
  "./img/add_to_desktop_android.webp",
  "./img/add_to_desktop_ios.webp",
  "./img/artficial_vs_paraffin.webp",
  "./img/boyBMI.webp",
  "./img/boy_height2.webp",
  "./img/ear_1.png",
  "./img/ear_2.png",
  "./img/ear_3.png",
  "./img/ear_4.png",
  "./img/ear_5.png",
  "./img/ear_6.png",
  "./img/eye_1.png",
  "./img/eye_2.png",
  "./img/eye_3.png",
  "./img/eye_4.png",
  "./img/eye_5.png",
  "./img/eye_6.png",
  "./img/girlBMI.webp",
  "./img/girl_height2.webp",
  "./img/height_prediction.webp",
  "./img/height_tips.webp",
  "./img/hem_oint_1.png",
  "./img/hem_oint_2.png",
  "./img/hem_oint_3.png",
  "./img/hem_oint_4.png",
  "./img/hem_oint_5.png",
  "./img/hem_oint_6.png",
  "./img/hemorr_sitbath_1.png",
  "./img/hemorr_sitbath_2.png",
  "./img/lan_1.webp",
  "./img/lan_2.webp",
  "./img/methodology_of_exam_Hp.webp",
  "./img/nasal_1.png",
  "./img/nasal_2.png",
  "./img/nasal_3.png",
  "./img/nasal_4.png",
  "./img/nasal_5.png",
  "./img/oint_choose.webp",
  "./img/oneFTU.webp",
  "./img/oral_hygiene_01.webp",
  "./img/oral_hygiene_02.webp",
  "./img/oral_hygiene_03.webp",
  "./img/oral_hygiene_04.webp",
  "./img/oral_hygiene_05.webp",
  "./img/oral_hygiene_06.webp",
  "./img/oral_hygiene_07.webp",
  "./img/oral_hygiene_08.webp",
  "./img/over_one_oint_01.webp",
  "./img/over_one_oint_02.webp",
  "./img/over_one_oint_03.webp",
  "./img/over_one_oint_04.webp",
  "./img/prevent_scar.webp",
  "./img/rec_1.png",
  "./img/rec_2.png",
  "./img/rec_3.png",
  "./img/rec_4.png",
  "./img/rec_5.png",
  "./img/rec_6.png",
  "./img/rec_7.png",
  "./img/rec_8.png",
  "./img/site_instruction_01.webp",
  "./img/site_instruction_02.webp",
  "./img/slipped_fall_wound.webp",
  "./img/thin_skin_part.webp",
  "./img/treatment_of_Hpylore.webp",
  "./img/vag_1.png",
  "./img/vag_2.png",
  "./img/vag_3.png",
  "./img/vag_4.png",
  "./img/vag_oint_1.png",
  "./img/vag_oint_2.png",
  "./img/vag_oint_3.png",
  "./img/vag_oint_4.png",
  "./img/vag_oint_5.png",
  "./img/vag_oint_6.png",
  "./img/wound_oint.webp",
  "./cards/height_prediction.html",
  "./cards/boy_height2.html",
  "./cards/girl_height2.html",
  "./cards/boyBMI.html",
  "./cards/girlBMI.html",
  "./cards/height_tips.html",
  "./cards/Wash_hands_five_steps.html",
  "./cards/Prevent_Enterovirus.html",
  "./cards/EnteroVirus_vaccine.html",
  "./cards/Exame_Hpylore.html",
  "./cards/5_ways_stomatch.html",
  "./cards/methodology_of_exam_Hp.html",
  "./cards/treatment_of_Hpylore.html",
  "./cards/Hantaviridae_01.html",
  "./cards/Hantaviridae_02.html",
  "./cards/Res3_ABCovid_1.html",
  "./cards/Res3_ABCovid_2.html",
  "./cards/Res3_ABCovid_3.html",
  "./cards/Res3_ABCovid_4.html",
  "./cards/oral_hygiene_01.html",
  "./cards/oral_hygiene_02.html",
  "./cards/oral_hygiene_03.html",
  "./cards/oral_hygiene_04.html",
  "./cards/oral_hygiene_05.html",
  "./cards/oral_hygiene_06.html",
  "./cards/oral_hygiene_07.html",
  "./cards/oral_hygiene_08.html",
  "./cards/artficial_vs_paraffin.html",
  "./cards/oint_choose.html",
  "./cards/prevent_scar.html",
  "./cards/slipped_fall_wound.html",
  "./cards/wound_oint.html",
  "./cards/AugmentinSyrup.html",
  "./cards/Champix.html",
  "./cards/Osteo_tooth_01.html",
  "./cards/Osteo_tooth_03.html",
  "./cards/Osteo_tooth_04.html",
  "./cards/eye_1.html",
  "./cards/eye_2.html",
  "./cards/eye_3.html",
  "./cards/eye_4.html",
  "./cards/eye_5.html",
  "./cards/eye_6.html",
  "./cards/site_instruction_01.html",
  "./cards/site_instruction_02.html",
  "./cards/lan_1.html",
  "./cards/lan_2.html",
  "./cards/add_to_desktop_ios.html",
  "./cards/add_to_desktop_android.html",
  "./cards/ZithromaxPOS.html",
  "./cards/Wet_Wrap.html",
  "./cards/acne.html",
  "./cards/oneFTU.html",
  "./cards/thin_skin_part.html",
  "./cards/over_one_oint_01.html",
  "./cards/over_one_oint_02.html",
  "./cards/over_one_oint_03.html",
  "./cards/over_one_oint_04.html",
  "./cards/Nicotine_1.html",
  "./cards/ear_1.html",
  "./cards/ear_2.html",
  "./cards/ear_3.html",
  "./cards/ear_4.html",
  "./cards/ear_5.html",
  "./cards/ear_6.html",
  "./cards/DM_damage.html",
  "./cards/Neupro.html",
  "./cards/Ps_hair_wash.html",
  "./cards/nasal_1.html",
  "./cards/nasal_2.html",
  "./cards/nasal_3.html",
  "./cards/nasal_4.html",
  "./cards/nasal_5.html",
  "./cards/Lidopat_1.html",
  "./cards/NTG_1.html",
  "./cards/NTG_2.html",
  "./cards/NTG_3.html",
  "./cards/MDI_1.html",
  "./cards/MDI_2.html",
  "./cards/MDI_3.html",
  "./cards/MDI_4.html",
  "./cards/MDI_5.html",
  "./cards/MDI_6.html",
  "./cards/MDI_7.html",
  "./cards/hemorr_sitbath_1.html",
  "./cards/hemorr_sitbath_2.html",
  "./cards/hem_oint_1.html",
  "./cards/hem_oint_2.html",
  "./cards/hem_oint_3.html",
  "./cards/hem_oint_4.html",
  "./cards/hem_oint_5.html",
  "./cards/hem_oint_6.html",
  "./cards/rec_1.html",
  "./cards/rec_2.html",
  "./cards/rec_3.html",
  "./cards/rec_4.html",
  "./cards/rec_5.html",
  "./cards/rec_6.html",
  "./cards/rec_7.html",
  "./cards/rec_8.html",
  "./cards/vag_1.html",
  "./cards/vag_2.html",
  "./cards/vag_3.html",
  "./cards/vag_4.html",
  "./cards/vag_oint_1.html",
  "./cards/vag_oint_2.html",
  "./cards/vag_oint_3.html",
  "./cards/vag_oint_4.html",
  "./cards/vag_oint_5.html",
  "./cards/vag_oint_6.html",
  "./cards/Ped_abx_susp_1.html",
  "./cards/Ped_abx_susp_2.html",
  "./cards/Ped_abx_susp_3.html",
  "./cards/Ped_abx_susp_4.html",
  "./cards/Ped_abx_susp_5.html",
  "./cards/Ped_abx_susp_6.html",
  "./cards/Ped_abx_susp_7.html",
  "./cards/Ped_abx_susp_8.html",
  "./cards/404.html"
];

// === 摰??挾 ===
self.addEventListener('install', (e) => {
  // ? 1嚗歲??敺?撘瑕???啁?
  self.skipWaiting(); 
  
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('????敹怠?瑼?...');
      // ?脣?撖急?嚗雿踵???獢銝嚗?銝?銝剜?嗡?瑼???頛?
      return Promise.all(
        urlsToCache.map(url => { // ?? ?ㄐ銋???? urlsToCache
          return cache.add(url).catch(err => {
            console.error('?? ?瑼??曆??堆?隢炎??GitHub 瑼?嚗?, url);
          });
        })
      );
    })
  );
});

// === ???挾 ===
self.addEventListener('activate', (e) => {
  // ? 2嚗??餅蝞∠???????
  e.waitUntil(clients.claim()); 

  e.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          // 憒?敹怠??迂頝??啁?銝?璅??撠勗?方???
          if (cacheName !== CACHE_NAME) {
            console.log('?完 ?芷?翰??', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// === ?隢??挾 ===
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
