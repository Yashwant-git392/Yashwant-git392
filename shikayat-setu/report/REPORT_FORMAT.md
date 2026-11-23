# Project report: format and submission checklist

The report follows the supplied `reference/PROJECT_REPORT_Sequence.pdf` for its sections: cover, college certificate, declaration, acknowledgement, index, Chapters 1–10, and supporting appendices. At the student’s request, it starts directly with the cover instead of the two blank pages in the template. It preserves the previous report's project material and reuses its navy-and-gold visual hierarchy. Requirements and hardware/software specifications use three-column tables; wider tables are adapted to two-column tables with labelled details to remain readable within the report margins. Table headers repeat across pages. Text uses 1.5 line spacing with space between paragraphs. Short text subtopics are kept together when practical, while long sections, tables and figures can continue across pages. Every application screenshot has its own page with its caption and explanation. Every numbered figure has an explanation directly beneath its caption. The review schedule and personal preparation reminders have been removed from the main report; the original uploaded files remain unchanged in `reference/`.

The main report is available as both PDF and editable DOCX, and every PDF under `shikayat-setu/` has a same-named DOCX companion. The Word report uses Times New Roman as a font setting (it is not embedded) and contains editable text and tables; screenshots and diagrams remain images. Its index uses Word page-reference fields rather than the PDF's fixed page numbers. Open it in Word, update all fields (Ctrl+A, then F9), and check the index and pagination before printing; Word may paginate differently depending on the installed fonts and printer. The Word version of the use-case PDF uses images; use the `.drawio` sources to edit the diagrams themselves. Reference-PDF conversions retain their original content and may need layout corrections. The existing study guide already had a DOCX version.

## Before printing or submission

- The student selected **MCA-I Semester-I**; the sequence template sample says Semester-II, while the review circular says Semester-I. Confirm with the college if needed.
- Fill in your roll number and the correct project guide. The certificate is only a draft: it must be reviewed and issued/signed by the college. Review the declaration and acknowledgement for accuracy; sign the declaration only if true.
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

On Windows PowerShell set `$env:SHIKAYAT_DB` to an unused path and `$env:PYTHONPATH = "app"` before running the same Python commands. The PDF generator reads the template PDF for its embedded font subsets, the bundled fallback fonts, and existing report screenshots/diagrams. The DOCX generator shares the report content and reads the same demo database and images. These commands overwrite their existing output files, so make backups first if needed. Seed dates vary at creation time; the examples are illustrative. To regenerate the Word companions for the two archived reference PDFs, optionally install `pdf2docx` and run `python report/build_reference_docx.py`; inspect those conversions afterwards.

`validate_report.py` checks that the cover is first, the required front matter and index entries, typography sizes and approximate page bounds, plus the numbered figures and their accompanying descriptions. It does not replace a visual proofread or college approval.
