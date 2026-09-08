# pages/3_Employee_Lookup.py
import streamlit as st

from utils.theme import inject_global_theme, render_sidebar_brand, render_engine_status
from utils.theme import section_label, page_header, risk_pill, kpi_card
from utils.charts import composite_score_gauge, domain_probability_bar
from utils.data_loader import (
    load_employees, load_payroll, load_procurement, load_reimbursement, get_backend,
)

st.set_page_config(page_title="Internal Fraud Detection | Employee Lookup", layout="wide")
inject_global_theme()
render_sidebar_brand()

backend = get_backend()
render_engine_status(backend["status"])

page_header(
    "Employee Risk Report",
    "End-to-end composite risk scoring for a single employee, orchestrated through main.py.",
)

if backend["status"] != "operational":
    st.error(
        f"The orchestration engine could not be initialized ({backend['error']}). "
        "Employee-level lookups require all four trained models to be present in /models."
    )
    st.stop()

employees = load_employees()
payroll = load_payroll()
procurement = load_procurement()
reimbursement = load_reimbursement()

employees_sorted = employees.sort_values("employee_id")
label_map = {
    row["employee_id"]: f"{row['employee_id']} — {row['employee_name']}"
    for _, row in employees_sorted.iterrows()
}

col_select, col_button = st.columns([3, 1])
with col_select:
    selected_id = st.selectbox(
        "Select Employee",
        options=list(label_map.keys()),
        format_func=lambda x: label_map[x],
    )
with col_button:
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("Generate Risk Report", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

profile_row = employees[employees["employee_id"] == selected_id]
profile = profile_row.iloc[0] if not profile_row.empty else None

section_label("Data Snapshot")
snap1, snap2, snap3, snap4 = st.columns(4)

pay_row = payroll[payroll["employee_id"] == selected_id]
proc_rows = procurement[procurement["employee_id"] == selected_id]
reimb_rows = reimbursement[reimbursement["Employee_ID"] == selected_id]

pay_flag = int(pay_row["fraud_flag"].iloc[0]) if not pay_row.empty else 0
proc_flag_count = int(proc_rows["fraud_flag"].sum()) if not proc_rows.empty else 0
reimb_flag_count = int(reimb_rows["Fraud_Label"].sum()) if not reimb_rows.empty else 0
salary_gap = int(pay_row["salary_difference"].iloc[0]) if not pay_row.empty else 0

with snap1:
    kpi_card("Payroll Flag", "Yes" if pay_flag else "No", light=True)
with snap2:
    kpi_card("Salary Gap", f"{salary_gap:,}", light=True)
with snap3:
    kpi_card("Procurement Flags", f"{proc_flag_count}", "Flagged purchase orders", light=True)
with snap4:
    kpi_card("Reimbursement Flags", f"{reimb_flag_count}", "Flagged expense claims", light=True)

st.markdown("<br>", unsafe_allow_html=True)

if not run:
    st.markdown(
        """
        <div class="info-card" style="text-align:center; padding:40px 24px;">
            <div style="font-size:1rem; font-weight:700; color:#0B1120; margin-bottom:6px;">
                No Composite Report Generated Yet
            </div>
            <div style="font-size:0.9rem; color:#64748B;">
                Select an employee above and choose <b>Generate Risk Report</b> to run the
                insider threat, procurement, reimbursement, and payroll models via main.py
                and produce a unified composite risk score.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

try:
    report, probabilities = backend["main"].analyze_single_employee(selected_id)
except Exception as exc:
    st.error(f"Report generation failed for {selected_id}: {exc}")
    st.stop()

if report is None:
    st.warning(f"No record found for employee ID {selected_id}.")
    st.stop()

section_label("Employee Profile")
p1, p2, p3, p4 = st.columns(4)
p1.metric("Employee", profile["employee_name"] if profile is not None else "Unrecorded")
p2.metric("Department", profile["department"] if profile is not None else "Unrecorded")
p3.metric("Position", profile["position"] if profile is not None else "Unrecorded")
p4.metric("Tenure (Years)", profile["tenure_years"] if profile is not None else "N/A")

st.markdown("<br>", unsafe_allow_html=True)
col_gauge, col_bar = st.columns([1, 1.2])

with col_gauge:
    section_label("Composite Risk")
    st.plotly_chart(
        composite_score_gauge(report["overall_score"], report["risk_level"]),
        use_container_width=True,
    )
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;">
            <strong>Risk Level:</strong>
            {risk_pill(report["risk_level"])}
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_bar:
    section_label("Model-Level Probabilities")
    st.plotly_chart(
        domain_probability_bar(
            ["Insider Threat", "Procurement", "Reimbursement", "Payroll"],
            [
                probabilities["insider"],
                probabilities["procurement"],
                probabilities["reimbursement"],
                probabilities["payroll"],
            ],
        ),
        use_container_width=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
section_label("System-Generated Flags")
for reason in report["reasons"]:
    st.markdown(f"— {reason}")

st.markdown("<br>", unsafe_allow_html=True)
section_label("Supporting Records")

tab_pay, tab_proc, tab_reimb = st.tabs(["Payroll", "Procurement", "Reimbursement"])

with tab_pay:
    if not pay_row.empty:
        st.dataframe(pay_row, use_container_width=True, hide_index=True)
    else:
        st.info("No payroll record found for this employee.")

with tab_proc:
    if not proc_rows.empty:
        st.dataframe(proc_rows, use_container_width=True, hide_index=True)
    else:
        st.info("No procurement records found for this employee.")

with tab_reimb:
    if not reimb_rows.empty:
        st.dataframe(reimb_rows, use_container_width=True, hide_index=True)
    else:
        st.info("No reimbursement claims found for this employee.")

with st.expander("Raw Probability Payload"):
    st.json(probabilities)