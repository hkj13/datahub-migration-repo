# Swiggy RPA

> Auto-generated on 2026-03-04 08:13

**Total queries:** 13

---

## Swiggy RPA Consolidated Course Report_Swiggy RPA Overall Engagement.sql

**Tables referenced:** analytics.nuggets_user_progress, course_report_1, courses, quiz_report, user_details

**Columns needing snake_case conversion:**

- `courseStatus` -> `course_status` (alias: `course_status AS "courseStatus"`)

- `inProgress` -> `in_progress` (alias: `in_progress AS "inProgress"`)

- `noOfCorrectAnswer` -> `no_of_correct_answer` (alias: `no_of_correct_answer AS "noOfCorrectAnswer"`)

- `noOfQuestionAnswered` -> `no_of_question_answered` (alias: `no_of_question_answered AS "noOfQuestionAnswered"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)


**Original Query:**

```sql
-- Data Source: Swiggy RPA Consolidated Course Report
-- Dashboard: Swiggy RPA Overall Engagement
-- Category: Swiggy RPA
-- Extracted: 2026-01-29 16:55:59
-- ============================================================

WITH course_report_1 AS
  (SELECT nup.nugget_id,
          nup.user_id,
          ud.identifier,
          c.name,
          least(min(base.sessions -> session_id ->> 'courseStatus'), min(nup.status)) AS status,
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
      WHERE ud.organization ILIKE '%rpa%'
        AND ud.phone_number IS NULL
        AND nup.status != 'sent'
        AND c.organization ILIKE '%rpa%'
	 and nup.updated_at between @{{:Swiggy RPA Engagement.Date Range.START}}::timestamp and @{{:Swiggy RPA Engagement.Date Range.END}}::timestamp + interval '1 day') base ON nup.nugget_id = base.nugget_id
   AND nup.user_id = base.user_id
   JOIN user_details ud ON nup.user_id = ud.uuid
   JOIN courses c ON nup.nugget_id = c.id
   WHERE ud.organization ILIKE '%rpa%'
     AND ud.phone_number IS NULL
     AND c.organization ILIKE '%rpa%'
     AND nup.status != 'sent'
   and nup.updated_at between @{{:Swiggy RPA Engagement.Date Range.START}}::timestamp and @{{:Swiggy RPA Engagement.Date Range.END}}::timestamp + interval '1 day'
   GROUP BY 1,
            2,
            3,
            4),
     quiz_report AS
  (SELECT nugget_id,
          user_id,
          CASE
              WHEN sum((quiz_cards->quiz_card_id->'noOfQuestionAnswered')::int) > 0 THEN sum((quiz_cards->quiz_card_id->'noOfCorrectAnswer')::int) * 100 / sum((quiz_cards->quiz_card_id->'noOfQuestionAnswered')::int)
              ELSE NULL
          END AS score_in_pct
   FROM
     (SELECT nup.nugget_id,
             nup.user_id,
             nup.status,
             jsonb_object_keys(nup.quiz_cards) AS quiz_card_id,
             nup.quiz_cards
      FROM analytics.nuggets_user_progress nup
      JOIN user_details ud ON nup.user_id = ud.uuid
      JOIN courses c ON nup.nugget_id = c.id
      WHERE ud.organization ILIKE '%rpa%'
        AND ud.phone_number IS NULL
        AND c.organization ILIKE '%rpa%'
	 and nup.updated_at between @{{:Swiggy RPA Engagement.Date Range.START}}::timestamp and @{{:Swiggy RPA Engagement.Date Range.END}}::timestamp + interval '1 day') base
   GROUP BY 1,
            2)
SELECT cr.name AS "Course Name",
       cr.identifier AS "User ID",
       CASE
           WHEN length(cr.identifier) >= 10 THEN 'Owner'
           ELSE 'Partner'
       END AS "Role",
       CASE
           WHEN cr.status = 'completed' THEN 'Completed'
           WHEN cr.status = 'inProgress' THEN 'In Progress'
           WHEN cr.status = 'notStarted' THEN 'Opened'
           ELSE NULL
       END AS "Status",
       qr.score_in_pct AS "Score in %",
       cr.no_of_times AS "No of times the course was clicked into",
       cr.time_spent AS "Total time spent on course (mins)",
       cr.nugget_id AS "Course KNID",
       cr.user_id AS "User KNID"
FROM course_report_1 cr
LEFT OUTER JOIN quiz_report qr ON cr.nugget_id = qr.nugget_id
AND cr.user_id = qr.user_id
ORDER BY 1,
         4,
         3,
         2
