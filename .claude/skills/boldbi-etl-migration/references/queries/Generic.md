# Generic

> Auto-generated on 2026-03-04 08:13

**Total queries:** 23

---

## Audit Details_Audits.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, location_acl, organizations, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Audit Details
-- Dashboard: Audits
-- Category: Generic
-- Extracted: 2026-01-29 16:55:37
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
     --AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'HQ',
                              'Head Office',
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
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
     td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = @{{:OrganizationParameter}}),
     base AS
  (SELECT organization_id,
          CASE
              WHEN result_score = '' THEN NULL
              ELSE result_score::numeric
          END AS result_score,
          CASE
              WHEN max_score = '' THEN NULL
              ELSE max_score::numeric
          END AS max_score,
          store_id,
          audit_main_theme,
          theme,
          audit_submitted_at,
          audit_submission_number,
          audit_submission_knid,
          auditor_name,
          checkpoint_knid,
          CHECKPOINT,
          RESULT,
          criticality,
          is_critical_question_failed,
          auditor_observations,
          total_follow_up_tasks,
          total_closed_follow_up_tasks,
          CASE
              WHEN result_score = '' THEN 'Not checked'
              WHEN result_score::numeric < max_score::numeric THEN 'Failed'
              ELSE 'Passed'
          END AS status,
                              row_number() OVER (PARTITION BY store_id,
                                       audit_main_theme,
                                       theme, checkpoint_knid,
                                       extract('Year'
                  FROM audit_submitted_at)
                          ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM checkpoint_master_sheet_table cms
   JOIN td ON cms.organization_id = td.organization
   join location_acl on cms.store_id = location_acl.job_location
   WHERE organization_id = @{{:OrganizationParameter}}
  and audit_submitted_at >= '2025-01-01'
 )
SELECT organization_id AS "Org",
       store_id AS "Location",
       audit_main_theme AS "Audit",
       audit_submitted_at AS "Audit Date",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
       auditor_name AS "Auditor",
	   theme as "Theme",
       checkpoint_knid as "Checkpoint KNID",
	   checkpoint as "Checkpoint",
	   result as "Result",
	   status as "Checkpoint Status",
	   auditor_observations as "Auditor Notes",
	   result_score as "Actual Score",
	   max_score as "Max Score",
	   criticality as "Criticality",
       total_follow_up_tasks AS "Total Follow Ups",
       total_closed_follow_up_tasks AS "Total Closed Follow Ups",
       "Audit No in Year"
FROM base
group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19
ORDER BY 1,
         2,
         4
```

---

## Audit Summary_Audits.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, location_acl, organizations, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Audit Summary
-- Dashboard: Audits
-- Category: Generic
-- Extracted: 2026-01-29 16:55:38
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
    -- AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'HQ',
                              'Head Office',
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
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
     td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = @{{:OrganizationParameter}}),
     base AS
  (SELECT organization_id,
          CASE
              WHEN result_score = '' THEN NULL
              ELSE result_score::numeric
          END AS result_score,
          CASE
              WHEN max_score = '' THEN NULL
              ELSE max_score::numeric
          END AS max_score,
          store_id,
          audit_main_theme,
          theme,
          audit_submitted_at,
          audit_submission_number,
          audit_submission_knid,
          auditor_name,
          checkpoint_knid,
          CHECKPOINT,
          RESULT,
          criticality,
          is_critical_question_failed,
          auditor_observations,
          total_follow_up_tasks,
          total_closed_follow_up_tasks,
          CASE
              WHEN result_score = '' THEN 'Not checked'
              WHEN result_score::numeric < max_score::numeric THEN 'Failed'
              ELSE 'Passed'
          END AS status,
                              row_number() OVER (PARTITION BY store_id,
                                       audit_main_theme,
                                       theme, checkpoint_knid,
                                       extract('Year'
                  FROM audit_submitted_at)
                          ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM checkpoint_master_sheet_table cms
   JOIN td ON cms.organization_id = td.organization
   join location_acl on cms.store_id = location_acl.job_location
   WHERE organization_id = @{{:OrganizationParameter}}
  and audit_submitted_at between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day' )
SELECT organization_id AS "Org",
       store_id AS "Location",
       audit_main_theme AS "Audit",
       audit_submitted_at AS "Audit Date",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
       auditor_name AS "Auditor",
       sum(result_score) as "Actual Score",
	   sum(max_score) as "Max Score",
	   sum(result_score)/sum(max_score) AS "Audit Score",
       count(CASE
                 WHEN is_critical_question_failed = 'true' THEN checkpoint_knid
                 ELSE NULL
             END) AS "Critical Failed Count",
       sum(total_follow_up_tasks) AS "Total Follow Ups",
       sum(total_closed_follow_up_tasks) AS "Total Closed Follow Ups",
       "Audit No in Year"
FROM location_acl acl
LEFT OUTER JOIN base ON acl.job_location = base.store_id
group by 1, 2, 3, 4, 5, 6, 7, 14
ORDER BY 1,
         2,
         4
```

---

## Compliments Report_Compliments Report.sql

**Tables referenced:** base, form_responses, form_submissions, location_acl, organizations, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Compliments Report
-- Dashboard: Compliments Report
-- Category: Generic
-- Extracted: 2026-01-29 16:59:29
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
   and is_active = 'true'
  and job_location not in ('KNOW', 'HQ', 'Head Office', 'All')
   and job_location not ilike 'Head Office%'
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
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = @{{:OrganizationParameter}}),
base  as (SELECT (submit_date + td.diff)::date AS date,
          max(CASE
                  WHEN question_id = 'section-1' THEN response -> 'sender' ->> 'userId'
                  ELSE NULL
              END) AS giver,
          max(CASE
                  WHEN question_id = '-notes' THEN response ->> 0
                  ELSE NULL
              END) AS compliment,
          max(CASE
                  WHEN question_id = '-compliment-type' THEN response -> 'selected' ->> 0
                  ELSE NULL
              END) AS compliment_type,
          max(CASE
                  WHEN question_id = '-compliment-to' THEN response -> 0 -> 'contact' ->> 'userId'
                  ELSE NULL
              END) AS recipient,
          form_submissions.id AS compliment_id
   FROM form_responses
   JOIN form_submissions ON form_responses.form_submit_id = form_submissions.id
		  join td on form_submissions.organization = td.organization
   WHERE submit_date + td.diff > current_timestamp - interval '6 months'
     AND form_submissions.form_id = '-compliment-form'
     AND form_submissions.organization = @{{:OrganizationParameter}}
        GROUP BY 1,
            form_submit_id,
            6)
			
			SELECT base.date AS "Compliment Date",
       base.compliment_type AS "Compliment Type",
       base.compliment AS "Compliment",
       recipient_details.first_name||recipient_details.last_name AS "Compliment Recipient Name",
       recipient_details.identifier AS "Compliment Recipient Employee ID",
       recipient_details.designation as "Compliment Recipient Designation",
       recipient_details.job_location AS "Compliment Recipient Outlet",
	   giver_details.first_name||giver_details.last_name AS "Compliment Giver Name",
       giver_details.identifier AS "Compliment Giver Employee ID",
       giver_details.designation as "Compliment Giver Designation",
       giver_details.job_location AS "Compliment Giver Outlet",
       base.compliment_id AS "Compliment Submit ID (KNOW Internal)"
	   from base
	   JOIN user_details giver_details ON base.giver = giver_details.uuid
