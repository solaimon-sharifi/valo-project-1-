# Recent changes and commits

This file summarizes the recent edits I made to the repository and the commits that were pushed to GitHub.

Summary of actions
------------------
- Created a concise, project-focused README for the "Valo Spectator Ghost" demo and added a CI badge.
- Replaced occurrences of the template repository name (`enterprise_ai_demo1_websearch`) in `docs/` with `valo_project_1` and updated quickstart clone URLs to your repo.
- Ran code formatters (black, isort) and reformatted 13 files.
- Ran pylint and achieved a score of 10.00/10.
- Added a single CI workflow at `.github/workflows/ci.yml` to run formatting checks, pylint, and pytest with coverage on Python 3.11 and 3.12.
- Added concise docs: `docs/overview.md`, `docs/architecture.md`, `docs/persona.md`.
- Added `static/images/README.md` for demo screenshots and assets.
- Fixed a duplicated workflow block in the CI YAML and committed the corrected workflow.
- Ran the full pytest suite: 69 tests passed, 100% coverage. Generated `coverage.xml` and `htmlcov/`.
- Committed and pushed all changes to the remote `origin` on branch `main`.

Git commits (recent)
--------------------
- "Add AI Spectator Ghost web interface with Valorant theme" (earlier change)
- "Add CI workflow, docs (overview/architecture/persona), and README badges" (added CI + docs)
- "Format and docs: finish formatting, update CI workflow, add docs and badges" (final cleanup and pushed)

Notes & next steps
------------------
- `.env` exists locally and contains an OpenAI key; it is not tracked by git. Rotate this key if it has been shared inadvertently.
- If you'd like a deploy pipeline or demo screenshots added, I can add a `DEPLOY.md` and placeholder images.