```

---

## Swiggy RPA Course Reaction Report_Course Reaction Report.sql

**Tables referenced:** analytics.nugget_analytics_raw, c, lesson_cards, lessons, nar, nuggets, public.courses, survey_cards, survey_definition, survey_questions, survey_responses, surveys.survey_responses, user_data, user_details

**Original Query:**

```sql
-- Data Source: Swiggy RPA Course Reaction Report
-- Dashboard: Course Reaction Report
-- Category: Swiggy RPA
-- Extracted: 2026-01-29 16:54:35
-- ============================================================

 SELECT
		"QueryTable 1"."Response Date" AS "Response Date",
		"QueryTable 1"."User Identifier" AS "User Identifier",
		"QueryTable 1"."Role" AS "Role",
		"QueryTable 1"."Course Title" AS "Course Title",
		"QueryTable 1"."Lesson Title" AS "Lesson Title",
		"QueryTable 1"."Survey Title" AS "Survey Title",
		"QueryTable 1"."Question" AS "Question",
		"QueryTable 1"."Selected Option" AS "Selected Option",
		"QueryTable 1"."Course KNID" AS "Course KNID",
		"QueryTable 1"."Lesson KNID" AS "Lesson KNID",
		"QueryTable 1"."Card KNID" AS "Card KNID",
		"QueryTable 1"."KNOW User ID" AS "KNOW User ID"
FROM(WITH c AS
  (SELECT *
   FROM public.courses
   WHERE organization = 'swiggyrpa-virgo'),
     nar AS
  (SELECT *
   FROM analytics.nugget_analytics_raw nar
   WHERE  nar.course_id IN
       (SELECT id
        FROM c) ),
		user_data AS
  (SELECT nar.course_id,
          nar.user_id,
          user_Details.identifier
   FROM nar
   JOIN user_details ON nar.user_id = user_details.uuid
   WHERE user_details.phone_number IS NULL),
     survey_cards AS
  (SELECT lessons.course_id,
          lessons.id AS lesson_id,
          lessons.title AS lesson_title,
          lesson_cards.id AS card_id,
          lesson_cards.title AS survey_title,
          lesson_cards.payload -> 'sections' -> 'section0' -> 'questions' AS question_list
   FROM lesson_cards
   JOIN lessons ON lesson_cards.lesson_id = lessons.id
   WHERE lesson_cards.type = 'survey' 
  and lessons.course_id in (select distinct course_id from nar )),
     survey_questions AS
  (SELECT survey_cards.course_id,
          survey_cards.lesson_id,
          survey_cards.card_id,
          survey_cards.lesson_title,
          survey_cards.survey_title,
          questions.value ->> 'text' AS question,
                              questions.ordinality - 1 AS question_id,
                              questions.value ->> 'type' AS question_type,
                                                  questions.value -> 'options' AS options_list
   FROM survey_cards,
        jsonb_array_elements(survey_cards.question_list) WITH
   ORDINALITY AS questions),
     survey_definition AS
  (SELECT survey_questions.course_id,
          survey_questions.lesson_id,
          survey_questions.card_id,
          survey_questions.lesson_title,
          survey_questions.survey_title,
          survey_questions.question_id,
          survey_questions.question,
          survey_questions.question_type,
          options.value AS OPTION,
          options.ordinality AS option_id
   FROM survey_questions,
        jsonb_array_elements(survey_questions.options_list) WITH
   ORDINALITY AS OPTIONS),
     survey_responses AS
  (SELECT user_id,
          course_id,
          created_at,
          card_id,
          responses ->> 'question' AS question_id,
                        responses ->> 'response' AS response_id
   FROM
     (SELECT *,
             jsonb_array_elements(response) AS responses
      FROM surveys.survey_responses) base)
SELECT *
FROM
  (SELECT (survey_responses.created_at AT TIME ZONE 'Asia/Kolkata')::date AS "Response Date",
          user_data.identifier AS "User Identifier",
          CASE
              WHEN length(user_data.identifier) >= 10 THEN 'Owner'
              ELSE 'Partner'
          END AS "Role",
          nuggets.title AS "Course Title",
          survey_definition.lesson_title AS "Lesson Title",
          survey_definition.survey_title AS "Survey Title",
          survey_definition.question AS "Question",
          CASE
              WHEN survey_definition.question_type NOT IN ('rating',
                                                           'text',
                                                           'nps') THEN replace(survey_definition.option::varchar, '"', '')
              ELSE survey_responses.response_id
          END AS "Selected Option",
          survey_Definition.course_id AS "Course KNID",
          survey_definition.lesson_id AS "Lesson KNID",
          survey_definition.card_id AS "Card KNID",
          survey_responses.user_id AS "KNOW User ID"
   FROM survey_responses
   JOIN survey_definition ON survey_responses.course_id = survey_definition.course_id
   AND survey_responses.card_id = survey_definition.card_id
   AND survey_responses.question_id = survey_definition.question_id::varchar
   AND CASE
           WHEN survey_definition.question_type NOT IN ('rating',
                                                        'text',
                                                        'nps') THEN survey_responses.response_id = survey_definition.option_id::varchar
           ELSE survey_responses.question_id = survey_definition.question_id::varchar
       END
   JOIN user_data ON survey_responses.user_id = user_data.user_id
   AND survey_responses.course_id = user_data.course_id
   JOIN nuggets ON survey_responses.course_id = nuggets.id
   ORDER BY 1,
            3,
            5,
            survey_responses.question_id) report_base
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
         12)"QueryTable 1"
