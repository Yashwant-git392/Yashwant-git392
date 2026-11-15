# Review 3 preparation — 21 November 2026

The college circular allocates 15 marks to Review 3. This is a preparation aid, not proof of submission, approval or a mark. The guide makes the final decision.

## Evidence in the project

- **Coding:** report Chapter 4 has routing, validation, transition, SQL and schema examples; full source is in `app/`.
- **Testing:** Chapter 5 identifies unit and acceptance-oriented integration scenarios with steps, inputs, expected and observed automated outcomes, and source test functions. `TESTING.md` explains scope and limitations. Latest source and extracted-package suite runs: 109 passed. Run `python -m pytest tests/ -q` again on the review PC.
- **Chapters 6–9:** limitations, proposed enhancements, conclusion and bibliography. The paper-based existing process is an assumption, not a verified description of the college.
- **User manual:** Chapter 10 includes 25 annotated viewport screenshots, covering all app screen types, role-specific actions and six reports, plus the validation catalogue. Scroll on long screens to see the rest.
- **Design:** Chapter 3 includes the ERD, table structure, separate actor use cases, conceptual class/record diagram, activity, deployment and module hierarchy diagrams. Editable diagrams.net sources are in `report/diagrams/`; they were generated programmatically and rendered with diagrams.net, not manually drawn in StarUML.
- **Five example records:** a fresh synthetic seed supplies at least five rows for each report. The routing report has two mode-summary rows (the only two modes) and a separate table with 37 individual complaint records. The figures may change as the database changes. Illustrative demo data is not real college evidence; confirm with the guide whether synthetic records and the detail table are acceptable.

## Do personally before review

1. Fill your roll number, identify the correct guide from the circular, and ask your guide to check the draft certificate and report format. Roll 1–34: Mrs. Priyanka M. Jagtap; 35 onwards: Mrs. Yogita A. Shirsath. Do not sign or claim institutional certification in advance.
2. Confirm the applicable SPPU syllabus pattern and any additional report format, originality, submission and presentation rules with the department.
3. Run the project and tests on the actual review machine. A new database can be selected with `SHIKAYAT_DB`; don't delete an existing database merely to reset the demo. Dependencies must be installed in advance.
4. Rehearse: student logs in and lodges a valid complaint; the appropriate officer acknowledges, starts work and resolves it with a sufficiently long remark; student confirms with feedback; admin shows all six reports and the routing detail records. Also explain public tracking, validation, ERD and separate actor use cases.
5. Explain limitations honestly: local demo credentials and development server, keyword rather than AI routing, role-dependent anonymous masking (free text may reveal identity), whole-day reopen check, and no enforced waiting period for admin force-close. Tracking errors can reveal whether a code exists; it is not strong authentication.
6. Review every report claim and citation, and verify the existing process with the college if you intend to present it as fact. Obtain actual feedback and signatures; do not assume completion or plagiarism clearance.

The circular schedules the first PPT presentation for 5 December and final PPT plus hard binding for 19 December (tentative). Check for later notices.
