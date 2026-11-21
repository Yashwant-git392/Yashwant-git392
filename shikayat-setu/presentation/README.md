# Campus Shikayat Setu — presentation

`CampusShikayatSetu_MCA-Mini-Project_Review.pptx` is a 16-slide, widescreen deck for both a project review and final viva. It uses the Office-compatible PowerPoint base template with a custom professional indigo/coral theme. The infographic shapes, text and page labels are editable in PowerPoint; the four application screenshots are images showing illustrative demo data. Each slide also has concise speaker notes.

The cover leaves roll number and project guide blank because they are unconfirmed. Replace them before presenting. Review the deck and notes yourself; the 114-test result is the documented run, not a guarantee of production readiness. Actual screenshots and counts may change with the database.

## Rebuild and check

From `shikayat-setu/`, install `python-pptx` and `Pillow`, then run:

```sh
python presentation/build_pptx.py
python presentation/validate_pptx.py
```

The generator uses images in `report/images/` and writes the PPTX in this directory. It does not open or modify the application database. The validator checks the slide count, editable objects, speaker notes, slide bounds, screen images and project-specific content; it does not replace an on-screen check in PowerPoint. No third-party rendering software is required to use the presentation.
