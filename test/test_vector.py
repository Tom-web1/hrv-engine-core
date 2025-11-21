# test/test_vector.py
# =====================================================
# 單元測試：vector/compute_vector.py
# 目標：
#   1) 驗證 compute_physio_levels 對 HR/TP/SDNN/RV 的分級
#   2) 驗證 compute_physio_vector 輸出四維向量
#   3) 確認會優先使用 DerivedFeatures.ln_tp（若有）
# =====================================================

import math
import pytest

from vector.compute_vector import (
    compute_physio_levels,
    compute_physio_vector,
    PhysioLevels,
    PhysioVector,
)


# -----------------------------------------------------
# 假的 measures / derived class（duck-typing 即可）
# -----------------------------------------------------

class DummyMeasures:
    def __init__(self, hr=None, sdnn=None, rv=None, tp=None):
        self.hr = hr
        self.sdnn = sdnn
        self.rv = rv
        self.tp = tp


class DummyDerived:
    def __init__(self, ln_tp=None):
        self.ln_tp = ln_tp


# -----------------------------------------------------
# 測試案例 1：JACK
#   HR=80, SD=29.5, RV=18, TP=539 (lnTP≈6.29)
# 預期：
#   HR:     在 65–85 → hr_level = 0
#   lnTP:   5.5–6.5 → tp_level = 0
#   SDNN:   25–45   → sdnn_level = 0
#   RV:     <20     → rv_level = -1
#   向量：  [0, 0, 0, -1]
# -----------------------------------------------------

def test_compute_physio_levels_jack():
    m = DummyMeasures(hr=80.0, sdnn=29.5, rv=18.0, tp=539.0)
    lv = compute_physio_levels(m, derived=None)

    assert isinstance(lv, PhysioLevels)
    assert lv.hr_level == 0
    assert lv.tp_level == 0
    assert lv.sdnn_level == 0
    assert lv.rv_level == -1


def test_compute_physio_vector_jack():
    m = DummyMeasures(hr=80.0, sdnn=29.5, rv=18.0, tp=539.0)
    vec = compute_physio_vector(m, derived=None)

    assert isinstance(vec, PhysioVector)
    assert vec.tension == 0      # HR=80 → 主力正常區
    assert vec.energy == 0       # lnTP≈6.29 → 能量平衡
    assert vec.elasticity == 0   # SDNN=29.5 → 中等
    assert vec.recovery == -1    # RV=18 → 恢復不足


# -----------------------------------------------------
# 測試案例 2：盧允柔
#   HR=98, SD=31.8, RV=1006, TP=905 (lnTP≈6.81)
# 預期：
#   HR:     >95          → hr_level = +1
#   lnTP:   >6.5         → tp_level = +1
#   SDNN:   25–45        → sdnn_level = 0
#   RV:     >=35         → rv_level = +1
#   向量：  [1, 1, 0, 1]
# -----------------------------------------------------

def test_compute_physio_vector_lu_yun_rou():
    m = DummyMeasures(hr=98.0, sdnn=31.8, rv=1006.0, tp=905.0)
    vec = compute_physio_vector(m, derived=None)

    assert isinstance(vec, PhysioVector)
    assert vec.tension == 1      # HR=98 → 張力偏高
    assert vec.energy == 1       # lnTP>6.5 → 能量偏高
    assert vec.elasticity == 0   # SDNN=31.8 → 中等
    assert vec.recovery == 1     # RV 很大 → 修復力佳


# -----------------------------------------------------
# 測試案例 3：確認會優先使用 derived.ln_tp
#   measures.tp = 100（理論 ln≈4.605）
#   derived.ln_tp = 6.0
#   預期：tp_level 根據 6.0 → 0（中等），
#        而不是依 measures.tp 計算出來的 -1
# -----------------------------------------------------

def test_compute_physio_levels_use_derived_ln_tp_priority():
    # tp 設成一個如果自己算 ln_tp 會變成「偏低」的值
    m = DummyMeasures(hr=70.0, sdnn=30.0, rv=25.0, tp=100.0)
    # 但 derived.ln_tp 人為指定為 6.0（中等）
    d = DummyDerived(ln_tp=6.0)

    lv = compute_physio_levels(m, derived=d)

    # HR=70 → 0, SDNN=30 → 0, RV=25 → 0，重點是 tp_level
    assert lv.hr_level == 0
    assert lv.sdnn_level == 0
    assert lv.rv_level == 0
    assert lv.tp_level == 0   # 使用 derived.ln_tp=6.0 → 能量平衡


# -----------------------------------------------------
# 若你想確認 NaN 行為，也可以補一個簡單測試
# -----------------------------------------------------

def test_compute_physio_levels_nan_safe():
    m = DummyMeasures(hr=math.nan, sdnn=math.nan, rv=math.nan, tp=math.nan)
    lv = compute_physio_levels(m, derived=None)

    # 全部 NaN → 分級都回 0（中性）
    assert lv.hr_level == 0
    assert lv.tp_level == 0
    assert lv.sdnn_level == 0
    assert lv.rv_level == 0

