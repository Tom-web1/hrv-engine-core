# engine_core.py
# ==========================================================
# HRV Engine Core — XML → 全部運算 → JSON + 文字報告
# ==========================================================

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Dict

from adapter.xml_adapter import parse_xml_to_models
from features.compute_features import compute_features
from quadrant.compute_quadrant import compute_quadrant
from constitution.compute_constitution import compute_constitution
from report.compute_report_data import compute_report_data

from vector.compute_vector import compute_physio_vector, PhysioVector
from pattern.compute_pattern import compute_pattern, PatternResult


# ---------- 小工具：dataclass → dict ----------

def dc(obj: Any) -> Any:
    if obj is None:
        return None
    if is_dataclass(obj):
        return asdict(obj)
    return obj


def _explain_level(level: int, low: str, normal: str, high: str) -> str:
    if level <= -1:
        return low
    if level >= 1:
        return high
    return normal


def _build_text_report(meta, vec: PhysioVector, pattern: PatternResult) -> str:
    name = getattr(meta, "name", "受測者")
    sex = getattr(meta, "sex", "")
    age = getattr(meta, "age", None)
    test_date = getattr(meta, "test_date", "")

    header_parts = [str(name)]
    if sex:
        header_parts.append(f"（{sex}")
        if age is not None:
            header_parts[-1] += f"，約 {age} 歲）"
        else:
            header_parts[-1] += "）"
    elif age is not None:
        header_parts.append(f"（約 {age} 歲）")

    header = "".join(header_parts) or "本次受測者"

    # 向量解讀
    tension_txt = _explain_level(
        vec.tension,
        "自律神經張力偏低，較不易進入警覺狀態，容易覺得提不起勁。",
        "自律神經張力大致平衡，能在放鬆與警覺之間切換。",
        "自律神經張力偏高，較容易緊繃、心跳偏快。",
    )
    energy_txt = _explain_level(
        vec.energy,
        "整體能量等級偏低，容易感到疲倦，恢復較慢。",
        "整體能量大致平衡，日常活動多半可負荷。",
        "整體能量偏高，像是長期維持在高檔輸出狀態。",
    )
    elasticity_txt = _explain_level(
        vec.elasticity,
        "心跳變異度偏低，抗壓彈性較不足，面對壓力時較難快速調整。",
        "心跳變異度在合理範圍，面對壓力有一定調節能力。",
        "心跳變異度偏高，調節彈性不錯。",
    )
    recovery_txt = _explain_level(
        vec.recovery,
        "副交感與恢復力偏弱，休息品質與修復效率可能不足。",
        "恢復能力大致尚可，休息後多半能找回精神。",
        "恢復力良好，休息與睡眠對身體的修復效果明顯。",
    )

    lines = []
    lines.append(f"{header}本次自律神經量測結果如下：")
    if test_date:
        lines.append(f"測量日期：{test_date}")
    lines.append("")

    lines.append("一、體質判讀")
    lines.append(f"目前體質傾向：{pattern.main_label}｜{pattern.sub_label}")
    lines.append(f"整體解讀 Summary：{pattern.summary}")
    lines.append("")

    lines.append("二、生理指標與向量解讀")
    lines.append(f"1. 神經張力（HR）：{tension_txt}")
    lines.append(f"2. 能量等級（TP）：{energy_txt}")
    lines.append(f"3. 氣血彈性（SDNN）：{elasticity_txt}")
    lines.append(f"4. 恢復力與副交感深度（RV）：{recovery_txt}")
    lines.append("")

    if pattern.body_feelings:
        lines.append("三、常見身體感受（僅為傾向，不代表診斷）")
        for s in pattern.body_feelings:
            lines.append(f"- {s}")
        lines.append("")

    if pattern.tcm_keywords:
        lines.append("四、中醫體質關鍵詞（供專業人員參考）")
        lines.append("、".join(pattern.tcm_keywords))
        lines.append("")

    if pattern.suggestions:
        lines.append("五、養生與生活型態建議")
        for s in pattern.suggestions:
            lines.append(f"- {s}")
        lines.append("")

    lines.append("※ 本報告僅供健康管理與生活調整參考，不作為任何醫療診斷依據。")
    return "\n".join(lines)


# ---------- 核心 API：XML → dict ----------

def run_engine_from_xml(xml_text: str) -> Dict[str, Any]:
    """
    輸入：單筆 <Patient .../> XML 字串
    輸出：可 json.dumps 的 dict（含 text_report）
    """
    xml_text = (xml_text or "").strip()
    if not xml_text:
        raise ValueError("XML 內容為空，請貼上 <Patient .../>。")

    # 1) XML → hrv + meta
    hrv, meta = parse_xml_to_models(xml_text)

    # 2) 衍生特徵
    features = compute_features(hrv, meta)

    # 3) 象限與體質
    quad = compute_quadrant(features)              # ✅ 只傳 features
    constitution = compute_constitution(hrv, features, quad, meta)

    # 4) ReportData（組裝標準輸出結構）
    report_data = compute_report_data(hrv, features, quad, constitution, meta)

    # 5) 生理向量
    vec = compute_physio_vector(hrv, derived=features)

    # 6) Pattern（象限＋向量 → 體質子型）
    quad_label = (
        getattr(quad, "constitution_label", None)
        or getattr(quad, "quadrant_label", None)
        or getattr(quad, "quadrant_name", None)
        or getattr(quad, "quadrant", None)
        or getattr(constitution, "constitution_label", None)
        or getattr(constitution, "constitution_type", None)
        or ""
    )
    pattern = compute_pattern(quad_label, vec)

    # 7) 文字報告
    text_report = _build_text_report(meta, vec, pattern)

    # 8) 組裝輸出
    return {
        "meta": dc(meta),
        "hrv": dc(hrv),
        "features": dc(features),
        "quadrant": dc(quad),
        "constitution": dc(constitution),
        "report_data": dc(report_data),
        "vector": vec.as_dict(),
        "pattern": pattern.to_dict(),
        "text_report": text_report,
    }
