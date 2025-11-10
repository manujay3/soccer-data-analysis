CREATE VIEW fa_cup_fixtures AS

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

CREATE VIEW efl_cup_fixtures AS

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

CREATE VIEW ucl_fixtures AS

SELECT * FROM "2024_25_uefa_champions_league__league_phase_fixtures"
UNION ALL
SELECT * FROM "2024_25_uefa_champions_league__round_of_16_fixtures"
UNION ALL
SELECT * FROM "2024_25_uefa_champions_league__quarterfinals_fixtures"
UNION ALL
SELECT * FROM "2024_25_uefa_champions_league__semifinals_fixtures"
UNION ALL
SELECT * FROM "2024_25_uefa_champions_league__final_fixtures";

CREATE VIEW liverpool_agg_results AS

WITH all_liverpool_matches AS (
    SELECT
        "matchDate", "HomeTeam", "AwayTeam", "HomeTeamScore", "AwayTeamScore",
        'Premier League' AS Competition
    FROM
        "2024_25_english_premier_league_fixtures"
    WHERE "HomeTeam" = 'Liverpool' OR "AwayTeam" = 'Liverpool'

    UNION ALL

    SELECT "matchDate", "HomeTeam", "AwayTeam", "HomeTeamScore", "AwayTeamScore", 'FA Cup' AS Competition
    FROM fa_cup_fixtures
    WHERE "HomeTeam" = 'Liverpool' OR "AwayTeam" = 'Liverpool'

    UNION ALL

    SELECT "matchDate", "HomeTeam", "AwayTeam", "HomeTeamScore", "AwayTeamScore", 'EFL Cup' AS Competition
    FROM efl_cup_fixtures
    WHERE "HomeTeam" = 'Liverpool' OR "AwayTeam" = 'Liverpool'

    UNION ALL

    SELECT "matchDate", "HomeTeam", "AwayTeam", "HomeTeamScore", "AwayTeamScore", 'Champions League' AS Competition
    FROM ucl_fixtures
    WHERE "HomeTeam" = 'Liverpool' OR "AwayTeam" = 'Liverpool'
),

     match_results AS (
         SELECT *,
                CASE
                    WHEN ("HomeTeam" = 'Liverpool' AND "HomeTeamScore" > "AwayTeamScore") THEN 'Win'
                    WHEN ("AwayTeam" = 'Liverpool' AND "AwayTeamScore" > "HomeTeamScore") THEN 'Win'
                    WHEN "HomeTeamScore" = "AwayTeamScore" THEN 'Draw'
                    ELSE 'Loss'
                    END AS liverpool_result
         FROM
             all_liverpool_matches
     )

SELECT
    Competition,
    COUNT(*) AS Games,
    SUM(CASE WHEN liverpool_result = 'Win' THEN 1 ELSE 0 END) AS W,
    SUM(CASE WHEN liverpool_result = 'Draw' THEN 1 ELSE 0 END) AS D,
    SUM(CASE WHEN liverpool_result = 'Loss' THEN 1 ELSE 0 END) AS L
FROM
    match_results
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