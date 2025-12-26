CREATE OR REPLACE VIEW coupedefrance_fixtures AS
SELECT * FROM "2024_25_coupe_de_france__round_of_64_fixtures"
UNION ALL
SELECT * FROM "2024_25_coupe_de_france__round_of_32_fixtures"
UNION ALL
SELECT * FROM "2024_25_coupe_de_france__round_of_16_fixtures"
UNION ALL
SELECT * FROM "2024_25_coupe_de_france__quarterfinals_fixtures"
UNION ALL
SELECT * FROM "2024_25_coupe_de_france__semifinals_fixtures"
UNION ALL
SELECT * FROM "2024_25_coupe_de_france__final_fixtures";



CREATE OR REPLACE VIEW french_top_flight AS
SELECT "eventId", "matchDate", "HomeTeam", "AwayTeam", "HomeTeamScore", "AwayTeamScore", 'Ligue 1' AS Competition
FROM "2024_25_ligue_1_fixtures"
UNION ALL
SELECT "eventId", "matchDate", "HomeTeam", "AwayTeam", "HomeTeamScore", "AwayTeamScore", 'Coupe De France' AS Competition
FROM coupedefrance_fixtures
UNION ALL
SELECT "eventId", "matchDate", "HomeTeam", "AwayTeam", "HomeTeamScore", "AwayTeamScore", 'French Super Cup' AS Competition
FROM "2024_french_super_cup_fixtures";


SELECT
    * FROM french_top_flight
WHERE
    "HomeTeam" IN (SELECT "displayName" FROM "2024_25_ligue_1_standings")
   OR "AwayTeam" IN (SELECT "displayName" FROM "2024_25_ligue_1_standings");




DROP VIEW IF EXISTS v_french_plays_data CASCADE;
CREATE OR REPLACE VIEW v_french_plays_data AS
    --
--
SELECT *, 'Ligue 1' AS Competition
FROM "2024_25_ligue_1_plays_data" UNION ALL
--
SELECT *, 'Coupe De France' AS Competition
FROM "2024_25_coupe_de_france__plays_data" UNION ALL
--
SELECT *, 'French Super Cup' AS Competition
FROM "2024_french_super_cup_plays_data";

-- list of goals
SELECT *
FROM
    french_top_flight
        INNER JOIN
    v_french_plays_data
    ON french_top_flight."eventId" = french_top_flight."eventId"
WHERE
    ("HomeTeam" IN (SELECT "displayName" FROM "2024_25_ligue_1_standings")
        OR "AwayTeam" IN (SELECT "displayName" FROM "2024_25_ligue_1_standings"))
  AND ("playDescription" LIKE 'Goal%' OR "playDescription" LIKE 'Penalty - Scored') AND
    team in (SELECT "displayName" FROM "2024_25_ligue_1_standings");



-- deadliest duos in 24/25  top-flight football
SELECT
    "participant" as Scorer,
    "Assister" as Assister,
    "team",
    COUNT(*) as goal_count
FROM v_french_plays_data
WHERE "playDescription" LIKE 'Goal%'
  AND "Assister" IS NOT NULL
  AND "team" IN (SELECT "displayName" FROM "2024_25_ligue_1_standings")
GROUP BY "participant", "Assister", "team"
ORDER BY goal_count DESC
LIMIT 10;

-- most stoppage time goals
SELECT
    team,
    COUNT(*) as stoppage_time_goals
FROM v_french_plays_data
WHERE ("playDescription" LIKE 'Goal%' OR "playDescription" LIKE 'Penalty - Scored')
  AND ("clockDisplayValue" LIKE '90%') AND
    team in (SELECT "displayName" FROM "2024_25_ligue_1_standings")
GROUP BY team
ORDER BY stoppage_time_goals DESC;

-- yellow card
SELECT
    "participant" as Player,
    "team",
    COUNT(*) as YellowCards
FROM v_french_plays_data
WHERE "playDescription" LIKE 'Yellow Card%' AND
    team in (SELECT "displayName" FROM "2024_25_ligue_1_standings")
GROUP BY "participant", "team"
Order BY YellowCards DESC
LIMIT 10;

-- Red card
SELECT
    "participant" as Player,
    "team",
    COUNT(*) as RedCards
FROM v_french_plays_data
WHERE "playDescription" LIKE 'Red Card%' AND
    team in (SELECT "displayName" FROM "2024_25_ligue_1_standings")
GROUP BY "participant", "team"
Order BY RedCards DESC
LIMIT 10;

-- Home Form Table
SELECT
    "HomeTeam" AS Team,
    COUNT(*) AS Matches_Played_At_Home,

    SUM(CASE WHEN "HomeTeamScore" > "AwayTeamScore" THEN 1 ELSE 0 END) AS Home_Wins,
    SUM(CASE WHEN "HomeTeamScore" = "AwayTeamScore" THEN 1 ELSE 0 END) AS Home_Draws,
    SUM(CASE WHEN "HomeTeamScore" < "AwayTeamScore" THEN 1 ELSE 0 END) AS Home_Losses,

    SUM("HomeTeamScore") AS Goals_Scored_Home,
    SUM("AwayTeamScore") AS Goals_Conceded_Home,
    (SUM("HomeTeamScore") - SUM("AwayTeamScore")) AS Home_Goal_Difference,

    SUM(CASE
            WHEN "HomeTeamScore" > "AwayTeamScore" THEN 3
            WHEN "HomeTeamScore" = "AwayTeamScore" THEN 1
            ELSE 0
        END) AS Home_Points

