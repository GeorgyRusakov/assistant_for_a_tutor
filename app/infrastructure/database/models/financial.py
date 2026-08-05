from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class FinancialData:
    """DTO для статистики по доходам"""
    name: str
    number: int
    total: int

@dataclass
class GeneralFinancialData:
    """DTO для общей статистики за все время"""
    month: int
    volume: int
    total: int