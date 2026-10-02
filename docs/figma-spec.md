# Figma prototype specification: 8 key screens

Build time: about 1 hour 45 minutes. Reference screenshots of the running app are in `design-screens/`
(1440 x 900, Chrome). Build each screen to match its screenshot; the spec below gives the exact values so you do not
have to measure.

## 0. Setup (15 minutes)

1. figma.com > **New design file**, name it `ExpenseFlow prototypes`.
2. Drag the 8 PNGs from `docs/design-screens/` onto a page called `Reference`. Lock them (Shift+Ctrl/Cmd+L).
3. Create a page called `Screens`. Every screen is a **Frame** (F) of **1440 x 900** (Desktop preset).
4. **Color styles** (Assets panel > Local styles > +):

   | Style | Hex | Used for |
   | --- | --- | --- |
   | primary | `#1565C0` | Buttons, links, the product name, chart bars |
   | background | `#F6F7FB` | Page background |
   | surface | `#FFFFFF` | Cards, app bar, sidebar |
   | border | `#E3E6EE` | 1 px card and app bar borders |
   | text | `#1F2328` | Headings and body |
   | text-muted | `#5F6670` | Subtitles, labels, captions |
   | status-submitted | `#0288D1` | SUBMITTED chip |
   | status-approved | `#2E7D32` | APPROVED chip, Approve button |
   | status-rejected | `#D32F2F` | REJECTED chip, Reject and Deactivate links |
   | status-reimbursed | `#9C27B0` | REIMBURSED chip, ADMIN role chip |
   | status-draft | `#616161` | DRAFT chip |

5. **Text styles** (font **Inter**, available in Figma):

   | Style | Size / line height | Weight |
   | --- | --- | --- |
   | brand | 20 / 32 | Bold |
   | page-title | 24 / 32 | Semibold |
   | subtitle | 16 / 24 | Regular, text-muted |
   | body | 14 / 20 | Regular |
   | label | 12 / 16 | Regular, text-muted |
   | stat | 24 / 32 | Semibold |
   | button | 14 / 20 | Medium, no uppercase |

6. **Components** (select, Ctrl/Cmd+Alt+K). Corner radius 10 unless stated.
   - `AppBar`: 1440 x 64, surface, bottom border 1 px border. Left at x 24: "ExpenseFlow" (brand, primary). Right at
     x 1360: role chip (pill, 12 px text, grey `#E0E0E0` fill, or status-reimbursed fill with white text for ADMIN)
     and a 32 px grey circle avatar with the first letter.
   - `Sidebar`: 240 x 836 at y 64, surface, right border. Section label "Work" (label, x 16, y 96). Nav items 224 x 36,
     x 8, radius 10, icon 20 px at x 28 + text (body) at x 60; spacing 36. Active item fill `#EBEBEB`.
     Variants: `USER` (Dashboard, My expenses, Import, Reports), `MANAGER` (+ Approvals after Import),
     `ADMIN` (+ section "Administration" with Users, Departments, Projects, Audit log).
   - `Button/primary`: height 36, padding 16, primary fill, white text. `Button/text`: primary text, no fill.
   - `Input`: height 56 (filled forms) or 40 (filters), 1 px `#C4C4C4` border, radius 10, label floating at the top
     border in label style.
   - `Chip/status`: pill, height 24, 1 px border and text in the status color, transparent fill, 13 px text.
     Variants: DRAFT, SUBMITTED, APPROVED, REJECTED, REIMBURSED.
   - `Card`: surface, 1 px border, radius 10, padding 24.
   - `Table row`: height 52, bottom border 1 px border, body text.

## 1. Login (10 minutes)

- **Layout.** Background fill. One `Card` 420 x 412, centred (x 510, y 244).
- **Content, top to bottom** (left 32): "ExpenseFlow" (brand, primary); "Sign in" (page-title, y +48);
  "Submit and approve expenses in one place." (subtitle); `Input` Email (focused: 2 px primary border, label in
  primary); `Input` Password; `Button/primary` "Sign in" full width (356 x 42); a row with "Create account" (left)
  and "Forgot password?" (right), both underlined primary links.
- **States** (duplicate the frame): `error` with a red alert box above the inputs, `#FDEDED` fill, red icon, text
  "Wrong email or password."; `throttled` with the same box and "Too many attempts. Wait a minute and try again."

## 2. Dashboard: employee (15 minutes)

- **Layout.** `AppBar`, `Sidebar/USER` with Dashboard active, content area x 264 to 1416, top y 88.
- **Header.** "Hello, Arta" (page-title); "Your own expenses" (subtitle).
- **KPI row** (y 168): four `Card`s 276 x 122, gap 16. Each: label on top (label 14), value (stat), optional caption
  (label): "Waiting for approval" 2 / "€380.00"; "Spent this month" €0.00 / "approved + reimbursed"; "Drafts" 0;
  "Rejected" 2.
- **Chart card** (x 264, y 306, 762 x 340): title "Approved spend, last 6 months (EUR)" (body 16), a bar chart with
  6 months on the x axis, primary bars, dashed grid lines.
- **Spend by type card** (x 1043, y 306, 373 x 340): title; three rows "EQUIPMENT €460.00", "MEAL €214.00",
  "TRAVEL €396.00" with dividers; caption "Updated 02:23 (cached up to 5 minutes)".
- **Variants** (note only): the manager sees department figures and "Approvals waiting"; the admin sees all.

## 3. Expense list (15 minutes)

- **Header.** "Expenses" + subtitle "Search, filter and open any expense you can see."; on the right
  `Button/text` "Import" and `Button/primary` "+ New expense".
- **Filter card** (y 168, height 74): Search description (432 wide), Status select (150), Type select (140),
  From date (166), To date (166), gap 16, all height 40.
