# pages/2_Predictive_Engine.py
import streamlit as st

from utils.theme import inject_global_theme, render_sidebar_brand, render_engine_status
from utils.theme import section_label, page_header, risk_pill
from utils.charts import probability_gauge, feature_importance_bar
from utils.data_loader import load_insider, get_backend, get_feature_importance

st.set_page_config(page_title="Internal Fraud Detection | Predictive Engine", layout="wide")
inject_global_theme()
render_sidebar_brand()

backend = get_backend()
render_engine_status(backend["status"])

page_header(
    "Predictive Inference Engine",
    "Real-time single-record scoring against each trained fraud detection model.",
)

if backend["status"] != "operational":
    st.error(
        f"Prediction models could not be loaded ({backend['error']}). "
        "Confirm the /models directory contains all required .pkl artifacts."
    )
    st.stop()

predictor = backend["predictor"]
risk_engine = backend["risk_engine"]

tab_insider, tab_procurement, tab_reimbursement, tab_payroll = st.tabs(
    ["Insider Threat", "Procurement", "Reimbursement", "Payroll"]
)


def render_result(probability, model_key, feature_row):
    level = risk_engine.get_risk_level(probability * 100)
    col_gauge, col_meta = st.columns([1, 1])
    with col_gauge:
        st.plotly_chart(probability_gauge(probability, f"{model_key.title()} Fraud Probability"), use_container_width=True)
    with col_meta:
        st.markdown(f"**Risk Classification:** {risk_pill(level)}", unsafe_allow_html=True)
        st.metric("Raw Probability", f"{probability:.4f}")
        st.metric("Scaled Score", f"{round(probability * 100, 2)} / 100")

    model = predictor.models.get(model_key)
    importances = get_feature_importance(model, list(feature_row.keys())) if model else None
    section_label("Feature Importance")
    if importances:
        st.plotly_chart(feature_importance_bar(importances, f"{model_key.title()} Model — Feature Weights"), use_container_width=True)
    else:
        st.info("Feature importance is not available for this model configuration.")


