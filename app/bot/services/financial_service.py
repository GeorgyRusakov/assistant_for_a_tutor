import logging
from typing import List, Tuple
from datetime import datetime, timedelta, date

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import ManagedRadio, ManagedListGroup, ManagedCheckbox, ManagedCounter

from ..constants.widget_ids import WIDGETS
from ...infrastructure.database.models.student import StudentData
from ...infrastructure.database.db import add_student, add_student_subject


logger = logging.getLogger(__name__)

class FinancialService:
    """
    Сервис для составления финансовой отчетности
    """

    def __init__(self, dialog_manager: DialogManager):
        self.dm = dialog_manager

    def make_week_report():
        """Собирает итоговый результат для отчета за неделю"""
        pass
