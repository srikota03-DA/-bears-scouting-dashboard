import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ── Page Config ──────────────────────────────
st.set_page_config(
    page_title="Bears Scouting Dashboard",
    page_icon="🐻",
    layout="wide"
)

# ── Load Data ─────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("bears_overall(2009-2024)_final.csv", low_memory=False)

    # Fix team abbreviations
    df.loc[df['DefensiveTeam'] == 'JAC', 'DefensiveTeam'] = 'JAX'
    df.loc[df['DefensiveTeam'] == 'OAK', 'DefensiveTeam'] = 'LV'
    df.loc[df['DefensiveTeam'] == 'LAR', 'DefensiveTeam'] = 'LA'
    df.loc[df['PenalizedTeam'] == 'JAC', 'PenalizedTeam'] = 'JAX'
    df.loc[df['PenalizedTeam'] == 'OAK', 'PenalizedTeam'] = 'LV'
    df.loc[df['PenalizedTeam'] == 'LAR', 'PenalizedTeam'] = 'LA'

    # Standardize PenaltyType
    df['PenaltyType'] = df['PenaltyType'].str.upper()
    df.loc[(df['Accepted.Penalty'] == 1) &
           (df['PenaltyType'].isnull()), 'PenaltyType'] = 'UNKNOWN'

    # Add PenaltySide column
    df['PenaltySide'] = 'None'
    df.loc[(df['Accepted.Penalty'] == 1) &
           (df['PenalizedTeam'] == df['posteam']), 'PenaltySide'] = 'Offensive'
    df.loc[(df['Accepted.Penalty'] == 1) &
           (df['PenalizedTeam'] == df['DefensiveTeam']), 'PenaltySide'] = 'Defensive'

    return df

bears = load_data()

# ── Red Zone Data (Overall — for penalty module) ──
red_zone_all = bears[bears['yrdline100'] <= 20]
rz_plays_all = red_zone_all[red_zone_all['PlayType'].isin(['Pass', 'Run'])]

# Pre-calculate overall penalty metrics
clean_td_overall    = rz_plays_all[rz_plays_all['PenaltySide'] == 'None']['Touchdown'].mean() * 100
off_pen_overall     = rz_plays_all[rz_plays_all['PenaltySide'] == 'Offensive']['Touchdown'].mean() * 100
def_pen_overall     = rz_plays_all[rz_plays_all['PenaltySide'] == 'Defensive']['Touchdown'].mean() * 100
def_pen_plays       = rz_plays_all[rz_plays_all['PenaltySide'] == 'Defensive']
wasted_overall      = (def_pen_plays['Touchdown'] == 0).sum() / len(def_pen_plays) * 100

