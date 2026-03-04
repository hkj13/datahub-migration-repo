# MyGym

> Auto-generated on 2026-03-04 08:13

**Total queries:** 2

---

## My Gym Course Report_Learn.sql

**Tables referenced:** analytics.nugget_analytics_raw, c, cards, cards_consumed, final_quiz_cards, final_scores, latest_attempt, latest_course_received, latest_course_shares, latest_received, latest_share_ids, nar, organizations, progress, public.courses, public.learning_journey_courses, public.lesson_cards, public.lessons, quiz.quiz_responses, quiz_status, td, user_acl, user_details, user_groups

**Columns needing snake_case conversion:**

- `latestAttempt` -> `latest_attempt` (alias: `latest_attempt AS "latestAttempt"`)

- `passMark` -> `pass_mark` (alias: `pass_mark AS "passMark"`)

- `qCount` -> `q_count` (alias: `q_count AS "qCount"`)


**Original Query:**

```sql
-- Data Source: My Gym Course Report
-- Dashboard: Learn
-- Category: MyGym
-- Extracted: 2026-01-29 16:58:06
-- ============================================================

WITH user_acl AS
  (SELECT ud.organization,
          ud.uuid,
          ud.first_name||' '||ud.last_name AS emp_name,
          ud.identifier AS emp_id,
          ud.division,
          ud.sub_division,
          ud.job_location,
          ud.department,
          ud.designation,
          ud.job_type
   FROM user_details ud
   WHERE organization ='omni-phoenix'
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'All')
     AND job_location NOT ILIKE 'Head Office%'
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid = @{{:UuidParameter}})
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id = @{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10),
     td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'omni-phoenix'),
     c AS
  (SELECT *
   FROM public.courses
   WHERE organization = 'omni-phoenix'),
     nar AS
  (SELECT *
   FROM analytics.nugget_analytics_raw nar
   WHERE created_at BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP + interval '1 day'
     AND nar.course_id IN
       (SELECT id
        FROM c) ),
     latest_share_ids AS
  (SELECT DISTINCT ON (nugget_id,
                       user_id) nugget_id,
                      share_id,
                      user_id,
                      nar.created_at AS sent_at,
                      course_id
   FROM nar
   WHERE event_id IN (1,
                      2,
                      8)
   ORDER BY 1,
            3,
            nar.created_at DESC),
     latest_course_shares AS
  (SELECT lsi.user_id,
          lsi.nugget_id AS course_id,
          lsi.share_id,
          lsi.sent_at,
          1 AS seq
   FROM latest_share_ids lsi
   UNION ALL SELECT lsi.user_id,
                    ljc.course_id,
                    lsi.share_id,
                    lsi.sent_at,
                    (seq::int)+1 AS seq
   FROM latest_share_ids lsi
   JOIN public.learning_journey_courses ljc ON lsi.nugget_id = ljc.learning_journey_id),
     latest_received AS
  (SELECT nar.user_id,
          nar.course_id,
          nar.nugget_id,
          nar.share_id,
          nar.created_at AS received_at
   FROM nar
   JOIN latest_share_ids lsi ON nar.user_id = lsi.user_id
   AND nar.nugget_id = lsi.nugget_id
   OR nar.course_id = lsi.course_id
   AND nar.share_id = lsi.share_id
   WHERE nar.event_id IN (5,
                          8)),
     latest_course_received AS
  (SELECT lr.user_id,
          lr.course_id,
          lr.share_id,
          min(lr.received_at) AS received_at
   FROM latest_received lr
   GROUP BY 1,
            2,
            3
   UNION ALL SELECT lr.user_id,
                    ljc.course_id,
                    lr.share_id,
                    min(lr.received_at) AS received_at
   FROM latest_received lr
   JOIN public.learning_journey_courses ljc ON lr.course_id = ljc.learning_journey_id
   GROUP BY 1,
            2,
            3),
     cards AS
  (SELECT l.course_id,
          lc.id AS card_id
   FROM public.lesson_cards lc
   JOIN public.lessons l ON l.id = lc.lesson_id
   WHERE l.course_id IN
       (SELECT id
        FROM c)
   GROUP BY 1,
            2),
     cards_consumed AS
  (SELECT nar.user_id,
          lcs.seq,
          nar.course_id,
          nar.share_id,
          lc.card_id,
          nar.lang,
          min(nar.created_at) AS consumed_at
   FROM nar
   JOIN latest_course_shares lcs ON nar.user_id = lcs.user_id
   AND nar.course_id = lcs.course_id
   AND nar.share_id = lcs.share_id
   JOIN cards lc ON lc.course_id = nar.course_id
   AND lc.card_id = nar.nugget_id
   WHERE nar.event_id = 3
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6
   ORDER BY 1,
            2,
            3,
            4,
            5),
     progress AS
  (SELECT cc.user_id,
          cc.course_id,
          cc.share_id,
          count(distinct(cc.card_id)) AS consumed_count
   FROM cards_consumed cc
   GROUP BY 1,
            2,
            3),
     final_quiz_cards AS
  (SELECT DISTINCT ON (l.course_id) l.course_id AS course_id,
                      lc.id AS quizcard_id,
                      jsonb_array_length(lc.payload -> 'questions') AS qCount,
                      (lc.settings->>'passMark')::numeric AS pass_mark
   FROM public.lesson_cards lc
   JOIN public.lessons l ON lc.lesson_id = l.id
   WHERE l.course_id IN
       (SELECT id
        FROM c)
     AND lc.type = 'quiz'
   ORDER BY l.course_id,
            l.seq DESC, lc.seq DESC),
     latest_attempt AS
  (SELECT qr.user_id,
          qr.course_id,
          qr.share_id,
          qr.card_id,
          qr.question_id,
          max(attempt) AS latestAttempt
   FROM quiz.quiz_responses qr
   JOIN latest_course_shares lcs ON qr.user_id = lcs.user_id
   AND qr.course_id = lcs.course_id
   AND qr.share_id = lcs.share_id
   JOIN final_quiz_cards qc ON qr.course_id = qc.course_id
   AND qr.card_id = qc.quizcard_id
   GROUP BY 1,
            2,
            3,
            4,
            5),
     final_scores AS
  (SELECT la.user_id,
          la.course_id,
          la.share_id,
          qc.quizcard_id,
          qc.pass_mark,
          qc.qcount,
          count(distinct(CASE
                             WHEN qr.is_correct = TRUE THEN qr.question_id
                             ELSE NULL
                         END))::numeric AS correct_count
   FROM latest_attempt la
   JOIN quiz.quiz_responses qr ON la.user_id = qr.user_id
   AND la.course_id = qr.course_id
   AND la.share_id = qr.share_id
   AND la.card_id = qr.card_id
   AND la.question_id = qr.question_id
   AND la.latestAttempt = qr.attempt
   JOIN final_quiz_cards qc ON qr.course_id = qc.course_id
   AND qr.card_id = qc.quizcard_id
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6),
     quiz_status AS
  (SELECT fs.user_id,
          fs.course_id,
          fs.share_id,
          count(distinct(quizcard_id)) AS no_of_quizzes,
          count(distinct(CASE
                             WHEN correct_count >= pass_mark THEN quizcard_id
                             ELSE NULL
                         END)) AS passed_quizzes,
          sum(correct_count) *100 / sum(qcount) AS score_in_pct
   FROM final_scores fs
   GROUP BY 1,
            2,
            3)
SELECT ud.organization,
       c.name as course_name,
       ud.emp_name,
       ud.emp_id,
       ud.division,
       ud.sub_division,
       ud.job_location AS LOCATION,
       ud.department,
       ud.designation,
       ud.job_type,
       lcs.sent_at + td.diff AS shared_at,
       max(cc.consumed_at + td.diff) AS completed_at,
       CASE
           WHEN (c.total_cards > 0
                 AND p.consumed_count = c.total_cards) THEN 'Completed'
           WHEN c.total_cards > 0
                AND p.consumed_count > 0
                AND p.consumed_count < c.total_cards THEN 'In Progress'
           WHEN c.total_cards > 0
                AND (p.consumed_count = 0
                     OR p.consumed_count IS NULL) THEN 'Not Started'
           ELSE NULL
       END AS course_status,
      CASE
           WHEN (c.total_cards > 0
                 AND p.consumed_count = c.total_cards)
                AND s.no_of_quizzes = 0 THEN 'NA'
           WHEN (c.total_cards > 0
                 AND p.consumed_count = c.total_cards)
                AND s.no_of_quizzes > 0
                AND s.passed_quizzes >= s.no_of_quizzes THEN 'Pass'
           WHEN (c.total_cards > 0
                 AND p.consumed_count = c.total_cards)
                AND s.no_of_quizzes > 0
                AND s.passed_quizzes < s.no_of_quizzes THEN 'Fail'
           ELSE NULL
       END AS quiz_status,
       s.score_in_pct,
       lcs.course_id AS course_knid,
       ud.uuid AS user_knid/*,
       (p.consumed_count::numeric) / (c.total_cards::numeric) AS completion_pct,
       upper(cc.lang) AS LANGUAGE*/
FROM user_acl ud
JOIN latest_course_shares lcs ON lcs.user_id = ud.uuid
LEFT OUTER JOIN latest_course_received lcr ON lcs.user_id = lcr.user_id
AND lcs.course_id = lcr.course_id
AND lcs.share_id = lcr.share_id
LEFT OUTER JOIN progress p ON lcs.user_id = p.user_id
AND lcs.course_id = p.course_id
AND lcs.share_id = p.share_id
LEFT OUTER JOIN cards_consumed cc ON lcs.user_id = cc.user_id
AND lcs.course_id = cc.course_id
AND lcs.share_id = cc.share_id
LEFT OUTER JOIN quiz_status s ON lcs.user_id = s.user_id
AND lcs.course_id = s.course_id
AND lcs.share_id = s.share_id
LEFT OUTER JOIN public.courses c ON lcs.course_id = c.id
LEFT OUTER JOIN td ON ud.organization = td.organization
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10,
         11,
         13,
         14,
         15,
         16,
         17
ORDER BY 1,
         2,
         13,
         5,
         6,
         7,
         3
```

