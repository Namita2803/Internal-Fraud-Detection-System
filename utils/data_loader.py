# utils/data_loader.py
"""
Centralized, cached data access layer for the dashboard.
Reads existing datasets from /datasets and lazily loads the backend
package (main.py, predictor.py, risk_engine.py) from /backend.
"""
import os
import sys
import json

import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "datasets")

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


@st.cache_data(show_spinner=False)
def load_employees() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATASET_DIR, "employees.csv"))


@st.cache_data(show_spinner=False)
def load_payroll() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATASET_DIR, "payroll.csv"))


@st.cache_data(show_spinner=False)
def load_procurement() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATASET_DIR, "procurement.csv"))


@st.cache_data(show_spinner=False)
def load_insider() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATASET_DIR, "insider_threat_clean_dataset.csv"))


@st.cache_data(show_spinner=False)
def load_reimbursement() -> pd.DataFrame:
    return pd.read_excel(os.path.join(DATASET_DIR, "improved_reimbursement_fraud_dataset.xlsx"))


@st.cache_data(show_spinner=False)
def load_vendors() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATASET_DIR, "vendors.csv"))


@st.cache_data(show_spinner=False)
def load_salary_grade() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATASET_DIR, "salary_grade.csv"))


@st.cache_data(show_spinner=False)
def load_json_database() -> dict:
    with open(os.path.join(DATASET_DIR, "fraud_system_full.json"), "r") as f:
        return json.load(f)


@st.cache_resource(show_spinner="Initializing fraud detection engine...")
def get_backend():
    """
    Lazily imports src.main / src.predictor / src.risk_engine.
    """

    try:
        from src import main as backend_main
        from src import predictor as backend_predictor
        from src import risk_engine as backend_risk_engine

        return {
            "main": backend_main,
            "predictor": backend_predictor,
            "risk_engine": backend_risk_engine,
            "status": "operational",
            "error": None,
        }

    except Exception as exc:

        return {
            "main": None,
            "predictor": None,
            "risk_engine": None,
            "status": "offline",
            "error": str(exc),
        }

@st.cache_data(show_spinner="Scoring employee population against trained models...")
def compute_population_risk(employee_ids: tuple) -> pd.DataFrame:
    backend = get_backend()
    if backend["status"] != "operational":
        return pd.DataFrame()

    rows = []
    failures = []
    for emp_id in employee_ids:
        try:
            result = backend["main"].analyze_single_employee(emp_id)
            if result is None:
                failures.append(f"{emp_id}: employee record not found")
                continue
            report, probs = result
            rows.append(
                {
                    "employee_id": emp_id,
                    "employee_name": report.get("employee_name", "Unrecorded"),
                    "insider_probability": probs["insider"],
                    "procurement_probability": probs["procurement"],
                    "reimbursement_probability": probs["reimbursement"],
                    "payroll_probability": probs["payroll"],
                    "overall_score": report["overall_score"],
                    "risk_level": report["risk_level"],
                    "reasons": "; ".join(report["reasons"]),
                }
            )
        except Exception as exc:
            failures.append(f"{emp_id}: {exc}")

    if failures and not rows:
        raise RuntimeError("Population scoring failed for every employee. First failures: " + " | ".join(failures[:5]))
    if failures:
        # Do not hide systemic failures; successful employee scores remain usable.
        # The failure details are retained in the dataframe for diagnostics without
        # changing the existing page layout.
        print("Population scoring failures: " + " | ".join(failures[:20]))

    return pd.DataFrame(rows)


def get_feature_importance(model, feature_names):
    """Best-effort extraction across raw estimators and sklearn Pipelines."""
    try:
        estimator = model
        if hasattr(model, "named_steps"):
            for step in model.named_steps.values():
                if hasattr(step, "feature_importances_") or hasattr(step, "coef_"):
                    estimator = step

        if hasattr(estimator, "feature_importances_"):
            values = estimator.feature_importances_
            return dict(zip(feature_names, values))

        if hasattr(estimator, "coef_"):
            coefs = estimator.coef_
            coefs = coefs[0] if getattr(coefs, "ndim", 1) > 1 else coefs
            return dict(zip(feature_names, coefs))

    except Exception:
        return None

    return None