from dataclasses import dataclass

@dataclass
class StudentsData:
    """DTO для данных списка учеников."""
    id: int
    name: str
    grade: str