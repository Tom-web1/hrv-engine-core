# report/compute_report_data.py
# ==========================================================
# 將 Engine 內部各模組的運算結果整合成 ReportData 結構
# ==========================================================

from adapter.xml_adapter import parse_xml
from features.compute_features import compute_derived_features
from quadrant.compute_quadrant import compute_quadrant
from constitution.compute_constitution import compute_constitution
from model.report_data import ReportData


def compute_report_from_xml(xml_text: str) -> ReportData:
    """
    舊版入口（仍保留相容性）：
    XML → MetaInfo + HRVMeasures
        → DerivedFeatures
        → QuadrantResult
        → ConstitutionResult
        → ReportData

    ※ 這會自動取用 features 裡的 bmi（features.bmi）
    """

    # 1) 解析 XML
    hrv, meta = parse_xml(xml_text)

    # 2) 衍生變數（含 BMI）
    feat = compute_derived_features(hrv, meta)

    # 3) 象限
    quad = compute_quadrant(feat)

    # 4) 體質整合（含 Healthy Zone）
    cons = compute_constitution(hrv, feat, quad, meta)

    # 5) 打包成 ReportData
    report = ReportData(
        meta=meta,
        hrv=hrv,
        features=feat,          # ← features 裡已經有 bmi
        quadrant=quad,
        constitution=cons,
    )

    return report


def compute_report_data(hrv, features, quadrant, constitution, meta) -> ReportData:
    """
    EngineCore 對外使用的新入口：
    - 假設 hrv / features / quadrant / constitution / meta 都已算好
    - 將它們組成 ReportData 物件
    """
    return ReportData(
        meta=meta,
        hrv=hrv,
        features=features,      # ← 這裡會帶出 features.bmi
        quadrant=quadrant,
        constitution=constitution,
    )
