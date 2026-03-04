# Swiggy DE

> Auto-generated on 2026-03-04 08:13

**Total queries:** 7

---

## City wise KN stats - Top 9 Cities_City wise KN stats - Top 9 Cities.sql

**Tables referenced:** data_team.announcement_city_stats

**Original Query:**

```sql
-- Data Source: City wise KN stats - Top 9 Cities
-- Dashboard: City wise KN stats - Top 9 Cities
-- Category: Swiggy DE
-- Extracted: 2026-01-29 16:53:06
-- ============================================================

SELECT * FROM data_team.announcement_city_stats a
WHERE a.city_id IN (
    'city_1','city_2','city_3','city_4',
    'city_5','city_6','city_7','city_8',
    'city_10459'
)
AND a.sent >= 50
AND report_date >= CURRENT_DATE - INTERVAL '62 days'
```

---

## City wise KN stats_City wise KN stats - Overall.sql

**Tables referenced:** data_team.announcement_city_stats

**Original Query:**

```sql
-- Data Source: City wise KN stats
-- Dashboard: City wise KN stats - Overall
-- Category: Swiggy DE
-- Extracted: 2026-01-29 16:53:06
-- ============================================================

SELECT * FROM data_team.announcement_city_stats a
WHERE a.sent >= 50
  AND a.city_id <> 'city_empty'
  AND report_date >= CURRENT_DATE - INTERVAL '31 days'
```

---

## OR DE NPS Seen Count_DE NPS Last Week Seen Count.sql

**Tables referenced:** analytics_requests, ar, t, tags, user_tags, ut

**Original Query:**

```sql
-- Data Source: OR DE NPS Seen Count
-- Dashboard: DE NPS Last Week Seen Count
-- Category: Swiggy DE
-- Extracted: 2026-01-29 16:57:41
-- ============================================================

WITH ar AS
  (SELECT DISTINCT user_id, date_trunc('Week', updated_at at time zone 'Asia/Kolkata') as week_of
   FROM analytics_requests
   WHERE event_id > 1
     AND updated_at at time zone 'Asia/Kolkata' > date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '7 days')
     AND nugget_id = '-de-nps-nov-2024'),
     t AS
  (SELECT *
   FROM tags
   WHERE tag ILIKE 'city_%'),
     ut AS
  (SELECT ut.user_id,
          replace(t.tag, 'city_', '') AS city_id
   FROM t
   JOIN user_tags ut ON t.id = ut.tag_id)
SELECT city_id, week_of, count(distinct(ar.user_id))
FROM ar
LEFT OUTER JOIN ut ON ar.user_id = ut.user_id
GROUP BY 1, 2
ORDER BY 2, 1
```

---

## SWIGGY Repeat Users_Swiggy Course Adoption.sql

**Tables referenced:** analytics.lms_raw_analytics, public.lessons, public.users

**Columns needing snake_case conversion:**

- `courseId` -> `course_id` (alias: `course_id AS "courseId"`)

- `createdAt` -> `created_at` (alias: `created_at AS "createdAt"`)

- `firstName` -> `first_name` (alias: `first_name AS "firstName"`)