JOIN user_details recipient_details ON base.recipient = recipient_details.uuid
join location_acl loc on loc.job_location = giver_details.job_location or loc.job_location = recipient_details.job_location
order by 1 desc, 2, 4, 8
```

---

## Course Report_Learn.sql

**Tables referenced:** analytics.nugget_analytics_raw, analytics.nuggets_user_share_requests, cards, cards_consumed, final_quiz_cards, final_scores, latest_attempt, latest_course_received, latest_course_shares, latest_received, latest_share_ids, organizations, progress, public.courses, public.learning_journey_courses, public.lesson_cards, public.lessons, quiz.quiz_responses, quiz_status, td, user_acl, user_details, user_groups

**Columns needing snake_case conversion:**

- `latestAttempt` -> `latest_attempt` (alias: `latest_attempt AS "latestAttempt"`)

- `passMark` -> `pass_mark` (alias: `pass_mark AS "passMark"`)

- `qCount` -> `q_count` (alias: `q_count AS "qCount"`)


**Original Query:**

```sql
-- Data Source: Course Report
-- Dashboard: Learn
-- Category: Generic
-- Extracted: 2026-01-29 16:53:03
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
   WHERE organization = @{{:OrganizationParameter}}
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
                  WHERE ug2.user_id =@{{:UuidParameter}}
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
   WHERE id = @{{:OrganizationParameter}}),
     latest_share_ids AS
  (SELECT DISTINCT ON (nugget_id,
                       user_id) nugget_id,
                      share_id,
                      user_id,
                      created_at AS sent_at
   FROM analytics.nuggets_user_share_requests nusr
   JOIN user_acl ud ON nusr.user_id = ud.uuid
   WHERE created_at BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP + interval '1 day'
   ORDER BY 1,
            3,
            created_at DESC),
     latest_course_shares AS
  (SELECT lsi.user_id,
          lsi.nugget_id AS course_id,
          lsi.share_id,
          lsi.sent_at,
          1 AS seq
   FROM latest_share_ids lsi
   JOIN public.courses c ON lsi.nugget_id = c.id
   WHERE c.organization = @{{:OrganizationParameter}}
   UNION ALL SELECT lsi.user_id,
                    ljc.course_id,
                    lsi.share_id,
                    lsi.sent_at,
                    (seq::int)+1 AS seq
   FROM latest_share_ids lsi
   JOIN public.learning_journey_courses ljc ON lsi.nugget_id = ljc.learning_journey_id
   JOIN public.courses c ON ljc.course_id = c.id),
     latest_received AS
  (SELECT ra.user_id,
          ra.nugget_id,
          ra.share_id,
          ra.created_at AS received_at
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
   WHERE c.organization = @{{:OrganizationParameter}}
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
   WHERE c.organization = @{{:OrganizationParameter}}
   GROUP BY 1,
            2,
            3),
     cards AS
  (SELECT l.course_id,
          lc.id AS card_id
   FROM public.lesson_cards lc
   JOIN public.lessons l ON l.id = lc.lesson_id
   JOIN public.courses c ON l.course_id = c.id
   WHERE c.organization = @{{:OrganizationParameter}}
   GROUP BY 1,
            2),
     cards_consumed AS
  (SELECT ra.user_id,
          lcs.seq,
          ra.course_id,
          ra.share_id,
          lc.card_id,
          ra.lang,
          min(ra.created_at) AS consumed_at
   FROM analytics.nugget_analytics_raw ra
   JOIN latest_course_shares lcs ON ra.user_id = lcs.user_id
   AND ra.course_id = lcs.course_id
   AND ra.share_id = lcs.share_id
   JOIN cards lc ON lc.course_id = ra.course_id
   AND lc.card_id = ra.nugget_id
   WHERE ra.event_id = 3
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
  (SELECT DISTINCT ON (c.id) c.id AS course_id,
                      lc.id AS quizcard_id,
                      jsonb_array_length(lc.payload -> 'questions') AS qCount,
                      (lc.settings->>'passMark')::numeric AS pass_mark
   FROM public.lesson_cards lc
   JOIN public.lessons l ON lc.lesson_id = l.id
   JOIN public.courses c ON l.course_id = c.id
   WHERE c.organization = @{{:OrganizationParameter}}
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

## Course Report_large data_Learn (L).sql

**Tables referenced:** analytics.nuggets_user_progress, course_report_1, courses, organizations, quiz_report, td, user_acl, user_details, user_groups

**Columns needing snake_case conversion:**

- `courseStatus` -> `course_status` (alias: `course_status AS "courseStatus"`)

- `inProgress` -> `in_progress` (alias: `in_progress AS "inProgress"`)

- `noOfCorrectAnswer` -> `no_of_correct_answer` (alias: `no_of_correct_answer AS "noOfCorrectAnswer"`)

- `noOfQuestionAnswered` -> `no_of_question_answered` (alias: `no_of_question_answered AS "noOfQuestionAnswered"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `quizStatus` -> `quiz_status` (alias: `quiz_status AS "quizStatus"`)


**Original Query:**

```sql
-- Data Source: Course Report_large data
-- Dashboard: Learn (L)
-- Category: Generic
-- Extracted: 2026-01-29 16:58:59
-- ============================================================

WITH user_acl AS
  (SELECT DISTINCT uuid
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
   and is_active = 'true'
  and job_location not in ('KNOW', 'All')
   and job_location not ilike 'Head Office%'
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
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
  where id = @{{:OrganizationParameter}}),
     course_report_1 AS
  (SELECT ud.organization,
          nup.nugget_id,
          nup.user_id,
          ud.first_name||' '||ud.last_name AS emp_name,
          ud.identifier AS emp_id,
          ud.division,
          ud.sub_division,
          ud.job_location,
          ud.department,
          ud.designation,
          ud.job_type,
          c.name,
          nup.created_at + td.diff AS shared_at,
          to_timestamp(min(CASE
                               WHEN base.sessions -> session_id ->> 'courseStatus' = 'completed' THEN (base.sessions->session_id->>'end')::bigint + tzoffset*60000
                               ELSE NULL
                           END)/1000) AS completed_at,
          least(min(base.sessions -> session_id ->> 'courseStatus'), min(nup.status)) AS status,
          nup.quiz_status,
          count(distinct(base.session_id)) AS no_of_times,
          sum(CASE
                  WHEN base.sessions -> session_id ->> 'end' IS NOT NULL
                       AND base.sessions -> session_id ->> 'start' IS NOT NULL THEN (base.sessions->session_id->>'end')::bigint - (base.sessions->session_id->>'start')::bigint
                  ELSE 0
              END)/1000/60 AS time_spent
   FROM analytics.nuggets_user_progress nup
   LEFT OUTER JOIN
     (SELECT nup.nugget_id,
             nup.user_id,
             jsonb_object_keys(nup.sessions) AS session_id,
             nup.sessions
      FROM user_details ud
      LEFT OUTER JOIN analytics.nuggets_user_progress nup ON nup.user_id = ud.uuid
      JOIN courses c ON nup.nugget_id = c.id
	  where nup.created_at between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
	 ) base ON nup.nugget_id = base.nugget_id
   AND nup.user_id = base.user_id
   JOIN user_details ud ON nup.user_id = ud.uuid
   JOIN courses c ON nup.nugget_id = c.id
   JOIN td ON ud.organization = td.organization
   where ud.organization = @{{:OrganizationParameter}}
   and c.is_archived = 'false'
   and nup.created_at between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
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
            16),
     quiz_report AS
  (SELECT nugget_id,
          user_id,
          quiz_card_id,
          quiz_cards->quiz_card_id->>'quizStatus' AS quiz_status,
                                     sum((quiz_cards->quiz_card_id->'noOfQuestionAnswered')::int) AS no_of_q_ans,
                                     sum((quiz_cards->quiz_card_id->'noOfCorrectAnswer')::int) AS no_of_correct
   FROM
     (SELECT nup.nugget_id,
             nup.user_id,
             nup.status,
             jsonb_object_keys(nup.quiz_cards) AS quiz_card_id,
             nup.quiz_cards
      FROM analytics.nuggets_user_progress nup
      JOIN user_details ud ON nup.user_id = ud.uuid
      JOIN courses c ON nup.nugget_id = c.id
	 where c.organization = @{{:OrganizationParameter}}
	 and c.is_archived = 'false'
	 and nup.created_at between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day') base
   GROUP BY 1,
            2,
            3,
            4)
SELECT cr.organization,
       cr.name AS course_name,
       cr.emp_name,
       cr.emp_id,
       cr.division,
       cr.sub_division,
       cr.job_location AS LOCATION,
       cr.department,
       cr.designation,
       cr.job_type,
       cr.shared_at,
       cr.completed_at,
       CASE
           WHEN cr.status = 'completed' THEN 'Completed'
           WHEN cr.status = 'inProgress' THEN 'In Progress'
           WHEN cr.status = 'notStarted' THEN 'Not Started'
           WHEN cr.status = 'sent' THEN 'Not Started'
           ELSE NULL
       END AS course_status,
       upper(left(min(qr.quiz_status), 1))||right(min(qr.quiz_status), length(min(qr.quiz_status))-1) AS quiz_status,
       CASE
           WHEN qr.no_of_q_ans > 0 THEN qr.no_of_correct * 100 / qr.no_of_q_ans
           ELSE NULL
       END AS score_in_pct,
       cr.no_of_times AS no_of_visits_to_course,
       cr.time_spent AS total_time_spent_mins,
       cr.nugget_id AS course_knid,
       cr.user_id AS user_knid
FROM user_acl
join course_report_1 cr on cr.user_id = user_acl.uuid
LEFT OUTER JOIN quiz_report qr ON cr.nugget_id = qr.nugget_id
AND cr.user_id = qr.user_id
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
         15,
         16,
         17,
         18,
         19
ORDER BY 1,
         2,
         13,
         5,
         6,
         7,
         3
```

---

## Daily Compliance Report_Daily Compliance Report.sql

**Tables referenced:** form_compliance, location_acl, nuggets, organizations, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Daily Compliance Report
-- Dashboard: Daily Compliance Report
-- Category: Generic
-- Extracted: 2026-01-29 16:59:21
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
   and is_active = 'true'
   and job_location not in ('KNOW', 'HQ', 'Head Office', 'All')
   and job_location not ilike 'Head Office%'
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
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = @{{:OrganizationParameter}})
select distinct on (fc.organization, fc.form_id, fc.job_location, fc.reminded_at)
fc.organization as "Organization",
@{{:Date}}::date as "Date",
fc.form_id as "Routine KNID",
n.title as "Routine Name",
fc.job_location as "Location",
fc.reminded_at + td.diff as "Reminded At",
case when fc.responded_at is not null then 1.00 else 0.00 end as "Complied"
from form_compliance fc
join location_acl on fc.job_location = location_acl.job_location
join td on td.organization = fc.organization
join nuggets n on fc.form_id = n.id
where fc.organization =@{{:OrganizationParameter}}
and date_trunc('Day', fc.reminded_At + td.diff) = date_trunc('Day', @{{:Date}}::timestamp + td.diff)
order by fc.organization, fc.form_id, fc.job_location, fc.reminded_at, fc.responded_at
```

---

## Forms Analytics Generic_Submissions Analytics.sql

**Tables referenced:** form_responses, form_submissions, forms, fr, fr_location, fs, location_acl, nuggets, organizations, question_definitions, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `endDate` -> `end_date` (alias: `end_date AS "endDate"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `startDate` -> `start_date` (alias: `start_date AS "startDate"`)


**Original Query:**

```sql
-- Data Source: Forms Analytics Generic
-- Dashboard: Submissions Analytics
-- Category: Generic
-- Extracted: 2026-01-29 16:57:19
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
   and is_active = 'true'
   and job_location not in ('KNOW', 'All')
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
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = @{{:OrganizationParameter}}),
			   forms as (select * from nuggets where id = @{{:formId}}),
						fs AS
  (SELECT DISTINCT ON (response_id) fs2.*
   FROM form_submissions fs2
   JOIN forms ON forms.id = fs2.form_id
   JOIN td ON fs2.organization = td.organization
   WHERE submit_date + td.diff between @{{:startDate}}::timestamp and @{{:endDate}}::timestamp + interval '1 day'
   ORDER BY response_id,
            fs2.id),
     fr_location AS
  (SELECT DISTINCT ON (fs.response_id) fs.response_id,
                      fr.response->>'name' AS fr_location
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   JOIN question_definitions qd ON fr.question_id = qd.question_id
   AND fs.form_id = qd.nugget_id
   WHERE qd.question_type = 'location'
   ORDER BY fs.response_id,
            fs.id,
            qd.section_id,
            qd.sqno),
     fr AS
  (SELECT fs.response_Id,
          fs.form_id,
          fs.id,
          fs.sno,
          fs.submit_date,
          fs.organization,
          fs.user_id,
          CASE
              WHEN fr_location.fr_location IS NULL THEN fs.location
              ELSE fr_location.fr_location
          END AS LOCATION
   FROM fs
   LEFT OUTER JOIN fr_location ON fs.response_id = fr_location.response_id)
SELECT forms.title AS "Form Title",
       forms.id AS "Form KNID",
       fr.response_id AS "Response KNID",
       fr.sno AS "Submission No",
       fr.submit_date + td.diff AS "Submitted At",
       fr.location AS "Form Location",
       ud.identifier AS "Submitter ID",
       ud.uuid AS "Submitter KNID",
       ud.first_name||' '||ud.last_name AS "Submitter Name",
       ud.division AS "Submitter Division",
       ud.sub_division AS "Submitter Sub Division",
       ud.job_location AS "Submitter Location",
       ud.department AS "Submitter Department",
       ud.designation AS "Submitter Designation",
       ud.job_type AS "Submitter Job Type"
FROM fr 
LEFT OUTER JOIN location_acl la ON fr.location = la.job_location
LEFT OUTER JOIN forms ON fr.form_id = forms.id
LEFT OUTER JOIN td ON fr.organization = td.organization
LEFT OUTER JOIN user_details ud ON fr.user_id = ud.uuid
ORDER BY 1,
         6,
         5
```

---

## Kitopi Follow up Tasks Summary-copy_1734086260_Kishore - Follow Ups.sql

**Tables referenced:** checkpoint_master_sheet_table, cms, cms_theme_score, cmscp, final_definition, form_responses, form_submissions, forms, fr, fs, fu, hse_obs, jsonb_Each, location_acl, location_map, nuggets, organizations, qd_non_table_with_logic, qdntwl_prework, question_definitions, t, tasks, td, tfq, user_details, user_groups

**Columns needing snake_case conversion:**

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `formDetails` -> `form_details` (alias: `form_details AS "formDetails"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `isAudit` -> `is_audit` (alias: `is_audit AS "isAudit"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)


**Original Query:**

```sql
-- Data Source: Kitopi Follow up Tasks Summary-copy_1734086260
-- Dashboard: Kishore - Follow Ups
-- Category: Generic
-- Extracted: 2026-01-29 16:57:42
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'HQ',
                              'Head Office',
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
               AND ug1.is_active = TRUE))),
    td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'kitopi-pegasus'),
     location_map AS
  (SELECT DISTINCT ON (job_location) job_location,
                      division AS country,
                      sub_division AS team,
                      designation AS CLUSTER
   FROM user_details
   WHERE is_active = 'true'
     AND organization = 'kitopi-pegasus'
     AND job_type IN ('CK',
                      'SK',
                      'Kitchen',
                      'Warehouse')
   ORDER BY job_location,
            created_at ASC),
     t AS
  (SELECT t.id AS "Task KNID",
          t.organization AS "Org",
          t.ext_id AS "Task ID",
          t.title AS "Task",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Closed'
              WHEN t.status ilike 'notStarted'
                   AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 'Overdue'
              WHEN t.status ILIKE 'notStarted'
                   AND to_timestamp(t.deadline/1000) >= CURRENT_TIMESTAMP THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened')
                   THEN 'In Progress'
          END AS "Status",
          CASE
              WHEN t.details->'formDetails'->>'name' ~* ' - (INTL|UAE)' THEN regexp_replace(t.details->'formDetails'->>'name', '(?i)( - (INTL|UAE)).*$', '')
              WHEN t.details->'formDetails'->>'name' ~ '\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$' THEN regexp_replace(t.details->'formDetails'->>'name', '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '')
              ELSE t.details->'formDetails'->>'name'
          END AS "Trigger Form",
          t.details->'formDetails'->>'formId' AS "Trigger Form KNID",
                                     t.details->'formDetails'->>'responseId' AS "Trigger Form Submission KNID",
                                                                t.details->'formDetails'->>'sno' AS "Trigger Form Submission No",
                                                                                           initcap(t.details->>'authorName') AS "Assigned By",
                                                                                           initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                           initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                           initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                           to_timestamp(t.created_at/1000) + td.diff AS "Assigned At",
                                                                                           to_timestamp(t.deadline/1000) + td.diff AS "Deadline",
                                                                                           CASE
                                                                                               WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) + td.diff
                                                                                           END AS "Started At",
                                                                                           CASE
                                                                                               WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) + td.diff
                                                                                               ELSE NULL
                                                                                           END AS "Completed At",
                                                                                           CASE
                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                    OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) + td.diff
                                                                                               ELSE NULL
                                                                                           END AS "Reopened At",
                                                                                           CASE
                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                               ELSE 0
                                                                                           END AS "Overdue Count",
                                                                                           CASE
                                                                                               WHEN t.status ILIKE 'notStarted'
                                                                                                    AND to_timestamp(t.deadline/1000) >= CURRENT_TIMESTAMP THEN 1
                                                                                               ELSE 0
                                                                                           END AS "Not Started Count",
                                                                                           CASE
                                                                                               WHEN (t.status ILIKE 'started'
                                                                                                     OR t.status ILIKE 'reopened')
                                                                                                    AND to_timestamp(t.deadline/1000) >= CURRENT_TIMESTAMP THEN 1
                                                                                               ELSE 0
                                                                                           END AS "In Progress Count",
                                                                                           CASE
                                                                                               WHEN t.status ILIKE 'completed' THEN 1
                                                                                               ELSE 0
                                                                                           END AS "Completed Count",
                                                                                           CASE
                                                                                               WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                               ELSE 0
                                                                                           END AS "Reopened Count",
                                                                                           split_part(t.details->'formDetails'->>'path', '/', 1) AS theme_knid,
                                                                                           split_part(t.details->'formDetails'->>'path', '/', 2) AS checkpoint_knid
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   JOIN td ON t.organization = td.organization
   WHERE t.organization = 'kitopi-pegasus'
     AND t.is_deleted = 'false'
     AND t.details->'formDetails'->>'formId' IS NOT NULL
     AND to_timestamp(t.created_at/1000) + td.diff BETWEEN @{{:Date Range.START}}::TIMESTAMP + td.diff AND @{{:Date Range.END}}::TIMESTAMP + td.diff),
     tfq AS
  (SELECT qd.nugget_id AS form_knid,
          qd.question_id AS theme_knid,
          qd.question AS theme,
          q.key AS checkpoint_knid,
          q.value->>'question' AS CHECKPOINT
   FROM question_definitions qd,
        LATERAL jsonb_each(qd.definition->'questions') AS q
   WHERE qd.question_type = 'nested'),
     cms AS
  (SELECT store_id,
          audit_submission_knid
   FROM checkpoint_master_sheet_table
   WHERE organization_id = 'kitopi-pegasus'
   GROUP BY 1,
            2),
     fu AS
  (SELECT location_map.country AS "Country",
          location_map.team AS "Team",
          location_map.cluster AS "Cluster",
          cms.store_id AS "Location",
          "Trigger Form",
          "Trigger Form Submission No",
          tfq.theme AS "Theme",
          tfq.checkpoint AS "Checkpoint",
          "Status",
          "Assigned At",
          "Deadline",
          "Started At",
          "Completed At",
          "Reopened At",
          "Assigned By",
          "Started By",
          "Completed By",
          "Reopened By",
          "Overdue Count",
          "Not Started Count",
          "In Progress Count",
          "Completed Count",
          "Reopened Count",
          "Task KNID",
          "Org",
          "Task ID",
          "Task",
          "Trigger Form KNID",
          "Trigger Form Submission KNID",
          tfq.theme_knid AS "Theme KNID",
          tfq.checkpoint_knid AS "Checkpoint KNID"
   FROM t
   LEFT OUTER JOIN tfq ON t."Trigger Form KNID" = tfq.form_knid
   AND t.theme_knid = tfq.theme_knid
   AND t.checkpoint_knid = tfq.checkpoint_knid
   LEFT OUTER JOIN cms ON t."Trigger Form Submission KNID" = cms.audit_submission_knid
   join location_acl on cms.store_id = location_acl.job_location
   JOIN location_map ON cms.store_id = location_map.job_location
   ORDER BY 10 DESC, 9 DESC, 1,
                             2,
                             3,
                             4,
                             5,
                             7,
                             8),
							 /*Getting observations for Health and Safety ASsessments*/ forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ILIKE 'A8. Health%'
     AND details->>'isAudit' = 'true'
     AND is_deleted = 'false'),
                                                                                            qd AS
  (SELECT qd.nugget_id AS form_id,
          jsonb_object_keys((jsonb_array_elements(definition->'logic'))->'questions') qids
   FROM question_definitions qd
   JOIN forms qf ON qd.nugget_id = qf.form_knid
   WHERE qd.question_type IN ('dropdown',
                              'multiple_choice',
                              'nested',
                              'audit')),
                                                                                            qdntwl_prework AS
  (SELECT *,
          jsonb_array_elements(definition -> 'logic') -> 'questions' q
   FROM forms
   JOIN question_definitions qd ON qd.nugget_id = forms.form_knid
   WHERE qd.definition -> 'logic' IS NOT NULL),
                                                                                            qd_non_table_with_logic AS
  (/*Non Table type Questions in Forms with Logic - SqNo will be in between the parent SqNo for sub questions*/ SELECT nugget_id AS form_knid,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
                                                                                            final_definition AS
  (SELECT *
   FROM qd_non_table_with_logic
   WHERE question ILIKE '%finding%'
     OR question ILIKE '%comment%'
     OR question ILIKE '%remark%'
     OR question ILIKE '%observation%'
   ORDER BY 1,
            2,
            3,
            5 DESC, 7 DESC),
                                                                                            fs AS
  (SELECT DISTINCT ON (response_id) *
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   where form_submissions.submit_date > @{{:Date Range.START}}::timestamp
   ORDER BY response_id,
            id DESC),
                                                                                            fr AS
  (SELECT *
   FROM form_responses fr
   JOIN fs ON fr.form_submit_id = fs.id),
                                                                                            hse_obs AS
  ( SELECT fr.sno,
           fd.parent_qid,
           fd.question,
           CASE
               WHEN fd.q_type IN ('dropdown',
                                  'multiple_choice')
                    AND fr.response -> 'selected'->>0 ILIKE 'other' THEN fr.response -> 'otherText'->>0
               WHEN fd.q_type IN ('dropdown',
                                  'multiple_choice')
                    AND fr.response -> 'selected'->>0 NOT ILIKE 'other' THEN fr.response -> 'selected'->>0
               WHEN fd.q_type IN ('checkboxes') THEN array_to_string(ARRAY
                                                                       (SELECT jsonb_array_elements_text(fr.response->'selected')
                                                                        UNION SELECT CASE
                                                                                         WHEN fr.response->>'otherText' IS NOT NULL THEN fr.response->>'otherText'
                                                                                         ELSE NULL
                                                                                     END), ', ')
               WHEN fd.q_type IN ('long_text_field',
                                  'single_text_field',
                                  'qr_code') THEN fr.response->>0
               ELSE NULL
           END AS response,
           form_name,
           fd.form_knid,
           fr.response_id
   FROM final_definition fd
   JOIN fr ON fr.question_id = fd.qid
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7
   ORDER BY 1,
            2,
            3),
                                                                                            cmscp AS
  (SELECT audit_submission_knid,
          checkpoint_knid,
          RESULT,
          CASE
              WHEN hse_obs.response IS NOT NULL THEN hse_obs.response
              ELSE auditor_observations
          END AS auditor_observations
   FROM checkpoint_master_sheet_table cms
   LEFT OUTER JOIN hse_obs ON cms.audit_submission_knid = hse_obs.response_id
   AND cms.checkpoint_knid = hse_obs.parent_qid
   WHERE organization_id = 'kitopi-pegasus'
     AND audit_submitted_at > @{{:Date Range.START}}::TIMESTAMP --AND auditor_observations IS NOT NULL
 ),
                                                                                            cms_theme_score AS
  (SELECT audit_submission_knid,
          theme,
          audit_submitted_At,
          sum(CASE
                  WHEN result_score = '' THEN NULL
                  ELSE result_score::numeric
              END)/sum(CASE
                           WHEN max_score = '' THEN NULL
                           ELSE max_score::numeric
                       END) AS theme_score
   FROM checkpoint_master_sheet_table
   WHERE organization_id = 'kitopi-pegasus'
     AND audit_submitted_at > @{{:Date Range.START}}::TIMESTAMP
   GROUP BY 1,
            2,
            3)
SELECT fu."Country",
       fu."Team",
       fu."Cluster",
       fu."Location",
       fu."Trigger Form",
       fu."Trigger Form Submission No",
	   cmsts.audit_submitted_at as "Audit Date",
       fu."Theme",
       cmsts.theme_score AS "Theme Score",
       fu."Checkpoint",
       cmscp.result AS "Result",
       cmscp.auditor_observations AS "Observation",
       fu."Status",
       fu."Assigned At",
       fu."Deadline",
       fu."Started At",
       fu."Completed At",
       fu."Reopened At",
       fu."Assigned By",
       fu."Started By",
       fu."Completed By",
       fu."Reopened By",
       fu."Overdue Count",
       fu."Not Started Count",
       fu."In Progress Count",
       fu."Completed Count",
       fu."Reopened Count",
       fu."Task KNID",
       fu."Org",
       fu."Task",
       fu."Trigger Form KNID",
       fu."Trigger Form Submission KNID",
       fu."Theme KNID",
       fu."Checkpoint KNID"
FROM fu
LEFT OUTER JOIN cmscp ON fu."Trigger Form Submission KNID" = cmscp.audit_submission_knid
AND fu."Checkpoint KNID" = cmscp.checkpoint_knid
LEFT OUTER JOIN cms_theme_score cmsts ON fu."Trigger Form Submission KNID" = cmsts.audit_submission_knid
AND fu."Theme" = cmsts.Theme
group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34
ORDER BY 7 desc, 14 DESC,
         13 DESC,
         1,
         2,
         3,
         4,
         5,
         8,
         10
```

---

## Location Pulse_Pulse of the Day.sql

**Tables referenced:** form_compliance, issue_count, issues, location_acl, nuggets, organizations, routine_compliance, routine_count, shift_attendance, shift_count, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Location Pulse
-- Dashboard: Pulse of the Day
-- Category: Generic
-- Extracted: 2026-01-29 16:57:10
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location,
                   organization
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
     AND is_active = 'true'
     and job_location not in ('KNOW', 'HQ', 'Head Office', 'All')
   and job_location not ilike 'Head Office%'
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
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
     td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = @{{:OrganizationParameter}}),
     issue_count AS
  (SELECT location_acl.job_location,
          count(distinct(CASE
                             WHEN issues.severity IN ('Critical') THEN issues.id
                             ELSE NULL
                         END)) AS issue_count
   FROM location_acl
   LEFT OUTER JOIN issues ON issues.location = location_acl.job_location
   WHERE issues.organization = @{{:OrganizationParameter}}
     AND (issues.is_deleted != 'true'
          OR is_deleted IS NULL)
     AND issues.status ILIKE 'open'
   GROUP BY 1),
     routine_compliance AS
  (SELECT DISTINCT ON (fc.organization,
                       fc.form_id,
                       fc.job_location,
                       (fc.reminded_at+td.diff)::date) fc.organization AS "Organization",
                      (fc.reminded_at + td.diff)::date AS "Date",
                      fc.form_id AS "Routine KNID",
                      n.title AS "Routine Name",
                      fc.job_location AS "Location",
                      fc.reminded_at + td.diff AS "Reminded At",
                      fc.responded_at + td.diff AS "Responded At",
                      CASE
                          WHEN fc.responded_at IS NULL THEN 0
                          ELSE 1
                      END AS "Compliance",
                      fc.response_id AS "Submission KNID"
   FROM form_compliance fc
   JOIN nuggets n ON fc.form_id = n.id
   JOIN location_acl ON fc.job_location = location_acl.job_location
   JOIN td ON td.organization = fc.organization
   WHERE fc.organization =@{{:OrganizationParameter}}
     AND date_trunc('Day', fc.reminded_at + td.diff) = date_trunc('Day', CURRENT_TIMESTAMP+td.diff)
   ORDER BY fc.organization,
            fc.form_id,
            fc.job_location,
            (fc.reminded_at + td.diff)::date,
            fc.responded_at + td.diff),
     routine_count AS
  (SELECT location_acl.job_location,
          count(routine_compliance."Compliance") AS routines_due,
          sum(routine_compliance."Compliance") AS routines_done
   FROM location_acl
   LEFT OUTER JOIN routine_compliance ON location_acl.job_location = routine_compliance."Location"
   GROUP BY 1),
     shift_count AS
  (SELECT location_acl.job_location,
          sum(shift_attendance."Scheduled Count") AS scheduled_count,
          sum(shift_attendance."Absent Count") AS absent_count,
          sum(shift_attendance."Scheduled Count") - sum(shift_attendance."Absent Count") AS present_count,
          sum(shift_attendance."Late Count") AS late_count
   FROM location_acl
   LEFT OUTER JOIN td ON location_acl.organization = td.organization
   LEFT OUTER JOIN shift_attendance ON location_acl.job_location = shift_attendance."Shift Location"
   AND shift_attendance."Status" != 'On Leave'
   AND shift_attendance."organization" = @{{:OrganizationParameter}}
   AND date_trunc('Day', shift_attendance."Scheduled Start Time" + td.diff) = date_trunc('Day', CURRENT_TIMESTAMP + td.diff)
   GROUP BY 1)
SELECT location_acl.job_location AS "Location",
       case when scheduled_count is null then 0 else scheduled_count end AS "Scheduled Count",
       case when absent_count is null then 0 else absent_count end AS "Absent Count",
       case when present_count is null then 0 else present_count end AS "Present Count",
       case when late_count is null then 0 else late_count end AS "Late Count",
       case when routines_due is null then 0 else routines_due end AS "Routines Due",
       case when routines_done is null then 0 else routines_done end AS "Routines Done",
       case when issue_count is null then 0 else issue_count end AS "Issue Count"
FROM location_acl
LEFT OUTER JOIN shift_count ON shift_count.job_location = location_acl.job_location
LEFT OUTER JOIN routine_count ON routine_count.job_location = location_acl.job_location
LEFT OUTER JOIN issue_count ON issue_count.job_location = location_acl.job_location
```

---

## Maintenance Ticket Management_Maintenance Ticket Management.sql

**Tables referenced:** public.demo_maintenance_ticket_master

**Original Query:**

```sql
-- Data Source: Maintenance Ticket Management
-- Dashboard: Maintenance Ticket Management
-- Category: Generic
-- Extracted: 2026-01-29 16:59:31
-- ============================================================

select * from public.demo_maintenance_ticket_master
```

---

## No of Form Submissions (Large)_Forms (Large).sql

**Tables referenced:** form_responses, form_submissions, forms, fr, fr_location, fs, location_acl, nuggets, organizations, question_definitions, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: No of Form Submissions (Large)
-- Dashboard: Forms (Large)
-- Category: Generic
-- Extracted: 2026-01-29 16:59:23
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
   and is_active = 'true'
   and job_location not in ('KNOW', 'All')
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
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = @{{:OrganizationParameter}}),
			   forms as (select * from nuggets where organization = @{{:OrganizationParameter}}
						 and (is_deleted = 'false' or is_deleted is null)
						 and classification_type = 'form'
						and title not ilike 'Issue Creation%'
						and title not ilike 'Issue Closure%'
						and id not ilike 'compliment%'
						and id not ilike 'leave%'),
						fs AS
  (SELECT DISTINCT ON (response_id) fs2.*
   FROM form_submissions fs2
   JOIN forms ON forms.id = fs2.form_id
   JOIN td ON fs2.organization = td.organization
   WHERE submit_date + td.diff between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp
   ORDER BY response_id,
            fs2.id),
     fr_location AS
  (SELECT DISTINCT ON (fs.response_id) fs.response_id,
                      fr.response->>'name' AS fr_location
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   JOIN question_definitions qd ON fr.question_id = qd.question_id
   AND fs.form_id = qd.nugget_id
   WHERE qd.question_type = 'location'
   ORDER BY fs.response_id,
            fs.id,
            qd.section_id,
            qd.sqno),
     fr AS
  (SELECT fs.response_Id,
          fs.form_id,
          fs.id,
          fs.sno,
          fs.submit_date,
          fs.organization,
          fs.user_id,
          CASE
              WHEN fr_location.fr_location IS NULL THEN fs.location
              ELSE fr_location.fr_location
          END AS LOCATION
   FROM fs
   LEFT OUTER JOIN fr_location ON fs.response_id = fr_location.response_id)
