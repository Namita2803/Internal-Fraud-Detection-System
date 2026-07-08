import streamlit as st

# ==========================================================
# COLOR PALETTE
# ==========================================================

COLOR_NAVY = "#0F172A"

COLOR_BLUE_900 = "#1E3A8A"
COLOR_BLUE_700 = "#1D4ED8"
COLOR_BLUE_600 = "#2563EB"
COLOR_BLUE_400 = "#60A5FA"
COLOR_BLUE_200 = "#BFDBFE"

COLOR_SLATE_500 = "#64748B"
COLOR_SLATE_100 = "#E2E8F0"

PLOTLY_COLORWAY = [
    COLOR_BLUE_900,
    COLOR_BLUE_700,
    COLOR_BLUE_600,
    COLOR_BLUE_400,
    COLOR_BLUE_200,
]

RISK_COLORS = {

    "Low": {
        "bar": "#60A5FA",
        "fill": "#DBEAFE",
        "text": "#1E3A8A",
    },

    "Medium": {
        "bar": "#2563EB",
        "fill": "#BFDBFE",
        "text": "#1E40AF",
    },

    "High": {
        "bar": "#1D4ED8",
        "fill": "#93C5FD",
        "text": "#1E3A8A",
    },

    "Critical": {
        "bar": "#0F172A",
        "fill": "#CBD5E1",
        "text": "#0F172A",
    },
}

# ==========================================================
# GLOBAL THEME
# ==========================================================

def inject_global_theme():

    st.markdown(
        """
        <style>

        .stApp{
            background:#F8FAFC;
        }

        .block-container{
            max-width:1400px;
            padding-top:2rem;
            padding-left:2rem;
            padding-right:2rem;
            padding-bottom:2rem;
        }

        [data-testid="stSidebar"]{
            background:white;
            border-right:1px solid #E2E8F0;
        }

        h1,h2,h3{
            color:#0F172A;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# SIDEBAR
# ==========================================================

def render_sidebar_brand():

    st.sidebar.title("Internal Fraud")

    st.sidebar.caption(
        "Enterprise Risk Analytics Platform"
    )


def render_engine_status(status="Operational"):

    if status.lower() == "operational":

        st.sidebar.success("Engine Operational")

    else:

        st.sidebar.error("Engine Offline")


# ==========================================================
# PAGE HELPERS
# ==========================================================

def page_header(title, subtitle):

    st.title(title)

    st.caption(subtitle)


def section_label(text):

    st.subheader(text)


def kpi_card(
    title,
    value,
    subtitle="",
    light=False,
):

    if light:
        border = "#BFDBFE"
        background = "#F8FBFF"
    else:
        border = "#E2E8F0"
        background = "#FFFFFF"

    st.markdown(
        f"""
        <div style="
            border:1px solid {border};
            border-radius:12px;
            padding:18px;
            background:{background};
            margin-bottom:12px;
        ">
            <div style="
                color:#64748B;
                font-size:14px;
            ">
                {title}
            </div>

            <div style="
                font-size:28px;
                font-weight:700;
                margin-top:8px;
            ">
                {value}
            </div>

            <div style="
                color:#64748B;
                margin-top:6px;
            ">
                {subtitle}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_pill(level):

    color = RISK_COLORS.get(level, COLOR_SLATE_500)

    return f"""
    <span style="
        background:{color};
        color:white;
        padding:4px 10px;
        border-radius:999px;
        font-size:0.85rem;
        font-weight:600;
    ">
        {level}
    </span>
    """