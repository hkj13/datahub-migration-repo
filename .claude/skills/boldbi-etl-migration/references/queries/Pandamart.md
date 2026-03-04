# Pandamart

> Auto-generated on 2026-03-04 08:13

**Total queries:** 1

---

## Pandamart Consolidated Course Report_All Country Course Report.sql

**Tables referenced:** analytics.nugget_analytics_raw, analytics.nuggets_user_share_requests, cards, final_quiz_cards, final_scores, first_course_consumed, full_progress, latest_attempt, latest_course_received, latest_course_shares, latest_received, latest_share_ids, organizations, progress, public.courses, public.learning_journey_courses, public.lesson_cards, public.lessons, public.user_details, quiz.quiz_responses

**Columns needing snake_case conversion:**

- `latestAttempt` -> `latest_attempt` (alias: `latest_attempt AS "latestAttempt"`)

- `qCount` -> `q_count` (alias: `q_count AS "qCount"`)


**Original Query:**

```sql
-- Data Source: Pandamart Consolidated Course Report
-- Dashboard: All Country Course Report
-- Category: Pandamart
-- Extracted: 2026-01-29 16:59:17
-- ============================================================

WITH latest_share_ids AS
  (SELECT DISTINCT ON (nugget_id,
                       share_id,
                       user_id) nugget_id,
                      share_id,
                      user_id,
                      created_at AS sent_at
   FROM analytics.nuggets_user_share_requests nusr
   WHERE created_at AT TIME ZONE 'Asia/Singapore' BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + interval '1 day'
   ORDER BY 1,
            2,
            3,
            created_at DESC),
     latest_course_shares AS
  (SELECT lsi.user_id,
          lsi.nugget_id AS course_id,
          lsi.share_id,
          lsi.sent_at
   FROM latest_share_ids lsi
   JOIN public.courses c ON lsi.nugget_id = c.id
   WHERE c.organization ILIKE 'Pan%'
   UNION ALL SELECT lsi.user_id,
                    ljc.course_id,
                    lsi.share_id,
                    lsi.sent_at
   FROM latest_share_ids lsi
   JOIN public.learning_journey_courses ljc ON lsi.nugget_id = ljc.learning_journey_id
   JOIN public.courses c ON ljc.course_id = c.id),
     latest_received AS
  (SELECT ra.user_id,
          ra.nugget_id,
          ra.share_id,
          ra.created_at AT TIME ZONE 'Asia/Singapore' AS received_at
   FROM analytics.nugget_analytics_raw ra
   JOIN latest_share_ids lsi ON ra.user_id = lsi.user_id
   AND ra.nugget_id = lsi.nugget_id
   AND ra.share_id = lsi.share_id
   WHERE ra.event_id NOT IN (1,
                             7)),
     latest_course_received AS
  (SELECT lr.user_id,
          lr.nugget_id AS course_id,
          lr.share_id,
          min(lr.received_at) AS received_at
   FROM latest_received lr
   JOIN public.courses c ON lr.nugget_id = c.id
   OR lr.nugget_id = c.id
   WHERE c.organization ILIKE 'Pan%'
   GROUP BY 1,
            2,
            3
   UNION ALL SELECT lr.user_id,
                    ljc.course_id,
                    lr.share_id,
                    min(lr.received_at) AS received_at
   FROM latest_received lr
   JOIN public.learning_journey_courses ljc ON lr.nugget_id = ljc.learning_journey_id
   JOIN public.courses c ON ljc.course_id = c.id
   WHERE c.organization ILIKE 'Pan%'
   GROUP BY 1,
            2,
            3),
     cards AS
  (SELECT l.course_id,
          lc.id AS card_id
   FROM public.lesson_cards lc
   JOIN public.lessons l ON l.id = lc.lesson_id
   JOIN public.courses c ON l.course_id = c.id
   WHERE c.organization ILIKE 'Pan%'
   GROUP BY 1,
            2),
     first_course_consumed AS
  (SELECT DISTINCT ON (ra.user_id,
                       ra.course_id,
                       ra.share_id) ra.user_id,
                      ra.course_id,
                      ra.share_id,
                      ra.lang,
                      ra.created_at AT TIME ZONE 'Asia/Singapore' AS consumed_at
   FROM analytics.nugget_analytics_raw ra
   JOIN latest_course_shares lcs ON ra.user_id = lcs.user_id
   AND ra.nugget_id = lcs.course_id
   AND ra.share_id = lcs.share_id
   WHERE ra.event_id = 3
   ORDER BY 1,
            2,
            3,
            ra.created_at),
     full_progress AS
  (SELECT DISTINCT ON (ra.user_id,
                       cards.course_id,
                       cards.card_id) ra.user_id,
                      cards.course_id,
                      cards.card_id,
                      ra.created_at AT TIME ZONE 'Asia/Singapore' AS consumed_at
   FROM analytics.nugget_analytics_raw ra
   JOIN latest_course_shares lcs ON ra.user_id = lcs.user_id
   AND ra.course_id = lcs.course_id
   AND ra.share_id = lcs.share_id
   JOIN cards ON ra.nugget_id = cards.card_id
   LEFT OUTER JOIN first_course_consumed fcc ON ra.user_id = fcc.user_id
   AND ra.course_id = fcc.course_id
   AND ra.share_id = fcc.share_id
   WHERE ra.event_id = 3
     AND (fcc.consumed_at IS NULL
          OR ra.created_at < fcc.consumed_at)
   ORDER BY 1,
            2,
            3,
            ra.created_at),
     progress AS
  (SELECT fp.user_id,
          fp.course_id,
          count(distinct(fp.card_id)) AS consumed_count
   FROM full_progress fp
   GROUP BY 1,
            2),
     final_quiz_cards AS
  (SELECT DISTINCT ON (c.id) c.id AS course_id,
                      lc.id AS quizcard_id,
                      jsonb_array_length(lc.payload -> 'questions') AS qCount
   FROM public.lesson_cards lc
   JOIN public.lessons l ON lc.lesson_id = l.id
   JOIN public.courses c ON l.course_id = c.id
   WHERE c.organization ILIKE 'Pan%'
     AND lc.type = 'quiz'
   ORDER BY c.id,
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
          count(distinct(CASE
                             WHEN qr.is_correct = TRUE THEN qr.question_id
                             ELSE NULL
                         END))::numeric / qc.qCount::numeric AS score
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
            qc.qCount)
SELECT right(o.name, length(o.name) - 10) AS "Country",
       c.name AS "Course Name",
       u.job_location AS "Location",
       u.first_name||' '||u.last_name AS "Staff Name",
       u.identifier AS "Staff ID",
       u.phone_number AS "Phone Number",
       lcs.sent_at AS "Shared At",
       CASE
           WHEN fcc.consumed_at IS NOT NULL
                OR (c.total_cards > 0
                    AND p.consumed_count = c.total_cards) THEN 'Completed'
           WHEN c.total_cards > 0
                AND p.consumed_count > 0
                AND p.consumed_count < c.total_cards THEN 'In Progress'
           WHEN c.total_cards > 0
                AND (p.consumed_count = 0
                     OR p.consumed_count IS NULL) THEN 'Not Started'
           ELSE NULL
       END AS "Status",
       CASE
           WHEN fcc.consumed_at IS NOT NULL THEN 1
           ELSE p.consumed_count / c.total_cards
       END AS "Completion %",
       s.score AS "Final Quiz Score",
       fcc.consumed_at AS "Completed At",
       upper(fcc.lang) AS "Language",
       lcs.user_id AS "User KNID",
       lcs.course_id AS "Course KNID",
       lcs.share_id AS "Share KNID",
       1 AS "Shared",
       CASE
           WHEN fcc.consumed_at IS NOT NULL
                OR (c.total_cards > 0
                    AND p.consumed_count = c.total_cards)
                OR (c.total_cards > 0
                    AND p.consumed_count > 0
                    AND p.consumed_count < c.total_cards) THEN 1
           ELSE 0
       END AS "Started",
       CASE
           WHEN fcc.consumed_at IS NOT NULL
                OR (c.total_cards > 0
                    AND p.consumed_count = c.total_cards) THEN 1
           ELSE 0
       END AS "Completed"
FROM latest_course_shares lcs
LEFT OUTER JOIN latest_course_received lcr ON lcs.user_id = lcr.user_id
AND lcs.course_id = lcr.course_id
LEFT OUTER JOIN progress p ON lcs.user_id = p.user_id
AND lcs.course_id = p.course_id
LEFT OUTER JOIN first_course_consumed fcc ON lcs.user_id = fcc.user_id
AND lcs.course_id = fcc.course_id
LEFT OUTER JOIN final_scores s ON lcs.user_id = s.user_id
AND lcs.course_id = s.course_id
LEFT OUTER JOIN public.courses c ON lcs.course_id = c.id
LEFT OUTER JOIN public.user_details u ON lcs.user_id = u.uuid
JOIN organizations o ON u.organization = o.id
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
         12,
         13,
         14,
         15,
         16,
         c.total_cards,
         p.consumed_count
ORDER BY 1,
         2,
         3,
         4
```

---
