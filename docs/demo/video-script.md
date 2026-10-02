# Demo video script (6 minutes 30 seconds)

Recorded on production (`https://<domain>`). Tool: QuickTime Player > File > New Screen Recording, or OBS. Screen
1920 x 1080, browser zoom 110%, Chrome with three profiles already signed in (Arta, Besa, Admin) and one guest
window. Microphone close, notifications off (Focus mode). Speak the lines in the "Say" column; they are written to
be read at a calm pace.

## Before recording (10 minutes)

1. `python docs/demo/make_demo_import.py` and keep `demo-import.csv` on the desktop.
2. On the server: `docker compose -p prod exec api python manage.py seed_demo --reset`.
3. Open tabs in the guest window: the app, `/api/docs/`, the activation inbox (production email) or Mailpit.
   In other tabs: Grafana dashboard, the latest green GitHub Actions run, the GitHub Project board, one merged pull
   request with its self-review comment.
4. Do one dry run without recording.

## Shots

| # | Time | Screen | Action | Say |
| --- | --- | --- | --- | --- |
| 1 | 0:00-0:20 | Title card (slide 1 of the final deck) | Hold | "ExpenseFlow: expense claims and approvals. I'm Rreze Konjusha; this is my UBT Lab Course 2 project, built alone under an approved exception." |
| 2 | 0:20-0:40 | Guest window, live URL | Click the padlock, then open `/api/docs/` and scroll the endpoint list | "It runs on a public server over HTTPS. The REST API is versioned under api/v1 and documented with OpenAPI 3." |
| 3 | 0:40-1:20 | Guest window | Register a new user, open the activation email, click the link, log in | "A new employee registers. The account stays inactive until the emailed link is used; the link works only once. Login returns a short-lived access token and sets a refresh token in an httpOnly cookie." |
| 4 | 1:20-2:05 | Arta | New expense: Meal, project ALPHA, 60 EUR, 1 attendee, Save | "Arta adds a client lunch: 60 euros, one attendee. The policy caps meals at 25 euros per attendee, so the server refuses it and says why." |
| 5 | 2:05-2:25 | Arta | Change attendees to 3, Save, Submit; toast | "With three attendees it is within policy. She saves the draft and submits it for approval." |
| 6 | 2:25-2:50 | Arta | Expenses > Import, upload `demo-import.csv` | "She can also import expenses from a file. Four rows are created as drafts; row five breaks the meal policy and comes back with its reason." |
| 7 | 2:50-3:10 | Arta, DevTools Network tab | Reload; point at `POST /auth/refresh/` | "On reload, the app asks the server for a new access token using the cookie. The refresh token rotates every time, and an old one is rejected." |
| 8 | 3:10-3:50 | Besa | Approvals; type "hotel" in search; Approve one; then Approve the GAMMA "Docking station" row; red toast | "Besa manages Engineering. Full-text search finds the hotel claims. She approves one. The next would push project GAMMA over its budget: the database trigger and a CHECK constraint refuse it, whatever screen or script tries." |
| 9 | 3:50-4:40 | Admin | Dashboard; Reports: last quarter, group by department, status APPROVED; Run; Save; open it; Export XLSX and open the file | "The admin sees all departments. The report builder groups and filters any way she likes; a saved report is a MongoDB snapshot, and it exports to CSV, Excel or JSON." |
| 10 | 4:40-5:10 | Admin | Reimbursement run until today, confirm the count; Audit log, expand an entry | "Reimbursement is one stored procedure call that marks every approved expense as paid and returns the count. Every critical action is in the audit log, with who did it and what changed." |
| 11 | 5:10-5:40 | Grafana, then GitHub Actions | Show the request and latency panels and the Loki errors panel; then a green CI run with its three jobs | "Prometheus and Grafana watch the API, Loki collects every container's logs. Each pull request runs linting, 85 backend tests with 94 percent coverage, the API contract tests and browser tests on a full Docker stack." |
| 12 | 5:40-6:05 | GitHub Project board, then a merged PR | Scroll the board; open a PR and its self-review comment | "Work is planned in GitHub Issues and sprints; every change went through a branch, a pull request with a self-review, and green CI before it could merge." |
| 13 | 6:05-6:30 | Final deck: testing and future work slide | Hold | "Under a thousand simulated users there were no failed requests, and the cache made typical requests six times faster. Next: more API replicas for the slowest one percent, and the path to microservices. Thank you." |

## After recording

- Trim the start and end; keep it between 6 and 7 minutes.
- Export 1080p MP4 (H.264). Name: `ExpenseFlow-demo-Rreze-Konjusha.mp4`.
- Upload unlisted to YouTube or to Google Drive with "Anyone with the link can view", and put the link in the final
  report and the README.
