# Little Farms

> Auto-generated on 2026-03-04 08:13

**Total queries:** 2

---

## little farms learn_Learn.sql

**Tables referenced:** data_team.little_farms_learn, user_acl, user_details, user_groups

**Original Query:**

```sql
-- Data Source: little farms learn
-- Dashboard: Learn
-- Category: Little Farms
-- Extracted: 2026-01-29 16:54:08
-- ============================================================

WITH user_acl AS (
    SELECT 
        ud.organization,
        ud.uuid,
        ud.first_name || ' ' || ud.last_name AS emp_name,
        ud.identifier AS emp_id,
        ud.division,
        ud.identifier,
        ud.sub_division,
        ud.job_location,
        ud.department,
        ud.designation,
        ud.job_type
    FROM user_details ud
    WHERE 
        organization = @{{:OrganizationParameter}} AND
        is_active = 'true' AND
        job_location NOT IN ('KNOW', 'All') AND
        job_location NOT ILIKE 'Head Office%' AND (
            (SELECT is_super_admin FROM user_details WHERE uuid = @{{:UuidParameter}})
            OR uuid IN (
                SELECT DISTINCT user_id
                FROM user_groups ug1
                WHERE ug1.group_id IN (
                    SELECT group_id
                    FROM user_groups ug2
                    WHERE ug2.user_id = @{{:UuidParameter}} AND ug2.has_access = TRUE
                )
                AND ug1.is_active = TRUE
            )
        )
    GROUP BY 1,2,3,4,5,6,7,8,9,10
)
select l.* from data_team.little_farms_learn l
join user_acl on l.location = user_acl.job_location 
where shared_at between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
```

---

## little farms quiz_Learn.sql

**Tables referenced:** lessons, public.courses, public.lesson_cards, qd, quiz.quiz_responses

**Original Query:**

```sql
-- Data Source: little farms quiz
-- Dashboard: Learn
-- Category: Little Farms
-- Extracted: 2026-01-29 16:55:19
-- ============================================================

WITH qd AS
  (SELECT l.course_id,
          c.name AS course_name,
          lc.id AS quizcard_id,
          lc.title AS quiz_name,
          q.question_index AS question_id, 
 q.question_obj->>'text' AS question_text
   FROM public.lesson_cards lc
   JOIN lessons l ON lc.lesson_id = l.id
   JOIN public.courses c ON l.course_id = c.id,
                            LATERAL jsonb_array_elements(lc.payload->'questions') WITH
   ORDINALITY AS q(question_obj, question_index)
   WHERE c.organization = 'little-farms-fireworks'
   ORDER BY course_name,
            quizcard_id,
            question_id)
SELECT qd.*,
       sum(CASE
               WHEN qr.is_correct = 'true' THEN 1
               ELSE 0
           END) AS total_correct,
       sum(CASE
               WHEN qr.is_correct = 'false' THEN 1
               ELSE 0
           END) AS total_wrong
FROM qd
 JOIN quiz.quiz_responses qr ON qd.quizcard_id = qr.card_id
AND qd.course_id = qr.course_id
AND qd.question_id - 1 = qr.question_id
and qr.created_at at time zone 'Asia/Singapore' between @{{:little farms learn.Date Range.START}}::timestamp and @{{:little farms learn.Date Range.END}}::timestamp + interval '1 day'
GROUP BY 1,
         2,
         3,
         4,
         5,
         6
```

---
