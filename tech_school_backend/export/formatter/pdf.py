from export.formatter.base import AbstractFormatter

from pdfme import build_pdf

from typing import Dict, Any


class PDFFormatter(AbstractFormatter):
    def __init__(self, *args, **kwargs):
        super(PDFFormatter, self).__init__(*args, **kwargs)
        self.document = {
            "style": {
                "margin_bottom": 15, "text_align": "j",
                "page_size": "a4", "margin": [60, 50]
            },
            "formats": {
                "url": {"c": "blue", "u": 1},
                "title": {"b": 1, "s": 13}
            },
            "sections": [
                {
                    "content": []
                },
            ]
        }

    def _add(self, element: Dict[str, Any]):
        self.document["sections"][0]["content"].append(element)

    def add_date(self):
        self._add({".": str(self.date), "style": "title", "label": "title1", "outline": {"level": 1,
                                                                                         "text": str(self.date)}})

    def add_table(self):
        table = {'widths': [], 'style': {'border_width': 0.5}, 'fills': [{'pos': '0', 'color': "#708090"}], 'table': []}

        super(PDFFormatter, self).add_table(table)

        self._add(table)

    def add_top_fields(self, table: Dict[str, Any]):
        for field in self.fields:
            table["widths"].append(max(len(field)/10, 0.3))
        table["table"].append([field.title() for field in self.fields])

    def add_all_fields(self, table: Dict[str, Any]):
        fields = [[str(getattr(obj, field, "")) for field in self.fields] for obj in self.queryset]
        table["table"] = table["table"] + fields

    def save(self):
        build_pdf(self.document, self.buffer)
