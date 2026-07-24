from dataclasses import dataclass

@dataclass(frozen=True)
class WidgetIDs:
    """Константы ID виджетов для диалогов."""
    NAME_INPUT: str = 'name_input'
    GRADE_RADIO: str = 'grade'
    LIST_GROUP: str = 'lg'
    SUBJECT_CHECKBOX: str = 'ch_subject'
    PRICE_COUNTER: str = 'go_price_input'

    # Диалоговые данные
    DIALOG_GRADES: str = 'lst_grade'
    DIALOG_SUBJECTS: str = 'lst_subject'
    DIALOG_CONNECTION: str = 'conn'


WIDGETS = WidgetIDs()