SELECT forms.title AS "Form Title",
       forms.id AS "Form KNID",
       fr.response_id AS "Response KNID",
       fr.sno AS "Submission No",
       fr.submit_date + td.diff AS "Submitted At",
       fr.location AS "Form Location",
       ud.identifier AS "Submitter ID",
       ud.uuid AS "Submitter KNID",
       ud.first_name||' '||ud.last_name AS "Submitter Name",
       ud.division AS "Submitter Division",
       ud.sub_division AS "Submitter Sub Division",
       ud.job_location AS "Submitter Location",
       ud.department AS "Submitter Department",
       ud.designation AS "Submitter Designation",
       ud.job_type AS "Submitter Job Type"
FROM location_acl la
LEFT OUTER JOIN fr ON fr.location = la.job_location
LEFT OUTER JOIN forms ON fr.form_id = forms.id
LEFT OUTER JOIN td ON fr.organization = td.organization
LEFT OUTER JOIN user_details ud ON fr.user_id = ud.uuid
ORDER BY 1,
         6,
         5
```

---

## No of Form Submissions_Forms.sql

**Tables referenced:** form_responses, form_submissions, forms, fr, fr_location, fs, location_acl, nuggets, organizations, question_definitions, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: No of Form Submissions
-- Dashboard: Forms
-- Category: Generic
-- Extracted: 2026-01-29 16:55:08
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
   and is_active = 'true'
   and job_location not in ('KNOW', 'All')
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
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = @{{:OrganizationParameter}}),
			   forms as (select * from nuggets where organization = @{{:OrganizationParameter}}
						 and (is_deleted = 'false' or is_deleted is null)
						 and classification_type = 'form'
						and title not ilike 'Issue Creation%'
						and title not ilike 'Issue Closure%'
						and id not ilike 'compliment%'
						and id not ilike 'leave%'),
						fs AS
  (SELECT DISTINCT ON (response_id) fs2.*
   FROM form_submissions fs2
   JOIN forms ON forms.id = fs2.form_id
   JOIN td ON fs2.organization = td.organization
   WHERE submit_date + td.diff between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
   ORDER BY response_id,
            fs2.id),
     fr_location AS
  (SELECT DISTINCT ON (fs.response_id) fs.response_id,
                      fr.response->>'name' AS fr_location
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   JOIN question_definitions qd ON fr.question_id = qd.question_id
   AND fs.form_id = qd.nugget_id
   WHERE qd.question_type = 'location'
   ORDER BY fs.response_id,
            fs.id,
            qd.section_id,
            qd.sqno),
     fr AS
  (SELECT fs.response_Id,
          fs.form_id,
          fs.id,
          fs.sno,
          fs.submit_date,
          fs.organization,
          fs.user_id,
          CASE
              WHEN fr_location.fr_location IS NULL THEN fs.location
              ELSE fr_location.fr_location
          END AS LOCATION
   FROM fs
   LEFT OUTER JOIN fr_location ON fs.response_id = fr_location.response_id)
SELECT forms.title AS "Form Title",
       forms.id AS "Form KNID",
       fr.response_id AS "Response KNID",
       fr.sno AS "Submission No",
       fr.submit_date + td.diff AS "Submitted At",
       fr.location AS "Form Location",
       ud.identifier AS "Submitter ID",
       ud.uuid AS "Submitter KNID",
       ud.first_name||' '||ud.last_name AS "Submitter Name",
       ud.division AS "Submitter Division",
       ud.sub_division AS "Submitter Sub Division",
       ud.job_location AS "Submitter Location",
       ud.department AS "Submitter Department",
       ud.designation AS "Submitter Designation",
       ud.job_type AS "Submitter Job Type",
	 to_char(fr.submit_date + td.diff, 'YYYY-MM-DD') as "Date"
FROM location_acl la
LEFT OUTER JOIN fr ON fr.location = la.job_location
LEFT OUTER JOIN forms ON fr.form_id = forms.id
LEFT OUTER JOIN td ON fr.organization = td.organization
LEFT OUTER JOIN user_details ud ON fr.user_id = ud.uuid
ORDER BY 1,
         6,
         5
```