```

---

## Swiggy RPA Course Reaction Report_Swiggy RPA Daily Reports.sql

**Tables referenced:** analytics.nugget_analytics_raw, c, lesson_cards, lessons, nar, nuggets, public.courses, survey_cards, survey_definition, survey_questions, survey_responses, surveys.survey_responses, user_data, user_details

**Original Query:**

```sql
-- Data Source: Swiggy RPA Course Reaction Report
-- Dashboard: Swiggy RPA Daily Reports
-- Category: Swiggy RPA
-- Extracted: 2026-01-29 16:54:35
-- ============================================================

 SELECT
		"QueryTable 1"."Response Date" AS "Response Date",
		"QueryTable 1"."User Identifier" AS "User Identifier",
		"QueryTable 1"."Role" AS "Role",
		"QueryTable 1"."Course Title" AS "Course Title",
		"QueryTable 1"."Lesson Title" AS "Lesson Title",
		"QueryTable 1"."Survey Title" AS "Survey Title",
		"QueryTable 1"."Question" AS "Question",
		"QueryTable 1"."Selected Option" AS "Selected Option",
		"QueryTable 1"."Course KNID" AS "Course KNID",
		"QueryTable 1"."Lesson KNID" AS "Lesson KNID",
		"QueryTable 1"."Card KNID" AS "Card KNID",
		"QueryTable 1"."KNOW User ID" AS "KNOW User ID"
FROM(WITH c AS
  (SELECT *
   FROM public.courses
   WHERE organization = 'swiggyrpa-virgo'),
     nar AS
  (SELECT *
   FROM analytics.nugget_analytics_raw nar
   WHERE  nar.course_id IN
       (SELECT id
        FROM c) ),
		user_data AS
  (SELECT nar.course_id,
          nar.user_id,
          user_Details.identifier
   FROM nar
   JOIN user_details ON nar.user_id = user_details.uuid
   WHERE user_details.phone_number IS NULL),
     survey_cards AS
  (SELECT lessons.course_id,
          lessons.id AS lesson_id,
          lessons.title AS lesson_title,
          lesson_cards.id AS card_id,
          lesson_cards.title AS survey_title,
          lesson_cards.payload -> 'sections' -> 'section0' -> 'questions' AS question_list
   FROM lesson_cards
   JOIN lessons ON lesson_cards.lesson_id = lessons.id
   WHERE lesson_cards.type = 'survey' 
  and lessons.course_id in (select distinct course_id from nar )),
     survey_questions AS
  (SELECT survey_cards.course_id,
          survey_cards.lesson_id,
          survey_cards.card_id,
          survey_cards.lesson_title,
          survey_cards.survey_title,
          questions.value ->> 'text' AS question,
                              questions.ordinality - 1 AS question_id,
                              questions.value ->> 'type' AS question_type,
                                                  questions.value -> 'options' AS options_list
   FROM survey_cards,
        jsonb_array_elements(survey_cards.question_list) WITH
   ORDINALITY AS questions),
     survey_definition AS
  (SELECT survey_questions.course_id,
          survey_questions.lesson_id,
          survey_questions.card_id,
          survey_questions.lesson_title,
          survey_questions.survey_title,
          survey_questions.question_id,
          survey_questions.question,
          survey_questions.question_type,
          options.value AS OPTION,
          options.ordinality AS option_id
   FROM survey_questions,
        jsonb_array_elements(survey_questions.options_list) WITH
   ORDINALITY AS OPTIONS),
     survey_responses AS
  (SELECT user_id,
          course_id,
          created_at,
          card_id,
          responses ->> 'question' AS question_id,
                        responses ->> 'response' AS response_id
   FROM
     (SELECT *,
             jsonb_array_elements(response) AS responses
      FROM surveys.survey_responses) base)
SELECT *
FROM
  (SELECT (survey_responses.created_at AT TIME ZONE 'Asia/Kolkata')::date AS "Response Date",
          user_data.identifier AS "User Identifier",
          CASE
              WHEN length(user_data.identifier) >= 10 THEN 'Owner'
              ELSE 'Partner'
          END AS "Role",
          nuggets.title AS "Course Title",
          survey_definition.lesson_title AS "Lesson Title",
          survey_definition.survey_title AS "Survey Title",
          survey_definition.question AS "Question",
          CASE
              WHEN survey_definition.question_type NOT IN ('rating',
                                                           'text',
                                                           'nps') THEN replace(survey_definition.option::varchar, '"', '')
              ELSE survey_responses.response_id
          END AS "Selected Option",
          survey_Definition.course_id AS "Course KNID",
          survey_definition.lesson_id AS "Lesson KNID",
          survey_definition.card_id AS "Card KNID",
          survey_responses.user_id AS "KNOW User ID"
   FROM survey_responses
   JOIN survey_definition ON survey_responses.course_id = survey_definition.course_id
   AND survey_responses.card_id = survey_definition.card_id
   AND survey_responses.question_id = survey_definition.question_id::varchar
   AND CASE
           WHEN survey_definition.question_type NOT IN ('rating',
                                                        'text',
                                                        'nps') THEN survey_responses.response_id = survey_definition.option_id::varchar
           ELSE survey_responses.question_id = survey_definition.question_id::varchar
       END
   JOIN user_data ON survey_responses.user_id = user_data.user_id
   AND survey_responses.course_id = user_data.course_id
   JOIN nuggets ON survey_responses.course_id = nuggets.id
   ORDER BY 1,
            3,
            5,
            survey_responses.question_id) report_base
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
         12)"QueryTable 1"
