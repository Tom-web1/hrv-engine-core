# quadrant/compute_quadrant.py
import math
from model.derived_features import DerivedFeatures
from model.quadrant_result import QuadrantResult


def classify_quadrant(x: float, y: float) -> tuple[int, str]:
    """
    根據 X, Y 決定象限：
    X = ln(LF/HF)（陽↔陰）
    Y = TP_Z（實↔虛）

    回傳 (quadrant_code, quadrant_label)
    """
    if x is None or y is None:
        return 0, "未知"

    if math.isnan(x) or math.isnan(y):
        return 0, "未知"

    if x >= 0 and y >= 0:
        return 1, "陽實型"
    elif x >= 0 and y < 0:
        return 2, "陽虛型"
    elif x < 0 and y < 0:
        return 3, "陰虛型"
    elif x < 0 and y >= 0:
        return 4, "陰實型"
    else:
        return 0, "未知"


def compute_quadrant(features: DerivedFeatures) -> QuadrantResult:
    """
    從 DerivedFeatures 計算象限結果：
    - X 軸 = ln(LF/HF)
    - Y 軸 = TP_Z
    - 回傳 QuadrantResult（目前只填基本象限資訊）
    """
    x = features.ln_lf_hf
    y = features.tp_z

    quadrant_code, quadrant_label = classify_quadrant(x, y)

    # Healthy Zone 未實作，先保留 None
    return QuadrantResult(
        x=x,
        y=y,
        quadrant_code=quadrant_code,
        quadrant_label=quadrant_label,
        in_healthy_zone=None,
        distance_to_center=None,
        distance_to_boundary=None,
    )