---

## Repetition Forms Generic-copy_1718777014_Form Compliance Analytics.sql

**Tables referenced:** form_compliance_v2, location_acl, user_details, user_groups

**Columns needing snake_case conversion:**

- `endDate` -> `end_date` (alias: `end_date AS "endDate"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `startDate` -> `start_date` (alias: `start_date AS "startDate"`)


**Original Query:**

```sql
-- Data Source: Repetition Forms Generic-copy_1718777014
-- Dashboard: Form Compliance Analytics
-- Category: Generic
-- Extracted: 2026-01-29 16:54:14
-- ============================================================

WITH location_acl AS (
  SELECT
    DISTINCT job_location
  FROM
    user_details
  WHERE
    organization = @{{:OrganizationParameter}}
    AND is_active = 'true'
    AND job_location NOT IN ('KNOW', 'All')
    AND (
      (
        SELECT
          is_super_admin
        FROM
          user_details
        WHERE
          uuid = @{{:UuidParameter}}
      )
      OR uuid IN (
        SELECT
          DISTINCT user_id
        FROM
          user_groups ug1
        WHERE
          ug1.group_id IN (
            SELECT
              group_id
            FROM
              user_groups ug2
            WHERE
              ug2.user_id = @{{:UuidParameter}}
              AND ug2.has_access = TRUE
          )
          AND ug1.is_active = TRUE
      )
    )
)select fc.*, to_char("Date", 'YYYY-MM-DD') as "Date Mod"
from form_compliance_v2 fc
  JOIN location_acl ON fc."Location" = location_acl.job_location
	 where "Routine KNID" = @{{:formId}}
	 and "Organization" = @{{:OrganizationParameter}}
	 and "Date" between @{{:startDate}}::timestamp and @{{:endDate}}::timestamp + interval '1 day'
```

---

## Repetition Forms Generic_Compliance Analytics.sql

**Tables referenced:** form_compliance_v2, location_acl, user_details, user_groups

**Columns needing snake_case conversion:**

- `endDate` -> `end_date` (alias: `end_date AS "endDate"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `startDate` -> `start_date` (alias: `start_date AS "startDate"`)


**Original Query:**

```sql
-- Data Source: Repetition Forms Generic
-- Dashboard: Compliance Analytics
-- Category: Generic
-- Extracted: 2026-01-29 16:57:06
-- ============================================================

 SELECT
		"QueryTable 1"."Organization" AS "Organization",
		"QueryTable 1"."Date" AS "Date",
		"QueryTable 1"."Routine KNID" AS "Routine KNID",
		"QueryTable 1"."Routine Name" AS "Routine Name",
		"QueryTable 1"."Location" AS "Location",
		"QueryTable 1"."Reminded At" AS "Reminded At",
		"QueryTable 1"."Responded At" AS "Responded At",
		"QueryTable 1"."Compliance" AS "Compliance",
		"QueryTable 1"."Submission KNID" AS "Submission KNID",
		"QueryTable 1"."Routine #" AS "Routine #",
		"QueryTable 1"."Date Mod" AS "Date Mod"
		
FROM(WITH location_acl AS (
  SELECT
    DISTINCT job_location
  FROM
    user_details
  WHERE
    organization = @{{:OrganizationParameter}}
    AND is_active = 'true'
    AND job_location NOT IN ('KNOW', 'All')
    AND (
      (
        SELECT
          is_super_admin
        FROM
          user_details
        WHERE
          uuid = @{{:UuidParameter}}
      )
      OR uuid IN (
        SELECT
          DISTINCT user_id
        FROM
          user_groups ug1
        WHERE
          ug1.group_id IN (
            SELECT
              group_id
            FROM
              user_groups ug2
            WHERE
              ug2.user_id = @{{:UuidParameter}}
              AND ug2.has_access = TRUE
          )
          AND ug1.is_active = TRUE
      )
    )
)
select fc.*, to_char("Date", 'YYYY-MM-DD') as "Date Mod"
from form_compliance_v2 fc
  JOIN location_acl ON fc."Location" = location_acl.job_location
	 where "Routine KNID" = @{{:formId}}
	 and "Organization" = @{{:OrganizationParameter}}
	 and "Date" between @{{:startDate}}::timestamp and @{{:endDate}}::timestamp + interval '1 day'
)"QueryTable 1"
```

---

## Repetition Location Forms Generic_Location Compliance Analytics.sql

**Tables referenced:** form_compliance_v2, location_acl, user_details, user_groups

**Columns needing snake_case conversion:**

- `endDate` -> `end_date` (alias: `end_date AS "endDate"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `startDate` -> `start_date` (alias: `start_date AS "startDate"`)


**Original Query:**

```sql
-- Data Source: Repetition Location Forms Generic
-- Dashboard: Location Compliance Analytics
-- Category: Generic
-- Extracted: 2026-01-29 16:52:52
-- ============================================================

WITH location_acl AS (
  SELECT
    DISTINCT job_location
  FROM
    user_details
  WHERE
    organization = @{{:OrganizationParameter}}
    AND is_active = 'true'
    AND job_location NOT IN ('KNOW', 'All')
    AND (
      (
        SELECT
          is_super_admin
        FROM
          user_details
        WHERE
          uuid = @{{:UuidParameter}}
      )
      OR uuid IN (
        SELECT
          DISTINCT user_id
        FROM
          user_groups ug1
        WHERE
          ug1.group_id IN (
            SELECT
              group_id
            FROM
              user_groups ug2
            WHERE
              ug2.user_id = @{{:UuidParameter}}
              AND ug2.has_access = TRUE
          )
          AND ug1.is_active = TRUE
      )
    )
)
select fc.*, to_char("Date", 'YYYY-MM-DD') as "Date Mod"
from form_compliance_v2 fc
  JOIN location_acl ON fc."Location" = location_acl.job_location
	 where "Routine KNID" = @{{:formId}}
	 and "Organization" = @{{:OrganizationParameter}}
	 and "Date" between @{{:startDate}}::timestamp and @{{:endDate}}::timestamp
```

---

## Routine Compliance - Large Data New_Routine Compliance (L) New.sql

**Tables referenced:** form_compliance_v2, location_acl, organizations, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Routine Compliance - Large Data New
-- Dashboard: Routine Compliance (L) New
-- Category: Generic
-- Extracted: 2026-01-29 16:57:07
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
   and is_active = 'true'
   and job_location not in ('KNOW', 'HQ', 'Head Office', 'All')
   and job_location not ilike 'Head Office%'
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
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = @{{:OrganizationParameter}})
select fc.*, to_char("Date", 'YYYY-MM-DD') as "Date Mod"
from form_compliance_v2 fc
join location_acl on fc."Location" = location_acl.job_location
where fc."Organization" =@{{:OrganizationParameter}}
and fc."Date" between @{{:Date Range.START}}::date and @{{:Date Range.END}}::date
order by 1, 3, 5, 2, 6
```

---

## Routine Compliance - Large Data_Routine Compliance (Large).sql

**Tables referenced:** form_compliance_v2, location_acl, organizations, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Routine Compliance - Large Data
-- Dashboard: Routine Compliance (Large)
-- Category: Generic
-- Extracted: 2026-01-29 16:58:17
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
   and is_active = 'true'
   and job_location not in ('KNOW', 'HQ', 'Head Office', 'All')
   and job_location not ilike 'Head Office%'
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
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = @{{:OrganizationParameter}})
select fc.*
from form_compliance_v2 fc
join location_acl on fc."Location" = location_acl.job_location
where fc."Organization" =@{{:OrganizationParameter}}
and fc."Date" between @{{:Date Range.START}}::date and @{{:Date Range.END}}::date
order by 1, 3, 5, 2, 6
```

---

## Routine Compliance_Routine Compliance.sql

**Tables referenced:** form_compliance_v2, location_acl, organizations, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Routine Compliance
-- Dashboard: Routine Compliance
-- Category: Generic
-- Extracted: 2026-01-29 16:54:17
-- ============================================================

 SELECT
		"QueryTable 1"."Organization" AS "Organization",
		"QueryTable 1"."Date" AS "Date",
		"QueryTable 1"."Routine KNID" AS "Routine KNID",
		"QueryTable 1"."Routine Name" AS "Routine Name",
		"QueryTable 1"."Location" AS "Location",
		"QueryTable 1"."Reminded At" AS "Reminded At",
		"QueryTable 1"."Responded At" AS "Responded At",
		"QueryTable 1"."Compliance" AS "Compliance",
		"QueryTable 1"."Submission KNID" AS "Submission KNID",
		"QueryTable 1"."Routine #" AS "Routine #",
		"QueryTable 1"."Date Mod" AS "Date Mod"
FROM(WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
   and is_active = 'true'
   and job_location not in ('KNOW', 'All', 'HO')
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid =@{{:UuidParameter}})
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = @{{:OrganizationParameter}})
select fc.*, to_char("Date", 'YYYY-MM-DD') as "Date Mod"
from form_compliance_v2 fc
join location_acl on fc."Location" = location_acl.job_location
where fc."Organization" =@{{:OrganizationParameter}}
	 AND fc."Reminded At" BETWEEN @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
	AND "Location" NOT IN ('West Kootenay''s area', 'East Kootenay''s area', 'Alberta area')
order by 1, 5, 2 desc, 6 desc, 4)"QueryTable 1"
```

---

## Sales Form Data_Sales Report.sql

**Tables referenced:** base, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, metadata, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, sales_data, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `isTotal` -> `is_total` (alias: `is_total AS "isTotal"`)


**Original Query:**

```sql
-- Data Source: Sales Form Data
-- Dashboard: Sales Report
-- Category: Generic
-- Extracted: 2026-01-29 16:55:01
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'All')
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
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
     td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = @{{:OrganizationParameter}}), /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id IN ('-NvdxgTjYHnXH8BVsg0e')), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT forms.organization,
                                                                  nugget_id AS form_knid,
                                                                  form_name,
                                                                  CASE
                                                                      WHEN qd.section_id = 'section' THEN 1
                                                                      ELSE replace(section_id, 'section-', '')::integer
                                                                  END AS section_no,
                                                                  CASE
                                                                      WHEN qd.question_type = 'section' THEN 0
                                                                      ELSE sqno::integer*10000
                                                                  END AS q_no,
                                                                  section_id,
                                                                  question_id AS parent_qid,
                                                                  question AS parent_question,
                                                                  question_type AS parent_q_type,
                                                                  question_id AS qid,
                                                                  question_type AS q_type,
                                                                  question AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   WHERE question_type NOT IN ('table')),
                                                                                       qdntwl_prework AS
  (SELECT *,
          jsonb_array_elements(definition -> 'logic') -> 'questions' q
   FROM forms
   JOIN question_definitions qd ON qd.nugget_id = forms.form_knid
   WHERE qd.definition -> 'logic' IS NOT NULL),
                                                                                       qd_non_table_with_logic AS
  (/*Non Table type Questions in Forms with Logic - SqNo will be in between the parent SqNo for sub questions*/ SELECT qd.organization,
                                                                                                                       nugget_id AS form_knid,
                                                                                                                       form_name,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question AS parent_question,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
                                                                                       qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT forms.organization,
                                                                                                        nugget_id AS form_knid,
                                                                                                        form_name,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question AS parent_question,
                                                                                                        question_type AS parent_q_type,
                                                                                                        def.key AS qid,
                                                                                                        def.value->>'question_type' AS q_type,
                                                                                                                    (def.value->>'question') AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   CROSS JOIN jsonb_each(definition -> 'questions') def
   WHERE qd.question_type IN ('table')),
                                                                                       final_definition AS
  (SELECT *
   FROM qd_non_table_non_logic
   UNION SELECT *
   FROM qd_non_table_with_logic
   UNION SELECT *
   FROM qd_table
   ORDER BY 1,
            2,
            3,
            5 DESC, 7 DESC),
                                                                                       fs AS
  (SELECT DISTINCT ON (response_id) *
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   join td on form_submissions.organization = td.organization
   where submit_date + td.diff >= '2024-03-01' 
   ORDER BY response_id,
            id DESC),
                                                                                       fr AS
  (SELECT form_submit_id,
          form_id,
          LOCATION,
          sno,
          submit_Date AS submitted_At,
                                   user_id,
                                   response_id,
                                   question_id AS parent_qid,
                                   question_id AS qid,
                                   response,
                                   1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                LOCATION,
                sno,
                submitted_At,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             form_id,
             LOCATION,
             sno,
             submit_Date AS submitted_At,
                                      user_id,
                                      response_id,
                                      question_id,
                                      base.value,
                                      base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table'
	  AND base.value->>'isTotal' IS NULL) base1
   CROSS JOIN jsonb_each(base1.value) res),
                                                                                       base AS
  (SELECT fd.organization AS "Organization",
          fr.location AS "Store ID",
          form_name AS "Form Name",
          submitted_at + td.diff AS "Submitted At",
          fr.sno AS "Submission No",
          fd.section_no AS "Section No",
          fd.q_no AS "Question No",
          fd.parent_question AS "Parent Question",
          fd.question AS "Question",
          rn AS "Row No",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Singapore', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS "Response",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS "Section Response",
          user_id AS "User KNID",
          fd.form_knid AS "Form KNID",
          fr.response_id AS "Submission KNID"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fd.form_knid = fr.form_id
   join td on fd.organization = td.organization
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
            15),
                                                                                       metadata AS
  (SELECT base."Organization",
          base."Submission KNID",
          base."Submission No",
          max(CASE
                  WHEN base."Question" = 'Location' THEN base."Response"
                  ELSE NULL
              END) AS "Location",
          max(CASE
                  WHEN base."Question" = 'Date' THEN to_date(base."Response", 'YYYY-MM-DD hh24:mi:ss')
                  ELSE NULL
              END) AS "Date"
   FROM base
   GROUP BY 1,
            2,
            3),
                                                                                       sales_data AS
  (SELECT base."Organization",
          base."Submission KNID",
          base."Submission No",
          base."Row No",
          max(CASE
                  WHEN base."Parent Question" = 'Sales data'
                       AND base."Question" = 'Type of Sale' THEN base."Response"
                  ELSE NULL
              END) AS "Type of Sale",
          sum(CASE
                  WHEN base."Parent Question" = 'Sales data'
                       AND base."Question" = 'Target Sales' THEN base."Response"::numeric
                  ELSE NULL
              END) AS "Target Sales",
          sum(CASE
                  WHEN base."Parent Question" = 'Sales data'
                       AND base."Question" = 'Actual Sales' THEN base."Response"::numeric
                  ELSE NULL
              END) AS "Actual Sales",
          sum(CASE
                  WHEN base."Parent Question" = 'Sales data'
                       AND base."Question" = 'No of bills' THEN base."Response"::numeric
                  ELSE NULL
              END) AS "No of bills",
          max(CASE
                  WHEN base."Question" = 'Remarks' THEN base."Response"
                  ELSE NULL
              END) AS "Remarks"
   FROM base
   GROUP BY 1,
            2,
            3,
            4)
SELECT md."Organization",
       md."Submission KNID",
       md."Submission No",
       md."Location",
       md."Date",
       sd."Row No",
       sd."Type of Sale",
       sd."Target Sales",
       sd."Actual Sales",
       sd."No of bills",
       sd."Remarks"
FROM metadata md
LEFT OUTER JOIN sales_data sd ON md."Organization" = sd."Organization"
AND md."Submission KNID" = sd."Submission KNID"
AND md."Submission No" = sd."Submission No"
join location_acl la on md."Location" = la.job_location
ORDER BY 1,
         4,
         5,
         6
```

---

## Shift Report LARGE_Attendance (L).sql

**Tables referenced:** location_acl, organizations, shift_attendance, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Shift Report LARGE
-- Dashboard: Attendance (L)
-- Category: Generic
-- Extracted: 2026-01-29 16:54:02
-- ============================================================

 SELECT
		"QueryTable 1"."Shift ID" AS "Shift ID",
		"QueryTable 1"."UUID" AS "UUID",
		"QueryTable 1"."Employee Name" AS "Employee Name",
		"QueryTable 1"."Employee ID" AS "Employee ID",
		"QueryTable 1"."Designation" AS "Designation",
		"QueryTable 1"."Department" AS "Department",
		"QueryTable 1"."Division" AS "Division",
		"QueryTable 1"."Sub Division" AS "Sub Division",
		"QueryTable 1"."Home Location" AS "Home Location",
		"QueryTable 1"."Job Type" AS "Job Type",
		"QueryTable 1"."organization" AS "organization",
		"QueryTable 1"."Employee Status" AS "Employee Status",
		"QueryTable 1"."Scheduled Start Time" AS "Scheduled Start Time",
		"QueryTable 1"."Scheduled End Time" AS "Scheduled End Time",
		"QueryTable 1"."Shift Location" AS "Shift Location",
		"QueryTable 1"."Scheduled Break Hours" AS "Scheduled Break Hours",
		"QueryTable 1"."Actual Clockin Time" AS "Actual Clockin Time",
		"QueryTable 1"."Actual Clockout Time" AS "Actual Clockout Time",
		"QueryTable 1"."Clockin Beacon" AS "Clockin Beacon",
		"QueryTable 1"."Clockin Geofence" AS "Clockin Geofence",
		"QueryTable 1"."ci_qr_location_id" AS "ci_qr_location_id",
		"QueryTable 1"."Clockout Beacon" AS "Clockout Beacon",
		"QueryTable 1"."Clockout Geofence" AS "Clockout Geofence",
		"QueryTable 1"."co_qr_location_id" AS "co_qr_location_id",
		"QueryTable 1"."Actual Work Duration" AS "Actual Work Duration",
		"QueryTable 1"."Actual Break Hours" AS "Actual Break Hours",
		"QueryTable 1"."Status" AS "Status",
		"QueryTable 1"."Scheduled Count" AS "Scheduled Count",
		"QueryTable 1"."Leave Count" AS "Leave Count",
		"QueryTable 1"."Present Count" AS "Present Count",
		"QueryTable 1"."Late Count" AS "Late Count",
		"QueryTable 1"."Absent Count" AS "Absent Count",
		"QueryTable 1"."Clockin QR Location" AS "Clockin QR Location",
		"QueryTable 1"."Clockout QR Location" AS "Clockout QR Location"
FROM(WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'watsons-leo'
   and is_active = 'true'
  and job_location not in ('KNOW', 'HQ', 'Head Office', 'All')
   and job_location not ilike 'Head Office%'
   AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid = 'ccxNfXFpAHrPZ4s3ziLEds')
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id ='ccxNfXFpAHrPZ4s3ziLEds'
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = 'watsons-leo')
SELECT shift_attendance."Shift ID",
shift_attendance."UUID",
shift_attendance."Employee Name",
shift_attendance."Employee ID",
shift_attendance."Designation",
shift_attendance."Department",
shift_attendance."Division",
shift_attendance."Sub Division",
shift_attendance."Home Location",
shift_attendance."Job Type",
shift_attendance."organization",
shift_attendance."Employee Status",
(shift_attendance."Scheduled Start Time" + td.diff) as "Scheduled Start Time",
(shift_attendance."Scheduled End Time" + td.diff) as "Scheduled End Time",
shift_attendance."Shift Location",
shift_attendance."Scheduled Break Hours",
(shift_attendance."Actual Clockin Time" + td.diff) as "Actual Clockin Time",
(shift_attendance."Actual Clockout Time" + td.diff) as "Actual Clockout Time",
shift_attendance."Clockin Beacon",
shift_attendance."Clockin Geofence",
shift_attendance."ci_qr_location_id",
shift_attendance."Clockout Beacon",
shift_attendance."Clockout Geofence",
shift_attendance."co_qr_location_id",
shift_attendance."Actual Work Duration",
shift_attendance."Actual Break Hours",
shift_attendance."Status",
shift_attendance."Scheduled Count",
shift_attendance."Leave Count",
shift_attendance."Present Count",
shift_attendance."Late Count",
shift_attendance."Absent Count",
shift_attendance."Clockin QR Location",
shift_attendance."Clockout QR Location"
FROM shift_attendance
JOIN location_acl ON shift_attendance."Shift Location" = location_acl.job_location
join td on shift_attendance."organization" = td.organization
where shift_attendance."organization" = @{{:OrganizationParameter}}
and shift_attendance."Scheduled Start Time" between @{{:Date Range.START}}::timestamp - td.diff and @{{:Date Range.END}}::timestamp - td.diff + interval '1 day')"QueryTable 1"
```

---

## Shift Report Small-copy_1767867407_Attendance - Copy.sql

**Tables referenced:** location_acl, organizations, shift_attendance, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `dateRange` -> `date_range` (alias: `date_range AS "dateRange"`)


**Original Query:**

```sql
-- Data Source: Shift Report Small-copy_1767867407
-- Dashboard: Attendance - Copy
-- Category: Generic
-- Extracted: 2026-01-29 16:52:44
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
   and is_active = 'true'
  and job_location not in ('KNOW', 'HQ', 'Head Office', 'All')
   and job_location not ilike 'Head Office%'
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
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = @{{:OrganizationParameter}})
SELECT shift_attendance."Shift ID",
shift_attendance."UUID",
shift_attendance."Employee Name",
shift_attendance."Employee ID",
shift_attendance."Designation",
shift_attendance."Department",
shift_attendance."Division",
shift_attendance."Sub Division",
shift_attendance."Home Location",
shift_attendance."Job Type",
shift_attendance."organization",
shift_attendance."Employee Status",
(shift_attendance."Scheduled Start Time" + td.diff) as "Scheduled Start Time",
(shift_attendance."Scheduled End Time" + td.diff) as "Scheduled End Time",
shift_attendance."Shift Location",
shift_attendance."Scheduled Break Hours",
(shift_attendance."Actual Clockin Time" + td.diff) as "Actual Clockin Time",
(shift_attendance."Actual Clockout Time" + td.diff) as "Actual Clockout Time",
shift_attendance."Clockin Beacon",
shift_attendance."Clockin Geofence",
shift_attendance."ci_qr_location_id",
shift_attendance."Clockout Beacon",
shift_attendance."Clockout Geofence",
shift_attendance."co_qr_location_id",
shift_attendance."Actual Work Duration",
shift_attendance."Actual Break Hours",
shift_attendance."Status",
shift_attendance."Scheduled Count",
shift_attendance."Leave Count",
shift_attendance."Present Count",
shift_attendance."Late Count",
shift_attendance."Absent Count",
shift_attendance."Clockin QR Location",
shift_attendance."Clockout QR Location"
FROM shift_attendance
JOIN location_acl ON shift_attendance."Shift Location" = location_acl.job_location
join td on shift_attendance."organization" = td.organization
where shift_attendance."organization" = @{{:OrganizationParameter}}
and shift_attendance."Scheduled Start Time" between @{{:dateRange.START}}::timestamp - td.diff and @{{:dateRange.END}}::timestamp - td.diff + interval '1 day'
```

---

## Shift Report Small_Attendance.sql

**Tables referenced:** location_acl, organizations, shift_attendance, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `dateRange` -> `date_range` (alias: `date_range AS "dateRange"`)


**Original Query:**

```sql
-- Data Source: Shift Report Small
-- Dashboard: Attendance
-- Category: Generic
-- Extracted: 2026-01-29 16:52:43
-- ============================================================

 SELECT
		"QueryTable 1"."Shift ID" AS "Shift ID",
		"QueryTable 1"."UUID" AS "UUID",
		"QueryTable 1"."Employee Name" AS "Employee Name",
		"QueryTable 1"."Employee ID" AS "Employee ID",
		"QueryTable 1"."Designation" AS "Designation",
		"QueryTable 1"."Department" AS "Department",
		"QueryTable 1"."Division" AS "Division",
		"QueryTable 1"."Sub Division" AS "Sub Division",
		"QueryTable 1"."Home Location" AS "Home Location",
		"QueryTable 1"."Job Type" AS "Job Type",
		"QueryTable 1"."organization" AS "organization",
		"QueryTable 1"."Employee Status" AS "Employee Status",
		"QueryTable 1"."Scheduled Start Time" AS "Scheduled Start Time",
		"QueryTable 1"."Scheduled End Time" AS "Scheduled End Time",
		"QueryTable 1"."Shift Location" AS "Shift Location",
		"QueryTable 1"."Scheduled Break Hours" AS "Scheduled Break Hours",
		"QueryTable 1"."Actual Clockin Time" AS "Actual Clockin Time",
		"QueryTable 1"."Actual Clockout Time" AS "Actual Clockout Time",
		"QueryTable 1"."Clockin Beacon" AS "Clockin Beacon",
		"QueryTable 1"."Clockin Geofence" AS "Clockin Geofence",
		"QueryTable 1"."ci_qr_location_id" AS "ci_qr_location_id",
		"QueryTable 1"."Clockout Beacon" AS "Clockout Beacon",
		"QueryTable 1"."Clockout Geofence" AS "Clockout Geofence",
		"QueryTable 1"."co_qr_location_id" AS "co_qr_location_id",
		"QueryTable 1"."Actual Work Duration" AS "Actual Work Duration",
		"QueryTable 1"."Actual Break Hours" AS "Actual Break Hours",
		"QueryTable 1"."Status" AS "Status",
		"QueryTable 1"."Scheduled Count" AS "Scheduled Count",
		"QueryTable 1"."Leave Count" AS "Leave Count",
		"QueryTable 1"."Present Count" AS "Present Count",
		"QueryTable 1"."Late Count" AS "Late Count",
		"QueryTable 1"."Absent Count" AS "Absent Count",
		"QueryTable 1"."Clockin QR Location" AS "Clockin QR Location",
		"QueryTable 1"."Clockout QR Location" AS "Clockout QR Location"
