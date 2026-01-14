import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
db_connection_str = st.secrets["db_connection_str"]
import plotly.express as px
import numpy as np

# ==========================================
# ⚙️ CONFIGURATION SECTION
# ==========================================
PAGE_TITLE = "2024/25 La Liga Analytics"
PLAYS_TABLE = "v_spanish_plays_data"
MATCHES_TABLE = "spanish_top_flight"
STANDINGS_TABLE = '"2024_25_laliga_standings"'
COMPETITION_FILTER = "La Liga"

# --- SETUP & CSS ---
db_connection = create_engine(db_connection_str)
st.set_page_config(page_title=PAGE_TITLE, layout="wide")

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
team_list_query = f"""
SELECT DISTINCT "displayName" 
FROM {STANDINGS_TABLE} 
ORDER BY "displayName";
"""
df_teams = pd.read_sql(team_list_query, db_connection)
unique_teams = df_teams['displayName'].tolist()

st.sidebar.header("Dashboard Filters")
selected_team = st.sidebar.selectbox("Select a Team:", ["All Teams"] + unique_teams)

if selected_team == "All Teams":
    team_filter = f'SELECT "displayName" FROM {STANDINGS_TABLE}'
else:
    team_filter = f"'{selected_team}'"

st.title(PAGE_TITLE)

# ==========================================
# 0. HERO SECTION (METRICS)
# ==========================================
st.divider()

# --- ROW 1: OFFENSE ---

# 1. Top Scorer
top_scorer_query = f"""
SELECT "participant", COUNT(*) as goals
FROM {PLAYS_TABLE}
WHERE ("playDescription" LIKE 'Goal%%' OR "playDescription" = 'Penalty - Scored')
  AND "playDescription" NOT LIKE '%%Disallowed%%'
  AND "playDescription" NOT LIKE '%%Own Goal%%'
  AND "competition" = '{COMPETITION_FILTER}'
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
  AND "playDescription" NOT LIKE '%%Disallowed%%'
  AND "playDescription" NOT LIKE '%%Own Goal%%'
  AND "competition" = '{COMPETITION_FILTER}'
  AND "Assister" IS NOT NULL
  AND team IN ({team_filter})
GROUP BY "Assister"
ORDER BY assists DESC
LIMIT 1;
"""
df_top_assist = pd.read_sql(top_assist_query, db_connection)

# 3. Best Offense (Includes Own Goals for Team Total)
top_team_query = f"""
SELECT team as "Team", COUNT(*) as goals
FROM {PLAYS_TABLE}
WHERE ("playDescription" LIKE 'Goal%%' OR "playDescription" = 'Penalty - Scored' OR "playDescription" LIKE '%%Own Goal%%')
  AND "playDescription" NOT LIKE '%%Disallowed%%'
  AND "competition" = '{COMPETITION_FILTER}'
  AND team IN ({team_filter})
GROUP BY team
ORDER BY goals DESC
LIMIT 1;
"""
df_top_team = pd.read_sql(top_team_query, db_connection)

# --- ROW 2: DEFENSE ---

if selected_team == "All Teams":
    defense_label = "🛡️ Most Clean Sheets"
    defense_delta = "Shutouts"
    defense_query = f"""
    SELECT team as "Name", COUNT(*) as count
    FROM (
        SELECT "HomeTeam" as team FROM {MATCHES_TABLE} 
        WHERE "AwayTeamScore" = 0 AND "competition" = '{COMPETITION_FILTER}'
        UNION ALL
        SELECT "AwayTeam" as team FROM {MATCHES_TABLE} 
        WHERE "HomeTeamScore" = 0 AND "competition" = '{COMPETITION_FILTER}'
    ) as cs
    WHERE team IN ({team_filter})
    GROUP BY team
    ORDER BY count DESC
    LIMIT 1;
    """
else:
    defense_label = "🧤 Most Saves"
    defense_delta = "Saves"
    defense_query = f"""
    SELECT "participant" as "Name", COUNT(*) as count
    FROM {PLAYS_TABLE}
    WHERE "playDescription" LIKE 'Save%%'
      AND "competition" = '{COMPETITION_FILTER}'
      AND team IN ({team_filter})
    GROUP BY "participant"
    ORDER BY count DESC
    LIMIT 1;
    """

df_defense = pd.read_sql(defense_query, db_connection)

