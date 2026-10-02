# Stakeholder questionnaire

Goal: confirm the problem and the requirements with people who claim or approve work expenses. Target: 15 to 20
responses (at least 10). Results feed SRS section 2 and the Phase I defense.

## 1. Build it in Google Forms (about 20 minutes)

1. Go to forms.google.com, sign in, click **Blank form**.
2. Title: `ExpenseFlow: how do you claim work expenses?`
   Description: `A 3-minute survey for a university project (UBT Lab Course 2). Anonymous. Your answers shape a web app for submitting and approving work expenses.`
3. Settings (gear icon or the **Settings** tab):
   - Responses: **Collect email addresses** = Do not collect (keeps it anonymous).
   - Responses: **Limit to 1 response** = off (it would force a Google login).
   - Presentation: **Show progress bar** = on.
4. Add the questions in section 2 exactly as listed: type, options, and the **Required** toggle.
5. Before question 7, click **Add section** (the icon with two bars) and name it `For approvers and finance`,
   description `Optional. Skip if you don't approve expenses.` Everyone sees it; questions 7 and 8 are not
   required, so employees simply click Next.
6. Click **Preview** (eye icon) and answer it once yourself; then delete that test response under
   **Responses > three-dot menu > Delete all responses**.
7. Click **Send**, choose the link icon, tick **Shorten URL**, copy it. Share it in WhatsApp or Viber groups,
   with internship colleagues and with relatives who work in companies. Ask them to forward it.
8. When responses arrive, open **Responses > Link to Sheets** to get a spreadsheet. Keep the form open until you
   have 15 or more responses or 7 days have passed.
9. Take two screenshots for the Phase I document: the form editor, and the **Responses > Summary** charts.
10. Copy the summary (counts per option and the open answers) into section 3 below; the results are written
    from them.

## 2. Questions

| # | Question | Type | Options | Required |
| --- | --- | --- | --- | --- |
| 1 | What is your role at work? | Multiple choice | Employee; Team lead or manager; Finance or accounting; Other | Yes |
| 2 | How often do you pay for work expenses yourself (travel, meals, equipment)? | Multiple choice | Never; A few times a year; Monthly; Weekly or more | Yes |
| 3 | How do you claim them today? | Checkboxes | Email with photos of receipts; Excel or a shared sheet; Paper form; A dedicated tool; Other | Yes |
| 4 | How long does it usually take until you are paid back? | Multiple choice | Under a week; 1 to 2 weeks; 2 to 4 weeks; More than a month; I don't know | Yes |
| 5 | What is the most frustrating part of the process? | Paragraph | (free text) | No |
| 6 | Have you ever lost a claim or forgotten to submit one? | Multiple choice | Yes; No; Not sure | Yes |
| 7 | If you approve expenses: what do you need to decide quickly? | Checkboxes | The receipt amount; Whether it follows company policy; Remaining project budget; The employee's history; Other | No |
| 8 | Which reports would finance need most? | Checkboxes | By project; By department; By month; By expense type; By employee; Other | No |
| 9 | Would you import expenses from a card or bank statement file (CSV)? | Multiple choice | Yes; No; Maybe | Yes |
| 10 | Which device would you use to submit expenses? | Multiple choice | Computer; Phone; Both | Yes |

Each question maps to requirements, so every answer either confirms or challenges one:

| Question | Checks |
| --- | --- |
| 1, 2 | Stakeholder mix and how often the problem occurs |
| 3, 4, 5, 6 | The problem itself: lost claims, slow reimbursement (FR-04, FR-06, FR-08, FR-14) |
| 7 | Approver needs: policy and budget checks (FR-05, FR-07) |
| 8 | Report grouping options (FR-11, FR-12) |
| 9 | Import (FR-10, extra feature 10) |
| 10 | Responsive design (NFR-08) |

## 3. Results

Status: **waiting for responses.** This section is written from the Google Forms summary once at least 10
responses are in: number of responses and role mix, a table of answer counts per question, the three most common
frustrations quoted from question 5, and for each finding the requirement it confirms or changes.