# ── Header ────────────────────────────────────
st.markdown("""
    <h1 style='text-align:center; color:#0B2265;'>
    🐻 Chicago Bears Scouting Dashboard
    </h1>
    <h4 style='text-align:center; color:#C83803;'>
    Opponent Defense Analysis Tool
    </h4>
    <hr>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Chicago_Bears_logo.svg/200px-Chicago_Bears_logo.svg.png",
    width=150)
st.sidebar.title("🎯 Select Opponent")

teams = sorted(bears['DefensiveTeam'].unique())
selected_team = st.sidebar.selectbox("Choose Opponent Defense:", teams)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Analysis Includes:")
st.sidebar.markdown("✅ Blitz Rate")
st.sidebar.markdown("✅ Run Defense")
st.sidebar.markdown("✅ Pass Defense")
st.sidebar.markdown("✅ 3rd Down Blitz")
st.sidebar.markdown("✅ Red Zone TD Rate")
st.sidebar.markdown("✅ Penalty Adjusted Red Zone")
st.sidebar.markdown("✅ Red Zone Play Type TD%")
st.sidebar.markdown("✅ Strategic Recommendation")

# ── Filter Opponent ───────────────────────────
opp = bears[bears['DefensiveTeam'] == selected_team]

# ── Metrics Row ───────────────────────────────
st.markdown(f"## 📋 Scouting Report vs {selected_team}")
col1, col2, col3, col4, col5 = st.columns(5)

blitz       = opp['QBHit'].mean() * 100
run_yards   = opp[opp['PlayType'] == 'Run']['Yards.Gained'].mean()
pass_yards  = opp[opp['PlayType'] == 'Pass']['Yards.Gained'].mean()
third_blitz = opp[opp['down'] == 3]['QBHit'].mean() * 100
red_td      = opp[opp['yrdline100'] <= 20]['Touchdown'].mean() * 100

col1.metric("Blitz Rate",      f"{blitz:.1f}%")
col2.metric("Avg Run Yards",   f"{run_yards:.2f}")
col3.metric("Avg Pass Yards",  f"{pass_yards:.2f}")
col4.metric("3rd Down Blitz",  f"{third_blitz:.1f}%")
col5.metric("Red Zone TD%",    f"{red_td:.1f}%")

st.markdown("---")

# ── Charts Row 1 ──────────────────────────────
st.markdown("### 📊 Detailed Analysis")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🔴 Blitz Rate vs All Opponents")
    blitz_rate = bears.groupby('DefensiveTeam')['QBHit'].mean() * 100
    blitz_rate = blitz_rate.sort_values(ascending=False).reset_index()
    blitz_rate.columns = ['DefensiveTeam', 'Blitz_Rate']
    colors = ['#C83803' if t == selected_team else '#0B2265'
              for t in blitz_rate['DefensiveTeam']]
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.bar(blitz_rate['DefensiveTeam'], blitz_rate['Blitz_Rate'], color=colors)
    ax1.set_title('Blitz Rate vs Bears', fontsize=14)
    ax1.set_xlabel('Opponent')
    ax1.set_ylabel('QB Hit Rate %')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig1)

with col2:
    st.markdown("#### 🏃 Run Defense vs All Opponents")
    run_def = bears[bears['PlayType'] == 'Run'].groupby(
        'DefensiveTeam')['Yards.Gained'].mean()
    run_def = run_def.sort_values(ascending=True).reset_index()
    colors2 = ['#C83803' if t == selected_team else '#0B2265'
               for t in run_def['DefensiveTeam']]
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.bar(run_def['DefensiveTeam'], run_def['Yards.Gained'], color=colors2)
    ax2.set_title('Avg Run Yards vs Each Defense', fontsize=14)
    ax2.set_xlabel('Opponent')
    ax2.set_ylabel('Avg Yards Per Run')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig2)

# ── Charts Row 2 ──────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown("#### 🏈 Pass Defense vs All Opponents")
    pass_def = bears[bears['PlayType'] == 'Pass'].groupby(
        'DefensiveTeam')['Yards.Gained'].mean()
    pass_def = pass_def.sort_values(ascending=True).reset_index()
    colors3 = ['#C83803' if t == selected_team else '#0B2265'
               for t in pass_def['DefensiveTeam']]
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    ax3.bar(pass_def['DefensiveTeam'], pass_def['Yards.Gained'], color=colors3)
    ax3.set_title('Avg Pass Yards vs Each Defense', fontsize=14)
    ax3.set_xlabel('Opponent')
    ax3.set_ylabel('Avg Yards Per Pass')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig3)

with col4:
    st.markdown("#### 🔴 Red Zone TD Rate vs All Opponents")
    red_td_all = red_zone_all.groupby(
        'DefensiveTeam')['Touchdown'].mean() * 100
    red_td_all = red_td_all.sort_values(ascending=False).reset_index()
    colors4 = ['#C83803' if t == selected_team else '#0B2265'
               for t in red_td_all['DefensiveTeam']]
    fig4, ax4 = plt.subplots(figsize=(10, 5))
    ax4.bar(red_td_all['DefensiveTeam'], red_td_all['Touchdown'], color=colors4)
    ax4.set_title('Red Zone TD Rate vs Each Defense', fontsize=14)
    ax4.set_xlabel('Opponent')
    ax4.set_ylabel('TD Rate %')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig4)

# ── Module 7 — Penalty Adjusted Red Zone ──────
st.markdown("---")
st.markdown("### 🚨 Penalty Adjusted Red Zone Analysis (Overall 2009-2024)")
st.info("ℹ️ These metrics show Bears overall performance across all opponents — sample size per team is too small to show individually.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Clean TD%",              f"{clean_td_overall:.1f}%",   help="TD% with no penalty")
col2.metric("Offensive Penalty TD%",  f"{off_pen_overall:.1f}%",    help="TD% when Bears got penalized")
col3.metric("Defensive Penalty TD%",  f"{def_pen_overall:.1f}%",    help="TD% when opponent got penalized")
col4.metric("Wasted Opportunity %",   f"{wasted_overall:.1f}%",     help="% of opponent penalties Bears failed to score on")

# ── Penalty Metrics Chart ──────────────────────
st.markdown("#### 📊 Penalty Impact on Red Zone Scoring")
fig5, ax5 = plt.subplots(figsize=(8, 5))
metrics     = ['Clean TD%', 'Offensive\nPenalty TD%', 'Defensive\nPenalty TD%', 'Wasted\nOpportunity %']
values      = [clean_td_overall, off_pen_overall, def_pen_overall, wasted_overall]
bar_colors  = ['#0B2265', '#C83803', '#228B22', '#FF8C00']
bars = ax5.bar(metrics, values, color=bar_colors)
ax5.set_title('Bears Red Zone Performance by Penalty Situation', fontsize=14)
ax5.set_ylabel('Percentage %')
for bar, val in zip(bars, values):
    ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f'{val:.1f}%', ha='center', fontsize=11, fontweight='bold')
plt.tight_layout()
st.pyplot(fig5)

# ── Insights ──────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    if wasted_overall > 75:
        st.error(f"⚠️ Bears waste {wasted_overall:.1f}% of opponent red zone penalties — must capitalize!")
    else:
        st.success(f"✅ Bears capitalize on {100 - wasted_overall:.1f}% of opponent penalties")
with col2:
    if off_pen_overall < clean_td_overall:
        st.error(f"⚠️ Own penalties reduce TD% from {clean_td_overall:.1f}% to {off_pen_overall:.1f}% — stay disciplined!")
    else:
        st.success(f"✅ Bears recover well from own penalties in red zone")

# ── Red Zone PlayType TD% ──────────────────────
st.markdown("---")
st.markdown("### 🏈 Red Zone TD% by Play Type (Overall)")
rz_playtype = rz_plays_all.groupby('PlayType')['Touchdown'].mean() * 100
rz_playtype = rz_playtype.sort_values(ascending=False).reset_index()

fig6, ax6 = plt.subplots(figsize=(6, 4))
ax6.bar(rz_playtype['PlayType'], rz_playtype['Touchdown'],
        color=['#0B2265', '#C83803'])
ax6.set_title('Red Zone TD Rate by Play Type', fontsize=14)
ax6.set_xlabel('Play Type')
ax6.set_ylabel('TD Rate %')
for i, (_, row) in enumerate(rz_playtype.iterrows()):
    ax6.text(i, row['Touchdown'] + 0.3, f"{row['Touchdown']:.1f}%",
             ha='center', fontsize=12, fontweight='bold')
plt.tight_layout()
st.pyplot(fig6)

# ── Strategic Recommendation ──────────────────
st.markdown("---")
st.markdown(f"### 🎯 Strategic Recommendation vs {selected_team}")

col1, col2 = st.columns(2)

with col1:
    if pass_yards > run_yards:
        st.success("✅ PASS FIRST STRATEGY RECOMMENDED")
    else:
        st.success("✅ RUN FIRST STRATEGY RECOMMENDED")

    if blitz > 15:
        st.error("⚠️ Very Heavy Blitz — Use quick passes!")
    elif blitz > 10:
        st.warning("⚠️ Moderate Blitz — Stay alert!")
    else:
        st.info("✅ Low Blitz Rate — QB has time to throw")

with col2:
    if red_td < 10:
        st.error("⚠️ Tough Red Zone — Score before 20 yard line!")
    elif red_td < 20:
        st.warning("😐 Average Red Zone Defense")
    else:
        st.success("✅ Good Red Zone Scoring Rate!")

    if third_blitz > 20:
        st.error("⚠️ Heavy 3rd Down Blitz — Use screens!")
    elif third_blitz > 10:
        st.warning("⚠️ Moderate 3rd Down Pressure")
    else:
        st.info("✅ Low 3rd Down Blitz Rate")

# ── Footer ────────────────────────────────────
st.markdown("---")
st.markdown("""
    <p style='text-align:center; color:gray;'>
    🐻 Chicago Bears Scouting Dashboard |
    Built with Python & Streamlit |
    Data: 2009-2024 NFL Seasons (16 Complete Seasons)
    </p>
""", unsafe_allow_html=True)