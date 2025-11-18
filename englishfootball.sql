CREATE OR REPLACE VIEW english_top_flight AS
SELECT "eventId", "matchDate", "HomeTeam", "AwayTeam", "HomeTeamScore", "AwayTeamScore", 'Premier League' AS Competition
FROM "2024_25_english_premier_league_fixtures"
UNION ALL
SELECT "eventId", "matchDate", "HomeTeam", "AwayTeam", "HomeTeamScore", "AwayTeamScore", 'FA Cup' AS Competition
FROM fa_cup_fixtures
UNION ALL
SELECT "eventId", "matchDate", "HomeTeam", "AwayTeam", "HomeTeamScore", "AwayTeamScore", 'EFL Cup' AS Competition
FROM efl_cup_fixtures;


SELECT
    * FROM english_top_flight
WHERE
    "HomeTeam" IN (SELECT "displayName" FROM "2024_25_english_premier_league_standings")
  OR "AwayTeam" IN (SELECT "displayName" FROM "2024_25_english_premier_league_standings");


-- SELECT * FROM english_top_flight INNER JOIN "2024_25_english_premier_league_plays_data" ON english_top_flight."eventId" = "2024_25_english_premier_league_plays_data"."eventId";
-- SELECT * FROM english_top_flight INNER JOIN "2024_25_english_fa_cup__plays_data" ON english_top_flight."eventId" = "2024_25_english_fa_cup__plays_data"."eventId";
-- SELECT * FROM english_top_flight INNER JOIN "2024_25_english_carabao_cup__plays_data" ON english_top_flight."eventId" = "2024_25_english_carabao_cup__plays_data"."eventId";
--          WHERE  "playDescription" LIKE 'Goal%' OR "playDescription" LIKE 'Penalty%';
CREATE OR REPLACE VIEW v_english_plays_data AS
--
-- Premier League
SELECT *, 'Premier League' AS Competition
FROM "2024_25_english_premier_league_plays_data" UNION ALL
-- FA Cup
SELECT *, 'FA Cup' AS Competition
FROM "2024_25_english_fa_cup__plays_data" UNION ALL
-- EFL Cup
SELECT *, 'EFL Cup' AS Competition
FROM "2024_25_english_carabao_cup__plays_data";

SELECT *
FROM
    english_top_flight
        INNER JOIN
    v_english_plays_data
    ON english_top_flight."eventId" = v_english_plays_data."eventId"
WHERE
    ("HomeTeam" IN (SELECT "displayName" FROM "2024_25_english_premier_league_standings")
   OR "AwayTeam" IN (SELECT "displayName" FROM "2024_25_english_premier_league_standings"))
  AND ("playDescription" LIKE 'Goal%' OR "playDescription" LIKE 'Penalty - Scored') AND
      team in (SELECT "displayName" FROM "2024_25_english_premier_league_standings")


-- CREATE OR REPLACE VIEW v_english_keyEvents_data AS
    --
-- -- Premier League
-- SELECT *, 'Premier League' AS Competition
-- FROM "2024_25_english_premier_league_keyevents_data" UNION ALL
-- -- FA Cup
-- SELECT *, 'FA Cup' AS Competition
-- FROM "2024_25_english_fa_cup__keyevents_data" UNION ALL
-- -- EFL Cup
-- SELECT *, 'EFL Cup' AS Competition
-- FROM "2024_25_english_carabao_cup__keyevents_data";
--
-- SELECT DISTINCT *
-- FROM
--     english_top_flight
--         FULL OUTER JOIN
--     v_english_keyEvents_data
--     ON english_top_flight."eventId" = v_english_keyEvents_data."eventId";
--
-- SELECT *
-- FROM
--     english_top_flight
--         FULL OUTER JOIN
--     v_english_keyEvents_data
--     ON english_top_flight."eventId" = v_english_keyEvents_data."eventId"
-- WHERE
--     ("HomeTeam" IN (SELECT "displayName" FROM "2024_25_english_premier_league_standings")
--         OR "AwayTeam" IN (SELECT "displayName" FROM "2024_25_english_premier_league_standings"))
--   AND ("keyEventDescription" = 'Goal')
-- ORDER BY
--     english_top_flight."matchDate" ASC;