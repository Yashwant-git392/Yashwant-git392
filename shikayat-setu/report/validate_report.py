#!/usr/bin/env python3
"""Check the generated report's sequence, index and basic page bounds."""
import re
from pathlib import Path

import pymupdf
from build_report import INDEX_ITEMS

PDF = Path(__file__).with_name('CampusShikayatSetu_MCA-Mini-Project_Report.pdf')


def normalize(text):
    return re.sub(r'\s+', ' ', text).strip()


def main():
    doc = pymupdf.open(PDF)
    assert all(not doc[i].get_text().strip() and not doc[i].get_images() for i in (0, 1))
    for index, expected in [(2, 'PROJECT REPORT'), (3, 'COLLEGE CERTIFICATE'),
                            (4, 'DECLARATION'), (5, 'ACKNOWLEDGEMENT'), (6, 'INDEX')]:
        assert expected in doc[index].get_text(), (index + 1, expected)
    for page in doc:
        assert abs(page.rect.width - 595.28) < 1 and abs(page.rect.height - 841.89) < 1
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    x0, y0, x1, y1 = span['bbox']
                    assert x0 >= 140 and x1 <= 490 and y0 >= 0 and y1 <= page.rect.height, (page.number + 1, span)
    index_pages = []
    for page in list(doc)[6:]:
        if 'CHAPTER 1' in page.get_text():
            break
        index_pages.append(page.get_text())
    index_text = normalize(' '.join(index_pages))
    previous_page = 1
    for number, title, key in INDEX_ITEMS:
        pattern = rf'(?<!\S){re.escape(number)}\s+{re.escape(title)}\s+—\s+(\d{{3}})'
        match = re.search(pattern, index_text)
        assert match, (number, title, 'not found in index')
        page_no = int(match.group(1))
        assert page_no >= previous_page and page_no <= len(doc), (number, page_no)
        previous_page = page_no
        text = normalize(doc[page_no - 1].get_text())
        if key.startswith('section:'):
            assert re.search(r'(?<!\S)' + re.escape(number) + r'\s', text), (number, page_no)
        elif key.startswith('ch'):
            assert 'CHAPTER ' + number in text, (number, page_no)
        else:
            assert 'APPENDIX ' + number in text, (number, page_no)
    full_text = normalize(' '.join(page.get_text() for page in doc))
    for n in range(1, 26):
        assert re.search(rf'Figure 10\.{n}(?!\d)', full_text), f'missing manual screenshot {n}'
    print(f'Validated {len(doc)} pages, {len(INDEX_ITEMS)} index entries and 25 manual screenshot captions.')


if __name__ == '__main__':
    main()