with tab_insider:
    section_label("Employee Profile & Behavioral Signals")
    insider_df = load_insider()

    with st.form("insider_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            employee_department = st.selectbox("Department", sorted(insider_df["employee_department"].dropna().unique()))
            employee_campus = st.selectbox("Campus", sorted(insider_df["employee_campus"].dropna().unique()))
            employee_position = st.selectbox("Position", sorted(insider_df["employee_position"].dropna().unique()))
            employee_seniority_years = st.number_input("Seniority (Years)", min_value=0, max_value=45, value=5)
            employee_classification = st.selectbox("Employee Classification", sorted(insider_df["employee_classification"].dropna().unique()))
            employee_origin_country = st.selectbox("Origin Country", sorted(insider_df["employee_origin_country"].dropna().unique()))
        with c2:
            total_printed_pages = st.number_input("Total Printed Pages", min_value=0, value=0)
            num_printed_pages_off_hours = st.number_input("Printed Pages (Off Hours)", min_value=0, value=0)
            total_files_burned = st.number_input("Total Files Burned", min_value=0, value=0)
            burned_from_other = st.selectbox("Burned From Other Device", [0, 1])
            trip_day_number = st.number_input("Trip Day Number", min_value=0, max_value=30, value=0)
            hostility_country_level = st.selectbox("Hostility Country Level", [0, 1, 2, 3])
        with c3:
            num_entries = st.number_input("Number of Building Entries", min_value=0, value=1)
            num_unique_campus = st.number_input("Unique Campuses Visited", min_value=0, max_value=5, value=1)
            is_contractor = st.selectbox("Is Contractor", [0, 1])
            has_foreign_citizenship = st.selectbox("Foreign Citizenship", [0, 1])
            has_criminal_record = st.selectbox("Criminal Record on File", [0, 1])
            has_medical_history = st.selectbox("Medical History on File", [0, 1])

        c4, c5 = st.columns(2)
        with c4:
            is_abroad = st.selectbox("Currently Abroad", [0, 1])
            late_exit_flag = st.selectbox("Late Exit Flag", [0, 1])
        with c5:
            entry_during_weekend = st.selectbox("Weekend Entry Flag", [0, 1])

        submitted = st.form_submit_button("Run Insider Threat Inference")

    if submitted:
        payload = {
            "employee_department": employee_department,
            "employee_campus": employee_campus,
            "employee_position": employee_position,
            "employee_seniority_years": employee_seniority_years,
            "is_contractor": is_contractor,
            "employee_classification": employee_classification,
            "has_foreign_citizenship": has_foreign_citizenship,
            "has_criminal_record": has_criminal_record,
            "has_medical_history": has_medical_history,
            "employee_origin_country": employee_origin_country,
            "total_printed_pages": total_printed_pages,
            "num_printed_pages_off_hours": num_printed_pages_off_hours,
            "total_files_burned": total_files_burned,
            "burned_from_other": burned_from_other,
            "is_abroad": is_abroad,
            "trip_day_number": trip_day_number,
            "hostility_country_level": hostility_country_level,
            "num_entries": num_entries,
            "num_unique_campus": num_unique_campus,
            "late_exit_flag": late_exit_flag,
            "entry_during_weekend": entry_during_weekend,
        }
        try:
            probability = predictor.predict_insider(payload)
            render_result(probability, "insider", payload)
        except Exception as exc:
            st.error(f"Insider inference failed: {exc}")


with tab_procurement:
    section_label("Purchase Order Details")

    with st.form("procurement_form"):
        c1, c2 = st.columns(2)
        with c1:
            price_system = st.number_input("System Price", min_value=0, value=1000000, step=1000)
            price_actual = st.number_input("Actual Invoiced Price", min_value=0, value=1000000, step=1000)
        with c2:
            account_mismatch_flag = st.selectbox("Account Mismatch Flag", [0, 1])
            st.caption("Price difference is derived automatically as System Price − Actual Price.")
        submitted = st.form_submit_button("Run Procurement Inference")

    if submitted:
        payload = {
            "price_system": price_system,
            "price_actual": price_actual,
            "price_difference": price_system - price_actual,
            "account_mismatch_flag": account_mismatch_flag,
        }
        try:
            probability = predictor.predict_procurement(payload)
            render_result(probability, "procurement", payload)
        except Exception as exc:
            st.error(f"Procurement inference failed: {exc}")


with tab_reimbursement:
    section_label("Expense Claim Details")

    with st.form("reimbursement_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            Department = st.selectbox("Department", ["HR", "Operations", "IT", "Sales", "Finance"])
            Expense_Type = st.selectbox("Expense Type", ["Fuel", "Hotel", "Travel", "Training", "Internet", "Meal", "Office Supplies"])
            Claim_Amount = st.number_input("Claim Amount", min_value=0, value=50000, step=1000)
        with c2:
            Approval_Status = st.selectbox("Approval Status", ["Approved", "Pending", "Rejected"])
            Designation = st.selectbox("Designation", ["Associate", "Senior Associate", "Intern", "Director", "Manager"])
            Employee_Tenure_Months = st.number_input("Employee Tenure (Months)", min_value=0, value=24)
        with c3:
            Payment_Method = st.selectbox("Payment Method", ["Bank Transfer", "Corporate Card", "Cash"])
            Previous_Claims_Count = st.number_input("Previous Claims Count", min_value=0, value=2)
            Approval_Time_Days = st.number_input("Approval Time (Days)", min_value=0, value=2)

        c4, c5, c6 = st.columns(3)
        with c4:
            Receipt_Available = st.selectbox("Receipt Available", [1, 0])
        with c5:
            Duplicate_Claim = st.selectbox("Duplicate Claim Flag", [0, 1])
        with c6:
            Weekend_Claim = st.selectbox("Weekend Claim Flag", [0, 1])

        Policy_Violation_Count = st.number_input("Policy Violation Count", min_value=0, value=0)
        submitted = st.form_submit_button("Run Reimbursement Inference")

    if submitted:
        payload = {
            "Department": Department,
            "Expense_Type": Expense_Type,
            "Claim_Amount": Claim_Amount,
            "Approval_Status": Approval_Status,
            "Designation": Designation,
            "Employee_Tenure_Months": Employee_Tenure_Months,
            "Receipt_Available": Receipt_Available,
            "Duplicate_Claim": Duplicate_Claim,
            "Previous_Claims_Count": Previous_Claims_Count,
            "Approval_Time_Days": Approval_Time_Days,
            "Weekend_Claim": Weekend_Claim,
            "Policy_Violation_Count": Policy_Violation_Count,
            "Payment_Method": Payment_Method,
        }
        try:
            probability = predictor.predict_reimbursement(payload)
            render_result(probability, "reimbursement", payload)
        except Exception as exc:
            st.error(f"Reimbursement inference failed: {exc}")


with tab_payroll:
    section_label("Compensation Record")

    try:
        department_options = predictor.get_payroll_departments()
        position_options = predictor.get_payroll_positions()
    except Exception:
        department_options, position_options = [], []

    with st.form("payroll_form"):
        c1, c2 = st.columns(2)
        with c1:
            department = st.selectbox("Department", department_options)
            salary_system = st.number_input("System Salary", min_value=0, value=4500000, step=10000)
        with c2:
            position = st.selectbox("Position", position_options)
            salary_received = st.number_input("Salary Received", min_value=0, value=4500000, step=10000)
        submitted = st.form_submit_button("Run Payroll Inference")

    if submitted:
        payload = {
            "department": department,
            "position": position,
            "salary_system": salary_system,
            "salary_received": salary_received,
            "salary_difference": salary_system - salary_received,
        }
        try:
            probability = predictor.predict_payroll(payload)
            render_result(probability, "payroll", payload)
        except Exception as exc:
            st.error(f"Payroll inference failed: {exc}")