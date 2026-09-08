"""Model loading and training-consistent inference helpers."""
import os
import pickle
from typing import Mapping

import joblib
import pandas as pd

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))

MODEL_PATHS = {
    "insider": os.path.join(MODEL_DIR, "insider_model.pkl"),
    "procurement": os.path.join(MODEL_DIR, "procurement_model.pkl"),
    "reimbursement": os.path.join(MODEL_DIR, "reimbursement_model.pkl"),
    "payroll": os.path.join(MODEL_DIR, "payroll_model.pkl"),
}
REIMBURSEMENT_ENCODERS = os.path.join(MODEL_DIR, "reimbursement_encoders.pkl")
PAYROLL_DEPARTMENT_ENCODER = os.path.join(MODEL_DIR, "payroll_department_encoder.pkl")
PAYROLL_POSITION_ENCODER = os.path.join(MODEL_DIR, "payroll_position_encoder.pkl")


def _load_pickle(path):
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        raise FileNotFoundError(f"Required model artifact is missing or empty: {path}")
    with open(path, "rb") as f:
        return pickle.load(f)


def load_models():
    models = {name: _load_pickle(path) for name, path in MODEL_PATHS.items()}
    models["reimbursement_encoders"] = _load_pickle(REIMBURSEMENT_ENCODERS)
    insider_path = os.path.join(MODEL_DIR, "insider_encoders.pkl")
    models["insider_encoders"] = _load_pickle(insider_path)
    models["payroll_department_encoder"] = joblib.load(PAYROLL_DEPARTMENT_ENCODER)
    models["payroll_position_encoder"] = joblib.load(PAYROLL_POSITION_ENCODER)
    return models


models = load_models()


def get_payroll_departments():
    return list(models["payroll_department_encoder"].classes_)


def get_payroll_positions():
    return list(models["payroll_position_encoder"].classes_)


def _model_features(model):
    features = getattr(model, "feature_names_in_", None)
    if features is None:
        raise ValueError("Model does not expose feature_names_in_; inference schema cannot be verified safely.")
    return list(features)


def _prepare_frame(data: Mapping, model, *, encoders=None, binary_columns=()):
    if data is None:
        raise ValueError("No model input was supplied.")

    expected = _model_features(model)
    missing = [c for c in expected if c not in data]
    unexpected = [c for c in data if c not in expected]
    if missing:
        raise ValueError(f"Missing model features: {', '.join(missing)}")
    if unexpected:
        # Extra application metadata must never leak into model input.
        data = {k: v for k, v in data.items() if k in expected}

    df = pd.DataFrame([{c: data[c] for c in expected}], columns=expected)

    if encoders:
        for column, encoder in encoders.items():
            if column not in df.columns:
                continue
            values = df[column]
            if column in binary_columns:
                values = values.apply(
                    lambda value: "No" if isinstance(value, (bool, int)) and int(value) == 0
                    else "Yes" if isinstance(value, (bool, int)) and int(value) == 1
                    else value
                )
            try:
                df[column] = encoder.transform(values)
            except Exception as exc:
                raise ValueError(
                    f"Unknown category in '{column}': {values.iloc[0]!r}. "
                    f"Valid training categories are {list(encoder.classes_)}"
                ) from exc

    for column in expected:
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError(f"Model feature '{column}' is not numeric after preprocessing.")
        df[column] = pd.to_numeric(df[column], errors="raise")

    return df


def _probability(model_name, data, *, encoders=None, binary_columns=()):
    model = models[model_name]
    df = _prepare_frame(data, model, encoders=encoders, binary_columns=binary_columns)
    try:
        return float(model.predict_proba(df)[0][1])
    except Exception as exc:
        raise ValueError(f"{model_name.title()} prediction failed: {exc}") from exc


def predict_insider(data):
    # Training encoded every object column independently with LabelEncoder.
    return _probability("insider", data, encoders={
        c: models["insider_encoders"][c]
        for c in models.get("insider_encoders", {})
    })


def predict_procurement(data):
    return _probability("procurement", data)


def predict_reimbursement(data):
    categorical = models["reimbursement_encoders"]
    return _probability(
        "reimbursement",
        data,
        encoders=categorical,
        binary_columns=("Receipt_Available", "Duplicate_Claim", "Weekend_Claim"),
    )


def predict_payroll(data):
    department_encoder = models["payroll_department_encoder"]
    position_encoder = models["payroll_position_encoder"]

    department = data.get("department") if data else None
    position = data.get("position") if data else None
    if department is None or position is None:
        raise ValueError("Payroll department and position are required.")

    if department not in set(department_encoder.classes_):
        raise ValueError(
            f"Unknown payroll department '{department}'. Valid categories are {list(department_encoder.classes_)}"
        )
    if position not in set(position_encoder.classes_):
        raise ValueError(
            f"Unknown payroll position '{position}'. Valid categories are {list(position_encoder.classes_)}"
        )

    encoded = dict(data)
    encoded["department"] = int(department_encoder.transform([department])[0])
    encoded["position"] = int(position_encoder.transform([position])[0])
    return _probability("payroll", encoded)


def predict_all(insider_data=None, procurement_data=None, reimbursement_data=None, payroll_data=None):
    """Score only domains for which genuine employee-level evidence exists."""
    results = {}
    if insider_data is not None:
        results["insider"] = predict_insider(insider_data)
    else:
        results["insider"] = None
    if procurement_data is not None:
        results["procurement"] = predict_procurement(procurement_data)
    else:
        results["procurement"] = None
    if reimbursement_data is not None:
        results["reimbursement"] = predict_reimbursement(reimbursement_data)
    else:
        results["reimbursement"] = None
    if payroll_data is not None:
        results["payroll"] = predict_payroll(payroll_data)
    else:
        results["payroll"] = None
    return results
