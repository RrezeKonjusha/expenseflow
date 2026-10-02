# Documentation index

| Document | File | Phase |
| --- | --- | --- |
| Design and implementation plan (living doc) | team design notes (see SRS and module docs) | all |
| Phase I: definition, feasibility, requirements analysis, framework | `phase-1.md` | I |
| Software Requirements Specification | `srs.md` | I |
| Screenshots of every page (desktop and mobile) | `screenshots/desktop/`, `screenshots/mobile/` | II, IV |
| Storybook stories (5 components, 19 states), screenshots | `frontend/src/components/*.stories.jsx`, `screenshots/storybook/` | II |
| Production readiness review: deploy checks, audits, fresh clone | `production-readiness.md` | IV |
| Final report (all phases, performance, retrospective, hats) | `final-report.md` | final |
| Demo video script, shot by shot | `demo/video-script.md` | final |
| Defense study guide: pitch, likely questions, model answers | `defense-guide.md` | all |
| Test report: results, load, security, defects | `test-report.md`, `test-results/` | III, IV |
| Phase II design: architecture, data, API, UI | `design.md` | II |
| Figma prototype spec and app screenshots | `figma-spec.md`, `design-screens/` | II |
| Stakeholder questionnaire | `questionnaire.md` | I |
| Diagrams: use case, class, ERD, component, deployment, state, sequence (2), DFD | `diagrams/*.puml`, rendered in `diagrams/rendered/` | II |
| API reference (OpenAPI 3.0) | `api/openapi.yml`, live at `/api/docs/` | II, IV |
| Module documentation (public API, logging, monitoring) | `modules/*.md` | II, III |
| Test plan and test cases | `test-plan.md` | III, IV |
| Deployment guide | `deployment.md` | IV |
| Project management, Git workflow, hats | `project-management.md` | I |
| Demo script and demo import file | `demo/README.md`, `demo/demo-import.csv` | IV |
| Maintenance and versioning | `maintenance.md` | IV |
| User manual | `user-manual.md` | IV |
| Backlog (backlog keys mapped to GitHub issues) | `backlog.csv` | I |

Re-render diagrams after editing: `java -jar plantuml.jar -tsvg -o rendered docs/diagrams/*.puml`
Regenerate the API schema: `python manage.py spectacular --file ../docs/api/openapi.yml`
Build the single documentation PDF (title page, contents, page numbers, all diagrams): `scripts/build-docs.sh` -> `build/ExpenseFlow-documentation.pdf` (needs pandoc 3, Node and Chrome; attached to each GitHub Release, not committed)
