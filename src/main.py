from predictor import predict_all
from risk_engine import generate_report

# --------------------------------------------------
# Sample Insider Data
# --------------------------------------------------

insider_data = {
    "employee_department": 0,
    "employee_campus": 0,
    "employee_position": 0,
    "employee_seniority_years": 5,
    "is_contractor": 0,
    "employee_classification": 0,
    "has_foreign_citizenship": 0,
    "has_criminal_record": 0,
    "has_medical_history": 0,
    "employee_origin_country": 0,
    "total_printed_pages": 20,
    "num_printed_pages_off_hours": 2,
    "total_files_burned": 0,
    "burned_from_other": 0,
    "is_abroad": 0,
    "trip_day_number": 0,
    "hostility_country_level": 0,
    "num_entries": 5,
    "num_unique_campus": 1,
    "late_exit_flag": 0,
    "entry_during_weekend": 0
}

# --------------------------------------------------
# Sample Procurement Data
# --------------------------------------------------

procurement_data = {
    "price_system": 10000,
    "price_actual": 9800,
    "price_difference": 200,
    "account_mismatch_flag": 0
}

# --------------------------------------------------
# Sample Reimbursement Data
# --------------------------------------------------

reimbursement_data = {
    "Department": 0,
    "Expense_Type": 0,
    "Claim_Amount": 5000,
    "Approval_Status": 1,
    "Designation": 1,
    "Employee_Tenure_Months": 24,
    "Receipt_Available": 1,
    "Duplicate_Claim": 0,
    "Previous_Claims_Count": 2,
    "Approval_Time_Days": 3,
    "Weekend_Claim": 0,
    "Policy_Violation_Count": 0,
    "Payment_Method": 0
}

# --------------------------------------------------
# Sample Payroll Data
# --------------------------------------------------

payroll_data = {
    "department": 0,
    "position": 0,
    "salary_system": 50000,
    "salary_received": 50000,
    "salary_difference": 0
}

# --------------------------------------------------
# Run All Models
# --------------------------------------------------

results = predict_all(
    insider_data,
    procurement_data,
    reimbursement_data,
    payroll_data
)

print(results)

# --------------------------------------------------
# Generate Final Report
# --------------------------------------------------

generate_report(
    results["insider"],
    results["procurement"],
    results["reimbursement"],
    results["payroll"]
)