"""
Predictor Module

Loads all trained models and returns fraud probabilities.
"""

import pickle
import os
import pandas as pd

# --------------------------------------------------
# Model Paths
# --------------------------------------------------

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

INSIDER_MODEL = os.path.join(MODEL_DIR, "insider_model.pkl")
PROCUREMENT_MODEL = os.path.join(MODEL_DIR, "procurement_model.pkl")
REIMBURSEMENT_MODEL = os.path.join(MODEL_DIR, "reimbursement_model.pkl")
PAYROLL_MODEL = os.path.join(MODEL_DIR, "payroll_model.pkl")


# --------------------------------------------------
# Load Models
# --------------------------------------------------

def load_models():

    models = {}

    with open(INSIDER_MODEL, "rb") as f:
        models["insider"] = pickle.load(f)

    with open(PROCUREMENT_MODEL, "rb") as f:
        models["procurement"] = pickle.load(f)

    with open(REIMBURSEMENT_MODEL, "rb") as f:
        models["reimbursement"] = pickle.load(f)

    with open(PAYROLL_MODEL, "rb") as f:
        models["payroll"] = pickle.load(f)

    return models


models = load_models()


# --------------------------------------------------
# Insider Prediction
# --------------------------------------------------

def predict_insider(data):

    df = pd.DataFrame([data])

    probability = models["insider"].predict_proba(df)[0][1]

    return probability


# --------------------------------------------------
# Procurement Prediction
# --------------------------------------------------

def predict_procurement(data):

    df = pd.DataFrame([data])

    probability = models["procurement"].predict_proba(df)[0][1]

    return probability


# --------------------------------------------------
# Reimbursement Prediction
# --------------------------------------------------

def predict_reimbursement(data):

    df = pd.DataFrame([data])

    probability = models["reimbursement"].predict_proba(df)[0][1]

    return probability


# --------------------------------------------------
# Payroll Prediction
# --------------------------------------------------

def predict_payroll(data):

    df = pd.DataFrame([data])

    probability = models["payroll"].predict_proba(df)[0][1]

    return probability


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
        "department": 0,
        "position": 0,
        "salary_system": 50000,
        "salary_received": 50000,
        "salary_difference": 0
    }

    probability = predict_payroll(payroll_data)

    print("Payroll Fraud Probability:", probability)