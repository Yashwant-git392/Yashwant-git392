#!/usr/bin/env python3
"""Convert the two untouched reference PDFs to editable Word companions.

Requires the optional pdf2docx package. Converted PDF layout may need review.
"""
from pathlib import Path
from pdf2docx import Converter

HERE = Path(__file__).resolve().parent / 'reference'
for name in ('CampusShikayatSetu_Previous_Report.pdf', 'PROJECT_REPORT_Sequence.pdf'):
    pdf = HERE / name
    converter = Converter(str(pdf))
    try:
        converter.convert(str(pdf.with_suffix('.docx')))
    finally:
        converter.close()
