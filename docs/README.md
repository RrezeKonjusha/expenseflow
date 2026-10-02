# Documentation index

| Document | File | Phase |
| --- | --- | --- |
| Design and implementation plan (living doc) | team design notes (see SRS and module docs) | all |
| Phase I: definition, feasibility, requirements analysis, framework | `phase-1.md` | I |
| Software Requirements Specification | `srs.md` | I |
| Stakeholder questionnaire | `questionnaire.md` | I |
| Diagrams: use case, class, ERD, component, deployment, state, sequence (2), DFD | `diagrams/*.puml`, rendered in `diagrams/rendered/` | II |
| API reference (OpenAPI 3.0) | `api/openapi.yml`, live at `/api/docs/` | II, IV |
| Module documentation (public API, logging, monitoring) | `modules/*.md` | II, III |
| Test plan and test cases | `test-plan.md` | III, IV |
| Deployment guide | `deployment.md` | IV |
| Maintenance and versioning | `maintenance.md` | IV |
| User manual | `user-manual.md` | IV |
| Backlog (backlog keys mapped to GitHub issues) | `backlog.csv` | I |

Re-render diagrams after editing: `java -jar plantuml.jar -tsvg -o rendered docs/diagrams/*.puml`
Regenerate the API schema: `python manage.py spectacular --file ../docs/api/openapi.yml`
Export everything to one PDF for submission: `pandoc docs/*.md -o ExpenseFlow-docs.pdf --toc`
