import json
import os
#from predictor import predict_all
#
#from risk_engine import generate_report_data

from  .predictor import predict_all
from  .risk_engine import generate_report_data

def analyze_single_employee(target_emp_id):
    """
    Finds an employee in the JSON database, filters all department lists 
    by their ID, maps them to dictionaries, and generates a risk report.
    """

    # 1. Dynamically locate and load the JSON database file
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    JSON_PATH = os.path.join(BASE_DIR, "datasets", "fraud_system_full.json")
    
    if not os.path.exists(JSON_PATH):
        # Fallback if your folder layout is flat or execution directory varies
        JSON_PATH = os.path.join(os.path.dirname(__file__), "fraud_system_full.json")
        
    with open(JSON_PATH, "r") as file:
        database = json.load(file)
        
    # 2. Extract the Employee Master Profile
    employee_profile = None
    for emp in database.get("employees", []):
        if emp["employee_id"] == target_emp_id:
            employee_profile = emp
            break
            
    if not employee_profile:
        print(f"❌ Employee ID {target_emp_id} not found in the database.")
        return None

    # 3. Scan the JSON lists using corrected keys to match the database structure
    insider_rec = next((item for item in database.get("insider_threat", []) if item.get("employee_id") == target_emp_id), {})
    procure_rec = next((item for item in database.get("procurement", []) if item.get("employee_id") == target_emp_id), {})
    reimburse_rec = next((item for item in database.get("reimbursement", []) if item.get("employee_id") == target_emp_id), {})
    payroll_rec = next((item for item in database.get("payroll", []) if item.get("employee_id") == target_emp_id), {})

    
    # 4. Map the raw JSON rows into the 4 schemas required by predictor.py
    insider_data = {
        "employee_department": insider_rec.get("employee_department", 0),
        "employee_campus": insider_rec.get("employee_campus", 0),
        "employee_position": insider_rec.get("employee_position", 0),
        "employee_seniority_years": int(float(employee_profile.get("tenure_years", 0))),
        "is_contractor": insider_rec.get("is_contractor", 0),
        "employee_classification": insider_rec.get("employee_classification", 0),
        "has_foreign_citizenship": insider_rec.get("has_foreign_citizenship", 0),
        "has_criminal_record": insider_rec.get("has_criminal_record", 0),
        "has_medical_history": insider_rec.get("has_medical_history", 0),
        "employee_origin_country": insider_rec.get("employee_origin_country", 0),
        "total_printed_pages": insider_rec.get("total_printed_pages", 0),
        "num_printed_pages_off_hours": insider_rec.get("num_printed_pages_off_hours", 0),
        "total_files_burned": insider_rec.get("total_files_burned", 0),
        "burned_from_other": insider_rec.get("burned_from_other", 0),
        "is_abroad": insider_rec.get("is_abroad", 0),
        "trip_day_number": insider_rec.get("trip_day_number", 0),
        "hostility_country_level": insider_rec.get("hostility_country_level", 0),
        "num_entries": insider_rec.get("num_entries", 0),
        "num_unique_campus": insider_rec.get("num_unique_campus", 1),
        "late_exit_flag": insider_rec.get("late_exit_flag", 0),
        "entry_during_weekend": insider_rec.get("entry_during_weekend", 0)
    }

    procurement_data = {
        "price_system": procure_rec.get("price_system", 0),
        "price_actual": procure_rec.get("price_actual", 0),
        "price_difference": procure_rec.get("price_difference", 0),
        "account_mismatch_flag": procure_rec.get("account_mismatch_flag", 0)
    }

    reimbursement_data = {
        "Department": reimburse_rec.get("Department", 0),
        "Expense_Type": reimburse_rec.get("Expense_Type", 0),
        "Claim_Amount": reimburse_rec.get("Claim_Amount", 0),
        "Approval_Status": reimburse_rec.get("Approval_Status", 1),
        "Designation": reimburse_rec.get("Designation", 1),
        "Employee_Tenure_Months": reimburse_rec.get("Employee_Tenure_Months", 24),
        "Receipt_Available": reimburse_rec.get("Receipt_Available", 1),
        "Duplicate_Claim": reimburse_rec.get("Duplicate_Claim", 0),
        "Previous_Claims_Count": reimburse_rec.get("Previous_Claims_Count", 0),
        "Approval_Time_Days": reimburse_rec.get("Approval_Time_Days", 1),
        "Weekend_Claim": reimburse_rec.get("Weekend_Claim", 0),
        "Policy_Violation_Count": reimburse_rec.get("Policy_Violation_Count", 0),
        "Payment_Method": reimburse_rec.get("Payment_Method", 0)
    }

    position = employee_profile.get("position", "Manager")

    position_mapping = {
        "Senior": "Senior Staff"
    }

    position = position_mapping.get(position, position)

    payroll_data = {
        "department": employee_profile.get("department", "Finance"),
        "position": position,
        "salary_system": payroll_rec.get("salary_system", 0),
        "salary_received": payroll_rec.get("salary_received", 0),
        "salary_difference": payroll_rec.get("salary_difference", 0)
    }

    

    # 5. Send the dynamic dictionaries to predictor.py
    probabilities = predict_all(insider_data, procurement_data, reimbursement_data, payroll_data)
    
    # 6. Generate final weighted calculation from risk_engine.py
    report = generate_report_data(
        probabilities["insider"], 
        probabilities["procurement"], 
        probabilities["reimbursement"], 
        probabilities["payroll"]
    )
    
    # Append the employee name to the report payload for front-end usage
    report["employee_name"] = employee_profile["employee_name"]
    return report, probabilities




#  Standalone execution validation block
if __name__ == "__main__":
    test_id = "EMP1000"  # Raka Saputra
    print(f"Scanning master JSON logs for ID: {test_id}...\n")
    
    results_bundle = analyze_single_employee(test_id)
    if results_bundle:
        report, models_probs = results_bundle
        print("====== BACKEND LOG VERIFICATION ======")
        print(f"Target Employee : {report['employee_name']} ({test_id})")
        print(f"Unified Score   : {report['overall_score']} / 100")
        print(f"Calculated Risk : {report['risk_level']}")
        print(f"System Flags    : {report['reasons']}")
        print("=======================================")