FROM(WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
   and is_active = 'true'
  and job_location not in ('KNOW', 'HQ', 'Head Office', 'All')
   and job_location not ilike 'Head Office%'
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
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = @{{:OrganizationParameter}})
SELECT shift_attendance."Shift ID",
shift_attendance."UUID",
shift_attendance."Employee Name",
shift_attendance."Employee ID",
shift_attendance."Designation",
shift_attendance."Department",
shift_attendance."Division",
shift_attendance."Sub Division",
shift_attendance."Home Location",
shift_attendance."Job Type",
shift_attendance."organization",
shift_attendance."Employee Status",
(shift_attendance."Scheduled Start Time" + td.diff) as "Scheduled Start Time",
(shift_attendance."Scheduled End Time" + td.diff) as "Scheduled End Time",
shift_attendance."Shift Location",
shift_attendance."Scheduled Break Hours",
(shift_attendance."Actual Clockin Time" + td.diff) as "Actual Clockin Time",
(shift_attendance."Actual Clockout Time" + td.diff) as "Actual Clockout Time",
shift_attendance."Clockin Beacon",
shift_attendance."Clockin Geofence",
shift_attendance."ci_qr_location_id",
shift_attendance."Clockout Beacon",
shift_attendance."Clockout Geofence",
shift_attendance."co_qr_location_id",
shift_attendance."Actual Work Duration",
shift_attendance."Actual Break Hours",
shift_attendance."Status",
shift_attendance."Scheduled Count",
shift_attendance."Leave Count",
shift_attendance."Present Count",
shift_attendance."Late Count",
shift_attendance."Absent Count",
shift_attendance."Clockin QR Location",
shift_attendance."Clockout QR Location"
FROM shift_attendance
JOIN location_acl ON shift_attendance."Shift Location" = location_acl.job_location
join td on shift_attendance."organization" = td.organization
where shift_attendance."organization" = @{{:OrganizationParameter}}
and shift_attendance."Scheduled Start Time" between @{{:dateRange.START}}::timestamp - td.diff and @{{:dateRange.END}}::timestamp - td.diff + interval '1 day')"QueryTable 1"
```

---

## Tasks_Tasks.sql

**Tables referenced:** accessible_tasks, analytics_requests, audit_tasks, form_tasks, organizations, t, tasks, td, user_acl, user_details, user_groups

**Columns needing snake_case conversion:**

- `auditDetails` -> `audit_details` (alias: `audit_details AS "auditDetails"`)

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `formDetails` -> `form_details` (alias: `form_details AS "formDetails"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `plannedStartDate` -> `planned_start_date` (alias: `planned_start_date AS "plannedStartDate"`)

