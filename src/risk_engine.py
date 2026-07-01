"""
Risk Engine for Internal Fraud Detection System

This module combines the outputs of all fraud detection models
and generates:
1. Overall Fraud Risk Score
2. Risk Level
3. Explanation
"""

# -----------------------------
# Calculate Overall Risk Score
# -----------------------------
def calculate_risk_score(
    insider_prob,
    procurement_prob,
    reimbursement_prob,
    payroll_prob
):
    """
    Calculate weighted fraud score.

    Input:
        Probability values between 0 and 1

    Output:
        Risk Score (0-100)
    """

    score = (
        insider_prob * 0.40 +
        procurement_prob * 0.25 +
        reimbursement_prob * 0.20 +
        payroll_prob * 0.15
    ) * 100

    return round(score, 2)


# -----------------------------
# Determine Risk Level
# -----------------------------
def get_risk_level(score):
    """
    Convert score into
    Low / Medium / High
    """

    if score >= 70:
        return "High"

    elif score >= 40:
        return "Medium"

    else:
        return "Low"


# -----------------------------
# Generate Explanation
# -----------------------------
def generate_explanation(
    insider_prob,
    procurement_prob,
    reimbursement_prob,
    payroll_prob
):

    reasons = []

    if insider_prob >= 0.5:
        reasons.append(
            "High insider threat detected."
        )

    if procurement_prob >= 0.5:
        reasons.append(
            "Suspicious procurement activity detected."
        )

    if reimbursement_prob >= 0.5:
        reasons.append(
            "Suspicious reimbursement claims detected."
        )

    if payroll_prob >= 0.5:
        reasons.append(
            "Potential payroll fraud detected."
        )

    if len(reasons) == 0:
        reasons.append(
            "No significant fraud indicators detected."
        )

    return reasons


# -----------------------------
# Display Final Report
# -----------------------------
def generate_report(
    insider_prob,
    procurement_prob,
    reimbursement_prob,
    payroll_prob
):

    score = calculate_risk_score(
        insider_prob,
        procurement_prob,
        reimbursement_prob,
        payroll_prob
    )

    level = get_risk_level(score)

    reasons = generate_explanation(
        insider_prob,  
        procurement_prob,
        reimbursement_prob,
        payroll_prob
    )

    print("=" * 45)
    print(" INTERNAL FRAUD DETECTION REPORT ")
    print("=" * 45)

    print(f"\nOverall Fraud Score : {score}%")
    print(f"Risk Level          : {level}")

    print("\nModel Outputs")
    print("------------------------------")
    print(f"Insider Model       : {insider_prob:.2f}")
    print(f"Procurement Model   : {procurement_prob:.2f}")
    print(f"Reimbursement Model : {reimbursement_prob:.2f}")
    print(f"Payroll Model       : {payroll_prob:.2f}")

    print("\nReasons")
    print("------------------------------")

    for reason in reasons:
        print(f"• {reason}")

    print("=" * 45)


# -----------------------------
# Test the Risk Engine
# -----------------------------
if __name__ == "__main__":

    # Sample probabilities
    insider_probability = 0.92
    procurement_probability = 0.25
    reimbursement_probability = 0.73
    payroll_probability = 0.81

    generate_report(
        insider_probability,
        procurement_probability,
        reimbursement_probability,
        payroll_probability
    )