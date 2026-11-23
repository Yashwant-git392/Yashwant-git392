#!/usr/bin/env python3
"""Check the generated report's sequence, index and basic page bounds."""
import re
from pathlib import Path

import pymupdf
from build_report import INDEX_ITEMS, LEFT, RIGHT, TOP, BOTTOM

PDF = Path(__file__).with_name('CampusShikayatSetu_MCA-Mini-Project_Report.pdf')


def normalize(text):
    return re.sub(r'\s+', ' ', text).strip()


def main():
    doc = pymupdf.open(PDF)
    for index, expected in [(0, 'PROJECT REPORT'), (1, 'COLLEGE CERTIFICATE'),
                            (2, 'DECLARATION'), (3, 'ACKNOWLEDGEMENT'), (4, 'INDEX')]:
        assert expected in doc[index].get_text(), (index + 1, expected)
    figures = []
    screenshot_pages = {}
    for page in doc:
        assert abs(page.rect.width - 595.28) < 1 and abs(page.rect.height - 841.89) < 1
        for block in page.get_text('dict')['blocks']:
            if block['type'] == 1:
                x0, y0, x1, y1 = block['bbox']
                assert x0 >= LEFT*72/25.4-3 and x1 <= page.rect.width-RIGHT*72/25.4+3 and y0 >= TOP*72/25.4-4 and y1 <= (297-BOTTOM)*72/25.4+4, (page.number + 1, block['bbox'])
            for line in block.get('lines', []):
                for span in line['spans']:
                    x0, y0, x1, y1 = span['bbox']
                    assert x0 >= LEFT*72/25.4-4 and x1 <= page.rect.width-RIGHT*72/25.4+4 and y0 >= 0 and y1 <= page.rect.height, (page.number + 1, span)
                    assert round(span['size'], 1) in (13.0, 15.0, 16.0), (page.number + 1, span)
                    if 85 < y0 < 765:  # exclude the header and footer
                        assert y0 >= TOP*72/25.4-5 and y1 <= (297-BOTTOM)*72/25.4+5, (page.number + 1, span)
        text = page.get_text()
        captions = list(re.finditer(r'Figure (1\.1|3\.\d+[a-e]?|10\.\d+)(?!\d)', text))
        descriptions = list(re.finditer(r'Description:', text))
        assert len(captions) == len(descriptions), (page.number + 1, 'figure/description count')
        for caption, description in zip(captions, descriptions):
            assert caption.end() < description.start(), (page.number + 1, 'description must follow figure')
            figures.append(caption.group(1))
        screen_captions = [c.group(1) for c in captions if c.group(1) in {'3.7','3.8','3.9','3.10','3.11'} or c.group(1).startswith('10.')]
        if screen_captions:
            assert len(captions) == 1 and len(screen_captions) == 1, (page.number + 1, 'screenshot must have its own page')
            assert len(page.get_image_info()) == 1, (page.number + 1, 'screenshot page must have one image')
            screenshot_pages[screen_captions[0]] = page.number + 1
        if captions:
            assert len(page.get_images()) >= len(captions), (page.number + 1, 'missing image')
            if re.search(r'Figure 3\.(?:1[a-c]|2[a-d]|3[a-b]|4[a-e]|5|6)(?![\da-z])', text):
                rectangles = [r for img in page.get_images() for r in page.get_image_rects(img[0])]
                assert rectangles and max(r.width for r in rectangles) >= 150 * 72 / 25.4, (page.number + 1, 'diagram is too small')
    expected_figures = (['1.1'] + [f'3.1{c}' for c in 'abc'] + [f'3.2{c}' for c in 'abcd'] +
                        [f'3.3{c}' for c in 'ab'] + [f'3.4{c}' for c in 'abcde'] + [f'3.{n}' for n in range(5, 12)] + [f'10.{n}' for n in range(1, 26)])
    assert sorted(figures) == sorted(expected_figures), (figures, expected_figures)
    assert len(screenshot_pages) == 30 and len(set(screenshot_pages.values())) == 30
    index_pages = []
    for page in list(doc)[4:]:
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
