# Project report: format and submission checklist

The report starts with the four supplied pages in `reference/PROJECT REPORT Sequence Yashwant.pdf`: cover, declaration, acknowledgement and official index. As requested, the previous generated front matter and populated index are omitted. The supplied index has **blank page numbers**, and the supplied pages do **not** contain a college certificate. Confirm whether the college requires a separate issued certificate and fill in index page numbers before submission. The uploaded file's local-path metadata was removed with the student's approval; its visible pages are unchanged.

The PDF inserts the four supplied pages without re-rendering. The supplied PDF is image-only, so the four pages in the Word report have been manually reconstructed as editable text and an editable index table; the college logo remains an image. The reconstruction approximates, but is not pixel-identical to, the official pages. Compare its wording and layout against the original before submission. The separate companion reference DOCX retains the four pages as images for comparison. The remainder of the Word report contains editable text and tables, with screenshots and diagrams as images. Word pagination may differ from the PDF, so check it in Word before printing. The official index table has blank page numbers; enter them manually after checking Word pagination. Section bookmarks and page-number fields remain in the editable report.

The body retains Chapters 1–10 and supporting appendices. Requirements and specifications use tables, text uses 1.5 line spacing, and each application screenshot has its own page with its caption and explanation. Descriptions remain beneath numbered figures. The original reference material remains in `reference/`.

## Before printing or submission

- The student selected **MCA-I Semester-I**; the sequence template sample says Semester-II, while the review circular says Semester-I. Confirm with the college if needed.
- The supplied pages leave the guide and index page numbers blank and include an originality declaration. Review the declaration and acknowledgement for accuracy, sign only if true, and supply any required roll number. Ask the college whether a separately issued certificate is required.
- The sequence document asks for two spiral copies, while the review circular specifies hard binding for final submission. Confirm the binding and number of copies with the college before printing.
- The student-requested larger diagrams use reduced margins (left 25.4 mm, right 15 mm, top 36 mm, bottom 25.4 mm), rather than the wider margins in the sequence template. Check with the college whether this is acceptable and inspect printed output for legibility; editable, programmatically generated diagrams.net files and a separate use-case PDF are in `diagrams/` and this folder. Screens show synthetic demo data; confirm that it is acceptable and review live reports with your guide.
- The report uses Times New Roman fonts embedded in the supplied template where those embedded subsets contain the character. Characters missing from those subsets fall back to Tinos (a Times-compatible font) or DejaVu Sans for unsupported symbols. Thus the PDF is **not exclusively Times New Roman**. Both fallback font licenses are in `fonts/`. Exact Times New Roman throughout requires access to a properly licensed full font and a fresh layout/print check.

## Regenerating the PDF

The report generator reads a SQLite database **without writing it**; use a disposable fresh seeded demo database, not an existing user database. Install the application's `requirements.txt` and the additional report packages in `requirements-report.txt` into your Python environment. From the `shikayat-setu` directory, for example on Linux/macOS:

```sh
python -m pip install -r requirements.txt -r report/requirements-report.txt
# Pick a new path that does not already contain a database you need.
export SHIKAYAT_DB="$(pwd)/report-example.db"
PYTHONPATH=app python -c 'import database; database.init_db(); database.seed_if_empty()'
python report/build_report.py
python report/build_report_docx.py
python report/build_usecase_docx.py
python report/validate_report.py
python report/validate_docx.py
```

On Windows PowerShell set `$env:SHIKAYAT_DB` to an unused path and `$env:PYTHONPATH = "app"` before running the same Python commands. The PDF generator inserts the four official pages and reads the original sequence template for its embedded font subsets, plus bundled fallback fonts and existing report screenshots/diagrams. The DOCX generator shares the report content and reads the same demo database and images. These commands overwrite their existing output files, so make backups first if needed. Seed dates vary at creation time; the examples are illustrative. To regenerate the Word companions for the two archived reference PDFs, optionally install `pdf2docx` and run `python report/build_reference_docx.py`; inspect those conversions afterwards.

`validate_report.py` checks that the four supplied pages are visually unchanged, the body sections exist, printed body page numbers are correct, and figures, descriptions and page bounds are intact. It does not populate or verify the blank image-based index. It does not replace a visual proofread or college approval.
