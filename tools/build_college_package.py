#!/usr/bin/env python3
"""Build the small, runnable college-submission ZIP without local user data."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'shikayat-setu'
OUTPUT = ROOT / 'Campus_Shikayat_Setu_College_Submission.zip'

README = '''CAMPUS SHIKAYAT SETU — COLLEGE SUBMISSION PACKAGE

This package contains the runnable application, project report, project
diagrams, and presentation. Project data shown in the documents is illustrative.

PROJECT DOCUMENTS
- report/CampusShikayatSetu_MCA-Mini-Project_Report.pdf
- report/CampusShikayatSetu_MCA-Mini-Project_Report.docx
- report/Campus_Shikayat_Setu_Use_Case_Diagrams.pdf and .docx
- report/Campus_Shikayat_Setu_Project_Diagrams.pdf and .docx
- report/diagrams/ contains editable diagrams.net source files
- report/reference/PROJECT REPORT Sequence Yashwant.pdf and .docx contain the supplied front pages
- presentation/CampusShikayatSetu_MCA-Mini-Project_Review.pptx

The supplied official index has blank page numbers; fill them in before submission.
The supplied pages do not include a certificate; confirm whether one is required.
The four supplied pages are images in Word, and their text is not editable.
Add any required roll number and confirmed guide, review the declaration before
signing, and inspect Word pagination before printing.
The report starts with the cover and uses reduced margins to enlarge diagrams,
as requested; confirm these changes and the required binding with the college.
The PDF uses font fallbacks for characters absent from the supplied template.

RUN THE APPLICATION
1. Extract the ZIP fully. Install Python 3.10 or newer (3.11/3.12 recommended).
   On Windows, select "Add Python to PATH" when installing Python.
2. Open the extracted shikayat-setu folder in VS Code. Choose Terminal > Run
   Task > Start Campus Shikayat Setu. Alternatively, double-click
   Start_Project.bat on Windows or run sh start-project.sh on macOS/Linux.
3. On the first run, the launcher creates .venv and installs dependencies;
   internet or locally available packages are normally needed. It reuses the
   environment on later runs. Keep the terminal open until finished.
4. Visit http://127.0.0.1:5001 on the same computer. Press Ctrl+C in the
   terminal to stop. Native Windows execution was not tested in this environment.

DEMONSTRATION ACCOUNTS
Admin:   admin / admin123
Student: MCA2026001 / student123
Officer: hostel.officer / officer123

A new database is created and seeded only if needed, at app/shikayat_setu.db.
Existing data is not reset by the launcher. This ZIP does not contain a database
or a prebuilt .venv. The seeded names and complaints are synthetic examples.
Demo credentials and the development server are not suitable for production.
'''

# Only runtime code, portable launchers, and presentation-ready documents.
FILES = [
    'run.py', 'start_project.py', 'Start_Project.bat', 'start-project.sh', 'requirements.txt',
    '.vscode/tasks.json', '.vscode/settings.json',
    'report/CampusShikayatSetu_MCA-Mini-Project_Report.pdf',
    'report/CampusShikayatSetu_MCA-Mini-Project_Report.docx',
    'report/reference/PROJECT REPORT Sequence Yashwant.pdf',
    'report/reference/PROJECT REPORT Sequence Yashwant.docx',
    'report/Campus_Shikayat_Setu_Use_Case_Diagrams.pdf',
    'report/Campus_Shikayat_Setu_Use_Case_Diagrams.docx',
    'report/Campus_Shikayat_Setu_Project_Diagrams.pdf',
    'report/Campus_Shikayat_Setu_Project_Diagrams.docx',
    'report/diagrams/fig-erd.drawio',
    'report/diagrams/fig-usecase.drawio',
    'report/diagrams/fig-class.drawio',
    'report/diagrams/fig-activity.drawio',
    'report/diagrams/fig-deployment.drawio',
    'report/diagrams/fig-modules.drawio',
    'presentation/CampusShikayatSetu_MCA-Mini-Project_Review.pptx',
]
RUNTIME_SUFFIXES = {'.py', '.sql', '.html', '.css', '.js'}


def main():
    app_files = sorted(p.relative_to(PROJECT).as_posix() for p in (PROJECT / 'app').rglob('*')
                       if p.is_file() and p.suffix in RUNTIME_SUFFIXES
                       and '__pycache__' not in p.parts)
    paths = sorted(FILES + app_files)
    assert len(paths) == len(set(paths)) and all((PROJECT / p).is_file() for p in paths)
    with ZipFile(OUTPUT, 'w', compression=ZIP_DEFLATED, compresslevel=7) as archive:
        info = ZipInfo('shikayat-setu/README_FIRST.txt', (2026, 1, 1, 0, 0, 0))
        info.compress_type = ZIP_DEFLATED
        info.create_system = 3
        info.external_attr = 0o100644 << 16
        archive.writestr(info, README.lstrip().encode('utf-8'))
        for path in paths:
            src = PROJECT / path
            info = ZipInfo.from_file(src, 'shikayat-setu/' + path)
            info.create_system = 3
            info.external_attr = (0o100755 if path == 'start-project.sh' else 0o100644) << 16
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, src.read_bytes(), compress_type=ZIP_DEFLATED, compresslevel=7)
    with ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        assert len(names) == len(paths) + 1
        assert not any(n.endswith(('.db', '.sqlite', '.sqlite3', '.pyc')) for n in names)
    print(f'Built {OUTPUT.name}: {len(paths)+1} files, {OUTPUT.stat().st_size:,} bytes.')


if __name__ == '__main__':
    main()
