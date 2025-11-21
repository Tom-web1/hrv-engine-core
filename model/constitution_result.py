from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ConstitutionResult:
    quadrant_label: str
    tp_level: str
    tp_z: float
    tp_q: float
    efficiency: float
    vl_pct: float
    balance: float
    ans_age_mid: float
    ans_age_diff: float
    risk_flags: List[str]
    in_healthy_zone: Optional[bool] = None
    distance_to_center: Optional[float] = None
