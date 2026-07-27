/* Shared configuration for the six medicine databases. Data remains in its existing source. */
window.MedicineExplorerConfigs = {
  topical: { key:'topical', name:'外用藥', icon:'🧴', accent:'#1f8f6b', root:'', total:2250, filters:[['ingredientClass','成分類別'],['dosage','劑型'],['legal','法律分類'],['status','藥證狀態']] },
  eye: { key:'eye', name:'眼用藥', icon:'👁️', accent:'#147d9a', root:'', dataUrl:'data/eye_meds_rebuild_20260711/final/eye_meds_final.json', total:492, filters:[['dosage','劑型'],['legal','藥品分類'],['year','藥證年份'],['status','藥證狀態'],['confirmed','成分確認狀態']] },
  patch: { key:'patch', name:'外用貼布', icon:'🩹', accent:'#3573b8', root:'../', total:null, filters:[['ingredientClass','成分類別'],['dosage','劑型'],['indicationCategory','適應症分類'],['legal','法律分類']] },
  spray: { key:'spray', name:'鼻腔／口咽噴劑', icon:'💨', accent:'#168a9b', root:'', dataUrl:'data/spray_meds_rebuild_20260714/final/spray_meds_final.json', total:141, filters:[['site','使用部位'],['legal','治療分類']] },
  suppository: { key:'suppository', name:'肛門／陰道塞劑', icon:'◒', accent:'#9a416c', root:'', dataUrl:'data/suppository_meds_rebuild_20260714/final/suppository_meds_final.json', total:148, filters:[['site','使用部位'],['scope','作用範圍'],['legal','治療分類']] },
  oral: { key:'oral', name:'口服液劑', icon:'🥄', accent:'#bd7b19', root:'', dataUrl:'data/oral_liquid_meds_rebuild_20260714/final/oral_liquid_meds_final.json', total:1034, filters:[['preparation','配製方式'],['dosage','劑型'],['legal','治療分類'],['concentration','濃度狀態']] }
  ,inhaler: { key:'inhaler', name:'台灣吸入劑', icon:'🫁', root:'' }
};
window.MedicineExplorerLinks = [
  ['topical','ingredient-explorer.html'], ['eye','eye_drop_explorer.html'], ['patch','web/taiwan_medicinal_patch_database_v2.html'], ['spray','spray_medicine_explorer.html'], ['suppository','suppository_medicine_explorer.html'], ['oral','oral_liquid_medicine_explorer.html']
  ,['inhaler','inhaler_medicine_explorer.html']
];
