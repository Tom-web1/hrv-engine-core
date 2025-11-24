from dataclasses import dataclass

@dataclass
class HRVMeasures:
    tp: float
    lf: float
    hf: float
    vl: float
    sd: float
    hr: float
    rv: float
    n_beats: float
    nn_interval: float
    er_count: float
    balance: float
