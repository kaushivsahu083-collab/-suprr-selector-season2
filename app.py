import json
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="SupeRR Selector | Pressure Analytics", page_icon="🏏", layout="wide")
ROOT = Path(__file__).parent

@st.cache_data
def load_csv(name):
    return pd.read_csv(ROOT / name)

bat_top = load_csv("top10_batters.csv")
bowl_top = load_csv("top10_bowlers.csv")
bat_all = load_csv("all_batter_scores.csv")
bowl_all = load_csv("all_bowler_scores.csv")
sensitivity = load_csv("sensitivity_analysis.csv")
audit = json.loads((ROOT / "audit_summary.json").read_text(encoding="utf-8"))

# Match the column names in the analysis outputs.
bat_name = "striker_name"
bowl_name = "bowler_name"

st.title("🏏 SupeRR Selector Season 2")
st.caption("Round 1 — Reliability under pressure | IPL + Men's T20I | Organizer-supplied data")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Matches analysed", f'{audit["analysis_matches"]:,}')
c2.metric("Deliveries analysed", f'{audit["analysis_deliveries"]:,}')
c3.metric("Eligible batters", f'{audit["eligible_batters"]:,}')
c4.metric("Eligible bowlers", f'{audit["eligible_bowlers"]:,}')

st.info(f'Data window: {audit["date_min"]} to {audit["date_max"]} | IPL: {audit["IPL_matches"]} matches | T20I: {audit["T20I_matches"]} matches')

tab1, tab2, tab3, tab4 = st.tabs(["Top 10 Batters", "Top 10 Bowlers", "All Players", "Sensitivity"])
with tab1:
    st.subheader("Top batters under pressure")
    st.bar_chart(bat_top.set_index(bat_name)["score"])
    cols=["rank",bat_name,"score","pressure_runs","pressure_balls","pressure_avg","pressure_sr","baseline_sr","pressure_innings","formats"]
    st.dataframe(bat_top[cols], use_container_width=True, hide_index=True)
with tab2:
    st.subheader("Top bowlers under pressure")
    st.bar_chart(bowl_top.set_index(bowl_name)["score"])
    cols=["rank",bowl_name,"score","pressure_wickets","pressure_overs","pressure_econ","adj_pressure_dot_pct","pressure_innings","formats"]
    st.dataframe(bowl_top[cols], use_container_width=True, hide_index=True)
with tab3:
    kind=st.radio("Player category",["Batters","Bowlers"],horizontal=True)
    if kind=="Batters":
        q=st.text_input("Search batter")
        view=bat_all.copy()
        if q: view=view[view[bat_name].str.contains(q,case=False,na=False)]
        st.dataframe(view.sort_values("score",ascending=False),use_container_width=True,hide_index=True)
    else:
        q=st.text_input("Search bowler")
        view=bowl_all.copy()
        if q: view=view[view[bowl_name].str.contains(q,case=False,na=False)]
        st.dataframe(view.sort_values("score",ascending=False),use_container_width=True,hide_index=True)
with tab4:
    st.subheader("Sensitivity checks")
    st.caption("Top-10 overlap and rank correlation against the core model under alternative assumptions.")
    st.dataframe(sensitivity,use_container_width=True,hide_index=True)
with st.expander("Pressure definitions and scoring methodology"):
    st.markdown("""
**Pressure situations** are defined in the accompanying methodology report. The analysis combines death-phase pressure, high required run rate, innings collapse, clutch chase and (for bowlers) large-partnership pressure.

**Eligibility:** minimum 60 pressure balls and 8 pressure innings. IPL and T20I components are normalised separately before combination.

**Important:** scores are model-based comparative ratings, not official organizer ratings. See the submitted methodology report for definitions, weights, limitations and sensitivity results.
""")
