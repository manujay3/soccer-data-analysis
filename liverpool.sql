-- ========= Part 1: Create the individual Cup Views =========

CREATE OR REPLACE VIEW fa_cup_fixtures AS
SELECT * FROM "2024_25_english_fa_cup__first_round_fixtures"
UNION ALL
SELECT * FROM "2024_25_english_fa_cup__second_round_fixtures"
UNION ALL
SELECT * FROM "2024_25_english_fa_cup__third_round_fixtures"
UNION ALL
SELECT * FROM "2024_25_english_fa_cup__fourth_round_fixtures"
UNION ALL
SELECT * FROM "2024_25_english_fa_cup__quarterfinals_fixtures"
UNION ALL
SELECT * FROM "2024_25_english_fa_cup__semifinals_fixtures"
UNION ALL
SELECT * FROM "2024_25_english_fa_cup__final_fixtures";

CREATE OR REPLACE VIEW efl_cup_fixtures AS
SELECT * FROM "2024_25_english_carabao_cup__first_round_fixtures"
UNION ALL
SELECT * FROM "2024_25_english_carabao_cup__second_round_fixtures"
UNION ALL
SELECT * FROM "2024_25_english_carabao_cup__third_round_fixtures"
UNION ALL
SELECT * FROM "2024_25_english_carabao_cup__fourth_round_fixtures"
UNION ALL
SELECT * FROM "2024_25_english_carabao_cup__quarterfinals_fixtures"
UNION ALL
SELECT * FROM "2024_25_english_carabao_cup__semifinals_fixtures"
UNION ALL
SELECT * FROM "2024_25_english_carabao_cup__final_fixtures";

CREATE OR REPLACE VIEW ucl_fixtures AS
SELECT * FROM "2024_25_uefa_champions_league__league_phase_fixtures"
UNION ALL
SELECT * FROM "2024_25_uefa_champions_league__round_of_16_fixtures"
UNION ALL
SELECT * FROM "2024_25_uefa_champions_league__quarterfinals_fixtures"
UNION ALL
SELECT * FROM "2024_25_uefa_champions_league__semifinals_fixtures"
UNION ALL
SELECT * FROM "2024_25_uefa_champions_league__final_fixtures";

DROP VIEW IF EXISTS v_liverpool_matches CASCADE;
-- ========= Part 2: Create the "Master List" View (v_liverpool_matches) =========
-- This view finds every match and calculates the result

CREATE OR REPLACE VIEW v_liverpool_matches AS
WITH all_liverpool_matches AS (
    SELECT "eventId", "matchDate", "HomeTeam", "AwayTeam", "HomeTeamScore", "AwayTeamScore", 'Premier League' AS Competition
    FROM "2024_25_english_premier_league_fixtures"
    WHERE "HomeTeam" = 'Liverpool' OR "AwayTeam" = 'Liverpool'
    UNION ALL
    SELECT "eventId", "matchDate", "HomeTeam", "AwayTeam", "HomeTeamScore", "AwayTeamScore", 'FA Cup' AS Competition
    FROM fa_cup_fixtures
    WHERE "HomeTeam" = 'Liverpool' OR "AwayTeam" = 'Liverpool'
    UNION ALL
    SELECT "eventId", "matchDate", "HomeTeam", "AwayTeam", "HomeTeamScore", "AwayTeamScore", 'EFL Cup' AS Competition
    FROM efl_cup_fixtures
    WHERE "HomeTeam" = 'Liverpool' OR "AwayTeam" = 'Liverpool'
    UNION ALL
    SELECT "eventId", "matchDate", "HomeTeam", "AwayTeam", "HomeTeamScore", "AwayTeamScore", 'Champions League' AS Competition
    FROM ucl_fixtures
    WHERE "HomeTeam" = 'Liverpool' OR "AwayTeam" = 'Liverpool'
)
SELECT
    *,
    CASE
        WHEN ("HomeTeam" = 'Liverpool' AND "HomeTeamScore" > "AwayTeamScore") THEN 'Win'
        WHEN ("AwayTeam" = 'Liverpool' AND "AwayTeamScore" > "HomeTeamScore") THEN 'Win'
        WHEN "HomeTeamScore" = "AwayTeamScore" THEN 'Draw'
        ELSE 'Loss'
        END AS liverpool_result,
    CASE
        WHEN "HomeTeam" = 'Liverpool' THEN 'Home'
        ELSE 'Away'
        END AS venue_type
FROM
    all_liverpool_matches;


-- ========= Part 3: Create the "Summary" View (liverpool_agg_results) =========
-- This view reads from your master list and builds the W-D-L table

CREATE OR REPLACE VIEW liverpool_agg_results AS
SELECT
    Competition,
    COUNT(*) AS Games,
    SUM(CASE WHEN liverpool_result = 'Win' THEN 1 ELSE 0 END) AS W,
    SUM(CASE WHEN liverpool_result = 'Draw' THEN 1 ELSE 0 END) AS D,
    SUM(CASE WHEN liverpool_result = 'Loss' THEN 1 ELSE 0 END) AS L
FROM
    v_liverpool_matches  -- This queries the view from Part 2
GROUP BY
    Competition;


-- ========= Part 4: Run Your Final Query =========
-- This is the only part that actually shows you a result

SELECT
    Competition,
    Games,
    W,
    D,
    L
FROM
    liverpool_agg_results
ORDER BY
    Games DESC, W DESC;

SELECT * FROM v_liverpool_matches;
SELECT * FROM v_liverpool_matches INNER JOIN "2024_25_english_premier_league_plays_data" ON v_liverpool_matches."eventId" = "2024_25_english_premier_league_plays_data"."eventId" WHERE  "team" = 'Liverpool' AND "playDescription" LIKE 'Goal%' OR "playDescription" LIKE 'Penalty%';

SELECT "Player Name", "Position", "Goals", "Assists", "Appearances" FROM "2024_25_english_premier_league_player_stats" WHERE "Team" = 'Liverpool' ORDER BY "Goals" DESC, "Assists" DESC;
SELECT SUM("2024_25_english_premier_league_player_stats"."Goals") AS "Goals", SUM("2024_25_english_premier_league_player_stats"."Assists") AS "Assists", "Player Name" FROM "2024_25_english_premier_league_player_stats" WHERE "Team" = 'Liverpool' GROUP BY "Player Name" ORDER BY "Goals" DESC, "Assists" DESC;
SELECT SUM("2024_25_english_premier_league_player_stats"."Goals") AS "Goals", SUM("2024_25_english_premier_league_player_stats"."Assists") AS "Assists", "Player Name" FROM "2024_25_english_premier_league_player_stats" WHERE "Team" = 'Liverpool' GROUP BY "Player Name" ORDER BY "Goals" DESC, "Assists" DESC;
