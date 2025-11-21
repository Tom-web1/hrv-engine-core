# constitution/compute_constitution.py

from model.derived_features import DerivedFeatures
from model.quadrant_result import QuadrantResult
from model.hrv_measures import HRVMeasures
from model.meta_info import MetaInfo
from model.constitution_result import ConstitutionResult
from healthy_zone.compute_healthy_zone import compute_healthy_zone


def build_risk_flags(hrv: HRVMeasures, features: DerivedFeatures) -> list:
    """
    建立風險標記（risk flags）
    規則可持續擴充。
    """
    flags = []

    # 壓力負荷大（VL 占比 > 45%）
    if features.vl_pct > 0.45:
        flags.append("壓力負荷較高（VL 偏高）")

    # 副交感較弱（HF% < 12%）
    if features.hf_pct < 0.12:
        flags.append("副交感較弱（HF% 偏低）")

    # 能量效率低（efficiency < 0.45）
    if features.efficiency < 0.45:
        flags.append("能量效率偏低")

    # 能量偏亢（TP_Z >= 2）
    if features.tp_z >= 2.0:
        flags.append("能量偏亢（TP_Z 高）")

    # 自律神經偏老（ANS_age_diff < -10）
    if features.ans_age_diff < -10:
        flags.append("自律神經明顯偏緊繃")

    # 交感 / 副交感平衡偏移（Balance 絕對值 > 3）
    if abs(hrv.balance) > 3:
        flags.append("交感/副交感平衡偏移")

    return flags


def compute_constitution(
    hrv: HRVMeasures,
    features: DerivedFeatures,
    quad: QuadrantResult,
    meta: MetaInfo,
) -> ConstitutionResult:
    """
    綜合：
    - DerivedFeatures（能量、壓力、效率）
    - QuadrantResult（陰陽虛實象限）
    - HRVMeasures（Balance）
    - MetaInfo（sex, age → Healthy Zone）
    """

    # 1) Healthy Zone 判斷
    hz = compute_healthy_zone(features, meta.sex, meta.age)

    quad.in_healthy_zone = hz["in_healthy_zone"]
    quad.distance_to_center = hz["distance_to_center"]
    quad.distance_to_boundary = hz["distance_to_boundary"]

    # 2) 風險標記
    risk_flags = build_risk_flags(hrv, features)

    # 3) 組合為 ConstitutionResult
    return ConstitutionResult(
        quadrant_label=quad.quadrant_label,

        tp_level=features.tp_level,
        tp_z=features.tp_z,
        tp_q=features.tp_q,
        efficiency=features.efficiency,

        vl_pct=features.vl_pct,
        balance=hrv.balance,

        ans_age_mid=features.ans_age_mid,
        ans_age_diff=features.ans_age_diff,

        risk_flags=risk_flags,

        in_healthy_zone=quad.in_healthy_zone,
        distance_to_center=quad.distance_to_center,
    )
