# HRV Engine Core
# HRV-TCM Engine — Module Summary (v1.0)

以下為本專案已成功實作並驗證可正常運作的 **六大核心模組** 摘要。此文件用於未來開新聊天時快速銜接整個 Engine 的架構與邏輯。

---

## ✅ Module 01 — XML Adapter

**功能：** 將 NOT 機器的單筆 `<Patient .../>` XML 格式，轉為：

* `MetaInfo`
* `HRVMeasures`

**輸入：** XML string
**輸出：** (hrv: HRVMeasures, meta: MetaInfo)

---

## ✅ Module 02 — DerivedFeatures（衍生變數）

**功能：** 根據 HRV 原始數據計算所有二階運算的指標：

* ln(TP), ln(LF), ln(HF), ln(VL)
* ln(LF/HF)
* TP_Z（能量標準化）
* TP_Q（有效能量）
* efficiency（能量效率）
* 頻譜百分比（VL%、LF%、HF%）
* ANS_age_mid / ANS_age_diff

**輸入：** HRVMeasures + MetaInfo
**輸出：** DerivedFeatures

---

## ✅ Module 03 — Quadrant（陰陽虛實象限分類）

**功能：** 依據：

* X = ln(LF/HF)
* Y = TP_Z

得到：

* 陰實型 / 陽實型 / 陰虛型 / 陽虛型
* quadrant_code（1~4）

**輸入：** DerivedFeatures
**輸出：** QuadrantResult

---

## ✅ Module 04 — Constitution（體質整合）

**功能：** 統整：

* DerivedFeatures
* QuadrantResult
* HRVMeasures

並產生：

* 體質分類（陽實 / 陰實 / 陽虛 / 陰虛）
* TP 等級（高 / 正常 / 低）
* risk_flags（壓力高 / 副交感弱 / 能量亢盛…）

**輸入：** hrv, features, quad, meta
**輸出：** ConstitutionResult

---

## ✅ Module 05 — Healthy Zone（健康橢圓區）

**功能：** 計算：

* 橢圓健康區中心 (0, μ_ln)
* 半徑 rx / ry
* 是否落在健康區內（in_healthy_zone）
* 距中心距離（distance_to_center）
* 距橢圓邊界距離（distance_to_boundary）

**輸入：** features + meta
**輸出：** 直接填入 QuadrantResult + ConstitutionResult

---

## ✅ Module 06 — ReportData（統一 API Output）

**功能：** 將以上所有結果組合成可給：

* Web 前端
* App
* Cloud API
* PDF / HTML 報告模板

可直接序列化成 JSON 的結構：

```
ReportData.to_dict()
```

包含：

* meta
* hrv
* features
* quadrant
* constitution
* healthy zone
* 建議欄位（預留）

---

## 🔥 最終結果：Cloud Engine API Ready

執行：

```
python app_demo.py
```

→ 打開瀏覽器 5000 port → 貼上 XML → 取得完整 JSON

這六個模組構成完整的 HRV-TCM Engine v1.0。

---

若未來擴充 Module 07（象限圖）、Module 08（HTML 報告），將可直接以 ReportData 作為單一資料入口。