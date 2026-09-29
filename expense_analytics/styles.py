"""Small presentation-only style layer; no remote fonts or UI dependencies."""

import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        .stMainBlockContainer { max-width: 1440px; padding: 2.5rem 2.4rem 4rem; }
        h1 { letter-spacing: -.045em; font-weight: 750; }
        h2, h3 { letter-spacing: -.025em; }
        [data-testid="stSidebar"] { border-right: 1px solid #e2e8f0; }
        [data-testid="stSidebar"] h3 { font-size: 1rem; }
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .8rem; }
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #fff 0%, #f8fafc 100%);
            border: 1px solid #dce5ed; border-radius: 16px; padding: 1.3rem;
            box-shadow: 0 4px 20px #16324f06;
        }
        [data-testid="stMetricLabel"] { color: #526477; font-weight: 500; }
        [data-testid="stMetricValue"] {
            color: #122d40; font-variant-numeric: tabular-nums;
            font-size: clamp(1.5rem, 2.5vw, 2.4rem); letter-spacing: -.035em;
        }
        [data-testid="stMetricValue"] > div { white-space: normal; overflow-wrap: anywhere; }
        [data-testid="stTabs"] [role="tablist"] {
            gap: .4rem; padding: .35rem; border-radius: 12px;
            background: #eaf0f4; border-bottom: 0; margin: .8rem 0 1.7rem;
        }
        [data-testid="stTabs"] [role="tab"] {
            padding: .65rem 1.15rem; border-radius: 8px; height: auto;
        }
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
            background: #fff; color: #087e8b; box-shadow: 0 2px 6px #122d4010;
        }
        [data-testid="stExpander"], [data-testid="stDataFrame"] {
            border-radius: 12px; background: #fff;
        }
        [data-testid="stAlert"] { border-radius: 12px; }
        [data-testid="stButton"] button { border-radius: 9px; font-weight: 600; }
        [data-testid="stCaptionContainer"] { color: #586c7e; }
        .pea-eyebrow { color: #087e8b; font-size: .72rem; font-weight: 750;
            letter-spacing: .15em; margin-bottom: .4rem; }
        .pea-note { border-left: 3px solid #087e8b; padding: .7rem 1rem;
            color: #526477; background: #eef7f7; border-radius: 0 8px 8px 0; }
        @media (max-width: 900px) {
            .stMainBlockContainer { padding: 1.5rem 1rem 3rem; }
            h1 { font-size: 2rem !important; }
            [data-testid="stTabs"] [role="tab"] { padding: .6rem .8rem; }
        }
        @media (max-width: 640px) {
            [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                min-width: 100% !important; width: 100% !important; flex: 1 1 100% !important;
            }
            [data-testid="stMetricValue"] { font-size: 2rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def style_chart(chart):
    """Apply consistent chart typography, subtle grids, and clean framing."""
    return (
        chart.configure_view(strokeWidth=0)
        .configure_axis(
            labelColor="#526477",
            titleColor="#526477",
            gridColor="#e9eff3",
            domain=False,
            labelFontSize=11,
            titleFontSize=11,
            titlePadding=14,
        )
        .configure_title(color="#122d40", fontSize=15, anchor="start")
    )
