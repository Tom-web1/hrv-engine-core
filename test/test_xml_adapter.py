import sys, os

# === 這三行決定你的模組能不能被找到 ===
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)
# =========================================

from adapter.xml_adapter import parse_xml

xml_data = """
<Patient Name="TOM" Sex="男" ID="20251015001"
 Height="175.0" Weight="67.0"
 Birthday="1974/06/06"
 TestTime="22:12:26" TestDate="2025-10-15"
 Age="51" HR="57" SD="63.7" RV="1861.00"
 ER="9" N="121" TP="4034" VL="1839"
 LF="1605" HF="528" NN="1051"
 ANSAgeMIN="-1" ANSAgeMAX="20"
 Balance="-1.2"/>
"""

hrv, meta = parse_xml(xml_data)

print("=== MetaInfo ===")
print(meta)
print("\n=== HRVMeasures ===")
print(hrv)
