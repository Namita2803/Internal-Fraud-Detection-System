"""Employee-level orchestration without fabricating cross-domain relationships."""
import os
import pandas as pd

from .predictor import predict_all
from .risk_engine import generate_report_data

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_DIR = os.path.join(BASE_DIR, "datasets")


def _employee_master():
    return pd.read_csv(os.path.join(DATASET_DIR, "employees.csv"))


def _payroll():
    return pd.read_csv(os.path.join(DATASET_DIR, "payroll.csv"))


def _procurement():
    return pd.read_csv(os.path.join(DATASET_DIR, "procurement.csv"))


def _reimbursement():
    return pd.read_excel(os.path.join(DATASET_DIR, "improved_reimbursement_fraud_dataset.xlsx"))


def _valid_payroll_position(position):
    # The only verified semantic normalization required by the training data.
    return "Senior Staff" if position == "Senior" else position


def analyze_single_employee(target_emp_id):
    employees = _employee_master()
    employee_rows = employees[employees["employee_id"] == target_emp_id]
    if employee_rows.empty:
        return None
    employee = employee_rows.iloc[0]

    payroll = _payroll()
    procurement = _procurement()
    reimbursement = _reimbursement()

    pay_rows = payroll[payroll["employee_id"] == target_emp_id]
    proc_rows = procurement[procurement["employee_id"] == target_emp_id]

    # No employee_id relationship exists in the insider dataset, so it is unavailable.
    insider_data = None

    # Reimbursement uses E### IDs while the master uses EMP####. No legitimate
    # crosswalk is present, so reimbursement is unavailable at employee level.
    reimbursement_data = None

    procurement_data = None
    if not proc_rows.empty:
        # The procurement model is transaction-level. For an employee with multiple
        # transactions, score every transaction and use the maximum probability as
        # the employee-level risk: one highly suspicious transaction must not be
        # hidden by whichever transaction happens to appear first.
        transaction_data = proc_rows[[
            "price_system", "price_actual", "price_difference", "account_mismatch_flag"
        ]].to_dict("records")
        procurement_data = transaction_data

    payroll_data = None
    if not pay_rows.empty:
        pay = pay_rows.iloc[0]
        position = _valid_payroll_position(employee["position"])
        payroll_data = {
            "department": employee["department"],
            "position": position,
            "salary_system": pay["salary_system"],
            "salary_received": pay["salary_received"],
            "salary_difference": pay["salary_difference"],
        }

    probabilities = predict_all(
        insider_data=None,
        procurement_data=None,
        reimbursement_data=None,
        payroll_data=payroll_data,
    )

    if procurement_data:
        procurement_probs = [
            predict_all(procurement_data=row)["procurement"]
            for row in procurement_data
        ]
        probabilities["procurement"] = max(procurement_probs)

    report = generate_report_data(
        probabilities.get("insider"),
        probabilities.get("procurement"),
        probabilities.get("reimbursement"),
        probabilities.get("payroll"),
    )
    report["employee_name"] = employee["employee_name"]
    return report, probabilities


if __name__ == "__main__":
    result = analyze_single_employee("EMP1000")
    print(result)