---

## My Gym Hours Worked_Hours Worked Report.sql

**Tables referenced:** organizations, shift_attendance, td, user_acl, user_details, user_groups

**Original Query:**

```sql
-- Data Source: My Gym Hours Worked
-- Dashboard: Hours Worked Report
-- Category: MyGym
-- Extracted: 2026-01-29 16:57:52
-- ============================================================

WITH user_acl AS
  (SELECT ud.organization,
          ud.uuid,
          ud.first_name||' '||ud.last_name AS emp_name,
          ud.identifier AS emp_id,
          ud.division,
          ud.sub_division,
          ud.job_location,
          ud.department,
          ud.designation,
          ud.job_type
   FROM user_details ud
   WHERE organization ='omni-phoenix'
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'All')
     AND job_location NOT ILIKE 'Head Office%'
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid = @{{:UuidParameter}})
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id = @{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10),
     td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'omni-phoenix')
   SELECT "Sub Division" as "Franchisee",
       "Home Location" as "Location",
       "Employee Name",
       "Employee ID",
       "Designation",
       "Department",
       "Job Type",
       "Employee Status",
       "UUID",
	   (@{{:Date Range.START}}::timestamp)::date as "Period From",
	   (@{{:Date Range.END}}::timestamp)::date as "Period To",
       sum("Actual Work Duration") AS "Total Worked Hours",
       count(distinct(CASE
                          WHEN "Present Count" > 0 THEN ("Scheduled Start Time" AT TIME ZONE 'UTC')::date
                          ELSE NULL
                      END)) AS "Total Days Worked",
       count(distinct(CASE
                          WHEN "Leave Count" > 0 THEN ("Scheduled Start Time" AT TIME ZONE 'UTC')::date
                          ELSE NULL
                      END)) AS "Total Days on Leave, including Off Days",
       sum("Absent Count") AS "No of Shifts Missed",
       sum("Late Count") AS "No of Late Shifts"
FROM shift_attendance sa
join user_acl on sa."UUID" = user_acl.uuid
join td on sa.organization = td.organization
WHERE sa.organization = 'omni-phoenix'
  AND "Scheduled Start Time" AT TIME ZONE 'UTC' + td.diff BETWEEN @{{:Date Range.START}}::timestamp + td.diff and @{{:Date Range.END}}::timestamp + interval '1 day' + td.diff
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
		 10,
		 11
ORDER BY 1,
         2,
         3,
         4
```

---
