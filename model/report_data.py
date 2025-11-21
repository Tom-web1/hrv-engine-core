# model/report_data.py

from dataclasses import dataclass
from typing import List, Optional
from model.meta_info import MetaInfo
from model.hrv_measures import HRVMeasures
from model.derived_features import DerivedFeatures
from model.quadrant_result import QuadrantResult
from model.constitution_result import ConstitutionResult


@dataclass
class ReportData:
    meta: MetaInfo
    hrv: HRVMeasures
    features: DerivedFeatures
    quadrant: QuadrantResult
    constitution: ConstitutionResult

    # 可選附加欄位（給 HTML/PDF）
    advice_constitution: Optional[str] = None
    advice_risk: Optional[str] = None
    advice_lifestyle: Optional[str] = None

    def to_dict(self):
        """轉成前端可用 JSON"""
        return {
            "meta": self.meta.__dict__,
            "hrv": self.hrv.__dict__,
            "features": self.features.__dict__,
            "quadrant": self.quadrant.__dict__,
            "constitution": self.constitution.__dict__,
            "advice_constitution": self.advice_constitution,
            "advice_risk": self.advice_risk,
            "advice_lifestyle": self.advice_lifestyle,
        }
