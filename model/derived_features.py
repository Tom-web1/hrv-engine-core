# model/derived_features.py
from dataclasses import dataclass

@dataclass
class DerivedFeatures:
    # ===== ln 系列 =====
    ln_tp: float
    ln_lf: float
    ln_hf: float
    ln_vl: float
    ln_lf_hf: float

    # 比值
    lf_hf_ratio: float

    # 頻譜占比
    vl_pct: float
    lf_pct: float
    hf_pct: float

    # 能量品質相關
    tp_q: float          # TP_Q：有效能量（TP × (LF+HF)/(LF+HF+VL)）
    ln_tp_q: float       # ln(TP_Q)
    efficiency: float    # 能量效率 = (LF+HF)/(LF+HF+VL)

    # TP 常模（Kuo 1999, ln 尺度）
    tp_norm_mu_ln: float
    tp_norm_sd_ln: float
    tp_z: float
    tp_level: str        # "低" / "正常" / "高" / "未知"

    # ANS 年齡
    ans_age_mid: float
    ans_age_diff: float

    # BMI（身體質量指數）
    bmi: float

