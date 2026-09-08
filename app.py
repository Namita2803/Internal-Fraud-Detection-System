# app.py
import streamlit as st
import pandas as pd

from utils.theme import (
    inject_global_theme, render_sidebar_brand, render_engine_status,
    kpi_card, section_label, page_header,
)
from utils.charts import alerts_by_domain_bar
from utils.data_loader import (
    load_employees, load_payroll, load_procurement, load_insider,
    load_reimbursement, get_backend,
)

st.set_page_config(
    page_title="Internal Fraud Detection | Overview",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_theme()
render_sidebar_brand()

backend = get_backend()
render_engine_status(backend["status"])

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.caption(
    "Navigate using the pages panel above to access Risk Breakdown, "
    "the Predictive Inference Engine, and Employee Lookup."
)
if backend["status"] != "operational":
    st.sidebar.warning(
        "Model artifacts could not be loaded from /models. "
        "Population scoring and inference pages will run in a limited "
        "capacity until artifacts are available."
    )

employees = load_employees()
payroll = load_payroll()
procurement = load_procurement()
insider = load_insider()
reimbursement = load_reimbursement()

page_header(
    "Internal Fraud Detection Overview",
    "Consolidated visibility across payroll, procurement, reimbursement, and insider-threat surfaces.",
)

total_employees = len(employees)
proc_alerts = int(procurement["fraud_flag"].sum())
pay_alerts = int(payroll["fraud_flag"].sum())
reimb_alerts = int(reimbursement["Fraud_Label"].sum())
insider_alerts = int(insider["is_malicious"].sum())
total_financial_alerts = proc_alerts + pay_alerts + reimb_alerts
model_coverage = "4 / 4" if backend["status"] == "operational" else "Limited"

col1, col2, col3, col4 = st.columns(4)
with col1:
    kpi_card("Employees Monitored", f"{total_employees:,}", "Active workforce records")
with col2:
    kpi_card("System Health", model_coverage, "Fraud detection modules online")
with col3:
    kpi_card("Financial Alerts", f"{total_financial_alerts:,}", "Payroll · Procurement · Reimbursement")
with col4:
    kpi_card("Insider Threat Signals", f"{insider_alerts:,}", "Flagged behavioral log entries")

st.markdown("<br>", unsafe_allow_html=True)

col_chart, col_table = st.columns([1, 1.3])

with col_chart:
    section_label("Alert Volume by Domain")
    fig = alerts_by_domain_bar(
        ["Payroll", "Procurement", "Reimbursement", "Insider"],
        [pay_alerts, proc_alerts, reimb_alerts, insider_alerts],
    )
    st.plotly_chart(fig, use_container_width=True)

with col_table:
    section_label("High Priority Alerts")

    proc_a = procurement[procurement["fraud_flag"] == 1][["employee_id", "price_difference"]].rename(
        columns={"price_difference": "metric"}
    )
    proc_a["domain"] = "Procurement"

    pay_a = payroll[payroll["fraud_flag"] == 1][["employee_id", "salary_difference"]].rename(
        columns={"salary_difference": "metric"}
    )
    pay_a["domain"] = "Payroll"

    reimb_a = reimbursement[reimbursement["Fraud_Label"] == 1][["Employee_ID", "Claim_Amount"]].rename(
        columns={"Employee_ID": "employee_id", "Claim_Amount": "metric"}
    )
    reimb_a["domain"] = "Reimbursement"

    alerts = pd.concat([proc_a, pay_a, reimb_a], ignore_index=True)
    alerts = alerts.merge(
        employees[["employee_id", "employee_name", "department"]], on="employee_id", how="left"
    )
    alerts["employee_name"] = alerts["employee_name"].fillna("Unrecorded")
    alerts["department"] = alerts["department"].fillna("Unrecorded")
    alerts = alerts.sort_values("metric", ascending=False).head(10)
    alerts = alerts[["employee_id", "employee_name", "department", "domain", "metric"]]
    alerts.columns = ["Employee ID", "Employee", "Department", "Domain", "Flagged Amount"]

    st.dataframe(
        alerts.style.background_gradient(subset=["Flagged Amount"], cmap="Blues"),
        use_container_width=True,
        hide_index=True,
        height=340,
    )

st.markdown("<br>", unsafe_allow_html=True)
section_label("Platform Modules")

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(
        """
        <div class="info-card">
        <b>Risk Breakdown</b><br>
        <span style="color:#64748B; font-size:0.88rem;">
        Composite risk scoring across the employee population, powered by
        risk_engine.py and the four trained fraud models.
        </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m2:
    st.markdown(
        """
        <div class="info-card">
        <b>Predictive Inference Engine</b><br>
        <span style="color:#64748B; font-size:0.88rem;">
        Real-time, single-record scoring against each domain model with
        probability thresholds and feature importance.
        </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m3:
    st.markdown(
        """
        <div class="info-card">
        <b>Employee Lookup</b><br>
        <span style="color:#64748B; font-size:0.88rem;">
        Full composite risk report for a single employee ID, orchestrated
        end-to-end through main.py.
        </span>
        </div>
        """,
        unsafe_allow_html=True,
    )