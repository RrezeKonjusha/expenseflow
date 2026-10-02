# Project management and Git workflow

Solo project: the professor approved an exception to the 5-person team rule. The five team roles are kept as
"hats" one person wears, shown on every issue as a `hat:*` label.

| Hat | Label | Owns |
| --- | --- | --- |
| Project manager, Scrum master, QA lead | `hat:pm-qa` | Board, SRS, questionnaire, test report, Cypress, presentations |
| Backend: auth and security | `hat:backend-auth` | `accounts`, `core`, security tests, throttling |
| Backend: business and reporting | `hat:backend-business` | `expenses`, `reporting`, MongoDB, import/export, Locust |
| Frontend | `hat:frontend` | React app, routing, pages, Figma, Storybook |
| DevOps and database | `hat:devops-db` | Docker, Caddy, CI/CD, VPS, PostgreSQL logic, monitoring |

## Tools

| Need | Tool | Where |
| --- | --- | --- |
| Version control | Git + GitHub | `RrezeKonjusha/expenseflow` |
| Task tracking | GitHub Issues | 78 issues: epics are parent issues with sub-issues |
| Board | GitHub Projects | columns To Do, In Progress, In Review, Done |
| Sprints | Milestones | `Sprint 1` to `Sprint 7`, two weeks each |
| Priorities | Labels | `priority:highest`, `priority:high`, `priority:medium`, `priority:low` |
| Issue types | Labels | `type:epic`, `type:story`, `type:task`, `type:bug` |
| Estimates | Issue body | "Story points: n" (1, 2, 3, 5, 8) |
| CI/CD | GitHub Actions | `ci.yml` on every PR and push to `develop`/`main`; `deploy.yml` on `main` |

`backlog.csv` lists every backlog item with its original key (`EXP-n`, used in the first commits) and its
GitHub issue number.

## Branches and pull requests

- `main`: production. Merging into `main` deploys to the VPS.
- `develop`: integration. Every feature lands here first.
- `feature/<issue>-short-name`: one branch per issue, cut from `develop`.

Both `main` and `develop` are protected: a pull request is required, the three CI checks must pass
("Backend lint + unit + integration", "Frontend lint + build", "Test environment (Docker) + Newman + Cypress"),
the branch must be up to date, conversations must be resolved, and force pushes and deletion are blocked.
Admins are not exempt. Required approvals are 0 because of the solo exception; instead every pull request gets a
self-review checklist comment before it is merged.

Pull requests are merged with a merge commit, so every conventional commit and its issue reference stays in the
history. At the end of a sprint `develop` is merged into `main` through a pull request and tagged `v0.<sprint>.0`.

## Commits

Conventional Commits with the issue number: `feat(expenses): add submit transition (#35)`, body ends with
`Refs #35`. Pull request bodies say `Closes #35`. Types used: `feat`, `fix`, `test`, `docs`, `ci`, `build`, `chore`.

## How the GitHub setup was done (reproducible)

```bash
# repository and integration branch
gh repo create RrezeKonjusha/expenseflow --public --source . --push
git branch develop main && git push -u origin develop

# branch protection (repeat for main)
gh api -X PUT repos/RrezeKonjusha/expenseflow/branches/develop/protection --input protection.json
#   protection.json: required_status_checks {strict: true, contexts: [the three CI jobs]},
#   enforce_admins: true, required_pull_request_reviews {required_approving_review_count: 0},
#   allow_force_pushes: false, allow_deletions: false, required_conversation_resolution: true

# production environment (Settings > Environments > production), secrets added in deployment.md
# labels, milestones Sprint 1-7, 78 issues with sub-issues: created from backlog.csv with gh (one-off script)

# board (needs the project scope: gh auth refresh -s project)
gh project create --owner RrezeKonjusha --title "ExpenseFlow"
gh project link <number> --owner RrezeKonjusha --repo RrezeKonjusha/expenseflow
```

On the board, the Status field has the four columns. The built-in workflows "Auto-add to project" (new issues
from the repo), "Item closed" and "Pull request merged" (both set Done) are switched on; In Progress and
In Review are set by hand when a branch is started and when its pull request opens. The board view groups by
Status; a second table view groups by milestone (sprint) and shows labels, so it doubles as the sprint backlog.

## Sprint ritual (solo)

| When | What | Evidence |
| --- | --- | --- |
| Sprint start | Pick issues into the milestone, set them to To Do | milestone page |
| Daily | Move the issue being worked on to In Progress | board |
| Each change | Branch, commits with `(#n)`, PR with self-review, green CI, merge | PR list |
| Sprint end | Close the milestone, merge `develop` into `main`, tag, short retrospective in the milestone description | tags, milestones |