```

---

## Swiggy RPA Course Reaction Report_Swiggy RPA Overall Engagement.sql

**Tables referenced:** analytics.nugget_analytics_raw, c, lesson_cards, lessons, nar, nuggets, public.courses, survey_cards, survey_definition, survey_questions, survey_responses, surveys.survey_responses, user_data, user_details

**Original Query:**

```sql
-- Data Source: Swiggy RPA Course Reaction Report
-- Dashboard: Swiggy RPA Overall Engagement
-- Category: Swiggy RPA
-- Extracted: 2026-01-29 16:54:35
-- ============================================================

 SELECT
		"QueryTable 1"."Response Date" AS "Response Date",
		"QueryTable 1"."User Identifier" AS "User Identifier",
		"QueryTable 1"."Role" AS "Role",
		"QueryTable 1"."Course Title" AS "Course Title",
		"QueryTable 1"."Lesson Title" AS "Lesson Title",
		"QueryTable 1"."Survey Title" AS "Survey Title",
		"QueryTable 1"."Question" AS "Question",
		"QueryTable 1"."Selected Option" AS "Selected Option",
		"QueryTable 1"."Course KNID" AS "Course KNID",
		"QueryTable 1"."Lesson KNID" AS "Lesson KNID",
		"QueryTable 1"."Card KNID" AS "Card KNID",
		"QueryTable 1"."KNOW User ID" AS "KNOW User ID"
FROM(WITH c AS
  (SELECT *
   FROM public.courses
   WHERE organization = 'swiggyrpa-virgo'),
     nar AS
  (SELECT *
   FROM analytics.nugget_analytics_raw nar
   WHERE  nar.course_id IN
       (SELECT id
        FROM c) ),
		user_data AS
  (SELECT nar.course_id,
          nar.user_id,
          user_Details.identifier
   FROM nar
   JOIN user_details ON nar.user_id = user_details.uuid
   WHERE user_details.phone_number IS NULL),
     survey_cards AS
  (SELECT lessons.course_id,
          lessons.id AS lesson_id,
          lessons.title AS lesson_title,
          lesson_cards.id AS card_id,
          lesson_cards.title AS survey_title,
          lesson_cards.payload -> 'sections' -> 'section0' -> 'questions' AS question_list
   FROM lesson_cards
   JOIN lessons ON lesson_cards.lesson_id = lessons.id
   WHERE lesson_cards.type = 'survey' 
  and lessons.course_id in (select distinct course_id from nar )),
     survey_questions AS
  (SELECT survey_cards.course_id,
          survey_cards.lesson_id,
          survey_cards.card_id,
          survey_cards.lesson_title,
          survey_cards.survey_title,
          questions.value ->> 'text' AS question,
                              questions.ordinality - 1 AS question_id,
                              questions.value ->> 'type' AS question_type,
                                                  questions.value -> 'options' AS options_list
   FROM survey_cards,
        jsonb_array_elements(survey_cards.question_list) WITH
   ORDINALITY AS questions),
     survey_definition AS
  (SELECT survey_questions.course_id,
          survey_questions.lesson_id,
          survey_questions.card_id,
          survey_questions.lesson_title,
          survey_questions.survey_title,
          survey_questions.question_id,
          survey_questions.question,
          survey_questions.question_type,
          options.value AS OPTION,
          options.ordinality AS option_id
   FROM survey_questions,
        jsonb_array_elements(survey_questions.options_list) WITH
   ORDINALITY AS OPTIONS),
     survey_responses AS
  (SELECT user_id,
          course_id,
          created_at,
          card_id,
          responses ->> 'question' AS question_id,
                        responses ->> 'response' AS response_id
   FROM
     (SELECT *,
             jsonb_array_elements(response) AS responses
      FROM surveys.survey_responses) base)
SELECT *
FROM
  (SELECT (survey_responses.created_at AT TIME ZONE 'Asia/Kolkata')::date AS "Response Date",
          user_data.identifier AS "User Identifier",
          CASE
              WHEN length(user_data.identifier) >= 10 THEN 'Owner'
              ELSE 'Partner'
          END AS "Role",
          nuggets.title AS "Course Title",
          survey_definition.lesson_title AS "Lesson Title",
          survey_definition.survey_title AS "Survey Title",
          survey_definition.question AS "Question",
          CASE
              WHEN survey_definition.question_type NOT IN ('rating',
                                                           'text',
                                                           'nps') THEN replace(survey_definition.option::varchar, '"', '')
              ELSE survey_responses.response_id
          END AS "Selected Option",
          survey_Definition.course_id AS "Course KNID",
          survey_definition.lesson_id AS "Lesson KNID",
          survey_definition.card_id AS "Card KNID",
          survey_responses.user_id AS "KNOW User ID"
   FROM survey_responses
   JOIN survey_definition ON survey_responses.course_id = survey_definition.course_id
   AND survey_responses.card_id = survey_definition.card_id
   AND survey_responses.question_id = survey_definition.question_id::varchar
   AND CASE
           WHEN survey_definition.question_type NOT IN ('rating',
                                                        'text',
                                                        'nps') THEN survey_responses.response_id = survey_definition.option_id::varchar
           ELSE survey_responses.question_id = survey_definition.question_id::varchar
       END
   JOIN user_data ON survey_responses.user_id = user_data.user_id
   AND survey_responses.course_id = user_data.course_id
   JOIN nuggets ON survey_responses.course_id = nuggets.id
   ORDER BY 1,
            3,
            5,
            survey_responses.question_id) report_base
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
         12)"QueryTable 1"
