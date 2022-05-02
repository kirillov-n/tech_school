from django.db import models
from django import template

from export.utils import get_admin_url, get_selected

from typing import Dict, Any


register = template.Library()


@register.inclusion_tag('tags/export.html')
def export(queryset: models.QuerySet) -> Dict[str, Any]:
    return {"MODEL_URL": get_admin_url(queryset.model), "SELECTED": get_selected(queryset)}
