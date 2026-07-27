from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class FinancialData:
    """DTO для статистики по доходам"""
    name: str
    number: int
    total: int