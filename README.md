📄《HRV-TCM Engine Specification v1.0》
完整送給你。
你只要 把以下內容完整複製 → 貼到 README.md
然後按 Save（Cmd+S），
你的專案正式文件就完成，未來任何人加入都可以立即理解架構。
📄 HRV-TCM Engine Specification v1.0
（你直接複製以下全部內容貼到 README.md）
# HRV-TCM Engine – Specification v1.0
Author: Tom Wang
Created: 2025
Purpose: 心理自主神經 × TCM 陰陽虛實分析引擎（可插拔式樂高架構）
## 1. 系統概述 (Overview)
本引擎（HRV-TCM Engine）用於：
解析 自律神經 HRV XML（NOT 醫療儀器格式）
轉為統一運算格式
計算 HRV 衍生特徵（ln、比值、TP_Z、ANS 年齡等）
建立四象限座標（X=ln(LF/HF), Y=TP_Z）
產生體質分類（陰陽虛實）
輸出 ReportData 給前端 Template 使用
架構採 樂高式模組化 → 每個功能都是 plugin：
Adapter（XML）
HRVMeasures (raw)
DerivedFeatures
QuadrantResult
ConstitutionResult
ReportData
Template（此層完全分離）
## 2. 主要 Pipeline（運算流程）
Raw XML（NOT 機器）  
        ↓  
XML Adapter  
        ↓  
HRVMeasures（原始 HRV 數值）  
MetaInfo（受測者資訊）  
        ↓  
DerivedFeatures（ln, ratio, TP_Z, ANS 差值）  
        ↓  
QuadrantResult（X=ln(LF/HF), Y=TP_Z）  
        ↓  
ConstitutionResult（陰陽虛實體質）  
        ↓  
ReportData（供模板渲染）
## 3. XML → Internal Mapping（v2 最終版）
（固定不變，NOT 公司的 XML 格式）
XML attr	HRVMeasures / MetaInfo	Type	Note
Name	meta.name	str	
Sex	meta.sex	str	男 / 女
ID	meta.id	str	
Birthday	meta.birthday	str	
Height	meta.height	float	
Weight	meta.weight	float	
TestDate	meta.test_date	str	
TestTime	meta.test_time	str	
Age	meta.age	int	
ANSAgeMIN	meta.ans_age_min	float	
ANSAgeMAX	meta.ans_age_max	float	
TP	hrv.tp	float	
LF	hrv.lf	float	
HF	hrv.hf	float	
VL	hrv.vl	float	
SD	hrv.sdnn	float	
HR	hrv.hr	float	
RV	hrv.rv	float	
N	hrv.n_beats	float	
NN	hrv.nn_interval	float	
ER	hrv.er_count	float	
Balance	hrv.balance	float	
## 4. Data Classes（運算資料結構）
### 4.1 MetaInfo（個人＋測試資訊）
@dataclass
class MetaInfo:
    name: str
    sex: str
    id: str
    birthday: str
    height: float
    weight: float
    test_date: str
    test_time: str
    age: int
    ans_age_min: float
    ans_age_max: float
### 4.2 HRVMeasures（所有 HRV 原始數值）
@dataclass
class HRVMeasures:
    tp: float
    lf: float
    hf: float
    vl: float
    sdnn: float
    hr: float
    rv: float
    n_beats: float
    nn_interval: float
    er_count: float
    balance: float
### 4.3 DerivedFeatures（衍生特徵）
包含 ln 系列、比值、TP_Z（標準化 TP）、ANS 年齡等。
@dataclass
class DerivedFeatures:
    ln_tp: float
    ln_lf: float
    ln_hf: float
    ln_vl: float
    ln_lf_hf: float
    lf_hf_ratio: float

    vl_pct: float
    lf_pct: float
    hf_pct: float

    tp_norm_mu_ln: float
    tp_norm_sd_ln: float
    tp_z: float
    tp_level: str

    ans_age_mid: float
    ans_age_diff: float
## 5. TP 常模（Kuo 1999，ln TP）
Y 軸採 TP_Z（標準化 TP）
採年齡區間對應 ln(TP) 常模（μ 與 SD）。
TP_BASE = {
    "男": [
        (29, 6.8, 0.5),
        (39, 6.5, 0.5),
        (49, 6.2, 0.6),
        (59, 5.8, 0.6),
        (69, 5.5, 0.7),
        (200, 5.2, 0.7),
    ],
    "女": [
        (29, 6.6, 0.5),
        (39, 6.4, 0.5),
        (49, 6.0, 0.5),
        (59, 5.6, 0.5),
        (69, 5.2, 0.5),
        (200, 4.9, 0.5),
    ],
}
## 6. DerivedFeatures 計算邏輯（Module 02）
所有 ln 計算使用：
ln(x) = log(x) if x > 0 else nan
衍生特徵包含：
✔ ln 系列
ln_tp
ln_lf
ln_hf
ln_vl
ln_lf_hf = ln(lf/hf)
✔ 頻譜百分比
vl_pct = VL / (VL + LF + HF)
lf_pct = LF / (...)
hf_pct = HF / (...)
✔ TP_Z（標準化 TP）
tp_z = (ln_tp - mu_ln) / sd_ln
tp_level = ["低", "正常", "高"]
✔ ANS 年齡
ans_age_mid = (min + max) / 2
ans_age_diff = ans_age_mid - actual_age
## 7. 象限座標（Module 03）
✔ X 軸：ln(LF/HF)（陽 ↔ 陰）
✔ Y 軸：TP_Z（虛 ↔ 實）
象限：
座標	體質
X>0, Y>0	陽實
X>0, Y<0	陽虛
X<0, Y>0	陰實
X<0, Y<0	陰虛
## 8. Template 層責任（最重要原則）
Engine 保留完整浮點精度
所有小數點、呈現格式、字體、顏色、HTML、PDF
全部在 template 層處理，不在 engine 計算層處理。
## 9. 模組列表（樂高積木）
adapter/xml_adapter.py → XML → HRVMeasures + MetaInfo
features/compute_features.py → DerivedFeatures
quadrant/compute_quadrant.py → 一/二象限座標
constitution/compute_constitution.py → 陰陽虛實體質
report/report_data.py → Package for template
templates/ → HTML/PDF markdown rendering（不屬於引擎）
## 10. Engine 設計原則
Engine 永不處理 UI/字體/格式
Engine 永不四捨五入小數（保持 float 精度）
所有輸入資料均以 XML adapter 為唯一入口
任意模組皆可替換（樂高模式）
Template 層完全獨立，可為不同客戶客製
API 模式以 ReportData 為輸出標準格式
## 11. Versioning
v1.0：XML adapter + DerivedFeatures（含 TP_Z）
v1.1：Quadrant + Constitution
v1.2：Healthy Zone（ellipse）
v2.0：ReportData + Template engine# hrv-engine-core
developing the Engine of HRV
