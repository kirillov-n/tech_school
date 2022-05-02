from .base import AbstractFormatter
from .xls import XLSFormatter
from .docs import DOCSFormatter
from .pdf import PDFFormatter

from typing import Dict, Type


FORMATTERS: Dict[str, Type[AbstractFormatter]] = {
    "XLS": XLSFormatter,
    "DOCS": DOCSFormatter,
    "PDF": PDFFormatter
}
