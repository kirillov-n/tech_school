from django.db import models

from typing import Iterator


def get_admin_url(model: models.Model) -> str:
    return f"/admin/{model._meta.app_label}/{model._meta.model_name}/"


def get_selected(queryset: models.QuerySet) -> Iterator[int]:
    return queryset.values_list('id', flat=True).distinct().iterator()
