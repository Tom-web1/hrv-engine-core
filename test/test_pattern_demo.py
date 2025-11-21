# test/test_pattern_demo.py
# 手動跑一次 Jack 的資料 → 看 JSON 輸出長什麼樣

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json
from vector.compute_vector import compute_physio_vector
from pattern.compute_pattern import compute_pattern, PatternResult


# 簡單的 DummyMeasures（模擬你的 HRVMeasures）
class DummyMeasures:
    def __init__(self, hr=None, sdnn=None, rv=None, tp=None):
        self.hr = hr
        self.sdnn = sdnn
        self.rv = rv
        self.tp = tp


def main():
    # Jack 的數值：HR=80, SD=29.5, RV=18, TP=539
    m = DummyMeasures(hr=80.0, sdnn=29.5, rv=18.0, tp=539.0)

    # 四維向量
    vec = compute_physio_vector(m, derived=None)

    # 象限：Jack 是陽實型 → 手動給 "yang_shi"
    pattern: PatternResult = compute_pattern("yang_shi", vec)

    # 打包成 JSON
    data = {
        "vector": vec.as_dict(),
        "pattern": pattern.to_dict(),
    }

    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
