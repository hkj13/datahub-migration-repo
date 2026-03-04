# Wingtai MY

> Auto-generated on 2026-03-04 08:13

**Total queries:** 1

---

## WingTai MY Customer Feedback Responses_Customer Feedback.sql

**Tables referenced:** final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, nuggets, our, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `userName` -> `user_name` (alias: `user_name AS "userName"`)


**Original Query:**

```sql
-- Data Source: WingTai MY Customer Feedback Responses
-- Dashboard: Customer Feedback
-- Category: Wingtai MY
-- Extracted: 2026-01-29 16:55:27
-- ============================================================

WITH forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = '-O6YokiWNKwNUmIlCZYz'
   and organization ilike 'wingtaimy%'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT nugget_id AS form_knid,
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
                                                                                             qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT nugget_id AS form_knid,
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
   ORDER BY response_id,
            id DESC),
                                                                                             fr AS
  (SELECT *
   FROM form_responses fr
   JOIN fs ON fr.form_submit_id = fs.id),                                                                                             RAW AS   (
   SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.question,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice', 
                                 'linear_scale') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('checkboxes') THEN array_to_string(ARRAY
                                                                      (SELECT jsonb_array_elements_text(fr.response->'selected')
                                                                       UNION SELECT CASE
                                                                                        WHEN fr.response->>'otherText' IS NOT NULL THEN fr.response->>'otherText'
                                                                                        ELSE NULL
                                                                                    END), ', ')
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Singapore', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS response,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS section_response,
          form_name,
          fd.form_knid,
          fr.response_id,
          fr.submit_date AT TIME ZONE 'Asia/Singapore' AS submit_date
   FROM final_definition fd
   JOIN fr ON fr.question_id = fd.qid
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10
   ORDER BY 1,
            2,
            3)
            select sno as "Feedback No",
            submit_date as "Received At",
            max(case when section_no = 1 and q_no = 0 then section_response->'sender'->>'userName' else null end) as "Received By",
            max(case when question ilike 'Which wt+ outlet did you shop at?' then response else null end) as "Outlet",
            max(case when question ilike 'Your Name' then response else null end) as "Customer Name",
            max(case when question ilike 'Your email address' then response else null end) as "Email",
            max(case when question ilike 'How often do you shop with us?' then response else null end) as "Shopping Frequency",
            max(case when question ilike 'Are you our wt+ member?' then response else null end) as "wt+ Member?",
            max(case when question ilike 'Have you made a purchase from our store today?' then response else null end) as "Purchase Today?",
            max(case when question ilike 'Tell us about our Staff''s Service' then response::int else null end) as "Service Rating",
            max(case when question ilike 'Tell us about our Store Ambience' then response::int else null end) as "Ambience Rating",
            max(case when question ilike 'Tell us about our Merchandise' then response::int else null end) as "Merch Rating",
            max(case when question ilike 'Overall, how would you rate your shopping experience?' then response::int else null end) as "Overall Experience Rating",
            max(case when question ilike 'Is there a staff who particularly stood out?' then response else null end) as "Standout Staff",
            max(case when question ilike 'What did you like /dislike about his /her service?' then response else null end) as "Remarks About Staff",
            max(case when question ilike 'Tell us more about our staff’s friendliness' then response else null end) as "Friendliness",
			 max(case when question ilike 'Tell us more about our staff’s knowledge%' then response else null end) as "Knowledge",
            max(case when question ilike 'Tell us more about our staff’s helpfulness' then response else null end) as "Helpfulness",
            max(case when question ilike 'Tell us more about our staff’s promptness' then response else null end) as "Promptness",
            max(case when question ilike 'What do you think about our merchandise quality?' then response else null end) as "Quality",
            max(case when question ilike 'What do you think about our merchandise pricing?' then response else null end) as "Pricing",
            max(case when question ilike 'What do you think about our merchandise variety?' then response else null end) as "Variety",
            max(case when question ilike 'What do you think about our merchandise trendiness?' then response else null end) as "Trendiness",
            max(case when question ilike 'What do you think about our store''s merchandise layout?' then response else null end) as "Layout",
            max(case when question ilike 'What do you think about our store''s window display?' then response else null end) as "Window Display",
            max(case when question ilike 'What do you think about our store''s cleanliness?' then response else null end) as "Cleanliness",
            form_knid as "Form KNID",
            response_id as "Submission KNID"
			from raw
            group by 1, 2, 27, 28
```

---
