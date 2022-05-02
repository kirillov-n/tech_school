from django import forms
import datetime


class ExportForm(forms.Form):
    CHOICES = (
        ("XLS", "XLS"),
        ("DOCS", "DOCS"),
        ("PDF", "PDF (не работает с кириллицей)"),
    )

    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)

    formatter = forms.ChoiceField(label="Формат", choices=CHOICES, widget=forms.RadioSelect)
    filename = forms.CharField(label="Имя документа", required=True)
    date = forms.DateField(label="Дата", initial=datetime.date.today, widget=forms.DateInput(attrs={"type": "date"}))
    signature = forms.BooleanField(label="Подпись")