```

---

## Swiggy RPA Course Report Consolidated_Swiggy RPA Daily Reports.sql

**Tables referenced:** analytics.nuggets_user_progress, course_report_1, courses, quiz_report, user_details

**Columns needing snake_case conversion:**

- `courseStatus` -> `course_status` (alias: `course_status AS "courseStatus"`)

- `inProgress` -> `in_progress` (alias: `in_progress AS "inProgress"`)

- `noOfCorrectAnswer` -> `no_of_correct_answer` (alias: `no_of_correct_answer AS "noOfCorrectAnswer"`)

- `noOfQuestionAnswered` -> `no_of_question_answered` (alias: `no_of_question_answered AS "noOfQuestionAnswered"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)


**Original Query:**

```sql
-- Data Source: Swiggy RPA Course Report Consolidated
-- Dashboard: Swiggy RPA Daily Reports
-- Category: Swiggy RPA
-- Extracted: 2026-01-29 16:56:04
-- ============================================================

WITH course_report_1 AS
  (SELECT nup.nugget_id,
          nup.user_id,
          ud.identifier,
          c.name,
          least(min(base.sessions -> session_id ->> 'courseStatus'), min(nup.status)) AS status,
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
      WHERE ud.organization ILIKE '%rpa%'
        AND ud.phone_number IS NULL
        AND nup.status != 'sent'
        AND c.organization ILIKE '%rpa%') base ON nup.nugget_id = base.nugget_id
   AND nup.user_id = base.user_id
   JOIN user_details ud ON nup.user_id = ud.uuid
   JOIN courses c ON nup.nugget_id = c.id
   WHERE ud.organization ILIKE '%rpa%'
     AND ud.phone_number IS NULL
     AND c.organization ILIKE '%rpa%'
     AND nup.status != 'sent'
   GROUP BY 1,
            2,
            3,
            4),
     quiz_report AS
  (SELECT nugget_id,
          user_id,
          CASE
              WHEN sum((quiz_cards->quiz_card_id->'noOfQuestionAnswered')::int) > 0 THEN sum((quiz_cards->quiz_card_id->'noOfCorrectAnswer')::int) * 100 / sum((quiz_cards->quiz_card_id->'noOfQuestionAnswered')::int)
              ELSE NULL
          END AS score_in_pct
   FROM
     (SELECT nup.nugget_id,
             nup.user_id,
             nup.status,
             jsonb_object_keys(nup.quiz_cards) AS quiz_card_id,
             nup.quiz_cards
      FROM analytics.nuggets_user_progress nup
      JOIN user_details ud ON nup.user_id = ud.uuid
      JOIN courses c ON nup.nugget_id = c.id
      WHERE ud.organization ILIKE '%rpa%'
        AND ud.phone_number IS NULL
        AND c.organization ILIKE '%rpa%') base
   GROUP BY 1,
            2)
SELECT cr.name AS "Course Name",
       cr.identifier AS "User ID",
       CASE
           WHEN length(cr.identifier) >= 10 THEN 'Owner'
           ELSE 'Partner'
       END AS "Role",
       CASE
           WHEN cr.status = 'completed' THEN 'Completed'
           WHEN cr.status = 'inProgress' THEN 'In Progress'
           WHEN cr.status = 'notStarted' THEN 'Opened'
           ELSE NULL
       END AS "Status",
       qr.score_in_pct AS "Score in %",
       cr.no_of_times AS "No of times the course was clicked into",
       cr.time_spent AS "Total time spent on course (mins)",
       cr.nugget_id AS "Course KNID",
       cr.user_id AS "User KNID"
FROM course_report_1 cr
LEFT OUTER JOIN quiz_report qr ON cr.nugget_id = qr.nugget_id
AND cr.user_id = qr.user_id
ORDER BY 1,
         4,
         3,
         2
```

---

## Swiggy RPA Course Report v2_Monthly Engagement.sql

**Tables referenced:** analytics.nugget_analytics_raw, c, cards, cards_consumed, latest_course_received, latest_course_shares, latest_received, latest_share_ids, nar, organizations, progress, public.courses, public.learning_journey_courses, public.lesson_cards, public.lessons, td, user_details

**Original Query:**

