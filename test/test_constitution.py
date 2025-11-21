import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

from adapter.xml_adapter import parse_xml
from features.compute_features import compute_derived_features
from quadrant.compute_quadrant import compute_quadrant
from constitution.compute_constitution import compute_constitution

xml = """
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

hrv, meta = parse_xml(xml)
feat = compute_derived_features(hrv, meta)
quad = compute_quadrant(feat)
cons = compute_constitution(hrv, feat, quad, meta)

print("=== MetaInfo ===")
print(meta)
print("\n=== DerivedFeatures ===")
print(feat)
print("\n=== QuadrantResult ===")
print(quad)
print("\n=== ConstitutionResult ===")
print(cons)
