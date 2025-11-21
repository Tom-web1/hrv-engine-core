# healthy_zone/compute_healthy_zone.py

import math
from model.derived_features import DerivedFeatures
from features.compute_features import get_tp_norm_ln


def _point_on_ellipse(rx: float, ry: float, theta_deg: float, cx: float, cy: float):
    """給定圓心(cx, cy)，橢圓半徑 rx, ry，角度 theta，求橢圓上的點"""
    t = math.radians(theta_deg)
    x = cx + rx * math.cos(t)
    y = cy + ry * math.sin(t)
    return x, y


def _find_min_distance_to_ellipse(x: float, y: float, cx: float, cy: float, rx: float, ry: float) -> float:
    """
    掃描 0~359 度，找出 (x,y) 到橢圓邊界的最短距離。
    這是快速近似法，精度對 HRV 報告來說已經足夠。
    """
    min_d = float("inf")

    for theta in range(360):
        ex, ey = _point_on_ellipse(rx, ry, theta, cx, cy)
        d = math.sqrt((x - ex) ** 2 + (y - ey) ** 2)
        if d < min_d:
            min_d = d

    return min_d


def compute_healthy_zone(
    features: DerivedFeatures,
    sex: str,
    age: int,
    rx: float = 0.5,
    ry: float = 0.7,
) -> dict:
    """
    Healthy Zone 判斷：
    X 軸：ln(LF/HF) — 中心 0、半徑 rx
    Y 軸：lnTP      — 中心 μ_ln、半徑 ry（由 TP 常模決定）
    """

    x = features.ln_lf_hf
    y = features.ln_tp

    # 取得該性別 × 年齡的 lnTP 常模 μ
    mu_ln, sd_ln = get_tp_norm_ln(age, sex)

    # 橢圓中心
    cx, cy = 0.0, mu_ln

    # 若有 NaN 就直接回傳不可判斷
    if any(math.isnan(v) for v in [x, y, mu_ln]):
        return {
            "in_healthy_zone": False,
            "distance_to_center": float("nan"),
            "distance_to_boundary": float("nan"),
            "ellipse_cx": cx,
            "ellipse_cy": cy,
            "ellipse_rx": rx,
            "ellipse_ry": ry,
        }

    # 橢圓方程式判斷是否在區域內
    eq = ((x - cx) ** 2) / (rx ** 2) + ((y - cy) ** 2) / (ry ** 2)
    in_zone = eq <= 1.0

    # 到中心的距離
    distance_to_center = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    # 到橢圓邊界最近距離
    distance_to_boundary = _find_min_distance_to_ellipse(x, y, cx, cy, rx, ry)

    return {
        "in_healthy_zone": in_zone,
        "distance_to_center": distance_to_center,
        "distance_to_boundary": distance_to_boundary,
        "ellipse_cx": cx,
        "ellipse_cy": cy,
        "ellipse_rx": rx,
        "ellipse_ry": ry,
    }

