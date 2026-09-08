# utils/charts.py
"""
Plotly chart factories. Every visual is restricted to the blue / white /
deep-navy palette defined in utils.theme — no purple, no red/green/amber.
"""
import plotly.graph_objects as go
import plotly.io as pio

from utils.theme import (
    PLOTLY_COLORWAY, COLOR_NAVY, COLOR_BLUE_900, COLOR_BLUE_700,
    COLOR_BLUE_600, COLOR_BLUE_400, COLOR_BLUE_200, COLOR_SLATE_500,
    COLOR_SLATE_100, RISK_COLORS,
)

_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        colorway=PLOTLY_COLORWAY,
        font=dict(family="Inter, sans-serif", color=COLOR_NAVY, size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor=COLOR_SLATE_100, zerolinecolor=COLOR_SLATE_100, linecolor=COLOR_SLATE_100),
        yaxis=dict(gridcolor=COLOR_SLATE_100, zerolinecolor=COLOR_SLATE_100, linecolor=COLOR_SLATE_100),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=10, r=10, t=40, b=10),
    )
)
pio.templates["fraud_theme"] = _TEMPLATE
pio.templates.default = "fraud_theme"


def probability_gauge(value: float, title: str) -> go.Figure:
    pct = round(value * 100, 2)
    if pct >= 70:
        bar_color = COLOR_NAVY
    elif pct >= 40:
        bar_color = COLOR_BLUE_600
    else:
        bar_color = COLOR_BLUE_400

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=pct,
            number={"suffix": "%", "font": {"size": 34, "color": COLOR_NAVY}},
            title={"text": title, "font": {"size": 14, "color": COLOR_SLATE_500}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": COLOR_SLATE_500},
                "bar": {"color": bar_color, "thickness": 0.32},
                "bgcolor": "white",
                "borderwidth": 1,
                "bordercolor": COLOR_SLATE_100,
                "steps": [
                    {"range": [0, 40], "color": COLOR_BLUE_200},
                    {"range": [40, 70], "color": COLOR_BLUE_400},
                    {"range": [70, 100], "color": COLOR_BLUE_700},
                ],
                "threshold": {
                    "line": {"color": COLOR_NAVY, "width": 3},
                    "thickness": 0.85,
                    "value": pct,
                },
            },
        )
    )
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=50, b=10))
    return fig


def composite_score_gauge(score: float, risk_level: str) -> go.Figure:
    bar_color = RISK_COLORS.get(risk_level, {}).get("bar", COLOR_BLUE_600)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": " / 100", "font": {"size": 30, "color": COLOR_NAVY}},
            title={"text": "Composite Fraud Risk Score", "font": {"size": 14, "color": COLOR_SLATE_500}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": bar_color, "thickness": 0.32},
                "steps": [
                    {"range": [0, 40], "color": COLOR_BLUE_200},
                    {"range": [40, 70], "color": COLOR_BLUE_400},
                    {"range": [70, 100], "color": COLOR_BLUE_700},
                ],
                "borderwidth": 1,
                "bordercolor": COLOR_SLATE_100,
            },
        )
    )
    fig.update_layout(height=270, margin=dict(l=20, r=20, t=50, b=10))
    return fig


def domain_probability_bar(labels, values, title="Model Output Comparison") -> go.Figure:
    available_pairs = [(label, value) for label, value in zip(labels, values) if value is not None]
    if not available_pairs:
        return go.Figure().update_layout(title=title, height=280, xaxis_title="Probability (%)", xaxis_range=[0, 100])
    sorted_pairs = sorted(available_pairs, key=lambda x: x[1])
    labels_s, values_s = zip(*sorted_pairs)
    colors = [
        COLOR_NAVY if v >= 0.7 else COLOR_BLUE_600 if v >= 0.4 else COLOR_BLUE_400
        for v in values_s
    ]
    fig = go.Figure(
        go.Bar(
            x=[round(v * 100, 2) for v in values_s],
            y=labels_s,
            orientation="h",
            marker=dict(color=colors),
            text=[f"{v*100:.1f}%" for v in values_s],
            textposition="outside",
        )
    )
    fig.update_layout(title=title, xaxis_title="Probability (%)", height=280, xaxis_range=[0, 100])
    return fig


def score_distribution_histogram(scores) -> go.Figure:
    fig = go.Figure(
        go.Histogram(
            x=scores,
            marker=dict(color=COLOR_BLUE_600, line=dict(color=COLOR_NAVY, width=0.5)),
            nbinsx=25,
        )
    )
    fig.update_layout(
        title="Composite Risk Score Distribution",
        xaxis_title="Overall Score (0–100)",
        yaxis_title="Employee Count",
        height=340,
        bargap=0.05,
    )
    return fig


def feature_importance_bar(importances: dict, title="Feature Importance") -> go.Figure:
    items = sorted(importances.items(), key=lambda x: abs(x[1]))[-15:]
    labels = [i[0] for i in items]
    values = [i[1] for i in items]
    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(color=COLOR_BLUE_700),
        )
    )
    fig.update_layout(title=title, height=max(320, 24 * len(labels)))
    return fig


def department_heatmap(pivot_df, title="Average Risk Score by Department") -> go.Figure:
    fig = go.Figure(
        go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale=[
                [0.0, COLOR_BLUE_200],
                [0.5, COLOR_BLUE_600],
                [1.0, COLOR_NAVY],
            ],
            colorbar=dict(title="Score"),
        )
    )
    fig.update_layout(title=title, height=380)
    return fig


def alerts_by_domain_bar(domains, counts) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=domains,
            y=counts,
            marker=dict(color=[COLOR_NAVY, COLOR_BLUE_900, COLOR_BLUE_700, COLOR_BLUE_600][: len(domains)]),
            text=counts,
            textposition="outside",
        )
    )
    fig.update_layout(title="Flagged Alerts by Domain", yaxis_title="Alert Count", height=340)
    return fig