
import streamlit as st
import pandas as pd
from datetime import date
from io import StringIO

st.set_page_config(
    page_title="Probation Caseload Risk & Compliance Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("Probation Caseload Risk & Compliance Dashboard")
st.caption(
    "Portfolio demonstration using fictitious records only. "
    "No real client or agency data is included."
)

@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    data["last_contact_date"] = pd.to_datetime(data["last_contact_date"], errors="coerce")
    data["next_court_date"] = pd.to_datetime(data["next_court_date"], errors="coerce")
    return data

def calculate_priority(row, today):
    score = 0
    reasons = []

    days_since_contact = (today - row["last_contact_date"].date()).days
    overdue_days = max(0, days_since_contact - int(row["required_contact_days"]))

    if overdue_days > 0:
        if overdue_days >= 14:
            score += 35
        elif overdue_days >= 7:
            score += 25
        else:
            score += 15
        reasons.append(f"Contact overdue by {overdue_days} day(s)")

    violations = int(row["active_violations"])
    if violations > 0:
        score += min(violations * 20, 40)
        reasons.append(f"{violations} active violation(s)")

    missed = int(row["missed_treatment_appointments"])
    if missed > 0:
        score += min(missed * 15, 30)
        reasons.append(f"{missed} missed treatment appointment(s)")

    court_days = (row["next_court_date"].date() - today).days
    if 0 <= court_days <= 3:
        score += 25
        reasons.append(f"Court in {court_days} day(s)")
    elif 4 <= court_days <= 7:
        score += 15
        reasons.append(f"Court in {court_days} day(s)")
    elif court_days < 0:
        score += 30
        reasons.append(f"Court date passed {-court_days} day(s) ago")

    baseline = {"High": 15, "Moderate": 8, "Low": 0}
    score += baseline.get(str(row["risk_level"]), 0)

    score = min(score, 100)

    if score >= 60:
        status = "RED"
    elif score >= 30:
        status = "YELLOW"
    else:
        status = "GREEN"

    if not reasons:
        reasons.append("No current exception flags")

    return score, status, "; ".join(reasons), overdue_days, court_days

def enrich(data):
    today = date.today()
    result = data.copy()

    calc = result.apply(
        lambda row: calculate_priority(row, today),
        axis=1,
        result_type="expand"
    )
    calc.columns = [
        "priority_score",
        "status",
        "exception_flags",
        "contact_overdue_days",
        "days_to_court"
    ]

    result = pd.concat([result, calc], axis=1)
    return result.sort_values(
        by=["priority_score", "next_court_date"],
        ascending=[False, True]
    )

def build_supervisor_report(data):
    report = data[
        [
            "case_id",
            "client_name",
            "risk_level",
            "status",
            "priority_score",
            "last_contact_date",
            "contact_overdue_days",
            "active_violations",
            "missed_treatment_appointments",
            "next_court_date",
            "days_to_court",
            "exception_flags"
        ]
    ].copy()

    report["last_contact_date"] = report["last_contact_date"].dt.date.astype(str)
    report["next_court_date"] = report["next_court_date"].dt.date.astype(str)
    return report

data = enrich(load_data("sample_caseload.csv"))

with st.sidebar:
    st.header("Filters")

    statuses = st.multiselect(
        "Status",
        options=["RED", "YELLOW", "GREEN"],
        default=["RED", "YELLOW", "GREEN"]
    )

    risk_levels = st.multiselect(
        "Baseline Risk Level",
        options=sorted(data["risk_level"].dropna().unique()),
        default=sorted(data["risk_level"].dropna().unique())
    )

    max_days_to_court = st.slider(
        "Show court dates within",
        min_value=0,
        max_value=90,
        value=90,
        step=5
    )

filtered = data[
    data["status"].isin(statuses)
    & data["risk_level"].isin(risk_levels)
    & (data["days_to_court"] <= max_days_to_court)
].copy()

red_count = (data["status"] == "RED").sum()
yellow_count = (data["status"] == "YELLOW").sum()
green_count = (data["status"] == "GREEN").sum()
overdue_count = (data["contact_overdue_days"] > 0).sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("High Priority", int(red_count))
c2.metric("Needs Attention", int(yellow_count))
c3.metric("On Track", int(green_count))
c4.metric("Overdue Contacts", int(overdue_count))

st.divider()

st.subheader("Caseload Priority Queue")

display_cols = [
    "status",
    "priority_score",
    "case_id",
    "client_name",
    "risk_level",
    "contact_overdue_days",
    "active_violations",
    "missed_treatment_appointments",
    "days_to_court",
    "exception_flags"
]

def color_status(value):
    if value == "RED":
        return "background-color: #ffcccc; color: #7a0000; font-weight: bold;"
    if value == "YELLOW":
        return "background-color: #fff3bf; color: #6b5200; font-weight: bold;"
    if value == "GREEN":
        return "background-color: #d3f9d8; color: #1b5e20; font-weight: bold;"
    return ""

styled = (
    filtered[display_cols]
    .style
    .map(color_status, subset=["status"])
    .format({"priority_score": "{:.0f}"})
)

st.dataframe(
    styled,
    use_container_width=True,
    hide_index=True,
    height=420
)

st.divider()

left, right = st.columns([2, 1])

with left:
    st.subheader("Priority Breakdown")

    selected_case = st.selectbox(
        "Select a case",
        options=filtered["case_id"].tolist()
    ) if len(filtered) else None

    if selected_case:
        case = filtered[filtered["case_id"] == selected_case].iloc[0]

        st.write(f"**Client:** {case['client_name']}")
        st.write(f"**Baseline risk:** {case['risk_level']}")
        st.write(f"**Priority score:** {case['priority_score']}/100")
        st.write(f"**Status:** {case['status']}")
        st.write(f"**Exception flags:** {case['exception_flags']}")

with right:
    st.subheader("Supervisor Export")

    supervisor_report = build_supervisor_report(filtered)
    csv_bytes = supervisor_report.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Supervisor Report (CSV)",
        data=csv_bytes,
        file_name="supervisor_caseload_report.csv",
        mime="text/csv",
        use_container_width=True
    )

    summary_text = f"""Probation Caseload Supervisor Summary

Total Cases: {len(data)}
High Priority (RED): {red_count}
Needs Attention (YELLOW): {yellow_count}
On Track (GREEN): {green_count}
Overdue Contacts: {overdue_count}

This report was generated from fictitious portfolio demonstration data.
"""

    st.download_button(
        label="Download Summary (TXT)",
        data=summary_text,
        file_name="supervisor_summary.txt",
        mime="text/plain",
        use_container_width=True
    )

st.divider()
st.caption(
    "Scoring is intentionally transparent and simplified for portfolio demonstration. "
    "It is not a validated probation risk-assessment instrument and should not be used "
    "for real-world supervision decisions."
)