- `questionGroupId` -> `question_group_id` (alias: `question_group_id AS "questionGroupId"`)

- `resolvedPayload` -> `resolved_payload` (alias: `resolved_payload AS "resolvedPayload"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)


**Original Query:**

```sql
-- Data Source: Tasks
-- Dashboard: Tasks
-- Category: Generic
-- Extracted: 2026-01-29 16:55:08
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
   WHERE organization = @{{:OrganizationParameter}}
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
   WHERE id = @{{:OrganizationParameter}}),
     form_tasks AS
  (SELECT t.id AS "Task KNID",
          t.organization AS "Org",
          t.ext_id AS "Task ID",
          t.title AS "Task",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Completed'
              WHEN t.status ILIKE 'notStarted' THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened') THEN 'In Progress'
          END AS "Status",
          t.details->'formDetails'->>'name' AS "Trigger Form",
                                     t.details->'formDetails'->>'formId' AS "Trigger Form KNID",
                                                                t.details->'formDetails'->>'responseId' AS "Trigger Form Submission KNID",
                                                                                           t.details->'formDetails'->>'sno' AS "Trigger Form Submission No",
                                                                                                                      initcap(t.details->>'authorName') AS "Assigned By",
                                                                                                                      to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AS "Planned Start",
                                                                                                                      initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                                                      initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                                                      initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                                                      to_timestamp(t.created_at/1000) + td.diff AS "Assigned At",
                                                                                                                      to_timestamp(t.deadline/1000) + td.diff AS "Deadline",
                                                                                                                      CASE
                                                                                                                          WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) + td.diff
                                                                                                                      END AS "Started At",
                                                                                                                      CASE
                                                                                                                          WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) + td.diff
                                                                                                                          ELSE NULL
                                                                                                                      END AS "Completed At",
                                                                                                                      CASE
                                                                                                                          WHEN t.status ILIKE 'completed'
                                                                                                                               OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) + td.diff
                                                                                                                          ELSE NULL
                                                                                                                      END AS "Reopened At",
                                                                                                                      CASE
                                                                                                                          WHEN t.status NOT ILIKE 'completed'
                                                                                                                               AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "Overdue Count",
                                                                                                                      CASE
                                                                                                                          WHEN t.status ILIKE 'notStarted'
                                                                                                                               THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "Not Started Count",
                                                                                                                      CASE
                                                                                                                          WHEN (t.status ILIKE 'started'
                                                                                                                                OR t.status ILIKE 'reopened')
                                                                                                                               THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "In Progress Count",
                                                                                                                      CASE
                                                                                                                          WHEN t.status ILIKE 'completed' THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "Completed Count",
                                                                                                                         CASE
                                                                                                                          WHEN t.status ILIKE 'completed' AND completed_at <= deadline THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "On Time Completed Count",
                                                                                                                      CASE
                                                                                                                          WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "Reopened Count",
   																													  t.details->>'comment' as "Completion Comment",
   																													  t.details->'resolvedPayload'->'images'->0->>'url' as "Completion Image",
                                                                                                                      split_part(t.details->'formDetails'->>'path', '/', 1) AS trigger_question_knid
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   JOIN td ON t.organization = td.organization
   WHERE t.is_deleted = 'false'
     AND to_timestamp((t.details->>'plannedStartDate')::bigint/1000) + td.diff BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + interval '1 day'
     AND t.organization = @{{:OrganizationParameter}}),
	 audit_tasks AS
  (SELECT t.id AS "Task KNID",
          t.organization AS "Org",
          t.ext_id AS "Task ID",
          t.title AS "Task",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Completed'
              WHEN t.status ILIKE 'notStarted' THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened') THEN 'In Progress'
          END AS "Status",
          t.details->'auditDetails'->>'name' AS "Trigger Form",
                                     t.details->'auditDetails'->>'formId' AS "Trigger Form KNID",
                                                                t.details->'auditDetails'->>'responseId' AS "Trigger Form Submission KNID",
                                                                                           t.details->'auditDetails'->>'sno' AS "Trigger Form Submission No",
                                                                                                                      initcap(t.details->>'authorName') AS "Assigned By",
                                                                                                                      to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AS "Planned Start",
                                                                                                                      initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                                                      initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                                                      initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                                                      to_timestamp(t.created_at/1000) + td.diff AS "Assigned At",
                                                                                                                      to_timestamp(t.deadline/1000) + td.diff AS "Deadline",
                                                                                                                      CASE
                                                                                                                          WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) + td.diff
                                                                                                                      END AS "Started At",
                                                                                                                      CASE
                                                                                                                          WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) + td.diff
                                                                                                                          ELSE NULL
                                                                                                                      END AS "Completed At",
                                                                                                                      CASE
                                                                                                                          WHEN t.status ILIKE 'completed'
                                                                                                                               OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) + td.diff
                                                                                                                          ELSE NULL
                                                                                                                      END AS "Reopened At",
                                                                                                                      CASE
                                                                                                                          WHEN t.status NOT ILIKE 'completed'
                                                                                                                               AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "Overdue Count",
                                                                                                                      CASE
                                                                                                                          WHEN t.status ILIKE 'notStarted'
                                                                                                                               THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "Not Started Count",
                                                                                                                      CASE
                                                                                                                          WHEN (t.status ILIKE 'started'
                                                                                                                                OR t.status ILIKE 'reopened')
                                                                                                                               THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "In Progress Count",
                                                                                                                      CASE
                                                                                                                          WHEN t.status ILIKE 'completed' THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "Completed Count",
                                                                                                                         CASE
                                                                                                                          WHEN t.status ILIKE 'completed' AND completed_at <= deadline THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "On Time Completed Count",
                                                                                                                      CASE
                                                                                                                          WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "Reopened Count",
   																													  t.details->>'comment' as "Completion Comment",
   																													  t.details->'resolvedPayload'->'images'->0->>'url' as "Completion Image",
                                                                                                                      t.details->'auditDetails'->>'questionGroupId' AS theme_knid
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   JOIN td ON t.organization = td.organization
   WHERE t.is_deleted = 'false'
     AND to_timestamp((t.details->>'plannedStartDate')::bigint/1000) + td.diff BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + interval '1 day'
     AND t.organization = @{{:OrganizationParameter}}),
	 t as (
	   select * from form_tasks
	   union select * from audit_tasks),
	 
    accessible_tasks AS
  (SELECT t."Task KNID",
          string_Agg(ua.emp_name, ', ') AS assignee_list
   FROM t
   JOIN analytics_requests ar ON t."Task KNID" = ar.nugget_id
   JOIN user_acl ua ON ar.user_id = ua.uuid
   WHERE ar.event_id = 1
   GROUP BY 1)
SELECT t.*,
       at.assignee_list AS "Assignee(s)"
FROM t
JOIN accessible_tasks AT ON t."Task KNID" = at."Task KNID"
ORDER BY 2,
         14,
         15
```

---
