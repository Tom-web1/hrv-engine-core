import xml.etree.ElementTree as ET
from model.hrv_measures import HRVMeasures
from model.meta_info import MetaInfo


def parse_xml(xml_text: str):
    """
    Parse <Patient ... /> XML string
    → return HRVMeasures + MetaInfo
    """

    try:
        root = ET.fromstring(xml_text.strip())
    except Exception as e:
        raise ValueError(f"XML 解析失敗: {e}")

    if root.tag != "Patient":
        raise ValueError("XML 格式錯誤：必須是 <Patient ... />")

    # 取得所有屬性
    attr = root.attrib

    # ========== MetaInfo ==========
    meta = MetaInfo(
        name=attr.get("Name", "").strip(),
        sex=attr.get("Sex", "").strip(),
        id=attr.get("ID", "").strip(),
        birthday=attr.get("Birthday", "").strip(),
        height=float(attr.get("Height", 0)),
        weight=float(attr.get("Weight", 0)),
        test_date=attr.get("TestDate", "").strip(),
        test_time=attr.get("TestTime", "").strip(),
        age=int(float(attr.get("Age", 0))),
        ans_age_min=float(attr.get("ANSAgeMIN", 0)),
        ans_age_max=float(attr.get("ANSAgeMAX", 0)),
    )

    # ========== HRVMeasures ==========
    hrv = HRVMeasures(
        tp=float(attr.get("TP", 0)),
        lf=float(attr.get("LF", 0)),
        hf=float(attr.get("HF", 0)),
        vl=float(attr.get("VL", 0)),
        sdnn=float(attr.get("SD", 0)),
        hr=float(attr.get("HR", 0)),
        rv=float(attr.get("RV", 0)),
        n_beats=float(attr.get("N", 0)),
        nn_interval=float(attr.get("NN", 0)),
        er_count=float(attr.get("ER", 0)),
        balance=float(attr.get("Balance", 0)),
    )

    return hrv, meta

def parse_xml_to_models(xml_text: str):
    """
    統一給 engine_core 使用的入口：
    輸入：<Patient ... /> XML 字串
    輸出：HRVMeasures, MetaInfo
    """
    return parse_xml(xml_text)