```sql
-- Data Source: Swiggy RPA Course Report v2
-- Dashboard: Monthly Engagement
-- Category: Swiggy RPA
-- Extracted: 2026-01-29 16:55:54
-- ============================================================

 SELECT
		"QueryTable 1"."User ID" AS "User ID",
		"QueryTable 1"."Role" AS "Role",
		"QueryTable 1"."Course ID" AS "Course ID",
		"QueryTable 1"."Course Name" AS "Course Name",
		"QueryTable 1"."Opened At" AS "Opened At",
		"QueryTable 1"."Started At" AS "Started At",
		"QueryTable 1"."Completed At" AS "Completed At",
		"QueryTable 1"."Status" AS "Status",
		"QueryTable 1"."No of Cards Consumed" AS "No of Cards Consumed",
		"QueryTable 1"."Consumed %" AS "Consumed %",
		"QueryTable 1"."course_knid" AS "course_knid",
		"QueryTable 1"."user_knid" AS "user_knid",
		"QueryTable 1"."Opened Count" AS "Opened Count",
		"QueryTable 1"."Started Count" AS "Started Count",
		"QueryTable 1"."Completed Count" AS "Completed Count"
FROM(WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'swiggyrpa-virgo'),
     c AS
  (SELECT *
   FROM public.courses
   WHERE organization = 'swiggyrpa-virgo'),
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
            3)
SELECT ud.identifier AS "User ID",
       CASE
           WHEN length(ud.identifier) >= 10 THEN 'Owner'
           ELSE 'Partner'
       END AS "Role",
       c.id AS "Course ID",
       c.name AS "Course Name",
       lcs.sent_at + td.diff AS "Opened At",
       lcr.received_at + td.diff AS "Started At",
       max(CASE
               WHEN (c.total_cards > 0
                     AND p.consumed_count = c.total_cards) THEN cc.consumed_at + td.diff
               ELSE NULL
           END) AS "Completed At",
       CASE
           WHEN (c.total_cards > 0
                 AND p.consumed_count = c.total_cards) THEN 'Completed'
           WHEN (c.total_cards > 0
                 AND p.consumed_count > 0
                 AND p.consumed_count < c.total_cards)
                OR lcr.received_At IS NOT NULL THEN 'In Progress'
           WHEN c.total_cards > 0
                AND (p.consumed_count = 0
                     OR p.consumed_count IS NULL)
                AND lcr.received_at IS NULL THEN 'Not Started'
           ELSE NULL
       END AS "Status",
       p.consumed_count AS "No of Cards Consumed",
       p.consumed_count::numeric/c.total_cards::numeric AS "Consumed %",
       lcs.course_id AS course_knid,
       ud.uuid AS user_knid,
       1 AS "Opened Count",
       CASE
           WHEN (c.total_cards > 0
                 AND p.consumed_count > 0
                 AND p.consumed_count <= c.total_cards)
                OR lcr.received_At IS NOT NULL THEN 1
           ELSE 0
       END AS "Started Count",
       CASE
           WHEN (c.total_cards > 0
                 AND p.consumed_count = c.total_cards) THEN 1
           ELSE 0
       END AS "Completed Count"
FROM latest_course_shares lcs
JOIN user_details ud ON lcs.user_id = ud.uuid
AND ud.organization = 'swiggyrpa-virgo'
LEFT OUTER JOIN latest_course_received lcr ON lcs.user_id = lcr.user_id
AND lcs.course_id = lcr.course_id
AND lcs.share_id = lcr.share_id
LEFT OUTER JOIN progress p ON lcs.user_id = p.user_id
AND lcs.course_id = p.course_id
AND lcs.share_id = p.share_id
LEFT OUTER JOIN cards_consumed cc ON lcs.user_id = cc.user_id
AND lcs.course_id = cc.course_id
AND lcs.share_id = cc.share_id
LEFT OUTER JOIN c ON lcs.course_id = c.id
LEFT OUTER JOIN td ON ud.organization = td.organization
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         8,
         9,
         10,
         11,
         12,
         13,
         14,
         15
ORDER BY 1,
         4,
         5)"QueryTable 1"
```

---

## Swiggy RPA Course Wise Engagement_Swiggy RPA Daily Reports.sql

**Tables referenced:** analytics.nuggets_user_progress, base, courses, cr, user_details

**Columns needing snake_case conversion:**

- `courseStatus` -> `course_status` (alias: `course_status AS "courseStatus"`)

