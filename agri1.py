import streamlit as st

st.set_page_config(
    page_title="Smart Agri Platform",
    page_icon="🌱",
    layout="wide",
)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import time
from datetime import datetime

from modules.collaboration_network import (
    get_collaboration_recommendation as service_collaboration_recommendation,
    get_market_story as service_market_story,
)
from modules.config import get_service_status
from modules.crop_planner import (
    get_crop_plan as service_crop_plan,
    recommend_crop_by_location,
    simulate_agronomy_scenario as service_simulate_agronomy_scenario,
)
from modules.disease_detection import detect_plant_disease
from modules.finance_module import calculate_farm_profit
from modules.marketplace import list_buyers
from modules.price_prediction import (
    fetch_mandi_prices,
    predict_crop_price,
)
from modules.storage import (
    build_collaboration_frame,
    init_db,
    save_collaboration_submission,
    save_crop_plan,
    save_farmer_profile,
    save_prediction,
)
from modules.voice_assistant import answer_farmer_question, transcribe_audio_bytes
from modules.weather_service import get_real_weather

# --- Page Configuration ---
st.set_page_config(
    page_title="Smart Agri-AI Platform", 
    layout="wide", 
    page_icon="🌱",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for "Visually Appealing" Design ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Manrope:wght@400;500;700&display=swap');

    :root {
        --text-strong: #173f2a;
        --text-main: #274635;
        --text-soft: #4f685a;
        --text-on-dark: #f7fff3;
        --text-on-dark-soft: rgba(247,255,243,0.88);
        --surface-light: rgba(255,255,255,0.84);
        --surface-input: rgba(255,255,255,0.96);
        --surface-sidebar-input: #295d35;
        --app-bg:
            radial-gradient(circle at top left, rgba(140, 220, 170, 0.22), transparent 25%),
            radial-gradient(circle at top right, rgba(255, 214, 102, 0.18), transparent 18%),
            linear-gradient(180deg, #f3fbf3 0%, #edf6ef 48%, #f7f1e7 100%);
        --sidebar-bg: linear-gradient(180deg, #123524 0%, #1b5e20 100%);
    }

    .stApp {
        font-family: 'Manrope', sans-serif;
        background: var(--app-bg);
    }

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
        max-width: 1320px;
    }

    header[data-testid="stHeader"] {
        background: transparent;
        height: auto;
    }

    [data-testid="stToolbar"] {
        opacity: 1;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    h1, h2, h3 {
        color: var(--text-strong) !important;
        font-family: 'Space Grotesk', sans-serif;
    }

    .stMarkdown, .stCaption, .stText, .stSelectbox label, .stSlider label,
    .stNumberInput label, .stTextInput label, .stFileUploader label {
        color: var(--text-main) !important;
    }

    [data-testid="stCaptionContainer"] p,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stWidgetLabel"] {
        color: var(--text-soft) !important;
    }

    .card p, .card li, .card label, .card span,
    .mini-card p, .mini-card li, .mini-card label, .mini-card span,
    [data-testid="stMetric"] p, [data-testid="stMetric"] span, [data-testid="stMetric"] label {
        color: var(--text-main) !important;
    }

    div.card {
        background: var(--surface-light);
        padding: 22px;
        border-radius: 24px;
        box-shadow: 0 18px 42px rgba(23, 63, 42, 0.10);
        margin-bottom: 20px;
        border: 1px solid rgba(23, 63, 42, 0.08);
        backdrop-filter: blur(10px);
        animation: riseIn 0.55s ease both;
    }

    div.card:nth-of-type(2) { animation-delay: 0.05s; }
    div.card:nth-of-type(3) { animation-delay: 0.1s; }
    div.card:nth-of-type(4) { animation-delay: 0.15s; }

    .app-topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        padding: 1rem 1.1rem;
        margin-bottom: 1.25rem;
        border-radius: 22px;
        background: rgba(255,255,255,0.74);
        border: 1px solid rgba(23, 63, 42, 0.08);
        box-shadow: 0 14px 30px rgba(23, 63, 42, 0.08);
        backdrop-filter: blur(10px);
        animation: appBoom 0.7s cubic-bezier(0.2, 0.9, 0.2, 1) both;
    }

    .app-brand {
        display: flex;
        flex-direction: column;
        gap: 0.15rem;
    }

    .app-kicker {
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--text-soft);
        font-weight: 700;
    }

    .app-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--text-strong);
    }

    .app-subtitle {
        color: var(--text-soft);
        font-size: 0.92rem;
    }

    .app-statusbar {
        display: flex;
        gap: 0.6rem;
        flex-wrap: wrap;
        justify-content: flex-end;
    }

    .app-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.48rem 0.8rem;
        border-radius: 999px;
        background: rgba(27, 94, 32, 0.08);
        color: var(--text-strong);
        font-size: 0.84rem;
        font-weight: 600;
        border: 1px solid rgba(23, 63, 42, 0.08);
    }

    .auth-shell {
        max-width: 520px;
        margin: 3rem auto 0 auto;
        padding: 2rem;
        border-radius: 28px;
        background: var(--surface-light);
        border: 1px solid rgba(23, 63, 42, 0.08);
        box-shadow: 0 24px 50px rgba(23, 63, 42, 0.12);
        position: relative;
        overflow: hidden;
        animation: authBoom 0.8s cubic-bezier(0.2, 0.9, 0.2, 1) both;
    }

    .auth-shell::after {
        content: "";
        position: absolute;
        width: 180px;
        height: 180px;
        right: -50px;
        top: -50px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(139,195,74,0.30) 0%, rgba(139,195,74,0.02) 72%);
        pointer-events: none;
        animation: pulseBurst 1.2s ease-out both;
    }

    .auth-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-strong);
        margin-bottom: 0.35rem;
    }

    .auth-copy {
        color: var(--text-soft);
        line-height: 1.6;
        margin-bottom: 1rem;
    }

    .hero-panel {
        padding: 2.2rem;
        border-radius: 30px;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #123524 0%, #1b5e20 52%, #8bc34a 100%);
        color: #f5fff0;
        box-shadow: 0 24px 60px rgba(18, 53, 36, 0.22);
        position: relative;
        overflow: hidden;
        animation: riseIn 0.7s ease both;
    }

    .hero-panel::after {
        content: "";
        position: absolute;
        right: 1.3rem;
        top: 1rem;
        font-size: 1.25rem;
        letter-spacing: 0.2rem;
        opacity: 0.26;
    }

    .hero-kicker {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.15);
        font-size: 0.78rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.9rem;
        color: var(--text-on-dark) !important;
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.15rem;
        line-height: 1;
        font-weight: 700;
        max-width: 12ch;
        margin-bottom: 0.85rem;
        color: var(--text-on-dark) !important;
    }

    .hero-copy {
        max-width: 58ch;
        color: var(--text-on-dark) !important;
        font-size: 1.02rem;
        line-height: 1.65;
    }

    .hero-copy strong {
        color: #fff7cf !important;
    }

    .section-label {
        display: inline-block;
        margin: 0.4rem 0 0.8rem 0;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        background: #dff3df;
        color: var(--text-strong);
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        box-shadow: 0 8px 20px rgba(46, 125, 50, 0.10);
    }

    .mini-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.78), rgba(230, 244, 232, 0.95));
        border: 1px solid rgba(23, 63, 42, 0.08);
        border-radius: 22px;
        padding: 1rem;
        box-shadow: 0 14px 34px rgba(23, 63, 42, 0.08);
        min-height: 140px;
        transition: transform 0.22s ease, box-shadow 0.22s ease;
        animation: riseIn 0.6s ease both;
    }

    .mini-card:nth-of-type(2) { animation-delay: 0.05s; }
    .mini-card:nth-of-type(3) { animation-delay: 0.1s; }
    .mini-card:nth-of-type(4) { animation-delay: 0.15s; }

    .mini-card.gold {
        background: linear-gradient(180deg, rgba(255,255,255,0.82), rgba(255, 244, 212, 0.96));
    }

    .mini-card.cream {
        background: linear-gradient(180deg, rgba(255,255,255,0.82), rgba(246, 236, 223, 0.96));
    }

    .mini-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-strong);
        margin-bottom: 0.45rem;
    }

    .mini-text {
        color: var(--text-soft);
        font-size: 0.95rem;
        line-height: 1.55;
    }

    .mini-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 18px 34px rgba(23, 63, 42, 0.12);
    }

    [data-testid="stMetric"] {
        background: var(--surface-light);
        border: 1px solid rgba(23, 63, 42, 0.08);
        padding: 0.75rem;
        border-radius: 20px;
        box-shadow: 0 14px 34px rgba(23, 63, 42, 0.08);
        animation: riseIn 0.5s ease both;
    }

    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
        color: var(--text-strong) !important;
    }

    [data-testid="stSidebar"] {
        background: var(--sidebar-bg);
    }

    [data-testid="stSidebar"] * {
        color: var(--text-on-dark);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
    }

    .sidebar-brand {
        padding: 1rem 1rem 1.1rem 1rem;
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(255,255,255,0.12), rgba(255,255,255,0.04));
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);
        margin-bottom: 0.9rem;
    }

    .sidebar-kicker {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        opacity: 0.8;
        margin-bottom: 0.35rem;
        color: var(--text-on-dark-soft) !important;
    }

    .sidebar-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.35rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
        color: var(--text-on-dark) !important;
    }

    .sidebar-copy {
        font-size: 0.9rem;
        line-height: 1.5;
        opacity: 0.9;
        color: var(--text-on-dark) !important;
    }

    .status-ribbon {
        padding: 0.9rem 1rem;
        border-radius: 18px;
        margin: 0.5rem 0 0.8rem 0;
        color: var(--text-strong);
        box-shadow: 0 14px 34px rgba(23, 63, 42, 0.08);
        border: 1px solid rgba(23, 63, 42, 0.08);
    }

    .status-ribbon.risk {
        background: linear-gradient(135deg, rgba(255,235,230,0.96), rgba(255,245,238,0.92));
    }

    .status-ribbon.ok {
        background: linear-gradient(135deg, rgba(229,244,229,0.96), rgba(246,255,244,0.92));
    }

    .status-ribbon.info {
        background: linear-gradient(135deg, rgba(235,246,255,0.96), rgba(246,251,255,0.92));
    }

    .ribbon-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
        margin-bottom: 0.28rem;
        color: var(--text-soft);
    }

    .ribbon-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .ribbon-text {
        font-size: 0.92rem;
        line-height: 1.5;
        color: var(--text-soft);
    }

    div.stButton > button {
        background: #1f6a2d;
        color: #ffffff !important;
        border-radius: 999px;
        padding: 0.7rem 1.3rem;
        border: none;
        font-weight: 800;
        letter-spacing: 0.01em;
        box-shadow: 0 12px 28px rgba(27, 94, 32, 0.20);
        transition: 0.25s ease;
        position: relative;
        overflow: hidden;
        text-shadow: none !important;
        opacity: 1 !important;
    }

    div.stButton > button:hover {
        background: #195825;
        transform: translateY(-1px);
    }

    div.stButton > button::after {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(120deg, transparent 20%, rgba(255,255,255,0.18) 50%, transparent 80%);
        transform: translateX(-120%);
        transition: transform 0.6s ease;
    }

    div.stButton > button:hover::after {
        transform: translateX(120%);
    }

    div.stButton > button p,
    div.stButton > button span,
    div.stButton > button div {
        color: #ffffff !important;
        opacity: 1 !important;
    }

    .stSelectbox div[data-baseweb="select"] > div,
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        color: var(--text-strong) !important;
        background: var(--surface-input) !important;
        border: 1px solid rgba(23, 63, 42, 0.12) !important;
    }

    .stExpander summary, .stExpander details {
        color: var(--text-strong) !important;
    }

    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid rgba(23, 63, 42, 0.08);
        border-radius: 24px;
        padding: 1rem 1rem 0.5rem 1rem;
        box-shadow: 0 14px 34px rgba(23, 63, 42, 0.08);
    }

    .stAlert {
        border-radius: 16px;
    }

    .stAlert [data-testid="stMarkdownContainer"] p {
        color: inherit !important;
    }

    [data-baseweb="notification"] {
        color: var(--text-main) !important;
    }

    [data-baseweb="notification"] [data-testid="stMarkdownContainer"] p,
    [data-baseweb="notification"] [data-testid="stMarkdownContainer"] li {
        color: var(--text-main) !important;
    }

    [data-testid="stSidebar"] .stRadio label {
        background: rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 0.55rem 0.75rem;
        transition: 0.2s ease;
        border: 1px solid rgba(255,255,255,0.08);
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.14);
        transform: translateX(2px);
    }

    [data-testid="stSidebar"] .stRadio label p,
    [data-testid="stSidebar"] .stRadio label span,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: var(--text-on-dark) !important;
        opacity: 1;
    }

    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
        color: var(--text-on-dark-soft) !important;
        font-weight: 600;
    }

    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="select"] > div > div {
        color: var(--text-on-dark) !important;
        background: var(--surface-sidebar-input) !important;
        border: 1px solid rgba(255,255,255,0.16) !important;
        border-radius: 14px !important;
        box-shadow: none !important;
        opacity: 1 !important;
        backdrop-filter: none !important;
        filter: none !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="select"] div,
    [data-testid="stSidebar"] input::placeholder {
        color: var(--text-on-dark) !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: var(--text-on-dark) !important;
        text-shadow: none !important;
        filter: none !important;
    }

    [data-testid="stSidebar"] svg {
        fill: var(--text-on-dark) !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] svg,
    [data-testid="stSidebar"] [data-baseweb="select"] path {
        color: var(--text-on-dark) !important;
        fill: var(--text-on-dark) !important;
        stroke: var(--text-on-dark) !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="select"] > div:hover,
    [data-testid="stSidebar"] [data-baseweb="select"] > div:focus,
    [data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within,
    [data-testid="stSidebar"] [data-baseweb="select"] > div[data-focus="true"] {
        background: #326c40 !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {
        border: 1px solid rgba(255,255,255,0.28) !important;
        box-shadow: 0 0 0 1px rgba(255,255,255,0.08) !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] input {
        color: var(--text-on-dark) !important;
        -webkit-text-fill-color: var(--text-on-dark) !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] {
        margin-bottom: 0.55rem;
    }

    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stNumberInput label {
        color: var(--text-on-dark-soft) !important;
    }

    .status-ribbon {
        padding: 1.05rem 1.1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        animation: riseIn 0.5s ease both;
    }

    .ribbon-title {
        color: var(--text-strong);
    }

    .ribbon-text {
        line-height: 1.6;
    }

    .status-ribbon:hover {
        transform: translateY(-2px);
        box-shadow: 0 18px 30px rgba(23, 63, 42, 0.12);
    }

    @keyframes riseIn {
        from {
            opacity: 0;
            transform: translateY(14px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes authBoom {
        0% {
            opacity: 0;
            transform: scale(0.92) translateY(18px);
        }
        65% {
            opacity: 1;
            transform: scale(1.02) translateY(0);
        }
        100% {
            opacity: 1;
            transform: scale(1) translateY(0);
        }
    }

    @keyframes appBoom {
        0% {
            opacity: 0;
            transform: scale(0.97) translateY(-10px);
        }
        70% {
            opacity: 1;
            transform: scale(1.01) translateY(0);
        }
        100% {
            opacity: 1;
            transform: scale(1) translateY(0);
        }
    }

    @keyframes pulseBurst {
        0% {
            opacity: 0;
            transform: scale(0.35);
        }
        50% {
            opacity: 1;
            transform: scale(1);
        }
        100% {
            opacity: 0.65;
            transform: scale(1.18);
        }
    }

    @keyframes pageFade {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .section-copy {
        color: var(--text-soft) !important;
        font-size: 1rem;
        max-width: 60ch;
        line-height: 1.65;
        margin-top: 0;
    }

    .page-shell {
        animation: pageFade 0.45s ease both;
    }

    [data-baseweb="tab-list"] {
        gap: 0.5rem;
        margin-bottom: 0.8rem;
    }

    [data-baseweb="tab"] {
        background: rgba(27, 94, 32, 0.08);
        border: 1px solid rgba(23, 63, 42, 0.08);
        border-radius: 999px;
        padding: 0.55rem 0.9rem;
        color: var(--text-strong) !important;
        font-weight: 700;
        transition: transform 0.18s ease, background 0.18s ease;
    }

    [data-baseweb="tab"]:hover {
        transform: translateY(-1px);
        background: rgba(27, 94, 32, 0.12);
    }

    [aria-selected="true"][data-baseweb="tab"] {
        background: #1f6a2d !important;
        color: #ffffff !important;
        border-color: #1f6a2d !important;
        box-shadow: 0 10px 24px rgba(27, 94, 32, 0.18);
    }

    [data-baseweb="tab-panel"] {
        animation: riseIn 0.35s ease both;
    }

    @media (max-width: 900px) {
        .app-topbar {
            flex-direction: column;
            align-items: flex-start;
        }

        .app-statusbar {
            justify-content: flex-start;
        }

        .hero-title {
            font-size: 2.35rem;
        }

        .hero-panel::after {
            font-size: 1rem;
            right: 0.8rem;
        }
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --text-strong: #eef8f0;
            --text-main: #d8e8dd;
            --text-soft: #a9c0b1;
            --text-on-dark: #f7fff3;
            --text-on-dark-soft: rgba(247,255,243,0.86);
            --surface-light: rgba(14, 27, 22, 0.88);
            --surface-input: rgba(20, 37, 30, 0.96);
            --surface-sidebar-input: #244d2f;
            --app-bg:
                radial-gradient(circle at top left, rgba(46, 125, 50, 0.18), transparent 24%),
                radial-gradient(circle at top right, rgba(255, 193, 7, 0.08), transparent 16%),
                linear-gradient(180deg, #08120e 0%, #0c1a14 54%, #13231c 100%);
            --sidebar-bg: linear-gradient(180deg, #0b1f15 0%, #123524 100%);
        }

        .stApp {
            color: var(--text-main);
        }

        .app-topbar {
            background: rgba(16, 30, 24, 0.88);
            border: 1px solid rgba(190, 220, 198, 0.08);
            box-shadow: 0 14px 30px rgba(0, 0, 0, 0.26);
        }

        .app-kicker,
        .app-subtitle,
        .app-chip {
            color: var(--text-main);
        }

        .app-title {
            color: var(--text-strong);
        }

        .app-chip {
            background: rgba(255,255,255,0.06);
            border-color: rgba(255,255,255,0.08);
        }

        [data-baseweb="tab"] {
            background: rgba(255,255,255,0.06);
            border-color: rgba(255,255,255,0.08);
            color: var(--text-main) !important;
        }

        [aria-selected="true"][data-baseweb="tab"] {
            background: #244d2f !important;
            border-color: #244d2f !important;
            color: #ffffff !important;
        }

        div.card,
        .mini-card,
        [data-testid="stMetric"],
        [data-testid="stForm"] {
            border: 1px solid rgba(190, 220, 198, 0.08);
            box-shadow: 0 14px 30px rgba(0, 0, 0, 0.26);
        }

        div.card,
        .mini-card,
        .mini-card.gold,
        .mini-card.cream,
        [data-testid="stMetric"],
        [data-testid="stForm"] {
            background: rgba(16, 30, 24, 0.9) !important;
        }

        .mini-title,
        .mini-text,
        .card p,
        .card li,
        .card label,
        .card span,
        .mini-card p,
        .mini-card li,
        .mini-card label,
        .mini-card span,
        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"],
        [data-testid="stMetric"] p,
        [data-testid="stMetric"] span,
        [data-testid="stMetric"] label {
            color: var(--text-main) !important;
        }

        .section-label {
            background: rgba(46, 125, 50, 0.18);
            color: #d8f1de;
            box-shadow: none;
        }

        .hero-panel {
            background: linear-gradient(135deg, #123524 0%, #1b5e20 52%, #4d8d2c 100%);
        }

        .status-ribbon.risk {
            background: linear-gradient(135deg, rgba(78, 26, 26, 0.94), rgba(58, 20, 20, 0.9));
        }

        .status-ribbon.ok {
            background: linear-gradient(135deg, rgba(20, 62, 36, 0.94), rgba(17, 49, 29, 0.9));
        }

        .status-ribbon.info {
            background: linear-gradient(135deg, rgba(18, 40, 56, 0.94), rgba(16, 33, 45, 0.9));
        }

        .ribbon-title,
        .ribbon-text,
        .ribbon-label {
            color: var(--text-main) !important;
        }

        .section-copy {
            color: var(--text-main) !important;
        }

        .stAlert [data-testid="stMarkdownContainer"] p,
        .stAlert [data-testid="stMarkdownContainer"] li {
            color: inherit !important;
        }

        [data-testid="stSidebar"] .stRadio label {
            background: rgba(255,255,255,0.06);
            border-color: rgba(255,255,255,0.08);
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Persistent Storage ---
init_db()

# --- Session State for Data Persistence (Functionality) ---
if 'regional_data' not in st.session_state:
    # Initial Mock Data
    data = {
        "Crop": ["Tomato", "Onion", "Beans", "Chili", "Millet", "Groundnut", "Rice"],
        "Farmers_Count": [96, 54, 28, 18, 26, 21, 72],
        "Demand_Index": [44, 68, 82, 88, 74, 66, 58]
    }
    st.session_state.regional_data = pd.DataFrame(data)

if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False

if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

if 'user_role' not in st.session_state:
    st.session_state.user_role = ""

if 'pred_result' not in st.session_state:
    st.session_state.pred_result = None

if 'planner_results' not in st.session_state:
    st.session_state.planner_results = None

if 'sim_result' not in st.session_state:
    st.session_state.sim_result = None

if 'treatment_notice' not in st.session_state:
    st.session_state.treatment_notice = ""

if 'location_recommendation' not in st.session_state:
    st.session_state.location_recommendation = None

def render_feature_card(title, text, variant=""):
    st.markdown(
        f"""
        <div class="mini-card {variant}">
            <div class="mini-title">{title}</div>
            <div class="mini-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_intro(kicker, title, text):
    st.markdown(
        f"""
        <div class="section-label">{kicker}</div>
        <h1 style="margin-top:0.2rem; margin-bottom:0.4rem;">{title}</h1>
        <p class="section-copy">{text}</p>
        """,
        unsafe_allow_html=True,
    )


def render_app_header(current_page, region, farmer_profile):
    st.markdown(
        f"""
        <div class="app-topbar">
            <div class="app-brand">
                <div class="app-kicker">Agricultural Intelligence Platform</div>
                <div class="app-title">Smart Agri Platform</div>
                <div class="app-subtitle">{current_page} · {region} · {farmer_profile}</div>
            </div>
            <div class="app-statusbar">
                <div class="app-chip">Region: {region}</div>
                <div class="app-chip">Profile: {farmer_profile}</div>
                <div class="app-chip">Live planning mode</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sign_in():
    st.markdown(
        """
        <div class="auth-shell">
            <div class="auth-title">Sign in to Smart Agri Platform</div>
            <div class="auth-copy">
                Access crop planning, agronomy simulation, market forecasting, and regional coordination from one session-aware workspace.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("sign_in_form"):
        user_name = st.text_input("Name", placeholder="Enter your name")
        user_role = st.selectbox("Role", ["Farmer", "Agronomist", "Researcher", "Student"])
        access_code = st.text_input("Access Code", type="password", placeholder="Use demo123")
        submitted = st.form_submit_button("Sign In")
        if submitted:
            if access_code == "demo123" and user_name.strip():
                st.session_state.is_authenticated = True
                st.session_state.user_role = user_role
                st.session_state.user_name = f"{user_name.strip()} ({user_role})"
                st.rerun()
            else:
                st.error("Enter a name and use access code `demo123`.")


def polish_plotly(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        font=dict(family="Manrope, sans-serif", color="#355846"),
        title_font=dict(family="Space Grotesk, sans-serif", size=20, color="#173f2a"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="#173f2a", font=dict(color="#f7fff3")),
        hovermode="x unified",
        transition=dict(duration=450, easing="cubic-in-out"),
    )
    return fig


def render_status_ribbon(label, title, text, tone="info"):
    st.markdown(
        f"""
        <div class="status-ribbon {tone}">
            <div class="ribbon-label">{label}</div>
            <div class="ribbon-title">{title}</div>
            <div class="ribbon-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_service_status_panel():
    status = get_service_status()
    st.sidebar.markdown("### Service Status")
    for service in status.values():
        state = "Live" if service["enabled"] else "Fallback"
        st.sidebar.caption(f"{service['label']}: {state}")
        if service["enabled"]:
            st.sidebar.success(service["detail"], icon="✅")
        else:
            st.sidebar.info(service["detail"], icon="ℹ️")

# --- Helper Functions (Logic) ---

PRICE_BASE = {"Tomato": 52, "Onion": 41, "Millet": 32, "Groundnut": 63, "Chili": 118, "Beans": 74, "Rice": 36}
SEASON_MULTIPLIERS = {
    "Winter (Rabi)": {"Tomato": 1.16, "Onion": 1.08, "Millet": 0.96, "Groundnut": 1.03, "Chili": 1.02, "Beans": 1.05, "Rice": 0.95},
    "Summer (Zaid)": {"Tomato": 1.28, "Onion": 1.14, "Millet": 1.03, "Groundnut": 0.98, "Chili": 0.92, "Beans": 1.01, "Rice": 0.88},
    "Monsoon (Kharif)": {"Tomato": 0.82, "Onion": 0.94, "Millet": 1.14, "Groundnut": 1.08, "Chili": 1.00, "Beans": 1.09, "Rice": 1.12},
}
REGION_MULTIPLIERS = {
    "Central Valley": 1.00,
    "North Belt": 1.04,
    "South Plains": 0.98,
    "Coastal Delta": 1.02,
}
REGION_PROFILES = {
    "Central Valley": {"weather_shift": 1, "humidity_shift": 2, "focus": "vegetable belt", "support": "irrigation and market-linkage"},
    "North Belt": {"weather_shift": -2, "humidity_shift": -6, "focus": "storage-led staples", "support": "warehouse and insurance"},
    "South Plains": {"weather_shift": 2, "humidity_shift": 4, "focus": "oilseeds and pulses", "support": "water-efficiency and credit"},
    "Coastal Delta": {"weather_shift": 0, "humidity_shift": 8, "focus": "rice and climate-resilient seed", "support": "flood resilience and seed access"},
}
CROP_COLORS = {
    "Tomato": "#ef5350",
    "Onion": "#8d6e63",
    "Beans": "#43a047",
    "Chili": "#fb8c00",
    "Millet": "#c0a24b",
    "Groundnut": "#6d4c41",
    "Rice": "#26a69a",
}
FARMER_PROFILES = {
    "Smallholder / Conservative": {
        "scale_factor": 0.82,
        "risk_bias": -6,
        "budget_bias": 0.9,
        "support_focus": "credit access and crop insurance",
        "planner_preference": {"Millet", "Beans", "Groundnut"},
    },
    "Growing / Balanced": {
        "scale_factor": 1.0,
        "risk_bias": 0,
        "budget_bias": 1.0,
        "support_focus": "market linkage and irrigation support",
        "planner_preference": {"Onion", "Beans", "Rice"},
    },
    "Commercial / Aggressive": {
        "scale_factor": 1.18,
        "risk_bias": 5,
        "budget_bias": 1.15,
        "support_focus": "storage, logistics, and premium market access",
        "planner_preference": {"Tomato", "Chili", "Onion"},
    },
}
WEATHER_BY_MONTH = {
    1: {"temp": 23, "humidity": 58, "rainfall": "Low", "forecast": "Cool and Dry"},
    2: {"temp": 25, "humidity": 60, "rainfall": "Low", "forecast": "Clear Intervals"},
    3: {"temp": 29, "humidity": 64, "rainfall": "Moderate", "forecast": "Warm with Passing Clouds"},
    4: {"temp": 32, "humidity": 68, "rainfall": "Moderate", "forecast": "Hot and Breezy"},
    5: {"temp": 34, "humidity": 72, "rainfall": "Moderate", "forecast": "Pre-Monsoon Build-up"},
    6: {"temp": 31, "humidity": 80, "rainfall": "High", "forecast": "Monsoon Onset"},
    7: {"temp": 29, "humidity": 86, "rainfall": "High", "forecast": "Wet Conditions"},
    8: {"temp": 28, "humidity": 88, "rainfall": "High", "forecast": "Cloudy and Humid"},
    9: {"temp": 29, "humidity": 84, "rainfall": "High", "forecast": "Intermittent Showers"},
    10: {"temp": 28, "humidity": 76, "rainfall": "Moderate", "forecast": "Clearing Conditions"},
    11: {"temp": 26, "humidity": 66, "rainfall": "Low", "forecast": "Drying Trend"},
    12: {"temp": 24, "humidity": 60, "rainfall": "Low", "forecast": "Cool and Stable"},
}
IMPLEMENTED_MODULES = [
    ("Field Sensing", "Soil moisture, pH, NPK proxy logic, temperature, and humidity are modeled as live inputs for crop planning."),
    ("AI Recommendation", "The prototype combines soil suitability, seasonal conditions, region profile, and farmer risk posture."),
    ("Market Forecasting", "Crop prices are estimated from seasonal multipliers, regional factors, and demand pressure."),
    ("Decision Dashboard", "Farmers receive crop suggestions, scenario analysis, collaboration alerts, and support pathways."),
]
PAGE_OPTIONS = [
    "Home Dashboard",
    "Price Prediction",
    "Collaboration Network",
    "AI Agronomist",
    "Crop Planner",
    "Financial Support",
]
ARCHITECTURE_FLOW = [
    "Field Sensors / Farm Inputs",
    "IoT Gateway / Data Capture Layer",
    "Cloud Database / Session Store",
    "AI Decision Models",
    "Recommendation Engine",
    "Farmer Dashboard",
]
CHEMISTRY_SIGNALS = [
    ("Nitrogen status", "Supports fertilizer recommendation and crop suitability decisions."),
    ("Soil moisture", "Protects root oxygen availability and helps irrigation timing."),
    ("Soil pH", "Improves nutrient uptake decisions and crop matching."),
    ("Temperature and humidity", "Shape crop stress, disease pressure, and expected growth."),
    ("CO2 / respiration proxy", "Represents soil biological activity and overall soil health interpretation."),
]
PROJECT_COSTS = [
    ("Soil moisture sensor", "200-400"),
    ("Soil pH sensor", "1500-3000"),
    ("Temperature / humidity sensor", "200-500"),
    ("NPK sensor", "4000-8000"),
    ("CO2 sensor", "1500-4000"),
    ("ESP32 / controller layer", "800-1500"),
    ("Relay + irrigation actuator", "1200-2500"),
    ("Cloud / dashboard / ML stack", "0-2000"),
]
RESEARCH_REFERENCES = [
    "IoT-enabled soil nutrient analysis and crop recommendation systems for precision agriculture.",
    "AI crop recommendation using nitrogen, phosphorus, potassium, pH, rainfall, and humidity features.",
    "Sensor-based irrigation and crop advisory systems using real-time field monitoring.",
    "Crop price prediction models using weather, historical price, and regional demand signals.",
]


def build_price_history(crop, season, region):
    mandi = fetch_mandi_prices(crop, region)
    history = mandi["recent_prices"]
    if len(history) < 7:
        anchor = mandi["average_price"]
        history = [round(anchor * (0.96 + idx * 0.003), 2) for idx in range(30)]
    drift_target = round(float(np.mean(history[-5:])) * SEASON_MULTIPLIERS[season][crop] * 0.01, 2)
    forecast = [round(history[-1] + drift_target * step, 2) for step in range(1, 8)]
    return history, forecast


def get_price_prediction(crop, season, region, farmer_profile):
    demand_lookup = st.session_state.regional_data.set_index("Crop")["Demand_Index"].to_dict()
    weather = get_real_weather(region)
    prediction = predict_crop_price(crop, season, region, weather, demand_lookup.get(crop, 65))
    trend_map = {
        "Rising": "📈 Rising",
        "Falling": "📉 Falling",
        "Stable": "➡️ Stable",
    }
    return prediction["predicted_price"], prediction["confidence_score"], trend_map[prediction["trend"]]


def get_weather_snapshot(region):
    weather = get_real_weather(region)
    return {
        "temp": weather["temperature"],
        "humidity": weather["humidity"],
        "forecast": weather["description"],
        "rainfall": f"{weather['rainfall_probability']}% rain probability",
        "source": weather["source"],
    }


def diagnose_crop_image(image):
    diagnosis = detect_plant_disease(image)
    return diagnosis["disease_name"], diagnosis["probability"]


def get_crop_plan(soil, water, budget, farmer_profile):
    location_hint = st.session_state.get("location_recommendation")
    plans = service_crop_plan(soil, water, budget, farmer_profile, location_hint=location_hint)
    return [(item["crop"], item["risk"], item["profit"]) for item in plans]


def get_market_story(crop):
    return service_market_story(crop)


def get_forecast_insights(crop, region, trend):
    region_notes = {
        "Central Valley": "Transport access is relatively strong, so timing matters more than reach.",
        "North Belt": "Storage and delayed selling can improve outcomes when prices are soft.",
        "South Plains": "Water efficiency and input discipline matter more than chasing peak output.",
        "Coastal Delta": "Resilience planning is critical because weather swings can erase margin quickly.",
    }
    action = {
        "📉 Falling": "Reduce exposure, split acreage, and keep one safer fallback crop.",
        "➡️ Stable": "Hold a balanced plan and monitor demand changes before scaling.",
        "📈 Rising": "This is a stronger window, but quality and timing still decide realized price.",
    }
    return {
        "market_note": get_market_story(crop),
        "region_note": region_notes.get(region, "Use local infrastructure strength to guide selling strategy."),
        "action_note": action.get(trend, "Stay flexible and review the next market signal."),
    }


def get_collaboration_recommendation(df):
    return service_collaboration_recommendation(df)


def get_operational_scenarios(crop, region, trend, farmer_profile, base_price):
    profile = FARMER_PROFILES[farmer_profile]
    region_factor = REGION_MULTIPLIERS.get(region, 1.0)
    downside = round(base_price * (0.9 if trend != "📉 Falling" else 0.82), 2)
    base = round(base_price, 2)
    upside = round(base_price * (1.08 + (region_factor - 1) * 0.4 + profile["risk_bias"] * 0.003), 2)
    return [
        ("Downside", f"INR {downside:.0f}/qtl", "Heavy arrivals or weaker buyer turnout compress realization."),
        ("Base Case", f"INR {base:.0f}/qtl", "Expected realization if current supply and transport conditions hold."),
        ("Upside", f"INR {upside:.0f}/qtl", "Quality retention and tighter arrivals improve negotiation range."),
    ]


def render_info_list(items, columns=2):
    cols = st.columns(columns)
    for index, (title, text) in enumerate(items):
        with cols[index % columns]:
            render_feature_card(title, text)


def simulate_agronomy_scenario(soil_moisture, soil_ph, nitrogen_level, temperature, humidity, region, farmer_profile):
    scenario = service_simulate_agronomy_scenario(
        soil_moisture,
        soil_ph,
        nitrogen_level,
        temperature,
        humidity,
        region,
        farmer_profile,
        location_hint=st.session_state.get("location_recommendation"),
    )
    price, _, _ = get_price_prediction(
        scenario["crop"],
        "Monsoon (Kharif)" if humidity > 70 else "Winter (Rabi)",
        region,
        farmer_profile,
    )
    scenario["price"] = price
    return scenario


def render_crop_plan_results(plan_rows, planner_budget, profile_config):
    st.subheader("Recommended Crops")
    for plan in plan_rows:
        crop = plan["crop"]
        risk = plan["risk"]
        profit = plan["profit"]
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.markdown(f"### {crop}")
        c2.metric("Risk Level", risk)
        c3.metric("Profit Potential", profit)

        with st.expander(f"View Detailed Plan for {crop}"):
            estimated_cost = int((planner_budget * profile_config["budget_bias"]) * (0.32 if crop in {"Millet", "Beans"} else 0.48))
            expected_yield = {"Millet": 18, "Groundnut": 16, "Rice": 28, "Beans": 14, "Tomato": 22, "Onion": 24, "Chili": 11}.get(crop, 17)
            climate_fit = {"Millet": 91, "Groundnut": 86, "Rice": 84, "Beans": 88, "Tomato": 79, "Onion": 82, "Chili": 80}.get(crop, 78)
            st.write(f"**Estimated Cost:** INR {estimated_cost}")
            st.write(f"**Expected Yield:** {expected_yield} quintals")
            st.write(f"**Water Strategy:** {plan['water_strategy']}")
            st.write(f"**Why recommended:** {' '.join(plan['reasons'])}")
            st.write(f"**Fertilizer logic:** {plan['fertilizer_plan']}")
            st.progress(climate_fit / 100, text=f"Climate fit score: {climate_fit}%")
            growth_df = pd.DataFrame({
                "Stage": ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6"],
                "Vigor": np.clip(np.cumsum(np.array([12, 14, 16, 18, 15, 11])) + (3 if crop in {"Rice", "Tomato"} else 0), 0, 100)
            })
            growth_fig = px.area(growth_df, x="Stage", y="Vigor")
            growth_fig = polish_plotly(growth_fig)
            growth_fig.update_traces(
                line_color=CROP_COLORS.get(crop, "#2e7d32"),
                fillcolor="rgba(46,125,50,0.18)",
                hovertemplate="%{x}<br>Growth index: %{y}<extra></extra>",
            )
            growth_fig.update_layout(title=f"{crop} establishment curve", showlegend=False)
            growth_fig.update_xaxes(title=None, showgrid=False)
            growth_fig.update_yaxes(title="Growth index", gridcolor="rgba(23,63,42,0.08)")
            st.plotly_chart(growth_fig, width="stretch")

# --- Sidebar Navigation ---
if not st.session_state.is_authenticated:
    render_sign_in()
    st.stop()

current_time = datetime.now().strftime("%d %b %Y · %I:%M %p")
st.sidebar.markdown(
    f"""
    <div class="sidebar-brand">
        <div class="sidebar-kicker">Agricultural Intelligence</div>
        <div class="sidebar-title">Smart Agri Platform</div>
        <div class="sidebar-copy">Decision support for pricing, crop planning, regional coordination, and resilience.</div>
        <div class="sidebar-copy" style="margin-top:0.45rem;">Signed in as {st.session_state.user_name}</div>
        <div class="sidebar-copy" style="margin-top:0.55rem; opacity:0.78;">{current_time}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

render_service_status_panel()

if st.sidebar.button("Sign Out"):
    st.session_state.is_authenticated = False
    st.session_state.user_name = ""
    st.session_state.user_role = ""
    st.session_state.pred_result = None
    st.session_state.planner_results = None
    st.session_state.sim_result = None
    st.session_state.treatment_notice = ""
    st.session_state.location_recommendation = None
    st.rerun()

selected_region = st.sidebar.selectbox(
    "Region Focus",
    ["Central Valley", "North Belt", "South Plains", "Coastal Delta"],
    index=0,
)
regional_df = build_collaboration_frame(st.session_state.regional_data, selected_region)
region_profile = REGION_PROFILES[selected_region]
farmer_profile = st.sidebar.selectbox(
    "Farmer Profile",
    ["Smallholder / Conservative", "Growing / Balanced", "Commercial / Aggressive"],
    index=1,
)
profile_config = FARMER_PROFILES[farmer_profile]

profile_signature = (st.session_state.user_name, st.session_state.user_role, selected_region, farmer_profile)
if st.session_state.get("saved_profile_signature") != profile_signature:
    save_farmer_profile(st.session_state.user_name, st.session_state.user_role, selected_region, farmer_profile)
    st.session_state.saved_profile_signature = profile_signature

page = st.sidebar.radio(
    "Navigation",
    PAGE_OPTIONS,
    label_visibility="collapsed"
)

# --- PAGES ---

render_app_header(page, selected_region, farmer_profile)
st.markdown('<div class="page-shell">', unsafe_allow_html=True)

if page == "Home Dashboard":
    weather = get_weather_snapshot(selected_region)
    st.markdown(
        f"""
        <div class="hero-panel">
            <div class="hero-kicker">Smart Agri Command Center</div>
            <div class="hero-title">Agricultural planning with clearer decision support.</div>
            <div class="hero-copy">
                Forecast prices, monitor regional supply pressure, review crop health,
                and evaluate resilience options from a single operating interface. Current focus:
                <strong>{selected_region}</strong>, where the dominant planning theme is {region_profile["focus"]}.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-label">Live Overview</div>', unsafe_allow_html=True)

    # Top Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Temperature", value=f"{weather['temp']}°C", delta=weather["forecast"])
    with col2:
        st.metric(label="Humidity", value=f"{weather['humidity']}%", delta=weather["rainfall"])
    with col3:
        st.metric(label="Active Farmers", value=f"{int(regional_df['Farmers_Count'].sum())}", delta="Regional network")
    with col4:
        crowded = int((regional_df["Farmers_Count"] > 70).sum())
        st.metric(label="Market Alerts", value=f"{crowded} Active", delta="Supply watch")

    render_status_ribbon(
        "Regional Lens",
        f"{selected_region} focus area",
        f"This zone currently emphasizes {region_profile['focus']} with stronger need for {region_profile['support']} support.",
        "info",
    )
    render_status_ribbon(
        "Farmer Mode",
        farmer_profile,
        f"This profile prioritizes {profile_config['support_focus']} and shifts planning toward a {('safer' if profile_config['risk_bias'] < 0 else 'bolder' if profile_config['risk_bias'] > 0 else 'balanced')} strategy.",
        "ok" if profile_config["risk_bias"] <= 0 else "info",
    )
    st.caption(f"Weather source: {weather['source']}")

    st.markdown('<div class="section-label">Core Capabilities</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        render_feature_card("Predictive Pricing", "Spot falling markets early and adjust crops before losses compound.")
    with f2:
        render_feature_card("Coordination Network", "Compare your planting plans with regional activity and demand pressure.", "gold")
    with f3:
        render_feature_card("Crop Intelligence", "Blend agronomy support, diagnostics, and resilience tools in one place.", "cream")

    st.markdown('<div class="section-label">Implemented System</div>', unsafe_allow_html=True)
    render_info_list(IMPLEMENTED_MODULES, columns=2)

    st.markdown('<div class="section-label">Architecture Flow</div>', unsafe_allow_html=True)
    flow_cols = st.columns(len(ARCHITECTURE_FLOW))
    for idx, step in enumerate(ARCHITECTURE_FLOW):
        with flow_cols[idx]:
            st.markdown(
                f"""
                <div class="mini-card">
                    <div class="mini-title">{idx + 1}. {step}</div>
                    <div class="mini-text">Connected stage in the implemented prototype workflow.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Charts Row
    chart_col1, chart_col2 = st.columns([2, 1])
    
    with chart_col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Regional Crop Distribution")
        st.caption("See where planting concentration is building across the active crop mix.")
        df = st.session_state.regional_data
        fig = px.bar(
            df,
            x='Crop',
            y='Farmers_Count',
            color='Crop',
            color_discrete_map=CROP_COLORS,
            text_auto=True,
        )
        fig.update_traces(
            marker_line_width=0,
            textfont_size=12,
            hovertemplate="<b>%{x}</b><br>Planned farmers: %{y}<extra></extra>",
        )
        fig = polish_plotly(fig)
        fig.update_layout(showlegend=False)
        fig.update_xaxes(title=None, showgrid=False)
        fig.update_yaxes(title="Farmers", gridcolor="rgba(23,63,42,0.08)")
        fig.add_annotation(
            x=df.loc[df["Farmers_Count"].idxmax(), "Crop"],
            y=df["Farmers_Count"].max(),
            text="Most crowded",
            showarrow=True,
            arrowhead=2,
            ay=-40,
            bgcolor="rgba(255,255,255,0.85)",
        )
        st.plotly_chart(fig, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with chart_col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Market Demand vs Supply")
        st.caption("Upper-left is healthy. Lower-right signals oversupply risk and weaker demand support.")
        
        # Scatter Plot for Demand vs Supply logic
        fig2 = px.scatter(
            df,
            x='Farmers_Count',
            y='Demand_Index',
            text='Crop',
            size='Demand_Index',
            size_max=24,
            color='Crop',
            color_discrete_map=CROP_COLORS,
        )
        fig2.update_traces(textposition='top center', marker=dict(size=18, line=dict(width=1, color="white")))
        fig2.add_shape(type="line", x0=0, y0=50, x1=130, y1=50, line=dict(color="Red", dash="dash"))
        fig2.add_shape(type="rect", x0=70, y0=0, x1=130, y1=50, line=dict(width=0), fillcolor="rgba(239,83,80,0.08)")
        fig2.add_shape(type="rect", x0=0, y0=70, x1=60, y1=100, line=dict(width=0), fillcolor="rgba(67,160,71,0.08)")
        fig2 = polish_plotly(fig2)
        fig2.update_layout(title="Supply Pressure Map", showlegend=False)
        fig2.update_xaxes(title="Planned Farmers", gridcolor="rgba(23,63,42,0.08)")
        fig2.update_yaxes(title="Demand Index", gridcolor="rgba(23,63,42,0.08)")
        fig2.add_annotation(x=98, y=22, text="Risk zone", showarrow=False, font=dict(color="#c62828"))
        fig2.add_annotation(x=26, y=88, text="Opportunity zone", showarrow=False, font=dict(color="#2e7d32"))
        st.plotly_chart(fig2, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "Price Prediction":
    render_section_intro(
        "Forecast Engine",
        "Price Forecasting",
        "Use seasonal signals, crop behavior, and demand pressure to estimate market direction before allocating acreage."
    )

    s1, s2, s3 = st.columns(3)
    with s1:
        render_feature_card("Fast Scenario Checks", "Switch crops and seasons instantly to compare likely outcomes.")
    with s2:
        render_feature_card("Confidence Layer", "Understand whether the prediction is firm, soft, or volatile.", "gold")
    with s3:
        render_feature_card("Decision Support", "Surface warnings early when price drop risk starts to build.", "cream")
    
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Input Parameters")
        st.caption("Create a forecast snapshot for one crop-season combination.")
        crop = st.selectbox("Select Crop", ["Tomato", "Onion", "Millet", "Groundnut", "Chili", "Beans", "Rice"])
        season = st.select_slider("Select Season", options=["Winter (Rabi)", "Summer (Zaid)", "Monsoon (Kharif)"])
        region = st.selectbox("Region", ["Central Valley", "North Belt", "South Plains", "Coastal Delta"], index=["Central Valley", "North Belt", "South Plains", "Coastal Delta"].index(selected_region))
        
        if st.button("Run Prediction Model"):
            with st.spinner('Processing mandi history and weather signals...'):
                time.sleep(0.6)
                demand_lookup = st.session_state.regional_data.set_index("Crop")["Demand_Index"].to_dict()
                market_weather = get_real_weather(region)
                prediction = predict_crop_price(crop, season, region, market_weather, demand_lookup.get(crop, 65))
                trend_map = {
                    "Rising": "📈 Rising",
                    "Falling": "📉 Falling",
                    "Stable": "➡️ Stable",
                }
                st.session_state.pred_result = {
                    "price": prediction["predicted_price"],
                    "conf": prediction["confidence_score"],
                    "trend": trend_map[prediction["trend"]],
                    "crop": crop,
                    "season": season,
                    "region": region,
                    "farmer_profile": farmer_profile,
                    "source": prediction["source"],
                    "model_used": prediction["model_used"],
                    "explanation": prediction["explanation"],
                    "historical_prices": prediction["historical_prices"],
                    "average_price": prediction["average_price"],
                    "weather": market_weather,
                }
                save_prediction(
                    st.session_state.user_name,
                    crop,
                    season,
                    region,
                    prediction["predicted_price"],
                    prediction["confidence_score"],
                    trend_map[prediction["trend"]],
                    prediction["explanation"]["recommendation_reason"],
                    prediction,
                )

    with col2:
        if st.session_state.pred_result:
            res = st.session_state.pred_result
            st.subheader(f"Forecast: {res['crop']}")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Predicted Price", f"INR {res['price']:.0f}", "Per quintal")
            m2.metric("Confidence", f"{res['conf']}%")
            m3.metric("Trend", res['trend'])
            insights = get_forecast_insights(res['crop'], res['region'], res['trend'])
            st.caption(insights["market_note"])
            st.caption(f"Data source: {res['source']} | Model: {res['model_used']}")
            
            # Warning Logic
            if res['trend'] == "📉 Falling":
                render_status_ribbon(
                    "Risk Signal",
                    "Price weakness detected",
                    "Current seasonal pressure suggests a softer selling window. Diversification or staggered planting is safer.",
                    "risk",
                )
                st.error("⚠️ **High Risk:** Market prices are predicted to drop. Consider diversifying crops.")
            else:
                render_status_ribbon(
                    "Market Signal",
                    "Outlook remains constructive",
                    "The current scenario indicates stable to improving pricing conditions for this crop-season mix.",
                    "ok",
                )
                st.success("✅ **Favorable Outlook:** Prices are stable or rising.")

            i1, i2 = st.columns(2)
            with i1:
                render_status_ribbon("Regional Read", res['region'], insights["region_note"], "info")
            with i2:
                render_status_ribbon("Action Cue", "Suggested move", insights["action_note"], "ok" if res["trend"] != "📉 Falling" else "risk")
            profile_focus = FARMER_PROFILES[res["farmer_profile"]]["support_focus"]
            st.caption(f"Profile influence: {res['farmer_profile']} mode emphasizes {profile_focus}.")
            render_status_ribbon("Why this crop outlook", "Price trend explanation", res["explanation"]["price_trend"], "info")
            render_status_ribbon("Environmental reasoning", "Weather-driven market context", res["explanation"]["environmental_reasoning"], "info")
            render_status_ribbon("Recommendation reasoning", "Why the model leaned this way", res["explanation"]["recommendation_reason"], "ok" if res["trend"] != "📉 Falling" else "risk")

            st.markdown('<div class="section-label">Operational Scenarios</div>', unsafe_allow_html=True)
            scenario_cols = st.columns(3)
            for col, (label, value, copy) in zip(
                scenario_cols,
                get_operational_scenarios(res["crop"], res["region"], res["trend"], res["farmer_profile"], res["price"]),
            ):
                with col:
                    render_feature_card(label, f"{value}\n\n{copy}")
            
            # Mock Historical Trend Chart
            days = pd.date_range(end=pd.Timestamp.today().normalize(), periods=30)
            hist_prices, future_prices = build_price_history(res['crop'], res['season'], res['region'])
            
            fig = go.Figure()
            crop_color = CROP_COLORS.get(res['crop'], '#1a5c38')
            fig.add_trace(go.Scatter(
                x=days,
                y=hist_prices,
                name="Historical",
                mode="lines+markers",
                line=dict(color=crop_color, width=3),
                marker=dict(size=5, color=crop_color),
                fill='tozeroy',
                fillcolor='rgba(46,125,50,0.08)',
                hovertemplate="Date: %{x|%d %b}<br>Price: INR %{y}<extra></extra>",
            ))
            fig.add_trace(go.Scatter(
                x=pd.date_range(days[-1] + pd.Timedelta(days=1), periods=7),
                y=future_prices,
                name="Forecast",
                mode="lines+markers",
                line=dict(color='#f59e0b', dash='dot', width=3),
                marker=dict(size=6, color='#f59e0b'),
                hovertemplate="Forecast date: %{x|%d %b}<br>Expected: INR %{y}<extra></extra>",
            ))
            fig = polish_plotly(fig)
            fig.update_layout(title="30-Day Price Trend & 7-Day Forecast")
            fig.update_xaxes(title=None, gridcolor="rgba(23,63,42,0.08)")
            fig.update_yaxes(title="Price / Quintal", gridcolor="rgba(23,63,42,0.08)")
            fig.add_hline(y=res["price"], line_dash="dash", line_color="rgba(245,158,11,0.65)")
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("👈 Input parameters and click 'Run Prediction' to see analysis.")
    
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Collaboration Network":
    render_section_intro(
        "Regional Intelligence",
        "Regional Collaboration Network",
        f"Make planting decisions with visibility into what nearby farmers are already planning so supply and demand stay more balanced across {selected_region}."
    )
    
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    # Form to add data
    with st.form("collaboration_form"):
        st.subheader("📝 Register Your Planting Plan")
        c1, c2 = st.columns(2)
        user_crop = c1.selectbox("Your Crop", ["Tomato", "Onion", "Beans", "Chili", "Millet", "Rice"])
        user_acre = c2.number_input("Acreage", min_value=1, max_value=100)
        
        submitted = st.form_submit_button("Submit Plan to Network")
        
        if submitted:
            # Update the session state dataframe (Functional Logic)
            current_data = st.session_state.regional_data
            # Find index
            idx = current_data.index[current_data['Crop'] == user_crop].tolist()
            if idx:
                current_data.at[idx[0], 'Farmers_Count'] += max(1, int(user_acre / 8))
                st.session_state.regional_data = current_data
                save_collaboration_submission(st.session_state.user_name, selected_region, user_crop, float(user_acre))
                st.success(f"✅ Plan registered! You are now part of the {user_crop} network.")
    
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Buyer Marketplace")
    st.caption("Filter active buyers by crop to see who is currently paying in the market.")
    buyer_crop = st.selectbox(
        "Filter Buyers by Crop",
        ["All", "Tomato", "Onion", "Beans", "Chili", "Millet", "Groundnut", "Rice"],
        key="buyer_crop_filter",
    )
    buyers_df = list_buyers(buyer_crop)
    st.dataframe(buyers_df, width="stretch", hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Visualizations
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Regional Crop Mix")
    st.caption("Shared planting patterns help expose where a community may be crowding into the same crop.")
    
    df = regional_df
    
    # Gauge Chart for Tomato Example
    colA, colB = st.columns([2, 1])
    
    with colA:
        fig = px.pie(df, values='Farmers_Count', names='Crop', title='Current Regional Crop Distribution', hole=0.4, color='Crop', color_discrete_map=CROP_COLORS)
        fig = polish_plotly(fig)
        fig.update_traces(textinfo="percent+label", pull=[0.08 if c == get_collaboration_recommendation(df) else 0 for c in df["Crop"]])
        fig.update_layout(title="Current Regional Crop Mix", showlegend=True)
        st.plotly_chart(fig, width="stretch")
        
    with colB:
        suggested_crop = get_collaboration_recommendation(df)
        render_status_ribbon(
            "Network Signal",
            "System recommendation",
            f"Use the {selected_region} crop mix to avoid crowded crops and move toward demand-supported options.",
            "info",
        )
        # Simple Logic for Recommendation
        over_supply = df[df['Farmers_Count'] > 50]
        if not over_supply.empty:
            for idx, row in over_supply.iterrows():
                render_status_ribbon(
                    "Oversupply Alert",
                    f"{row['Crop']} is crowded",
                    f"{row['Farmers_Count']} farmers are already leaning into this crop, which increases crash risk.",
                    "risk",
                )
                st.warning(f"⚠️ **{row['Crop']}** is over-planted ({row['Farmers_Count']} farmers). Price crash risk HIGH.")
        
        under_supply = df[df['Demand_Index'] > 80]
        if not under_supply.empty:
            render_status_ribbon(
                "Opportunity",
                "Demand-led openings found",
                "Some crops have stronger demand support than current planting activity. Those are better diversification targets.",
                "ok",
            )
            st.success("🚀 **Opportunity Found**:")
            for idx, row in under_supply.iterrows():
                st.write(f"Consider **{row['Crop']}**: High demand, low supply.")
        st.caption(f"Best diversification pick right now: {suggested_crop}")
        tomato_count = int(df.loc[df["Crop"] == "Tomato", "Farmers_Count"].iloc[0]) if "Tomato" in df["Crop"].values else 0
        render_status_ribbon(
            "Pressure Test",
            "If tomato planting expands further",
            f"If tomato participation moves from {tomato_count} to {tomato_count + 10} farmers, the system should expect a sharper discount window at harvest.",
            "risk" if tomato_count > 70 else "info",
        )

    st.markdown("</div>", unsafe_allow_html=True)

elif page == "AI Agronomist":
    render_section_intro(
        "Crop Diagnostics",
        "AI Agronomist",
        "Upload a crop image to receive a first-pass health assessment, confidence score, and treatment guidance."
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["System Inputs", "Agricultural Chemistry", "Automation Logic", "Scenario Simulator", "Voice Assistant"])
    with tab1:
        render_info_list(
            [
                ("Soil moisture", "Used to understand irrigation need and root oxygen stress risk."),
                ("Soil pH", "Supports nutrient availability checks and crop compatibility."),
                ("Nitrogen / NPK", "Drives fertilizer recommendation and crop planning confidence."),
                ("Temperature", "Helps estimate heat stress and seasonal suitability."),
                ("Humidity", "Used to infer disease pressure and crop stress conditions."),
                ("Market price signal", "Adds profitability context to the agronomic recommendation."),
            ],
            columns=3,
        )
    with tab2:
        render_info_list(CHEMISTRY_SIGNALS, columns=2)
        render_status_ribbon(
            "Chemistry Focus",
            "Applied agricultural chemistry layer",
            "This prototype does not stop at disease detection. It interprets soil chemistry, nutrient balance, moisture-driven oxygen stress, and fertilizer planning together.",
            "info",
        )
    with tab3:
        render_info_list(
            [
                ("Irrigation trigger", "If soil moisture falls below threshold, the system can recommend or trigger irrigation."),
                ("Fertilizer advisory", "Low nitrogen status increases fertilizer dosage guidance per acre."),
                ("Crop switch alert", "When chemistry and price signals conflict, the system pushes alternative crops."),
                ("Scenario simulation", "Farmers can compare better and worse price-yield outcomes before planting."),
            ],
            columns=2,
        )
    with tab4:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Integrated Agronomy Simulator")
        st.caption("Test field conditions virtually before making an on-farm decision.")
        s1, s2, s3 = st.columns(3)
        with s1:
            sim_moisture = st.slider("Soil Moisture (%)", 10, 90, 30)
            sim_ph = st.slider("Soil pH", 4.5, 8.5, 6.8)
        with s2:
            sim_nitrogen = st.slider("Nitrogen Level", 10, 80, 35)
            sim_temp = st.slider("Temperature (°C)", 18, 40, 30)
        with s3:
            sim_humidity = st.slider("Humidity (%)", 30, 95, 68)
            sim_run = st.button("Run Simulator")

        if sim_run:
            sim_result = simulate_agronomy_scenario(
                sim_moisture,
                sim_ph,
                sim_nitrogen,
                sim_temp,
                sim_humidity,
                selected_region,
                farmer_profile,
            )
            st.session_state.sim_result = sim_result
            r1, r2, r3 = st.columns(3)
            r1.metric("Recommended Crop", sim_result["crop"])
            r2.metric("Expected Price", f"₹{sim_result['price'] * 83:.0f}/quintal")
            r3.metric("Yield Index", sim_result["yield_index"])
            render_status_ribbon(
                "Simulation Result",
                f"{sim_result['crop']} is the strongest match",
                sim_result["reason"],
                "info",
            )
            st.write(f"**Fertilizer Suggestion:** {sim_result['fertilizer']}")
            st.write(f"**Irrigation Strategy:** {sim_result['irrigation']}")
        elif st.session_state.sim_result:
            sim_result = st.session_state.sim_result
            r1, r2, r3 = st.columns(3)
            r1.metric("Recommended Crop", sim_result["crop"])
            r2.metric("Expected Price", f"â‚¹{sim_result['price'] * 83:.0f}/quintal")
            r3.metric("Yield Index", sim_result["yield_index"])
            render_status_ribbon(
                "Simulation Result",
                f"{sim_result['crop']} is the strongest match",
                sim_result["reason"],
                "info",
            )
            st.write(f"**Fertilizer Suggestion:** {sim_result['fertilizer']}")
            st.write(f"**Irrigation Strategy:** {sim_result['irrigation']}")
        st.markdown("</div>", unsafe_allow_html=True)
    with tab5:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Farmer Voice Assistant")
        st.caption("Ask a farming question by text or upload a short WAV voice note for transcription.")
        voice_prompt = st.text_input("Ask your question", placeholder="Which crop should I grow this season?", key="voice_prompt")
        voice_audio = st.file_uploader("Optional voice note (WAV)", type=["wav"], key="voice_audio")
        if voice_audio is not None:
            transcript = transcribe_audio_bytes(voice_audio.getvalue())
            st.write(f"**Transcribed Question:** {transcript}")
            if transcript and "could not" not in transcript.lower() and "dependency" not in transcript.lower():
                st.info(answer_farmer_question(transcript))
        if voice_prompt:
            st.info(answer_farmer_question(voice_prompt))
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.caption("Upload a close crop image for a visual diagnosis preview.")
    
    uploaded_file = st.file_uploader("Drop an image here (Leaf, Soil, Stem)", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(uploaded_file, caption="Uploaded Sample", width="stretch")
            
        with col2:
            with st.spinner('Analyzing visual patterns...'):
                time.sleep(0.8)
                image = Image.open(uploaded_file)
                diagnosis = detect_plant_disease(image)
                result = diagnosis["disease_name"]
                confidence = diagnosis["probability"]
                
                st.subheader("Diagnosis Report")
                st.caption(f"Model source: {diagnosis['model_source']}")
                
                if result == "Healthy":
                    render_status_ribbon(
                        "Plant Health",
                        "Crop appears healthy",
                        "No visible stress pattern is dominating the image. Continue routine checks and irrigation discipline.",
                        "ok",
                    )
                    st.success(f"✅ **Status: {result}**")
                    st.metric("Confidence", f"{confidence}%")
                    st.caption(diagnosis["reasoning"])
                    st.info("No action needed right now. Maintain the current regimen and keep monitoring moisture stress.")
                else:
                    render_status_ribbon(
                        "Plant Health",
                        "Intervention recommended",
                        "The visual pattern suggests a likely disease or nutrient issue. Immediate containment is safer than waiting.",
                        "risk",
                    )
                    st.error(f"🦠 **Detection: {result}**")
                    st.metric("Confidence", f"{confidence}%")
                    st.caption(diagnosis["reasoning"])
                    st.warning("⚠️ **Immediate Action Required**")
                    
                    st.markdown("**Recommended Treatment:**")
                    st.write(diagnosis["recommended_treatment"])
                    
                    # Product Link Button (Mock)
                    if st.button("Find Treatments Nearby", type="secondary"):
                        st.session_state.treatment_notice = (
                            f"Nearby treatment options queued for {selected_region}. "
                            "Compare one chemical input supplier and one biological input vendor before buying."
                        )
    
    else:
        st.info("Upload an image to activate the AI Diagnostic Engine.")

    if st.session_state.treatment_notice:
        st.success(st.session_state.treatment_notice)
    
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Crop Planner":
    render_section_intro(
        "Planning Studio",
        "Crop Planner",
        "Match soil, water, and budget constraints to crop options that are more viable operationally and economically."
    )
    
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("Input your farm conditions to generate a more defensible crop mix.")

    loc1, loc2, loc3 = st.columns(3)
    with loc1:
        planner_lat = st.number_input("Latitude", value=17.3850, format="%.4f", key="planner_lat")
    with loc2:
        planner_lon = st.number_input("Longitude", value=78.4867, format="%.4f", key="planner_lon")
    with loc3:
        if st.button("Analyze Location", key="analyze_location"):
            st.session_state.location_recommendation = recommend_crop_by_location(planner_lat, planner_lon)

    if st.session_state.location_recommendation:
        loc_info = st.session_state.location_recommendation
        render_status_ribbon(
            "Location Intelligence",
            f"{loc_info['soil_type']} soil | {loc_info['climate_zone']}",
            loc_info["reason"],
            "info",
        )
        st.caption(f"Suitable crops by location: {', '.join(loc_info['suitable_crops'])}")
    
    with st.form("planner_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            soil = st.select_slider("Soil Type", options=["Sandy", "Loamy", "Clay", "Black", "Red"])
        with col2:
            water = st.select_slider("Water Availability", options=["Low", "Medium", "High"])
        with col3:
            budget = st.slider("Budget Level (INR)", 10000, 250000, 60000, step=5000)
            
        submit = st.form_submit_button("Generate Optimization Plan")
        
        if submit:
            plan_rows = service_crop_plan(
                soil,
                water,
                budget,
                farmer_profile,
                location_hint=st.session_state.get("location_recommendation"),
            )
            st.session_state.planner_results = {
                "soil": soil,
                "water": water,
                "budget": budget,
                "farmer_profile": farmer_profile,
                "crops": plan_rows,
            }
            save_crop_plan(
                st.session_state.user_name,
                selected_region,
                soil,
                water,
                budget,
                {"recommendations": plan_rows, "location": st.session_state.get("location_recommendation")},
            )

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.planner_results:
        planner_budget = st.session_state.planner_results["budget"]
        best_crops = st.session_state.planner_results["crops"]
        render_crop_plan_results(best_crops, planner_budget, profile_config)

elif page == "Financial Support":
    render_section_intro(
        "Resilience Layer",
        "Financial Support and Resilience",
        f"Bring subsidy discovery, insurance visibility, and resilient seed access together so farm planning in {selected_region} is less exposed."
    )

    proj1, proj2 = st.columns(2)
    with proj1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Prototype Cost Estimate")
        st.caption("Estimated academic prototype cost in Indian Rupees.")
        cost_df = pd.DataFrame(PROJECT_COSTS, columns=["Component", "Estimated Cost (INR)"])
        st.dataframe(cost_df, width="stretch", hide_index=True)
        st.metric("Prototype Estimate", "₹10,000 - ₹25,000")
        st.markdown("</div>", unsafe_allow_html=True)
    with proj2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Research Alignment")
        for ref in RESEARCH_REFERENCES:
            st.markdown(f"- {ref}")
        render_status_ribbon(
            "Research Gap",
            "Why this prototype is broader",
            "Most systems cover crop recommendation or disease detection. This prototype combines chemistry, crop planning, market forecasting, and automation logic in one interface.",
            "info",
        )
        st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Subsidy Finder")
        st.write(f"Schemes are grouped here as a quick planning layer for funding and protection in {selected_region}.")
        
        schemes = [
            ("PM-KISAN", "Direct Income Support", "Eligible", "$600/year"),
            ("Crop Insurance", "Weather Damage Cover", "Pending Verification", "Subsidized Premium"),
            ("Drip Irrigation", "Water Conservation", "Eligible", "90% Subsidy")
        ]
        
        for name, desc, status, amount in schemes:
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{name}**")
            c1.caption(desc)
            if status == "Eligible":
                c2.success(f"✅ {status}")
            else:
                c2.warning(f"⚠️ {status}")
            c2.write(f"💵 {amount}")
            st.markdown("---")
        render_status_ribbon("Support Signal", "Most relevant support", f"For {selected_region}, the strongest support theme is {region_profile['support']}, especially for a {farmer_profile.lower()} profile focused on {profile_config['support_focus']}.", "info")
        st.markdown("</div>", unsafe_allow_html=True)
            
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Seed Resilience Network")
        st.caption(f"Nearby sources for resilient seed access and climate-adaptive planting options in {selected_region}.")
        
        # Mock Map
        df_map = pd.DataFrame({
            'lat': [20.5937 + np.random.rand()*0.1 for _ in range(5)],
            'lon': [78.9629 + np.random.rand()*0.1 for _ in range(5)],
            'Type': ['Flood Resistant', 'Drought Tolerant', 'Hybrid', 'Heirloom', 'Hybrid']
        })
        
        st.map(df_map)
        st.caption(f"📍 Seed and resislience points aligned to {selected_region} priorities.")
        
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Loan and Profit Risk Calculator")
    default_crop = st.session_state.pred_result["crop"] if st.session_state.pred_result else "Rice"
    default_price = st.session_state.pred_result["price"] * 83 if st.session_state.pred_result else 2200
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        finance_crop = st.selectbox(
            "Crop",
            ["Tomato", "Onion", "Millet", "Groundnut", "Chili", "Beans", "Rice"],
            index=["Tomato", "Onion", "Millet", "Groundnut", "Chili", "Beans", "Rice"].index(default_crop),
            key="finance_crop",
        )
    with f2:
        expected_yield = st.number_input("Expected Yield (quintals)", min_value=1.0, value=20.0, step=1.0, key="finance_yield")
    with f3:
        predicted_price_inr = st.number_input("Predicted Price (INR/quintal)", min_value=500.0, value=float(default_price), step=50.0, key="finance_price")
    with f4:
        loan_amount = st.number_input("Loan Amount (INR)", min_value=0.0, value=50000.0, step=5000.0, key="finance_loan")

    finance_result = calculate_farm_profit(finance_crop, expected_yield, predicted_price_inr, loan_amount)
    r1, r2, r3 = st.columns(3)
    r1.metric("Expected Profit", f"INR {finance_result['expected_profit']:.0f}")
    r2.metric("Repayment Ability", finance_result["repayment_ability"])
    r3.metric("Risk Level", finance_result["risk_level"])
    render_status_ribbon(
        "Profitability Logic",
        f"Revenue INR {finance_result['revenue']:.0f} vs cost INR {finance_result['total_cost']:.0f}",
        "This estimate combines crop-specific operating cost with loan burden to test whether the projected sale window can carry repayment.",
        "ok" if finance_result["risk_level"] == "Low" else "risk" if finance_result["risk_level"] == "High" else "info",
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