# 5. Most Red Cards
red_card_query = f"""
SELECT "participant", team as "Team", COUNT(*) as reds
FROM {PLAYS_TABLE}
WHERE "playDescription" LIKE 'Red Card%%'
  AND "competition" = '{COMPETITION_FILTER}'
  AND team IN ({team_filter})
GROUP BY "participant", team
ORDER BY reds DESC
LIMIT 1;
"""
df_red_cards = pd.read_sql(red_card_query, db_connection)

# 6. Most Yellow Cards
yellow_card_query = f"""
SELECT "participant", team as "Team", COUNT(*) as yellows
FROM {PLAYS_TABLE}
WHERE "playDescription" LIKE 'Yellow Card%%'
  AND "competition" = '{COMPETITION_FILTER}'
  AND team IN ({team_filter})
GROUP BY "participant", team
ORDER BY yellows DESC
LIMIT 1;
"""
df_yellow_cards = pd.read_sql(yellow_card_query, db_connection)

# --- DISPLAY METRICS ---
col1, col2, col3 = st.columns(3)
with col1:
    if not df_top_scorer.empty:
        st.metric("🥇 Top Scorer", df_top_scorer.iloc[0]['participant'], f"{df_top_scorer.iloc[0]['goals']} Goals")
    else:
        st.metric("🥇 Top Scorer", "N/A", "0 Goals")

with col2:
    if not df_top_assist.empty:
        st.metric("🎯 Top Assister", df_top_assist.iloc[0]['Assister'], f"{df_top_assist.iloc[0]['assists']} Assists")
    else:
        st.metric("🎯 Top Assister", "N/A", "0 Assists")

with col3:
    if not df_top_team.empty:
        st.metric("⚽ Best Offense", df_top_team.iloc[0]['Team'], f"{df_top_team.iloc[0]['goals']} Goals")
    else:
        st.metric("⚽ Best Offense", "N/A", "0 Goals")

col4, col5, col6 = st.columns(3)
with col4:
    if not df_defense.empty:
        st.metric(defense_label, df_defense.iloc[0]['Name'], f"{df_defense.iloc[0]['count']} {defense_delta}")
    else:
        st.metric(defense_label, "N/A", f"0 {defense_delta}")

with col5:
    if not df_red_cards.empty:
        st.metric("🟥 Most Red Cards", df_red_cards.iloc[0]['participant'], f"{df_red_cards.iloc[0]['reds']} Reds", delta_color="inverse")
    else:
        st.metric("🟥 Most Red Cards", "Clean", "0 Reds", delta_color="inverse")

with col6:
    if not df_yellow_cards.empty:
        st.metric("🟨 Most Yellow Cards", df_yellow_cards.iloc[0]['participant'], f"{df_yellow_cards.iloc[0]['yellows']} Yellows", delta_color="inverse")
    else:
        st.metric("🟨 Most Yellow Cards", "Clean", "0 Yellows", delta_color="inverse")

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
    fig = px.bar(df_stoppage, x="stoppage_time_goals", y="team", orientation='h', title="Late Game Drama", color="stoppage_time_goals", color_continuous_scale="Reds")
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No stoppage time goals found.")

# ==========================================
# 2. DECISIVE GOALS
# ==========================================
st.divider()
st.header("Decisive Goals")
st.markdown("Players who scored goals that changed the match result.")

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
SELECT d."Player", d."Team", d."Decisive_Goals", t.total_goals AS "Total_Goals"
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
        df_decisive, x="jitter_total", y="jitter_decisive", size="Decisive_Goals", color="Player",
        hover_name="Player", hover_data={"jitter_total": False, "jitter_decisive": False, "Total_Goals": True, "Decisive_Goals": True},
        title="Clutch Analysis", labels={"Total_Goals": "Total Goals", "Decisive_Goals": "Winning Goals"}
    )
    fig.update_layout(xaxis_title="Total Goals", yaxis_title="Winning Goals")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No decisive goals found.")

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
df_contrib = pd.read_sql(goal_contribution_query, db_connection)

if not df_contrib.empty:
    fig = px.bar(df_contrib, x="MVP", y=["Total_Goals", "Total_Assists"], title="Top Contributors", color_discrete_map={"Total_Goals": "#1f77b4", "Total_Assists": "#ff7f0e"}, hover_data=["Involvement_Pct", "team"])
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No goal contributions found.")

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
        st.metric("🔥 Best Super Sub", top_sub['Super_Sub_Name'], f"{top_sub['Goals_From_Bench']} Bench Goals")
    with colB:
        fig = px.bar(df_supersub, x="Goals_From_Bench", y="Super_Sub_Name", orientation='h', title="Top Substitutes", color="Goals_From_Bench")
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=300)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No bench goals found.")

