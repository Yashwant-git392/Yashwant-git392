# Project report: format and submission checklist

The report follows the supplied `reference/PROJECT_REPORT_Sequence.pdf`: two blank pages, cover, college certificate, declaration, acknowledgement, index, Chapters 1–10, and then supporting appendices. The index gives PDF page numbers, including the two blank sheets. Wide tables are presented as labelled records to keep text readable within the prescribed margins.

## Before printing or submission

- Confirm the semester with your guide: the sequence template's sample cover says **MCA-I Semester-II**, whereas the project review circular says **MCA-I Semester-I**. The report retains Semester-I until confirmed.
- Fill in your roll number and the correct project guide. The certificate is only a draft: it must be reviewed and issued/signed by the college. Review the declaration and acknowledgement for accuracy; sign the declaration only if true.
- The sequence document asks for two spiral copies, while the review circular specifies hard binding for final submission. Confirm the binding and number of copies with the college before printing.
- The prescribed wide margins leave a narrow area for screenshots and diagrams. Inspect printed output for legibility; editable, programmatically generated diagrams.net files and a separate use-case PDF are in `diagrams/` and this folder. Screens show synthetic demo data; confirm that it is acceptable and review live reports with your guide.
- The report uses Times New Roman fonts embedded in the supplied template where those embedded subsets contain the character. Characters missing from those subsets fall back to Tinos (a Times-compatible font) or DejaVu Sans for unsupported symbols. Thus the PDF is **not exclusively Times New Roman**. Both fallback font licenses are in `fonts/`. Exact Times New Roman throughout requires access to a properly licensed full font and a fresh layout/print check.

## Regenerating the PDF

The report generator reads a SQLite database **without writing it**; use a disposable fresh seeded demo database, not an existing user database. Install the application's `requirements.txt` and the additional report packages in `requirements-report.txt` into your Python environment. From the `shikayat-setu` directory, for example on Linux/macOS:

```sh
python -m pip install -r requirements.txt -r report/requirements-report.txt
# Pick a new path that does not already contain a database you need.
export SHIKAYAT_DB="$(pwd)/report-example.db"
PYTHONPATH=app python -c 'import database; database.init_db(); database.seed_if_empty()'
python report/build_report.py
python report/validate_report.py
```

On Windows PowerShell set `$env:SHIKAYAT_DB` to an unused path and `$env:PYTHONPATH = "app"` before running the same Python commands. The generator also reads the template PDF for its embedded font subsets, the bundled fallback fonts, and existing report screenshots/diagrams. Do not delete or overwrite a real database to create demo data. The output overwrites `CampusShikayatSetu_MCA-Mini-Project_Report.pdf`, so make a backup first if needed. Seed dates vary at creation time; the examples are illustrative.

`validate_report.py` checks the blank pages, required front matter and index entries, approximate text bounds and expected screenshot captions. It does not replace a visual proofread or college approval.
