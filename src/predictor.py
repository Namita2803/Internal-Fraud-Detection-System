"""
Predictor Module

Loads all trained models and returns fraud probabilities.
"""
import joblib
import pickle
import os
import pandas as pd

# --------------------------------------------------
# Model Paths
# --------------------------------------------------

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

INSIDER_MODEL = os.path.join(MODEL_DIR, "insider_model.pkl")
INSIDER_ENCODERS = os.path.join(MODEL_DIR, "insider_encoders.pkl")  # Added Insider Encoders

PROCUREMENT_MODEL = os.path.join(MODEL_DIR, "procurement_model.pkl")
REIMBURSEMENT_MODEL = os.path.join(MODEL_DIR, "reimbursement_model.pkl")
PAYROLL_MODEL = os.path.join(MODEL_DIR, "payroll_model.pkl")
PAYROLL_DEPARTMENT_ENCODER = os.path.join(
    MODEL_DIR,
    "payroll_department_encoder.pkl"
)

PAYROLL_POSITION_ENCODER = os.path.join(
    MODEL_DIR,
    "payroll_position_encoder.pkl"
)


# --------------------------------------------------
# Load Models
# --------------------------------------------------

def load_models():

    models = {}

    with open(INSIDER_MODEL, "rb") as f:
        models["insider"] = pickle.load(f)

    # Load Insider Encoders
    models["insider_encoders"] = joblib.load(INSIDER_ENCODERS)

    with open(PROCUREMENT_MODEL, "rb") as f:
        models["procurement"] = pickle.load(f)

    with open(REIMBURSEMENT_MODEL, "rb") as f:
        models["reimbursement"] = pickle.load(f)

    with open(PAYROLL_MODEL, "rb") as f:
        models["payroll"] = pickle.load(f)

    models["payroll_department_encoder"] = joblib.load(
        PAYROLL_DEPARTMENT_ENCODER
    )
    models["payroll_position_encoder"] = joblib.load(
        PAYROLL_POSITION_ENCODER
    )

    return models


models = load_models()

# --------------------------------------------------
# Validate Input
# --------------------------------------------------

def validate_input(data, required_columns):

    missing = []

    for column in required_columns:

        if column not in data:

            missing.append(column)

    if missing:

        raise ValueError(
            "Missing required fields: " +
            ", ".join(missing)
        )


# --------------------------------------------------
# Insider Prediction
# --------------------------------------------------

# --------------------------------------------------
# Insider Prediction
# --------------------------------------------------

def predict_insider(data):

    try:

        df = pd.DataFrame([data])

        # Apply saved LabelEncoders to text columns
        insider_encoders = models["insider_encoders"]
        for col, encoder in insider_encoders.items():
            if col in df.columns:
                df[col] = encoder.transform(df[col].astype(str))

        # 🔑 Reorder columns to match the exact order expected by the trained model
        if hasattr(models["insider"], "feature_names_in_"):
            df = df[models["insider"].feature_names_in_]

        probability = models["insider"].predict_proba(df)[0][1]

        return float(probability)

    except Exception as e:

        raise ValueError(f"Insider prediction failed: {e}")
    

# --------------------------------------------------
# Procurement Prediction
# --------------------------------------------------

def predict_procurement(data):

    try:

        df = pd.DataFrame([data])

        probability = models["procurement"].predict_proba(df)[0][1]

        return float(probability)

    except Exception as e:

        raise ValueError(f"Procurement prediction failed: {e}")


# --------------------------------------------------
# Reimbursement Prediction
# --------------------------------------------------

def predict_reimbursement(data):

    try:

        required_columns = [

            "Department",

            "Expense_Type",

            "Claim_Amount",

            "Approval_Status",

            "Designation",

            "Employee_Tenure_Months",

            "Receipt_Available",

            "Duplicate_Claim",

            "Previous_Claims_Count",

            "Approval_Time_Days",

            "Weekend_Claim",

            "Policy_Violation_Count",

            "Payment_Method"

        ]

        validate_input(data, required_columns)

        df = pd.DataFrame([data])

        probability = models["reimbursement"].predict_proba(df)[0][1]

        return float(probability)

    except Exception as e:

        raise ValueError(f"Reimbursement prediction failed: {e}")


# --------------------------------------------------
# Payroll Prediction
# --------------------------------------------------

def predict_payroll(data):
    

    try:

        required_columns = [

            "department",

            "position",

            "salary_system",

            "salary_received",

            "salary_difference"

        ]

        validate_input(data, required_columns)

        df = pd.DataFrame([data])

        df["department"] = models[
            "payroll_department_encoder"
        ].transform(df["department"])

        df["position"] = models[
            "payroll_position_encoder"
        ].transform(df["position"])

        probability = models["payroll"].predict_proba(df)[0][1]

        return float(probability)

    except Exception as e:

        raise ValueError(f"Payroll prediction failed: {e}")


# --------------------------------------------------
# Predict Using All Models
# --------------------------------------------------

def predict_all(
    insider_data,
    procurement_data,
    reimbursement_data,
    payroll_data
):

    results = {

        "insider": predict_insider(insider_data),

        "procurement": predict_procurement(procurement_data),

        "reimbursement": predict_reimbursement(reimbursement_data),

        "payroll": predict_payroll(payroll_data)

    }

    return results

# --------------------------------------------------
# Test Payroll Prediction
# --------------------------------------------------

if __name__ == "__main__":

    payroll_data = {
    "department": "Finance",
    "position": "Manager",
    "salary_system": 50000,
    "salary_received": 50000,
    "salary_difference": 0
}

    probability = predict_payroll(payroll_data)

    print("Payroll Fraud Probability:", probability)


# --------------------------------------------------
# Test Insider Prediction
# --------------------------------------------------

if __name__ == "__main__":

    sample_insider_data = {
        "employee_department": "Engineering Department",
        "employee_campus": "Campus C",
        "employee_position": "Design Engineer",
        "employee_seniority_years": 22,
        "is_contractor": 0,
        "employee_classification": 2,
        "has_foreign_citizenship": 0,
        "has_criminal_record": 0,
        "has_medical_history": 0,
        "employee_origin_country": "Georgia",
        "total_files_burned": 4,
        "burned_from_other": 0,
        "is_abroad": 0,
        "trip_day_number": 0.0,
        "hostility_country_level": 0,
        "num_entries": 1,
        "num_unique_campus": 1,
        "late_exit_flag": 0,
        "entry_during_weekend": 1,
        "total_printed_pages": 0,
        "num_printed_pages_off_hours": 0
    }

    try:
        insider_prob = predict_insider(sample_insider_data)
        print(f"✅ Insider Fraud Probability: {insider_prob:.4f}")
    except Exception as e:
        print(f"❌ Insider Prediction Failed: {e}")