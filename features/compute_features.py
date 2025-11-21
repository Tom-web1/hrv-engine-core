# features/compute_features.py
import math
from model.hrv_measures import HRVMeasures
from model.meta_info import MetaInfo
from model.derived_features import DerivedFeatures

# ===== 年齡 × 性別 TP 常模 (ln 值, Kuo 1999) =====
# (上限年齡, mu_ln, sd_ln)
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


def safe_ln(x: float) -> float:
    """避免 ln(0) 爆炸；小於等於 0 時回傳 NaN。"""
    try:
        x = float(x)
    except Exception:
        return float("nan")
    if x > 0:
        return math.log(x)
    return float("nan")


def get_tp_norm_ln(age: int, sex: str):
    """
    根據年齡與性別，從 TP_BASE 取得 (mu_ln, sd_ln)
    sex: "男" / "女"，其他情況一律 fallback 到 "男"
    """
    if sex not in TP_BASE:
        sex = "男"
    for age_limit, mu_ln, sd_ln in TP_BASE[sex]:
        if age <= age_limit:
            return mu_ln, sd_ln
    # 理論上不會到這裡，保險起見
    return TP_BASE[sex][-1][1], TP_BASE[sex][-1][2]


def classify_tp_level(tp_z: float) -> str:
    """
    依 Z 分數給 TP 等級：
    tp_z <= -1     → "低"
    -1 < tp_z < 1  → "正常"
    tp_z >= 1      → "高"
    """
    try:
        z = float(tp_z)
    except Exception:
        return "未知"

    if math.isnan(z):
        return "未知"
    if z <= -1.0:
        return "低"
    if z >= 1.0:
        return "高"
    return "正常"


def compute_tp_quality(hrv: HRVMeasures) -> tuple[float, float, float]:
    """
    計算：
    - efficiency = (LF + HF) / (LF + HF + VL)
    - tp_q = TP × efficiency
    - ln_tp_q = ln(tp_q)

    若分母為 0 或數值異常 → 回傳 NaN。
    """
    lf = float(hrv.lf)
    hf = float(hrv.hf)
    vl = float(hrv.vl)
    tp = float(hrv.tp)

    denom = lf + hf + vl
    if denom > 0:
        efficiency = (lf + hf) / denom
    else:
        efficiency = float("nan")

    if not math.isnan(efficiency) and tp > 0:
        tp_q = tp * efficiency
    else:
        tp_q = float("nan")

    ln_tp_q = safe_ln(tp_q)

    return efficiency, tp_q, ln_tp_q


def compute_bmi(meta: MetaInfo) -> float:
    """
    計算 BMI = 體重(kg) / 身高(m)^2
    若身高或體重異常 → 回傳 NaN。
    """
    try:
        h_cm = float(meta.height)
        w_kg = float(meta.weight)
    except Exception:
        return float("nan")

    if h_cm <= 0 or w_kg <= 0:
        return float("nan")

    h_m = h_cm / 100.0
    return w_kg / (h_m * h_m)


def compute_derived_features(hrv: HRVMeasures, meta: MetaInfo) -> DerivedFeatures:
    """
    核心運算：
    - ln 系列
    - LF/HF 比值
    - 頻譜占比 (VL/LF/HF)
    - TP_Z 分數 (Kuo 1999, ln 尺度)
    - TP_Q / lnTP_Q / efficiency
    - ANS 年齡中位數與差值
    - BMI
    """
    # ===== ln 系列 =====
    ln_tp = safe_ln(hrv.tp)
    ln_lf = safe_ln(hrv.lf)
    ln_hf = safe_ln(hrv.hf)
    ln_vl = safe_ln(hrv.vl)

    # ln(LF/HF) & ratio
    if hrv.hf > 0:
        lf_hf_ratio = hrv.lf / hrv.hf
        ln_lf_hf = safe_ln(lf_hf_ratio)
    else:
        lf_hf_ratio = float("nan")
        ln_lf_hf = float("nan")

    # ===== 頻譜占比 =====
    total_spec = hrv.vl + hrv.lf + hrv.hf
    if total_spec > 0:
        vl_pct = hrv.vl / total_spec
        lf_pct = hrv.lf / total_spec
        hf_pct = hrv.hf / total_spec
    else:
        vl_pct = lf_pct = hf_pct = float("nan")

    # ===== TP_Q / lnTP_Q / efficiency =====
    efficiency, tp_q, ln_tp_q = compute_tp_quality(hrv)

    # ===== TP 常模 (Kuo 1999, ln 尺度) =====
    ln_tp = safe_ln(hrv.tp)
    tp_norm_mu_ln, tp_norm_sd_ln = get_tp_norm_ln(meta.age, meta.sex)
    if tp_norm_sd_ln > 0 and not math.isnan(ln_tp):
        tp_z = (ln_tp - tp_norm_mu_ln) / tp_norm_sd_ln
    else:
        tp_z = float("nan")

    tp_level = classify_tp_level(tp_z)

    # ===== ANS 年齡 =====
    # 改成「ANSAgeMIN - 實際年齡」
    try:
        ans_age_min = float(meta.ans_age_min)
    except Exception:
        ans_age_min = float("nan")

    ans_age_mid = ans_age_min  # 直接當作「自律神經參考年齡」
    if math.isnan(ans_age_mid):
        ans_age_diff = float("nan")
    else:
        ans_age_diff = ans_age_mid - float(meta.age)

    # ===== BMI =====
    bmi = compute_bmi(meta)

    return DerivedFeatures(
        ln_tp=ln_tp,
        ln_lf=ln_lf,
        ln_hf=ln_hf,
        ln_vl=ln_vl,
        ln_lf_hf=ln_lf_hf,
        lf_hf_ratio=lf_hf_ratio,
        vl_pct=vl_pct,
        lf_pct=lf_pct,
        hf_pct=hf_pct,
        tp_q=tp_q,
        ln_tp_q=ln_tp_q,
        efficiency=efficiency,
        tp_norm_mu_ln=tp_norm_mu_ln,
        tp_norm_sd_ln=tp_norm_sd_ln,
        tp_z=tp_z,
        tp_level=tp_level,
        ans_age_mid=ans_age_mid,
        ans_age_diff=ans_age_diff,
        bmi=bmi,
    )


def compute_features(hrv: HRVMeasures, meta: MetaInfo) -> DerivedFeatures:
    """
    統一對外入口：
    - 給 engine_core 或其他模組呼叫
    - 內部實際運算仍然使用 compute_derived_features
    """
    return compute_derived_features(hrv, meta)