- **Table card** (y 258): columns Date (sorted, arrow down), Type, Description, Project, Employee, Amount (right
  aligned), Status (`Chip/status`). 10 visible rows from the screenshot. Footer: "Rows per page: 20", "1-20 of 20",
  previous/next arrows.
- **States.** `empty`: table body replaced by the grid's centred default text "No rows"; `loading`: a 4 px
  primary progress bar under the table header.
- **Prototype link.** Click a row > Expense detail; click "+ New expense" > Expense form.

## 4. Expense form (15 minutes)

- **Header.** "New expense"; subtitle "Saved as a draft. Submit it from the detail page."
- **Form card** (x 264, y 168, 860 x 348), padding 24, 3-column grid with gap 16:
  row 1: Type select "Meal" (1 column), Project select (2 columns); row 2: Amount (EUR), Date "10/02/2026",
  Attendees "1" with helper "Max 25 EUR per attendee"; row 3: Description, multi-line, full width, height 78.
  Bottom right: `Button/text` "Cancel", `Button/primary` "Save draft".
- **Type variants** (component property on the third field): Travel shows "Distance (km)" and "Destination";
  Equipment shows "Item name" and "Serial number".
- **States.** `policy error`: Attendees field red border, helper text in red "Max 25 EUR per attendee" and the
  Amount field red with "Meals are capped at 25.00 EUR per attendee: max 25.00 EUR."; `saving`: primary button
  disabled with a spinner.
- **Prototype link.** "Save draft" > Expense detail (DRAFT variant).

## 5. Expense detail (10 minutes)

- **Header.** "EQUIPMENT expense #1245"; subtitle "Docking station for hot desk".
- **Card** (y 168, full width, height 330): `Chip/status` SUBMITTED + amount "€190.00" (24 semibold); a 3-column
  grid of label/value pairs: Date "29 Sep 2026", Project "GAMMA", Employee "Arta Krasniqi (Engineering)"; next row
  Item "Docking station (S/N GM-9)"; divider; "Timeline" (body semibold) with "Created 02 Oct 2026, 02:23" and
  "Submitted 02 Oct 2026, 02:23".
- **Action variants** (buttons right of the amount, driven by the API's `_links`): DRAFT shows "Edit",
  "Delete" (red text) and `Button/primary` "Submit"; REJECTED shows a red alert "Rejected: <reason>" above the card and "Reopen";
  a manager on SUBMITTED sees `Approve` (green) and `Reject` (red outline).
- **Modals.** "Delete draft?" confirm dialog (400 wide, Cancel / Delete); "Reject expense" dialog with a required
  multi-line field "Reason (shown to the employee)".

## 6. Approvals: manager (15 minutes)

- **Shell.** `AppBar` with MANAGER chip and avatar "B"; `Sidebar/MANAGER` with Approvals active.
- **Header.** "Approvals"; subtitle "Submitted expenses from your department, oldest first."
- **Search card** (y 168): one full-width input "Search description".
- **Table card** (y 258): columns Date, Employee, Type, Description, Project, Amount, actions. Each row ends with a
  small green filled button "Approve" and a red text button "Reject". 8 rows from the screenshot.
- **States.** `toast success`: bottom-left snackbar, green, "Approved"; `toast error`: red snackbar
  "Project GAMMA budget would be exceeded (budget 3000.00, spent 2850.00, this expense 190.00)." (this is the
  database trigger at work: show it in the defense).

## 7. Report builder: admin (20 minutes)

- **Shell.** `Sidebar/ADMIN` with Reports active; ADMIN chip in purple.
- **Header.** "Reports"; subtitle "Build a report from any criteria, save it, and export it."
- **Criteria card** (x 264, y 168, 762 x 246): row 1 From "07/01/2026", To "10/02/2026", Group by "department";
  row 2 Statuses multi-select with chips "APPROVED" and "REIMBURSED", Types; row 3 Departments, Projects;
  bottom right `Button/text` "Save report" and `Button/primary` "Run report".
- **Result card** (y 432): bar chart (Engineering, Sales, Finance) and a table Group / Count / Total with a bold
  Total row "49 / €7,002.00".
- **Right column** (x 1043, 373 wide): "Saved reports" card listing "Last 90 days by department",
  "department · €6,946.00 · 02 Oct" with a delete icon; "Reimbursement run" card with text "Marks every approved
  expense up to the date as reimbursed (stored procedure).", a date input and `Button/primary` "Reimburse".
- **States.** `save dialog`: "Save report" modal with a name field; `export`: the saved report view with three
  buttons "CSV", "XLSX", "JSON".

## 8. Admin: users (10 minutes)

- **Header.** "Users" with `Button/primary` "New user" (person-plus icon) on the right.
- **Filter card**: Search (full width minus 166) and Role select (150).
- **Table card**: columns Email, Name, Role, Department, Status (green outlined "Active" chip), Joined, then
  "Edit" (primary text) and "Deactivate" (red text). 9 rows from the screenshot; footer "Rows per page: 20",
  "1-9 of 9".
- **Modal.** "New user" dialog: Email, First name, Last name, Role select, Department select, Cancel / Create.

## 9. Prototype wiring (10 minutes)

Switch to the **Prototype** tab and connect: Login "Sign in" > Dashboard; Sidebar items > their screens; Expense
list row > Expense detail; "+ New expense" > Expense form; "Save draft" > Expense detail; Approvals "Approve" >
the success toast frame (Smart animate, 200 ms). Set Login as the flow's starting point and press Present to check.

Export: select all frames on `Screens` > Export > PNG 1x into `docs/figma/` and add the Figma link (View only,
"Anyone with the link") to the Phase II document.
