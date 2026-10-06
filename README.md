# Probation Caseload Risk & Compliance Dashboard

A portfolio project demonstrating how a repetitive probation workflow can be turned into a simple operational dashboard using Python, pandas, and Streamlit.

**Important:** All included records are fictitious. This project contains no real client, court, agency, or protected information.

## What it does

The dashboard:

1. Reads structured caseload data from CSV.
2. Calculates a transparent priority score based on:
   - overdue required contacts,
   - active violations,
   - missed treatment appointments,
   - upcoming or overdue court dates,
   - baseline supervision risk level.
3. Assigns each case a RED / YELLOW / GREEN status.
4. Creates a sortable, filterable priority queue.
5. Shows the reason each case received its score.
6. Exports a supervisor-ready CSV report.
7. Generates a simple caseload summary.

## Why this project exists

Probation work involves a large amount of deadline tracking, documentation, exception handling, risk prioritization, and supervisory reporting.

This project demonstrates how those operational requirements can be translated into a lightweight information system rather than relying entirely on manual spreadsheets and individual reminders.

## Technologies

- Python
- pandas
- Streamlit
- CSV data processing
- Business-rule automation
- Data validation
- Operational reporting

## Run it

### Windows

Install Python 3 first.

Then double-click:

`run_dashboard.bat`

Or from PowerShell / Command Prompt:

```powershell
pip install -r requirements.txt
streamlit run app.py
```

The dashboard will open in your browser.

## Priority logic

The scoring model is deliberately simple and explainable.

### Overdue contact

- 1–6 days overdue: +15
- 7–13 days overdue: +25
- 14+ days overdue: +35

### Active violations

- +20 per active violation
- Maximum +40

### Missed treatment appointments

- +15 per missed appointment
- Maximum +30

### Court date

- Court in 0–3 days: +25
- Court in 4–7 days: +15
- Court date already passed: +30

### Baseline risk level

- High: +15
- Moderate: +8
- Low: +0

### Status

- RED: score 60–100
- YELLOW: score 30–59
- GREEN: score 0–29

## Portfolio talking point

> Built a probation caseload risk and compliance dashboard that automated deadline tracking, priority scoring, exception flagging, and supervisory reporting using structured case data.

## Skills demonstrated

- Python scripting
- Data transformation
- Workflow automation
- Operational risk logic
- Exception handling
- Dashboard design
- Reporting automation
- User-focused interface design
- Translating business requirements into technical solutions

## Ethical / operational note

This application is a portfolio demonstration only.

The scoring model is not a validated risk-assessment instrument and must not be used to make actual supervision, detention, sentencing, treatment, or liberty decisions.
