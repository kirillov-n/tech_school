from .forms import ExportForm

from .formatter import FORMATTERS

from .utils import get_selected

from django.contrib import admin
from django.http import HttpRequest, FileResponse
from django.shortcuts import render
from django.db import models

from io import BytesIO


@admin.action(description="Экспортировать как...")
def export(_: admin.ModelAdmin, request: HttpRequest, queryset: models.QuerySet):
    """Export models as document"""
    if "apply" in request.POST:
        form = ExportForm(request.POST)
        if form.is_valid():
            buffer = BytesIO()
            FORMATTERS[form.cleaned_data["formatter"]](form.cleaned_data["filename"], form.cleaned_data["date"],
                                                       queryset, buffer).format()
            return FileResponse(buffer, as_attachment=True, filename=form.cleaned_data["filename"])
    else:
        form = ExportForm(initial={'_selected_action': get_selected(queryset)})
    return render(request, "admin/export.html", {"form": form, "title": "Экспорт моделей"})


admin.site.add_action(export)