FROM french_top_flight
WHERE french_top_flight.Competition = 'Ligue 1'
GROUP BY "HomeTeam"
ORDER BY Home_Points DESC, Home_Goal_Difference DESC;

--Away Form Table
SELECT
    "AwayTeam" AS Team,
    COUNT(*) AS Matches_Played_Away,

    SUM(CASE WHEN "AwayTeamScore" > "HomeTeamScore" THEN 1 ELSE 0 END) AS Away_Wins,
    SUM(CASE WHEN "AwayTeamScore" = "HomeTeamScore" THEN 1 ELSE 0 END) AS Away_Draws,
    SUM(CASE WHEN "AwayTeamScore" < "HomeTeamScore" THEN 1 ELSE 0 END) AS Away_Losses,

    SUM("AwayTeamScore") AS Goals_Scored_Away,
    SUM("HomeTeamScore") AS Goals_Conceded_Away,
    (SUM("AwayTeamScore") - SUM("HomeTeamScore")) AS Away_Goal_Difference,

    SUM(CASE
            WHEN "AwayTeamScore" > "HomeTeamScore" THEN 3
            WHEN "AwayTeamScore" = "HomeTeamScore" THEN 1
            ELSE 0
        END) AS Away_Points

FROM french_top_flight
WHERE french_top_flight.Competition = 'Ligue 1'
GROUP BY "AwayTeam"
ORDER BY Away_Points DESC, Away_Goal_Difference DESC;

-- goal involvement
WITH Combined_Stats AS (
    -- 1. Get the Goals (Credit the 'participant')
    SELECT
        "participant" AS Player,
        team,
        1 AS Goals,
        0 AS Assists
    FROM v_french_plays_data
    WHERE "playDescription" LIKE 'Goal%' OR "playDescription" = 'Penalty - Scored'

    UNION ALL

    -- 2. Get the Assists (Credit the 'Assister')
    SELECT
        "Assister" AS Player,
        team,
        0 AS Goals,
        1 AS Assists
    FROM v_french_plays_data
    WHERE ("playDescription" LIKE 'Goal%' OR "playDescription" = 'Penalty - Scored')
      AND "Assister" IS NOT NULL
),

     Aggregated_Stats AS (
         -- 3. Sum them up by Player
         SELECT
             team,
             Player,
             SUM(Goals) AS Total_Goals,
             SUM(Assists) AS Total_Assists,
             SUM(Goals + Assists) AS Total_Involvements,

             -- NEW: Calculate pure Team Goals (Summing only the 'Goals' column across the whole team)
             SUM(SUM(Goals)) OVER (PARTITION BY team) AS Team_Goals_Count,

             -- Rank the players to find the MVP
             ROW_NUMBER() OVER (PARTITION BY team ORDER BY SUM(Goals + Assists) DESC) as rank
         FROM Combined_Stats
         WHERE Player IS NOT NULL
         GROUP BY team, Player
     )

SELECT
    team,
    Player AS "MVP",
    Total_Involvements AS "Total_G+A",
    Team_Goals_Count AS "Team_Goals",
    ROUND((Total_Involvements * 100.0 / Team_Goals_Count), 1) AS "Involvement_%"
FROM Aggregated_Stats
WHERE rank = 1
  AND team IN (SELECT "displayName" FROM "2024_25_ligue_1_standings")
ORDER BY "Involvement_%" DESC;

--super sub
SELECT
    s."participant" AS "Super_Sub_Name",
    s.team,
    COUNT(g."eventId") AS "Goals_From_Bench"

FROM
    v_french_plays_data s  JOIN v_french_plays_data g -- The Goal Event
                                 ON s."eventId" = g."eventId"           -- Same Match
                                     AND s."participant" = g."participant"  -- Same Player
WHERE
    s."playDescription" LIKE '%Substitution%'
  AND (g."playDescription" LIKE 'Goal%' OR g."playDescription" = 'Penalty - Scored')
  AND g."playId" > s."playId"
  AND s.team IN (SELECT "displayName" FROM "2024_25_ligue_1_standings")
GROUP BY
    s."participant", s.team
ORDER BY
    "Goals_From_Bench" DESC
LIMIT 10;

--decisive goals
WITH Goal_Context AS (
    SELECT
        p."participant",
        p.team,
        m."HomeTeam",
        m."HomeTeamScore" AS Final_Home,
        m."AwayTeamScore" AS Final_Away,
        COALESCE(SUM(CASE WHEN p.team = m."HomeTeam" THEN 1 ELSE 0 END) OVER (PARTITION BY p."eventId" ORDER BY p."playId" ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING), 0) AS Home_Pre,
        COALESCE(SUM(CASE WHEN p.team = m."AwayTeam" THEN 1 ELSE 0 END) OVER (PARTITION BY p."eventId" ORDER BY p."playId" ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING), 0) AS Away_Pre
    FROM v_french_plays_data p
             JOIN french_top_flight m ON p."eventId" = m."eventId"
    WHERE (p."playDescription" LIKE 'Goal%' OR p."playDescription" = 'Penalty - Scored')
      AND p.team IN (SELECT "displayName" FROM "2024_25_ligue_1_standings")
)

SELECT
    "participant" AS Scorer,
    team,
    COUNT(*) AS Decisive_Goals
FROM Goal_Context
WHERE
    (Home_Pre = Away_Pre AND ((team = "HomeTeam" AND Final_Home > Final_Away) OR (team != "HomeTeam" AND Final_Away > Final_Home)))
   OR
    (Final_Home = Final_Away AND ABS(Home_Pre - Away_Pre) = 1)
GROUP BY 1, 2
ORDER BY 3 DESC
LIMIT 15;

