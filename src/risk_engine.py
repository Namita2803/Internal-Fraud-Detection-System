"""
Risk Engine for Internal Fraud Detection System

This module combines the outputs of all fraud detection models
and generates:
1. Overall Fraud Risk Score
2. Risk Level (with Flowchart Override Logic)
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
    Input: Probability values between 0 and 1
    Output: Risk Score (0-100)
    """
    score = (
        insider_prob * 0.40 +
        procurement_prob * 0.25 +
        reimbursement_prob * 0.20 +
        payroll_prob * 0.15
    ) * 100

    return round(score, 2)


# -----------------------------
# Determine Risk Level (UPDATED WITH YOUR FLOWCHART)
# -----------------------------
def get_risk_level(score, insider_prob, procurement_prob, reimbursement_prob, payroll_prob):
    """
    Convert score into Low / Medium / High
    Applies your custom flowchart override guards.
    """
    all_probs = [insider_prob, procurement_prob, reimbursement_prob, payroll_prob]
    
    # 🚨 OVERRIDE 1: If ANY single model has a probability of 70% (0.70) or more
    if max(all_probs) >= 0.70:
        return "High"
        
    # 🚨 OVERRIDE 2: If ANY TWO or more models have a probability of 50% (0.50) or more
    models_over_50 = sum(1 for p in all_probs if p >= 0.50)
    if models_over_50 >= 2:
        return "High"

    # Standard baseline fallback conditions
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
        reasons.append("High insider threat detected.")

    if procurement_prob >= 0.5:
        reasons.append("Suspicious procurement activity detected.")

    if reimbursement_prob >= 0.5:
        reasons.append("Suspicious reimbursement claims detected.")

    if payroll_prob >= 0.5:
        reasons.append("Potential payroll fraud detected.")

    if len(reasons) == 0:
        reasons.append("No significant fraud indicators detected.")

    return reasons


# -----------------------------
<<<<<<< Updated upstream
# Display Final Report (UPDATED CALL SIGNATURE)
=======
# Generate Critical Alerts
# -----------------------------
def generate_critical_alerts(
    insider_prob,
    procurement_prob,
    reimbursement_prob,
    payroll_prob
):

    alerts = []

    if insider_prob >= 0.80:
        alerts.append("CRITICAL: High Insider Threat detected.")

    if procurement_prob >= 0.80:
        alerts.append("CRITICAL: High Procurement Fraud detected.")

    if reimbursement_prob >= 0.80:
        alerts.append("CRITICAL: High Reimbursement Fraud detected.")

    if payroll_prob >= 0.80:
        alerts.append("CRITICAL: High Payroll Fraud detected.")

    return alerts


# -----------------------------
# Display Final Report
>>>>>>> Stashed changes
# -----------------------------
def generate_report(
    insider_prob,
    procurement_prob,
    reimbursement_prob,
    payroll_prob
):
<<<<<<< Updated upstream
=======
    


>>>>>>> Stashed changes
    score = calculate_risk_score(
        insider_prob,
        procurement_prob,
        reimbursement_prob,
        payroll_prob
    )

    # Passed individual probabilities here to trigger your flowchart checks
    level = get_risk_level(score, insider_prob, procurement_prob, reimbursement_prob, payroll_prob)

    reasons = generate_explanation(
        insider_prob,  
        procurement_prob,
        reimbursement_prob,
        payroll_prob
    )


    alerts = generate_critical_alerts(
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


    

    print("\nCritical Alerts")
    print("------------------------------")

    if alerts:
       

       for alert in alerts:

        print(f"⚠ {alert}")
    else:

        print("No critical alerts.")

    print("\nReasons")
    print("------------------------------")
    for reason in reasons:
        print(f"• {reason}")
    print("=" * 45)


# -----------------------------
# Return Report Data (UPDATED CALL SIGNATURE)
# -----------------------------
def generate_report_data(
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

    # Passed individual probabilities here to support Streamlit UI changes
    level = get_risk_level(score, insider_prob, procurement_prob, reimbursement_prob, payroll_prob)

    reasons = generate_explanation(
        insider_prob,
        procurement_prob,
        reimbursement_prob,
        payroll_prob
    )

    alerts = generate_critical_alerts(
    insider_prob,
    procurement_prob,
    reimbursement_prob,
    payroll_prob
)

    return {
<<<<<<< Updated upstream
        "overall_score": float(score),
        "risk_level": level,
        "insider_probability": float(insider_prob),
        "procurement_probability": float(procurement_prob),
        "reimbursement_probability": float(reimbursement_prob),
        "payroll_probability": float(payroll_prob),
        "reasons": reasons
    }



# Test the Risk Engine (UPDATED WITH COMPARISON CASES)
=======

    "overall_score": float(score),

    "risk_level": level,

    "insider_probability": float(insider_prob),

    "procurement_probability": float(procurement_prob),

    "reimbursement_probability": float(reimbursement_prob),

    "payroll_probability": float(payroll_prob),

    "critical_alerts": alerts,

    "reasons": reasons

}

# -----------------------------
# Test the Risk Engine
>>>>>>> Stashed changes
# -----------------------------
if __name__ == "__main__":
    print("\n--- TEST 1: The 98% Payroll Fraudster ---")
    # Low score weighted calculation (~14%), but single-model override kicks in!
    generate_report(0.00, 0.00, 0.00, 0.98)
    
    print("\n--- TEST 2: Multi-Department Moderate Coordination ---")
    # Both sit at 55%. Overall score is only ~24%, but two-model override triggers!
    generate_report(0.00, 0.55, 0.55, 0.00)