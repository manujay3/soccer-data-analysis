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


CREATE OR REPLACE VIEW liverpool_agg_results AS
SELECT
    Competition,
    COUNT(*) AS Games,
    SUM(CASE WHEN liverpool_result = 'Win' THEN 1 ELSE 0 END) AS W,
    SUM(CASE WHEN liverpool_result = 'Draw' THEN 1 ELSE 0 END) AS D,
    SUM(CASE WHEN liverpool_result = 'Loss' THEN 1 ELSE 0 END) AS L
FROM
    v_liverpool_matches
GROUP BY
    Competition;


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

-- -- =========================================================
-- -- PART 1: Create the "Cup" Plays Views
-- -- (Stacking all rounds into one view for each cup)
-- -- =========================================================
--
-- -- 1. FA Cup Plays View
-- CREATE OR REPLACE VIEW fa_cup_plays AS
-- SELECT * FROM "2024_25_english_fa_cup__first_round_plays_data"
-- UNION ALL
-- SELECT * FROM "2024_25_english_fa_cup__second_round_plays_data"
-- UNION ALL
-- SELECT * FROM "2024_25_english_fa_cup__third_round_plays_data"
-- UNION ALL
-- SELECT * FROM "2024_25_english_fa_cup__fourth_round_plays_data"
-- UNION ALL
-- SELECT * FROM "2024_25_english_fa_cup__quarterfinals_plays_data"
-- UNION ALL
-- SELECT * FROM "2024_25_english_fa_cup__semifinals_plays_data"
-- UNION ALL
-- SELECT * FROM "2024_25_english_fa_cup__final_plays_data";
--
-- -- 2. EFL Cup Plays View
-- CREATE OR REPLACE VIEW efl_cup_plays AS
-- SELECT * FROM "2024_25_english_carabao_cup__first_round_plays_data"
-- UNION ALL
-- SELECT * FROM "2024_25_english_carabao_cup__second_round_plays_data"
-- UNION ALL
-- SELECT * FROM "2024_25_english_carabao_cup__third_round_plays_data"
-- UNION ALL
-- SELECT * FROM "2024_25_english_carabao_cup__fourth_round_plays_data"
-- UNION ALL
-- SELECT * FROM "2024_25_english_carabao_cup__quarterfinals_plays_data"
-- UNION ALL
-- SELECT * FROM "2024_25_english_carabao_cup__semifinals_plays_data"
-- UNION ALL
-- SELECT * FROM "2024_25_english_carabao_cup__final_plays_data";

-- -- 3. Champions League Plays View
-- CREATE OR REPLACE VIEW ucl_plays AS
-- SELECT * FROM "2024_25_uefa_champions_league__league_phase_plays_data"
-- UNION ALL
-- SELECT * FROM "2024_25_uefa_champions_league__knockout_round_play_offs_plays_data"
-- UNION ALL
-- SELECT * FROM "2024_25_uefa_champions_league__round_of_16_plays_data"
-- UNION ALL
-- SELECT * FROM "2024_25_uefa_champions_league__quarterfinals_plays_data"
-- UNION ALL
-- SELECT * FROM "2024_25_uefa_champions_league__semifinals_plays_data"
-- UNION ALL
-- SELECT * FROM "2024_25_uefa_champions_league__final_plays_data";
--
--
-- -- =========================================================
-- -- PART 2: Create the "Grand Master" Plays View
-- -- (Combining Premier League + All Cups)
-- -- =========================================================
--
-- CREATE OR REPLACE VIEW v_all_plays_data AS
--
-- -- Premier League
-- SELECT *, 'Premier League' AS Competition
-- FROM "2024_25_english_premier_league_plays_data"
--
-- UNION ALL
--
-- -- FA Cup
-- SELECT *, 'FA Cup' AS Competition
-- FROM fa_cup_plays
--
-- UNION ALL
--
-- -- EFL Cup
-- SELECT *, 'EFL Cup' AS Competition
-- FROM efl_cup_plays
--
-- UNION ALL
--
-- -- Champions League
-- SELECT *, 'Champions League' AS Competition
-- FROM ucl_plays;

SELECT * FROM v_liverpool_matches;
SELECT * FROM v_liverpool_matches INNER JOIN "2024_25_english_premier_league_plays_data" ON v_liverpool_matches."eventId" = "2024_25_english_premier_league_plays_data"."eventId" WHERE  "team" = 'Liverpool' AND "playDescription" LIKE 'Goal%' OR "playDescription" LIKE 'Penalty%';

SELECT "Player Name", "Position", "Goals", "Assists", "Appearances" FROM "2024_25_english_premier_league_player_stats" WHERE "Team" = 'Liverpool' ORDER BY "Goals" DESC, "Assists" DESC;
SELECT SUM("2024_25_english_premier_league_player_stats"."Goals") AS "Goals", SUM("2024_25_english_premier_league_player_stats"."Assists") AS "Assists", "Player Name" FROM "2024_25_english_premier_league_player_stats" WHERE "Team" = 'Liverpool' GROUP BY "Player Name" ORDER BY "Goals" DESC, "Assists" DESC;
