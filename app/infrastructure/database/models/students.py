from dataclasses import dataclass

@dataclass
class StudentsData:
    """DTO для данных списка учеников из таблицы students."""
    id: int
    name: str
    grade: str