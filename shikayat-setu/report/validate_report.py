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
    figures = []
    for page in doc:
        assert abs(page.rect.width - 595.28) < 1 and abs(page.rect.height - 841.89) < 1
        for block in page.get_text('dict')['blocks']:
            if block['type'] == 1:
                x0, y0, x1, y1 = block['bbox']
                assert x0 >= 143 and x1 <= 488 and y0 >= 142 and y1 <= 735, (page.number + 1, block['bbox'])
            for line in block.get('lines', []):
                for span in line['spans']:
                    x0, y0, x1, y1 = span['bbox']
                    assert x0 >= 140 and x1 <= 490 and y0 >= 0 and y1 <= page.rect.height, (page.number + 1, span)
                    assert round(span['size'], 1) in (13.0, 15.0, 16.0), (page.number + 1, span)
                    if 125 < y0 < 756:  # exclude the header and footer
                        assert y0 >= 139 and y1 <= 739, (page.number + 1, span)
        text = page.get_text()
        captions = list(re.finditer(r'Figure (1\.1|3\.\d+[a-d]?|10\.\d+)(?!\d)', text))
        descriptions = list(re.finditer(r'Description:', text))
        assert len(captions) == len(descriptions), (page.number + 1, 'figure/description count')
        for caption, description in zip(captions, descriptions):
            assert caption.end() < description.start(), (page.number + 1, 'description must follow figure')
            figures.append(caption.group(1))
        if captions:
            assert len(page.get_images()) >= len(captions), (page.number + 1, 'missing image')
    expected_figures = (['1.1'] + [f'3.1{c}' for c in 'abc'] + [f'3.2{c}' for c in 'abcd'] +
                        [f'3.{n}' for n in range(3, 12)] + [f'10.{n}' for n in range(1, 26)])
    assert sorted(figures) == sorted(expected_figures), (figures, expected_figures)
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
    for forbidden in ('github', 'review 3', 'review schedule', 'draft:', 'before final submission'):
        assert forbidden not in full_text.lower(), forbidden
    for n in range(1, 26):
        assert re.search(rf'Figure 10\.{n}(?!\d)', full_text), f'missing manual screenshot {n}'
    print(f'Validated {len(doc)} pages, {len(INDEX_ITEMS)} index entries and {len(figures)} figures with descriptions.')


if __name__ == '__main__':
    main()
