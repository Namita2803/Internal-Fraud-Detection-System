# utils/theme.py
"""
Central visual theme for the Internal Fraud Detection platform.
Palette: deep navy / slate black with blue and white gradients only.
No purple is used anywhere in this module.
"""
import streamlit as st

COLOR_BLACK = "#05070D"
COLOR_NAVY = "#0B1120"
COLOR_SLATE_900 = "#0F172A"
COLOR_SLATE_700 = "#334155"
COLOR_SLATE_500 = "#64748B"
COLOR_SLATE_300 = "#CBD5E1"
COLOR_SLATE_100 = "#E2E8F0"
COLOR_BLUE_900 = "#1E3A8A"
COLOR_BLUE_700 = "#1D4ED8"
COLOR_BLUE_600 = "#2563EB"
COLOR_BLUE_400 = "#60A5FA"
COLOR_BLUE_200 = "#BFDBFE"
COLOR_BLUE_100 = "#DBEAFE"
COLOR_WHITE = "#FFFFFF"

RISK_COLORS = {
    "Low": {"bg": COLOR_BLUE_100, "fg": COLOR_BLUE_900, "bar": COLOR_BLUE_400},
    "Medium": {"bg": COLOR_BLUE_600, "fg": COLOR_WHITE, "bar": COLOR_BLUE_700},
    "High": {"bg": COLOR_NAVY, "fg": COLOR_WHITE, "bar": COLOR_BLACK},
}

PLOTLY_COLORWAY = [
    COLOR_NAVY, COLOR_BLUE_900, COLOR_BLUE_700,
    COLOR_BLUE_600, COLOR_BLUE_400, COLOR_BLUE_200, COLOR_SLATE_300,
]


def inject_global_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        div[data-testid="stDecoration"] {display: none;}

        .stApp {
            background: linear-gradient(180deg, #F8FAFC 0%, #EEF2F7 45%, #E7EDF5 100%);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #05070D 0%, #0B1120 55%, #101B33 100%);
            border-right: 1px solid rgba(255,255,255,0.05);
        }
        section[data-testid="stSidebar"] * {
            color: #E2E8F0 !important;
        }
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stMultiSelect label {
            color: #94A3B8 !important;
        }

        .platform-title {
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: 0.06em;
            color: #F8FAFC;
            text-transform: uppercase;
            margin-bottom: 0;
        }
        .platform-subtitle {
            font-size: 0.78rem;
            color: #94A3B8;
            letter-spacing: 0.02em;
            margin-top: 2px;
        }

        .page-header {
            font-size: 1.9rem;
            font-weight: 800;
            color: #0B1120;
            letter-spacing: -0.01em;
            margin-bottom: 0;
        }
        .page-subheader {
            font-size: 0.95rem;
            color: #64748B;
            margin-top: 2px;
            margin-bottom: 1.4rem;
        }

        .section-label {
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #1D4ED8;
            border-left: 3px solid #1D4ED8;
            padding-left: 8px;
            margin: 1.6rem 0 0.8rem 0;
        }

        .kpi-card {
            background: linear-gradient(135deg, #0B1120 0%, #1E3A8A 100%);
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 8px 24px rgba(11,17,32,0.18);
            border: 1px solid rgba(255,255,255,0.06);
            height: 100%;
        }
        .kpi-card.light {
            background: linear-gradient(135deg, #FFFFFF 0%, #EAF1FC 100%);
            border: 1px solid #DCE6F5;
            box-shadow: 0 6px 18px rgba(30,58,138,0.08);
        }
        .kpi-label {
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #93C5FD;
            margin-bottom: 6px;
        }
        .kpi-card.light .kpi-label { color: #1D4ED8; }
        .kpi-value {
            font-size: 1.9rem;
            font-weight: 800;
            color: #FFFFFF;
            line-height: 1.1;
        }
        .kpi-card.light .kpi-value { color: #0B1120; }
        .kpi-delta {
            font-size: 0.78rem;
            color: #BFDBFE;
            margin-top: 6px;
        }
        .kpi-card.light .kpi-delta { color: #475569; }

        .status-pill {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .risk-pill {
            display: inline-block;
            padding: 3px 12px;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }

        .info-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 20px 22px;
            box-shadow: 0 4px 14px rgba(15,23,42,0.05);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            border-bottom: 1px solid #DCE6F5;
        }
        .stTabs [data-baseweb="tab"] {
            height: 42px;
            border-radius: 8px 8px 0 0;
            color: #475569;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #EAF1FC;
            color: #0B1120 !important;
            border-bottom: 3px solid #1D4ED8;
        }

        .stButton > button {
            background: linear-gradient(135deg, #0B1120 0%, #1E3A8A 100%);
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            padding: 0.55rem 1.2rem;
            transition: 0.15s ease-in-out;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
            color: #FFFFFF;
        }

        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 12px 16px;
        }

        [data-testid="stDataFrame"] {
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #E2E8F0;
        }

        hr {
            border: none;
            border-top: 1px solid #E2E8F0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand():
    st.sidebar.markdown(
        """
        <div style="padding: 6px 0 18px 0;">
            <div class="platform-title">Internal Fraud Detection</div>
            <div class="platform-subtitle">Enterprise Risk Intelligence Platform</div>
        </div>
        <hr style="border-top: 1px solid rgba(255,255,255,0.08);">
        """,
        unsafe_allow_html=True,
    )


def render_engine_status(status: str):
    if status == "operational":
        bg, fg, label = COLOR_BLUE_600, COLOR_WHITE, "Models Operational"
    else:
        bg, fg, label = COLOR_SLATE_700, COLOR_SLATE_100, "Models Offline"
    st.sidebar.markdown(
        f"""
        <span class="status-pill" style="background:{bg}; color:{fg};">{label}</span>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, delta: str = None, light: bool = False):
    variant = "light" if light else ""
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="kpi-card {variant}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_label(text: str):
    st.markdown(f'<div class="section-label">{text}</div>', unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="page-header">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subheader">{subtitle}</div>', unsafe_allow_html=True)


def risk_pill(level: str) -> str:
    colors = RISK_COLORS.get(level, {"bg": COLOR_SLATE_300, "fg": COLOR_SLATE_900})
    return f'<span class="risk-pill" style="background:{colors["bg"]}; color:{colors["fg"]};">{level}</span>'