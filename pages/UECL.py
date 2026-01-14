import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from directory import db_connection_str
import plotly.express as px
import numpy as np

# ==========================================
# ⚙️ CONFIGURATION SECTION
# ==========================================
PAGE_TITLE = "2024/25 Conference League Analytics"
PLAYS_TABLE = "v_uecl_plays_data"
MATCHES_TABLE = "uecl_top_flight"
STANDINGS_TABLE = '"2024_25_uefa_conference_league__league_phase_standings"'

# --- SETUP & CSS ---
db_connection = create_engine(db_connection_str)

st.markdown(
    """
    <style>
    div[data-testid="stMetricValue"] {
        white-space: normal;
        word-wrap: break-word;
        font-size: 28px !important;
        line-height: 1.2 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# SIDEBAR FILTER
# ==========================================
# 1. Get unique teams
team_list_query = f"""
SELECT DISTINCT "displayName"
FROM {STANDINGS_TABLE}
ORDER BY "displayName";
"""
df_teams = pd.read_sql(team_list_query, db_connection)
unique_teams = df_teams['displayName'].tolist()

# 2. Sidebar Dropdown
st.sidebar.header("Dashboard Filters")
selected_team = st.sidebar.selectbox("Select a Team:", ["All Teams"] + unique_teams)

# 3. Create helper string for SQL queries
if selected_team == "All Teams":
    team_filter = f'SELECT "displayName" FROM {STANDINGS_TABLE}'
else:
    team_filter = f"'{selected_team}'"

st.title(PAGE_TITLE)

# ==========================================
# 0. HERO SECTION (METRICS)
# ==========================================
st.divider()

# --- ROW 1: OFFENSE QUERIES ---

# 1. Top Scorer
top_scorer_query = f"""
SELECT "participant", COUNT(*) as goals
FROM {PLAYS_TABLE}
WHERE "playDescription" LIKE 'Goal%%'
  AND team IN ({team_filter})
GROUP BY "participant"
ORDER BY goals DESC
LIMIT 1;
"""
df_top_scorer = pd.read_sql(top_scorer_query, db_connection)

# 2. Top Assister
top_assist_query = f"""
SELECT "Assister", COUNT(*) as assists
FROM {PLAYS_TABLE}
WHERE ("playDescription" LIKE 'Goal%%' OR "playDescription" = 'Penalty - Scored')
  AND "Assister" IS NOT NULL
  AND team IN ({team_filter})
GROUP BY "Assister"
ORDER BY assists DESC
LIMIT 1;
"""
df_top_assist = pd.read_sql(top_assist_query, db_connection)

# 3. Best Offense
top_team_query = f"""
SELECT team as "Team", COUNT(*) as goals
FROM {PLAYS_TABLE}
WHERE "playDescription" LIKE 'Goal%%'
  AND team IN ({team_filter})
GROUP BY team
ORDER BY goals DESC
LIMIT 1;
"""
df_top_team = pd.read_sql(top_team_query, db_connection)

# --- ROW 2: DEFENSE QUERIES ---

# 4. Most Clean Sheets
clean_sheet_query = f"""
SELECT team as "Team", COUNT(*) as clean_sheets
FROM (
    SELECT "HomeTeam" as team FROM {MATCHES_TABLE} WHERE "AwayTeamScore" = 0
    UNION ALL
    SELECT "AwayTeam" as team FROM {MATCHES_TABLE} WHERE "HomeTeamScore" = 0
) as cs
WHERE team IN ({team_filter})
GROUP BY team
ORDER BY clean_sheets DESC
LIMIT 1;
"""
df_clean_sheets = pd.read_sql(clean_sheet_query, db_connection)

# 5. Most Red Cards
red_card_query = f"""
SELECT team as "Team", COUNT(*) as reds
FROM {PLAYS_TABLE}
WHERE "playDescription" LIKE 'Red Card%%'
  AND team IN ({team_filter})
GROUP BY team
ORDER BY reds DESC
LIMIT 1;
"""
df_red_cards = pd.read_sql(red_card_query, db_connection)

# 6. Most Yellow Cards
yellow_card_query = f"""
SELECT team as "Team", COUNT(*) as yellows
FROM {PLAYS_TABLE}
WHERE "playDescription" LIKE 'Yellow Card%%'
  AND team IN ({team_filter})
GROUP BY team
ORDER BY yellows DESC
LIMIT 1;
"""
df_yellow_cards = pd.read_sql(yellow_card_query, db_connection)

# --- DISPLAY ROW 1 (OFFENSE) ---
col1, col2, col3 = st.columns(3)

with col1:
    if not df_top_scorer.empty:
        st.metric(label="🥇 Top Scorer", value=df_top_scorer.iloc[0]['participant'], delta=f"{df_top_scorer.iloc[0]['goals']} Goals")
    else:
        st.metric(label="🥇 Top Scorer", value="N/A", delta="0 Goals")

with col2:
    if not df_top_assist.empty:
        st.metric(label="🎯 Top Assister", value=df_top_assist.iloc[0]['Assister'], delta=f"{df_top_assist.iloc[0]['assists']} Assists")
    else:
        st.metric(label="🎯 Top Assister", value="N/A", delta="0 Assists")

with col3:
    if not df_top_team.empty:
        st.metric(label="⚽ Best Offense", value=df_top_team.iloc[0]['Team'], delta=f"{df_top_team.iloc[0]['goals']} Goals")
    else:
        st.metric(label="⚽ Best Offense", value="N/A", delta="0 Goals")

# --- DISPLAY ROW 2 (DEFENSE) ---
col4, col5, col6 = st.columns(3)

with col4:
    if not df_clean_sheets.empty:
        st.metric(label="🛡️ Most Clean Sheets", value=df_clean_sheets.iloc[0]['Team'], delta=f"{df_clean_sheets.iloc[0]['clean_sheets']} Shutouts")
    else:
        st.metric(label="🛡️ Most Clean Sheets", value="N/A", delta="0 Shutouts")

with col5:
    if not df_red_cards.empty:
        st.metric(label="🟥 Most Red Cards", value=df_red_cards.iloc[0]['Team'], delta=f"{df_red_cards.iloc[0]['reds']} Reds", delta_color="inverse")
    else:
        st.metric(label="🟥 Most Red Cards", value="Clean", delta="0 Reds", delta_color="inverse")

with col6:
    if not df_yellow_cards.empty:
        st.metric(label="🟨 Most Yellow Cards", value=df_yellow_cards.iloc[0]['Team'], delta=f"{df_yellow_cards.iloc[0]['yellows']} Yellows", delta_color="inverse")
    else:
        st.metric(label="🟨 Most Yellow Cards", value="Clean", delta="0 Yellows", delta_color="inverse")

# ==========================================
# 1. STOPPAGE TIME
# ==========================================
stoppage_time_query = f"""
SELECT team, COUNT(*) as stoppage_time_goals
FROM {PLAYS_TABLE}
WHERE ("playDescription" LIKE 'Goal%%' OR "playDescription" LIKE 'Penalty - Scored')
  AND ("clockDisplayValue" LIKE '90%%') 
  AND team IN ({team_filter})
GROUP BY team
ORDER BY stoppage_time_goals DESC
LIMIT 10;
"""

st.header("Most Stoppage Time Goals")
df_stoppage = pd.read_sql(stoppage_time_query, db_connection)

if not df_stoppage.empty:
    fig = px.bar(
        df_stoppage,
        x="stoppage_time_goals",
        y="team",
        orientation='h',
        title="Late Game Drama: Stoppage Time Goals",
        color="stoppage_time_goals",
        color_continuous_scale="Reds",
        text="stoppage_time_goals"
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(f"No stoppage time goals found for {selected_team}.")

# ==========================================
# 2. DECISIVE GOALS
# ==========================================
st.divider()
st.header("Decisive Goals")
st.markdown("Players who scored goals that changed the match result (e.g., turning a Draw into a Win).")

decisive_goals_query = f"""
WITH Total_Goals AS (
    SELECT "participant", COUNT(*) as total_goals
    FROM {PLAYS_TABLE}
    WHERE ("playDescription" LIKE 'Goal%%' OR "playDescription" = 'Penalty - Scored')
      AND team IN ({team_filter})
    GROUP BY "participant"
),
Goal_Context AS (
    SELECT
        p."participant",
        p.team,
        m."HomeTeam",
        m."HomeTeamScore" AS Final_Home,
        m."AwayTeamScore" AS Final_Away,
        COALESCE(SUM(CASE WHEN p.team = m."HomeTeam" THEN 1 ELSE 0 END) OVER (PARTITION BY p."eventId" ORDER BY p."playId" ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING), 0) AS Home_Pre,
        COALESCE(SUM(CASE WHEN p.team = m."AwayTeam" THEN 1 ELSE 0 END) OVER (PARTITION BY p."eventId" ORDER BY p."playId" ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING), 0) AS Away_Pre
    FROM {PLAYS_TABLE} p
             JOIN {MATCHES_TABLE} m ON p."eventId" = m."eventId"
    WHERE (p."playDescription" LIKE 'Goal%%' OR p."playDescription" = 'Penalty - Scored')
      AND p.team IN ({team_filter})
),
Decisive_Stats AS (
    SELECT
        "participant" AS "Player",
        team AS "Team",
        COUNT(*) AS "Decisive_Goals"
    FROM Goal_Context
    WHERE
        (Home_Pre = Away_Pre AND ((team = "HomeTeam" AND Final_Home > Final_Away) OR (team != "HomeTeam" AND Final_Away > Final_Home)))
       OR
        (Final_Home = Final_Away AND ABS(Home_Pre - Away_Pre) = 1)
    GROUP BY 1, 2
)
SELECT
   d."Player",
   d."Team",
   d."Decisive_Goals",
   t.total_goals AS "Total_Goals"
FROM Decisive_Stats d
JOIN Total_Goals t ON d."Player" = t."participant"
ORDER BY d."Decisive_Goals" DESC
LIMIT 15;
"""

df_decisive = pd.read_sql(decisive_goals_query, db_connection)

if not df_decisive.empty:
    df_decisive['jitter_total'] = df_decisive['Total_Goals'] + np.random.uniform(-0.15, 0.15, size=len(df_decisive))
    df_decisive['jitter_decisive'] = df_decisive['Decisive_Goals'] + np.random.uniform(-0.15, 0.15, size=len(df_decisive))

    fig = px.scatter(
        df_decisive,
        x="jitter_total",
        y="jitter_decisive",
        size="Decisive_Goals",
        color="Team",
        hover_name="Player",
        hover_data={"jitter_total": False, "jitter_decisive": False, "Total_Goals": True, "Decisive_Goals": True},
        title="Clutch Analysis: Total Goals vs. Winning Goals",
        labels={"Total_Goals": "Total Goals", "Decisive_Goals": "Winning Goals"}
    )
    fig.update_layout(
        xaxis_title="Total Goals Scored",
        yaxis_title="Game-Winning/Tying Goals",
        yaxis_range=[0, df_decisive['Decisive_Goals'].max() + 0.5],
        xaxis_range=[0, df_decisive['Total_Goals'].max() + 0.5]
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(f"No decisive goals found for {selected_team}.")

# ==========================================
# 3. GOAL CONTRIBUTION
# ==========================================
st.divider()
st.header("Goal Contribution")

goal_contribution_query = f"""
WITH Combined_Stats AS (
    SELECT "participant" AS Player, team, 1 AS Goals, 0 AS Assists
    FROM {PLAYS_TABLE}
    WHERE ("playDescription" LIKE 'Goal%%' OR "playDescription" = 'Penalty - Scored') AND team IN ({team_filter})
    UNION ALL
    SELECT "Assister" AS Player, team, 0 AS Goals, 1 AS Assists
    FROM {PLAYS_TABLE}
    WHERE ("playDescription" LIKE 'Goal%%' OR "playDescription" = 'Penalty - Scored') AND "Assister" IS NOT NULL AND team IN ({team_filter})
),
Aggregated_Stats AS (
     SELECT team, Player, SUM(Goals) AS "Total_Goals", SUM(Assists) AS "Total_Assists", SUM(Goals + Assists) AS Total_Involvements, SUM(SUM(Goals)) OVER (PARTITION BY team) AS Team_Goals_Count
     FROM Combined_Stats WHERE Player IS NOT NULL GROUP BY team, Player
)
SELECT team, Player AS "MVP", "Total_Goals", "Total_Assists", Total_Involvements AS "Total_G+A", ROUND((Total_Involvements * 100.0 / NULLIF(Team_Goals_Count, 0)), 1) AS "Involvement_Pct"
FROM Aggregated_Stats ORDER BY "Total_G+A" DESC LIMIT 10;
"""

df_goalcontribution = pd.read_sql(goal_contribution_query, db_connection)

if not df_goalcontribution.empty:
    fig = px.bar(
        df_goalcontribution,
        x="MVP",
        y=["Total_Goals", "Total_Assists"],
        title="Top 10 Contributors: Goals vs. Assists",
        labels={"value": "Count", "variable": "Type", "MVP": "Player"},
        color_discrete_map={"Total_Goals": "#1f77b4", "Total_Assists": "#ff7f0e"},
        hover_data=["Involvement_Pct", "team"]
    )
    fig.update_layout(legend_title_text="Contribution Type", xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(f"No goal contributions found for {selected_team}.")

# ==========================================
# 4. SUPER SUB
# ==========================================
st.divider()
st.header("Super Sub")

super_sub_query = f""" 
SELECT s."participant" AS "Super_Sub_Name", s.team, COUNT(g."eventId") AS "Goals_From_Bench"
FROM {PLAYS_TABLE} s 
JOIN {PLAYS_TABLE} g ON s."eventId" = g."eventId" AND s."participant" = g."participant"
WHERE s."playDescription" LIKE '%%Substitution%%'
  AND (g."playDescription" LIKE 'Goal%%' OR g."playDescription" = 'Penalty - Scored')
  AND g."playId" > s."playId"
  AND s.team IN ({team_filter})
GROUP BY s."participant", s.team
ORDER BY "Goals_From_Bench" DESC LIMIT 10;
"""

df_supersub = pd.read_sql(super_sub_query, db_connection)

if not df_supersub.empty:
    top_sub = df_supersub.iloc[0]
    colA, colB = st.columns([1, 2])
    with colA:
        st.metric(label="🔥 Best Super Sub", value=top_sub['Super_Sub_Name'], delta=f"{top_sub['Goals_From_Bench']} Bench Goals")
        st.caption(f"Plays for: {top_sub['team']}")
    with colB:
        fig = px.bar(
            df_supersub,
            x="Goals_From_Bench",
            y="Super_Sub_Name",
            orientation='h',
            title="Most Impactful Substitutes",
            color="Goals_From_Bench",
            color_continuous_scale="Viridis",
            labels={"Goals_From_Bench": "Goals Scored", "Super_Sub_Name": "Player"}
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=300)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info(f"No bench goals recorded for {selected_team}.")

# ==========================================
# 5. DISCIPLINE OVERVIEW
# ==========================================
st.divider()
st.header("Discipline Overview")

discipline_query = f""" 
SELECT team,
    CASE 
        WHEN "playDescription" LIKE 'Yellow Card%%' THEN 'Yellow Card'
        WHEN "playDescription" LIKE 'Red Card%%' THEN 'Red Card'
    END as card_type,
    COUNT(*) as count
FROM {PLAYS_TABLE}
WHERE ("playDescription" LIKE 'Yellow Card%%' OR "playDescription" LIKE 'Red Card%%')
  AND team IN ({team_filter})
GROUP BY team, card_type
ORDER BY count DESC;
"""

df_discipline = pd.read_sql(discipline_query, db_connection)

if not df_discipline.empty:
    fig = px.bar(
        df_discipline,
        x="team",
        y="count",
        color="card_type",
        title="Discipline: Yellow vs. Red Cards",
        labels={"count": "Total Cards", "team": "Team"},
        color_discrete_map={'Red Card': '#d32f2f', 'Yellow Card': '#fdd835'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(f"No discipline records found for {selected_team}.")