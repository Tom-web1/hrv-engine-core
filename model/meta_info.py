from dataclasses import dataclass

@dataclass
class MetaInfo:
    name: str
    sex: str
    id: str
    birthday: str
    height: float
    weight: float
    test_date: str
    test_time: str
    age: int
    ans_age_min: float
    ans_age_max: float
