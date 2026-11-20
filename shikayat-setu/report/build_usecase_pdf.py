"""Build a printable four-page PDF from the diagrams.net use-case exports.

The editable source is diagrams/fig-usecase.drawio. Export each named page to
its matching PNG in images/ before running this script. Requires fpdf2, Pillow.
"""
from pathlib import Path
from fpdf import FPDF

REPORT = Path(__file__).resolve().parent
PAGES = ('student', 'officer', 'administrator', 'public-visitor')
OUT = REPORT / 'Campus_Shikayat_Setu_Use_Case_Diagrams.pdf'


def main():
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(False)
    pdf.set_title('Campus Shikayat Setu — Actor Use-Case Diagrams')
    for page in PAGES:
        pdf.add_page()
        pdf.image(str(REPORT / 'images' / f'fig-usecase-{page}.png'), x=18, y=12, w=261, h=186, keep_aspect_ratio=True)
    pdf.output(OUT)
    print('Built:', OUT)


if __name__ == '__main__':
    main()