- `sessionId` -> `session_id` (alias: `session_id AS "sessionId"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: SWIGGY Repeat Users
-- Dashboard: Swiggy Course Adoption
-- Category: Swiggy DE
-- Extracted: 2026-01-29 16:55:22
-- ============================================================

 SELECT
    l.title as `Course Name`,
    ra.courseId AS `Course KNID`,
    ra.userId AS `DE ID`,
    u.firstName, 
    COUNT(DISTINCT ra.sessionId) AS session_count
  FROM analytics.lms_raw_analytics ra
  Join public.lessons l on ra.courseId = l.courseId
  join public.users u on ra.userId = u.userId
  WHERE ra.createdAt between @{{:Swiggy DE LMS Reports.Enrolled Date Range.START}} 
  and @{{:Swiggy DE LMS Reports.Enrolled Date Range.END}}
  GROUP BY ra.courseId, ra.userId,l.title,u.firstName
```

---

## Swiggy DE JRI_Swiggy DE JRI.sql

**Tables referenced:** aggregated.course_report, analytics.quiz_responses, answers, base, conf, ke

**Columns needing snake_case conversion:**

- `answeredAt` -> `answered_at` (alias: `answered_at AS "answeredAt"`)

- `cardId` -> `card_id` (alias: `card_id AS "cardId"`)

- `courseId` -> `course_id` (alias: `course_id AS "courseId"`)

- `isCorrect` -> `is_correct` (alias: `is_correct AS "isCorrect"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Swiggy DE JRI
-- Dashboard: Swiggy DE JRI
-- Category: Swiggy DE
-- Extracted: 2026-01-29 16:55:53
-- ============================================================

WITH base AS (
  SELECT 
    `DE KNID`,
    `Course KNID`,
    `Course Name`,
    `DE ID`,
    `Enrolled At`
  FROM aggregated.course_report cr
  WHERE `Enrolled At` BETWEEN @{{:Enrolled Date Range.START}} AND TIMESTAMP_ADD(@{{:Enrolled Date Range.END}}, INTERVAL 1 DAY)
    AND cr.`Course KNID` IN (
      'rWMPW7eGTtpHD9wTDypiWy', 'v7uo2Q7a3VMHHzxuiqT8v5', 'euXLS4rxqDibRtfcEgPN3u', 'u6RuThw9eEKwJk8xqgdUV8',
      'x8HmS5aJYizC598BRp4cnw', 'gLBethXD5knCV8QpHupuWW', 'iPwVf5PiNfTy3661UJpQim', '8ThPgedutjd4jyK76vNKJe',
      'wZciKzi4xjCy3de7jevNWF', 'aArx8WTBnxiEbSiSsUS9sx', '9NZyKP19WwbjABBs191Lym', '8T7LMgUzPAEo5edWCafBkS',
      'xf3bMeaArckwUQndBesKjV', 'u9JKdGYBTvznEm3kqWAScH', 'sSUPm5DFgXTeEJCTrQ4p4Y', 'ePuWy6eA9eYcM9sGYAMTdC',
      'mfYozWVNx3tCFZnLmiwxgG', '4MABmoEk745MU7VkKHvSUx', 'sh2K9Y1u1CtWBg8bLLx2qf', 'nHjShYAmqwZ8xcDUQtCaXq',
      'pkYBdu5MtCkZZnYRTZwapF', '9Sb88ZKTV4mM8XZiPysgqk', 'dDJNXPwWr8Up9oautGNXvL', '6YtuYvgStuTv7ixD5TkRht',
      'uaQafrSXzDdECpERiy5aYW', 'u2tMHyH9YrvSvV9kow7Xsp', 'pMZY1CYDoEQW9S1FgYVqhs', 'cSZq8PP9MKX7fmNRQKGDYr',
      '3ihCamZbfgp4U6pSJHKDbV', '3RH7QFRzed91V5ek3SBHGp', 'tmjvjjL2ZtC8vS9PTdtubu', 'ozLjazpsoGL6UoheDZBVtN',
      'pkYBdu5MtCkZZnYRTZwapF'
    )
),

answers AS (
  SELECT 
    base.`DE KNID`,
    base.`Course KNID`,
    base.`DE ID`,
    base.`Course Name`,
    base.`Enrolled At`,
    q.cardId,
    q.questionId,
    TIMESTAMP_MILLIS(INT64(q.payload.dt)) AS answeredAt,
    q.isCorrect,
    ROW_NUMBER() OVER (
      PARTITION BY q.courseId, q.cardId, q.questionId, q.userId
      ORDER BY INT64(q.payload.dt) DESC
    ) AS rn
  FROM analytics.quiz_responses q
  JOIN base ON q.courseId = base.`Course KNID` AND q.userId = base.`DE KNID`
),

ke AS (
  SELECT 
    answers.`DE KNID`,
    answers.`Course KNID`,
    answers.`Course Name`,
    answers.`DE ID`,
    answers.`Enrolled At`,
    COUNT(DISTINCT CASE WHEN isCorrect = TRUE THEN cardId || questionId ELSE NULL END) AS correct_questions,
    COUNT(DISTINCT cardId || questionId) AS total_questions,
    COUNT(DISTINCT CASE WHEN isCorrect = TRUE THEN cardId || questionId ELSE NULL END) * 100.0 /
    COUNT(DISTINCT cardId || questionId) AS score
  FROM answers
  WHERE rn = 1
  GROUP BY 1, 2, 3, 4, 5
),

conf AS (
  SELECT 
    courseId AS course_id,
    userId AS user_id,
    SUM(CAST(JSON_VALUE(r, '$.response') AS INT)) * 20 / COUNT(CAST(JSON_VALUE(r, '$.question') AS INT)) AS conf_score
  FROM (
    SELECT sr.*
    FROM `orange-rocket.analytics.survey_responses` sr
    JOIN base ON sr.userId = base.`DE KNID` AND sr.courseId = base.`Course KNID`
  ) s, s.data AS r
  WHERE CAST(JSON_VALUE(r, '$.question') AS INT) < 3
  GROUP BY 1, 2
)

SELECT 
  ke.`Course Name`,
  ke.`DE ID`,
  ke.score AS `KE Score`,
  ke.correct_questions AS `Quiz Score`,
  ke.total_questions AS `Total Quiz Score`,
  conf.conf_score AS `Confidence Score`,
  ke.`Course KNID`,
  ke.`DE KNID`,
  ke.`Enrolled At`
FROM ke
JOIN conf ON conf.course_id = ke.`Course KNID` AND ke.`DE KNID` = conf.user_id
```

---

## Swiggy DE LMS Reports_Swiggy Course Adoption.sql

**Tables referenced:** aggregated.course_report, analytics.lms_raw_analytics, course_sessions, de_course_bucketed, de_course_minutes, de_course_visits

**Columns needing snake_case conversion:**

- `courseId` -> `course_id` (alias: `course_id AS "courseId"`)

- `createdAt` -> `created_at` (alias: `created_at AS "createdAt"`)

- `sessionId` -> `session_id` (alias: `session_id AS "sessionId"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Swiggy DE LMS Reports
-- Dashboard: Swiggy Course Adoption
-- Category: Swiggy DE
-- Extracted: 2026-01-29 16:54:40
-- ============================================================

WITH de_course_visits AS (
  SELECT
    `DE ID`,
    COUNT(DISTINCT `Course KNID`) AS course_count
  FROM aggregated.course_report
  WHERE `Enrolled At` BETWEEN @{{:Enrolled Date Range.START}} AND @{{:Enrolled Date Range.END}}
    AND `status` != 'Not Started'
  GROUP BY `DE ID`
),

de_course_bucketed AS (
  SELECT
    `DE ID`,
    CASE
      WHEN course_count IS NULL THEN 'Visited 0 Course'
      WHEN course_count = 1 THEN 'Visited 1 Course'
      WHEN course_count = 2 THEN 'Visited 2 Courses'
      WHEN course_count = 3 THEN 'Visited 3 Courses'
      WHEN course_count = 4 THEN 'Visited 4 Courses'
      WHEN course_count = 5 THEN 'Visited 5 Courses'
      ELSE 'Visited 6+ Courses'
    END AS course_bucket
  FROM de_course_visits
),

-- ✅ Aggregate sessions per DE & Course
course_sessions AS (
  SELECT
    ra.userId AS user_id,
    ra.courseId AS course_id,
    COUNT(DISTINCT ra.sessionId) AS session_count
  FROM analytics.lms_raw_analytics ra
  WHERE ra.createdAt BETWEEN @{{:Enrolled Date Range.START}} AND @{{:Enrolled Date Range.END}}
  GROUP BY ra.userId, ra.courseId
),

-- ✅ Aggregate mins at DE + Course level first
de_course_minutes AS (
  SELECT
    `DE ID`,
    `Course KNID`,
    SUM(`Mins in Course`) AS course_minutes
  FROM aggregated.course_report
  WHERE `Enrolled At` BETWEEN @{{:Enrolled Date Range.START}} AND @{{:Enrolled Date Range.END}}
    AND `Status` != 'Not Started'
  GROUP BY `DE ID`, `Course KNID`
)

SELECT
  c.`DE ID`,
  c.`DE Name`,
  c.`Course Name`,
  DATETIME(c.`Enrolled At`) AS `Assigned At`,
  c.`Status`,
  c.`Completion %`,
  c.`Score`,
  DATETIME(c.`Completed At`) AS `Completed At`,
  c.`Language`,
  dm.course_minutes AS `Mins in Course`,  -- ✅ Safe aggregated minutes
  c.`DE KNID`,
  c.`Course KNID`,
  c.`Share KNID`,
  cs.session_count,
  cs.course_id,
  1 AS `Assigned`,
  IF(c.`Status` IN ('In Progress', 'Completed'), 1, 0) AS `Started`,
  IF(c.`Status` = 'Completed', 1, 0) AS `Completed`,
  dcb.course_bucket
FROM aggregated.course_report AS c
LEFT JOIN de_course_bucketed dcb ON c.`DE ID` = dcb.`DE ID`
LEFT JOIN de_course_minutes dm ON c.`DE ID` = dm.`DE ID` AND c.`Course KNID` = dm.`Course KNID`
LEFT JOIN course_sessions cs ON c.`DE ID` = cs.user_id AND c.`Course KNID` = cs.course_id
WHERE c.`Enrolled At` BETWEEN @{{:Enrolled Date Range.START}} AND @{{:Enrolled Date Range.END}}
```

---

## Swiggy DE Time Spent_Swiggy Course Adoption.sql

**Tables referenced:** DATA, analytics.lms_callback_analytics, public.users

**Columns needing snake_case conversion:**

- `courseId` -> `course_id` (alias: `course_id AS "courseId"`)

- `firstName` -> `first_name` (alias: `first_name AS "firstName"`)

- `lastName` -> `last_name` (alias: `last_name AS "lastName"`)

- `sessionEndTime` -> `session_end_time` (alias: `session_end_time AS "sessionEndTime"`)

- `sessionId` -> `session_id` (alias: `session_id AS "sessionId"`)

- `sessionStartTime` -> `session_start_time` (alias: `session_start_time AS "sessionStartTime"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Swiggy DE Time Spent
-- Dashboard: Swiggy Course Adoption
-- Category: Swiggy DE
-- Extracted: 2026-01-29 16:54:23
-- ============================================================

WITH DATA AS (
  SELECT 
      userId,
      sessionId,
      UNIX_SECONDS(CAST(sessionStartTime AS TIMESTAMP)) AS starttime,
      UNIX_SECONDS(CAST(sessionEndTime AS TIMESTAMP)) AS endtime,
      ROW_NUMBER() OVER (
          PARTITION BY userId, sessionId
          ORDER BY sessionStartTime DESC
      ) AS rn
  FROM analytics.lms_callback_analytics lca
  WHERE TIMESTAMP_ADD(CAST(sessionStartTime AS TIMESTAMP), INTERVAL 330 MINUTE)
      BETWEEN @{{:Swiggy DE LMS Reports.Enrolled Date Range.START}}
          AND @{{:Swiggy DE LMS Reports.Enrolled Date Range.END}}
    AND courseId NOT IN (
        'mfYozWVNx3tCFZnLmiwxgG','4MABmoEk745MU7VkKHvSUx','sh2K9Y1u1CtWBg8bLLx2qf',
        'nHjShYAmqwZ8xcDUQtCaXq','u2tMHyH9YrvSvV9kow7Xsp','mfYozWVNx3tCFZnLmiwxgG',
        '4MABmoEk745MU7VkKHvSUx','sh2K9Y1u1CtWBg8bLLx2qf','nHjShYAmqwZ8xcDUQtCaXq',
        'euXLS4rxqDibRtfcEgPN3u','v7uo2Q7a3VMHHzxuiqT8v5','u6RuThw9eEKwJk8xqgdUV8',
        'x8HmS5aJYizC598BRp4cnw','gLBethXD5knCV8QpHupuWW','iPwVf5PiNfTy3661UJpQim',
        'pMZY1CYDoEQW9S1FgYVqhs','wZciKzi4xjCy3de7jevNWF','aArx8WTBnxiEbSiSsUS9sx',
        '9NZyKP19WwbjABBs191Lym','8T7LMgUzPAEo5edWCafBkS','xf3bMeaArckwUQndBesKjV',
        'u9JKdGYBTvznEm3kqWAScH','sSUPm5DFgXTeEJCTrQ4p4Y','rWMPW7eGTtpHD9wTDypiWy',
        'cSZq8PP9MKX7fmNRQKGDYr','3ihCamZbfgp4U6pSJHKDbV','3RH7QFRzed91V5ek3SBHGp',
        'tmjvjjL2ZtC8vS9PTdtubu','ozLjazpsoGL6UoheDZBVtN','ePuWy6eA9eYcM9sGYAMTdC',
        'pkYBdu5MtCkZZnYRTZwapF','9Sb88ZKTV4mM8XZiPysgqk','dDJNXPwWr8Up9oautGNXvL',
        '6YtuYvgStuTv7ixD5TkRht','8ThPgedutjd4jyK76vNKJe','uaQafrSXzDdECpERiy5aYW'
    )
)

SELECT 
    u.identifier,
    INITCAP(u.firstName || ' ' || u.lastName) AS user_name,
    SUM(endtime - starttime)/60 AS time_spent_in_sec
FROM DATA d
JOIN public.users u
  ON d.userId = u.userId
WHERE d.rn = 1
GROUP BY u.identifier, user_name
ORDER BY time_spent_in_sec DESC
```

---
