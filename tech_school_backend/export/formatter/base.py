from django.db import models

from abc import ABCMeta, abstractmethod
from typing import Optional, List
from io import BytesIO
import datetime


class AbstractFormatter(metaclass=ABCMeta):
    def __init__(self, filename: str, date: datetime.date, queryset: models.QuerySet, buffer: Optional[BytesIO] = None):
        self.filename = filename
        self.date = date
        self.queryset = queryset
        self.buffer = buffer if buffer else open(self.filename, "w")

    @property
    def fields(self) -> List[str]:
        return [f.name for f in self.queryset.model._meta.get_fields() if isinstance(f, models.Field)]

    @property
    def verbose_fields(self) -> List[str]:
        return [f.verbose_name for f in self.queryset.model._meta.get_fields() if isinstance(f, models.Field)]

    @abstractmethod
    def add_date(self):
        pass

    def add_table(self, *args, **kwargs):
        self.add_top_fields(*args, **kwargs)
        self.add_all_fields(*args, **kwargs)

    @abstractmethod
    def add_top_fields(self, *args, **kwargs):
        pass

    @abstractmethod
    def add_all_fields(self, *args, **kwargs):
        pass

    @abstractmethod
    def save(self):
        pass

    def format(self) -> BytesIO:
        self.add_date()

        self.add_table()

        self.save()
        self.buffer.seek(0)

        return self.buffer
