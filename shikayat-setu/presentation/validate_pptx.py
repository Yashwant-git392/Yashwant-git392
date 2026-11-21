#!/usr/bin/env python3
"""Check structure and essential claims of the generated presentation."""
from pathlib import Path
from zipfile import ZipFile

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

PPT = Path(__file__).with_name('CampusShikayatSetu_MCA-Mini-Project_Review.pptx')


def main():
    with ZipFile(PPT) as package:
        assert package.testzip() is None
        theme = package.read('ppt/theme/theme1.xml').decode()
        assert 'Campus Professional' in theme
    presentation = Presentation(PPT)
    assert len(presentation.slides) == 16
    assert abs(presentation.slide_width.inches - 13.3333) < .01
    assert abs(presentation.slide_height.inches - 7.5) < .01
    all_text = []
    images = 0
    for number, slide in enumerate(presentation.slides, 1):
        assert slide.has_notes_slide, f'Slide {number} has no speaker notes'
        notes = slide.notes_slide.notes_text_frame.text
        assert len(notes.strip()) > 30, f'Slide {number} has insufficient notes'
        for obj in slide.shapes:
            assert obj.left >= -1000 and obj.top >= -1000, (number, obj.name)
            assert obj.left + obj.width <= presentation.slide_width + 1000, (number, obj.name)
            assert obj.top + obj.height <= presentation.slide_height + 1000, (number, obj.name)
            if obj.has_text_frame:
                all_text.append(obj.text_frame.text)
            if obj.shape_type == MSO_SHAPE_TYPE.PICTURE:
                images += 1
    assert images == 4
    text = '\n'.join(all_text)
    for required in ('Yashwant Santosh Ahire', 'STUDENT', 'OFFICER', 'ADMINISTRATOR',
                     'PUBLIC VISITOR', 'SQLite', '114', '24', '72', '168',
                     '37 routing-detail records', 'future ideas', 'Thank you'):
        assert required.lower() in text.lower(), required
    for prohibited in ('github', 'git clone', 'review 3', '19 december', 'guide: confirm'):
        assert prohibited not in text.lower(), prohibited
    assert 'Guide: ____________________' in text and 'Roll No.: ____________' in text
    print(f'Validated {len(presentation.slides)} slides, 16 notes, {images} screenshots and editable infographic shapes.')


if __name__ == '__main__':
    main()
