# model/quadrant_result.py
from dataclasses import dataclass

@dataclass
class QuadrantResult:
    # 座標
    x: float  # X 軸 = ln(LF/HF)
    y: float  # Y 軸 = TP_Z

    # 象限資訊
    quadrant_code: int   # 0=未知, 1=陽實, 2=陽虛, 3=陰虛, 4=陰實
    quadrant_label: str  # "陽實型" / "陽虛型" / "陰虛型" / "陰實型" / "未知"

    # 預留給未來 Healthy Zone 的欄位（先用 None / NaN）
    in_healthy_zone: bool | None = None
    distance_to_center: float | None = None
    distance_to_boundary: float | None = None
