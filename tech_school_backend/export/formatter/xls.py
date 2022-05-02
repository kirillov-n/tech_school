from export.formatter.base import AbstractFormatter

from string import ascii_uppercase
import xlsxwriter


class XLSFormatter(AbstractFormatter):
    def __init__(self, *args, **kwargs):
        super(XLSFormatter, self).__init__(*args, **kwargs)
        self.workbook = xlsxwriter.Workbook(self.buffer)
        self.worksheet = self.workbook.add_worksheet()

    def add_date(self):
        formatting = self.workbook.add_format({"bold": True})
        self.worksheet.write("A1", str(self.date), formatting)

    def add_top_fields(self):
        formatting = self.workbook.add_format({"bold": True, "border": 1, "bg_color": "#708090",
                                               "font_color": "#FFFFFF"})

        pos = 0
        for field in self.verbose_fields:
            self.worksheet.write(f"{ascii_uppercase[pos]}3", field, formatting)
            pos += 1

    def add_all_fields(self):
        formatting = self.workbook.add_format({"border": 1})

        row = 4
        for obj in self.queryset:
            column = 0
            for field in self.fields:
                content = str(getattr(obj, field, ""))
                self.worksheet.write(f"{ascii_uppercase[column]}{row}", content, formatting)
                column += 1
            row += 1

    def save(self):
        self.workbook.close()
