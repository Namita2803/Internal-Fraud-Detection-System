"""Weighted fraud-risk aggregation with explicit handling of unavailable domains."""

WEIGHTS = {
    "insider": 0.40,
    "procurement": 0.25,
    "reimbursement": 0.20,
    "payroll": 0.15,
}


def calculate_risk_score(insider_prob, procurement_prob, reimbursement_prob, payroll_prob):
    probabilities = {
        "insider": insider_prob,
        "procurement": procurement_prob,
        "reimbursement": reimbursement_prob,
        "payroll": payroll_prob,
    }
    available = {k: float(v) for k, v in probabilities.items() if v is not None}
    if not available:
        raise ValueError("No employee-level model evidence is available for risk scoring.")

    # Preserve the existing relative weights while renormalizing across domains
    # for which genuine employee-level evidence exists.
    weight_total = sum(WEIGHTS[k] for k in available)
    score = sum(available[k] * WEIGHTS[k] for k in available) / weight_total * 100
    return round(score, 2)


def get_risk_level(score):
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def generate_explanation(insider_prob, procurement_prob, reimbursement_prob, payroll_prob):
    probabilities = {
        "insider": insider_prob,
        "procurement": procurement_prob,
        "reimbursement": reimbursement_prob,
        "payroll": payroll_prob,
    }
    reasons = []
    labels = {
        "insider": "High insider threat detected.",
        "procurement": "Suspicious procurement activity detected.",
        "reimbursement": "Suspicious reimbursement claims detected.",
        "payroll": "Potential payroll fraud detected.",
    }
    for key, probability in probabilities.items():
        if probability is not None and probability >= 0.5:
            reasons.append(labels[key])

    unavailable = [key.title() for key, value in probabilities.items() if value is None]
    if not reasons:
        reasons.append("No significant fraud indicators detected.")
    if unavailable:
        reasons.append("Employee-level evidence unavailable for: " + ", ".join(unavailable) + ".")
    return reasons


def generate_report_data(insider_prob, procurement_prob, reimbursement_prob, payroll_prob):
    score = calculate_risk_score(insider_prob, procurement_prob, reimbursement_prob, payroll_prob)
    return {
        "overall_score": float(score),
        "risk_level": get_risk_level(score),
        "insider_probability": None if insider_prob is None else float(insider_prob),
        "procurement_probability": None if procurement_prob is None else float(procurement_prob),
        "reimbursement_probability": None if reimbursement_prob is None else float(reimbursement_prob),
        "payroll_probability": None if payroll_prob is None else float(payroll_prob),
        "reasons": generate_explanation(insider_prob, procurement_prob, reimbursement_prob, payroll_prob),
    }