- `inProgress` -> `in_progress` (alias: `in_progress AS "inProgress"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)


**Original Query:**

```sql
-- Data Source: Swiggy RPA Course Wise Engagement
-- Dashboard: Swiggy RPA Daily Reports
-- Category: Swiggy RPA
-- Extracted: 2026-01-29 16:56:04
-- ============================================================

WITH base AS
  (SELECT nup.nugget_id,
          nup.user_id,
          jsonb_object_keys(nup.sessions) AS session_id,
          nup.sessions
   FROM user_details ud
   LEFT OUTER JOIN analytics.nuggets_user_progress nup ON nup.user_id = ud.uuid
   JOIN courses c ON nup.nugget_id = c.id
   WHERE ud.organization ILIKE '%rpa%'
     AND ud.phone_number IS NULL
     AND nup.status != 'sent'
     AND c.organization ILIKE '%rpa%'),
     cr AS
  (SELECT nup.nugget_id,
          nup.user_id,
          least(min(base.sessions -> session_id ->> 'courseStatus'), min(nup.status)) AS status
   FROM analytics.nuggets_user_progress nup
   LEFT OUTER JOIN base ON nup.nugget_id = base.nugget_id
   AND nup.user_id = base.user_id
   JOIN user_details ud ON nup.user_id = ud.uuid
   JOIN courses c ON nup.nugget_id = c.id
   WHERE ud.organization ILIKE '%rpa%'
     AND ud.phone_number IS NULL
     AND c.organization ILIKE '%rpa%'
     AND nup.status != 'sent'
   GROUP BY 1,
            2)
SELECT c.id AS "Course KNID",
       c.name AS "Course Name",
       count(distinct(CASE
                          WHEN cr.status IN ('inProgress', 'completed', 'notStarted') THEN cr.user_id
                          ELSE NULL
                      END)) AS total_opened_count,
       count(distinct(CASE
                          WHEN cr.status IN ('inProgress', 'completed') THEN cr.user_id
                          ELSE NULL
                      END)) AS total_started_count,
       count(distinct(CASE
                          WHEN cr.status = 'completed' THEN cr.user_id
                          ELSE NULL
                      END)) AS total_completed_count,
       count(distinct(CASE
                          WHEN cr.status IN ('inProgress', 'completed', 'notStarted')
                               AND length(ud.identifier) >= 10 THEN cr.user_id
                          ELSE NULL
                      END)) AS total_owner_opened_count,
       count(distinct(CASE
                          WHEN cr.status IN ('inProgress', 'completed')
                               AND length(ud.identifier) >= 10 THEN cr.user_id
                          ELSE NULL
                      END)) AS total_owner_started_count,
       count(distinct(CASE
                          WHEN cr.status = 'completed'
                               AND length(ud.identifier) >= 10 THEN cr.user_id
                          ELSE NULL
                      END)) AS total_owner_completed_count,
       count(distinct(CASE
                          WHEN cr.status IN ('inProgress', 'completed', 'notStarted')
                               AND length(ud.identifier) < 10 THEN cr.user_id
                          ELSE NULL
                      END)) AS total_partner_opened_count,
       count(distinct(CASE
                          WHEN cr.status IN ('inProgress', 'completed')
                               AND length(ud.identifier) < 10 THEN cr.user_id
                          ELSE NULL
                      END)) AS total_partner_started_count,
       count(distinct(CASE
                          WHEN cr.status = 'completed'
                               AND length(ud.identifier) < 10 THEN cr.user_id
                          ELSE NULL
                      END)) AS total_partner_completed_count
FROM courses c
JOIN cr ON c.id = cr.nugget_id
JOIN user_details ud ON cr.user_id = ud.uuid
WHERE c.is_archived != 'true'
  AND c.organization ILIKE '%rpa%'
  AND ud.phone_number IS NULL
GROUP BY 1,
         2
ORDER BY 3 DESC,
         4 DESC,
         5 DESC
```

---

## Swiggy RPA Engagement_Swiggy RPA Overall Engagement.sql

**Tables referenced:** analytics.nuggets_user_progress, courses, user_details

**Columns needing snake_case conversion:**

- `inProgress` -> `in_progress` (alias: `in_progress AS "inProgress"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)


**Original Query:**

```sql
-- Data Source: Swiggy RPA Engagement
-- Dashboard: Swiggy RPA Overall Engagement
-- Category: Swiggy RPA
-- Extracted: 2026-01-29 16:54:55
-- ============================================================

SELECT
		"QueryTable 1"."User ID" AS "User ID",
		"QueryTable 1"."Role" AS "Role",
		"QueryTable 1"."Course ID" AS "Course ID",
		"QueryTable 1"."Course Name" AS "Course Name",
		"QueryTable 1"."Opened" AS "Opened",
		"QueryTable 1"."Started" AS "Started",
		"QueryTable 1"."Completed" AS "Completed"
FROM(SELECT ud.identifier AS "User ID",
       CASE
           WHEN length(ud.identifier) >= 10 THEN 'Owner'
           ELSE 'Partner'
       END AS "Role",
       c.id AS "Course ID",
       c.name AS "Course Name",
       CASE
           WHEN nup.status IN ('completed',
                               'inProgress',
                               'notStarted') THEN 1
           ELSE 0
       END AS "Opened",
       CASE
           WHEN nup.status IN ('completed',
                               'inProgress') THEN 1
           ELSE 0
       END AS "Started",
       CASE
           WHEN nup.status IN ('completed') THEN 1
           ELSE 0
       END AS "Completed"
FROM user_details ud
JOIN analytics.nuggets_user_progress nup ON ud.uuid = nup.user_id
JOIN courses c ON nup.nugget_id = c.id
WHERE ud.phone_number IS NULL
  AND ud.organization ILIKE '%rpa%'
  AND nup.status != 'sent'
  and nup.updated_at between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
ORDER BY 2,
         1,
         4)"QueryTable 1"
```

