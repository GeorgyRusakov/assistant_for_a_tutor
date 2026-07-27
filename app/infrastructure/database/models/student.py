from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class StudentData:
    """DTO для данных ученика"""
    name: str
    grade: str
    selected_subjects: List[Tuple[int, int]]