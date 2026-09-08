# pages/1_Risk_Breakdown.py
import streamlit as st
import pandas as pd

from utils.theme import inject_global_theme, render_sidebar_brand, render_engine_status
from utils.theme import section_label, page_header, kpi_card, risk_pill
from utils.charts import score_distribution_histogram, department_heatmap
from utils.data_loader import (
    load_employees, load_payroll, load_procurement, load_reimbursement,
    get_backend, compute_population_risk,
)

st.set_page_config(page_title="Internal Fraud Detection | Risk Breakdown", layout="wide")
inject_global_theme()
render_sidebar_brand()

backend = get_backend()
render_engine_status(backend["status"])

employees = load_employees()

page_header(
    "Population Risk Breakdown",
    "Composite fraud risk scores generated per employee via risk_engine.py's weighted model.",
)

if backend["status"] != "operational":
    st.warning(
        f"Model artifacts are unavailable ({backend['error']}). "
        "Showing raw dataset-level alert rates instead of live model scores."
    )
    payroll = load_payroll()
    procurement = load_procurement()
    reimbursement = load_reimbursement()

    dept_stats = employees.merge(
        payroll[["employee_id", "fraud_flag"]], on="employee_id", how="left"
    )
    dept_summary = dept_stats.groupby("department")["fraud_flag"].mean().reset_index()
    dept_summary.columns = ["Department", "Payroll Flag Rate"]

    section_label("Payroll Flag Rate by Department")
    st.dataframe(
        dept_summary.style.background_gradient(subset=["Payroll Flag Rate"], cmap="Blues"),
        use_container_width=True,
        hide_index=True,
    )
    st.stop()

employee_ids = tuple(sorted(employees["employee_id"].tolist()))
risk_df = compute_population_risk(employee_ids)

if risk_df.empty:
    st.error("Population scoring returned no results. Verify dataset and model compatibility.")
    st.stop()

risk_df = risk_df.merge(employees[["employee_id", "department"]], on="employee_id", how="left")
risk_df["department"] = risk_df["department"].fillna("Unrecorded")

avg_score = round(risk_df["overall_score"].mean(), 2)
high_count = int((risk_df["risk_level"] == "High").sum())
medium_count = int((risk_df["risk_level"] == "Medium").sum())
low_count = int((risk_df["risk_level"] == "Low").sum())

c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Average Composite Score", f"{avg_score}", "Out of 100")
with c2:
    kpi_card("High Risk Employees", f"{high_count}", "Requires review")
with c3:
    kpi_card("Medium Risk Employees", f"{medium_count}", "Monitor closely")
with c4:
    kpi_card("Low Risk Employees", f"{low_count}", "Nominal standing")

st.markdown("<br>", unsafe_allow_html=True)
col_a, col_b = st.columns([1.2, 1])

with col_a:
    section_label("Composite Score Distribution")
    st.plotly_chart(score_distribution_histogram(risk_df["overall_score"]), use_container_width=True)

with col_b:
    section_label("Average Risk by Department")
    pivot = risk_df.groupby("department")[["overall_score"]].mean().round(1)
    pivot.columns = ["Avg Score"]
    st.plotly_chart(department_heatmap(pivot), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
section_label("Employee Risk Register")

filter_col1, filter_col2 = st.columns([1, 2])
with filter_col1:
    level_filter = st.multiselect(
        "Risk Level", options=["Low", "Medium", "High"], default=["Low", "Medium", "High"]
    )
with filter_col2:
    search_term = st.text_input("Search by Employee ID or Name", "")

filtered = risk_df[risk_df["risk_level"].isin(level_filter)]
if search_term:
    mask = (
        filtered["employee_id"].str.contains(search_term, case=False, na=False)
        | filtered["employee_name"].str.contains(search_term, case=False, na=False)
    )
    filtered = filtered[mask]

filtered = filtered.sort_values("overall_score", ascending=False)

display_df = filtered[
    ["employee_id", "employee_name", "department", "overall_score", "risk_level", "reasons"]
].copy()
display_df.columns = ["Employee ID", "Name", "Department", "Score", "Risk Level", "Flags"]

st.dataframe(
    display_df.style.background_gradient(subset=["Score"], cmap="Blues"),
    use_container_width=True,
    hide_index=True,
    height=420,
)

st.download_button(
    "Export Risk Register (CSV)",
    data=display_df.to_csv(index=False).encode("utf-8"),
    file_name="employee_risk_register.csv",
    mime="text/csv",
)