# vector/compute_vector.py
# ==========================================================
# 生理向量 (HR / TP / SDNN / RV)
# 重要原則：
#   1) 不 parse XML
#   2) 不自行算 TP/SDNN/RV，全部用 adapter → model 給的
#   3) 優先使用 derived.ln_tp（若有）
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any, Dict
import math

# ----------------------------------------------------------
# 型別提示：如果 model 存在就導入；不存在就 fallback 成 Any
# ----------------------------------------------------------

try:
    from model.hrv_measures import HRVMeasures  # type: ignore
except Exception:
    HRVMeasures = Any  # type: ignore

try:
    from model.derived_features import DerivedFeatures  # type: ignore
except Exception:
    DerivedFeatures = Any  # type: ignore


# ----------------------------------------------------------
# 資料結構
# ----------------------------------------------------------

@dataclass
class PhysioLevels:
    """分級結果：-1=低，0=中，+1=高"""
    hr_level: int
    tp_level: int
    sdnn_level: int
    rv_level: int

    def as_dict(self) -> Dict[str, int]:
        return {
            "hr_level": self.hr_level,
            "tp_level": self.tp_level,
            "sdnn_level": self.sdnn_level,
            "rv_level": self.rv_level,
        }


@dataclass
class PhysioVector:
    """四維向量（後續要給 pattern engine 用）"""
    tension: int       # HR → 交感張力
    energy: int        # lnTP → 能量
    elasticity: int    # SDNN → 氣血彈性
    recovery: int      # RV → 修復力

    def as_dict(self) -> Dict[str, int]:
        return {
            "tension": self.tension,
            "energy": self.energy,
            "elasticity": self.elasticity,
            "recovery": self.recovery,
        }


# ----------------------------------------------------------
# 分級規則（v1，可微調）
# ----------------------------------------------------------

def _classify_hr_level(hr: float) -> int:
    """HR 張力等級（你指定主力範圍 65–85）"""
    if hr is None or math.isnan(hr):
        return 0
    if hr < 60:
        return -1
    if hr < 65:
        return -1
    if hr <= 85:
        return 0
    if hr <= 95:
        return 1
    return 1


def _classify_tp_level_from_ln(ln_tp: Optional[float]) -> int:
    """TP 能量等級"""
    if ln_tp is None or math.isnan(ln_tp):
        return 0
    if ln_tp < 5.5:
        return -1
    if ln_tp <= 6.5:
        return 0
    return 1


def _classify_sdnn_level(sdnn: float) -> int:
    """SDNN 彈性等級"""
    if sdnn is None or math.isnan(sdnn):
        return 0
    if sdnn < 25:
        return -1
    if sdnn < 45:
        return 0
    return 1


def _classify_rv_level(rv: float) -> int:
    """RV 修復能力等級"""
    if rv is None or math.isnan(rv):
        return 0
    if rv < 20:
        return -1
    if rv < 35:
        return 0
    return 1


# ----------------------------------------------------------
# 工具：安全抓屬性（duck-typing）
# ----------------------------------------------------------

def _safe_attr(obj: Any, name: str, default=None):
    return getattr(obj, name, default)


# ----------------------------------------------------------
# 主流程：compute_physio_levels
# ----------------------------------------------------------

def compute_physio_levels(
    measures: HRVMeasures,
    derived: Optional[DerivedFeatures] = None
) -> PhysioLevels:

    # --- HR ---
    hr = _safe_attr(measures, "hr", None)
    if hr is None:
        hr = _safe_attr(measures, "HR", None)
    hr_level = _classify_hr_level(hr)

    # --- lnTP（優先使用 derived）---
    ln_tp = None
    if derived is not None:
        ln_tp = _safe_attr(derived, "ln_tp", None)

    # derived 沒有的話，自己算（來源仍是 measures.tp）
    if ln_tp is None:
        tp_val = _safe_attr(measures, "tp", None)
        if tp_val is None:
            tp_val = _safe_attr(measures, "TP", None)
        if tp_val is not None and tp_val > 0:
            ln_tp = math.log(tp_val)
        else:
            ln_tp = None

    tp_level = _classify_tp_level_from_ln(ln_tp)

    # --- SDNN ---
    sdnn = _safe_attr(measures, "sdnn", None)
    if sdnn is None:
        sdnn = _safe_attr(measures, "SD", None)
    sdnn_level = _classify_sdnn_level(sdnn)

    # --- RV ---
    rv = _safe_attr(measures, "rv", None)
    if rv is None:
        rv = _safe_attr(measures, "RV", None)
    rv_level = _classify_rv_level(rv)

    return PhysioLevels(
        hr_level=hr_level,
        tp_level=tp_level,
        sdnn_level=sdnn_level,
        rv_level=rv_level,
    )


# ----------------------------------------------------------
# 主流程：compute_physio_vector（四維向量）
# ----------------------------------------------------------

def compute_physio_vector(
    measures: HRVMeasures,
    derived: Optional[DerivedFeatures] = None
) -> PhysioVector:

    lv = compute_physio_levels(measures, derived)

    return PhysioVector(
        tension=lv.hr_level,
        energy=lv.tp_level,
        elasticity=lv.sdnn_level,
        recovery=lv.rv_level,
    )