# ==========================================
# 5. HOME AND AWAY FORM
# ==========================================
st.divider()
st.header("Home and Away Form")
tab_home, tab_away = st.tabs(["Home Table", "Away Table"])

with tab_home:
    st.subheader("Home Standings")
    home_query = f"""
    SELECT "HomeTeam" AS "Team", COUNT(*) AS "Played",
        SUM(CASE WHEN "HomeTeamScore" > "AwayTeamScore" THEN 1 ELSE 0 END) AS "W",
        SUM(CASE WHEN "HomeTeamScore" = "AwayTeamScore" THEN 1 ELSE 0 END) AS "D",
        SUM(CASE WHEN "HomeTeamScore" < "AwayTeamScore" THEN 1 ELSE 0 END) AS "L",
        SUM("HomeTeamScore") AS "GF", SUM("AwayTeamScore") AS "GA", (SUM("HomeTeamScore") - SUM("AwayTeamScore")) AS "GD",
        SUM(CASE WHEN "HomeTeamScore" > "AwayTeamScore" THEN 3 WHEN "HomeTeamScore" = "AwayTeamScore" THEN 1 ELSE 0 END) AS "PTS"
    FROM {MATCHES_TABLE} WHERE competition = '{COMPETITION_FILTER}'
    GROUP BY "HomeTeam" ORDER BY "PTS" DESC, "GD" DESC;
    """
    df_home = pd.read_sql(home_query, db_connection)
    df_home.index += 1
    st.dataframe(df_home, height=(len(df_home) + 1) * 35, use_container_width=True)

with tab_away:
    st.subheader("Away Standings")
    away_query = f"""
    SELECT "AwayTeam" AS "Team", COUNT(*) AS "Played",
        SUM(CASE WHEN "AwayTeamScore" > "HomeTeamScore" THEN 1 ELSE 0 END) AS "W",
        SUM(CASE WHEN "AwayTeamScore" = "HomeTeamScore" THEN 1 ELSE 0 END) AS "D",
        SUM(CASE WHEN "AwayTeamScore" < "HomeTeamScore" THEN 1 ELSE 0 END) AS "L",
        SUM("AwayTeamScore") AS "GF", SUM("HomeTeamScore") AS "GA", (SUM("AwayTeamScore") - SUM("HomeTeamScore")) AS "GD",
        SUM(CASE WHEN "AwayTeamScore" > "HomeTeamScore" THEN 3 WHEN "AwayTeamScore" = "HomeTeamScore" THEN 1 ELSE 0 END) AS "PTS"
    FROM {MATCHES_TABLE} WHERE competition = '{COMPETITION_FILTER}'
    GROUP BY "AwayTeam" ORDER BY "PTS" DESC, "GD" DESC;
    """
    df_away = pd.read_sql(away_query, db_connection)
    df_away.index += 1
    st.dataframe(df_away, height=(len(df_away) + 1) * 35, use_container_width=True)

# ==========================================
# 6. DISCIPLINE (SPLIT)
# ==========================================
st.divider()
st.header("Discipline Overview")
col_yellow, col_red = st.columns(2)

with col_yellow:
    y_query = f"""SELECT "participant" as "Player", team, COUNT(*) as "Yellow Cards" FROM {PLAYS_TABLE} 
                 WHERE "playDescription" LIKE 'Yellow Card%%' AND team IN ({team_filter}) GROUP BY "participant", team ORDER BY "Yellow Cards" DESC LIMIT 10"""
    df_y = pd.read_sql(y_query, db_connection)
    if not df_y.empty:
        fig_y = px.bar(df_y, x="Player", y="Yellow Cards", title="Most Yellow Cards", color_discrete_sequence=['#fdd835'])
        st.plotly_chart(fig_y, use_container_width=True)

with col_red:
    r_query = f"""SELECT "participant" as "Player", team, COUNT(*) as "Red Cards" FROM {PLAYS_TABLE} 
                 WHERE "playDescription" LIKE 'Red Card%%' AND team IN ({team_filter}) GROUP BY "participant", team ORDER BY "Red Cards" DESC LIMIT 10"""
    df_r = pd.read_sql(r_query, db_connection)
    if not df_r.empty:
        fig_r = px.bar(df_r, x="Player", y="Red Cards", title="Most Red Cards", color_discrete_sequence=['#d32f2f'])
        fig_r.update_layout(yaxis=dict(dtick=1))
        st.plotly_chart(fig_r, use_container_width=True)