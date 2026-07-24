import logging
from typing import List, Tuple

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import ManagedRadio, ManagedListGroup, ManagedCheckbox, ManagedCounter

from ..constants.widget_ids import WIDGETS
from ...infrastructure.database.models.student import StudentData
from ...infrastructure.database.db import add_student, add_student_subject


logger = logging.getLogger(__name__)

class StudentService:
    """
    Сервис для работы с данными учеников.
    Отвечает за извлечение данных из UI и их сохранение.
    """

    def __init__(self, dialog_manager: DialogManager):
        self.dm = dialog_manager

    def extract_student_data(self) -> StudentData:
        """Извлекает все данные ученика из виджетов диалога."""
        name = self._get_name()
        grade = self._get_grade()
        subjects = self._get_subjects()

        return StudentData(
            name=name,
            grade=grade,
            selected_subjects=subjects
        )

    def _get_name(self) -> str:
        """Извлекает имя ученика."""
        name_input: ManagedTextInput = self.dm.find(WIDGETS.NAME_INPUT)
        return name_input.get_value().strip()

    def _get_grade(self) -> str:
        """Извлекает класс ученика."""
        grade_radio: ManagedRadio = self.dm.find(WIDGETS.GRADE_RADIO)
        grade_id = grade_radio.get_checked()

        grades = self.dm.dialog_data.get(WIDGETS.DIALOG_GRADES, [])

        grades_map = {grade_id: name for name, grade_id in grades}

        if grade_id not in grades_map:
            raise ValueError(f"Класс с ID {grade_id} не найден")

        return grades_map[grade_id]

    def _get_subjects(self) -> List[Tuple[int, int]]:
        """Извлекает выбранные предметы с ценами."""
        list_group: ManagedListGroup = self.dm.find(WIDGETS.LIST_GROUP)
        subjects = self.dm.dialog_data.get(WIDGETS.DIALOG_SUBJECTS, [])

        selected = []
        for subject_name, subject_id in subjects:
            checkbox: ManagedCheckbox = list_group.find_for_item(
                WIDGETS.SUBJECT_CHECKBOX,
                str(subject_id)
            )

            if checkbox.is_checked():
                counter: ManagedCounter = list_group.find_for_item(
                    WIDGETS.PRICE_COUNTER,
                    str(subject_id)
                )
                price = counter.get_value()
                selected.append((subject_id, price))

        return selected

    async def save_student(self, data: StudentData) -> None:
        """Сохраняет данные ученика в БД."""
        connection = self.dm.middleware_data.get(WIDGETS.DIALOG_CONNECTION)
        if not connection:
            raise RuntimeError("Соединение с БД не найдено")

        try:
            # Сохраняем ученика и получаем ID
            student_id = await add_student(
                connection,
                name=data.name,
                grade=data.grade
            )

            # Сохраняем предметы
            for subject_id, price in data.selected_subjects:
                await add_student_subject(
                    connection,
                    id_subject=subject_id,
                    id_student=student_id,
                    price=price
                )

            logger.info("Ученик %s сохранен с ID=%s", data.name, student_id)

        except Exception as e:
            logger.exception("Ошибка сохранения ученика %s: %s", data.name, e)
            raise


def create_student_service(dialog_manager: DialogManager) -> StudentService:
    """Фабрика для создания сервиса."""
    return StudentService(dialog_manager)