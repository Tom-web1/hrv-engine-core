# pattern/compute_pattern.py
# ==========================================================
# 象限 (quadrant) + 四維向量 (PhysioVector) → 體質 pattern
#   quadrant_code: "yang_shi", "yang_xu", "yin_shi", "yin_xu"
#   vector: PhysioVector (from vector.compute_vector)
#
# 輸出：
#   PatternResult 物件 + to_dict() → 可直接輸出 JSON
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from vector.compute_vector import PhysioVector


# ----------------------------------------------------------
# PatternResult：給上層引擎 / 報告用
# ----------------------------------------------------------

@dataclass
class PatternResult:
    pattern_id: str              # 內部用 ID，例如 "YS_overcomp"
    quadrant_code: str           # "yang_shi" / "yang_xu" / "yin_shi" / "yin_xu" / "unknown"
    main_label: str              # 主體質（例如：陽實型、陽虛型…）
    sub_label: str               # 子型（例如：外實內虛·硬撐型）
    severity: str                # "mild" / "moderate" / "severe"
    summary: str                 # 一句總結說明
    body_feelings: List[str]     # 可能出現的身體感受
    tcm_keywords: List[str]      # 中醫關鍵詞（氣虛、陽虛、陰虛、心火…）
    suggestions: List[str]       # 建議方向（睡眠、運動、飲食…）

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "quadrant_code": self.quadrant_code,
            "main_label": self.main_label,
            "sub_label": self.sub_label,
            "severity": self.severity,
            "summary": self.summary,
            "body_feelings": self.body_feelings,
            "tcm_keywords": self.tcm_keywords,
            "suggestions": self.suggestions,
        }


# ----------------------------------------------------------
# 象限字串標準化
# ----------------------------------------------------------

def normalize_quadrant_code(raw: Optional[str]) -> str:
    """
    把各種可能的象限標記，收斂成：
      "yang_shi" / "yang_xu" / "yin_shi" / "yin_xu" / "unknown"
    """
    if not raw:
        return "unknown"

    s = str(raw).strip().lower()

    # 英文代碼
    if s in ["yang_shi", "ys", "yangshi"]:
        return "yang_shi"
    if s in ["yang_xu", "yx", "yangxu"]:
        return "yang_xu"
    if s in ["yin_shi", "is", "yinshi"]:
        return "yin_shi"
    if s in ["yin_xu", "ix", "yinxu"]:
        return "yin_xu"

    # 中文（防手動對接用）
    if "陽" in s and "實" in s:
        return "yang_shi"
    if "陽" in s and "虛" in s:
        return "yang_xu"
    if "陰" in s and "實" in s:
        return "yin_shi"
    if "陰" in s and "虛" in s:
        return "yin_xu"

    return "unknown"


# ----------------------------------------------------------
# 主介面：compute_pattern
# ----------------------------------------------------------