---

## Swiggy RPA Regd and Active Users_Swiggy RPA Overall Engagement.sql

**Tables referenced:** analytics.nuggets_user_progress, user_details

**Columns needing snake_case conversion:**

- `inProgress` -> `in_progress` (alias: `in_progress AS "inProgress"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)


**Original Query:**

```sql
-- Data Source: Swiggy RPA Regd and Active Users
-- Dashboard: Swiggy RPA Overall Engagement
-- Category: Swiggy RPA
-- Extracted: 2026-01-29 16:56:02
-- ============================================================

SELECT count(distinct(ud.uuid)) AS "Total Regd Users",
       count(distinct(CASE
                          WHEN nup.status IN ('notStarted', 'inProgress', 'completed') THEN nup.user_id
                          ELSE NULL
                      END)) AS "Total Active Users",
       count(distinct(CASE
                          WHEN length(ud.identifier) >= 10 THEN ud.uuid
                          ELSE NULL
                      END)) AS "Total Regd Owners",
       count(distinct(CASE
                          WHEN nup.status IN ('notStarted', 'inProgress', 'completed')
                               AND length(ud.identifier) >= 10 THEN nup.user_id
                          ELSE NULL
                      END)) AS "Total Active Owners",
       count(distinct(CASE
                          WHEN length(ud.identifier) < 10 THEN ud.uuid
                          ELSE NULL
                      END)) AS "Total Regd Partners",
       count(distinct(CASE
                          WHEN nup.status IN ('notStarted', 'inProgress', 'completed')
                               AND length(ud.identifier) < 10 THEN nup.user_id
                          ELSE NULL
                      END)) AS "Total Active Partners"
FROM user_details ud
LEFT OUTER JOIN analytics.nuggets_user_progress nup ON ud.uuid = nup.user_id
WHERE ud.organization ILIKE '%rpa%'
  AND ud.phone_number IS NULL
```

---

## Swiggy RPA Registered Users_Swiggy RPA Daily Reports.sql

**Tables referenced:** user_details

**Original Query:**

```sql
-- Data Source: Swiggy RPA Registered Users
-- Dashboard: Swiggy RPA Daily Reports
-- Category: Swiggy RPA
-- Extracted: 2026-01-29 16:56:02
-- ============================================================

SELECT identifier
FROM user_details
WHERE organization ILIKE '%rpa%'
  AND phone_number IS NULL
```

---

## Swiggy RPA Registered Users_Swiggy RPA Overall Engagement.sql

**Tables referenced:** user_details

**Original Query:**

```sql
-- Data Source: Swiggy RPA Registered Users
-- Dashboard: Swiggy RPA Overall Engagement
-- Category: Swiggy RPA
-- Extracted: 2026-01-29 16:56:02
-- ============================================================

SELECT identifier
FROM user_details
WHERE organization ILIKE '%rpa%'
  AND phone_number IS NULL
```

---

## Swiggy RPA User Wise Engagement_Swiggy RPA Daily Reports.sql

**Tables referenced:** analytics.nuggets_user_progress, user_details

**Columns needing snake_case conversion:**

- `inProgress` -> `in_progress` (alias: `in_progress AS "inProgress"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)


**Original Query:**

```sql
-- Data Source: Swiggy RPA User Wise Engagement
-- Dashboard: Swiggy RPA Daily Reports
-- Category: Swiggy RPA
-- Extracted: 2026-01-29 16:56:03
-- ============================================================

SELECT ud.identifier as "User ID",
       CASE
           WHEN length(ud.identifier) >= 10 THEN 'Owner'
           ELSE 'Partner'
       END AS "Role",
       count(distinct(CASE
                          WHEN nup.status IN ('completed', 'inProgress', 'notStarted') THEN nup.nugget_id
                          ELSE NULL
                      END)) AS "Total Opened Courses",
       count(distinct(CASE
                          WHEN nup.status IN ('completed', 'inProgress') THEN nup.nugget_id
                          ELSE NULL
                      END)) AS "Total Started Courses",
       count(distinct(CASE
                          WHEN nup.status IN ('completed') THEN nup.nugget_id
                          ELSE NULL
                      END)) AS "Total Completed Courses"
FROM user_details ud
JOIN analytics.nuggets_user_progress nup ON ud.uuid = nup.user_id
WHERE ud.phone_number IS NULL
  AND ud.organization ILIKE '%rpa%'
  AND nup.status != 'sent'
GROUP BY 1,
         2
ORDER BY 3 DESC,
         4 DESC,
         5 DESC
```

---

## swiggypartnersearch_Swiggy Partner Search.sql

**Tables referenced:** rpo_report

**Original Query:**

```sql
-- Data Source: swiggypartnersearch
-- Dashboard: Swiggy Partner Search
-- Category: Swiggy RPA
-- Extracted: 2026-01-29 16:55:49
-- ============================================================

select * from rpo_report
```

---
