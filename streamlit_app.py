#!/usr/bin/env python3
"""
CKP-ROU-TATA Passenger Punctuality Dashboard  —  Streamlit app
==============================================================

A multi-page interactive dashboard for assessing passenger-train punctuality
on the Chakradharpur -> Rourkela -> Tatanagar sub-corridor of SER.

Data is consolidated from three source documents:
  1. IIM Kozhikode IRTO Programme - SER CKP Passenger Delay Optimisation Case Study
  2. Action Plan for reducing Wagon Balance & Improving Mobility - CKP Division (05.04.2026)
  3. Punctuality Improvement Action Plan - CKP Division (24.11.2025)

------------------------------------------------------------------
HOW TO RUN LOCALLY
------------------------------------------------------------------
  1. Install the two dependencies (one-time):
         pip install streamlit plotly
     (or:  pip install -r requirements.txt)

  2. Launch the app from the folder that contains this file:
         streamlit run streamlit_app.py

  3. Your browser opens automatically at http://localhost:8501
     To stop the app, press Ctrl+C in the terminal.

------------------------------------------------------------------
HOW TO REFRESH FOR A NEW MONTH
------------------------------------------------------------------
  Edit the values in the "DATA" section below and save the file.
  Streamlit auto-reloads — just click "Rerun" in the browser, or
  use the editable Delay Attribution table inside the app itself.
------------------------------------------------------------------
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# =====================================================================
# PAGE CONFIG  (must be the first Streamlit call)
# =====================================================================
st.set_page_config(
    page_title="CKP-ROU-TATA Punctuality Dashboard",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================================
# THEME / COLOURS
# =====================================================================
NAVY    = "#0D1B2A"
STEEL   = "#324A5F"
SAFFRON = "#F4A261"
CRIMSON = "#C44536"
GREEN   = "#2A9D8F"
AMBER   = "#E9C46A"
MUTED   = "#6B7C93"

PLOTLY_FONT = dict(family="Arial, sans-serif", size=12, color=STEEL)

def style_fig(fig, height=340, legend_bottom=True):
    """Apply a consistent look to every plotly figure."""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        font=PLOTLY_FONT,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title_font=dict(size=13, color=NAVY),
    )
    if legend_bottom:
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom",
                                      y=1.02, xanchor="left", x=0))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#EEF1F4")
    return fig

# Light CSS polish
st.markdown(f"""
<style>
  .block-container {{ padding-top: 2rem; padding-bottom: 3rem; }}
  h1, h2, h3 {{ color: {NAVY}; }}
  [data-testid="stMetricValue"] {{ font-size: 1.7rem; }}
  .corridor-banner {{
      background: linear-gradient(135deg, {NAVY} 0%, #1B2A41 100%);
      color: white; padding: 18px 24px; border-radius: 8px;
      border-bottom: 4px solid {SAFFRON}; margin-bottom: 8px;
  }}
  .corridor-banner h1 {{ color: white; margin: 0 0 4px 0; font-size: 1.5rem; }}
  .corridor-banner p {{ color: #E0E6ED; margin: 0; font-size: 0.85rem; }}
  .src-note {{ color: {MUTED}; font-size: 0.78rem; font-style: italic; }}
</style>
""", unsafe_allow_html=True)


# #####################################################################
#
#   DATA  —  edit values here to refresh the dashboard
#
# #####################################################################

# --- Punctuality % by year -------------------------------------------
PUNCTUALITY_TREND = pd.DataFrame([
    {"Year": "2022-23", "M/Exp %": 77.88, "Passenger %": 97.25, "Overall %": 84.48},
    {"Year": "2023-24", "M/Exp %": 65.61, "Passenger %": 96.76, "Overall %": 77.72},
    {"Year": "2024-25", "M/Exp %": 52.26, "Passenger %": 96.91, "Overall %": 68.32},
    {"Year": "2025-26", "M/Exp %": 46.57, "Passenger %": 92.97, "Overall %": 61.29},
])

# --- 28 delay cause codes (trains detained, Apr-Oct) -----------------
CAUSE_CODES = pd.DataFrame([
    {"SL": 1,  "Code": "ACP",    "Cause": "Alarm Chain Pulling",           "2025-26": 109,  "2024-25": 183},
    {"SL": 2,  "Code": "MA",     "Cause": "Miscreants Activity",           "2025-26": 27,   "2024-25": 56},
    {"SL": 3,  "Code": "AGT",    "Cause": "Agitation",                     "2025-26": 19,   "2024-25": 18},
    {"SL": 4,  "Code": "ACC",    "Cause": "Accident",                      "2025-26": 51,   "2024-25": 111},
    {"SL": 5,  "Code": "IDSL",   "Cause": "Diesel Loco (Indirect)",        "2025-26": 2,    "2024-25": 9},
    {"SL": 6,  "Code": "DELC",   "Cause": "Electric Loco (Direct)",        "2025-26": 27,   "2024-25": 57},
    {"SL": 7,  "Code": "IELC",   "Cause": "Electric Loco (Indirect)",      "2025-26": 35,   "2024-25": 61},
    {"SL": 8,  "Code": "INC",    "Cause": "Incident",                      "2025-26": 1275, "2024-25": 993},
    {"SL": 9,  "Code": "DCW",    "Cause": "Carriage & Wagon (Direct)",     "2025-26": 131,  "2024-25": 260},
    {"SL": 10, "Code": "ICW",    "Cause": "Carriage & Wagon (Indirect)",   "2025-26": 56,   "2024-25": 71},
    {"SL": 11, "Code": "OHE",    "Cause": "OHE / Grid Failure",            "2025-26": 21,   "2024-25": 37},
    {"SL": 12, "Code": "ENG",    "Cause": "Engineering",                   "2025-26": 1580, "2024-25": 954},
    {"SL": 13, "Code": "ST",     "Cause": "Signal & Telecom",              "2025-26": 327,  "2024-25": 351},
    {"SL": 14, "Code": "ELEC",   "Cause": "Electric Defect",               "2025-26": 59,   "2024-25": 101},
    {"SL": 15, "Code": "WEA",    "Cause": "Bad Weather",                   "2025-26": 267,  "2024-25": 181},
    {"SL": 16, "Code": "RUN",    "Cause": "Run Over",                      "2025-26": 44,   "2024-25": 68},
    {"SL": 17, "Code": "CNST",   "Cause": "Construction",                  "2025-26": 128,  "2024-25": 95},
    {"SL": 18, "Code": "TFC",    "Cause": "Traffic",                       "2025-26": 2623, "2024-25": 1262},
    {"SL": 19, "Code": "COMM",   "Cause": "Commercial",                    "2025-26": 35,   "2024-25": 45},
    {"SL": 20, "Code": "PATH",   "Cause": "Out of Path",                   "2025-26": 1064, "2024-25": 1655},
    {"SL": 21, "Code": "LAW",    "Cause": "Law & Order",                   "2025-26": 76,   "2024-25": 47},
    {"SL": 22, "Code": "LC",     "Cause": "LC Gate",                       "2025-26": 32,   "2024-25": 39},
    {"SL": 23, "Code": "CONNI",  "Cause": "Non-IL Working - Construction", "2025-26": 112,  "2024-25": 114},
    {"SL": 24, "Code": "PRONI",  "Cause": "Non-IL Working - Project",      "2025-26": 23,   "2024-25": 139},
    {"SL": 25, "Code": "OPLNI",  "Cause": "Non-IL Working - Open Line",    "2025-26": 9,    "2024-25": 17},
    {"SL": 26, "Code": "PBOL",   "Cause": "Planned Block - Open Line",     "2025-26": 429,  "2024-25": 455},
    {"SL": 27, "Code": "PBC",    "Cause": "Planned Block - Construction",  "2025-26": 2,    "2024-25": 6},
    {"SL": 28, "Code": "LINENC", "Cause": "Line Not Clear",                "2025-26": 690,  "2024-25": 502},
])

# --- Train-wise delay attribution (case-study operating-day scenario) -
# 'Arr TATA (Actual)' is the editable column inside the app.
DELAY_TRAINS = pd.DataFrame([
    {"No.": "P1", "Train": "Ispat Express",          "Dep CKP": "06:15", "Arr TATA (Sched)": "08:05",
     "Arr TATA (Actual)": "08:31", "Priority W": 10, "Max Permissible": 30,
     "Primary Cause": "TSR on BS-4 + headway behind F1 iron-ore rake (departs 06:30 from CKP)",
     "Category": "TSR; Freight headway"},
    {"No.": "P2", "Train": "Howrah-Mumbai Mail",     "Dep CKP": "07:40", "Arr TATA (Sched)": "09:55",
     "Arr TATA (Actual)": "10:36", "Priority W": 9,  "Max Permissible": 45,
     "Primary Cause": "Freight headway behind F2 coal rake (PSSA 08:00-08:45) + TSR cumulative effect",
     "Category": "Freight headway; TSR"},
    {"No.": "P3", "Train": "Rourkela Passenger",     "Dep CKP": "09:30", "Arr TATA (Sched)": "12:10",
     "Arr TATA (Actual)": "12:53", "Priority W": 5,  "Max Permissible": 60,
     "Primary Cause": "BS-2 single-line block-token working (10:00-13:00) clearance + TSR",
     "Category": "Single-line; TSR; Compound"},
    {"No.": "P4", "Train": "Purushottam SF Express", "Dep CKP": "11:00", "Arr TATA (Sched)": "13:05",
     "Arr TATA (Actual)": "13:23", "Priority W": 10, "Max Permissible": 20,
     "Primary Cause": "BS-2 SLB + F4 iron-ore overlap (10:30-11:15) + crew-change halt at MNPR",
     "Category": "Single-line; Freight headway; Compound"},
    {"No.": "P5", "Train": "Gitanjali Express",      "Dep CKP": "13:20", "Arr TATA (Sched)": "15:30",
     "Arr TATA (Actual)": "16:08", "Priority W": 9,  "Max Permissible": 25,
     "Primary Cause": "Held at MNPR/BNDM during BS-3 maintenance block (14:30-16:00)",
     "Category": "Maintenance; Compound"},
    {"No.": "P6", "Train": "Odisha Sampark Kranti",  "Dep CKP": "16:45", "Arr TATA (Sched)": "18:50",
     "Arr TATA (Actual)": "19:14", "Priority W": 8,  "Max Permissible": 30,
     "Primary Cause": "Trail effect of BS-3 maintenance clearance + TSR + ROU platform contention",
     "Category": "Maintenance; TSR"},
    {"No.": "P7", "Train": "Chakradharpur Intercity","Dep CKP": "19:10", "Arr TATA (Sched)": "21:45",
     "Arr TATA (Actual)": "22:03", "Priority W": 6,  "Max Permissible": 60,
     "Primary Cause": "TSR on BS-4 + F8 container rake headway (commitment window 17:30)",
     "Category": "TSR; Freight headway"},
])

# --- Passenger train master ------------------------------------------
PASSENGER_TRAINS = pd.DataFrame([
    {"No.": "P1", "Train": "Ispat Express",          "Category": "SF Express", "Dep CKP": "06:15", "Arr TATA": "08:05", "Transit (min)": 110, "Occupancy %": 95, "Priority W": 10, "Max Delay (min)": 30},
    {"No.": "P2", "Train": "Howrah-Mumbai Mail",     "Category": "Mail",       "Dep CKP": "07:40", "Arr TATA": "09:55", "Transit (min)": 135, "Occupancy %": 88, "Priority W": 9,  "Max Delay (min)": 45},
    {"No.": "P3", "Train": "Rourkela Passenger",     "Category": "Passenger",  "Dep CKP": "09:30", "Arr TATA": "12:10", "Transit (min)": 160, "Occupancy %": 72, "Priority W": 5,  "Max Delay (min)": 60},
    {"No.": "P4", "Train": "Purushottam SF Express", "Category": "SF Express", "Dep CKP": "11:00", "Arr TATA": "13:05", "Transit (min)": 125, "Occupancy %": 97, "Priority W": 10, "Max Delay (min)": 20},
    {"No.": "P5", "Train": "Gitanjali Express",      "Category": "Superfast",  "Dep CKP": "13:20", "Arr TATA": "15:30", "Transit (min)": 130, "Occupancy %": 91, "Priority W": 9,  "Max Delay (min)": 25},
    {"No.": "P6", "Train": "Odisha Sampark Kranti",  "Category": "SF Express", "Dep CKP": "16:45", "Arr TATA": "18:50", "Transit (min)": 125, "Occupancy %": 85, "Priority W": 8,  "Max Delay (min)": 30},
    {"No.": "P7", "Train": "Chakradharpur Intercity","Category": "Intercity",  "Dep CKP": "19:10", "Arr TATA": "21:45", "Transit (min)": 155, "Occupancy %": 68, "Priority W": 6,  "Max Delay (min)": 60},
])

# --- Freight train master --------------------------------------------
FREIGHT_TRAINS = pd.DataFrame([
    {"Code": "F1", "Commodity": "Iron Ore / BOXNHL",  "Origin -> Destination": "Noamundi -> Paradip",      "Window (CKP)": "06:30-07:00", "Type": "Steel FSA",  "Load (T)": 3800, "Penalty (Rs L)": 4.5, "Flex (min)": 15},
    {"Code": "F2", "Commodity": "Coal / BOXN",        "Origin -> Destination": "Ib Valley -> Rourkela TPS","Window (CKP)": "08:00-08:45", "Type": "PSSA",       "Load (T)": 3200, "Penalty (Rs L)": 3.8, "Flex (min)": 20},
    {"Code": "F3", "Commodity": "Steel Slabs / BOST", "Origin -> Destination": "Rourkela -> Vizag Port",   "Window (CKP)": "09:15-09:45", "Type": "Port Cmt.",  "Load (T)": 2900, "Penalty (Rs L)": 5.0, "Flex (min)": 10},
    {"Code": "F4", "Commodity": "Iron Ore / BOXNHL",  "Origin -> Destination": "Kiriburu -> Haldia",       "Window (CKP)": "10:30-11:15", "Type": "Steel FSA",  "Load (T)": 3800, "Penalty (Rs L)": 4.5, "Flex (min)": 15},
    {"Code": "F5", "Commodity": "Cement / BCN",       "Origin -> Destination": "Sundargarh -> Howrah",     "Window (CKP)": "12:00-12:30", "Type": "General",    "Load (T)": 2100, "Penalty (Rs L)": 0.0, "Flex (min)": 45},
    {"Code": "F6", "Commodity": "Coal / BOXN",        "Origin -> Destination": "Talcher -> Bokaro TPS",    "Window (CKP)": "13:45-14:15", "Type": "PSSA",       "Load (T)": 3200, "Penalty (Rs L)": 3.8, "Flex (min)": 20},
    {"Code": "F7", "Commodity": "Iron Ore / BOXNHL",  "Origin -> Destination": "Noamundi -> Kalinganagar", "Window (CKP)": "15:00-15:30", "Type": "Steel FSA",  "Load (T)": 3800, "Penalty (Rs L)": 4.5, "Flex (min)": 15},
    {"Code": "F8", "Commodity": "Container / BLCA",   "Origin -> Destination": "Mundra -> Tatanagar",      "Window (CKP)": "17:30-18:00", "Type": "General",    "Load (T)": 1800, "Penalty (Rs L)": 0.0, "Flex (min)": 60},
])

# --- Block sections (TSR adjusted) -----------------------------------
BLOCK_SECTIONS = pd.DataFrame([
    {"BS": "BS-1", "From -> To": "Chakradharpur -> Sini Jn",      "km": 18, "Pass kmph": 110, "Freight kmph": 60, "Pass traversal (min)": 10, "Freight traversal (min)": 18, "Note": ""},
    {"BS": "BS-2", "From -> To": "Sini Jn -> Manoharpur",         "km": 14, "Pass kmph": 110, "Freight kmph": 60, "Pass traversal (min)": 8,  "Freight traversal (min)": 14, "Note": "Single-line block-token working 10:00-13:00"},
    {"BS": "BS-3", "From -> To": "Manoharpur -> Bondamunda",      "km": 22, "Pass kmph": 100, "Freight kmph": 50, "Pass traversal (min)": 13, "Freight traversal (min)": 26, "Note": "Maintenance block 14:30-16:00"},
    {"BS": "BS-4", "From -> To": "Bondamunda -> Rourkela Yard",   "km": 8,  "Pass kmph": 75,  "Freight kmph": 30, "Pass traversal (min)": 7,  "Freight traversal (min)": 16, "Note": "TEMPORARY SPEED RESTRICTION - all day"},
    {"BS": "BS-5", "From -> To": "Rourkela Yard -> Rajgangpur",   "km": 21, "Pass kmph": 110, "Freight kmph": 65, "Pass traversal (min)": 12, "Freight traversal (min)": 20, "Note": ""},
    {"BS": "BS-6", "From -> To": "Rajgangpur -> Tatanagar",       "km": 14, "Pass kmph": 110, "Freight kmph": 65, "Pass traversal (min)": 8,  "Freight traversal (min)": 13, "Note": ""},
])

# --- Wagon holding & loading -----------------------------------------
WAGON_HOLDING = pd.DataFrame([
    {"Year": "2021-22", "Loading (MT)": 145.52, "Avg Wagon Holding": 16233},
    {"Year": "2022-23", "Loading (MT)": 143.67, "Avg Wagon Holding": 16702},
    {"Year": "2023-24", "Loading (MT)": 149.18, "Avg Wagon Holding": 19691},
    {"Year": "2024-25", "Loading (MT)": 154.07, "Avg Wagon Holding": 24097},
    {"Year": "2025-26", "Loading (MT)": 154.97, "Avg Wagon Holding": 24321},
])

# --- IR NBOX vs GPWIS empty holding ----------------------------------
EMPTY_HOLDING = pd.DataFrame([
    {"Year": "2022-23", "IR NBOX Empty": 71.68, "GPWIS Empty": 15.73},
    {"Year": "2023-24", "IR NBOX Empty": 61.59, "GPWIS Empty": 30.88},
    {"Year": "2024-25", "IR NBOX Empty": 65.19, "GPWIS Empty": 65.59},
    {"Year": "2025-26", "IR NBOX Empty": 76.52, "GPWIS Empty": 81.27},
])

# --- JSG-ROU daily excess engineering CD -----------------------------
EXCESS_CD = pd.DataFrame([
    {"Date": "15-Nov", "ROU->JSG (UP)": 19.84, "JSG->ROU (DN)": 28.10},
    {"Date": "16-Nov", "ROU->JSG (UP)": 23.49, "JSG->ROU (DN)": 26.97},
    {"Date": "17-Nov", "ROU->JSG (UP)": 23.49, "JSG->ROU (DN)": 27.27},
    {"Date": "18-Nov", "ROU->JSG (UP)": 27.24, "JSG->ROU (DN)": 24.63},
    {"Date": "19-Nov", "ROU->JSG (UP)": 26.12, "JSG->ROU (DN)": 24.63},
    {"Date": "20-Nov", "ROU->JSG (UP)": 26.12, "JSG->ROU (DN)": 26.12},
    {"Date": "21-Nov", "ROU->JSG (UP)": 22.47, "JSG->ROU (DN)": 28.28},
])

# --- Elephant caution monthly impact ---------------------------------
ELEPHANT_CD = pd.DataFrame([
    {"Month": "Jun-25", "Trains affected": 1361, "Trains/day": 45.37, "Time lost/day (min)": 304.57},
    {"Month": "Jul-25", "Trains affected": 1992, "Trains/day": 64.26, "Time lost/day (min)": 428.81},
    {"Month": "Aug-25", "Trains affected": 1877, "Trains/day": 60.55, "Time lost/day (min)": 432.16},
    {"Month": "Sep-25", "Trains affected": 1816, "Trains/day": 60.53, "Time lost/day (min)": 883.67},
    {"Month": "Oct-25", "Trains affected": 1921, "Trains/day": 61.97, "Time lost/day (min)": 678.93},
])

# --- GPWIS rake inductions by station --------------------------------
GPWIS_INDUCT = pd.DataFrame([
    {"Year": "2019", "ADTP": 5,  "BKEY": 2,  "BNDM": 0, "DPS": 9,  "NPRY": 3},
    {"Year": "2020", "ADTP": 4,  "BKEY": 0,  "BNDM": 0, "DPS": 4,  "NPRY": 2},
    {"Year": "2021", "ADTP": 0,  "BKEY": 2,  "BNDM": 0, "DPS": 6,  "NPRY": 6},
    {"Year": "2022", "ADTP": 5,  "BKEY": 4,  "BNDM": 0, "DPS": 1,  "NPRY": 6},
    {"Year": "2023", "ADTP": 16, "BKEY": 12, "BNDM": 3, "DPS": 13, "NPRY": 35},
    {"Year": "2024", "ADTP": 10, "BKEY": 7,  "BNDM": 5, "DPS": 5,  "NPRY": 41},
    {"Year": "2025", "ADTP": 5,  "BKEY": 7,  "BNDM": 2, "DPS": 1,  "NPRY": 0},
])

# --- Coaching trains per day by section ------------------------------
SECTION_DENSITY = pd.DataFrame([
    {"Section": "TATA-CKP-TATA", "Coaching trains/day": 52},
    {"Section": "ASB-TATA-ASB",  "Coaching trains/day": 56},
    {"Section": "TATA-CNI-TATA", "Coaching trains/day": 30},
])

# --- Control-board operational constraints ---------------------------
BOARD_CONSTRAINTS = {
    "TATA Board": {
        "scope": "ASB-GMH-CNI / ASB-GMH-CKP / SYN-KND",
        "stats": [("Coaching trains/day", "52"), ("DN runtime CKP->TATA", "163 min")],
        "issues": [
            "Long 14.43 km TATA-ASB block section with no intermediate crossing facility",
            "Inadequate freight lines & PF at TATA (88 coaching + 85 freight handled/day)",
            "Diamond crossings at both ends of TATA yard impose 10 kmph SR on loops",
            "3rd line ADTP-TATA-SLJR(W) yet to be commissioned",
            "Banker requirement for GMH-CNI 1:100 up-gradient eats into path",
            "No PF on UP/DN Main at GMH, SYN, KND, KZU, BIRP, BRM, MMV",
            "Inadequate freight lines at CKP - only one UP PF on 3rd Main",
        ],
    },
    "Rourkela Board": {
        "scope": "CKP-ROU / ROU-BRMP / ROU-JSG",
        "stats": [("Excess CD JSG-ROU avg/day", "25.6 min"), ("Convergence directions", "4 UP / 2 DN")],
        "issues": [
            "No PF on UP/DN Main at LPH, GOL, PST, MOU, JRA; BZR only DN",
            "1:100 gradient zones with curvature on ROU-CKP and ROU-JSG",
            "Surface crossings at ROU & K Cabin for BNDM-terminating freight",
            "3rd line config creates a DN-direction bottleneck beyond BNDM A-cabin",
            "Elephant CD 18:00-06:00 on MOU-JRA and KIJ-BMPR",
            "BS-4 (Bondamunda -> Rourkela Yard) TSR - 16 min freight vs 10 min normal",
            "Big siding terminals (RSP, GP-OCL, BRMP, SXN-GS) with unpredictable rake acceptance",
        ],
    },
    "DPS Board": {
        "scope": "RKSN-DPS-GX-JRLI",
        "stats": [("PF at BBN", "1 only"), ("Elephant CD window", "18:00-06:00")],
        "issues": [
            "Only one PF at BBN - drives frequent short-termination of 12021/22 at BJMD",
            "Elephant CD overnight affects both coaching and freight",
            "4th line DPS-RKSN under sanction (DPR stage)",
            "Yard modification at DPS proposed (PH-16, FY 2026-27)",
        ],
    },
}

# --- Action plan tracker ---------------------------------------------
ACTION_PLAN = pd.DataFrame([
    {"Horizon": "Short term",  "Measure": "Drastic reduction of wagon balance to manageable level",                   "Status": "In progress",        "Cost (Rs Cr)": None},
    {"Horizon": "Short term",  "Measure": "Path planning for coaching in RKSN-SYN-GMH-TATA & CNI-KND-GMH-TATA",        "Status": "In progress",        "Cost (Rs Cr)": None},
    {"Horizon": "Short term",  "Measure": "Stop pushing freight ahead of coaching at CNI ex-ADRA",                     "Status": "In progress",        "Cost (Rs Cr)": None},
    {"Horizon": "Short term",  "Measure": "Better adjacent-zone coordination to avoid en-route stabling",              "Status": "In progress",        "Cost (Rs Cr)": None},
    {"Horizon": "Short term",  "Measure": "Cancel 7 TOD pairs in ASB-CKP-JSG",                                         "Status": "Proposal",           "Cost (Rs Cr)": None},
    {"Horizon": "Short term",  "Measure": "Change terminals of 4 pairs from TATA to ADTP",                             "Status": "Proposal",           "Cost (Rs Cr)": None},
    {"Horizon": "Short term",  "Measure": "Cancel duplicate MEMU services in TATA-GUA & TATA-BBN",                     "Status": "Proposal",           "Cost (Rs Cr)": None},
    {"Horizon": "Short term",  "Measure": "Reduce Engineering CD; localise TRT mega-block",                            "Status": "In progress",        "Cost (Rs Cr)": None},
    {"Horizon": "Short term",  "Measure": "AI-based elephant detection to localise caution",                           "Status": "Tender opened",      "Cost (Rs Cr)": None},
    {"Horizon": "Medium term", "Measure": "Fill LP vacancies (35% gap - 2,394 of 6,843)",                              "Status": "Ongoing",            "Cost (Rs Cr)": None},
    {"Horizon": "Medium term", "Measure": "NI TATA yard - 3rd Line ADTP-TATA-SLJR(W)",                                 "Status": "Sanctioned",         "Cost (Rs Cr)": None},
    {"Horizon": "Medium term", "Measure": "SINI NI - additional loop line",                                            "Status": "Sanctioned",         "Cost (Rs Cr)": None},
    {"Horizon": "Medium term", "Measure": "NI JSG passenger yard - 4 additional PF lines",                             "Status": "Sanctioned",         "Cost (Rs Cr)": None},
    {"Horizon": "Medium term", "Measure": "NI BNDM K & D cabins - 5th line BNDM A-cabin to ROU",                       "Status": "Sanctioned",         "Cost (Rs Cr)": None},
    {"Horizon": "Medium term", "Measure": "NI PPO + Auto Signal PPO-KXN",                                              "Status": "Sanctioned",         "Cost (Rs Cr)": None},
    {"Horizon": "Long term",   "Measure": "BEH-JSG 4th line (21.5 km)",                                                "Status": "Work in progress",   "Cost (Rs Cr)": 320.95},
    {"Horizon": "Long term",   "Measure": "SINI-KND 3rd & 4th line",                                                   "Status": "Work sanctioned",    "Cost (Rs Cr)": 286.82},
    {"Horizon": "Long term",   "Measure": "GMH-CNI 3rd & 4th line",                                                    "Status": "Work sanctioned",    "Cost (Rs Cr)": 1167.93},
    {"Horizon": "Long term",   "Measure": "ASB-BEH 4th line",                                                          "Status": "Under sanction",     "Cost (Rs Cr)": None},
    {"Horizon": "Long term",   "Measure": "DPS-RKSN 4th line",                                                         "Status": "Under sanction",     "Cost (Rs Cr)": 1348.00},
    {"Horizon": "Long term",   "Measure": "SINI-RKSN 5th & 6th line",                                                  "Status": "FLS sanctioned",     "Cost (Rs Cr)": None},
    {"Horizon": "Long term",   "Measure": "Yard works - ADTP, MAH, DPS, BNDM, MAU",                                    "Status": "With ED Gati Shakti","Cost (Rs Cr)": None},
    {"Horizon": "Long term",   "Measure": "Dumitra-RSP Y-connection",                                                  "Status": "Work in progress",   "Cost (Rs Cr)": None},
    {"Horizon": "Long term",   "Measure": "Bisra-BNDM Link C Y-connection",                                            "Status": "Work in progress",   "Cost (Rs Cr)": 36.92},
])


# #####################################################################
#
#   HELPER FUNCTIONS
#
# #####################################################################

def to_minutes(hhmm: str) -> int:
    """Convert an 'HH:MM' string to minutes past midnight. Returns -1 on bad input."""
    try:
        h, m = str(hhmm).strip().split(":")
        return int(h) * 60 + int(m)
    except Exception:
        return -1


def compute_delays(df: pd.DataFrame) -> pd.DataFrame:
    """Add Delay (min) and Within Limit? columns from scheduled vs actual arrival."""
    out = df.copy()
    sched = out["Arr TATA (Sched)"].apply(to_minutes)
    actual = out["Arr TATA (Actual)"].apply(to_minutes)
    out["Delay (min)"] = (actual - sched).where((sched >= 0) & (actual >= 0), 0)
    out["Within Limit?"] = out["Delay (min)"] <= out["Max Permissible"]
    return out


def cause_with_variance(df: pd.DataFrame) -> pd.DataFrame:
    """Add delta and variance % columns to the cause-code table."""
    out = df.copy()
    out["Delta"] = out["2025-26"] - out["2024-25"]
    out["Variance %"] = (out["Delta"] / out["2024-25"].replace(0, pd.NA) * 100).round(2)
    return out


# #####################################################################
#
#   PAGE RENDERERS
#
# #####################################################################

def page_overview():
    st.subheader("Overview")
    st.markdown('<p class="src-note">FY 2025-26 figures are through 31 October 2025. '
                'Variance shown against FY 2024-25.</p>', unsafe_allow_html=True)

    last = PUNCTUALITY_TREND.iloc[-1]
    prev = PUNCTUALITY_TREND.iloc[-2]
    det_curr = int(CAUSE_CODES["2025-26"].sum())
    det_prev = int(CAUSE_CODES["2024-25"].sum())
    wagon_last = int(WAGON_HOLDING.iloc[-1]["Avg Wagon Holding"])
    wagon_first = int(WAGON_HOLDING.iloc[0]["Avg Wagon Holding"])

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("M/Exp Punctuality", f"{last['M/Exp %']:.2f}%",
              f"{last['M/Exp %'] - prev['M/Exp %']:.2f} pp", delta_color="normal")
    c2.metric("Passenger Punctuality", f"{last['Passenger %']:.2f}%",
              f"{last['Passenger %'] - prev['Passenger %']:.2f} pp", delta_color="normal")
    c3.metric("Overall Punctuality", f"{last['Overall %']:.2f}%",
              f"{last['Overall %'] - prev['Overall %']:.2f} pp", delta_color="normal")
    c4.metric("Trains Detained (Apr-Oct)", f"{det_curr:,}",
              f"{(det_curr - det_prev) / det_prev * 100:+.1f}%", delta_color="inverse")
    c5.metric("Avg Wagon Holding", f"{wagon_last:,}",
              f"{(wagon_last - wagon_first) / wagon_first * 100:+.1f}% vs {WAGON_HOLDING.iloc[0]['Year']}",
              delta_color="inverse")

    st.warning(
        "**Headline:** M/Exp punctuality has fallen 31.3 percentage points in four years "
        "(77.88% -> 46.57%). The drop tracks a 49.8% rise in wagon holding and sharp increases "
        "in Traffic (+108%), Engineering (+66%) and Line-Not-Clear (+37%) detentions. "
        "BS-4 (Bondamunda -> Rourkela Yard) is the binding bottleneck this week due to a TSR."
    )

    left, right = st.columns([2, 1])
    with left:
        st.markdown("**Punctuality % by Category**")
        long = PUNCTUALITY_TREND.melt(id_vars="Year", var_name="Category", value_name="Punctuality %")
        fig = px.line(long, x="Year", y="Punctuality %", color="Category", markers=True,
                      color_discrete_map={"M/Exp %": CRIMSON, "Passenger %": GREEN, "Overall %": NAVY})
        fig.update_traces(line=dict(width=3))
        fig.update_yaxes(range=[40, 100])
        st.plotly_chart(style_fig(fig), use_container_width=True)
    with right:
        st.markdown("**Year-on-Year Table**")
        st.dataframe(PUNCTUALITY_TREND, hide_index=True, use_container_width=True)
        st.caption("Lower % = more delayed trains. M/Exp deterioration is the steepest.")


def page_trend():
    st.subheader("Punctuality Trend")
    years = PUNCTUALITY_TREND["Year"].tolist()
    sel = st.multiselect("Years to display", years, default=years)
    cats = st.multiselect("Categories", ["M/Exp %", "Passenger %", "Overall %"],
                          default=["M/Exp %", "Passenger %", "Overall %"])
    if not sel or not cats:
        st.info("Select at least one year and one category.")
        return

    df = PUNCTUALITY_TREND[PUNCTUALITY_TREND["Year"].isin(sel)]
    long = df.melt(id_vars="Year", value_vars=cats, var_name="Category", value_name="Punctuality %")
    fig = px.line(long, x="Year", y="Punctuality %", color="Category", markers=True,
                  color_discrete_map={"M/Exp %": CRIMSON, "Passenger %": GREEN, "Overall %": NAVY})
    fig.update_traces(line=dict(width=3))
    st.plotly_chart(style_fig(fig, height=420), use_container_width=True)

    st.markdown("**Year-on-year change (percentage points)**")
    delta = PUNCTUALITY_TREND.copy()
    for c in ["M/Exp %", "Passenger %", "Overall %"]:
        delta[c + " Δ"] = delta[c].diff().round(2)
    st.dataframe(delta[["Year", "M/Exp % Δ", "Passenger % Δ", "Overall % Δ"]],
                 hide_index=True, use_container_width=True)


def page_causes():
    st.subheader("Delay Cause Analysis - 28 Cause Codes")
    st.markdown('<p class="src-note">Trains detained, April-October, current FY vs prior FY.</p>',
                unsafe_allow_html=True)

    cv = cause_with_variance(CAUSE_CODES)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Top 10 Causes - Current FY**")
        top10 = cv.nlargest(10, "2025-26").sort_values("2025-26")
        fig = go.Figure()
        fig.add_bar(y=top10["Code"], x=top10["2025-26"], name="2025-26",
                    orientation="h", marker_color=CRIMSON)
        fig.add_bar(y=top10["Code"], x=top10["2024-25"], name="2024-25",
                    orientation="h", marker_color=STEEL)
        fig.update_layout(barmode="group")
        st.plotly_chart(style_fig(fig, height=420), use_container_width=True)
    with col2:
        st.markdown("**YoY Variance - Biggest Movers**")
        movers = cv.reindex(cv["Delta"].abs().sort_values(ascending=False).index).head(10)
        movers = movers.sort_values("Delta")
        colors = [CRIMSON if d >= 0 else GREEN for d in movers["Delta"]]
        fig = go.Figure(go.Bar(y=movers["Code"], x=movers["Delta"], orientation="h",
                               marker_color=colors,
                               text=movers["Cause"], hovertemplate="%{text}: %{x:+d}<extra></extra>"))
        st.plotly_chart(style_fig(fig, height=420, legend_bottom=False), use_container_width=True)

    st.markdown("**All 28 Cause Codes**")
    q = st.text_input("Search code or cause name", "")
    table = cv.copy()
    if q:
        mask = table["Code"].str.contains(q, case=False) | table["Cause"].str.contains(q, case=False)
        table = table[mask]
    st.caption(f"{len(table)} of {len(cv)} causes shown - click any column header to sort")
    st.dataframe(
        table[["SL", "Code", "Cause", "2025-26", "2024-25", "Delta", "Variance %"]],
        hide_index=True, use_container_width=True,
        column_config={
            "2025-26": st.column_config.NumberColumn(format="%d"),
            "2024-25": st.column_config.NumberColumn(format="%d"),
            "Delta": st.column_config.NumberColumn(format="%+d"),
            "Variance %": st.column_config.NumberColumn(format="%+.2f%%"),
        },
    )
    tot_c, tot_p = int(cv["2025-26"].sum()), int(cv["2024-25"].sum())
    st.info(f"**Total trains detained:** {tot_c:,} in 2025-26 vs {tot_p:,} in 2024-25  "
            f"(**{(tot_c - tot_p) / tot_p * 100:+.2f}%**)")


def page_boards():
    st.subheader("Control Board-wise Operational Constraints")
    st.markdown('<p class="src-note">Where delays concentrate across the CKP-ROU-TATA corridor.</p>',
                unsafe_allow_html=True)

    cols = st.columns(3)
    for col, (board, info) in zip(cols, BOARD_CONSTRAINTS.items()):
        with col:
            st.markdown(f"### {board}")
            st.caption(info["scope"])
            for label, val in info["stats"]:
                st.metric(label, val)
            for issue in info["issues"]:
                st.markdown(f"- {issue}")

    st.divider()
    st.markdown("**Coaching Train Density by Section (both directions / day)**")
    fig = px.bar(SECTION_DENSITY, x="Section", y="Coaching trains/day",
                 color="Section",
                 color_discrete_sequence=[NAVY, CRIMSON, STEEL])
    fig.update_layout(showlegend=False)
    st.plotly_chart(style_fig(fig, height=320, legend_bottom=False), use_container_width=True)


def page_corridor():
    st.subheader("CKP-ROU-TATA Sub-Corridor Detail")
    st.markdown('<p class="src-note">97 km - 6 block sections - 7 nominated passenger trains - 8 freight trains.</p>',
                unsafe_allow_html=True)

    st.markdown("**Block-Section Traversal Times (TSR adjusted)**")
    bs = BLOCK_SECTIONS.copy()
    st.dataframe(
        bs, hide_index=True, use_container_width=True,
        column_config={
            "Pass traversal (min)": st.column_config.NumberColumn(format="%d min"),
            "Freight traversal (min)": st.column_config.NumberColumn(format="%d min"),
        },
    )

    fig = go.Figure()
    fig.add_bar(x=bs["BS"], y=bs["Pass traversal (min)"], name="Passenger (min)", marker_color=GREEN)
    fig.add_bar(x=bs["BS"], y=bs["Freight traversal (min)"], name="Freight (min)", marker_color=CRIMSON)
    fig.update_layout(barmode="group")
    st.plotly_chart(style_fig(fig, height=300), use_container_width=True)

    st.error("**Compound mid-day constraint:** BS-2 single-line working (10:00-13:00) and BS-3 "
             "maintenance block (14:30-16:00) overlap the busiest path window. BS-4 carries a "
             "Temporary Speed Restriction the entire operating day.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**7 Nominated Passenger Trains**")
        st.dataframe(PASSENGER_TRAINS, hide_index=True, use_container_width=True,
                     column_config={"Occupancy %": st.column_config.NumberColumn(format="%d%%")})
    with c2:
        st.markdown("**8 Freight Trains - Commitment Windows**")
        st.dataframe(FREIGHT_TRAINS, hide_index=True, use_container_width=True,
                     column_config={"Penalty (Rs L)": st.column_config.NumberColumn(format="%.1f"),
                                    "Load (T)": st.column_config.NumberColumn(format="%d")})
    st.caption("Heavy BOXNHL/BOXN rakes impose 25-min clear headway; Container/BCN impose 15-min; "
               "passenger 5-min. Minimum 6 loaded freight paths/day are mandatory.")


def page_delays():
    st.subheader("Train-wise Actual vs Scheduled Delay Attribution")
    st.markdown('<p class="src-note">Operating-day scenario built from the case-study constraint set. '
                'Edit the <b>Arr TATA (Actual)</b> column below to refresh - delays and KPIs recompute live.</p>',
                unsafe_allow_html=True)

    edited = st.data_editor(
        DELAY_TRAINS,
        hide_index=True,
        use_container_width=True,
        disabled=["No.", "Train", "Dep CKP", "Arr TATA (Sched)",
                  "Priority W", "Max Permissible", "Primary Cause", "Category"],
        column_config={
            "Arr TATA (Actual)": st.column_config.TextColumn(
                "Arr TATA (Actual)", help="Edit as HH:MM (24-hour). Delay recomputes automatically."),
        },
        key="delay_editor",
    )

    df = compute_delays(edited)

    if (df["Arr TATA (Actual)"].apply(to_minutes) < 0).any():
        st.error("One or more 'Arr TATA (Actual)' values are not valid HH:MM times - fix them above.")

    # KPI row
    total_weighted = int((df["Delay (min)"] * df["Priority W"]).sum())
    avg_delay = df["Delay (min)"].mean()
    within = int(df["Within Limit?"].sum())
    p10_within = int(((df["Priority W"] == 10) & df["Within Limit?"]).sum())
    p10_total = int((df["Priority W"] == 10).sum())

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Weighted Delay", f"{total_weighted:,}", "train-minutes (Σ W×D)")
    k2.metric("Avg Delay / Train", f"{avg_delay:.1f} min")
    k3.metric("Within Max-Permissible", f"{within} of {len(df)}")
    k4.metric("Priority-10 Within Limit", f"{p10_within} of {p10_total}")

    st.divider()

    left, right = st.columns([2, 1])
    with left:
        st.markdown("**Train-by-Train Delay vs Max Permissible**")
        colors = [GREEN if w else CRIMSON for w in df["Within Limit?"]]
        fig = go.Figure()
        fig.add_bar(x=df["No."] + " " + df["Train"].str.split().str[0],
                    y=df["Delay (min)"], name="Actual delay (min)",
                    marker_color=colors,
                    text=df["Primary Cause"], hovertemplate="%{text}<br>Delay: %{y} min<extra></extra>")
        fig.add_scatter(x=df["No."] + " " + df["Train"].str.split().str[0],
                        y=df["Max Permissible"], name="Max permissible",
                        mode="lines+markers", line=dict(color=SAFFRON, dash="dash", width=2))
        st.plotly_chart(style_fig(fig, height=360), use_container_width=True)
    with right:
        st.markdown("**Cause Category Mix**")
        cat_keys = ["Freight headway", "TSR", "Single-line", "Maintenance", "Compound"]
        cat_minutes = {}
        for k in cat_keys:
            mask = df["Category"].str.contains(k, case=False)
            cat_minutes[k] = int(df.loc[mask, "Delay (min)"].sum())
        cat_df = pd.DataFrame({"Category": list(cat_minutes.keys()),
                               "Delay minutes": list(cat_minutes.values())})
        fig = px.pie(cat_df, names="Category", values="Delay minutes", hole=0.55,
                     color="Category",
                     color_discrete_map={"Freight headway": NAVY, "TSR": CRIMSON,
                                         "Single-line": SAFFRON, "Maintenance": STEEL,
                                         "Compound": AMBER})
        st.plotly_chart(style_fig(fig, height=360, legend_bottom=False), use_container_width=True)
        st.caption("Categories overlap - compound delays count under each contributing cause.")

    st.markdown("**Computed Attribution Table**")
    show = df[["No.", "Train", "Arr TATA (Sched)", "Arr TATA (Actual)", "Delay (min)",
               "Max Permissible", "Within Limit?", "Priority W", "Primary Cause"]]
    st.dataframe(
        show, hide_index=True, use_container_width=True,
        column_config={
            "Delay (min)": st.column_config.NumberColumn(format="%d min"),
            "Within Limit?": st.column_config.CheckboxColumn(),
        },
    )


def page_drivers():
    st.subheader("Operational Drivers")
    st.markdown('<p class="src-note">Underlying causes of path saturation on the corridor.</p>',
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Wagon Holding vs Loading**")
        fig = go.Figure()
        fig.add_bar(x=WAGON_HOLDING["Year"], y=WAGON_HOLDING["Avg Wagon Holding"],
                    name="Avg wagon holding", marker_color=CRIMSON)
        fig.add_scatter(x=WAGON_HOLDING["Year"], y=WAGON_HOLDING["Loading (MT)"],
                        name="Loading (MT)", mode="lines+markers",
                        line=dict(color=GREEN, width=3), yaxis="y2")
        fig.update_layout(yaxis2=dict(title="Loading (MT)", overlaying="y",
                                      side="right", range=[130, 165], showgrid=False))
        st.plotly_chart(style_fig(fig, height=320), use_container_width=True)
    with c2:
        st.markdown("**IR NBOX vs GPWIS Empty Holding (SER)**")
        long = EMPTY_HOLDING.melt(id_vars="Year", var_name="Type", value_name="Empty rakes")
        fig = px.bar(long, x="Year", y="Empty rakes", color="Type", barmode="group",
                     color_discrete_map={"IR NBOX Empty": STEEL, "GPWIS Empty": SAFFRON})
        st.plotly_chart(style_fig(fig, height=320), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**JSG-ROU Excess Engineering CD (Daily)**")
        long = EXCESS_CD.melt(id_vars="Date", var_name="Direction", value_name="Excess CD (min)")
        fig = px.bar(long, x="Date", y="Excess CD (min)", color="Direction", barmode="group",
                     color_discrete_map={"ROU->JSG (UP)": CRIMSON, "JSG->ROU (DN)": NAVY})
        fig.add_hline(y=8, line_dash="dash", line_color=MUTED,
                      annotation_text="Engg allowance 8 min/day")
        st.plotly_chart(style_fig(fig, height=320), use_container_width=True)
    with c4:
        st.markdown("**Elephant Caution Impact (2025)**")
        fig = go.Figure()
        fig.add_bar(x=ELEPHANT_CD["Month"], y=ELEPHANT_CD["Trains/day"],
                    name="Trains/day", marker_color=SAFFRON)
        fig.add_scatter(x=ELEPHANT_CD["Month"], y=ELEPHANT_CD["Time lost/day (min)"],
                        name="Time lost/day (min)", mode="lines+markers",
                        line=dict(color=CRIMSON, width=3), yaxis="y2")
        fig.update_layout(yaxis2=dict(title="Min/day", overlaying="y", side="right", showgrid=False))
        st.plotly_chart(style_fig(fig, height=320), use_container_width=True)

    st.markdown("**GPWIS Rake Inductions - Year-wise (stacked by station)**")
    long = GPWIS_INDUCT.melt(id_vars="Year", var_name="Station", value_name="Rakes inducted")
    fig = px.bar(long, x="Year", y="Rakes inducted", color="Station",
                 color_discrete_sequence=[NAVY, STEEL, MUTED, SAFFRON, CRIMSON])
    st.plotly_chart(style_fig(fig, height=300), use_container_width=True)


def page_actions():
    st.subheader("Action Plan Tracker")
    st.markdown('<p class="src-note">Solutions from the CKP Division punctuality improvement plan (Nov 2025).</p>',
                unsafe_allow_html=True)

    horizons = ACTION_PLAN["Horizon"].unique().tolist()
    pick = st.multiselect("Filter by horizon", horizons, default=horizons)
    df = ACTION_PLAN[ACTION_PLAN["Horizon"].isin(pick)] if pick else ACTION_PLAN

    for horizon in ["Short term", "Medium term", "Long term"]:
        if horizon not in pick:
            continue
        sub = df[df["Horizon"] == horizon]
        st.markdown(f"#### {horizon}  ({len(sub)} measures)")
        st.dataframe(
            sub[["Measure", "Status", "Cost (Rs Cr)"]],
            hide_index=True, use_container_width=True,
            column_config={"Cost (Rs Cr)": st.column_config.NumberColumn(format="%.2f")},
        )

    total_cost = ACTION_PLAN["Cost (Rs Cr)"].sum()
    st.info(f"**Total sanctioned/costed long-term infrastructure spend:** "
            f"Rs {total_cost:,.2f} Cr across {ACTION_PLAN['Cost (Rs Cr)'].notna().sum()} costed works.")


# #####################################################################
#
#   SIDEBAR + ROUTER
#
# #####################################################################

st.markdown("""
<div class="corridor-banner">
  <h1>🚆 Passenger Punctuality Assessment Dashboard</h1>
  <p>South Eastern Railway &middot; Chakradharpur Division &middot;
     Chakradharpur &rarr; Rourkela &rarr; Tatanagar Sub-Corridor</p>
</div>
""", unsafe_allow_html=True)

PAGES = {
    "Overview":                      page_overview,
    "Punctuality Trend":             page_trend,
    "Cause Analysis (28 codes)":     page_causes,
    "Control Boards":                page_boards,
    "Sub-Corridor Detail":           page_corridor,
    "Delay Attribution":             page_delays,
    "Operational Drivers":           page_drivers,
    "Action Plan Tracker":           page_actions,
}

with st.sidebar:
    st.markdown("### Navigation")
    choice = st.radio("Section", list(PAGES.keys()), label_visibility="collapsed")
    st.divider()
    st.markdown("### About")
    st.caption(
        "Interactive dashboard for assessing passenger-train punctuality on the "
        "CKP-ROU-TATA sub-corridor of SER."
    )
    st.markdown("**Data sources**")
    st.caption(
        "1. IIM Kozhikode IRTO Programme - SER CKP Passenger Delay Optimisation Case Study\n\n"
        "2. Action Plan for reducing Wagon Balance & Improving Mobility - CKP Division (05.04.2026)\n\n"
        "3. Punctuality Improvement Action Plan - CKP Division (24.11.2025)"
    )
    st.divider()
    st.caption("To refresh data: edit the DATA section at the top of streamlit_app.py and save, "
               "then click Rerun. The Delay Attribution page is editable directly in the browser.")

# Render the selected page
PAGES[choice]()
