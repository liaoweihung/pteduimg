window.TAIWAN_CHILD_GROWTH_DATA = {
  "version": "1.0.0",
  "locale": "zh-TW",
  "purpose": "兒童生長百分位區間判讀資料；用於身高、體重與BMI的區間顯示，不用於診斷。",
  "source": {
    "title": "台灣兒童青少年生長曲線／兒童及青少年BMI建議值",
    "basis": "陳偉德醫師及張美惠醫師2010年發表之研究成果；0–5歲採WHO嬰幼兒生長標準，7–18歲依1997年台閩地區中小學學生體適能檢測資料，5–7歲為銜接資料。",
    "citation": "Chen W, Chang MH. New growth charts for Taiwanese children and adolescents based on World Health Organization standards and health-related physical fitness. Pediatr Neonatol. 2010.",
    "url": "https://www.pediatr-neonatol.com/article/S1875-9572(10)60014-9/pdf",
    "data_file": "兒童生長曲線摺頁之圖表原始數據.ods"
  },
  "units": {
    "age": "years/months",
    "height": "cm",
    "weight": "kg",
    "bmi": "kg/m^2"
  },
  "notes": [
    "此資料適合做百分位區間判讀，例如≤P3、P3–P15、P15–P25、P25–P50、P50–P75、P75–P85、P85–P97、≥P97。",
    "若使用者年齡落在表格點之間，建議顯示最近年齡點或相鄰年齡區間，不建議宣稱精確百分位。",
    "BMI判讀使用門檻：過輕 < cut-off；正常 >= 過輕門檻且 < 過重門檻；過重 >= 過重門檻且 < 肥胖門檻；肥胖 >= 肥胖門檻。",
    "所有結果為衛教與初步篩檢用途；實際評估請由小兒科或成長門診醫師判斷。"
  ],
  "percentile_keys": [
    "p3",
    "p15",
    "p25",
    "p50",
    "p75",
    "p85",
    "p97"
  ],
  "classification_rules": {
    "height_weight_percentile_interval": [
      {
        "id": "below_p3",
        "label": "≤第3百分位",
        "color": "red",
        "condition": "value <= p3"
      },
      {
        "id": "p3_to_p15",
        "label": "第3–15百分位",
        "color": "yellow",
        "condition": "p3 < value <= p15"
      },
      {
        "id": "p15_to_p25",
        "label": "第15–25百分位",
        "color": "green",
        "condition": "p15 < value <= p25"
      },
      {
        "id": "p25_to_p50",
        "label": "第25–50百分位",
        "color": "green",
        "condition": "p25 < value <= p50"
      },
      {
        "id": "p50_to_p75",
        "label": "第50–75百分位",
        "color": "green",
        "condition": "p50 < value <= p75"
      },
      {
        "id": "p75_to_p85",
        "label": "第75–85百分位",
        "color": "green",
        "condition": "p75 < value <= p85"
      },
      {
        "id": "p85_to_p97",
        "label": "第85–97百分位",
        "color": "yellow",
        "condition": "p85 < value <= p97"
      },
      {
        "id": "above_p97",
        "label": "≥第97百分位",
        "color": "red",
        "condition": "value > p97"
      }
    ],
    "bmi": [
      {
        "id": "underweight",
        "label": "過輕",
        "color": "yellow",
        "condition": "bmi < underweight_lt"
      },
      {
        "id": "normal",
        "label": "正常",
        "color": "green",
        "condition": "normal_gte <= bmi < normal_lt"
      },
      {
        "id": "overweight",
        "label": "過重",
        "color": "yellow",
        "condition": "overweight_gte <= bmi < overweight_lt"
      },
      {
        "id": "obese",
        "label": "肥胖",
        "color": "red",
        "condition": "bmi >= obese_gte"
      }
    ]
  },
  "data": {
    "boys": {
      "height": [
        {
          "age_label": "birth",
          "age_years": 0.0,
          "age_months": 0,
          "percentiles": {
            "p3": 46.3,
            "p15": 47.9,
            "p25": 48.6,
            "p50": 49.9,
            "p75": 51.2,
            "p85": 51.8,
            "p97": 53.4
          }
        },
        {
          "age_label": "0.5",
          "age_years": 0.5,
          "age_months": 6,
          "percentiles": {
            "p3": 63.6,
            "p15": 65.4,
            "p25": 66.2,
            "p50": 67.6,
            "p75": 69.1,
            "p85": 69.8,
            "p97": 71.6
          }
        },
        {
          "age_label": "1",
          "age_years": 1.0,
          "age_months": 12,
          "percentiles": {
            "p3": 71.3,
            "p15": 73.3,
            "p25": 74.1,
            "p50": 75.7,
            "p75": 77.4,
            "p85": 78.2,
            "p97": 80.2
          }
        },
        {
          "age_label": "1.5",
          "age_years": 1.5,
          "age_months": 18,
          "percentiles": {
            "p3": 77.2,
            "p15": 79.5,
            "p25": 80.4,
            "p50": 82.3,
            "p75": 84.1,
            "p85": 85.1,
            "p97": 87.3
          }
        },
        {
          "age_label": "2",
          "age_years": 2.0,
          "age_months": 24,
          "percentiles": {
            "p3": 82.1,
            "p15": 84.6,
            "p25": 85.8,
            "p50": 87.8,
            "p75": 89.9,
            "p85": 91.0,
            "p97": 93.6
          }
        },
        {
          "age_label": "2.5",
          "age_years": 2.5,
          "age_months": 30,
          "percentiles": {
            "p3": 85.5,
            "p15": 88.4,
            "p25": 89.6,
            "p50": 91.9,
            "p75": 94.2,
            "p85": 95.5,
            "p97": 98.3
          }
        },
        {
          "age_label": "3",
          "age_years": 3.0,
          "age_months": 36,
          "percentiles": {
            "p3": 89.1,
            "p15": 92.2,
            "p25": 93.6,
            "p50": 96.1,
            "p75": 98.6,
            "p85": 99.9,
            "p97": 103.1
          }
        },
        {
          "age_label": "3.5",
          "age_years": 3.5,
          "age_months": 42,
          "percentiles": {
            "p3": 92.4,
            "p15": 95.7,
            "p25": 97.2,
            "p50": 99.9,
            "p75": 102.5,
            "p85": 104.0,
            "p97": 107.3
          }
        },
        {
          "age_label": "4",
          "age_years": 4.0,
          "age_months": 48,
          "percentiles": {
            "p3": 95.4,
            "p15": 99.0,
            "p25": 100.5,
            "p50": 103.5,
            "p75": 106.2,
            "p85": 107.7,
            "p97": 111.2
          }
        },
        {
          "age_label": "4.5",
          "age_years": 4.5,
          "age_months": 54,
          "percentiles": {
            "p3": 98.4,
            "p15": 102.1,
            "p25": 103.7,
            "p50": 106.7,
            "p75": 109.6,
            "p85": 111.2,
            "p97": 115.0
          }
        },
        {
          "age_label": "5",
          "age_years": 5.0,
          "age_months": 60,
          "percentiles": {
            "p3": 101.2,
            "p15": 105.2,
            "p25": 106.8,
            "p50": 110.0,
            "p75": 113.1,
            "p85": 114.8,
            "p97": 118.7
          }
        },
        {
          "age_label": "5.5",
          "age_years": 5.5,
          "age_months": 66,
          "percentiles": {
            "p3": 103.9,
            "p15": 107.9,
            "p25": 109.5,
            "p50": 112.8,
            "p75": 116.0,
            "p85": 117.7,
            "p97": 121.8
          }
        },
        {
          "age_label": "6",
          "age_years": 6.0,
          "age_months": 72,
          "percentiles": {
            "p3": 106.5,
            "p15": 110.5,
            "p25": 112.3,
            "p50": 115.6,
            "p75": 118.9,
            "p85": 120.6,
            "p97": 124.9
          }
        },
        {
          "age_label": "6.5",
          "age_years": 6.5,
          "age_months": 78,
          "percentiles": {
            "p3": 109.2,
            "p15": 113.2,
            "p25": 115.0,
            "p50": 118.4,
            "p75": 121.7,
            "p85": 123.6,
            "p97": 128.1
          }
        },
        {
          "age_label": "7",
          "age_years": 7.0,
          "age_months": 84,
          "percentiles": {
            "p3": 111.8,
            "p15": 115.8,
            "p25": 117.8,
            "p50": 121.2,
            "p75": 124.6,
            "p85": 126.5,
            "p97": 131.2
          }
        },
        {
          "age_label": "8",
          "age_years": 8.0,
          "age_months": 96,
          "percentiles": {
            "p3": 117.0,
            "p15": 121.3,
            "p25": 123.3,
            "p50": 126.8,
            "p75": 130.3,
            "p85": 132.2,
            "p97": 137.2
          }
        },
        {
          "age_label": "9",
          "age_years": 9.0,
          "age_months": 108,
          "percentiles": {
            "p3": 121.8,
            "p15": 126.0,
            "p25": 128.0,
            "p50": 131.8,
            "p75": 135.5,
            "p85": 137.5,
            "p97": 142.5
          }
        },
        {
          "age_label": "10",
          "age_years": 10.0,
          "age_months": 120,
          "percentiles": {
            "p3": 126.0,
            "p15": 130.5,
            "p25": 132.5,
            "p50": 136.5,
            "p75": 140.5,
            "p85": 142.8,
            "p97": 148.3
          }
        },
        {
          "age_label": "11",
          "age_years": 11.0,
          "age_months": 132,
          "percentiles": {
            "p3": 130.5,
            "p15": 135.6,
            "p25": 137.8,
            "p50": 142.0,
            "p75": 146.7,
            "p85": 149.4,
            "p97": 156.1
          }
        },
        {
          "age_label": "12",
          "age_years": 12.0,
          "age_months": 144,
          "percentiles": {
            "p3": 135.6,
            "p15": 141.1,
            "p25": 143.8,
            "p50": 148.8,
            "p75": 154.2,
            "p85": 157.1,
            "p97": 164.4
          }
        },
        {
          "age_label": "13",
          "age_years": 13.0,
          "age_months": 156,
          "percentiles": {
            "p3": 141.9,
            "p15": 148.5,
            "p25": 151.5,
            "p50": 156.9,
            "p75": 162.0,
            "p85": 164.9,
            "p97": 171.0
          }
        },
        {
          "age_label": "14",
          "age_years": 14.0,
          "age_months": 168,
          "percentiles": {
            "p3": 149.3,
            "p15": 156.3,
            "p25": 159.0,
            "p50": 163.7,
            "p75": 168.3,
            "p85": 170.8,
            "p97": 176.0
          }
        },
        {
          "age_label": "15",
          "age_years": 15.0,
          "age_months": 180,
          "percentiles": {
            "p3": 155.5,
            "p15": 161.3,
            "p25": 163.5,
            "p50": 167.6,
            "p75": 171.8,
            "p85": 173.9,
            "p97": 179.0
          }
        },
        {
          "age_label": "16",
          "age_years": 16.0,
          "age_months": 192,
          "percentiles": {
            "p3": 159.3,
            "p15": 164.0,
            "p25": 166.2,
            "p50": 170.0,
            "p75": 173.8,
            "p85": 175.8,
            "p97": 180.5
          }
        },
        {
          "age_label": "17",
          "age_years": 17.0,
          "age_months": 204,
          "percentiles": {
            "p3": 160.9,
            "p15": 165.5,
            "p25": 167.7,
            "p50": 171.5,
            "p75": 174.8,
            "p85": 176.8,
            "p97": 181.5
          }
        }
      ],
      "weight": [
        {
          "age_label": "birth",
          "age_years": 0.0,
          "age_months": 0,
          "percentiles": {
            "p3": 2.5,
            "p15": 2.9,
            "p25": 3.0,
            "p50": 3.3,
            "p75": 3.7,
            "p85": 3.9,
            "p97": 4.3
          }
        },
        {
          "age_label": "0.5",
          "age_years": 0.5,
          "age_months": 6,
          "percentiles": {
            "p3": 6.4,
            "p15": 7.1,
            "p25": 7.4,
            "p50": 7.9,
            "p75": 8.5,
            "p85": 8.9,
            "p97": 9.7
          }
        },
        {
          "age_label": "1",
          "age_years": 1.0,
          "age_months": 12,
          "percentiles": {
            "p3": 7.8,
            "p15": 8.6,
            "p25": 9.0,
            "p50": 9.6,
            "p75": 10.4,
            "p85": 10.8,
            "p97": 11.8
          }
        },
        {
          "age_label": "1.5",
          "age_years": 1.5,
          "age_months": 18,
          "percentiles": {
            "p3": 8.9,
            "p15": 9.7,
            "p25": 10.1,
            "p50": 10.9,
            "p75": 11.8,
            "p85": 12.3,
            "p97": 13.5
          }
        },
        {
          "age_label": "2",
          "age_years": 2.0,
          "age_months": 24,
          "percentiles": {
            "p3": 9.8,
            "p15": 10.8,
            "p25": 11.3,
            "p50": 12.2,
            "p75": 13.1,
            "p85": 13.7,
            "p97": 15.1
          }
        },
        {
          "age_label": "2.5",
          "age_years": 2.5,
          "age_months": 30,
          "percentiles": {
            "p3": 10.7,
            "p15": 11.8,
            "p25": 12.3,
            "p50": 13.3,
            "p75": 14.4,
            "p85": 15.0,
            "p97": 16.6
          }
        },
        {
          "age_label": "3",
          "age_years": 3.0,
          "age_months": 36,
          "percentiles": {
            "p3": 11.4,
            "p15": 12.7,
            "p25": 13.2,
            "p50": 14.3,
            "p75": 15.6,
            "p85": 16.3,
            "p97": 18.0
          }
        },
        {
          "age_label": "3.5",
          "age_years": 3.5,
          "age_months": 42,
          "percentiles": {
            "p3": 12.2,
            "p15": 13.5,
            "p25": 14.1,
            "p50": 15.3,
            "p75": 16.7,
            "p85": 17.5,
            "p97": 19.4
          }
        },
        {
          "age_label": "4",
          "age_years": 4.0,
          "age_months": 48,
          "percentiles": {
            "p3": 12.9,
            "p15": 14.3,
            "p25": 15.0,
            "p50": 16.3,
            "p75": 17.8,
            "p85": 18.7,
            "p97": 20.9
          }
        },
        {
          "age_label": "4.5",
          "age_years": 4.5,
          "age_months": 54,
          "percentiles": {
            "p3": 13.6,
            "p15": 15.2,
            "p25": 15.9,
            "p50": 17.3,
            "p75": 19.0,
            "p85": 19.9,
            "p97": 22.3
          }
        },
        {
          "age_label": "5",
          "age_years": 5.0,
          "age_months": 60,
          "percentiles": {
            "p3": 14.3,
            "p15": 16.0,
            "p25": 16.7,
            "p50": 18.3,
            "p75": 20.1,
            "p85": 21.1,
            "p97": 23.8
          }
        },
        {
          "age_label": "5.5",
          "age_years": 5.5,
          "age_months": 66,
          "percentiles": {
            "p3": 15.3,
            "p15": 17.1,
            "p25": 17.9,
            "p50": 19.6,
            "p75": 21.6,
            "p85": 22.9,
            "p97": 26.5
          }
        },
        {
          "age_label": "6",
          "age_years": 6.0,
          "age_months": 72,
          "percentiles": {
            "p3": 16.3,
            "p15": 18.2,
            "p25": 19.0,
            "p50": 20.9,
            "p75": 23.2,
            "p85": 24.7,
            "p97": 29.2
          }
        },
        {
          "age_label": "6.5",
          "age_years": 6.5,
          "age_months": 78,
          "percentiles": {
            "p3": 17.4,
            "p15": 19.3,
            "p25": 20.2,
            "p50": 22.3,
            "p75": 24.7,
            "p85": 26.4,
            "p97": 32.0
          }
        },
        {
          "age_label": "7",
          "age_years": 7.0,
          "age_months": 84,
          "percentiles": {
            "p3": 18.4,
            "p15": 20.4,
            "p25": 21.3,
            "p50": 23.6,
            "p75": 26.3,
            "p85": 28.2,
            "p97": 34.7
          }
        },
        {
          "age_label": "8",
          "age_years": 8.0,
          "age_months": 96,
          "percentiles": {
            "p3": 20.3,
            "p15": 22.7,
            "p25": 23.8,
            "p50": 26.3,
            "p75": 29.6,
            "p85": 32.2,
            "p97": 40.2
          }
        },
        {
          "age_label": "9",
          "age_years": 9.0,
          "age_months": 108,
          "percentiles": {
            "p3": 22.1,
            "p15": 24.8,
            "p25": 26.0,
            "p50": 28.8,
            "p75": 32.7,
            "p85": 35.7,
            "p97": 44.3
          }
        },
        {
          "age_label": "10",
          "age_years": 10.0,
          "age_months": 120,
          "percentiles": {
            "p3": 24.0,
            "p15": 26.9,
            "p25": 28.4,
            "p50": 31.5,
            "p75": 36.0,
            "p85": 39.4,
            "p97": 48.6
          }
        },
        {
          "age_label": "11",
          "age_years": 11.0,
          "age_months": 132,
          "percentiles": {
            "p3": 26.3,
            "p15": 29.6,
            "p25": 31.4,
            "p50": 35.3,
            "p75": 40.8,
            "p85": 44.7,
            "p97": 54.8
          }
        },
        {
          "age_label": "12",
          "age_years": 12.0,
          "age_months": 144,
          "percentiles": {
            "p3": 29.3,
            "p15": 33.1,
            "p25": 35.2,
            "p50": 40.3,
            "p75": 46.5,
            "p85": 50.4,
            "p97": 61.5
          }
        },
        {
          "age_label": "13",
          "age_years": 13.0,
          "age_months": 156,
          "percentiles": {
            "p3": 32.8,
            "p15": 38.0,
            "p25": 40.7,
            "p50": 46.5,
            "p75": 53.0,
            "p85": 56.8,
            "p97": 68.5
          }
        },
        {
          "age_label": "14",
          "age_years": 14.0,
          "age_months": 168,
          "percentiles": {
            "p3": 38.0,
            "p15": 44.0,
            "p25": 46.8,
            "p50": 52.5,
            "p75": 58.7,
            "p85": 62.7,
            "p97": 74.3
          }
        },
        {
          "age_label": "15",
          "age_years": 15.0,
          "age_months": 180,
          "percentiles": {
            "p3": 43.0,
            "p15": 49.0,
            "p25": 51.3,
            "p50": 56.5,
            "p75": 62.5,
            "p85": 66.5,
            "p97": 77.6
          }
        },
        {
          "age_label": "16",
          "age_years": 16.0,
          "age_months": 192,
          "percentiles": {
            "p3": 46.8,
            "p15": 52.0,
            "p25": 54.1,
            "p50": 59.0,
            "p75": 65.0,
            "p85": 69.0,
            "p97": 79.3
          }
        },
        {
          "age_label": "17",
          "age_years": 17.0,
          "age_months": 204,
          "percentiles": {
            "p3": 49.3,
            "p15": 54.0,
            "p25": 56.1,
            "p50": 61.0,
            "p75": 66.6,
            "p85": 70.0,
            "p97": 80.0
          }
        }
      ],
      "bmi": [
        {
          "age_label": "2",
          "age_years": 2.0,
          "age_months": 24,
          "thresholds": {
            "underweight_lt": 14.2,
            "normal_gte": 14.2,
            "normal_lt": 17.4,
            "overweight_gte": 17.4,
            "overweight_lt": 18.3,
            "obese_gte": 18.3
          }
        },
        {
          "age_label": "2.5",
          "age_years": 2.5,
          "age_months": 30,
          "thresholds": {
            "underweight_lt": 13.9,
            "normal_gte": 13.9,
            "normal_lt": 17.2,
            "overweight_gte": 17.2,
            "overweight_lt": 18.0,
            "obese_gte": 18.0
          }
        },
        {
          "age_label": "3",
          "age_years": 3.0,
          "age_months": 36,
          "thresholds": {
            "underweight_lt": 13.7,
            "normal_gte": 13.7,
            "normal_lt": 17.0,
            "overweight_gte": 17.0,
            "overweight_lt": 17.8,
            "obese_gte": 17.8
          }
        },
        {
          "age_label": "3.5",
          "age_years": 3.5,
          "age_months": 42,
          "thresholds": {
            "underweight_lt": 13.6,
            "normal_gte": 13.6,
            "normal_lt": 16.8,
            "overweight_gte": 16.8,
            "overweight_lt": 17.7,
            "obese_gte": 17.7
          }
        },
        {
          "age_label": "4",
          "age_years": 4.0,
          "age_months": 48,
          "thresholds": {
            "underweight_lt": 13.4,
            "normal_gte": 13.4,
            "normal_lt": 16.7,
            "overweight_gte": 16.7,
            "overweight_lt": 17.6,
            "obese_gte": 17.6
          }
        },
        {
          "age_label": "4.5",
          "age_years": 4.5,
          "age_months": 54,
          "thresholds": {
            "underweight_lt": 13.3,
            "normal_gte": 13.3,
            "normal_lt": 16.7,
            "overweight_gte": 16.7,
            "overweight_lt": 17.6,
            "obese_gte": 17.6
          }
        },
        {
          "age_label": "5",
          "age_years": 5.0,
          "age_months": 60,
          "thresholds": {
            "underweight_lt": 13.3,
            "normal_gte": 13.3,
            "normal_lt": 16.7,
            "overweight_gte": 16.7,
            "overweight_lt": 17.7,
            "obese_gte": 17.7
          }
        },
        {
          "age_label": "5.5",
          "age_years": 5.5,
          "age_months": 66,
          "thresholds": {
            "underweight_lt": 13.4,
            "normal_gte": 13.4,
            "normal_lt": 16.7,
            "overweight_gte": 16.7,
            "overweight_lt": 18.0,
            "obese_gte": 18.0
          }
        },
        {
          "age_label": "6",
          "age_years": 6.0,
          "age_months": 72,
          "thresholds": {
            "underweight_lt": 13.5,
            "normal_gte": 13.5,
            "normal_lt": 16.9,
            "overweight_gte": 16.9,
            "overweight_lt": 18.5,
            "obese_gte": 18.5
          }
        },
        {
          "age_label": "6.5",
          "age_years": 6.5,
          "age_months": 78,
          "thresholds": {
            "underweight_lt": 13.6,
            "normal_gte": 13.6,
            "normal_lt": 17.3,
            "overweight_gte": 17.3,
            "overweight_lt": 19.2,
            "obese_gte": 19.2
          }
        },
        {
          "age_label": "7",
          "age_years": 7.0,
          "age_months": 84,
          "thresholds": {
            "underweight_lt": 13.8,
            "normal_gte": 13.8,
            "normal_lt": 17.9,
            "overweight_gte": 17.9,
            "overweight_lt": 20.3,
            "obese_gte": 20.3
          }
        },
        {
          "age_label": "8",
          "age_years": 8.0,
          "age_months": 96,
          "thresholds": {
            "underweight_lt": 14.1,
            "normal_gte": 14.1,
            "normal_lt": 19.0,
            "overweight_gte": 19.0,
            "overweight_lt": 21.6,
            "obese_gte": 21.6
          }
        },
        {
          "age_label": "9",
          "age_years": 9.0,
          "age_months": 108,
          "thresholds": {
            "underweight_lt": 14.3,
            "normal_gte": 14.3,
            "normal_lt": 19.5,
            "overweight_gte": 19.5,
            "overweight_lt": 22.3,
            "obese_gte": 22.3
          }
        },
        {
          "age_label": "10",
          "age_years": 10.0,
          "age_months": 120,
          "thresholds": {
            "underweight_lt": 14.5,
            "normal_gte": 14.5,
            "normal_lt": 20.0,
            "overweight_gte": 20.0,
            "overweight_lt": 22.7,
            "obese_gte": 22.7
          }
        },
        {
          "age_label": "11",
          "age_years": 11.0,
          "age_months": 132,
          "thresholds": {
            "underweight_lt": 14.8,
            "normal_gte": 14.8,
            "normal_lt": 20.7,
            "overweight_gte": 20.7,
            "overweight_lt": 23.2,
            "obese_gte": 23.2
          }
        },
        {
          "age_label": "12",
          "age_years": 12.0,
          "age_months": 144,
          "thresholds": {
            "underweight_lt": 15.2,
            "normal_gte": 15.2,
            "normal_lt": 21.3,
            "overweight_gte": 21.3,
            "overweight_lt": 23.9,
            "obese_gte": 23.9
          }
        },
        {
          "age_label": "13",
          "age_years": 13.0,
          "age_months": 156,
          "thresholds": {
            "underweight_lt": 15.7,
            "normal_gte": 15.7,
            "normal_lt": 21.9,
            "overweight_gte": 21.9,
            "overweight_lt": 24.5,
            "obese_gte": 24.5
          }
        },
        {
          "age_label": "14",
          "age_years": 14.0,
          "age_months": 168,
          "thresholds": {
            "underweight_lt": 16.3,
            "normal_gte": 16.3,
            "normal_lt": 22.5,
            "overweight_gte": 22.5,
            "overweight_lt": 25.0,
            "obese_gte": 25.0
          }
        },
        {
          "age_label": "15",
          "age_years": 15.0,
          "age_months": 180,
          "thresholds": {
            "underweight_lt": 16.9,
            "normal_gte": 16.9,
            "normal_lt": 22.9,
            "overweight_gte": 22.9,
            "overweight_lt": 25.4,
            "obese_gte": 25.4
          }
        },
        {
          "age_label": "16",
          "age_years": 16.0,
          "age_months": 192,
          "thresholds": {
            "underweight_lt": 17.4,
            "normal_gte": 17.4,
            "normal_lt": 23.3,
            "overweight_gte": 23.3,
            "overweight_lt": 25.6,
            "obese_gte": 25.6
          }
        },
        {
          "age_label": "17",
          "age_years": 17.0,
          "age_months": 204,
          "thresholds": {
            "underweight_lt": 17.8,
            "normal_gte": 17.8,
            "normal_lt": 23.5,
            "overweight_gte": 23.5,
            "overweight_lt": 25.6,
            "obese_gte": 25.6
          }
        }
      ]
    },
    "girls": {
      "height": [
        {
          "age_label": "birth",
          "age_years": 0.0,
          "age_months": 0,
          "percentiles": {
            "p3": 45.6,
            "p15": 47.2,
            "p25": 47.9,
            "p50": 49.1,
            "p75": 50.4,
            "p85": 51.1,
            "p97": 52.7
          }
        },
        {
          "age_label": "0.5",
          "age_years": 0.5,
          "age_months": 6,
          "percentiles": {
            "p3": 61.5,
            "p15": 63.4,
            "p25": 64.2,
            "p50": 65.7,
            "p75": 67.3,
            "p85": 68.1,
            "p97": 70.0
          }
        },
        {
          "age_label": "1",
          "age_years": 1.0,
          "age_months": 12,
          "percentiles": {
            "p3": 69.2,
            "p15": 71.3,
            "p25": 72.3,
            "p50": 74.0,
            "p75": 75.8,
            "p85": 76.7,
            "p97": 78.9
          }
        },
        {
          "age_label": "1.5",
          "age_years": 1.5,
          "age_months": 18,
          "percentiles": {
            "p3": 75.2,
            "p15": 77.7,
            "p25": 78.7,
            "p50": 80.7,
            "p75": 82.7,
            "p85": 83.7,
            "p97": 86.2
          }
        },
        {
          "age_label": "2",
          "age_years": 2.0,
          "age_months": 24,
          "percentiles": {
            "p3": 80.3,
            "p15": 83.1,
            "p25": 84.2,
            "p50": 86.4,
            "p75": 88.6,
            "p85": 89.8,
            "p97": 92.5
          }
        },
        {
          "age_label": "2.5",
          "age_years": 2.5,
          "age_months": 30,
          "percentiles": {
            "p3": 84.0,
            "p15": 87.0,
            "p25": 88.3,
            "p50": 90.7,
            "p75": 93.1,
            "p85": 94.3,
            "p97": 97.3
          }
        },
        {
          "age_label": "3",
          "age_years": 3.0,
          "age_months": 36,
          "percentiles": {
            "p3": 87.9,
            "p15": 91.1,
            "p25": 92.5,
            "p50": 95.1,
            "p75": 97.6,
            "p85": 99.0,
            "p97": 102.2
          }
        },
        {
          "age_label": "3.5",
          "age_years": 3.5,
          "age_months": 42,
          "percentiles": {
            "p3": 91.4,
            "p15": 94.8,
            "p25": 96.3,
            "p50": 99.0,
            "p75": 101.8,
            "p85": 103.3,
            "p97": 106.7
          }
        },
        {
          "age_label": "4",
          "age_years": 4.0,
          "age_months": 48,
          "percentiles": {
            "p3": 94.6,
            "p15": 98.3,
            "p25": 99.8,
            "p50": 102.7,
            "p75": 105.6,
            "p85": 107.2,
            "p97": 110.8
          }
        },
        {
          "age_label": "4.5",
          "age_years": 4.5,
          "age_months": 54,
          "percentiles": {
            "p3": 97.6,
            "p15": 101.5,
            "p25": 103.1,
            "p50": 106.2,
            "p75": 109.2,
            "p85": 110.9,
            "p97": 114.7
          }
        },
        {
          "age_label": "5",
          "age_years": 5.0,
          "age_months": 60,
          "percentiles": {
            "p3": 100.5,
            "p15": 104.5,
            "p25": 106.2,
            "p50": 109.4,
            "p75": 112.6,
            "p85": 114.4,
            "p97": 118.4
          }
        },
        {
          "age_label": "5.5",
          "age_years": 5.5,
          "age_months": 66,
          "percentiles": {
            "p3": 103.0,
            "p15": 107.1,
            "p25": 108.8,
            "p50": 112.1,
            "p75": 115.3,
            "p85": 117.1,
            "p97": 121.3
          }
        },
        {
          "age_label": "6",
          "age_years": 6.0,
          "age_months": 72,
          "percentiles": {
            "p3": 105.5,
            "p15": 109.7,
            "p25": 111.3,
            "p50": 114.8,
            "p75": 118.0,
            "p85": 119.9,
            "p97": 124.2
          }
        },
        {
          "age_label": "6.5",
          "age_years": 6.5,
          "age_months": 78,
          "percentiles": {
            "p3": 108.1,
            "p15": 112.3,
            "p25": 113.9,
            "p50": 117.6,
            "p75": 120.8,
            "p85": 122.6,
            "p97": 127.2
          }
        },
        {
          "age_label": "7",
          "age_years": 7.0,
          "age_months": 84,
          "percentiles": {
            "p3": 110.6,
            "p15": 114.9,
            "p25": 116.4,
            "p50": 120.3,
            "p75": 123.5,
            "p85": 125.4,
            "p97": 130.1
          }
        },
        {
          "age_label": "8",
          "age_years": 8.0,
          "age_months": 96,
          "percentiles": {
            "p3": 115.7,
            "p15": 120.3,
            "p25": 122.0,
            "p50": 125.8,
            "p75": 129.2,
            "p85": 131.3,
            "p97": 136.5
          }
        },
        {
          "age_label": "9",
          "age_years": 9.0,
          "age_months": 108,
          "percentiles": {
            "p3": 120.7,
            "p15": 125.5,
            "p25": 127.5,
            "p50": 131.3,
            "p75": 135.4,
            "p85": 137.8,
            "p97": 143.5
          }
        },
        {
          "age_label": "10",
          "age_years": 10.0,
          "age_months": 120,
          "percentiles": {
            "p3": 125.8,
            "p15": 131.0,
            "p25": 133.0,
            "p50": 137.5,
            "p75": 142.3,
            "p85": 144.8,
            "p97": 150.8
          }
        },
        {
          "age_label": "11",
          "age_years": 11.0,
          "age_months": 132,
          "percentiles": {
            "p3": 131.8,
            "p15": 137.5,
            "p25": 139.8,
            "p50": 144.5,
            "p75": 149.4,
            "p85": 151.8,
            "p97": 157.3
          }
        },
        {
          "age_label": "12",
          "age_years": 12.0,
          "age_months": 144,
          "percentiles": {
            "p3": 137.9,
            "p15": 143.8,
            "p25": 146.3,
            "p50": 150.5,
            "p75": 154.9,
            "p85": 157.0,
            "p97": 161.8
          }
        },
        {
          "age_label": "13",
          "age_years": 13.0,
          "age_months": 156,
          "percentiles": {
            "p3": 143.2,
            "p15": 148.5,
            "p25": 150.7,
            "p50": 154.5,
            "p75": 158.4,
            "p85": 160.3,
            "p97": 164.8
          }
        },
        {
          "age_label": "14",
          "age_years": 14.0,
          "age_months": 168,
          "percentiles": {
            "p3": 146.8,
            "p15": 151.3,
            "p25": 153.2,
            "p50": 156.8,
            "p75": 160.4,
            "p85": 162.3,
            "p97": 167.0
          }
        },
        {
          "age_label": "15",
          "age_years": 15.0,
          "age_months": 180,
          "percentiles": {
            "p3": 148.5,
            "p15": 152.5,
            "p25": 154.5,
            "p50": 157.9,
            "p75": 161.5,
            "p85": 163.5,
            "p97": 168.2
          }
        },
        {
          "age_label": "16",
          "age_years": 16.0,
          "age_months": 192,
          "percentiles": {
            "p3": 149.5,
            "p15": 153.5,
            "p25": 155.3,
            "p50": 158.7,
            "p75": 162.3,
            "p85": 164.2,
            "p97": 168.8
          }
        },
        {
          "age_label": "17",
          "age_years": 17.0,
          "age_months": 204,
          "percentiles": {
            "p3": 150.0,
            "p15": 154.0,
            "p25": 155.8,
            "p50": 159.3,
            "p75": 162.8,
            "p85": 164.7,
            "p97": 169.0
          }
        }
      ],
      "weight": [
        {
          "age_label": "birth",
          "age_years": 0.0,
          "age_months": 0,
          "percentiles": {
            "p3": 2.4,
            "p15": 2.8,
            "p25": 2.9,
            "p50": 3.2,
            "p75": 3.6,
            "p85": 3.7,
            "p97": 4.2
          }
        },
        {
          "age_label": "0.5",
          "age_years": 0.5,
          "age_months": 6,
          "percentiles": {
            "p3": 5.8,
            "p15": 6.4,
            "p25": 6.7,
            "p50": 7.3,
            "p75": 7.9,
            "p85": 8.3,
            "p97": 9.2
          }
        },
        {
          "age_label": "1",
          "age_years": 1.0,
          "age_months": 12,
          "percentiles": {
            "p3": 7.1,
            "p15": 7.9,
            "p25": 8.2,
            "p50": 8.9,
            "p75": 9.7,
            "p85": 10.2,
            "p97": 11.3
          }
        },
        {
          "age_label": "1.5",
          "age_years": 1.5,
          "age_months": 18,
          "percentiles": {
            "p3": 8.2,
            "p15": 9.0,
            "p25": 9.4,
            "p50": 10.2,
            "p75": 11.1,
            "p85": 11.6,
            "p97": 13.0
          }
        },
        {
          "age_label": "2",
          "age_years": 2.0,
          "age_months": 24,
          "percentiles": {
            "p3": 9.2,
            "p15": 10.1,
            "p25": 10.6,
            "p50": 11.5,
            "p75": 12.5,
            "p85": 13.1,
            "p97": 14.6
          }
        },
        {
          "age_label": "2.5",
          "age_years": 2.5,
          "age_months": 30,
          "percentiles": {
            "p3": 10.1,
            "p15": 11.2,
            "p25": 11.7,
            "p50": 12.7,
            "p75": 13.8,
            "p85": 14.5,
            "p97": 16.2
          }
        },
        {
          "age_label": "3",
          "age_years": 3.0,
          "age_months": 36,
          "percentiles": {
            "p3": 11.0,
            "p15": 12.1,
            "p25": 12.7,
            "p50": 13.9,
            "p75": 15.1,
            "p85": 15.9,
            "p97": 17.8
          }
        },
        {
          "age_label": "3.5",
          "age_years": 3.5,
          "age_months": 42,
          "percentiles": {
            "p3": 11.8,
            "p15": 13.1,
            "p25": 13.7,
            "p50": 15.0,
            "p75": 16.4,
            "p85": 17.3,
            "p97": 19.5
          }
        },
        {
          "age_label": "4",
          "age_years": 4.0,
          "age_months": 48,
          "percentiles": {
            "p3": 12.5,
            "p15": 14.0,
            "p25": 14.7,
            "p50": 16.1,
            "p75": 17.7,
            "p85": 18.6,
            "p97": 21.1
          }
        },
        {
          "age_label": "4.5",
          "age_years": 4.5,
          "age_months": 54,
          "percentiles": {
            "p3": 13.2,
            "p15": 14.8,
            "p25": 15.6,
            "p50": 17.2,
            "p75": 18.9,
            "p85": 20.0,
            "p97": 22.8
          }
        },
        {
          "age_label": "5",
          "age_years": 5.0,
          "age_months": 60,
          "percentiles": {
            "p3": 14.0,
            "p15": 15.7,
            "p25": 16.5,
            "p50": 18.2,
            "p75": 20.2,
            "p85": 21.3,
            "p97": 24.4
          }
        },
        {
          "age_label": "5.5",
          "age_years": 5.5,
          "age_months": 66,
          "percentiles": {
            "p3": 14.9,
            "p15": 16.7,
            "p25": 17.5,
            "p50": 19.4,
            "p75": 21.5,
            "p85": 22.7,
            "p97": 26.5
          }
        },
        {
          "age_label": "6",
          "age_years": 6.0,
          "age_months": 72,
          "percentiles": {
            "p3": 15.9,
            "p15": 17.7,
            "p25": 18.5,
            "p50": 20.5,
            "p75": 22.8,
            "p85": 24.2,
            "p97": 28.6
          }
        },
        {
          "age_label": "6.5",
          "age_years": 6.5,
          "age_months": 78,
          "percentiles": {
            "p3": 16.8,
            "p15": 18.6,
            "p25": 19.6,
            "p50": 21.7,
            "p75": 24.0,
            "p85": 25.6,
            "p97": 30.8
          }
        },
        {
          "age_label": "7",
          "age_years": 7.0,
          "age_months": 84,
          "percentiles": {
            "p3": 17.8,
            "p15": 19.6,
            "p25": 20.6,
            "p50": 22.8,
            "p75": 25.3,
            "p85": 27.1,
            "p97": 32.9
          }
        },
        {
          "age_label": "8",
          "age_years": 8.0,
          "age_months": 96,
          "percentiles": {
            "p3": 19.6,
            "p15": 21.8,
            "p25": 22.8,
            "p50": 25.4,
            "p75": 28.4,
            "p85": 30.8,
            "p97": 37.8
          }
        },
        {
          "age_label": "9",
          "age_years": 9.0,
          "age_months": 108,
          "percentiles": {
            "p3": 21.5,
            "p15": 24.0,
            "p25": 25.3,
            "p50": 28.2,
            "p75": 32.1,
            "p85": 35.0,
            "p97": 42.8
          }
        },
        {
          "age_label": "10",
          "age_years": 10.0,
          "age_months": 120,
          "percentiles": {
            "p3": 23.8,
            "p15": 26.6,
            "p25": 28.3,
            "p50": 31.8,
            "p75": 36.7,
            "p85": 39.8,
            "p97": 47.3
          }
        },
        {
          "age_label": "11",
          "age_years": 11.0,
          "age_months": 132,
          "percentiles": {
            "p3": 26.5,
            "p15": 30.3,
            "p25": 32.5,
            "p50": 36.9,
            "p75": 42.2,
            "p85": 45.5,
            "p97": 52.7
          }
        },
        {
          "age_label": "12",
          "age_years": 12.0,
          "age_months": 144,
          "percentiles": {
            "p3": 29.8,
            "p15": 34.8,
            "p25": 37.1,
            "p50": 41.7,
            "p75": 47.0,
            "p85": 50.1,
            "p97": 57.8
          }
        },
        {
          "age_label": "13",
          "age_years": 13.0,
          "age_months": 156,
          "percentiles": {
            "p3": 33.5,
            "p15": 38.7,
            "p25": 40.9,
            "p50": 45.4,
            "p75": 50.5,
            "p85": 53.5,
            "p97": 61.2
          }
        },
        {
          "age_label": "14",
          "age_years": 14.0,
          "age_months": 168,
          "percentiles": {
            "p3": 37.1,
            "p15": 41.7,
            "p25": 43.8,
            "p50": 48.1,
            "p75": 53.0,
            "p85": 56.0,
            "p97": 63.9
          }
        },
        {
          "age_label": "15",
          "age_years": 15.0,
          "age_months": 180,
          "percentiles": {
            "p3": 39.3,
            "p15": 43.8,
            "p25": 45.7,
            "p50": 49.6,
            "p75": 54.5,
            "p85": 57.5,
            "p97": 65.5
          }
        },
        {
          "age_label": "16",
          "age_years": 16.0,
          "age_months": 192,
          "percentiles": {
            "p3": 40.5,
            "p15": 44.8,
            "p25": 46.7,
            "p50": 50.5,
            "p75": 55.0,
            "p85": 58.0,
            "p97": 66.2
          }
        },
        {
          "age_label": "17",
          "age_years": 17.0,
          "age_months": 204,
          "percentiles": {
            "p3": 41.5,
            "p15": 45.2,
            "p25": 47.2,
            "p50": 51.0,
            "p75": 55.0,
            "p85": 58.0,
            "p97": 66.7
          }
        }
      ],
      "bmi": [
        {
          "age_label": "2",
          "age_years": 2.0,
          "age_months": 24,
          "thresholds": {
            "underweight_lt": 13.7,
            "normal_gte": 13.7,
            "normal_lt": 17.2,
            "overweight_gte": 17.2,
            "overweight_lt": 18.1,
            "obese_gte": 18.1
          }
        },
        {
          "age_label": "2.5",
          "age_years": 2.5,
          "age_months": 30,
          "thresholds": {
            "underweight_lt": 13.6,
            "normal_gte": 13.6,
            "normal_lt": 17.0,
            "overweight_gte": 17.0,
            "overweight_lt": 17.9,
            "obese_gte": 17.9
          }
        },
        {
          "age_label": "3",
          "age_years": 3.0,
          "age_months": 36,
          "thresholds": {
            "underweight_lt": 13.5,
            "normal_gte": 13.5,
            "normal_lt": 16.9,
            "overweight_gte": 16.9,
            "overweight_lt": 17.8,
            "obese_gte": 17.8
          }
        },
        {
          "age_label": "3.5",
          "age_years": 3.5,
          "age_months": 42,
          "thresholds": {
            "underweight_lt": 13.3,
            "normal_gte": 13.3,
            "normal_lt": 16.8,
            "overweight_gte": 16.8,
            "overweight_lt": 17.8,
            "obese_gte": 17.8
          }
        },
        {
          "age_label": "4",
          "age_years": 4.0,
          "age_months": 48,
          "thresholds": {
            "underweight_lt": 13.2,
            "normal_gte": 13.2,
            "normal_lt": 16.8,
            "overweight_gte": 16.8,
            "overweight_lt": 17.9,
            "obese_gte": 17.9
          }
        },
        {
          "age_label": "4.5",
          "age_years": 4.5,
          "age_months": 54,
          "thresholds": {
            "underweight_lt": 13.1,
            "normal_gte": 13.1,
            "normal_lt": 16.9,
            "overweight_gte": 16.9,
            "overweight_lt": 18.0,
            "obese_gte": 18.0
          }
        },
        {
          "age_label": "5",
          "age_years": 5.0,
          "age_months": 60,
          "thresholds": {
            "underweight_lt": 13.1,
            "normal_gte": 13.1,
            "normal_lt": 17.0,
            "overweight_gte": 17.0,
            "overweight_lt": 18.1,
            "obese_gte": 18.1
          }
        },
        {
          "age_label": "5.5",
          "age_years": 5.5,
          "age_months": 66,
          "thresholds": {
            "underweight_lt": 13.1,
            "normal_gte": 13.1,
            "normal_lt": 17.0,
            "overweight_gte": 17.0,
            "overweight_lt": 18.3,
            "obese_gte": 18.3
          }
        },
        {
          "age_label": "6",
          "age_years": 6.0,
          "age_months": 72,
          "thresholds": {
            "underweight_lt": 13.1,
            "normal_gte": 13.1,
            "normal_lt": 17.2,
            "overweight_gte": 17.2,
            "overweight_lt": 18.8,
            "obese_gte": 18.8
          }
        },
        {
          "age_label": "6.5",
          "age_years": 6.5,
          "age_months": 78,
          "thresholds": {
            "underweight_lt": 13.2,
            "normal_gte": 13.2,
            "normal_lt": 17.5,
            "overweight_gte": 17.5,
            "overweight_lt": 19.2,
            "obese_gte": 19.2
          }
        },
        {
          "age_label": "7",
          "age_years": 7.0,
          "age_months": 84,
          "thresholds": {
            "underweight_lt": 13.4,
            "normal_gte": 13.4,
            "normal_lt": 17.7,
            "overweight_gte": 17.7,
            "overweight_lt": 19.6,
            "obese_gte": 19.6
          }
        },
        {
          "age_label": "8",
          "age_years": 8.0,
          "age_months": 96,
          "thresholds": {
            "underweight_lt": 13.8,
            "normal_gte": 13.8,
            "normal_lt": 18.4,
            "overweight_gte": 18.4,
            "overweight_lt": 20.7,
            "obese_gte": 20.7
          }
        },
        {
          "age_label": "9",
          "age_years": 9.0,
          "age_months": 108,
          "thresholds": {
            "underweight_lt": 14.0,
            "normal_gte": 14.0,
            "normal_lt": 19.1,
            "overweight_gte": 19.1,
            "overweight_lt": 21.3,
            "obese_gte": 21.3
          }
        },
        {
          "age_label": "10",
          "age_years": 10.0,
          "age_months": 120,
          "thresholds": {
            "underweight_lt": 14.3,
            "normal_gte": 14.3,
            "normal_lt": 19.7,
            "overweight_gte": 19.7,
            "overweight_lt": 22.0,
            "obese_gte": 22.0
          }
        },
        {
          "age_label": "11",
          "age_years": 11.0,
          "age_months": 132,
          "thresholds": {
            "underweight_lt": 14.7,
            "normal_gte": 14.7,
            "normal_lt": 20.5,
            "overweight_gte": 20.5,
            "overweight_lt": 22.7,
            "obese_gte": 22.7
          }
        },
        {
          "age_label": "12",
          "age_years": 12.0,
          "age_months": 144,
          "thresholds": {
            "underweight_lt": 15.2,
            "normal_gte": 15.2,
            "normal_lt": 21.3,
            "overweight_gte": 21.3,
            "overweight_lt": 23.5,
            "obese_gte": 23.5
          }
        },
        {
          "age_label": "13",
          "age_years": 13.0,
          "age_months": 156,
          "thresholds": {
            "underweight_lt": 15.7,
            "normal_gte": 15.7,
            "normal_lt": 21.9,
            "overweight_gte": 21.9,
            "overweight_lt": 24.3,
            "obese_gte": 24.3
          }
        },
        {
          "age_label": "14",
          "age_years": 14.0,
          "age_months": 168,
          "thresholds": {
            "underweight_lt": 16.3,
            "normal_gte": 16.3,
            "normal_lt": 22.5,
            "overweight_gte": 22.5,
            "overweight_lt": 24.9,
            "obese_gte": 24.9
          }
        },
        {
          "age_label": "15",
          "age_years": 15.0,
          "age_months": 180,
          "thresholds": {
            "underweight_lt": 16.7,
            "normal_gte": 16.7,
            "normal_lt": 22.7,
            "overweight_gte": 22.7,
            "overweight_lt": 25.2,
            "obese_gte": 25.2
          }
        },
        {
          "age_label": "16",
          "age_years": 16.0,
          "age_months": 192,
          "thresholds": {
            "underweight_lt": 17.1,
            "normal_gte": 17.1,
            "normal_lt": 22.7,
            "overweight_gte": 22.7,
            "overweight_lt": 25.3,
            "obese_gte": 25.3
          }
        },
        {
          "age_label": "17",
          "age_years": 17.0,
          "age_months": 204,
          "thresholds": {
            "underweight_lt": 17.3,
            "normal_gte": 17.3,
            "normal_lt": 22.7,
            "overweight_gte": 22.7,
            "overweight_lt": 25.3,
            "obese_gte": 25.3
          }
        }
      ]
    }
  }
}
;
