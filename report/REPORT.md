# SmartLibrary — Project Report (companion to the PDF)

**Compiled PDF:** [`SmartLibrary_MCA-Mini-Project_Report.pdf`](SmartLibrary_MCA-Mini-Project_Report.pdf) — 33 pages, A4, SPPU MCA-I (Sem-I) Application Development, A.Y. 2026-27.

This file documents how the report was produced so it can be regenerated after any change
to the application or the diagrams.

## Contents of the PDF

| § | Section | Source of truth |
|---|---------|-----------------|
| — | Cover · Certificate · INDEX | `build_report.py` |
| Ch. 1 | Abstract | hand-written |
| Ch. 2 | Introduction — problem statement, similar systems, feasibility, objectives, users, scope | hand-written + report tables |
| Ch. 3 | System Analysis & Design — FR/NFR, ERD, use case, class, activity, deployment, module hierarchy, 4 screen mock-ups, sample input/output with live seeded data (₹26 fines, 7 issued, 5 overdue) | `images/fig-*.png`, `images/screen-*-mock.png` + `build_report.py` |
| Ch. 4 | Coding — login, issue, fine engine, atomic seed, report queries (verified excerpts) | live `mini-project/app/` source |
| Ch. 5 | Testing — Track A: 12/12 pytest (0.36 s) · Track B: 8 manual scenarios executed 09-11-2026; regression log | `mini-project/tests/test_app.py`, live app on :5000 |
| Ch. 6 | Limitations L-1…L-10 | hand-written |
| Ch. 7 | Proposed enhancements E-1…E-10 | hand-written |
| Ch. 8 | Conclusion | hand-written |
| Ch. 9 | Bibliography (IEEE style) | hand-written |
| Ch. 10 | User Manual — runbook + 16 screens with per-field validation rules, FAQ | verified against the running app |
| App. A | `schema.sql` verbatim | `../mini-project/app/schema.sql` |
| App. B | Seed data — 12 books / 8 members / first 8 of 15 transactions (queried live from `smartlibrary.db`) | `build_report.py` → `db_rows()` |
| App. C | Glossary & acronyms | hand-written |

## Rebuilding

```bash
cd report

python gen_diagrams.py     # regenerates images/fig-*.png       (matplotlib + graphviz-free)
python gen_screens.py      # regenerates images/screen-*-mock.png (styled renderings, real data)
python build_report.py     # two-pass build → SmartLibrary_MCA-Mini-Project_Report.pdf
```

Dependencies: `fpdf2`, `Pillow`, `matplotlib`. Figures are embedded at generation time;
the INDEX dot leaders and page numbers are resolved in the second pass, so a single
`python build_report.py` invocation performs both passes automatically.

## Conventions & caveats

- **Screen images are renderings, not photos.** They are styled window drawings generated
  from the live database contents — the same values the app shows at `http://127.0.0.1:5000`.
- **Fine amounts, counts and registers** (₹26 collected · ₹160 pending · issued 7 · overdue 5)
  are queried live from the seeded `mini-project/app/smartlibrary.db` at build time.
- **₹ symbol** renders via DejaVu Sans; ₹ requires a Unicode font — do not substitute a
  Latin-1 core font.
- Sample outputs satisfy the ≥ 5 valid records per report requirement of the SPPU brief.
- git does **not** track `mini-project/app/smartlibrary.db` (see `.gitignore`); it is
  auto-created and re-seeded on first run. Appendix B data was captured from the seeded file.

## Branch

All work lives on `arena/aafd53cc-yashwant-git392`. The report was tuned against the
*Application Development Review Schedule 2026-27* (Review 3: **21-11-2026**, Final: **19-12-2026**).