def compute_pattern(quadrant_code: str, vec: PhysioVector) -> PatternResult:
    """
    quadrant_code: 來自象限演算法的結果（建議先 mapping 成 "yang_shi" 等）
    vec: PhysioVector（來自 vector.compute_vector）
    """
    q = normalize_quadrant_code(quadrant_code)

    # 先預設一些共用資訊，後面再因 pattern 覆寫
    main_label = "未分類"
    sub_label = "尚未定義"
    severity = "mild"
    summary = "目前體質狀態尚待明確判讀。"
    body_feelings: List[str] = []
    tcm_keywords: List[str] = []
    suggestions: List[str] = []

    t = vec.tension
    e = vec.energy
    el = vec.elasticity
    r = vec.recovery

    # ======================================================
    # 一、陽實型（交感偏強，能量偏高 or 正常）
    # ======================================================
    if q == "yang_shi":
        main_label = "陽實型"

        # 1) 張力高 + 恢復差 → 外實內虛·硬撐型
        if t >= 1 and r <= -1:
            pattern_id = "YS_overcomp"
            sub_label = "外實內虛・硬撐型"
            severity = "moderate"
            summary = (
                "交感神經偏強，但恢復力不足，屬於外表看起來撐得住、"
                "其實內在已經在透支的『硬撐模式』。"
            )
            body_feelings = [
                "常覺得精神繃緊、放鬆不太下來",
                "晚上不容易睡深，早上醒來仍然覺得累",
                "肩頸僵硬、胸口悶、偶爾心悸",
            ]
            tcm_keywords = ["陽氣外浮", "陰血不足", "外實內虛", "心火偏旺"]
            suggestions = [
                "優先調整睡眠與恢復，而不是一味加大運動量",
                "晚間減少螢幕藍光刺激，睡前做 10 分鐘腹式呼吸或伸展",
                "避免過量咖啡因與刺激性飲食（辣、炸）",
            ]

        # 2) 張力高 + 能量高 + 恢復尚可 → 高效亢奮型
        elif t >= 1 and e >= 1 and r >= 0:
            pattern_id = "YS_hyperactive"
            sub_label = "高效亢奮型"
            severity = "moderate"
            summary = (
                "交感神經與整體能量都偏高，屬於火力全開、行程滿檔的狀態，"
                "短期表現不錯，但長期要小心過勞與情緒波動。"
            )
            body_feelings = [
                "白天精神亢奮、腦袋停不下來",
                "容易急躁、脾氣變得比較衝",
                "偶爾會覺得心跳快、胸悶",
            ]
            tcm_keywords = ["陽氣偏旺", "肝火偏亢", "氣血上衝"]
            suggestions = [
                "保留固定的下班儀式，讓身體知道可以收工了",
                "每週至少安排 1～2 天完全不排工作、讓神經系統休息",
                "避免熬夜，睡前可做簡單伸展或靜坐，幫助交感神經降檔",
            ]

        # 3) 其餘 → 一般陽實偏緊型
        else:
            pattern_id = "YS_mild"
            sub_label = "陽實偏緊型"
            severity = "mild"
            summary = (
                "交感神經略為偏強，整體偏向陽實體質，緊張感偏多，"
                "建議平時就開始練習放鬆與調息。"
            )
            body_feelings = [
                "容易緊張、思慮較多",
                "壓力大時肩頸容易僵硬",
                "偶爾會覺得睡得不夠深",
            ]
            tcm_keywords = ["陽氣偏盛", "氣機偏上", "肝氣不舒"]
            suggestions = [
                "在日常加入規律的走路、緩和運動，幫助能量疏泄",
                "學習一兩種簡單的放鬆技巧（例如 4-6 呼吸、伸展）",
                "避免長時間久坐、建議每 50 分鐘起來活動一下",
            ]

    # ======================================================
    # 二、陽虛型（陽氣不足、外冷內虛）
    # ======================================================
    elif q == "yang_xu":
        main_label = "陽虛型"

        # 1) 能量低 + 恢復一般/低 → 氣虛代償型
        if e <= -1 and r <= 0:
            pattern_id = "YX_qi_def"
            sub_label = "氣虛代償型"
            severity = "moderate"
            summary = (
                "整體能量偏低，容易覺得累、提不起勁，若又長期硬撐，"
                "容易演變成陽氣虛弱、四肢冰冷的狀態。"
            )
            body_feelings = [
                "容易疲倦、提不起勁",
                "手腳冰冷、畏寒",
                "勉強工作一整天，回家就像電池見底",
            ]
            tcm_keywords = ["氣虛", "陽氣不足", "脾腎陽虛"]
            suggestions = [
                "先把睡眠與作息調整到穩定，再談運動強度",
                "飲食上可偏溫熱、少冰品，幫助身體慢慢『點火』",
                "建議午間安排短暫休息，避免整天持續超載",
            ]

        # 2) 張力高 + 能量中/低 → 緊繃・體力不足型
        elif t >= 1 and e <= 0:
            pattern_id = "YX_stress"
            sub_label = "緊繃・體力不足型"
            severity = "moderate"
            summary = (
                "神經系統處在緊繃狀態，但底氣與體力並不跟得上，"
                "容易覺得一緊張就『瞬間沒電』。"
            )
            body_feelings = [
                "容易焦慮、心裡緊緊的",
                "一遇到壓力就很快覺得累",
                "有時會暈暈沉沉、專注力下降",
            ]
            tcm_keywords = ["陽虛夾鬱", "氣血兩虛", "心脾兩虛"]
            suggestions = [
                "避免長時間高壓工作，必要時把任務拆小、分段完成",
                "先從輕度運動開始（散步、伸展），不要一開始就衝高強度",
                "規律三餐、避免暴飲暴食與過度節食",
            ]

        else:
            pattern_id = "YX_mild"
            sub_label = "陽虛傾向型"
            severity = "mild"
            summary = (
                "陽氣略顯不足，遇到壓力時容易覺得冷、累，"
                "平時若能維持溫和運動與良好作息，可逐步改善。"
            )
            body_feelings = [
                "天氣變冷時特別不舒服",
                "久坐久站容易覺得腿酸、腰痠",
                "精神狀態容易受天氣與氣溫影響",
            ]
            tcm_keywords = ["陽虛", "脾腎虛寒"]
            suggestions = [
                "日常可以多曬太陽、多活動，幫助陽氣運行",
                "飲食避免過度生冷，多選擇溫熱、易消化食物",
                "睡前可泡腳或做簡單暖身，幫助入睡與循環",
            ]

    # ======================================================
    # 三、陰實型（代謝偏慢、修復過度／滯塞）
    # ======================================================
    elif q == "yin_shi":
        main_label = "陰實型"

        # 1) 能量高 + 彈性/恢復一般或低 → 代謝滯塞型
        if e >= 1 and (el <= 0 or r <= 0):
            pattern_id = "IS_stuck"
            sub_label = "代謝滯塞型"
            severity = "moderate"
            summary = (
                "整體能量雖然不低，但身體的調節與排解效率不佳，"
                "容易出現水腫、沉重感或代謝偏慢的狀態。"
            )
            body_feelings = [
                "容易覺得身體沉重、懶得動",
                "有時會水腫、腰圍或體重不容易下降",
                "飯後容易想睡、精神變鈍",
            ]
            tcm_keywords = ["痰濕", "濕阻", "代謝遲緩"]
            suggestions = [
                "建議循序漸進增加活動量，幫助代謝啟動",
                "飲食上減少過油、過甜與高鹽食物",
                "保持足量飲水與適度流汗，有助於代謝代謝產物",
            ]

        else:
            pattern_id = "IS_mild"
            sub_label = "陰實傾向型"
            severity = "mild"
            summary = (
                "體質略偏陰實，代謝與循環偏緩慢，"
                "若長期缺乏活動，容易往痰濕、代謝問題發展。"
            )
            body_feelings = [
                "久坐久站後會覺得腿沉、腳脹",
                "體重或腰圍容易慢慢往上走",
                "天氣悶熱時會特別不舒服",
            ]
            tcm_keywords = ["陰實", "濕氣偏重"]
            suggestions = [
                "建議每週維持規律中等強度運動（如快走、騎車）",
                "減少甜食與精緻澱粉，增加蔬菜與適量蛋白質",
                "避免久坐，必要時每隔一段時間起來走動與伸展",
            ]

    # ======================================================
    # 四、陰虛型（陰分不足、修復不足）
    # ======================================================
    elif q == "yin_xu":
        main_label = "陰虛型"

        # 1) 恢復差 + 張力偏高 → 陰虛火旺型
        if r <= -1 and t >= 0:
            pattern_id = "IX_fire"
            sub_label = "陰虛火旺型"
            severity = "moderate"
            summary = (
                "身體的『陰分』（修復、滋養）偏不足，又加上張力偏高，"
                "容易出現虛火上炎、睡不好的情況。"
            )
            body_feelings = [
                "容易心煩、口乾、睡不深",
                "半夜容易醒來、或多夢",
                "有時會覺得手心腳心燒燒的",
            ]
            tcm_keywords = ["陰虛火旺", "心腎不交", "虛火上炎"]
            suggestions = [
                "減少熬夜與過度用腦，讓身體有時間修復",
                "睡前避免重口味與刺激性飲食",
                "可考慮安排固定的放鬆儀式（伸展、靜坐、呼吸）",
            ]

        else:
            pattern_id = "IX_mild"
            sub_label = "陰虛傾向型"
            severity = "mild"
            summary = (
                "陰液與修復能量略顯不足，容易在壓力後覺得『空虛感』比較重，"
                "若好好照顧睡眠與休息，可慢慢改善。"
            )
            body_feelings = [
                "勞累後會覺得特別空虛、虛弱",
                "容易口乾、眼睛乾澀",
                "壓力大時比較不耐熱",
            ]
            tcm_keywords = ["陰虛", "津液不足"]
            suggestions = [
                "規律作息，避免長期熬夜與爆肝工作",
                "適度補充水分與富含抗氧化營養素的食物",
                "避免過度使用刺激性飲品（濃茶、咖啡、酒）",
            ]

    # ======================================================
    # 五、無法辨識象限 → unknown
    # ======================================================
    else:
        pattern_id = "unknown"
        main_label = "體質未明確分類"
        sub_label = "資訊不足或暫無適用類別"
        severity = "mild"
        summary = (
            "目前資料尚不足以判定明確的陰陽虛實類型，"
            "建議搭配更多測量紀錄與臨床問診一起評估。"
        )
        body_feelings = []
        tcm_keywords = []
        suggestions = [
            "建議累積更多量測數據，觀察長期趨勢",
            "必要時搭配專業中醫師問診與理學檢查",
        ]

    return PatternResult(
        pattern_id=pattern_id,
        quadrant_code=q,
        main_label=main_label,
        sub_label=sub_label,
        severity=severity,
        summary=summary,
        body_feelings=body_feelings,
        tcm_keywords=tcm_keywords,
        suggestions=suggestions,
    )
