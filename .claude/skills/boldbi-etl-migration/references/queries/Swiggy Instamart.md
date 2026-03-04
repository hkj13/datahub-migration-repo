# Swiggy Instamart

> Auto-generated on 2026-03-04 08:13

**Total queries:** 36

---

## Clean Sweep Audit Summary_Clean Sweep.sql

**Tables referenced:** Pod, checkpoint_master_sheet_table, form_submissions, location_map, user_Details

**Original Query:**

```sql
-- Data Source: Clean Sweep Audit Summary
-- Dashboard: Clean Sweep
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:54:48
-- ============================================================

WITH location_map AS
  (SELECT DISTINCT ON (division,
                       sub_division,
                       regexp_replace(job_location, '([0-9]+).*', '\1')) division AS region,
                      sub_division AS city,
                      regexp_replace(job_location, '([0-9]+).*', '\1') AS pod
   FROM user_Details
   WHERE (regexp_replace(job_location, '([0-9]+).*', '\1') IS NOT NULL
          OR regexp_replace(job_location, '([0-9]+).*', '\1') != '')
     AND is_active = TRUE
   ORDER BY 1,
            2,
            3,
            created_at DESC)
SELECT distinct on(audit_submission_number ) audit_submission_number AS "Audit Report No",
lm.region AS "Region",
       initcap(lm.city) AS "City",
       lm.pod AS "Pod",
	   initcap(cms.store_id) as "Pod Name",
       cms.audit_type AS "Audit Type",
       cms.audit_main_theme AS "Audit",
       auditor_name AS "Auditor",
       to_timestamp(cms.audit_started_at/1000) AT TIME ZONE 'Asia/Kolkata' AS "Audit Started At",
                                                            audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
															fs.approx_distance_in_km as "Audit Distance from Pod",
                                                                                            
                                                                                                                    sum(CASE
                                                                                                                        WHEN result_score = '' THEN NULL
                                                                                                                        ELSE result_score::numeric
                                                                                                                    END) / sum(CASE
                                                                                                                        WHEN result_score = '' THEN NULL
                                                                                                                        ELSE max_score::numeric
                                                                                                                    END) AS "Audit Score",
                                                                                                                    sum(total_follow_up_tasks) AS "Assigned Action Count",
                                                                                                                    sum(total_closed_follow_up_tasks) AS "Closed Action Count",
                                                                                                                    audit_submission_knid AS "Audit Report KNID"
FROM checkpoint_master_sheet_table cms
join form_submissions fs on cms.audit_submission_knid = fs.response_id
left outer JOIN location_map lm ON regexp_replace(cms.store_id, '([0-9]+).*', '\1') = lm.pod
WHERE cms.audit_main_theme ILIKE 'Pod Compliance%'
and cms.checkpoint IN (
'1) Validate cleaning checklists of racks, chillers/freezers & toilets.',
 '2) “No Cockroaches, Lizards, House Flies, Mosquito, Rodent dropping, rat bites, are observed in POD at any area. Pest control shall be in place. ”',
  '3) Functional Pest-o-Flash or Insectocutor shall be used inside the POD, positioned at the entrance of the POD and at 6-7 feet height. Glue pads shall be discarded & replaced with new as and when insects are filled up.',
  '4) Dump bins & Dust bins used shall be of Cap Closure & Bins should be in clean condition. No Dump Stock have contact with Fresh and good material . Dump shall be kept seperately and discarded on time.',
  '5) All Shelves are clean, no cob web, no dust, no rust, no spillage of Food & Non-food (FMCG) products on racks, chiller, freezers & Floors',
  '6) Timely removal of empty carton boxes',
  '7) “Washrooms & Floors shall be kept regularly Clean & hygienic and Running water available. (Auditor must check for female restroom in case of female employees)”',
  '8) No Expired articles found in racks ( F&V, Ambient, Chiller and Freezer). If 1 Expiry is seen no negotiation Score will be “0”',
  '11) Temperature checks for DSD / Warehouse F&V Products shall be in place, If DSD / Warehouse Cut F&V are not meeting <10 Degree Celcius, products must be rejected by PODs',
  '12) F&V articles are stored as per the storage SOP - A, C, F & T',
  '13) No F&V is overloaded in racks',
  '14) F&V Storage shall be organized at Racks, Crates, Freezers & Chillers',
  '15) Leaf articles shall be covered with Pre-pack polybags.',
  '17) “20 SKUs (Including F&V) FIFO/FEFO check - 100% accuracy ”',
  '18) “The temperature of ”“Reach-In/Walk-In Freezer”“ shall me maintained between ”“-18 and -22”“ degree Celsius If the ideal temperature is not attained , auditor to recheck after 1hr.”',
  '19) “The temperature of ”“Reach-In/Walk-In Chiller”“ shall me maintained between ”“0 and 5”“ degree Celsius If the ideal temperature is not attained , auditor to recheck after 1hr.”',
  '20) “F&V Room shall be maintained at +18 to +22 degree Celsius throughout the F&V Storage If the ideal temperature is not attained , auditor to recheck after 1hr.”',
  '21) F&V Shelves are free for Rotten/Rotting Produce',
  '22) Cold room, Chiller rooms & Chest freezers are in best working condition with no ice formation, No overload of materials in it, No storage of dumps',
  '23) Temperature checks of Chillers & freezers shall be in place',
  '24) Are atta, breads, buns, and eggs stacked based on the First Expired, First Out (FEFO) method. If any SKUs found deviating the FEFO process, no negotiation Score will be “0”',
  '28) Are ice-cream SKUs packed using Insulation bag / Ice bag? - Sampling',
  '29) Calibrated and functional Thermometer is available at POD.',
  '38) POD shall have valid FSSAI License that shall be pasted on wall and visible clearly',
  '39) POD shall have updated A3 Size Coloured Food Safety Display Board, shall be pasted on wall and visible clearl'
)
AND audit_submitted_at AT TIME ZONE 'Asia/Kolkata' BETWEEN @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15
ORDER BY 1,
         2,
         3,
         4,
         5,
         8 DESC
```

---

## Clean Sweep Audit_Clean Sweep.sql

**Tables referenced:** checkpoint_master_sheet_table, location_map, user_Details

**Original Query:**

```sql
-- Data Source: Clean Sweep Audit
-- Dashboard: Clean Sweep
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:54:49
-- ============================================================

WITH location_map AS
  (SELECT DISTINCT ON (division,
                       sub_division,
                       regexp_replace(job_location, '([0-9]+).*', '\1')) division AS region,
                      sub_division AS city,
                      regexp_replace(job_location, '([0-9]+).*', '\1') AS pod
   FROM user_Details
   WHERE (regexp_replace(job_location, '([0-9]+).*', '\1') IS NOT NULL
          OR regexp_replace(job_location, '([0-9]+).*', '\1') != '')
     AND is_active = TRUE
   ORDER BY 1,
            2,
            3,
            created_at DESC)
SELECT lm.region AS "Region",
       initcap(lm.city) AS "City",
       lm.pod AS "Pod",
	   initcap(cms.store_id) as "Pod Name",
       cms.audit_type AS "Audit Type",
       cms.audit_main_theme AS "Audit",
       audit_submission_number AS "Audit Report No",
       auditor_name AS "Auditor",
       to_timestamp(cms.audit_started_at/1000) AT TIME ZONE 'Asia/Kolkata' AS "Audit Started At",
                                                            audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
                                                                                            theme AS "Theme",
                                                                                            CHECKPOINT AS "Attribute",
                                                                                                          criticality AS "Criticality",
                                                                                                          RESULT AS "Result",
                                                                                                                    CASE
                                                                                                                        WHEN result_score = '' THEN NULL
                                                                                                                        ELSE result_score::numeric
                                                                                                                    END AS "Actual Score",
                                                                                                                    CASE
                                                                                                                        WHEN result_score = '' THEN NULL
                                                                                                                        ELSE max_score::numeric
                                                                                                                    END AS "Max Score",
                                                                                                                    auditor_observations AS "Observations",
                                                                                                                    total_follow_up_tasks AS "Assigned Action Count",
                                                                                                                    total_closed_follow_up_tasks AS "Closed Action Count",
                                                                                                                    audit_submission_knid AS "Audit Report KNID",
                                                                                                                    checkpoint_knid AS "Attribute KNID"
FROM checkpoint_master_sheet_table cms
left outer JOIN location_map lm ON regexp_replace(cms.store_id, '([0-9]+).*', '\1') = lm.pod
WHERE cms.audit_main_theme ILIKE 'Pod Compliance%'
and cms.checkpoint IN (
'1) Validate cleaning checklists of racks, chillers/freezers & toilets.',
 '2) “No Cockroaches, Lizards, House Flies, Mosquito, Rodent dropping, rat bites, are observed in POD at any area. Pest control shall be in place. ”',
  '3) Functional Pest-o-Flash or Insectocutor shall be used inside the POD, positioned at the entrance of the POD and at 6-7 feet height. Glue pads shall be discarded & replaced with new as and when insects are filled up.',
  '4) Dump bins & Dust bins used shall be of Cap Closure & Bins should be in clean condition. No Dump Stock have contact with Fresh and good material . Dump shall be kept seperately and discarded on time.',
  '5) All Shelves are clean, no cob web, no dust, no rust, no spillage of Food & Non-food (FMCG) products on racks, chiller, freezers & Floors',
  '6) Timely removal of empty carton boxes',
  '7) “Washrooms & Floors shall be kept regularly Clean & hygienic and Running water available. (Auditor must check for female restroom in case of female employees)”',
  '8) No Expired articles found in racks ( F&V, Ambient, Chiller and Freezer). If 1 Expiry is seen no negotiation Score will be “0”',
  '11) Temperature checks for DSD / Warehouse F&V Products shall be in place, If DSD / Warehouse Cut F&V are not meeting <10 Degree Celcius, products must be rejected by PODs',
  '12) F&V articles are stored as per the storage SOP - A, C, F & T',
  '13) No F&V is overloaded in racks',
  '14) F&V Storage shall be organized at Racks, Crates, Freezers & Chillers',
  '15) Leaf articles shall be covered with Pre-pack polybags.',
  '17) “20 SKUs (Including F&V) FIFO/FEFO check - 100% accuracy ”',
  '18) “The temperature of ”“Reach-In/Walk-In Freezer”“ shall me maintained between ”“-18 and -22”“ degree Celsius If the ideal temperature is not attained , auditor to recheck after 1hr.”',
  '19) “The temperature of ”“Reach-In/Walk-In Chiller”“ shall me maintained between ”“0 and 5”“ degree Celsius If the ideal temperature is not attained , auditor to recheck after 1hr.”',
  '20) “F&V Room shall be maintained at +18 to +22 degree Celsius throughout the F&V Storage If the ideal temperature is not attained , auditor to recheck after 1hr.”',
  '21) F&V Shelves are free for Rotten/Rotting Produce',
  '22) Cold room, Chiller rooms & Chest freezers are in best working condition with no ice formation, No overload of materials in it, No storage of dumps',
  '23) Temperature checks of Chillers & freezers shall be in place',
  '24) Are atta, breads, buns, and eggs stacked based on the First Expired, First Out (FEFO) method. If any SKUs found deviating the FEFO process, no negotiation Score will be “0”',
  '28) Are ice-cream SKUs packed using Insulation bag / Ice bag? - Sampling',
  '29) Calibrated and functional Thermometer is available at POD.',
  '38) POD shall have valid FSSAI License that shall be pasted on wall and visible clearly',
  '39) POD shall have updated A3 Size Coloured Food Safety Display Board, shall be pasted on wall and visible clearl'
)
AND audit_submitted_at AT TIME ZONE 'Asia/Kolkata' between @{{:Clean Sweep Audit Summary.Date Range.START}}::timestamp and @{{:Clean Sweep Audit Summary.Date Range.END}}::timestamp + interval '1 day'
ORDER BY 1,
         2,
         3,
         4,
         5,
         8 DESC
```

---

## Instamart Audit Details_Audits.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, organizations, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Instamart Audit Details
-- Dashboard: Audits
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:58:23
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
          regexp_replace(audit_main_theme, '\s*\(.*\)', '') as audit_main_theme,
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
   WHERE organization_id = @{{:OrganizationParameter}}
   AND (audit_main_theme ilike '%COM%' OR audit_main_theme ilike 'POD%'))
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
having audit_main_theme is not null
ORDER BY 1,
         2,
         4
```

---

## Instamart Audit Summary_Audits.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, location_acl, organizations, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Instamart Audit Summary
-- Dashboard: Audits
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:58:23
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
          regexp_replace(audit_main_theme, '\s*\(.*\)', '') as audit_main_theme,
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
   WHERE organization_id = @{{:OrganizationParameter}}
   AND (audit_main_theme ilike '%COM%' OR audit_main_theme ilike 'POD%'))
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
having audit_main_theme is not null
ORDER BY 1,
         2,
         4
```

---

## Instamart COM Gemba Adoption_GEMBA Walk Adoption.sql

**Tables referenced:** com_compliance, com_forms, com_responses, expected_com, form_responses, form_submissions, fs, generate_series, location_map, nuggets, public.locations, public.user_details

**Original Query:**

```sql
-- Data Source: Instamart COM Gemba Adoption
-- Dashboard: GEMBA Walk Adoption
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:58:08
-- ============================================================

WITH com_forms AS
  (SELECT id AS form_knid,
          'Walk to Elevate - COM' AS form_name
   FROM nuggets
   WHERE organization = 'swiggy-mart-whirlpool'
     AND classification_type = 'form'
     AND title LIKE 'Walk to Elevate - COM%'),
     expected_com AS
  (SELECT *
   FROM
     (SELECT date::date
      FROM generate_series(date_trunc('Week', @{{:Instamart SM Gemba Adoption.Date Range.START}}::timestamp), date_trunc('Week', least(current_timestamp at time zone 'Asia/Kolkata', @{{:Instamart SM Gemba Adoption.Date Range.END}}::timestamp)), '1 week'::interval) AS date) AS cal
   CROSS JOIN
     (SELECT SUBSTRING(location_name
                       FROM '\d+') AS pod
      FROM public.locations
      WHERE location_name ~ '^\d{3}'
        AND organization = 'swiggy-mart-whirlpool'
        AND is_active = TRUE) outlets
   CROSS JOIN
     (SELECT 'Walk to Elevate - COM' AS form)),
     fs AS
  (SELECT DISTINCT ON (fs.response_id) date_trunc('Week', (fs.submit_date AT TIME ZONE 'Asia/Kolkata'))::date AS date,
                      'Walk to Elevate - COM' AS form,
                      fs.response_id,
                      fs.sno,
                      fs.location,
                      fs.id
   FROM form_submissions fs
   WHERE fs.form_id IN
       (SELECT form_knid
        FROM com_forms)
     AND submit_date AT TIME ZONE 'Asia/Kolkata' BETWEEN @{{:Instamart SM Gemba Adoption.Date Range.START}}::timestamp AND @{{:Instamart SM Gemba Adoption.Date Range.END}}::timestamp + interval '1 day'
   ORDER BY fs.response_id,
            fs.id),
     com_responses AS
  (SELECT fs.date,
          form,
          response_id,
          sno,
          SUBSTRING(COALESCE(fr.response->>'name', fs.location)
                    FROM '\d+') AS pod
   FROM fs
   LEFT OUTER JOIN form_responses fr ON fs.id = fr.form_submit_id
   AND fr.response->>'name' IS NOT NULL
   AND fr.response->>'id' IS NOT NULL
   WHERE COALESCE(fr.response->>'name', fs.location) ~ '^\d{3}' ),
     com_compliance AS
  (SELECT expected_com.date AS "Date",
          expected_com.form AS "Form",
          expected_com.pod AS "Pod ID",
          CASE
              WHEN com_responses.response_id IS NOT NULL THEN 1
              ELSE 0
          END AS "Compliance",
          CASE
              WHEN com_responses.response_id IS NOT NULL THEN 'Completed'
              ELSE 'Missed'
          END AS "Status",
          com_responses.sno AS "Submission No",
          com_responses.response_id AS "Submission KNID"
   FROM expected_com
   LEFT OUTER JOIN com_responses ON expected_com.date = com_responses.date
   AND expected_com.form = com_responses.form
   AND expected_com.pod = com_responses.pod
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7),
     location_map AS
  (SELECT DISTINCT ON (SUBSTRING(job_location
                                 FROM '\d+')) SUBSTRING(job_location
                                                        FROM '\d+') AS pod,
                      division,
                      sub_division
   FROM public.user_details
   WHERE job_location ~ '^\d{3}'
     AND is_active = TRUE
   ORDER BY SUBSTRING(job_location
                      FROM '\d+'),
            created_at DESC)
SELECT compliance."Date",
       compliance."Form",
       compliance."Pod ID" AS "Location",
       location_map.division AS "Region",
       location_map.sub_division AS "City",
       compliance."Status",
       compliance."Compliance",
       compliance."Submission No",
       compliance."Submission KNID"
FROM com_compliance AS compliance
LEFT OUTER JOIN location_map ON compliance."Pod ID" = location_map.pod
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9
ORDER BY 1,
         2,
         3,
         4,
         5
```

---

## Instamart Course Adoption Report_Course Reports.sql

**Tables referenced:** analytics.lms_raw_analytics, analytics.quiz_responses, cards, course_consumed_at, final_quiz_cards, final_scores, first_course_consumed, full_progress, latest_attempt, latest_course_received, latest_course_shares, latest_received, latest_share_ids, latest_shares, progress, public.courses, public.learning_journey_courses, public.lesson_cards, public.lessons, public.users, quiz_cards

**Columns needing snake_case conversion:**

- `cardId` -> `card_id` (alias: `card_id AS "cardId"`)

- `consumedAt` -> `consumed_at` (alias: `consumed_at AS "consumedAt"`)

- `consumedCount` -> `consumed_count` (alias: `consumed_count AS "consumedCount"`)

- `courseID` -> `course_id` (alias: `course_id AS "courseID"`)

- `courseId` -> `course_id` (alias: `course_id AS "courseId"`)

- `createdAt` -> `created_at` (alias: `created_at AS "createdAt"`)

- `firstName` -> `first_name` (alias: `first_name AS "firstName"`)

- `gwGnYHWZDJudRMYfZeXjkY` -> `gw_gn_yhwzd_jud_rm_yf_ze_xjk_y` (alias: `gw_gn_yhwzd_jud_rm_yf_ze_xjk_y AS "gwGnYHWZDJudRMYfZeXjkY"`)

- `isArchived` -> `is_archived` (alias: `is_archived AS "isArchived"`)

- `isCorrect` -> `is_correct` (alias: `is_correct AS "isCorrect"`)

- `lastName` -> `last_name` (alias: `last_name AS "lastName"`)

- `latestAttempt` -> `latest_attempt` (alias: `latest_attempt AS "latestAttempt"`)

- `learningJourneyId` -> `learning_journey_id` (alias: `learning_journey_id AS "learningJourneyId"`)

- `lessonId` -> `lesson_id` (alias: `lesson_id AS "lessonId"`)

- `ljId` -> `lj_id` (alias: `lj_id AS "ljId"`)

- `nuggetID` -> `nugget_id` (alias: `nugget_id AS "nuggetID"`)

- `nuggetId` -> `nugget_id` (alias: `nugget_id AS "nuggetId"`)

- `phoneNumber` -> `phone_number` (alias: `phone_number AS "phoneNumber"`)

- `qCount` -> `q_count` (alias: `q_count AS "qCount"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `quizCardId` -> `quiz_card_id` (alias: `quiz_card_id AS "quizCardId"`)

- `receivedAt` -> `received_at` (alias: `received_at AS "receivedAt"`)

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `shareId` -> `share_id` (alias: `share_id AS "shareId"`)

- `totalCards` -> `total_cards` (alias: `total_cards AS "totalCards"`)

- `userID` -> `user_id` (alias: `user_id AS "userID"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Instamart Course Adoption Report
-- Dashboard: Course Reports
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:59:18
-- ============================================================

WITH latest_shares AS
  (SELECT nuggetId,
          shareId,
          userId,
          createdAt,
          ROW_NUMBER() OVER (PARTITION BY nuggetId,
                                          userId,
                                          shareId
                             ORDER BY createdAt DESC) AS rn
   FROM `analytics.lms_raw_analytics`
   WHERE event in ('sent', 'created')
     AND TIMESTAMP_ADD(createdAt, INTERVAL 330 MINUTE) between @{{:Date Range.START}} and timestamp_add(@{{:Date Range.END}}, interval 1 day)),
     latest_share_ids AS
  (SELECT ls.nuggetId,
          ls.shareId,
          ls.userId,
          max(TIMESTAMP_ADD(ls.createdAt, INTERVAL 330 MINUTE)) AS sentAt
   FROM latest_shares ls
   WHERE rn = 1
   GROUP BY 1,
            2,
            3),
     latest_course_shares AS
  (SELECT lsi.userId,
          lsi.nuggetId AS courseId,
          lsi.shareId,
          lsi.sentAt
   FROM latest_share_ids lsi
   JOIN public.courses c ON lsi.nuggetID = c.id
   WHERE c.organization = 'swiggy-mart-whirlpool'
     AND (c.isArchived = FALSE
          OR c.isArchived IS NULL)
   UNION ALL SELECT lsi.userId,
                    ljc.courseId,
                    lsi.shareId,
                    lsi.sentAt
   FROM latest_share_ids lsi
   JOIN public.learning_journey_courses ljc ON lsi.nuggetId = ljc.learningJourneyId
   JOIN public.courses c ON ljc.courseId = c.id
   WHERE c.organization = 'swiggy-mart-whirlpool'
     AND (c.isArchived = FALSE
          OR c.isArchived IS NULL)),
     latest_received AS
  (SELECT ra.userId,
          ra.nuggetId,
          ra.courseId,
          ra.ljId,
          ra.shareId,
          TIMESTAMP_ADD(ra.createdAt, INTERVAL 330 MINUTE) AS receivedAt
   FROM `analytics.lms_raw_analytics` ra
   JOIN latest_share_ids lsi ON ra.userId = lsi.userId
   AND ra.nuggetId = lsi.nuggetId
   AND ra.shareId = lsi.shareId
   WHERE ra.event NOT IN ('sent', 'created')),
     latest_course_received AS
  (SELECT lr.userId,
          lr.nuggetId AS courseId,
          lr.shareId,
          min(lr.receivedAt) AS receivedAt
   FROM latest_received lr
   JOIN public.courses c ON lr.nuggetID = c.id
   OR lr.courseId = c.id
   WHERE c.organization = 'swiggy-mart-whirlpool'
     AND (c.isArchived = FALSE
          OR c.isArchived IS NULL)
   GROUP BY 1,
            2,
            3
   UNION ALL SELECT lr.userId,
                    ljc.courseId,
                    lr.shareId,
                    min(lr.receivedAt) AS receivedAt
   FROM latest_received lr
   JOIN public.learning_journey_courses ljc ON lr.nuggetId = ljc.learningJourneyId
   OR lr.ljId = ljc.learningJourneyId
   OR lr.courseID = ljc.courseId
   JOIN public.courses c ON ljc.courseId = c.id
   WHERE c.organization = 'swiggy-mart-whirlpool'
     AND (c.isArchived = FALSE
          OR c.isArchived IS NULL)
   GROUP BY 1,
            2,
            3),
     cards AS
  (SELECT l.courseId,
          lc.id AS cardId
   FROM public.lesson_cards lc
   JOIN public.lessons l ON l.id = lc.lessonId
   JOIN public.courses c ON l.courseId = c.id
   WHERE c.organization = 'swiggy-mart-whirlpool'
     AND (c.isArchived = FALSE
          OR c.isArchived IS NULL)
   GROUP BY 1,
            2),
     course_consumed_at AS
  (SELECT ra.userId,
          ra.courseId,
          ra.shareId,
          ra.lang,
          TIMESTAMP_ADD(ra.createdAt, INTERVAL 330 MINUTE) AS consumedAt,
          row_number() OVER (PARTITION BY ra.userId,
                                          ra.nuggetId
                             ORDER BY ra.createdAt) AS rn
   FROM analytics.lms_raw_analytics ra
   JOIN latest_course_shares lcs ON ra.userId = lcs.userId
   AND ra.nuggetId = lcs.courseId
   AND ra.shareId = lcs.shareId
   WHERE ra.event = 'consumed'),
     first_course_consumed AS
  (SELECT cca.userId,
          cca.courseId,
          cca.shareId,
          cca.lang,
          cca.consumedAt
   FROM course_consumed_at cca
   WHERE rn = 1 ),
     full_progress AS
  (SELECT ra.userId,
          cards.courseId,
          cards.cardId,
          TIMESTAMP_ADD(ra.createdAt, INTERVAL 330 MINUTE) AS consumedAt,
          row_number() OVER (PARTITION BY ra.userId,
                                          ra.nuggetId
                             ORDER BY ra.createdAt) AS rn
   FROM analytics.lms_raw_analytics ra
   JOIN latest_course_shares lcs ON ra.userId = lcs.userId
   AND ra.courseId = lcs.courseId
   AND ra.shareId = lcs.shareId
   JOIN cards ON ra.nuggetId = cards.cardId
   LEFT OUTER JOIN first_course_consumed fcc ON ra.userID = fcc.userId
   AND ra.courseId = fcc.courseId
   AND ra.shareId = fcc.shareId
   WHERE ra.event = 'consumed'
     AND (fcc.consumedAt IS NULL
     OR TIMESTAMP_ADD(ra.createdAt, INTERVAL 330 MINUTE) < TIMESTAMP_ADD(fcc.consumedAt, INTERVAL 330 MINUTE))),
     progress AS
  (SELECT fp.userId,
          fp.courseId,
          count(distinct(fp.cardId)) AS consumedCount
   FROM full_progress fp
   WHERE rn = 1
   GROUP BY 1,
            2),
     quiz_cards AS
  (SELECT c.id AS courseId,
          lc.id AS quizCardId,
          array_length(json_extract_array((parse_json(lc.payload)).questions)) AS qCount,
          row_number() OVER (PARTITION BY c.id
                             ORDER BY l.seq DESC, lc.seq DESC) AS rn
   FROM public.lesson_cards lc
   JOIN public.lessons l ON lc.lessonId = l.id
   JOIN public.courses c ON l.courseId = c.id
   WHERE c.organization = 'swiggy-mart-whirlpool'
     AND (c.isArchived = FALSE
          OR c.isArchived IS NULL)
     AND lc.type = 'quiz'
   ORDER BY c.id,
            lc.id,
            l.seq DESC, lc.seq DESC),
     final_quiz_cards AS
  (SELECT *
   FROM quiz_cards
   WHERE rn = 1),
     latest_attempt AS
  (SELECT qr.userId,
          qr.courseId,
          qr.shareId,
          qr.cardId,
          qr.questionId,
          max(attempt) AS latestAttempt
   FROM analytics.quiz_responses qr
   JOIN latest_course_shares lcs ON qr.userId = lcs.userId
   AND qr.courseId = lcs.courseId
   AND qr.shareId = lcs.shareId
   JOIN final_quiz_cards qc ON qr.courseId = qc.courseId
   AND qr.cardId = qc.quizCardId
   GROUP BY 1,
            2,
            3,
            4,
            5),
     final_scores AS
  (SELECT la.userId,
          la.courseId,
          count(distinct(CASE
                             WHEN qr.isCorrect = TRUE THEN qr.questionId
                             ELSE NULL
                         END)) / qc.qCount AS score
   FROM latest_attempt la
   JOIN analytics.quiz_responses qr ON la.userId = qr.userId
   AND la.courseId = qr.courseId
   AND la.shareId = qr.shareId
   AND la.cardId = qr.cardId
   AND la.questionId = qr.questionId
   AND la.latestAttempt = qr.attempt
   JOIN final_quiz_cards qc ON qr.courseId = qc.courseId
   AND qr.cardId = qc.quizCardId
   GROUP BY 1,
            2,
            qc.qCount)
SELECT u.identifier AS `Staff ID`,
       u.firstName||' '||u.lastName AS `Staff Name`,
       u.phoneNumber AS `Phone Number`,
       CASE
           WHEN c.id = 'gwGnYHWZDJudRMYfZeXjkY' THEN 'Day 1-1 '||c.name
           WHEN c.id = 'gjUQtz8uDaxyhme6nVScvi' THEN 'Day 2-1 '||c.name
           WHEN c.id = 'bidvm66pkDfoZ8FrBJsgoZ' THEN 'Day 3-1 '||c.name
           WHEN c.id = '4VrK1gbCQZ4MS32xMtKo4w' THEN 'Day 3-2 '||c.name
           WHEN c.id = '4SFg55oeWXSiWK322YYJPD' THEN 'Day 4-1 '||c.name
           WHEN c.id = '7De2YCm42esCR4szqL2wt1' THEN 'Day 5-1 '||c.name
           WHEN c.id = 'bgLGYXpa4uGQGNtXFQh7tS' THEN 'Day 5-2 '||c.name
           ELSE c.name
       END AS `Course Name`,
       TIMESTAMP_ADD(u.createdAt, INTERVAL 330 MINUTE) AS `Joined At`,
       lcs.sentAt AS `Enrolled At`,
       CASE
           WHEN fcc.consumedAt IS NOT NULL
                OR (c.totalCards > 0
                    AND p.consumedCount = c.totalCards) THEN 'Completed'
           WHEN c.totalCards > 0
                AND p.consumedCount > 0
                AND p.consumedCount < c.totalCards THEN 'In Progress'
           WHEN c.totalCards > 0
                AND (p.consumedCount = 0
                     OR p.consumedCount IS NULL) THEN 'Not Started'
           ELSE NULL
       END AS `Status`,
       CASE
           WHEN fcc.consumedAt IS NOT NULL THEN 1
           ELSE p.consumedCount / c.totalCards
       END AS `Completion %`,
       s.score AS `Final Quiz Score`,
       fcc.consumedAt AS `Completed At`,
       upper(fcc.lang) AS `Language`,
       lcs.userID AS `User KNID`,
       lcs.courseId AS `Course KNID`,
       lcs.shareId AS `Share KNID`,
       1 AS `Enrolled`,
       CASE
           WHEN (lcr.receivedAt IS NOT NULL)
                OR (fcc.consumedAt IS NOT NULL
                    OR (c.totalCards > 0
                        AND p.consumedCount = c.totalCards))
                OR (c.totalCards > 0
                    AND p.consumedCount > 0
                    AND p.consumedCount < c.totalCards) THEN 1
           ELSE 0
       END AS `Logged In`,
       CASE
           WHEN fcc.consumedAt IS NOT NULL
                OR (c.totalCards > 0
                    AND p.consumedCount = c.totalCards)
                OR (c.totalCards > 0
                    AND p.consumedCount > 0
                    AND p.consumedCount < c.totalCards) THEN 1
           ELSE 0
       END AS `Adopted`,
       CASE
           WHEN fcc.consumedAt IS NOT NULL
                OR (c.totalCards > 0
                    AND p.consumedCount = c.totalCards) THEN 1
           ELSE 0
       END AS `Completed`,
FROM latest_course_shares lcs
LEFT OUTER JOIN latest_course_received lcr ON lcs.userId = lcr.userId
AND lcs.courseId = lcr.courseId
LEFT OUTER JOIN progress p ON lcs.userId = p.userId
AND lcs.courseId = p.courseId
LEFT OUTER JOIN first_course_consumed fcc ON lcs.userId = fcc.userId
AND lcs.courseId = fcc.courseId
LEFT OUTER JOIN final_scores s ON lcs.userId = s.userId
AND lcs.courseId = s.courseId
LEFT OUTER JOIN public.courses c ON lcs.courseId = c.id
LEFT OUTER JOIN public.users u ON lcs.userId = u.userId
where u.identifier is not null
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
         17,
         18
ORDER BY 1,
         5,
         6,
         7,
         8 DESC
```

---

## Instamart Course Feedback Survey Response_Instamart Course Survey Report.sql

**Tables referenced:** analytics.nuggets_user_progress, courses, lesson_cards, lessons, nuggets, survey_cards, survey_definition, survey_questions, survey_responses, survey_sections, surveys.survey_responses, user_data, user_details

**Columns needing snake_case conversion:**

- `sectionID` -> `section_id` (alias: `section_id AS "sectionID"`)

- `userTags` -> `user_tags` (alias: `user_tags AS "userTags"`)


**Original Query:**

```sql
-- Data Source: Instamart Course Feedback Survey Response
-- Dashboard: Instamart Course Survey Report
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:59:30
-- ============================================================

WITH user_data AS
  (SELECT nup.nugget_id,
          nup.user_id,
          ud.first_name||' ' ||ud.last_name AS emp_name,
          ud.identifier AS emp_id,
   initcap(PROFILE -> 'userTags' -> 'role' -> 0 ->> 'value') AS role,
                                           initcap(PROFILE -> 'userTags' -> 'city' -> 0 ->> 'value') AS city,
                                                                               initcap(PROFILE -> 'userTags' -> 'store' -> 0 ->> 'value') AS store
   FROM analytics.nuggets_user_progress nup
   JOIN user_details ud ON nup.user_id = ud.uuid
   WHERE ud.organization = 'swiggy-mart-whirlpool'),
     survey_cards AS
  (SELECT lessons.course_id,
          lesson_cards.id AS card_id,
          lesson_cards.title AS survey_title,
          jsonb_object_keys(lesson_cards.payload -> 'sections') as section_id,
          lesson_cards.payload -> 'sections' as sections
   FROM lesson_cards
   JOIN lessons ON lesson_cards.lesson_id = lessons.id
   join courses on lessons.course_id = courses.id
   WHERE lesson_cards.type = 'survey'
     AND courses.organization = 'swiggy-mart-whirlpool'),
     survey_sections AS
  (SELECT sc.course_id,
          sc.card_id,
          sc.survey_title,
          sc.section_id,
          sc.sections -> sc.section_id -> 'questions' as question_list
   FROM survey_cards sc),
     survey_questions AS
  (SELECT survey_sections.course_id,
          survey_sections.card_id,
          survey_sections.survey_title,
          survey_sections.section_id,
          questions.value ->> 'text' AS question,
                              questions.ordinality - 1 AS question_id,
                              questions.value ->> 'type' AS question_type,
                                                  questions.value -> 'options' AS options_list
   FROM survey_sections,
        jsonb_array_elements(survey_sections.question_list) WITH
   ORDINALITY AS questions),
     survey_definition AS
  (SELECT survey_questions.course_id,
          survey_questions.card_id,
          survey_questions.survey_title,
          survey_questions.section_id,
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
          responses ->> 'sectionID' as section_id,
          responses ->> 'question' AS question_id,
                        responses ->> 'response' AS response_id
   FROM
     (SELECT *,
             jsonb_array_elements(response) AS responses
      FROM surveys.survey_responses
	  where created_at at time zone 'Asia/Kolkata' between @{{:Date Range.START}} and @{{:Date Range.END}}::timestamp + interval '1 day'
      ) base)
SELECT *
FROM
  (SELECT (survey_responses.created_at AT TIME ZONE 'Asia/Singapore')::date AS "Response Date",
          ud.emp_name AS "Employee Name",
          ud.emp_id AS "Employee ID",
   ud.role as "Role",
 ud. city as "City",
   ud.store as "Store",
          nuggets.title AS "Course Title",
          survey_definition.survey_title AS "Survey Title",
          survey_definition.question AS "Question",
          CASE
              WHEN survey_definition.question_type NOT IN ('rating',
                                                           'text',
                                                           'nps') THEN replace(survey_definition.option::varchar, '"', '')
              ELSE survey_responses.response_id
          END AS "Selected Option",
          survey_Definition.course_id AS "Course KNID",
          survey_definition.card_id AS "Card KNID",
          survey_responses.user_id AS "KNOW User ID"
   FROM survey_responses
   JOIN survey_definition ON survey_responses.course_id = survey_definition.course_id
   AND survey_responses.card_id = survey_definition.card_id
   and survey_responses.section_id = survey_definition.section_id
   AND survey_responses.question_id = survey_definition.question_id::varchar
   AND CASE
           WHEN survey_definition.question_type NOT IN ('rating',
                                                        'text',
                                                        'nps') THEN survey_responses.response_id = survey_definition.option_id::varchar
           ELSE survey_responses.question_id = survey_definition.question_id::varchar
       END
   JOIN user_data ud ON survey_responses.user_id = ud.user_id
   AND survey_responses.course_id = ud.nugget_id
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
         10, 11, 12, 13
		 order by 7, 1 desc, 3
```

---

## Instamart IMPACT Report_COM Compliance.sql

**Tables referenced:** base_forms, form_reminders, form_responses, form_submissions, forms, fr, fs, lfr, lm, location_form_reminders, locations, looker.locations_map_orange_mart, nuggets

**Original Query:**

```sql
-- Data Source: Instamart IMPACT Report
-- Dashboard: COM Compliance
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:57:39
-- ============================================================

WITH lm AS
  (select * from looker.locations_map_orange_mart),
				base_forms as (SELECT id,
       CASE
           WHEN title ~ '\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$' THEN regexp_replace(title,
																									  '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '')
           ELSE title
       END AS title
FROM nuggets
WHERE classification_type = 'form'
  AND organization = 'swiggy-mart-whirlpool'
  AND is_deleted = 'false'
  AND id IN ('-OC37vPYSTaYpa6rNk7y',
             '-OB4CVmT_YAytFR2fty7',
             '-OB4xcGu1NqT84w0lAWQ',
             '-O9U1GGkwZWt_Vs6okDW',
             '-OB4z2473dKeZ34McBIV',
             '-OB4zWin85ZrjPUjH0RV',
             '-OB4zm7TVqXaKK3J0vAX',
             '-OB5-5PzkC26eek0Bk-1',
             '-OB5-Q1oguPmrJlRlBnH',
             '-OBPR5RTpUGaHJsVJFZH',
             '-OB5-kLCkZWwy65-Ek6h',
             '-OB505iZAJ8wJ0zZxcFM',
             '-OB525WEclHOXV6JYtJn',
             '-OB51wGxzBWxhStUNtqv',
             '-OB52IvLT3rJTvAM7wLT',
             '-OB52TuE5WfUdYkJdmrE',
             '-OB52jx59NEjUjPBixqy',
             '-OB52ttmR2iTHizVPXwE',
             '-OB55VCsN1K47jdOc-N2',
             '-OB5622pYYZHwe2fCC1W',
             '-OB56cNfUDEhTxUPhJ4S',
             '-OB56mQetguLSxb-mTv6',
             '-OB57bk-9BG-rX7wAceu',
             '-OAIJndZxwVht8750Zc6',
             '-OAIsM27j29lvnM9Br5O',
             '-OAIx7irPIBo-9cKLh_y',
             '-OALkeIDkVHTQtxyEVne',
             '-OAvN4-5jv-XvXPhQEeM',
             '-OAvPLR9pQLC_wvRpX0Y',
             '-OAvQgdymG5aSTHcrVQR',
             '-OAvVUTteJqBgqdYYJgq',
             '-OAvVhmAOQCKn9Ln_JC-',
             '-OAvVvs7yNtCfVItyUr4',
             '-OAvWIJh_dc1cSU8uJgq',
             '-OAvWV2dPw9S0L6KWBlb',
             '-OAvb8LGJYxjlH_YrSRb',
             '-OAvWvojjYv0Cxl9uTai',
             '-OBAL68W_bLx6qrgfVjm',
             '-OB0_uO6Q4lBeasMViQT',
             '-OB56yx-t8HP7oBY0JQX',
             '-OB0_OEwgHSkOq9KOr7P',
             '-OBZLlW2pRYqtVoLwUJq',
             '-OBdNIXxFdIQrGnbqESi',
             '-OBdNs7lzEaEIhrrlwHk',
             '-OC351d72Tg3nF69kF0Z',
             '-O5vnwzkiszWtqSl6QGF',
             '-O73HoSK3DHguZxXg_q0')),
			 forms as (select id from nuggets where regexp_replace(title,
																									  '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '') in (select title from base_forms)
					   and classification_type = 'form'
					   and is_deleted = 'false'),
					   
     lfr AS
  (SELECT lfr.reminder_id,
          fr.organization,
          fr.tz_offset AS tz_offset_sec,
          fr.form_id,
          l.location_name AS LOCATION,
          (to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset)::date AS reminded_date,
          row_number() OVER (PARTITION BY fr.form_id,
                                          l.location_name,
                                          (to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset)::date
                             ORDER BY to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset) AS reminder_no,
                            to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset AS reminded_at,
                                                                          to_timestamp(lfr.reminder_window_end/1000) + interval '1 sec'*fr.tz_offset AS reminder_window_end,
                                                                                                                                lfr.form_response_id,
                                                                                                                                CASE
                                                                                                                                    WHEN responded_at = 0 THEN NULL
                                                                                                                                    ELSE to_timestamp(lfr.responded_at/1000) + interval '1 sec'*fr.tz_offset
                                                                                                                                END AS responded_at
   FROM location_form_reminders lfr
   JOIN form_reminders fr ON fr.id = lfr.reminder_id
   JOIN locations l ON lfr.location_id = l.id
   WHERE to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset between @{{:Date Range.START}}::timestamp
   and @{{:Date Range.END}}::timestamp
   and to_timestamp(lfr.reminded_at/1000) >= '2024-12-05'::timestamp at time zone 'Asia/Kolkata'
     AND fr.form_id IN (select id from forms)
      and l.is_active = true
      and l.organization = 'swiggy-mart-whirlpool'
  AND regexp_replace(l.location_name, '([0-9]+).*', '\1') in (select pod_id from lm)),
     fs AS
  (SELECT fs.*
   FROM form_submissions fs
   WHERE fs.location NOT ILIKE 'KNOW'
     AND fs.location NOT ILIKE 'HQ'
     AND fs.location NOT ILIKE '%HO'
     AND fs.submit_date AT TIME ZONE 'Asia/Kolkata' between @{{:Date Range.START}}::timestamp
   and @{{:Date Range.END}}::timestamp
     and fs.submit_date >= '2024-12-05'::timestamp at time zone 'Asia/Kolkata'
     AND fs.form_id IN (select id from forms)),
     fr AS
  (SELECT fs.form_id,
          fs.submit_date,
          fs.response_id,
          fr.response->>'name' AS LOCATION,
                        row_number() OVER (PARTITION BY fs.form_id,
                                                        (fs.submit_date AT TIME ZONE 'Asia/Kolkata')::date,
                                                        fr.response->>'name'
                                           ORDER BY fs.submit_date) AS submission_no
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   WHERE fr.question_type = 'location'
  AND regexp_replace(fr.response->>'name', '([0-9]+).*', '\1') in (select pod_id from lm))
SELECT lfr.organization AS "Organization",
       lm.cluster AS "Cluster",
       lm.city AS "City",
       coalesce(lm.pod_id, regexp_replace(lfr."location", '([0-9]+).*', '\1')) AS "Pod ID",
       lm.pod_name AS "Pod Name",
       lm.com AS "COM",
       lm.dch AS "DCH",
       (lfr.reminded_at)::date AS "Date",
       lfr.form_id AS "Routine KNID",
       n.title AS "Routine Name",
       lfr.reminded_at AS "Reminded At",
       CASE
           WHEN (lfr.reminded_at)::TIME BETWEEN '06:00:01' AND '12:00:01' THEN '1 - Morning'
           WHEN (lfr.reminded_at)::TIME BETWEEN '12:00:01' AND '20:00:01' THEN '2 - Afternoon'
           ELSE '3 - Night'
       END AS "Shift",
       CASE
           WHEN lfr.form_response_id IS NOT NULL THEN 'Compliant'
           WHEN fr.response_id IS NULL THEN 'Missed'
           ELSE 'Done Late'
       END AS "Status",
       CASE
           WHEN lfr.form_response_id IS NOT NULL THEN 1
           WHEN fr.response_id IS NULL THEN 0
           ELSE 0.5
       END AS "Compliance Score",
       CASE
           WHEN coalesce(lfr.form_response_id, fr.response_id) IS NULL THEN 0.0
           ELSE 1.0
       END AS "Completion Score",
       coalesce(lfr.form_response_id, fr.response_id) AS "Submission KNID"
FROM lfr
JOIN nuggets n ON lfr.form_id = n.id
LEFT OUTER JOIN fr ON fr.form_id = lfr.form_id
AND (fr.submit_date + interval '1 sec'*lfr.tz_offset_Sec)::date = (lfr.reminded_at)::date
AND fr.location = lfr.location
AND fr.submission_no = lfr.reminder_no
LEFT OUTER JOIN lm ON regexp_replace(lfr."location", '([0-9]+).*', '\1') = lm.pod_id
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
         16
ORDER BY 11 desc,
         10,
         1,
         2,
         3,
         4
```

---

## Instamart IMPACT Report_DCH Compliance.sql

**Tables referenced:** base_forms, form_reminders, form_responses, form_submissions, forms, fr, fs, lfr, lm, location_form_reminders, locations, looker.locations_map_orange_mart, nuggets

**Original Query:**

```sql
-- Data Source: Instamart IMPACT Report
-- Dashboard: DCH Compliance
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:57:39
-- ============================================================

WITH lm AS
  (select * from looker.locations_map_orange_mart),
				base_forms as (SELECT id,
       CASE
           WHEN title ~ '\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$' THEN regexp_replace(title,
																									  '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '')
           ELSE title
       END AS title
FROM nuggets
WHERE classification_type = 'form'
  AND organization = 'swiggy-mart-whirlpool'
  AND is_deleted = 'false'
  AND id IN ('-OC37vPYSTaYpa6rNk7y',
             '-OB4CVmT_YAytFR2fty7',
             '-OB4xcGu1NqT84w0lAWQ',
             '-O9U1GGkwZWt_Vs6okDW',
             '-OB4z2473dKeZ34McBIV',
             '-OB4zWin85ZrjPUjH0RV',
             '-OB4zm7TVqXaKK3J0vAX',
             '-OB5-5PzkC26eek0Bk-1',
             '-OB5-Q1oguPmrJlRlBnH',
             '-OBPR5RTpUGaHJsVJFZH',
             '-OB5-kLCkZWwy65-Ek6h',
             '-OB505iZAJ8wJ0zZxcFM',
             '-OB525WEclHOXV6JYtJn',
             '-OB51wGxzBWxhStUNtqv',
             '-OB52IvLT3rJTvAM7wLT',
             '-OB52TuE5WfUdYkJdmrE',
             '-OB52jx59NEjUjPBixqy',
             '-OB52ttmR2iTHizVPXwE',
             '-OB55VCsN1K47jdOc-N2',
             '-OB5622pYYZHwe2fCC1W',
             '-OB56cNfUDEhTxUPhJ4S',
             '-OB56mQetguLSxb-mTv6',
             '-OB57bk-9BG-rX7wAceu',
             '-OAIJndZxwVht8750Zc6',
             '-OAIsM27j29lvnM9Br5O',
             '-OAIx7irPIBo-9cKLh_y',
             '-OALkeIDkVHTQtxyEVne',
             '-OAvN4-5jv-XvXPhQEeM',
             '-OAvPLR9pQLC_wvRpX0Y',
             '-OAvQgdymG5aSTHcrVQR',
             '-OAvVUTteJqBgqdYYJgq',
             '-OAvVhmAOQCKn9Ln_JC-',
             '-OAvVvs7yNtCfVItyUr4',
             '-OAvWIJh_dc1cSU8uJgq',
             '-OAvWV2dPw9S0L6KWBlb',
             '-OAvb8LGJYxjlH_YrSRb',
             '-OAvWvojjYv0Cxl9uTai',
             '-OBAL68W_bLx6qrgfVjm',
             '-OB0_uO6Q4lBeasMViQT',
             '-OB56yx-t8HP7oBY0JQX',
             '-OB0_OEwgHSkOq9KOr7P',
             '-OBZLlW2pRYqtVoLwUJq',
             '-OBdNIXxFdIQrGnbqESi',
             '-OBdNs7lzEaEIhrrlwHk',
             '-OC351d72Tg3nF69kF0Z',
             '-O5vnwzkiszWtqSl6QGF',
             '-O73HoSK3DHguZxXg_q0')),
			 forms as (select id from nuggets where regexp_replace(title,
																									  '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '') in (select title from base_forms)
					   and classification_type = 'form'
					   and is_deleted = 'false'),
					   
     lfr AS
  (SELECT lfr.reminder_id,
          fr.organization,
          fr.tz_offset AS tz_offset_sec,
          fr.form_id,
          l.location_name AS LOCATION,
          (to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset)::date AS reminded_date,
          row_number() OVER (PARTITION BY fr.form_id,
                                          l.location_name,
                                          (to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset)::date
                             ORDER BY to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset) AS reminder_no,
                            to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset AS reminded_at,
                                                                          to_timestamp(lfr.reminder_window_end/1000) + interval '1 sec'*fr.tz_offset AS reminder_window_end,
                                                                                                                                lfr.form_response_id,
                                                                                                                                CASE
                                                                                                                                    WHEN responded_at = 0 THEN NULL
                                                                                                                                    ELSE to_timestamp(lfr.responded_at/1000) + interval '1 sec'*fr.tz_offset
                                                                                                                                END AS responded_at
   FROM location_form_reminders lfr
   JOIN form_reminders fr ON fr.id = lfr.reminder_id
   JOIN locations l ON lfr.location_id = l.id
   WHERE to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset between @{{:Date Range.START}}::timestamp
   and @{{:Date Range.END}}::timestamp
   and to_timestamp(lfr.reminded_at/1000) >= '2024-12-05'::timestamp at time zone 'Asia/Kolkata'
     AND fr.form_id IN (select id from forms)
      and l.is_active = true
      and l.organization = 'swiggy-mart-whirlpool'
  AND regexp_replace(l.location_name, '([0-9]+).*', '\1') in (select pod_id from lm)),
     fs AS
  (SELECT fs.*
   FROM form_submissions fs
   WHERE fs.location NOT ILIKE 'KNOW'
     AND fs.location NOT ILIKE 'HQ'
     AND fs.location NOT ILIKE '%HO'
     AND fs.submit_date AT TIME ZONE 'Asia/Kolkata' between @{{:Date Range.START}}::timestamp
   and @{{:Date Range.END}}::timestamp
     and fs.submit_date >= '2024-12-05'::timestamp at time zone 'Asia/Kolkata'
     AND fs.form_id IN (select id from forms)),
     fr AS
  (SELECT fs.form_id,
          fs.submit_date,
          fs.response_id,
          fr.response->>'name' AS LOCATION,
                        row_number() OVER (PARTITION BY fs.form_id,
                                                        (fs.submit_date AT TIME ZONE 'Asia/Kolkata')::date,
                                                        fr.response->>'name'
                                           ORDER BY fs.submit_date) AS submission_no
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   WHERE fr.question_type = 'location'
  AND regexp_replace(fr.response->>'name', '([0-9]+).*', '\1') in (select pod_id from lm))
SELECT lfr.organization AS "Organization",
       lm.cluster AS "Cluster",
       lm.city AS "City",
       coalesce(lm.pod_id, regexp_replace(lfr."location", '([0-9]+).*', '\1')) AS "Pod ID",
       lm.pod_name AS "Pod Name",
       lm.com AS "COM",
       lm.dch AS "DCH",
       (lfr.reminded_at)::date AS "Date",
       lfr.form_id AS "Routine KNID",
       n.title AS "Routine Name",
       lfr.reminded_at AS "Reminded At",
       CASE
           WHEN (lfr.reminded_at)::TIME BETWEEN '06:00:01' AND '12:00:01' THEN '1 - Morning'
           WHEN (lfr.reminded_at)::TIME BETWEEN '12:00:01' AND '20:00:01' THEN '2 - Afternoon'
           ELSE '3 - Night'
       END AS "Shift",
       CASE
           WHEN lfr.form_response_id IS NOT NULL THEN 'Compliant'
           WHEN fr.response_id IS NULL THEN 'Missed'
           ELSE 'Done Late'
       END AS "Status",
       CASE
           WHEN lfr.form_response_id IS NOT NULL THEN 1
           WHEN fr.response_id IS NULL THEN 0
           ELSE 0.5
       END AS "Compliance Score",
       CASE
           WHEN coalesce(lfr.form_response_id, fr.response_id) IS NULL THEN 0.0
           ELSE 1.0
       END AS "Completion Score",
       coalesce(lfr.form_response_id, fr.response_id) AS "Submission KNID"
FROM lfr
JOIN nuggets n ON lfr.form_id = n.id
LEFT OUTER JOIN fr ON fr.form_id = lfr.form_id
AND (fr.submit_date + interval '1 sec'*lfr.tz_offset_Sec)::date = (lfr.reminded_at)::date
AND fr.location = lfr.location
AND fr.submission_no = lfr.reminder_no
LEFT OUTER JOIN lm ON regexp_replace(lfr."location", '([0-9]+).*', '\1') = lm.pod_id
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
         16
ORDER BY 11 desc,
         10,
         1,
         2,
         3,
         4
```

---

## Instamart IMPACT Report_P7D Routine Compliance.sql

**Tables referenced:** base_forms, form_reminders, form_responses, form_submissions, forms, fr, fs, lfr, lm, location_form_reminders, locations, looker.locations_map_orange_mart, nuggets

**Original Query:**

```sql
-- Data Source: Instamart IMPACT Report
-- Dashboard: P7D Routine Compliance
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:57:39
-- ============================================================

WITH lm AS
  (select * from looker.locations_map_orange_mart),
				base_forms as (SELECT id,
       CASE
           WHEN title ~ '\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$' THEN regexp_replace(title,
																									  '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '')
           ELSE title
       END AS title
FROM nuggets
WHERE classification_type = 'form'
  AND organization = 'swiggy-mart-whirlpool'
  AND is_deleted = 'false'
  AND id IN ('-OC37vPYSTaYpa6rNk7y',
             '-OB4CVmT_YAytFR2fty7',
             '-OB4xcGu1NqT84w0lAWQ',
             '-O9U1GGkwZWt_Vs6okDW',
             '-OB4z2473dKeZ34McBIV',
             '-OB4zWin85ZrjPUjH0RV',
             '-OB4zm7TVqXaKK3J0vAX',
             '-OB5-5PzkC26eek0Bk-1',
             '-OB5-Q1oguPmrJlRlBnH',
             '-OBPR5RTpUGaHJsVJFZH',
             '-OB5-kLCkZWwy65-Ek6h',
             '-OB505iZAJ8wJ0zZxcFM',
             '-OB525WEclHOXV6JYtJn',
             '-OB51wGxzBWxhStUNtqv',
             '-OB52IvLT3rJTvAM7wLT',
             '-OB52TuE5WfUdYkJdmrE',
             '-OB52jx59NEjUjPBixqy',
             '-OB52ttmR2iTHizVPXwE',
             '-OB55VCsN1K47jdOc-N2',
             '-OB5622pYYZHwe2fCC1W',
             '-OB56cNfUDEhTxUPhJ4S',
             '-OB56mQetguLSxb-mTv6',
             '-OB57bk-9BG-rX7wAceu',
             '-OAIJndZxwVht8750Zc6',
             '-OAIsM27j29lvnM9Br5O',
             '-OAIx7irPIBo-9cKLh_y',
             '-OALkeIDkVHTQtxyEVne',
             '-OAvN4-5jv-XvXPhQEeM',
             '-OAvPLR9pQLC_wvRpX0Y',
             '-OAvQgdymG5aSTHcrVQR',
             '-OAvVUTteJqBgqdYYJgq',
             '-OAvVhmAOQCKn9Ln_JC-',
             '-OAvVvs7yNtCfVItyUr4',
             '-OAvWIJh_dc1cSU8uJgq',
             '-OAvWV2dPw9S0L6KWBlb',
             '-OAvb8LGJYxjlH_YrSRb',
             '-OAvWvojjYv0Cxl9uTai',
             '-OBAL68W_bLx6qrgfVjm',
             '-OB0_uO6Q4lBeasMViQT',
             '-OB56yx-t8HP7oBY0JQX',
             '-OB0_OEwgHSkOq9KOr7P',
             '-OBZLlW2pRYqtVoLwUJq',
             '-OBdNIXxFdIQrGnbqESi',
             '-OBdNs7lzEaEIhrrlwHk',
             '-OC351d72Tg3nF69kF0Z',
             '-O5vnwzkiszWtqSl6QGF',
             '-O73HoSK3DHguZxXg_q0')),
			 forms as (select id from nuggets where regexp_replace(title,
																									  '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '') in (select title from base_forms)
					   and classification_type = 'form'
					   and is_deleted = 'false'),
					   
     lfr AS
  (SELECT lfr.reminder_id,
          fr.organization,
          fr.tz_offset AS tz_offset_sec,
          fr.form_id,
          l.location_name AS LOCATION,
          (to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset)::date AS reminded_date,
          row_number() OVER (PARTITION BY fr.form_id,
                                          l.location_name,
                                          (to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset)::date
                             ORDER BY to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset) AS reminder_no,
                            to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset AS reminded_at,
                                                                          to_timestamp(lfr.reminder_window_end/1000) + interval '1 sec'*fr.tz_offset AS reminder_window_end,
                                                                                                                                lfr.form_response_id,
                                                                                                                                CASE
                                                                                                                                    WHEN responded_at = 0 THEN NULL
                                                                                                                                    ELSE to_timestamp(lfr.responded_at/1000) + interval '1 sec'*fr.tz_offset
                                                                                                                                END AS responded_at
   FROM location_form_reminders lfr
   JOIN form_reminders fr ON fr.id = lfr.reminder_id
   JOIN locations l ON lfr.location_id = l.id
   WHERE to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset between @{{:Date Range.START}}::timestamp
   and @{{:Date Range.END}}::timestamp
   and to_timestamp(lfr.reminded_at/1000) >= '2024-12-05'::timestamp at time zone 'Asia/Kolkata'
     AND fr.form_id IN (select id from forms)
      and l.is_active = true
      and l.organization = 'swiggy-mart-whirlpool'
  AND regexp_replace(l.location_name, '([0-9]+).*', '\1') in (select pod_id from lm)),
     fs AS
  (SELECT fs.*
   FROM form_submissions fs
   WHERE fs.location NOT ILIKE 'KNOW'
     AND fs.location NOT ILIKE 'HQ'
     AND fs.location NOT ILIKE '%HO'
     AND fs.submit_date AT TIME ZONE 'Asia/Kolkata' between @{{:Date Range.START}}::timestamp
   and @{{:Date Range.END}}::timestamp
     and fs.submit_date >= '2024-12-05'::timestamp at time zone 'Asia/Kolkata'
     AND fs.form_id IN (select id from forms)),
     fr AS
  (SELECT fs.form_id,
          fs.submit_date,
          fs.response_id,
          fr.response->>'name' AS LOCATION,
                        row_number() OVER (PARTITION BY fs.form_id,
                                                        (fs.submit_date AT TIME ZONE 'Asia/Kolkata')::date,
                                                        fr.response->>'name'
                                           ORDER BY fs.submit_date) AS submission_no
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   WHERE fr.question_type = 'location'
  AND regexp_replace(fr.response->>'name', '([0-9]+).*', '\1') in (select pod_id from lm))
SELECT lfr.organization AS "Organization",
       lm.cluster AS "Cluster",
       lm.city AS "City",
       coalesce(lm.pod_id, regexp_replace(lfr."location", '([0-9]+).*', '\1')) AS "Pod ID",
       lm.pod_name AS "Pod Name",
       lm.com AS "COM",
       lm.dch AS "DCH",
       (lfr.reminded_at)::date AS "Date",
       lfr.form_id AS "Routine KNID",
       n.title AS "Routine Name",
       lfr.reminded_at AS "Reminded At",
       CASE
           WHEN (lfr.reminded_at)::TIME BETWEEN '06:00:01' AND '12:00:01' THEN '1 - Morning'
           WHEN (lfr.reminded_at)::TIME BETWEEN '12:00:01' AND '20:00:01' THEN '2 - Afternoon'
           ELSE '3 - Night'
       END AS "Shift",
       CASE
           WHEN lfr.form_response_id IS NOT NULL THEN 'Compliant'
           WHEN fr.response_id IS NULL THEN 'Missed'
           ELSE 'Done Late'
       END AS "Status",
       CASE
           WHEN lfr.form_response_id IS NOT NULL THEN 1
           WHEN fr.response_id IS NULL THEN 0
           ELSE 0.5
       END AS "Compliance Score",
       CASE
           WHEN coalesce(lfr.form_response_id, fr.response_id) IS NULL THEN 0.0
           ELSE 1.0
       END AS "Completion Score",
       coalesce(lfr.form_response_id, fr.response_id) AS "Submission KNID"
FROM lfr
JOIN nuggets n ON lfr.form_id = n.id
LEFT OUTER JOIN fr ON fr.form_id = lfr.form_id
AND (fr.submit_date + interval '1 sec'*lfr.tz_offset_Sec)::date = (lfr.reminded_at)::date
AND fr.location = lfr.location
AND fr.submission_no = lfr.reminder_no
LEFT OUTER JOIN lm ON regexp_replace(lfr."location", '([0-9]+).*', '\1') = lm.pod_id
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
         16
ORDER BY 11 desc,
         10,
         1,
         2,
         3,
         4
```

---

## Instamart IMPACT Report_Pod Compliance.sql

**Tables referenced:** base_forms, form_reminders, form_responses, form_submissions, forms, fr, fs, lfr, lm, location_form_reminders, locations, looker.locations_map_orange_mart, nuggets

**Original Query:**

```sql
-- Data Source: Instamart IMPACT Report
-- Dashboard: Pod Compliance
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:57:39
-- ============================================================

WITH lm AS
  (select * from looker.locations_map_orange_mart),
				base_forms as (SELECT id,
       CASE
           WHEN title ~ '\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$' THEN regexp_replace(title,
																									  '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '')
           ELSE title
       END AS title
FROM nuggets
WHERE classification_type = 'form'
  AND organization = 'swiggy-mart-whirlpool'
  AND is_deleted = 'false'
  AND id IN ('-OC37vPYSTaYpa6rNk7y',
             '-OB4CVmT_YAytFR2fty7',
             '-OB4xcGu1NqT84w0lAWQ',
             '-O9U1GGkwZWt_Vs6okDW',
             '-OB4z2473dKeZ34McBIV',
             '-OB4zWin85ZrjPUjH0RV',
             '-OB4zm7TVqXaKK3J0vAX',
             '-OB5-5PzkC26eek0Bk-1',
             '-OB5-Q1oguPmrJlRlBnH',
             '-OBPR5RTpUGaHJsVJFZH',
             '-OB5-kLCkZWwy65-Ek6h',
             '-OB505iZAJ8wJ0zZxcFM',
             '-OB525WEclHOXV6JYtJn',
             '-OB51wGxzBWxhStUNtqv',
             '-OB52IvLT3rJTvAM7wLT',
             '-OB52TuE5WfUdYkJdmrE',
             '-OB52jx59NEjUjPBixqy',
             '-OB52ttmR2iTHizVPXwE',
             '-OB55VCsN1K47jdOc-N2',
             '-OB5622pYYZHwe2fCC1W',
             '-OB56cNfUDEhTxUPhJ4S',
             '-OB56mQetguLSxb-mTv6',
             '-OB57bk-9BG-rX7wAceu',
             '-OAIJndZxwVht8750Zc6',
             '-OAIsM27j29lvnM9Br5O',
             '-OAIx7irPIBo-9cKLh_y',
             '-OALkeIDkVHTQtxyEVne',
             '-OAvN4-5jv-XvXPhQEeM',
             '-OAvPLR9pQLC_wvRpX0Y',
             '-OAvQgdymG5aSTHcrVQR',
             '-OAvVUTteJqBgqdYYJgq',
             '-OAvVhmAOQCKn9Ln_JC-',
             '-OAvVvs7yNtCfVItyUr4',
             '-OAvWIJh_dc1cSU8uJgq',
             '-OAvWV2dPw9S0L6KWBlb',
             '-OAvb8LGJYxjlH_YrSRb',
             '-OAvWvojjYv0Cxl9uTai',
             '-OBAL68W_bLx6qrgfVjm',
             '-OB0_uO6Q4lBeasMViQT',
             '-OB56yx-t8HP7oBY0JQX',
             '-OB0_OEwgHSkOq9KOr7P',
             '-OBZLlW2pRYqtVoLwUJq',
             '-OBdNIXxFdIQrGnbqESi',
             '-OBdNs7lzEaEIhrrlwHk',
             '-OC351d72Tg3nF69kF0Z',
             '-O5vnwzkiszWtqSl6QGF',
             '-O73HoSK3DHguZxXg_q0')),
			 forms as (select id from nuggets where regexp_replace(title,
																									  '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '') in (select title from base_forms)
					   and classification_type = 'form'
					   and is_deleted = 'false'),
					   
     lfr AS
  (SELECT lfr.reminder_id,
          fr.organization,
          fr.tz_offset AS tz_offset_sec,
          fr.form_id,
          l.location_name AS LOCATION,
          (to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset)::date AS reminded_date,
          row_number() OVER (PARTITION BY fr.form_id,
                                          l.location_name,
                                          (to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset)::date
                             ORDER BY to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset) AS reminder_no,
                            to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset AS reminded_at,
                                                                          to_timestamp(lfr.reminder_window_end/1000) + interval '1 sec'*fr.tz_offset AS reminder_window_end,
                                                                                                                                lfr.form_response_id,
                                                                                                                                CASE
                                                                                                                                    WHEN responded_at = 0 THEN NULL
                                                                                                                                    ELSE to_timestamp(lfr.responded_at/1000) + interval '1 sec'*fr.tz_offset
                                                                                                                                END AS responded_at
   FROM location_form_reminders lfr
   JOIN form_reminders fr ON fr.id = lfr.reminder_id
   JOIN locations l ON lfr.location_id = l.id
   WHERE to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset between @{{:Date Range.START}}::timestamp
   and @{{:Date Range.END}}::timestamp
   and to_timestamp(lfr.reminded_at/1000) >= '2024-12-05'::timestamp at time zone 'Asia/Kolkata'
     AND fr.form_id IN (select id from forms)
      and l.is_active = true
      and l.organization = 'swiggy-mart-whirlpool'
  AND regexp_replace(l.location_name, '([0-9]+).*', '\1') in (select pod_id from lm)),
     fs AS
  (SELECT fs.*
   FROM form_submissions fs
   WHERE fs.location NOT ILIKE 'KNOW'
     AND fs.location NOT ILIKE 'HQ'
     AND fs.location NOT ILIKE '%HO'
     AND fs.submit_date AT TIME ZONE 'Asia/Kolkata' between @{{:Date Range.START}}::timestamp
   and @{{:Date Range.END}}::timestamp
     and fs.submit_date >= '2024-12-05'::timestamp at time zone 'Asia/Kolkata'
     AND fs.form_id IN (select id from forms)),
     fr AS
  (SELECT fs.form_id,
          fs.submit_date,
          fs.response_id,
          fr.response->>'name' AS LOCATION,
                        row_number() OVER (PARTITION BY fs.form_id,
                                                        (fs.submit_date AT TIME ZONE 'Asia/Kolkata')::date,
                                                        fr.response->>'name'
                                           ORDER BY fs.submit_date) AS submission_no
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   WHERE fr.question_type = 'location'
  AND regexp_replace(fr.response->>'name', '([0-9]+).*', '\1') in (select pod_id from lm))
SELECT lfr.organization AS "Organization",
       lm.cluster AS "Cluster",
       lm.city AS "City",
       coalesce(lm.pod_id, regexp_replace(lfr."location", '([0-9]+).*', '\1')) AS "Pod ID",
       lm.pod_name AS "Pod Name",
       lm.com AS "COM",
       lm.dch AS "DCH",
       (lfr.reminded_at)::date AS "Date",
       lfr.form_id AS "Routine KNID",
       n.title AS "Routine Name",
       lfr.reminded_at AS "Reminded At",
       CASE
           WHEN (lfr.reminded_at)::TIME BETWEEN '06:00:01' AND '12:00:01' THEN '1 - Morning'
           WHEN (lfr.reminded_at)::TIME BETWEEN '12:00:01' AND '20:00:01' THEN '2 - Afternoon'
           ELSE '3 - Night'
       END AS "Shift",
       CASE
           WHEN lfr.form_response_id IS NOT NULL THEN 'Compliant'
           WHEN fr.response_id IS NULL THEN 'Missed'
           ELSE 'Done Late'
       END AS "Status",
       CASE
           WHEN lfr.form_response_id IS NOT NULL THEN 1
           WHEN fr.response_id IS NULL THEN 0
           ELSE 0.5
       END AS "Compliance Score",
       CASE
           WHEN coalesce(lfr.form_response_id, fr.response_id) IS NULL THEN 0.0
           ELSE 1.0
       END AS "Completion Score",
       coalesce(lfr.form_response_id, fr.response_id) AS "Submission KNID"
FROM lfr
JOIN nuggets n ON lfr.form_id = n.id
LEFT OUTER JOIN fr ON fr.form_id = lfr.form_id
AND (fr.submit_date + interval '1 sec'*lfr.tz_offset_Sec)::date = (lfr.reminded_at)::date
AND fr.location = lfr.location
AND fr.submission_no = lfr.reminder_no
LEFT OUTER JOIN lm ON regexp_replace(lfr."location", '([0-9]+).*', '\1') = lm.pod_id
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
         16
ORDER BY 11 desc,
         10,
         1,
         2,
         3,
         4
```

---

## Instamart Impact Daily Misses_IMPACT Daily Misses Report.sql

**Tables referenced:** ROLES, acl, active_locations_pods, base, base_forms, filtered_lfr, form_responses, form_submissions, forms, fr, fs, lfr, lm, locations, lr, public.form_reminders, public.location_form_reminders, public.locations, public.nuggets, role_holders, user_details

**Original Query:**

```sql
-- Data Source: Instamart Impact Daily Misses
-- Dashboard: IMPACT Daily Misses Report
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:56:54
-- ============================================================

WITH acl AS
  (select regexp_replace(l.location_name, '([0-9]+).*', '\1') AS store_id 
from locations l 
where organization = 'swiggy-mart-whirlpool'
and is_active = true),
     lr AS
  (SELECT acl.store_id,
          l.location_name AS store_name,
          r.name AS ROLE,
          ud.uuid AS holder_id,
          ud.first_name||' '||ud.last_name AS holder
   FROM acl
   JOIN locations l ON acl.store_id = regexp_replace(l.location_name, '([0-9]+).*', '\1')
   left JOIN role_holders rh ON l.id = rh.location_id and rh.is_active = true
   left JOIN ROLES r ON r.id = rh.role_id AND r.name IN ('Cluster Ops Manager',
                    'Deputy City Head')
   LEFT OUTER JOIN user_details ud ON rh.role_holder_id = ud.uuid
   WHERE l.organization = 'swiggy-mart-whirlpool'
     AND l.is_active = 'true'
     AND ud.is_active = 'true'
     AND r.name IN ('Cluster Ops Manager',
                    'Deputy City Head')
   ORDER BY 1,
            2),
     lm AS
  (SELECT lr.store_id AS pod_id,
          lr.store_name AS pod_name,
          ud.division AS CLUSTER,
          ud.sub_division AS city,
          max(CASE
                  WHEN ROLE = 'Cluster Ops Manager' THEN holder
                  ELSE NULL
              END) AS com,
          max(CASE
                  WHEN ROLE = 'Cluster Ops Manager' THEN holder_id
                  ELSE NULL
              END) AS com_knid,
          max(CASE
                  WHEN ROLE = 'Deputy City Head' THEN holder
                  ELSE NULL
              END) AS dch,
          max(CASE
                  WHEN ROLE ='Deputy City Head' THEN holder_id
                  ELSE NULL
              END) AS dch_knid
   FROM lr
   JOIN
     (SELECT DISTINCT ON (job_location) job_location,
                         division,
                         sub_division
      FROM user_details
      WHERE regexp_replace(job_location, '([0-9]+).*', '\1') IS NOT NULL
	  AND division is not null
      ORDER BY job_location,
               created_at DESC) ud ON lr.store_name = ud.job_location
   GROUP BY 1,
            2,
            3,
            4
   ORDER BY 1),
     active_locations_pods AS
  ( SELECT id,
           location_name
   FROM public.locations l
   WHERE l.organization = 'swiggy-mart-whirlpool'
     AND l.is_active = TRUE
     AND regexp_replace(l.location_name, '([0-9]+).*', '\1') IN
       (SELECT pod_id
        FROM lm) ),
     base_forms AS
  ( SELECT id,
           regexp_replace(title, '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '') AS title
   FROM public.nuggets
   WHERE is_deleted = FALSE
     AND id IN ( '-OC37vPYSTaYpa6rNk7y',
                 '-OB4CVmT_YAytFR2fty7',
                 '-OB4xcGu1NqT84w0lAWQ',
                 '-O9U1GGkwZWt_Vs6okDW',
                 '-OB4z2473dKeZ34McBIV',
                 '-OB4zWin85ZrjPUjH0RV',
                 '-OB4zm7TVqXaKK3J0vAX',
                 '-OB5-5PzkC26eek0Bk-1',
                 '-OB5-Q1oguPmrJlRlBnH',
                 '-OBPR5RTpUGaHJsVJFZH',
                 '-OB5-kLCkZWwy65-Ek6h',
                 '-OB505iZAJ8wJ0zZxcFM',
                 '-OB525WEclHOXV6JYtJn',
                 '-OB51wGxzBWxhStUNtqv',
                 '-OB52IvLT3rJTvAM7wLT',
                 '-OB52TuE5WfUdYkJdmrE',
                 '-OB52jx59NEjUjPBixqy',
                 '-OB52ttmR2iTHizVPXwE',
                 '-OB55VCsN1K47jdOc-N2',
                 '-OB5622pYYZHwe2fCC1W',
                 '-OB56cNfUDEhTxUPhJ4S',
                 '-OB56mQetguLSxb-mTv6',
                 '-OB57bk-9BG-rX7wAceu',
                 '-OAIJndZxwVht8750Zc6',
                 '-OAIsM27j29lvnM9Br5O',
                 '-OAIx7irPIBo-9cKLh_y',
                 '-OALkeIDkVHTQtxyEVne',
                 '-OAvN4-5jv-XvXPhQEeM',
                 '-OAvPLR9pQLC_wvRpX0Y',
                 '-OAvQgdymG5aSTHcrVQR',
                 '-OAvVUTteJqBgqdYYJgq',
                 '-OAvVhmAOQCKn9Ln_JC-',
                 '-OAvVvs7yNtCfVItyUr4',
                 '-OAvWIJh_dc1cSU8uJgq',
                 '-OAvWV2dPw9S0L6KWBlb',
                 '-OAvb8LGJYxjlH_YrSRb',
                 '-OAvWvojjYv0Cxl9uTai',
                 '-OBAL68W_bLx6qrgfVjm',
                 '-OB0_uO6Q4lBeasMViQT',
                 '-OB56yx-t8HP7oBY0JQX',
                 '-OB0_OEwgHSkOq9KOr7P',
                 '-OBZLlW2pRYqtVoLwUJq',
                 '-OBdNIXxFdIQrGnbqESi',
                 '-OBdNs7lzEaEIhrrlwHk',
                 '-OC351d72Tg3nF69kF0Z',
                 '-O5vnwzkiszWtqSl6QGF',
                 '-O73HoSK3DHguZxXg_q0' ) ),
     forms AS
  ( SELECT n.id,
           bf.title
   FROM public.nuggets n
   JOIN base_forms bf ON bf.title = regexp_replace(n.title, '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '')
   WHERE n.classification_type = 'form'
     AND n.organization = 'swiggy-mart-whirlpool'
     AND n.is_deleted = FALSE ),
     filtered_lfr AS
  ( SELECT lfr.reminder_id,
           lfr.reminded_at,
           lfr.reminder_window_end,
           lfr.form_response_id,
           lfr.responded_at,
           lfr.location_id,
           fr.organization,
           fr.tz_offset,
           fr.form_id,
           fn.title,
           alp.location_name AS "location"
   FROM public.form_reminders fr
   JOIN forms fn ON fn.id = fr.form_id
   JOIN public.location_form_reminders lfr ON fr.id = lfr.reminder_id
   JOIN active_locations_pods alp ON lfr.location_id = alp.id
   WHERE to_timestamp(lfr.reminded_at/1000) AT TIME ZONE 'Asia/Kolkata' >= date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '1 day') AND to_timestamp(lfr.reminded_at/1000) AT TIME ZONE 'Asia/Kolkata' < date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')),
     lfr AS
  ( SELECT lfr.reminder_id,
           lfr.organization,
           lfr.tz_offset AS tz_offset_sec,
           lfr.form_id,
           lfr.title,
           lfr.location,
           regexp_replace(lfr."location", '([0-9]+).*', '\1') AS pod_id,
           (to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*lfr.tz_offset)::date AS reminded_date,
           row_number() OVER ( PARTITION BY lfr.form_id,
                                            alp.location_name,
                                            (to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*lfr.tz_offset)::date
                              ORDER BY to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*lfr.tz_offset ) AS reminder_no,
                             to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*lfr.tz_offset AS reminded_at,
                                                                           to_timestamp(lfr.reminder_window_end/1000) + interval '1 sec'*lfr.tz_offset AS reminder_window_end,
                                                                                                                                 lfr.form_response_id,
                                                                                                                                 CASE
                                                                                                                                     WHEN lfr.responded_at = 0 THEN NULL
                                                                                                                                     ELSE to_timestamp(lfr.responded_at/1000) + interval '1 sec'*lfr.tz_offset
                                                                                                                                 END AS responded_at
   FROM filtered_lfr lfr
   JOIN active_locations_pods alp ON lfr.location_id = alp.id),
     fs AS
  ( SELECT fs.*
   FROM form_submissions fs
   WHERE fs.submit_date AT TIME ZONE 'Asia/Kolkata' >= date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '1 day') AND fs.submit_date AT TIME ZONE 'Asia/Kolkata' < date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')
     AND fs.form_id IN
       (SELECT id
        FROM forms)
     AND fs.location IN
       (SELECT location_name
        FROM active_locations_pods) ),
     fr AS
  ( SELECT fs.form_id,
           fs.submit_date AT TIME ZONE 'Asia/Kolkata' AS submit_date,
                                       fs.response_id,
                                       fr.response->>'name' AS LOCATION,
                                                     row_number() OVER ( PARTITION BY fs.form_id,
                                                                                      (fs.submit_date AT TIME ZONE 'Asia/Kolkata')::date,
                                                                                      fr.response->>'name'
                                                                        ORDER BY fs.submit_date ) AS submission_no
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   WHERE fr.question_type = 'location'
     AND regexp_replace(fr.response->>'name', '([0-9]+).*', '\1') IN
       (SELECT pod_id
        FROM lm) ), base as (
SELECT lfr.organization AS "Organization",
       lm.cluster AS "Cluster",
       lm.city AS "City",
       coalesce(lm.pod_id, lfr.pod_id) AS "Pod ID",
       lm.pod_name AS "Pod Name",
       lm.com AS "COM",
       lm.dch AS "DCH",
       (lfr.reminded_at)::date AS "Date",
       count(lfr.form_id)::numeric AS "Total Due",
       sum(CASE
           WHEN coalesce(lfr.form_response_id, fr.response_id) IS NULL THEN 0.0
           ELSE 1.0
       END) AS "Total Done"
FROM lfr
LEFT OUTER JOIN fr ON fr.form_id = lfr.form_id
AND (fr.submit_date)::date = (lfr.reminded_at)::date
AND fr.location = lfr.location
AND fr.submission_no = lfr.reminder_no
LEFT OUTER JOIN lm ON lfr.pod_id = lm.pod_id
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8)
		 select *,
		case when "Total Done" = 0 then 1 else 0 end as "0 Adoption",
		case when "Total Done" > 0 and "Total Done" / "Total Due" < 0.5 then 1 else 0 end as "Sub 50 Adoption"
		from base
ORDER BY 8 DESC,
         1, 2, 3, 4
```

---

## Instamart Impact Daily Report_IMPACT Report Daily Emailer.sql

**Tables referenced:** ROLES, acl, active_locations_pods, base_forms, filtered_lfr, form_responses, form_submissions, forms, fr, fs, lfr, lm, locations, lr, public.form_reminders, public.location_form_reminders, public.locations, public.nuggets, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Instamart Impact Daily Report
-- Dashboard: IMPACT Report Daily Emailer
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:57:10
-- ============================================================

WITH acl AS
  (select regexp_replace(l.location_name, '([0-9]+).*', '\1') AS store_id 
from locations l 
where organization = 'swiggy-mart-whirlpool'
and is_active = true
and (
               (SELECT is_super_admin
                FROM user_details
                WHERE uuid = @{{:UUIDParameter}})
             OR location_name in (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'swiggy-mart-whirlpool'
   and is_active = 'true'
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid = @{{:UUIDParameter}})
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id =@{{:UUIDParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))))),
     lr AS
  (SELECT acl.store_id,
          l.location_name AS store_name,
          r.name AS ROLE,
          ud.uuid AS holder_id,
          ud.first_name||' '||ud.last_name AS holder
   FROM acl
   JOIN locations l ON acl.store_id = regexp_replace(l.location_name, '([0-9]+).*', '\1')
   JOIN role_holders rh ON l.id = rh.location_id and rh.is_active = true
   JOIN ROLES r ON r.id = rh.role_id and r.is_active = 'true'
   LEFT OUTER JOIN user_details ud ON rh.role_holder_id = ud.uuid
   WHERE l.organization = 'swiggy-mart-whirlpool'
     AND l.is_active = 'true'
     AND ud.is_active = 'true'
     AND r.name IN ('Cluster Ops Manager',
                    'Deputy City Head')
   ORDER BY 1,
            2),
     lm AS
  (SELECT lr.store_id AS pod_id,
          lr.store_name AS pod_name,
          ud.division AS CLUSTER,
          ud.sub_division AS city,
          max(CASE
                  WHEN ROLE = 'Cluster Ops Manager' THEN holder
                  ELSE NULL
              END) AS com,
          max(CASE
                  WHEN ROLE = 'Cluster Ops Manager' THEN holder_id
                  ELSE NULL
              END) AS com_knid,
          max(CASE
                  WHEN ROLE = 'Deputy City Head' THEN holder
                  ELSE NULL
              END) AS dch,
          max(CASE
                  WHEN ROLE ='Deputy City Head' THEN holder_id
                  ELSE NULL
              END) AS dch_knid
   FROM lr
   JOIN
     (SELECT DISTINCT ON (job_location) job_location,
                         division,
                         sub_division
      FROM user_details
      WHERE regexp_replace(job_location, '([0-9]+).*', '\1') IS NOT NULL
	  AND division is not null
      ORDER BY job_location,
               created_at DESC) ud ON lr.store_name = ud.job_location
   GROUP BY 1,
            2,
            3,
            4
   ORDER BY 1),
     active_locations_pods AS
  ( SELECT id,
           location_name
   FROM public.locations l
   WHERE l.organization = 'swiggy-mart-whirlpool'
     AND l.is_active = TRUE
     AND regexp_replace(l.location_name, '([0-9]+).*', '\1') IN
       (SELECT pod_id
        FROM lm) ),
     base_forms AS
  ( SELECT id,
           regexp_replace(title, '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '') AS title
   FROM public.nuggets
   WHERE is_deleted = FALSE
     AND id IN ( '-OC37vPYSTaYpa6rNk7y',
                 '-OB4CVmT_YAytFR2fty7',
                 '-OB4xcGu1NqT84w0lAWQ',
                 '-O9U1GGkwZWt_Vs6okDW',
                 '-OB4z2473dKeZ34McBIV',
                 '-OB4zWin85ZrjPUjH0RV',
                 '-OB4zm7TVqXaKK3J0vAX',
                 '-OB5-5PzkC26eek0Bk-1',
                 '-OB5-Q1oguPmrJlRlBnH',
                 '-OBPR5RTpUGaHJsVJFZH',
                 '-OB5-kLCkZWwy65-Ek6h',
                 '-OB505iZAJ8wJ0zZxcFM',
                 '-OB525WEclHOXV6JYtJn',
                 '-OB51wGxzBWxhStUNtqv',
                 '-OB52IvLT3rJTvAM7wLT',
                 '-OB52TuE5WfUdYkJdmrE',
                 '-OB52jx59NEjUjPBixqy',
                 '-OB52ttmR2iTHizVPXwE',
                 '-OB55VCsN1K47jdOc-N2',
                 '-OB5622pYYZHwe2fCC1W',
                 '-OB56cNfUDEhTxUPhJ4S',
                 '-OB56mQetguLSxb-mTv6',
                 '-OB57bk-9BG-rX7wAceu',
                 '-OAIJndZxwVht8750Zc6',
                 '-OAIsM27j29lvnM9Br5O',
                 '-OAIx7irPIBo-9cKLh_y',
                 '-OALkeIDkVHTQtxyEVne',
                 '-OAvN4-5jv-XvXPhQEeM',
                 '-OAvPLR9pQLC_wvRpX0Y',
                 '-OAvQgdymG5aSTHcrVQR',
                 '-OAvVUTteJqBgqdYYJgq',
                 '-OAvVhmAOQCKn9Ln_JC-',
                 '-OAvVvs7yNtCfVItyUr4',
                 '-OAvWIJh_dc1cSU8uJgq',
                 '-OAvWV2dPw9S0L6KWBlb',
                 '-OAvb8LGJYxjlH_YrSRb',
                 '-OAvWvojjYv0Cxl9uTai',
                 '-OBAL68W_bLx6qrgfVjm',
                 '-OB0_uO6Q4lBeasMViQT',
                 '-OB56yx-t8HP7oBY0JQX',
                 '-OB0_OEwgHSkOq9KOr7P',
                 '-OBZLlW2pRYqtVoLwUJq',
                 '-OBdNIXxFdIQrGnbqESi',
                 '-OBdNs7lzEaEIhrrlwHk',
                 '-OC351d72Tg3nF69kF0Z',
                 '-O5vnwzkiszWtqSl6QGF',
                 '-O73HoSK3DHguZxXg_q0' ) ),
     forms AS
  ( SELECT n.id,
           bf.title
   FROM public.nuggets n
   JOIN base_forms bf ON bf.title = regexp_replace(n.title, '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '')
   WHERE n.classification_type = 'form'
     AND n.organization = 'swiggy-mart-whirlpool'
     AND n.is_deleted = FALSE ),
     filtered_lfr AS
  ( SELECT lfr.reminder_id,
           lfr.reminded_at,
           lfr.reminder_window_end,
           lfr.form_response_id,
           lfr.responded_at,
           lfr.location_id,
           fr.organization,
           fr.tz_offset,
           fr.form_id,
           fn.title,
           alp.location_name AS "location"
   FROM public.form_reminders fr
   JOIN forms fn ON fn.id = fr.form_id
   JOIN public.location_form_reminders lfr ON fr.id = lfr.reminder_id
   JOIN active_locations_pods alp ON lfr.location_id = alp.id
   WHERE to_timestamp(lfr.reminded_at/1000) AT TIME ZONE 'Asia/Kolkata' BETWEEN date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '1 day') AND date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')),
     lfr AS
  ( SELECT lfr.reminder_id,
           lfr.organization,
           lfr.tz_offset AS tz_offset_sec,
           lfr.form_id,
           lfr.title,
           lfr.location,
           regexp_replace(lfr."location", '([0-9]+).*', '\1') AS pod_id,
           (to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*lfr.tz_offset)::date AS reminded_date,
           row_number() OVER ( PARTITION BY lfr.form_id,
                                            alp.location_name,
                                            (to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*lfr.tz_offset)::date
                              ORDER BY to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*lfr.tz_offset ) AS reminder_no,
                             to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*lfr.tz_offset AS reminded_at,
                                                                           to_timestamp(lfr.reminder_window_end/1000) + interval '1 sec'*lfr.tz_offset AS reminder_window_end,
                                                                                                                                 lfr.form_response_id,
                                                                                                                                 CASE
                                                                                                                                     WHEN lfr.responded_at = 0 THEN NULL
                                                                                                                                     ELSE to_timestamp(lfr.responded_at/1000) + interval '1 sec'*lfr.tz_offset
                                                                                                                                 END AS responded_at
   FROM filtered_lfr lfr
   JOIN active_locations_pods alp ON lfr.location_id = alp.id),
     fs AS
  ( SELECT fs.*
   FROM form_submissions fs
   WHERE fs.submit_date AT TIME ZONE 'Asia/Kolkata' BETWEEN date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '1 day') AND date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')
     AND fs.form_id IN
       (SELECT id
        FROM forms)
     AND fs.location IN
       (SELECT location_name
        FROM active_locations_pods) ),
     fr AS
  ( SELECT fs.form_id,
           fs.submit_date AT TIME ZONE 'Asia/Kolkata' AS submit_date,
                                       fs.response_id,
                                       fr.response->>'name' AS LOCATION,
                                                     row_number() OVER ( PARTITION BY fs.form_id,
                                                                                      (fs.submit_date AT TIME ZONE 'Asia/Kolkata')::date,
                                                                                      fr.response->>'name'
                                                                        ORDER BY fs.submit_date ) AS submission_no
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   WHERE fr.question_type = 'location'
     AND regexp_replace(fr.response->>'name', '([0-9]+).*', '\1') IN
       (SELECT pod_id
        FROM lm) )
SELECT lfr.organization AS "Organization",
       lm.cluster AS "Cluster",
       lm.city AS "City",
       coalesce(lm.pod_id, lfr.pod_id) AS "Pod ID",
       lm.pod_name AS "Pod Name",
       lm.com AS "COM",
       lm.dch AS "DCH",
       (lfr.reminded_at)::date AS "Date",
       lfr.form_id AS "Routine KNID",
       lfr.title AS "Routine Name",
       lfr.reminded_at AS "Reminded At",
       lfr.reminder_window_end AS "Due At",
       CASE
           WHEN (lfr.reminded_at)::TIME BETWEEN '06:00:01' AND '12:00:01' THEN '1 - Morning'
           WHEN (lfr.reminded_at)::TIME BETWEEN '12:00:01' AND '20:00:01' THEN '2 - Afternoon'
           ELSE '3 - Night'
       END AS "Shift",
       CASE
           WHEN lfr.form_response_id IS NOT NULL THEN 'Compliant'
           WHEN fr.response_id IS NULL THEN 'Missed'
           ELSE 'Done Late'
       END AS "Status",
       CASE
           WHEN lfr.form_response_id IS NOT NULL THEN 1
           WHEN fr.response_id IS NULL THEN 0
           ELSE 0.5
       END AS "Compliance Score",
       CASE
           WHEN coalesce(lfr.form_response_id, fr.response_id) IS NULL THEN 0.0
           ELSE 1.0
       END AS "Completion Score",
       coalesce(lfr.form_response_id, fr.response_id) AS "Submission KNID"
FROM lfr
LEFT OUTER JOIN fr ON fr.form_id = lfr.form_id
AND (fr.submit_date)::date = (lfr.reminded_at)::date
AND fr.location = lfr.location
AND fr.submission_no = lfr.reminder_no
LEFT OUTER JOIN lm ON lfr.pod_id = lm.pod_id
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
         17
ORDER BY 11 DESC,
         10,
         1,
         2,
         3,
         4
```

---

## Instamart Impact Report with custom date range_IMPACT Report.sql

**Tables referenced:** ROLES, acl, active_locations_pods, base_forms, filtered_lfr, form_responses, form_submissions, forms, fr, fs, lfr, lm, locations, lr, public.form_reminders, public.location_form_reminders, public.locations, public.nuggets, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Instamart Impact Report with custom date range
-- Dashboard: IMPACT Report
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:57:15
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT regexp_replace(l.location_name, '([0-9]+).*', '\1') AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id AND rh.is_active = true
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
        AND left(l.location_name, 3) ~ '^\d{3}'
      UNION SELECT regexp_replace(l.location_name, '([0-9]+).*', '\1') AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
        AND left(l.location_name, 3) ~ '^\d{3}'
      UNION SELECT regexp_replace(ud.job_location, '([0-9]+).*', '\1') AS store_id
      FROM user_details ud
      WHERE organization = 'swiggy-mart-whirlpool'
        AND is_active = 'true'
        AND left(ud.job_location, 3) ~ '^\d{3}'
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
                  AND ug1.is_active = TRUE))) l),     
				  
				  lr AS   (
                  SELECT acl.store_id,
          l.location_name AS store_name,
          r.name AS ROLE,
          ud.uuid AS holder_id,
          ud.first_name||' '||ud.last_name AS holder
   FROM acl
   JOIN locations l ON acl.store_id = regexp_replace(l.location_name, '([0-9]+).*', '\1')
   JOIN role_holders rh ON l.id = rh.location_id and rh.is_active = true
   JOIN ROLES r ON r.id = rh.role_id
   LEFT OUTER JOIN user_details ud ON rh.role_holder_id = ud.uuid
   WHERE l.organization = 'swiggy-mart-whirlpool'
     AND l.is_active = 'true'
     AND ud.is_active = 'true'
     AND r.name IN ('Cluster Ops Manager',
                    'Deputy City Head')
   ORDER BY 1,
            2),     
			
			lm AS  (
            SELECT lr.store_id AS pod_id,
          lr.store_name AS pod_name,
          ud.division AS CLUSTER,
          ud.sub_division AS city,
          max(CASE
                  WHEN ROLE = 'Cluster Ops Manager' THEN holder
                  ELSE NULL
              END) AS com,
          max(CASE
                  WHEN ROLE = 'Cluster Ops Manager' THEN holder_id
                  ELSE NULL
              END) AS com_knid,
          max(CASE
                  WHEN ROLE = 'Deputy City Head' THEN holder
                  ELSE NULL
              END) AS dch,
          max(CASE
                  WHEN ROLE ='Deputy City Head' THEN holder_id
                  ELSE NULL
              END) AS dch_knid
   FROM lr
   JOIN
     (SELECT DISTINCT ON (job_location) job_location,
                         division,
                         sub_division
      FROM user_details
      WHERE regexp_replace(job_location, '([0-9]+).*', '\1') IS NOT NULL
	  AND division is not null
      ORDER BY job_location,
               created_at DESC) ud ON lr.store_name = ud.job_location
   GROUP BY 1,
            2,
            3,
            4
   ORDER BY 1),      
   
   active_locations_pods AS  (
   SELECT id,
           location_name
   FROM public.locations l
   WHERE l.organization = 'swiggy-mart-whirlpool'
     AND l.is_active = TRUE
     AND regexp_replace(l.location_name, '([0-9]+).*', '\1') IN
       (SELECT pod_id
        FROM lm) ),
		
     base_forms AS
  ( SELECT id,
           regexp_replace(title, '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '') AS title
   FROM public.nuggets
   WHERE is_deleted = FALSE
     AND id IN ( '-OC37vPYSTaYpa6rNk7y',
                 '-OB4CVmT_YAytFR2fty7',
                 '-OB4xcGu1NqT84w0lAWQ',
                 '-O9U1GGkwZWt_Vs6okDW',
                 '-OB4z2473dKeZ34McBIV',
                 '-OB4zWin85ZrjPUjH0RV',
                 '-OB4zm7TVqXaKK3J0vAX',
                 '-OB5-5PzkC26eek0Bk-1',
                 '-OB5-Q1oguPmrJlRlBnH',
                 '-OBPR5RTpUGaHJsVJFZH',
                 '-OB5-kLCkZWwy65-Ek6h',
                 '-OB505iZAJ8wJ0zZxcFM',
                 '-OB525WEclHOXV6JYtJn',
                 '-OB51wGxzBWxhStUNtqv',
                 '-OB52IvLT3rJTvAM7wLT',
                 '-OB52TuE5WfUdYkJdmrE',
                 '-OB52jx59NEjUjPBixqy',
                 '-OB52ttmR2iTHizVPXwE',
                 '-OB55VCsN1K47jdOc-N2',
                 '-OB5622pYYZHwe2fCC1W',
                 '-OB56cNfUDEhTxUPhJ4S',
                 '-OB56mQetguLSxb-mTv6',
                 '-OB57bk-9BG-rX7wAceu',
                 '-OAIJndZxwVht8750Zc6',
                 '-OAIsM27j29lvnM9Br5O',
                 '-OAIx7irPIBo-9cKLh_y',
                 '-OALkeIDkVHTQtxyEVne',
                 '-OAvN4-5jv-XvXPhQEeM',
                 '-OAvPLR9pQLC_wvRpX0Y',
                 '-OAvQgdymG5aSTHcrVQR',
                 '-OAvVUTteJqBgqdYYJgq',
                 '-OAvVhmAOQCKn9Ln_JC-',
                 '-OAvVvs7yNtCfVItyUr4',
                 '-OAvWIJh_dc1cSU8uJgq',
                 '-OAvWV2dPw9S0L6KWBlb',
                 '-OAvb8LGJYxjlH_YrSRb',
                 '-OAvWvojjYv0Cxl9uTai',
                 '-OBAL68W_bLx6qrgfVjm',
                 '-OB0_uO6Q4lBeasMViQT',
                 '-OB56yx-t8HP7oBY0JQX',
                 '-OB0_OEwgHSkOq9KOr7P',
                 '-OBZLlW2pRYqtVoLwUJq',
                 '-OBdNIXxFdIQrGnbqESi',
                 '-OBdNs7lzEaEIhrrlwHk',
                 '-OC351d72Tg3nF69kF0Z',
                 '-O5vnwzkiszWtqSl6QGF',
                 '-O73HoSK3DHguZxXg_q0' ) ),
				 
     forms AS
  ( SELECT n.id,
           bf.title
   FROM public.nuggets n
   JOIN base_forms bf ON bf.title = regexp_replace(n.title, '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '')
   WHERE n.classification_type = 'form'
     AND n.organization = 'swiggy-mart-whirlpool'
     AND n.is_deleted = FALSE ),     
	 
	 filtered_lfr AS   (
     SELECT lfr.reminder_id,
           lfr.reminded_at,
           lfr.reminder_window_end,
           lfr.form_response_id,
           lfr.responded_at,
           lfr.location_id,
           fr.organization,
           fr.tz_offset,
           fr.form_id,
           fn.title,
           alp.location_name AS "location"
   FROM public.form_reminders fr
   JOIN forms fn ON fn.id = fr.form_id
   JOIN public.location_form_reminders lfr ON fr.id = lfr.reminder_id
   JOIN active_locations_pods alp ON lfr.location_id = alp.id
   WHERE to_timestamp(lfr.reminded_at/1000) AT TIME ZONE 'Asia/Kolkata' BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + interval '1 day'),
   
   lfr AS
  ( SELECT lfr.reminder_id,
           lfr.organization,
           lfr.tz_offset AS tz_offset_sec,
           lfr.form_id,
           lfr.title,
           lfr.location,
           regexp_replace(lfr."location", '([0-9]+).*', '\1') AS pod_id,
           (to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*lfr.tz_offset)::date AS reminded_date,
           row_number() OVER ( PARTITION BY lfr.form_id,
                                            alp.location_name,
                                            (to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*lfr.tz_offset)::date
                              ORDER BY to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*lfr.tz_offset ) AS reminder_no,
                             to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*lfr.tz_offset AS reminded_at,
                                                                           to_timestamp(lfr.reminder_window_end/1000) + interval '1 sec'*lfr.tz_offset AS reminder_window_end,
                                                                                                                                 lfr.form_response_id,
                                                                                                                                 CASE
                                                                                                                                     WHEN lfr.responded_at = 0 THEN NULL
                                                                                                                                     ELSE to_timestamp(lfr.responded_at/1000) + interval '1 sec'*lfr.tz_offset
                                                                                                                                 END AS responded_at
   FROM filtered_lfr lfr
   JOIN active_locations_pods alp ON lfr.location_id = alp.id),
  
  fs AS
  ( SELECT fs.*
   FROM form_submissions fs
   WHERE fs.submit_date AT TIME ZONE 'Asia/Kolkata' BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + interval '1 day'
     AND fs.form_id IN
       (SELECT id
        FROM forms)
     AND fs.location IN
       (SELECT location_name
        FROM active_locations_pods) ),
  
  fr AS
  ( SELECT fs.form_id,
           fs.submit_date AT TIME ZONE 'Asia/Kolkata' AS submit_date,
                                       fs.response_id,
                                       fr.response->>'name' AS LOCATION,
                                                     row_number() OVER ( PARTITION BY fs.form_id,
                                                                                      (fs.submit_date AT TIME ZONE 'Asia/Kolkata')::date,
                                                                                      fr.response->>'name'
                                                                        ORDER BY fs.submit_date ) AS submission_no
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   WHERE fr.question_type = 'location'
     AND regexp_replace(fr.response->>'name', '([0-9]+).*', '\1') IN
       (SELECT pod_id
        FROM lm) )
		
SELECT lfr.organization AS "Organization",
       lm.cluster AS "Cluster",
       lm.city AS "City",
       coalesce(lm.pod_id, lfr.pod_id) AS "Pod ID",
       lm.pod_name AS "Pod Name",
       lm.com AS "COM",
       lm.dch AS "DCH",
       (lfr.reminded_at)::date AS "Date",
       lfr.form_id AS "Routine KNID",
       lfr.title AS "Routine Name",
       lfr.reminded_at AS "Reminded At",
       lfr.reminder_window_end AS "Due At",
       CASE
           WHEN (lfr.reminded_at)::TIME BETWEEN '06:00:01' AND '12:00:01' THEN '1 - Morning'
           WHEN (lfr.reminded_at)::TIME BETWEEN '12:00:01' AND '20:00:01' THEN '2 - Afternoon'
           ELSE '3 - Night'
       END AS "Shift",
       CASE
           WHEN lfr.form_response_id IS NOT NULL THEN 'Compliant'
           WHEN fr.response_id IS NULL THEN 'Missed'
           ELSE 'Done Late'
       END AS "Status",
       CASE
           WHEN lfr.form_response_id IS NOT NULL THEN 1
           WHEN fr.response_id IS NULL THEN 0
           ELSE 0.5
       END AS "Compliance Score",
       CASE
           WHEN coalesce(lfr.form_response_id, fr.response_id) IS NULL THEN 0.0
           ELSE 1.0
       END AS "Completion Score",
       coalesce(lfr.form_response_id, fr.response_id) AS "Submission KNID"
FROM lfr
LEFT OUTER JOIN fr ON fr.form_id = lfr.form_id
AND (fr.submit_date)::date = (lfr.reminded_at)::date
AND fr.location = lfr.location
AND fr.submission_no = lfr.reminder_no
LEFT OUTER JOIN lm ON lfr.pod_id = lm.pod_id
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
         17
ORDER BY 11 DESC,
         10,
         1,
         2,
         3,
         4
```

---

## Instamart Job Readiness Index_Job Readiness Index.sql

**Tables referenced:** best_answer, conf_score, ke_score, max_attempt, rel_score

**Columns needing snake_case conversion:**

- `cardId` -> `card_id` (alias: `card_id AS "cardId"`)

- `courseID` -> `course_id` (alias: `course_id AS "courseID"`)

- `courseId` -> `course_id` (alias: `course_id AS "courseId"`)

- `createdAt` -> `created_at` (alias: `created_at AS "createdAt"`)

- `isCorrect` -> `is_correct` (alias: `is_correct AS "isCorrect"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Instamart Job Readiness Index
-- Dashboard: Job Readiness Index
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:53:40
-- ============================================================

WITH conf_score AS
  (SELECT userId AS user_id,
          sum(cast(JSON_VALUE(r, '$.response') AS int))*1.00/count(cast(JSON_VALUE(r, '$.question') AS int))/5 AS conf_score
   FROM `whirlpool-galaxy.analytics.survey_responses` s,
        s.data AS r
   WHERE courseId IN ('vPD4uWQJ9Mh3Eua1XtabAy')
   and cast(JSON_VALUE(r, '$.question') AS int) in (3, 4)
     AND TIMESTAMP_ADD(createdAt, INTERVAL 330 MINUTE) BETWEEN cast(@{{:Date Range.START}} AS TIMESTAMP) AND cast(TIMESTAMP_ADD(@{{:Date Range.END}}, INTERVAL 1 DAY) AS TIMESTAMP)
   GROUP BY 1),
     rel_score AS
  (SELECT userId AS user_id,
          sum(cast(JSON_VALUE(r, '$.response') AS int))*1.00/count(cast(JSON_VALUE(r, '$.question') AS int))/5 AS rel_score
   FROM `whirlpool-galaxy.analytics.survey_responses` s,
        s.data AS r
   WHERE courseId IN ('vPD4uWQJ9Mh3Eua1XtabAy')
   and cast(JSON_VALUE(r, '$.question') AS int) in (0, 1, 2)
     AND TIMESTAMP_ADD(createdAt, INTERVAL 330 MINUTE) BETWEEN cast(@{{:Date Range.START}} AS TIMESTAMP) AND cast(TIMESTAMP_ADD(@{{:Date Range.END}}, INTERVAL 1 DAY) AS TIMESTAMP)
   GROUP BY 1),
     max_attempt AS
  (SELECT userId,
          courseId,
          cardId,
          max(attempt) AS last_attempt
   FROM `whirlpool-galaxy.analytics.quiz_responses` q
   WHERE courseId IN ('wtsGhTLYUKXpThHnE4A9Q6')
     AND cardId IN ('dwiP7NVhwHUhqnWWVQipYM')
     AND TIMESTAMP_ADD(createdAt, INTERVAL 330 MINUTE) BETWEEN cast(@{{:Date Range.START}} AS TIMESTAMP) AND cast(TIMESTAMP_ADD(@{{:Date Range.END}}, INTERVAL 1 DAY) AS TIMESTAMP)
   GROUP BY 1,
            2,
            3),
     best_answer AS
  (SELECT q.userId,
          q.courseId,
          q.cardId,
          q.questionId,
          max(q.isCorrect) AS best_answer
   FROM `whirlpool-galaxy.analytics.quiz_responses` q
   JOIN max_attempt ma ON q.userId = ma.userId
   AND q.courseID = ma.courseId
   AND q.cardId = ma.cardId
   AND q.attempt = ma.last_attempt
   WHERE q.courseId IN ('wtsGhTLYUKXpThHnE4A9Q6')
     AND q.cardId IN ('dwiP7NVhwHUhqnWWVQipYM')
   GROUP BY 1,
            2,
            3,
            4),
     ke_score AS
  (SELECT q.userId AS user_id,
          count(distinct(CASE
                    WHEN ba.best_answer = TRUE THEN q.questionId
                    ELSE NULL
                END))*1.00/count(distinct(ba.questionId)) AS ke_score
   FROM `whirlpool-galaxy.analytics.quiz_responses` q
   JOIN best_answer ba ON q.userId = ba.userId
   AND q.courseID = ba.courseId
   AND q.cardId = ba.cardId
   AND q.questionId = ba.questionId
   WHERE q.courseId IN ('wtsGhTLYUKXpThHnE4A9Q6')
     AND q.cardId IN ('dwiP7NVhwHUhqnWWVQipYM')
   GROUP BY 1)
SELECT u.uuid AS `Staff KNID`,
       u.identifier AS `Staff ID`,
       u.first_name||' '||u.last_name AS `Staff Name`,
       u.phone_number AS `Phone Number`,
       u.job_location AS `Job Location`,
       u.division AS `Division`,
       u.sub_division AS `Sub Division`,	   
       ke_score.ke_score*100 AS `KE Score`,
       conf_score.conf_score*100 AS `Confidence Score`,
       rel_score.rel_score*100 AS `Relevance Score`,
       (ke_score.ke_score + conf_score.conf_score + rel_score.rel_score)*100/3 AS `JRI`
FROM `whirlpool-galaxy.public.user_details` u
JOIN ke_score ON u.uuid = ke_score.user_id
LEFT OUTER JOIN conf_score ON u.uuid = conf_score.user_id
LEFT OUTER JOIN rel_score ON u.uuid = rel_score.user_id
```

---

## Instamart Last Week COM GEMBA Adoption_Last Week COM Gemba Adoption.sql

**Tables referenced:** ROLES, com_compliance, com_responses, expected_com, form_responses, form_submissions, forms, fs, generate_series, lm, locations, lr, nuggets, role_holders, user_details

**Original Query:**

```sql
-- Data Source: Instamart Last Week COM GEMBA Adoption
-- Dashboard: Last Week COM Gemba Adoption
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:57:11
-- ============================================================

WITH forms AS
  (SELECT id AS form_knid,
          'Walk to Elevate - COMs' AS form_name
   FROM nuggets
   WHERE organization = 'swiggy-mart-whirlpool'
     AND classification_type = 'form'
     AND title LIKE 'Walk to Elevate - COMs%'),
     lr AS
  (SELECT regexp_replace(l.location_name, '([0-9]+).*', '\1') AS store_id,
          l.location_name AS store_name,
          r.name AS ROLE,
          ud.uuid AS holder_id,
          ud.first_name||' '||ud.last_name AS holder
   FROM locations l
   LEFT JOIN role_holders rh ON l.id = rh.location_id
   AND rh.is_active = TRUE
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.is_active = 'true'
   LEFT OUTER JOIN user_details ud ON rh.role_holder_id = ud.uuid
   WHERE l.organization = 'swiggy-mart-whirlpool'
     AND l.is_active = 'true'
     AND ud.is_active = 'true'
     AND r.name IN ('Cluster Ops Manager')
     AND location_name ~ '^\d{3}'
   ORDER BY 1,
            2),
     lm AS
  (SELECT lr.store_id AS pod_id,
          lr.store_name AS pod_name,
          ud.division AS CLUSTER,
          ud.sub_division AS city,
          max(CASE
                  WHEN ROLE = 'Cluster Ops Manager' THEN holder
                  ELSE NULL
              END) AS com,
          max(CASE
                  WHEN ROLE = 'Cluster Ops Manager' THEN holder_id
                  ELSE NULL
              END) AS com_knid
   FROM lr
   JOIN
     (SELECT DISTINCT ON (job_location) job_location,
                         division,
                         sub_division
      FROM user_details
      WHERE regexp_replace(job_location, '([0-9]+).*', '\1') IS NOT NULL
        AND division IS NOT NULL
      ORDER BY job_location,
               created_at DESC) ud ON lr.store_name = ud.job_location
   GROUP BY 1,
            2,
            3,
            4
   ORDER BY 1),
     expected_com AS
  (SELECT *
   FROM
     (SELECT date::date
      FROM generate_series(date_trunc('Week', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '7 days'), date_trunc('Week', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '7 days'), '1 day'::interval) AS date) AS cal
   CROSS JOIN
     (SELECT *
      FROM lm) outlets
   CROSS JOIN
     (SELECT 'Walk to Elevate - COMs' AS form)),
     fs AS
  (SELECT DISTINCT ON (fs.response_id) (fs.submit_date AT TIME ZONE 'Asia/Kolkata')::date AS date,
                      'Walk to Elevate - COMs' AS form,
                      fs.response_id,
                      fs.sno,
                      fs.location,
                      fs.id
   FROM form_submissions fs
   WHERE fs.form_id IN
       (SELECT form_knid
        FROM forms)
     AND submit_date AT TIME ZONE 'Asia/Kolkata' BETWEEN date_trunc('Week', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '7 days') AND date_trunc('Week', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')
   ORDER BY fs.response_id,
            fs.id),
     com_responses AS
  (SELECT fs.date,
          form,
          response_id,
          sno,
          coalesce(regexp_replace(fr.response->>'name', '([0-9]+).*', '\1'), regexp_replace(fs.location, '([0-9]+).*', '\1')) AS pod_id
   FROM fs
   LEFT OUTER JOIN form_responses fr ON fs.id = fr.form_submit_id
   AND fr.response->>'name' IS NOT NULL
   AND fr.response->>'id' IS NOT NULL
   WHERE COALESCE(fr.response->>'name', fs.location) ~ '^\d{3}' ),
     com_compliance AS
  (SELECT expected_com.date AS "Date",
          expected_com.form AS "Form",
          expected_com.pod_id AS "Pod ID",
          CASE
              WHEN com_responses.response_id IS NOT NULL THEN 1
              ELSE 0
          END AS "Compliance",
          CASE
              WHEN com_responses.response_id IS NOT NULL THEN 'Completed'
              ELSE 'Missed'
          END AS "Status",
          com_responses.sno AS "Submission No",
          com_responses.response_id AS "Submission KNID"
   FROM expected_com
   LEFT OUTER JOIN com_responses ON expected_com.date = date_trunc('Week', com_responses.date)
   AND expected_com.form = com_responses.form
   AND expected_com.pod_id = com_responses.pod_id
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7)
SELECT DISTINCT ON (lm.pod_id,
                    compliance."Date",
                    compliance."Form") compliance."Date" AS "Week of",
                   lm.pod_id AS "Pod ID",
                   compliance."Form" AS "Audit Type",
                   lm.cluster AS "Cluster",
                   lm.city AS "City",
                   lm.com AS "Cluster Ops Manager",
                   compliance."Status",
                   compliance."Compliance",
                   compliance."Submission No",
                   compliance."Submission KNID"
FROM lm
LEFT OUTER JOIN com_compliance compliance ON compliance."Pod ID" = lm.pod_id
ORDER BY lm.pod_id,
         compliance."Date",
         compliance."Form",
         compliance."Submission No"
```

---

## Instamart MTD Gemba Adoption_MTD SM Gemba Adoption.sql

**Tables referenced:** expected_sm, form_responses, form_submissions, forms, fs, generate_series, location_map, nuggets, public.locations, public.user_details, sm_compliance, sm_responses

**Original Query:**

```sql
-- Data Source: Instamart MTD Gemba Adoption
-- Dashboard: MTD SM Gemba Adoption
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:57:12
-- ============================================================

WITH forms AS
  (SELECT id AS form_knid,
          'Walk to Elevate - SM/ASM' AS form_name
   FROM nuggets
   WHERE organization = 'swiggy-mart-whirlpool'
     AND classification_type = 'form'
     AND title LIKE 'Walk to Elevate - SM%'),
     expected_sm AS
  (SELECT *
   FROM
     (SELECT date::date
      FROM generate_series(date_trunc('Month', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '1 day'), date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '1 day'), '1 day'::interval) AS date) AS cal
   CROSS JOIN
     (SELECT SUBSTRING(location_name
                       FROM '\d+') AS pod
      FROM public.locations
      WHERE location_name ~ '^\d{3}'
        AND organization = 'swiggy-mart-whirlpool'
        AND is_active = TRUE) outlets
   CROSS JOIN
     (SELECT 'Walk to Elevate - SM/ASM' AS form)),
     fs AS
  (SELECT DISTINCT ON (fs.response_id) (fs.submit_date AT TIME ZONE 'Asia/Kolkata')::date AS date,
                      'Walk to Elevate - SM/ASM' AS form,
                      fs.response_id,
                      fs.sno,
                      fs.location,
                      fs.id
   FROM form_submissions fs
   WHERE fs.form_id IN
       (SELECT form_knid
        FROM forms)
     AND submit_date AT TIME ZONE 'Asia/Kolkata' BETWEEN date_trunc('Month', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '1 day') AND date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')
   ORDER BY fs.response_id,
            fs.id),
     sm_responses AS
  (SELECT fs.date,
          form,
          response_id,
          sno,
          SUBSTRING(COALESCE(fr.response->>'name', fs.location)
                    FROM '\d+') AS pod
   FROM fs
   LEFT OUTER JOIN form_responses fr ON fs.id = fr.form_submit_id
   AND fr.response->>'name' IS NOT NULL
   AND fr.response->>'id' IS NOT NULL
   WHERE COALESCE(fr.response->>'name', fs.location) ~ '^\d{3}' ),
     sm_compliance AS
  (SELECT expected_sm.date AS "Date",
          expected_sm.form AS "Form",
          expected_sm.pod AS "Pod ID",
          CASE
              WHEN sm_responses.response_id IS NOT NULL THEN 1
              ELSE 0
          END AS "Compliance",
          CASE
              WHEN sm_responses.response_id IS NOT NULL THEN 'Completed'
              ELSE 'Missed'
          END AS "Status",
          sm_responses.sno AS "Submission No",
          sm_responses.response_id AS "Submission KNID"
   FROM expected_sm
   LEFT OUTER JOIN sm_responses ON expected_sm.date = sm_responses.date
   AND expected_sm.form = sm_responses.form
   AND expected_sm.pod = sm_responses.pod
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7),
     location_map AS
  (SELECT DISTINCT ON (SUBSTRING(job_location
                                 FROM '\d+')) SUBSTRING(job_location
                                                        FROM '\d+') AS pod,
                      division,
                      sub_division
   FROM public.user_details
   WHERE job_location ~ '^\d{3}'
     AND is_active = TRUE
   ORDER BY SUBSTRING(job_location
                      FROM '\d+'),
            created_at DESC)
SELECT location_map.division AS "Region",
       location_map.sub_division AS "City",
       compliance."Pod ID",
       compliance."Date" AS "Date",
       CASE
           WHEN compliance."Form" LIKE '%SM/ASM%' THEN 'SM Gemba'
           WHEN compliance."Form" LIKE '%COM%' THEN 'COM Gemba'
           ELSE NULL
       END AS "Audit type",
       compliance."Status",
       compliance."Compliance",
       compliance."Submission No",
       compliance."Submission KNID"
FROM sm_compliance AS compliance
LEFT OUTER JOIN location_map ON compliance."Pod ID" = location_map.pod
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9
ORDER BY 1,
         2,
         3,
         4,
         5
```

---

## Instamart Onboarding Journey Adoption Report-copy_Onboarding Journey Adoption Report.sql

**Tables referenced:** DATA, analytics.lms_raw_analytics, analytics.quiz_responses, c, cards, course_consumed_at, final_quiz_cards, final_scores, first_course_consumed, full_progress, oj_attempt, oj_course_received, oj_course_shares, oj_received, oj_share_ids, oj_shares, progress, public.courses, public.learning_journey_courses, public.lesson_cards, public.lessons, public.user_details, quiz_cards

**Columns needing snake_case conversion:**

- `cardId` -> `card_id` (alias: `card_id AS "cardId"`)

- `consumedAt` -> `consumed_at` (alias: `consumed_at AS "consumedAt"`)

- `consumedCount` -> `consumed_count` (alias: `consumed_count AS "consumedCount"`)

- `courseID` -> `course_id` (alias: `course_id AS "courseID"`)

- `courseId` -> `course_id` (alias: `course_id AS "courseId"`)

- `createdAt` -> `created_at` (alias: `created_at AS "createdAt"`)

- `isCorrect` -> `is_correct` (alias: `is_correct AS "isCorrect"`)

- `learningJourneyId` -> `learning_journey_id` (alias: `learning_journey_id AS "learningJourneyId"`)

- `lessonId` -> `lesson_id` (alias: `lesson_id AS "lessonId"`)

- `ljId` -> `lj_id` (alias: `lj_id AS "ljId"`)

- `nuggetID` -> `nugget_id` (alias: `nugget_id AS "nuggetID"`)

- `nuggetId` -> `nugget_id` (alias: `nugget_id AS "nuggetId"`)

- `ojAttempt` -> `oj_attempt` (alias: `oj_attempt AS "ojAttempt"`)

- `qCount` -> `q_count` (alias: `q_count AS "qCount"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `quizCardId` -> `quiz_card_id` (alias: `quiz_card_id AS "quizCardId"`)

- `receivedAt` -> `received_at` (alias: `received_at AS "receivedAt"`)

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `shareId` -> `share_id` (alias: `share_id AS "shareId"`)

- `totalCards` -> `total_cards` (alias: `total_cards AS "totalCards"`)

- `userID` -> `user_id` (alias: `user_id AS "userID"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Instamart Onboarding Journey Adoption Report-copy
-- Dashboard: Onboarding Journey Adoption Report
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:52:54
-- ============================================================

WITH c AS
  (SELECT *
   FROM public.courses
   WHERE id IN (
                'azwDGTkdA51Htk3ns9frSi',
               'wtsGhTLYUKXpThHnE4A9Q6',
               '3cgPTwQuwzqNu1ZmT5tNcB',
               'vPD4uWQJ9Mh3Eua1XtabAy',
               'bidvm66pkDfoZ8FrBJsgoZ',
               '4SFg55oeWXSiWK322YYJPD',
               '7De2YCm42esCR4szqL2wt1',
               'vxsQbLcNxHDwRs3L1Ypsjf',
               '4m8w85RwfBYmtnwMFzhttx',
   			   'kzCrxCs33Y7KR2Lbx1x2x5')),
    oj_shares AS (
  SELECT 
    ra.nuggetId,
    ra.shareId,
    ra.userId,
    ra.createdAt,
    ROW_NUMBER() OVER (
      PARTITION BY ra.nuggetId, ra.userId, ra.shareId
      ORDER BY ra.createdAt
    ) AS rn
  FROM `analytics.lms_raw_analytics` ra
  JOIN public.user_details u 
    ON u.uuid = ra.userId
  WHERE ra.event IN ('sent', 'created')
    AND u.phone_number IS NOT NULL
    AND u.email IS NULL
  AND TIMESTAMP_MILLIS(CAST(u.created_at AS INT64))
    BETWEEN CAST(@{{:Joining Date Range.START}} AS TIMESTAMP)
        AND TIMESTAMP_ADD(CAST(@{{:Joining Date Range.END}} AS TIMESTAMP), INTERVAL 1 DAY)
),
     oj_share_ids AS
  (SELECT ls.nuggetId,
          ls.shareId,
          ls.userId,
          min(TIMESTAMP_ADD(ls.createdAt, INTERVAL 330 MINUTE)) AS sentAt
   FROM oj_shares ls
   WHERE rn = 1
   GROUP BY 1,
            2,
            3),
     oj_course_shares AS
  (SELECT lsi.userId,
          lsi.nuggetId AS courseId,
          lsi.shareId,
          lsi.sentAt
   FROM oj_share_ids lsi
   JOIN c ON lsi.nuggetID = c.id
   UNION ALL SELECT lsi.userId,
                    ljc.courseId,
                    lsi.shareId,
                    lsi.sentAt
   FROM oj_share_ids lsi
   JOIN public.learning_journey_courses ljc ON lsi.nuggetId = ljc.learningJourneyId
   JOIN c ON ljc.courseId = c.id),
     oj_received AS
  (SELECT ra.userId,
          ra.nuggetId,
          ra.courseId,
          ra.ljId,
          ra.shareId,
          TIMESTAMP_ADD(ra.createdAt, INTERVAL 330 MINUTE) AS receivedAt
   FROM `analytics.lms_raw_analytics` ra
   JOIN oj_share_ids lsi ON ra.userId = lsi.userId
   AND ra.nuggetId = lsi.nuggetId
   AND ra.shareId = lsi.shareId
   WHERE ra.event NOT IN ('sent',
                          'created')),
     oj_course_received AS
  (SELECT lr.userId,
          lr.nuggetId AS courseId,
          lr.shareId,
          min(lr.receivedAt) AS receivedAt
   FROM oj_received lr
   JOIN c ON lr.nuggetID = c.id
   OR lr.courseId = c.id
   GROUP BY 1,
            2,
            3
   UNION ALL SELECT lr.userId,
                    ljc.courseId,
                    lr.shareId,
                    min(lr.receivedAt) AS receivedAt
   FROM oj_received lr
   JOIN public.learning_journey_courses ljc ON lr.nuggetId = ljc.learningJourneyId
   OR lr.ljId = ljc.learningJourneyId
   OR lr.courseID = ljc.courseId
   JOIN c ON ljc.courseId = c.id
   GROUP BY 1,
            2,
            3),
     cards AS
  (SELECT l.courseId,
          lc.id AS cardId
   FROM public.lesson_cards lc
   JOIN public.lessons l ON l.id = lc.lessonId
   JOIN c ON l.courseId = c.id
   GROUP BY 1,
            2),
     course_consumed_at AS
  (SELECT ra.userId,
          ra.courseId,
          ra.shareId,
          ra.lang,
          TIMESTAMP_ADD(ra.createdAt, INTERVAL 330 MINUTE) AS consumedAt,
          row_number() OVER (PARTITION BY ra.userId,
                                          ra.nuggetId
                             ORDER BY ra.createdAt) AS rn
   FROM analytics.lms_raw_analytics ra
   JOIN oj_course_shares lcs ON ra.userId = lcs.userId
   AND ra.nuggetId = lcs.courseId
   AND ra.shareId = lcs.shareId
   WHERE ra.event = 'consumed'),
     first_course_consumed AS
  (SELECT cca.userId,
          cca.courseId,
          cca.shareId,
          cca.lang,
          cca.consumedAt
   FROM course_consumed_at cca
   WHERE rn = 1 ),
     full_progress AS
  (SELECT ra.userId,
          cards.courseId,
          cards.cardId,
          TIMESTAMP_ADD(ra.createdAt, INTERVAL 330 MINUTE) AS consumedAt,
          row_number() OVER (PARTITION BY ra.userId,
                                          ra.nuggetId
                             ORDER BY ra.createdAt) AS rn
   FROM analytics.lms_raw_analytics ra
   JOIN oj_course_shares lcs ON ra.userId = lcs.userId
   AND ra.courseId = lcs.courseId
   AND ra.shareId = lcs.shareId
   JOIN cards ON ra.nuggetId = cards.cardId
   LEFT OUTER JOIN first_course_consumed fcc ON ra.userID = fcc.userId
   AND ra.courseId = fcc.courseId
   AND ra.shareId = fcc.shareId
   WHERE ra.event = 'consumed'
     AND (fcc.consumedAt IS NULL
          OR TIMESTAMP_ADD(ra.createdAt, INTERVAL 330 MINUTE) < TIMESTAMP_ADD(fcc.consumedAt, INTERVAL 330 MINUTE))),
     progress AS
  (SELECT fp.userId,
          fp.courseId,
          count(distinct(fp.cardId)) AS consumedCount
   FROM full_progress fp
   WHERE rn = 1
   GROUP BY 1,
            2),
     quiz_cards AS
  (SELECT c.id AS courseId,
          lc.id AS quizCardId,
          array_length(json_extract_array((parse_json(lc.payload)).questions)) AS qCount,
          row_number() OVER (PARTITION BY c.id
                             ORDER BY l.seq DESC, lc.seq DESC) AS rn
   FROM public.lesson_cards lc
   JOIN public.lessons l ON lc.lessonId = l.id
   JOIN c ON l.courseId = c.id
   AND lc.type = 'quiz'
   ORDER BY c.id,
            lc.id,
            l.seq DESC, lc.seq DESC),
     final_quiz_cards AS
  (SELECT *
   FROM quiz_cards
   WHERE rn = 1),
     oj_attempt AS
  (SELECT qr.userId,
          qr.courseId,
          qr.shareId,
          qr.cardId,
          qr.questionId,
          max(attempt) AS ojAttempt
   FROM analytics.quiz_responses qr
   JOIN oj_course_shares lcs ON qr.userId = lcs.userId
   AND qr.courseId = lcs.courseId
   AND qr.shareId = lcs.shareId
   JOIN final_quiz_cards qc ON qr.courseId = qc.courseId
   AND qr.cardId = qc.quizCardId
   GROUP BY 1,
            2,
            3,
            4,
            5),
     final_scores AS
  (SELECT la.userId,
          la.courseId,
          count(distinct(CASE
                             WHEN qr.isCorrect = TRUE THEN qr.questionId
                             ELSE NULL
                         END)) / qc.qCount AS score
   FROM oj_attempt la
   JOIN analytics.quiz_responses qr ON la.userId = qr.userId
   AND la.courseId = qr.courseId
   AND la.shareId = qr.shareId
   AND la.cardId = qr.cardId
   AND la.questionId = qr.questionId
   AND la.ojAttempt = qr.attempt
   JOIN final_quiz_cards qc ON qr.courseId = qc.courseId
   AND qr.cardId = qc.quizCardId
   GROUP BY 1,
            2,
            qc.qCount),
     DATA AS
  (SELECT u.identifier AS `Staff ID`,
          u.first_name||' '||u.last_name AS `Staff Name`,
          u.phone_number AS `Phone Number`,
          case 
    when (c.name like '%Loader Onboarding%' or c.name like '%Picker Onboarding%' or c.name like '%Order Picking Simulation%') 
        then 'Day 1 - ' || c.name
    when (c.name like '%New Employee Onboarding%') 
        then 'Day 2 - ' || c.name
    when (c.name like '%SPOT%') 
        then 'Day 3 - ' || c.name
    when (c.name like '%FTR%' or c.name like '%IGCC%' or c.name like '%O2MFR%') 
        then 'Day 4 - ' || c.name
    when (c.name like '%Cycle%') 
        then 'Day 5 - ' || c.name
    else c.name 
end as `Course Name`,
           TIMESTAMP_MILLIS(CAST(u.created_at AS INT64)) AS `Joined At`,
          lcs.sentAt AS `Enrolled At`,
          CASE
              WHEN fcc.consumedAt IS NOT NULL
                   OR (c.totalCards > 0
                       AND p.consumedCount = c.totalCards) THEN 'Completed'
              WHEN c.totalCards > 0
                   AND p.consumedCount > 0
                   AND p.consumedCount < c.totalCards THEN 'In Progress'
              WHEN c.totalCards > 0
                   AND (p.consumedCount = 0
                        OR p.consumedCount IS NULL) THEN 'Not Started'
              ELSE NULL
          END AS `Status`,
          CASE
              WHEN fcc.consumedAt IS NOT NULL THEN 1
              ELSE p.consumedCount / c.totalCards
          END AS `Completion %`,
          s.score AS `Final Quiz Score`,
          fcc.consumedAt AS `Completed At`,
          upper(fcc.lang) AS `Language`,
          lcs.userID AS `User KNID`,
          lcs.courseId AS `Course KNID`,
          lcs.shareId AS `Share KNID`,
          1 AS `Enrolled`,
          CASE
              WHEN (lcr.receivedAt IS NOT NULL)
                   OR (fcc.consumedAt IS NOT NULL
                       OR (c.totalCards > 0
                           AND p.consumedCount = c.totalCards))
                   OR (c.totalCards > 0
                       AND p.consumedCount > 0
                       AND p.consumedCount < c.totalCards) THEN 1
              ELSE 0
          END AS `Logged In`,
          CASE
              WHEN fcc.consumedAt IS NOT NULL
                   OR (c.totalCards > 0
                       AND p.consumedCount = c.totalCards)
                   OR (c.totalCards > 0
                       AND p.consumedCount > 0
                       AND p.consumedCount < c.totalCards) THEN 1
              ELSE 0
          END AS `Adopted`,
          CASE
              WHEN fcc.consumedAt IS NOT NULL
                   OR (c.totalCards > 0
                       AND p.consumedCount = c.totalCards) THEN 1
              ELSE 0
          END AS `Completed`,
          u.division AS `Division`,
          u.sub_division AS `Sub Division`,
          u.is_active AS `Is Active`,
          CASE
    WHEN c.id = '3cgPTwQuwzqNu1ZmT5tNcB' THEN 1  -- Loader Onboarding Training V2 (Day 1)
    WHEN c.id = 'wtsGhTLYUKXpThHnE4A9Q6' THEN 2  -- Picker Onboarding Training V2 (Day 1)
   WHEN c.id = 'kzCrxCs33Y7KR2Lbx1x2x5'  THEN 3  -- Picker Onboarding Training V2 (Day 1)
    WHEN c.id = '4m8w85RwfBYmtnwMFzhttx' THEN 4  -- Order Picking Simulation Training - V1 (Day 1)
    WHEN c.id = 'vPD4uWQJ9Mh3Eua1XtabAy' THEN 5  -- New Employee Onboarding Training Feedback (Day 2)
    WHEN c.id = 'azwDGTkdA51Htk3ns9frSi' THEN 6  -- SPOT & REPORT (Day 3)
    WHEN c.id = 'bidvm66pkDfoZ8FrBJsgoZ' THEN 7  -- IGCC (Day 4)
    WHEN c.id = '4SFg55oeWXSiWK322YYJPD' THEN 8  -- O2MFR (Day 4)
    WHEN c.id = '7De2YCm42esCR4szqL2wt1' THEN 9  -- FTR (Day 4)
    WHEN c.id = 'vxsQbLcNxHDwRs3L1Ypsjf' THEN 10  -- Cycle Count - Loader Flow (Day 5)
    ELSE 999
END AS sort_order,
          row_number() OVER (PARTITION BY lcs.userId,
                                          lcs.courseId
                             ORDER BY lcs.sentAt) AS rn
   FROM oj_course_shares lcs
   LEFT OUTER JOIN oj_course_received lcr ON lcs.userId = lcr.userId
   AND lcs.courseId = lcr.courseId
   LEFT OUTER JOIN progress p ON lcs.userId = p.userId
   AND lcs.courseId = p.courseId
   LEFT OUTER JOIN first_course_consumed fcc ON lcs.userId = fcc.userId
   AND lcs.courseId = fcc.courseId
   LEFT OUTER JOIN final_scores s ON lcs.userId = s.userId
   AND lcs.courseId = s.courseId
   LEFT OUTER JOIN c ON lcs.courseId = c.id
   LEFT OUTER JOIN public.user_details u ON lcs.userId = u.uuid
   WHERE u.identifier IS NOT NULL)
SELECT *
FROM DATA
WHERE rn = 1
ORDER BY sort_order,
         1,
         5,
         4,
         7,
         8 DESC
```

---

## Instamart Pod Compliance  Audit Summary_Pod Compliance Audit.sql

**Tables referenced:** im.pod_compliance_audit_summary

**Original Query:**

```sql
-- Data Source: Instamart Pod Compliance  Audit Summary
-- Dashboard: Pod Compliance Audit
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:53:37
-- ============================================================

SELECT *
FROM im.pod_compliance_audit_summary
where "Audit Started At" AT TIME ZONE 'Asia/Kolkata' BETWEEN@{{:Instamart Pod Compliance Audit.Date Range.START}}::timestamp and @{{:Instamart Pod Compliance Audit.Date Range.END}}::timestamp + interval '1 day'
ORDER BY 1,
         2,
         3,
         4,
         5,
         8 DESC
```

---

## Instamart Pod Compliance Audit_Pod Compliance Audit.sql

**Tables referenced:** im.pod_compliance_audit

**Original Query:**

```sql
-- Data Source: Instamart Pod Compliance Audit
-- Dashboard: Pod Compliance Audit
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:54:46
-- ============================================================

select *
from im.pod_compliance_audit
where "Audit Started At" AT TIME ZONE 'Asia/Kolkata' BETWEEN @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
ORDER BY 1,
         2,
         3,
         4,
         5,
         8 DESC
```

---

## Instamart Pod Gate Meeting Compliance v2_Gate Meeting.sql

**Tables referenced:** fc, form_compliance_v2, form_responses, form_submissions, forms, fs, loc_q, location_acl, location_map, nuggets, organizations, question_definitions, submissions, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Instamart Pod Gate Meeting Compliance v2
-- Dashboard: Gate Meeting
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:58:09
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT regexp_replace(job_location, '([0-9]+).*', '\1') as "Pod ID"
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'All',
                              'HQ')
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid = @{{:UUIDParameter}})
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id = @{{:UUIDParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'swiggy-mart-whirlpool'),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = '-O8qdhuV9zaoXTpQiPOY'),
     fc AS
  (SELECT "Routine KNID",
          "Routine Name",
          "Location" AS "Pod",
          "Reminded At"::date AS "Date",
          count("Compliance") AS "Scheduled Count",
          sum("Compliance") AS "Adhered Count"
   FROM form_compliance_v2
   WHERE "Routine KNID" IN
       (SELECT form_knid
        FROM forms)
   and "Reminded At" BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + interval '1 day'
   GROUP BY 1,
            2,
            3,
            4),
     loc_q AS
  (SELECT nugget_id AS form_knid,
          question_id AS qid,
          question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   WHERE question_type = 'location'
   ORDER BY nugget_id,
            sqno::integer,
            created_At DESC
   LIMIT 1),
     fs AS
  (SELECT DISTINCT ON (response_id) fs.response_id,
                      sno,
                      LOCATION,
                      fs.id,
                      fs.form_id,
                      fs.submit_date + td.diff AS submitted_at
   FROM forms
   JOIN form_submissions fs ON forms.form_knid = fs.form_id
   JOIN td ON fs.organization = td.organization
   WHERE fs.submit_date + td.diff BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + interval '1 day'
   ORDER BY response_id,
            id DESC),
     submissions AS
  (SELECT fs.form_id,
          fr.response->>'name' AS pod,
                        fs.submitted_At::date AS date,
                        count(distinct(fs.response_id)) AS submission_count
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   JOIN loc_q ON fr.question_id = loc_q.qid
   AND fs.form_id = loc_q.form_knid
   GROUP BY 1,
            2,
            3),
     location_map AS
  (SELECT "Region",
          "City",
          regexp_replace("Pod", '([0-9]+).*', '\1') AS "Pod ID"
   FROM
     (SELECT division AS "Region",
             sub_division AS "City",
             job_lOCATION AS "Pod",
             row_number() OVER (PARTITION BY division,
                                             sub_division,
                                             job_location
                                ORDER BY created_At DESC) rn
      FROM user_details
      WHERE job_location ~ '^\d{3}'
        AND is_active = TRUE) base
   WHERE rn = 1)
SELECT fc."Routine KNID",
       fc."Routine Name",
	   fc."Date",
       lm."Region",
       lm."City",
       fc."Pod",
       regexp_replace(fc."Pod", '([0-9]+).*', '\1') AS "Pod ID",
       fc."Scheduled Count",
       fc."Adhered Count",
       case when s.submission_count is null then 0 else s.submission_count end AS "Submitted Count"
FROM fc
LEFT OUTER JOIN submissions s ON fc."Routine KNID" = s.form_id
AND regexp_replace(fc."Pod", '([0-9]+).*', '\1') = regexp_replace(s.pod, '([0-9]+).*', '\1')
AND fc."Date" = s.date
LEFT OUTER JOIN location_map lm ON regexp_replace(fc."Pod", '([0-9]+).*', '\1') = lm."Pod ID"
join location_acl on regexp_replace(fc."Pod", '([0-9]+).*', '\1') = location_acl."Pod ID"
ORDER BY 2,
         3,
         4,
		 5,
         7
```

---

## Instamart Pod Gate Meeting_Pod Gate Meeting.sql

**Tables referenced:** DATA, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_map, metadata, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, user_Details

**Columns needing snake_case conversion:**

- `endDate` -> `end_date` (alias: `end_date AS "endDate"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `startDate` -> `start_date` (alias: `start_date AS "startDate"`)


**Original Query:**

```sql
-- Data Source: Instamart Pod Gate Meeting
-- Dashboard: Pod Gate Meeting
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:58:12
-- ============================================================

WITH forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = @{{:formId}}),
     qd_non_table_non_logic AS
  (SELECT nugget_id AS form_knid,
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
          question AS parent_question,
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
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::integer*10000+(def.value->>'order')::integer AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          def.key AS qid,
          def.value->>'question_type' AS q_type,
                      def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
     qd_table AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::integer*10000+(def.value->>'order')::integer AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
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
  (SELECT DISTINCT ON (response_id) form_submissions.*,
                      form_name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   where form_submissions.submit_date at time zone 'Asia/Kolkata' between @{{:startDate}}::timestamp and @{{:endDate}}::timestamp + interval '1 day'
   ORDER BY response_id,
            id DESC),
     fr AS
  (SELECT form_submit_id,
          form_id,
          form_name,
          sno,
          submit_date,
          user_id,
          response_id,
          question_id AS parent_qid,
          question_id AS qid,
          question_type,
          response,
          1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                form_name,
                sno,
                submit_date,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                question_type,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             form_id,
             form_name,
             sno,
             submit_date,
             user_id,
             response_id,
             question_id,
             question_type,
             base.value,
             base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
     metadata AS
  (SELECT form_name,
          fd.form_knid,
          fr.response_id,
          fr.sno,
          fr.submit_date AT TIME ZONE 'Asia/Kolkata' AS submit_date,
                                      fr.response ->> 'name'AS pod
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   WHERE fd.q_type = 'location'
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6
   ORDER BY 1,
            5),
     DATA AS
  (SELECT fr.response_id,
          fd.question,
          OPTION->>0 as option
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid,
              jsonb_array_elements(fr.response->'selected') AS OPTION
   WHERE fd.q_type = 'checkboxes'
   GROUP BY 1,
            2,
            3
   ORDER BY 1,
            2,
            3), location_map AS
  (SELECT DISTINCT ON (division,
                       sub_division,
                       regexp_replace(job_location, '([0-9]+).*', '\1')) division AS region,
                      sub_division AS city,
                      regexp_replace(job_location, '([0-9]+).*', '\1') AS pod
   FROM user_Details
   WHERE (regexp_replace(job_location, '([0-9]+).*', '\1') IS NOT NULL
          OR regexp_replace(job_location, '([0-9]+).*', '\1') != '')
     AND is_active = TRUE
   ORDER BY 1,
            2,
            3,
            created_at DESC)
SELECT md.form_name AS "Form",
       md.form_knid AS "Form KNID",
       md.response_id AS "Submission KNID",
       md.sno AS "Submission No",
       md.submit_date AS "Submitted At",
       initcap(lm.region) AS "Region",
       initcap(lm.city) AS "City",
       lm.pod AS "Pod",
       initcap(md.pod) AS "Pod Name",
       d.question AS "Question",
       d.option AS "Topic Covered"
FROM metadata md
JOIN DATA d ON md.response_id = d.response_id
LEFT OUTER JOIN location_map lm ON regexp_replace(md.pod, '([0-9]+).*', '\1') = lm.pod
ORDER BY 1,
         6,
         7,
         8,
         5 DESC
```

---

## Instamart Pod P4W Routine Compliance_P4W Routine Compliance.sql

**Tables referenced:** form_reminders, form_responses, form_submissions, fr, fs, lfr, lfr.reminded_at, lm, location_form_reminders, locations, nuggets

**Original Query:**

```sql
-- Data Source: Instamart Pod P4W Routine Compliance
-- Dashboard: P4W Routine Compliance
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:57:57
-- ============================================================

WITH lm AS
  (SELECT '1113109' AS pod_id,
          'Antopehill' AS pod_name,
          'West' AS CLUSTER,
          'Mumbai' AS city,
          'durvesh.gholap@swiggy.in' AS com,
          'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1396283' AS pod_id,
                'Byculla' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1385841' AS pod_id,
                'Century Bazaar' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1135722' AS pod_id,
                'Chowpatty' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1383130' AS pod_id,
                'Dhobi Talao' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1295148' AS pod_id,
                'Juhu' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1396295' AS pod_id,
                'Sion East' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1396282' AS pod_id,
                'Tardeo Police Station' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1311101' AS pod_id,
                'Wadala' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '810366' AS pod_id,
                'Andheri East' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'manoj.gahlot@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '969383' AS pod_id,
                'Bandra West' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'manoj.gahlot@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1062417' AS pod_id,
                'Dadar' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'manoj.gahlot@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1392531' AS pod_id,
                'Lower Parel' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'manoj.gahlot@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1381967' AS pod_id,
                'Mahim' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'manoj.gahlot@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1390224' AS pod_id,
                'Model Colony Mumbai' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'manoj.gahlot@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1397051' AS pod_id,
                'Vile Parle' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'manoj.gahlot@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1384969' AS pod_id,
                'Chandivali' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sagar.kudtarkar@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1238358' AS pod_id,
                'Jvlr' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sagar.kudtarkar@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1391897' AS pod_id,
                'Postal Colony Chembur' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sagar.kudtarkar@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1135720' AS pod_id,
                'Powai2' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sagar.kudtarkar@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1387703' AS pod_id,
                'Rk Studios' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sagar.kudtarkar@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '649837' AS pod_id,
                'Kalina' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sagar.kudtarkar@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1335483' AS pod_id,
                'Seawoods (Navi Mumbai)' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sagar.kudtarkar@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1380622' AS pod_id,
                'Seven Hills' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sagar.kudtarkar@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1383573' AS pod_id,
                'Shiravane' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sagar.kudtarkar@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1382256' AS pod_id,
                'Gokuldham' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shadab.husain@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1135721' AS pod_id,
                'Goregaon_2' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shadab.husain@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1239162' AS pod_id,
                'Inorbit Mall Malad West' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shadab.husain@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1190779' AS pod_id,
                'Kandivali East' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shadab.husain@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1231809' AS pod_id,
                'Malad West' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shadab.husain@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1388686' AS pod_id,
                'Pragati Nagar' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shadab.husain@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1382439' AS pod_id,
                'Thakur Village' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shadab.husain@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1314371' AS pod_id,
                'Vasai Virar' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shadab.husain@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '810365' AS pod_id,
                'Versova' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1319696' AS pod_id,
                'Bandra West (Khar)' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1238359' AS pod_id,
                'Lokhandwala' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1382657' AS pod_id,
                'Oshiwara' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1190780' AS pod_id,
                'Vileparle' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1295147' AS pod_id,
                'Vileparle East' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1381561' AS pod_id,
                'Hawaiian Village' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sonuaniruddh.sahani@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1396296' AS pod_id,
                'Hiranandani Mbc Park' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sonuaniruddh.sahani@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1381443' AS pod_id,
                'Majiwada' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sonuaniruddh.sahani@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1181694' AS pod_id,
                'Thane2' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sonuaniruddh.sahani@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1267915' AS pod_id,
                'Thane Hiranandani Estate' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sonuaniruddh.sahani@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1336659' AS pod_id,
                'Thane West' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sonuaniruddh.sahani@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1381643' AS pod_id,
                'Uthalsar' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sonuaniruddh.sahani@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '929911' AS pod_id,
                'Yojit Estates' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sonuaniruddh.sahani@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1084119' AS pod_id,
                'Belapur' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1389632' AS pod_id,
                'Gaothan' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1385645' AS pod_id,
                'Ghansoli' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1381966' AS pod_id,
                'Indira Nagar' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1082435' AS pod_id,
                'Kharghar' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1380959' AS pod_id,
                'Nmims Navi Mumbai' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1238356' AS pod_id,
                'Panvel' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1388688' AS pod_id,
                'Sanpada' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1386846' AS pod_id,
                'Taloja Jail Road' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1381500' AS pod_id,
                'Telecom Factory' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1398445' AS pod_id,
                'Vashi' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1388687' AS pod_id,
                'Bhayander' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'tejas.shetty@scootsy.com' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '762615' AS pod_id,
                'Borivali' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'tejas.shetty@scootsy.com' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1237261' AS pod_id,
                'Borivali East' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'tejas.shetty@scootsy.com' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1062418' AS pod_id,
                'Dahisar West' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'tejas.shetty@scootsy.com' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1237262' AS pod_id,
                'Kandivali West' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'tejas.shetty@scootsy.com' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1346590' AS pod_id,
                'Mira Hubtown' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'tejas.shetty@scootsy.com' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1230883' AS pod_id,
                'Oberoi Mall' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'tejas.shetty@scootsy.com' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1381833' AS pod_id,
                'Unique Gardens' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'tejas.shetty@scootsy.com' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1390223' AS pod_id,
                'Chikan Ghar' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1381834' AS pod_id,
                'Container Yard' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1062416' AS pod_id,
                'Ghatkopar East' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1388387' AS pod_id,
                'Kalyan East' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1386534' AS pod_id,
                'Katai Pipeline Road' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1395728' AS pod_id,
                'Katai Village' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '788745' AS pod_id,
                'Bhandup' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1278165' AS pod_id,
                'Mulund West' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1298955' AS pod_id,
                'Rcity Mall, Ghatkopar West' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1238357' AS pod_id,
                'Sagarli Gaon' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '810367' AS pod_id,
                'Vikhroli' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1398760' AS pod_id,
                'Matunga East' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                '' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1383571' AS pod_id,
                'Arhat Bazaar' AS pod_name,
                'North' AS CLUSTER,
                'Dehradun' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1393569' AS pod_id,
                'Doon It Park' AS pod_name,
                'North' AS CLUSTER,
                'Dehradun' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1391903' AS pod_id,
                'Isbt' AS pod_name,
                'North' AS CLUSTER,
                'Dehradun' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1381970' AS pod_id,
                'Jakhan' AS pod_name,
                'North' AS CLUSTER,
                'Dehradun' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1388685' AS pod_id,
                'Jogiwala' AS pod_name,
                'North' AS CLUSTER,
                'Dehradun' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1388316' AS pod_id,
                'Karanpur' AS pod_name,
                'North' AS CLUSTER,
                'Dehradun' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1394449' AS pod_id,
                'Saharanpur Road' AS pod_name,
                'North' AS CLUSTER,
                'Dehradun' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1398750' AS pod_id,
                'Ashok Vihar' AS pod_name,
                'North' AS CLUSTER,
                'Kanpur' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1398751' AS pod_id,
                'Kakadeo' AS pod_name,
                'North' AS CLUSTER,
                'Kanpur' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1397090' AS pod_id,
                'Geeta Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Kanpur' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1398443' AS pod_id,
                'Antas Mall' AS pod_name,
                'North' AS CLUSTER,
                'Lucknow' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1309583' AS pod_id,
                'Ashiana Road' AS pod_name,
                'North' AS CLUSTER,
                'Lucknow' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1339714' AS pod_id,
                'Jankipuram' AS pod_name,
                'North' AS CLUSTER,
                'Lucknow' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1398442' AS pod_id,
                'Lucknow High Court' AS pod_name,
                'North' AS CLUSTER,
                'Lucknow' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1347753' AS pod_id,
                'Nadan Mahal Road' AS pod_name,
                'North' AS CLUSTER,
                'Lucknow' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1382963' AS pod_id,
                'Sector-C' AS pod_name,
                'North' AS CLUSTER,
                'Lucknow' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1397032' AS pod_id,
                'South City' AS pod_name,
                'North' AS CLUSTER,
                'Lucknow' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1394452' AS pod_id,
                'Chetganj' AS pod_name,
                'North' AS CLUSTER,
                'Varanasi' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1396292' AS pod_id,
                'Naria' AS pod_name,
                'North' AS CLUSTER,
                'Varanasi' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1388388' AS pod_id,
                'Alpha 1' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'bhuvaneshwar.kumar@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1384147' AS pod_id,
                'Baraula' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'bhuvaneshwar.kumar@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1385647' AS pod_id,
                'Felix Hospital' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'bhuvaneshwar.kumar@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '406773' AS pod_id,
                'Sec46' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'bhuvaneshwar.kumar@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1386387' AS pod_id,
                'Sec 132' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'bhuvaneshwar.kumar@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1388200' AS pod_id,
                'Sec 50 B Block' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'bhuvaneshwar.kumar@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1397625' AS pod_id,
                'Noida Expressway' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'bhuvaneshwar.kumar@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1389634' AS pod_id,
                'Gaur City 2' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'farukh.1@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1383251' AS pod_id,
                'Cisf' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'farukh.1@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1390227' AS pod_id,
                'Eco City' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'farukh.1@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1386450' AS pod_id,
                'Gda Market Vaishali' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'farukh.1@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1385946' AS pod_id,
                'Jaipuria Mall' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'farukh.1@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1383133' AS pod_id,
                'Sector 59' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'farukh.1@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1388198' AS pod_id,
                'Sector 62' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'farukh.1@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1387080' AS pod_id,
                'Pvr Vvip Ghaziabad' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'rahul.singh02@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1394453' AS pod_id,
                'Raj Nagar Gzb' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'rahul.singh02@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1387081' AS pod_id,
                'Tech Zone 4' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'rahul.singh02@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1398130' AS pod_id,
                'Hazipur Sector 104' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'rahul.singh02@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1386943' AS pod_id,
                'Mayur Vihar Phase 3' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'rahul.singh02@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1388531' AS pod_id,
                'Sector 122' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'rahul.singh02@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1383134' AS pod_id,
                'Sector 44' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'rahul.singh02@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1382167' AS pod_id,
                'Sector 76' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'rahul.singh02@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1395430' AS pod_id,
                'Sector 9' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'rahul.singh02@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1390221' AS pod_id,
                'Chrompet 1' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'balaji.p1@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1390222' AS pod_id,
                'George Town' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'balaji.p1@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1398439' AS pod_id,
                'Jawahar Nagar' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'balaji.p1@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1150192' AS pod_id,
                'Mylapores' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'balaji.p1@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386091' AS pod_id,
                'Nolambur New' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'balaji.p1@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '854384' AS pod_id,
                'Pallavaram' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'balaji.p1@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386974' AS pod_id,
                'Pursaiwakam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'balaji.p1@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1237710' AS pod_id,
                'Villivakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'balaji.p1@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386264' AS pod_id,
                'Tambaram/ Tambaram West' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'karthick.r2@scootsy.com' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1397045' AS pod_id,
                'Sreekaryam' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thiruvananthapuram' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1394675' AS pod_id,
                'Kazhakootam' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thiruvananthapuram' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1381968' AS pod_id,
                'Kulathoor' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thiruvananthapuram' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1382059' AS pod_id,
                'Palayam' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thiruvananthapuram' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1387569' AS pod_id,
                'Poojappura' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thiruvananthapuram' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1388389' AS pod_id,
                'Sasthamangalam' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thiruvananthapuram' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1396291' AS pod_id,
                'Sreekaryam' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thiruvananthapuram' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1394676' AS pod_id,
                'Thampanoor' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thiruvananthapuram' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1395734' AS pod_id,
                'NehruNagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thrissur' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1395735' AS pod_id,
                'Punkunnam' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thrissur' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1387907' AS pod_id,
                'Ambatur' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1382426' AS pod_id,
                'Anna Nagar Main' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1393566' AS pod_id,
                'Ayappanthangal' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '836516' AS pod_id,
                'Ekkatuthungul' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386449' AS pod_id,
                'Manapakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1393567' AS pod_id,
                'Poonamalee' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386266' AS pod_id,
                'Porur' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1396287' AS pod_id,
                'Puthagaram' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1380670' AS pod_id,
                'Vijaya Nagar' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1230880' AS pod_id,
                'Virugambakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1398449' AS pod_id,
                'Rockfort' AS pod_name,
                'TN' AS CLUSTER,
                'Trichy' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1381276' AS pod_id,
                'Alandur' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'pandiyarajan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1002694' AS pod_id,
                'Kovilambakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'pandiyarajan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1394671' AS pod_id,
                'Kuberan Nagar' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'pandiyarajan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1381753' AS pod_id,
                'Madambakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'pandiyarajan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1389252' AS pod_id,
                'Pammal' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'pandiyarajan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1397026' AS pod_id,
                'Parasakthi nagar' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'pandiyarajan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1349401' AS pod_id,
                'Raghava Nagar' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'pandiyarajan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1393568' AS pod_id,
                'Urapakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'pandiyarajan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1397630' AS pod_id,
                'Velachery' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'pandiyarajan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1265810' AS pod_id,
                'Balaji Nagar' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1388683' AS pod_id,
                'Kotivakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '810362' AS pod_id,
                'Perungudi 2' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386941' AS pod_id,
                'T Nagar' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1369819' AS pod_id,
                'Thiruvanmiyur' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1237711' AS pod_id,
                'Peelamedu' AS pod_name,
                'TN' AS CLUSTER,
                'Coimbatore' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1388684' AS pod_id,
                'Rs Puram Main' AS pod_name,
                'TN' AS CLUSTER,
                'Coimbatore' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1383850' AS pod_id,
                'Saibaba Colony' AS pod_name,
                'TN' AS CLUSTER,
                'Coimbatore' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1397027' AS pod_id,
                'Saravanampatti' AS pod_name,
                'TN' AS CLUSTER,
                'Coimbatore' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1396288' AS pod_id,
                'Singanallur' AS pod_name,
                'TN' AS CLUSTER,
                'Coimbatore' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1392529' AS pod_id,
                'Trichy Link Road' AS pod_name,
                'TN' AS CLUSTER,
                'Coimbatore' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1395426' AS pod_id,
                'Alwarpet' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'shivaraj.j@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1383824' AS pod_id,
                'Karapakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'shivaraj.j@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1385476' AS pod_id,
                'Medavakkam New' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'shivaraj.j@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386813' AS pod_id,
                'Mogappair East' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'shivaraj.j@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386448' AS pod_id,
                'Tirumurthy Nagar' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'shivaraj.j@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '969381' AS pod_id,
                'Vadapalani' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'shivaraj.j@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1389007' AS pod_id,
                'Lawspet' AS pod_name,
                'TN' AS CLUSTER,
                'Pondicherry' AS city,
                'shivaraj.j@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1392533' AS pod_id,
                'Mudaliarpet' AS pod_name,
                'TN' AS CLUSTER,
                'Pondicherry' AS city,
                'shivaraj.j@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1393570' AS pod_id,
                'Aluva' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386092' AS pod_id,
                'Infopark' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1393018' AS pod_id,
                'Kacheripady' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1383382' AS pod_id,
                'Kakkanad' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386715' AS pod_id,
                'Kaloor' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1387563' AS pod_id,
                'Padivattom' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1382427' AS pod_id,
                'Peeta Metro Station' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1381849' AS pod_id,
                'Perumanoor' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1397629' AS pod_id,
                'Ponekkara' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1319695' AS pod_id,
                'Thengod' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1381277' AS pod_id,
                'Vidya Nagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1397030' AS pod_id,
                'Govindapuram' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kozhikode' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1396290' AS pod_id,
                'Velliparamba' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kozhikode' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1388451' AS pod_id,
                'West Hills' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kozhikode' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1380531' AS pod_id,
                'Kelambakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1381832' AS pod_id,
                'Natham' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1385475' AS pod_id,
                'Padur' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1388138' AS pod_id,
                'Perumbakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1395723' AS pod_id,
                'Rajakilpakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1391892' AS pod_id,
                'Semmencheri' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386267' AS pod_id,
                'Sholinganallur' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386265' AS pod_id,
                'Thuraipakam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1395732' AS pod_id,
                'Alagapuram' AS pod_name,
                'TN' AS CLUSTER,
                'Salem' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1398447' AS pod_id,
                'Gugai' AS pod_name,
                'TN' AS CLUSTER,
                'Salem' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1336431' AS pod_id,
                'Airoli' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'jeetendra.tiwari@swiggy.in' AS dch
   UNION SELECT '592956' AS pod_id,
                'Alwal' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1398441' AS pod_id,
                'AMR Planet' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1396289' AS pod_id,
                'Anand Bagh' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '988469' AS pod_id,
                'A.S Rao Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1396294' AS pod_id,
                'Boduppal' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1155153' AS pod_id,
                'Bowenpally' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1388385' AS pod_id,
                'Damaiguda' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1388312' AS pod_id,
                'Kompally' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '816649' AS pod_id,
                'Tarnaka' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1393828' AS pod_id,
                'West Marredpally' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1381355' AS pod_id,
                'Barkatpura' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'mogili.reddy@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1385839' AS pod_id,
                'Gangaputra Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'Mogili.reddy@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1382255' AS pod_id,
                'Musheerabad' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'Mogili.reddy@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1386716' AS pod_id,
                'New Bolarum' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'Mogili.reddy@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1237254' AS pod_id,
                'Yapral' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'Mogili.reddy@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1388311' AS pod_id,
                'Aparna Hill Park' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'mohammed.abdul@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1387634' AS pod_id,
                'Beeramguda' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'mohammed.abdul@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1380712' AS pod_id,
                'Botanical Garden' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'mohammed.abdul@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1381356' AS pod_id,
                'Hitech City' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'mohammed.abdul@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '737088' AS pod_id,
                'Madhapur' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'mohammed.abdul@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1385563' AS pod_id,
                'Nanakaramguda (Relocation)' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'mohammed.abdul@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1396027' AS pod_id,
                'Pragathi Nagar Phase 1' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'mohammed.abdul@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1084118' AS pod_id,
                'Puppalaguda2' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'mohammed.abdul@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1381278' AS pod_id,
                'Chinthal' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '587699' AS pod_id,
                'Gcw' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1061926' AS pod_id,
                'Kondapur' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1223630' AS pod_id,
                'Kondapur-2' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1386094' AS pod_id,
                'Kothaguda' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1397057' AS pod_id,
                'Madhapur' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '810364' AS pod_id,
                'Miyapur' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1181691' AS pod_id,
                'Nizampet5' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1386717' AS pod_id,
                'Suchitra' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1386269' AS pod_id,
                'Tcs Synergy Park' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1387564' AS pod_id,
                'Bachupally 2' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1381160' AS pod_id,
                'Gopanpally' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1261840' AS pod_id,
                'Hafeezpet' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1383129' AS pod_id,
                'Kukatpally' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1237255' AS pod_id,
                'Nalagandla' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1082432' AS pod_id,
                'Nizampet4' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1238352' AS pod_id,
                'Nizampet 6' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1389637' AS pod_id,
                'Pjr Layout' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1393827' AS pod_id,
                'Satadar Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1386815' AS pod_id,
                'Tellapur' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1386093' AS pod_id,
                'Venkata Ramana Colony' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1386816' AS pod_id,
                'Attapur' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1391894' AS pod_id,
                'B N Reddy Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1387078' AS pod_id,
                'Bandlaguda' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1398749' AS pod_id,
                'Chanchalguda' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1311100' AS pod_id,
                'Charminar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1392530' AS pod_id,
                'Chintalkunta' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1181692' AS pod_id,
                'Kharmanghat_Kothapet_2' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1295144' AS pod_id,
                'Kodandaram Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '762613' AS pod_id,
                'Kothapet' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1397628' AS pod_id,
                'Mahesh Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1238351' AS pod_id,
                'New Malakpet' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1380523' AS pod_id,
                'Abhyudaya Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'tattikota.kumar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1396293' AS pod_id,
                'Alkapuri Township' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'tattikota.kumar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1382981' AS pod_id,
                'Arvind Nagar Colony' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'tattikota.kumar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1386268' AS pod_id,
                'Datar Manzil' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'tattikota.kumar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1387566' AS pod_id,
                'Narsinghi' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'tattikota.kumar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1223632' AS pod_id,
                'Puppalaguda-3' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'tattikota.kumar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1398453' AS pod_id,
                'Sheikpet' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'tattikota.kumar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1386533' AS pod_id,
                'Vikas Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'tattikota.kumar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1387565' AS pod_id,
                'Waverock' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'tattikota.kumar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1389688' AS pod_id,
                'Allwyn Colony' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1380448' AS pod_id,
                'Balkampet' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1385944' AS pod_id,
                'Habsiguda' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1383572' AS pod_id,
                'Jublee Hills Checkpost' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1389638' AS pod_id,
                'Kalpataru' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '988472' AS pod_id,
                'Lakdikapul' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1382391' AS pod_id,
                'Masjid Banda' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1267913' AS pod_id,
                'Mithila Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1229994' AS pod_id,
                'Punjagutta' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1155152' AS pod_id,
                'Secunderabad-2' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '886521' AS pod_id,
                'Yosufguda' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1380621' AS pod_id,
                'Beck Bagan' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'abhishek.das1@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1169284' AS pod_id,
                'Haltu 1' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'abhishek.das1@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1384141' AS pod_id,
                'Itc Topsia' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'abhishek.das1@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1385840' AS pod_id,
                'Kasba' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'abhishek.das1@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1391896' AS pod_id,
                'Manicktala' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'abhishek.das1@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1384877' AS pod_id,
                'Satgram' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'abhishek.das1@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1135719' AS pod_id,
                'Tartala' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'abhishek.das1@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '901840' AS pod_id,
                'Tollygunge' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'abhishek.das1@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1396286' AS pod_id,
                'Bapuji Nagar' AS pod_name,
                'East' AS CLUSTER,
                'Bhubaneswar' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1389257' AS pod_id,
                'District Centre' AS pod_name,
                'East' AS CLUSTER,
                'Bhubaneswar' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1391904' AS pod_id,
                'Kiit' AS pod_name,
                'East' AS CLUSTER,
                'Bhubaneswar' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1237258' AS pod_id,
                'Garia' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1380524' AS pod_id,
                'Golf Green' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1167234' AS pod_id,
                'Haltu 2' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1388313' AS pod_id,
                'Lake Town' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1386270' AS pod_id,
                'Patuli' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1314370' AS pod_id,
                'Rajpur Sonapur' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1386096' AS pod_id,
                'Tiljala' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '867467' AS pod_id,
                'Ultadanga' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1395725' AS pod_id,
                '45 Pally' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sohrab.ahmad@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1387079' AS pod_id,
                'Jagdishpur' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sohrab.ahmad@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1386097' AS pod_id,
                'Mani Square' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sohrab.ahmad@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1237259' AS pod_id,
                'New Town' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sohrab.ahmad@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1391895' AS pod_id,
                'Purabanchal' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sohrab.ahmad@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1387910' AS pod_id,
                'Rajarhat' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sohrab.ahmad@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '867466' AS pod_id,
                'Arjunpur' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1373486' AS pod_id,
                'Eco Park (New Town)' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1389000' AS pod_id,
                'Madhyamgram' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1382982' AS pod_id,
                'Manickpore' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1386913' AS pod_id,
                'Nagerbazar' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1395726' AS pod_id,
                'Rathtala' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1388197' AS pod_id,
                'Salt Lake Sector V' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1397622' AS pod_id,
                'Sinthi' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1382353' AS pod_id,
                'Talbagan' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1395730' AS pod_id,
                'Kadru' AS pod_name,
                'East' AS CLUSTER,
                'Ranchi' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1397024' AS pod_id,
                'Bagaluru Road' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1382164' AS pod_id,
                'Bellahalli' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1396660' AS pod_id,
                'Bhartiya City' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '762611' AS pod_id,
                'Rk Hegde Nagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1390217' AS pod_id,
                'Kyalasanahalli' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1382656' AS pod_id,
                'Nagavara' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1386386' AS pod_id,
                'Puttanahalli' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1393565' AS pod_id,
                'Singapura' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '565140' AS pod_id,
                'Ylk' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1386712' AS pod_id,
                'Yelahanka New Town' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1387633' AS pod_id,
                'Cooke Town' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'rajat.jaiswal1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1382412' AS pod_id,
                'Dasappa Layout' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'rajat.jaiswal1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '816648' AS pod_id,
                'Ulsoor' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'rajat.jaiswal1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1386532' AS pod_id,
                'Hbr Layout' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'rajat.jaiswal1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1390218' AS pod_id,
                'Hrbr Layout' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'rajat.jaiswal1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1395722' AS pod_id,
                'Murgesh palya' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'rajat.jaiswal1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1394669' AS pod_id,
                'P and T Layout' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'rajat.jaiswal1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1313712' AS pod_id,
                'Shivaji Nagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'rajat.jaiswal1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1385942' AS pod_id,
                'Thigalarapalya' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'rajat.jaiswal1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '788742' AS pod_id,
                'Banashankari' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'sangamesh.k@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '911032' AS pod_id,
                'Chamrajpet 1' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'sangamesh.k@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1380899' AS pod_id,
                'Hoshalli Extension' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'sangamesh.k@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1190778' AS pod_id,
                'Indiranagar 5' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'sangamesh.k@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1237709' AS pod_id,
                'Kumaraswamy Layout' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'sangamesh.k@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '911033' AS pod_id,
                'Laggere' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'sangamesh.k@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1396285' AS pod_id,
                'RR Nagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'sangamesh.k@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1387077' AS pod_id,
                'Uttarahalli' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'sangamesh.k@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1390219' AS pod_id,
                'Vajrahalli' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'sangamesh.k@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1380898' AS pod_id,
                'Bt Purshottam Layout' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'wilsonpeter.g@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1238349' AS pod_id,
                'Horamavu' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'wilsonpeter.g@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1082430' AS pod_id,
                'Kalyan Nagar 5' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'wilsonpeter.g@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1373485' AS pod_id,
                'Kr Puram' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'wilsonpeter.g@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1381969' AS pod_id,
                'Lingarajapuram' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'wilsonpeter.g@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '593243' AS pod_id,
                'Kng2' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'wilsonpeter.g@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1394670' AS pod_id,
                'Sobha Garrison' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'wilsonpeter.g@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1381559' AS pod_id,
                'Vivekananda Nagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'wilsonpeter.g@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1396467' AS pod_id,
                'Yeshwantpur' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'wilsonpeter.g@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1395427' AS pod_id,
                'Brindavan Gardens' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Guntur' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1394684' AS pod_id,
                'Medical College' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Guntur' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1398748' AS pod_id,
                'Gorantla' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Guntur' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1382259' AS pod_id,
                'Autonagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vijayawada' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1387707' AS pod_id,
                'Bhavanipuram' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vijayawada' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1388390' AS pod_id,
                'Labipet' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vijayawada' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1399348' AS pod_id,
                'Mytri Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vijayawada' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1382660' AS pod_id,
                'Payakapuram' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vijayawada' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1391901' AS pod_id,
                'Ramavarapadu' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vijayawada' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1398450' AS pod_id,
                'Tadepalle' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vijayawada' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1395433' AS pod_id,
                'Public Garden' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Warangal' AS city,
                'mohammed.abdul@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1382440' AS pod_id,
                'Dwarka Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vizag' AS city,
                'thigutla.srinath@scootsy.com' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1388113' AS pod_id,
                'Madhurwada' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vizag' AS city,
                'thigutla.srinath@scootsy.com' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1381358' AS pod_id,
                'Mvp Double Road' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vizag' AS city,
                'thigutla.srinath@scootsy.com' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1345681' AS pod_id,
                'Nad Junction' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vizag' AS city,
                'thigutla.srinath@scootsy.com' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1309584' AS pod_id,
                'Nawab Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vizag' AS city,
                'thigutla.srinath@scootsy.com' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1395432' AS pod_id,
                'TPT Colony' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vizag' AS city,
                'thigutla.srinath@scootsy.com' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1398448' AS pod_id,
                'VK Puram' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Tirupati' AS city,
                'thigutla.srinath@scootsy.com ' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1397621' AS pod_id,
                'Alwal' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                '' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1388112' AS pod_id,
                'Beml' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '565139' AS pod_id,
                'Cvr' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1388682' AS pod_id,
                'Guttahalli' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1231805' AS pod_id,
                'Hebbal' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1393563' AS pod_id,
                'Kaggadasapura' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1382868' AS pod_id,
                'Nanjappa Circle' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1229990' AS pod_id,
                'Sahakar Nagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '816646' AS pod_id,
                'Sanjay Nagar 1' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1216213' AS pod_id,
                'Sanjay Nagar 5' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '969380' AS pod_id,
                'Sanjay Nagar 3' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1384788' AS pod_id,
                'Balagere' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'hariprasad.a@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1392080' AS pod_id,
                'Bda Complex Hsr' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'hariprasad.a@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '788740' AS pod_id,
                'Krg3' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'hariprasad.a@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1113105' AS pod_id,
                'Hsr 2' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'hariprasad.a@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1231052' AS pod_id,
                'Hsr 3' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'hariprasad.a@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1386090' AS pod_id,
                'Hsr Sec 2' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'hariprasad.a@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1387562' AS pod_id,
                'Panathur' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'hariprasad.a@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1395720' AS pod_id,
                'Somasoundarapalya' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'hariprasad.a@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1387560' AS pod_id,
                'Anantnagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1239157' AS pod_id,
                'Begur' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1385835' AS pod_id,
                'Beratena Agrahara' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1393562' AS pod_id,
                'DLF Woodland' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1388681' AS pod_id,
                'Hulimavu' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1382870' AS pod_id,
                'Mylasandra' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1384787' AS pod_id,
                'Neeladri Nagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1380710' AS pod_id,
                'Rayasandra' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1381848' AS pod_id,
                'Vinayaka Nagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1398444' AS pod_id,
                'Attavar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Mangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1394683' AS pod_id,
                'Kottara' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Mangaluru' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1386098' AS pod_id,
                'Chamundi Temple' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Mysore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1397623' AS pod_id,
                'Mysore East' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Mysore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1395429' AS pod_id,
                'Mysore University' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Mysore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1239166' AS pod_id,
                'Vani Vilas' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Mysore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1374258' AS pod_id,
                'Bhoganhalli (Kadubeesanahalli)' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'shaik.mansoor2@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1392421' AS pod_id,
                'CARMELARAM' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'shaik.mansoor2@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1382707' AS pod_id,
                'Gottigere' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'shaik.mansoor2@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1392660' AS pod_id,
                'Haralur Megapod' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'shaik.mansoor2@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1385836' AS pod_id,
                'Kasavanahalli' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'shaik.mansoor2@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1381157' AS pod_id,
                'Mullur' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'shaik.mansoor2@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1386714' AS pod_id,
                'Orr - Rmz' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'shaik.mansoor2@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1387903' AS pod_id,
                'Salapuria Sancity' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'shaik.mansoor2@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '854382' AS pod_id,
                'Sarjapur 2' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'shaik.mansoor2@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1382494' AS pod_id,
                'Jangpura' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lallan.prasad@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1383851' AS pod_id,
                'Lodi Colony' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lallan.prasad@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1394450' AS pod_id,
                'Mehroli' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lallan.prasad@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1387704' AS pod_id,
                'Nfc' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lallan.prasad@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '810368' AS pod_id,
                'Munirika' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lallan.prasad@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1391898' AS pod_id,
                'Gur Mandi' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lokesh.punia@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1062419' AS pod_id,
                'Karol Bagh2' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lokesh.punia@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1229997' AS pod_id,
                'Patel Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lokesh.punia@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1062023' AS pod_id,
                'Rohini' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lokesh.punia@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1388196' AS pod_id,
                'Adarsh Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Jaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1382290' AS pod_id,
                'Bani Park' AS pod_name,
                'North' AS CLUSTER,
                'Jaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1382166' AS pod_id,
                'Krishna Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Jaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1346769' AS pod_id,
                'Lalkothi' AS pod_name,
                'North' AS CLUSTER,
                'Jaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1381754' AS pod_id,
                'Mansarovar' AS pod_name,
                'North' AS CLUSTER,
                'Jaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1387909' AS pod_id,
                'Ns Road' AS pod_name,
                'North' AS CLUSTER,
                'Jaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1386095' AS pod_id,
                'Patrika Gate' AS pod_name,
                'North' AS CLUSTER,
                'Jaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1395724' AS pod_id,
                'Pratap Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Jaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1398451' AS pod_id,
                'Pahada' AS pod_name,
                'North' AS CLUSTER,
                'Udaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1397089' AS pod_id,
                'Surajpole' AS pod_name,
                'North' AS CLUSTER,
                'Udaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1229998' AS pod_id,
                'Safdarjung Enclave' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Santosh.v@scootsy.com ' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1382964' AS pod_id,
                'Saket Metro Station' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Santosh.v@scootsy.com ' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1384512' AS pod_id,
                'Yusuf Sarai' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Santosh.v@scootsy.com ' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1380671' AS pod_id,
                'Babarpur' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'anil.sarswat@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1388689' AS pod_id,
                'Dilshad Colony' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'anil.sarswat@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1099459' AS pod_id,
                'Dilshad Garden 2' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'anil.sarswat@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1385945' AS pod_id,
                'Keventers' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'anil.sarswat@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1384511' AS pod_id,
                'Pv Ranikhet' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'anil.sarswat@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1381835' AS pod_id,
                'Rajendra Place' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'anil.sarswat@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '816651' AS pod_id,
                'Vardhman Mall' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'anil.sarswat@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1383826' AS pod_id,
                'Budella' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'arpita.sharma@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '762550' AS pod_id,
                'Janakpuri' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'arpita.sharma@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1062420' AS pod_id,
                'Janakpuri_ Rajouri' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'arpita.sharma@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1387705' AS pod_id,
                'Nawada' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'arpita.sharma@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1383383' AS pod_id,
                'Pochanpur' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'arpita.sharma@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1388690' AS pod_id,
                'Rajapuri' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'arpita.sharma@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '649851' AS pod_id,
                'Rajouri' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'arpita.sharma@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1383384' AS pod_id,
                'Shubham Enclave' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'arpita.sharma@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1398755' AS pod_id,
                'AIIMS' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lallan.prasad@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1389690' AS pod_id,
                'Cr Park' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lallan.prasad@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '406774' AS pod_id,
                'Malviya' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lallan.prasad@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1386536' AS pod_id,
                'Vasant Square Mall' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lallan.prasad@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1294674' AS pod_id,
                'Diving Road' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lokesh.punia@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1386271' AS pod_id,
                'Kohat Enclave' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lokesh.punia@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1390225' AS pod_id,
                'Shakti Vihar' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lokesh.punia@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1386535' AS pod_id,
                'Subhash Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lokesh.punia@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1382871' AS pod_id,
                'Chandar Vihar' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Mithlesh.kumar@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1386719' AS pod_id,
                'Cp' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Mithlesh.kumar@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1384143' AS pod_id,
                'Kakrola Dwarka' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Mithlesh.kumar@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '649841' AS pod_id,
                'Laxmi N' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Mithlesh.kumar@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1099458' AS pod_id,
                'Laxmi Nagar2' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Mithlesh.kumar@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1381851' AS pod_id,
                'Mahavir Enclave' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Mithlesh.kumar@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1230886' AS pod_id,
                'Mayur Vihar 2' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Mithlesh.kumar@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1325203' AS pod_id,
                'Timarpur' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Mithlesh.kumar@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1386948' AS pod_id,
                'East Of Kailash' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Pankaj.Kumar08@scootsy.com ' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1267917' AS pod_id,
                'Kailash Colony' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Pankaj.Kumar08@scootsy.com ' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1382291' AS pod_id,
                'Masjid Moth' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Pankaj.Kumar08@scootsy.com ' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1381357' AS pod_id,
                'Jasola' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Santosh.v@scootsy.com ' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1261842' AS pod_id,
                'Kirti Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Vijay.t@scootsy.com' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1099457' AS pod_id,
                'Tilak Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Vijay.t@scootsy.com' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1389689' AS pod_id,
                'Uttam Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Vijay.t@scootsy.com' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1393826' AS pod_id,
                'Nehru Colony' AS pod_name,
                'North' AS CLUSTER,
                'Faridabad' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1347907' AS pod_id,
                'Sector 12' AS pod_name,
                'North' AS CLUSTER,
                'Faridabad' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1391900' AS pod_id,
                'Sector 20B' AS pod_name,
                'North' AS CLUSTER,
                'Faridabad' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1390226' AS pod_id,
                'Sector 21 A' AS pod_name,
                'North' AS CLUSTER,
                'Faridabad' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1391899' AS pod_id,
                'Sector 37' AS pod_name,
                'North' AS CLUSTER,
                'Faridabad' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1394451' AS pod_id,
                'Sector 14 Main' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1381563' AS pod_id,
                'Sector 20 Ggn' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1298919' AS pod_id,
                'Sector 28' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1381279' AS pod_id,
                'Greenwood City' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1384144' AS pod_id,
                'Sikandapura Le Meridian' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1380623' AS pod_id,
                'Dlf Cyber Hub' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'apurv.gupta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1395428' AS pod_id,
                'DLF Sec 54' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'apurv.gupta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1265812' AS pod_id,
                'Jharsa Road (Sec 39)' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'apurv.gupta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1384513' AS pod_id,
                'Om Vihar' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'apurv.gupta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1385646' AS pod_id,
                'Samaspur' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'apurv.gupta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1389005' AS pod_id,
                'Sector 104, Gurgaon' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'apurv.gupta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1389006' AS pod_id,
                'Sector 10A' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'apurv.gupta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1383827' AS pod_id,
                'Sector 39 Jharsa(Franchisee)' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'apurv.gupta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1397088' AS pod_id,
                'Golden Temple' AS pod_name,
                'North' AS CLUSTER,
                'Amritsar' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1385943' AS pod_id,
                'Gillco Parkhills' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1397025' AS pod_id,
                'Kurali Road' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1385562' AS pod_id,
                'Peermuchalla' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1387904' AS pod_id,
                'Phse 3B' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1387905' AS pod_id,
                'Sec 10 Panchkula' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1387906' AS pod_id,
                'Sec 67 Chandigarh' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1389004' AS pod_id,
                'Sec 7 Panchkula' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1383823' AS pod_id,
                'Sector 23' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1339713' AS pod_id,
                'Sector 63' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1390220' AS pod_id,
                'Shivalik City' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1381441' AS pod_id,
                'Sub City Center' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1386912' AS pod_id,
                'Sunny Enclave' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1388997' AS pod_id,
                'Vip Road' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1348435' AS pod_id,
                'Zirakpur' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1395727' AS pod_id,
                'Hargobind Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Ludhiana' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1397034' AS pod_id,
                'Pritam Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Ludhiana' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1381444' AS pod_id,
                'Sector 88' AS pod_name,
                'North' AS CLUSTER,
                'Faridabad' AS city,
                'lokesh.patel@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1382659' AS pod_id,
                'Av Phase 3' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'lokesh.patel@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1384146' AS pod_id,
                'Choma Village' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'lokesh.patel@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1239163' AS pod_id,
                'Dlf Phase 1 (Sec 42)' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'lokesh.patel@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1397028' AS pod_id,
                'Gehlot Farm' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'lokesh.patel@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1389633' AS pod_id,
                'Sapphire Mall' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'lokesh.patel@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1392083' AS pod_id,
                'Sector 53' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'lokesh.patel@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1278169' AS pod_id,
                'Sector 67' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'lokesh.patel@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1382258' AS pod_id,
                'Tulip Society Sec 70' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'lokesh.patel@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '762551' AS pod_id,
                'Spencer' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'Mithun.kumar@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1387911' AS pod_id,
                'Sector 57' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'Mithun.kumar@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1387568' AS pod_id,
                'Vatika City Ggn' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'Mithun.kumar@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1382708' AS pod_id,
                'Airport Road' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'anil.thakare1@swiggy.in ' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1385566' AS pod_id,
                'Alpha Homes' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'anil.thakare1@swiggy.in ' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1383135' AS pod_id,
                'Aundh Gaon' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'anil.thakare1@swiggy.in ' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1386537' AS pod_id,
                'Goodwill Square Lohegaon' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'anil.thakare1@swiggy.in ' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1385564' AS pod_id,
                'Kalyani Nagar' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'anil.thakare1@swiggy.in ' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1382710' AS pod_id,
                'Sayaji Hotel' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'anil.thakare1@swiggy.in ' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1390228' AS pod_id,
                'Shivrajnagar' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'anil.thakare1@swiggy.in ' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1380714' AS pod_id,
                'Wagholi' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'anil.thakare1@swiggy.in ' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1394682' AS pod_id,
                'Alto Porvorim' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1386814' AS pod_id,
                'Baga' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1392081' AS pod_id,
                'Cujira Ward' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1386942' AS pod_id,
                'Dabolim' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1385837' AS pod_id,
                'Mapusa' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1390351' AS pod_id,
                'Margao' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1113107' AS pod_id,
                'North Goa' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1386927' AS pod_id,
                'Panji' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1382351' AS pod_id,
                'Porvorim' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1392082' AS pod_id,
                'Siolim Goa' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1381971' AS pod_id,
                'Taliegao' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1387908' AS pod_id,
                'Vagator' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1383574' AS pod_id,
                'Atma Nagar' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1388453' AS pod_id,
                'Balewadi' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1393573' AS pod_id,
                'Dattawadi' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1389002' AS pod_id,
                'Dhankawadi' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1278175' AS pod_id,
                'Hinjewadi It Park' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1385565' AS pod_id,
                'Hinjewadi Phase 1' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1382965' AS pod_id,
                'Hinjewadi Phase 3' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1393574' AS pod_id,
                'Kunal Icon Pimple Saudagar' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1383575' AS pod_id,
                'Mohan Nagar Society' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1386163' AS pod_id,
                'Nanded City' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1390229' AS pod_id,
                'Pashan Gaon' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1385649' AS pod_id,
                'Pranjali Patil Nagar' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1389254' AS pod_id,
                'Ravet' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1389001' AS pod_id,
                'Samarth Colony' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1393575' AS pod_id,
                'Vikas Udyan' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '737089' AS pod_id,
                'Warje' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1384148' AS pod_id,
                'Azad Chowk Kothrud' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1394673' AS pod_id,
                'Bhekrai' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1383853' AS pod_id,
                'Hadapsar' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1382354' AS pod_id,
                'Kausar Bagh' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '713116' AS pod_id,
                'Kharadi' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1389691' AS pod_id,
                'Kharadi 2' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1381445' AS pod_id,
                'Manjari' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1382709' AS pod_id,
                'Nyati' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1397626' AS pod_id,
                'Kharadi' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1388314' AS pod_id,
                'Wanwadi New' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1397037' AS pod_id,
                'Adgaon' AS pod_name,
                'West' AS CLUSTER,
                'Nashik' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1388452' AS pod_id,
                'Bombay Naka' AS pod_name,
                'West' AS CLUSTER,
                'Nashik' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1389256' AS pod_id,
                'College Road' AS pod_name,
                'West' AS CLUSTER,
                'Nashik' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1383570' AS pod_id,
                'Bodakdev' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1393824' AS pod_id,
                'Celebration Mall' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1385348' AS pod_id,
                'Gurukul' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1388195' AS pod_id,
                'Motera' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1385642' AS pod_id,
                'Navrangpura' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1386812' AS pod_id,
                'Panchwati' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1385834' AS pod_id,
                'Prahladnagar' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1387076' AS pod_id,
                'Sargasan Gandhinagar' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1397023' AS pod_id,
                'Science City' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1388194' AS pod_id,
                'Vandematram' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1386811' AS pod_id,
                'Vejalpur' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1395731' AS pod_id,
                'Civil Hospital' AS pod_name,
                'West' AS CLUSTER,
                'Rajkot' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1393825' AS pod_id,
                'Aashima Mall' AS pod_name,
                'West' AS CLUSTER,
                'Bhopal' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1397619' AS pod_id,
                'Anand nagar' AS pod_name,
                'West' AS CLUSTER,
                'Bhopal' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1399345' AS pod_id,
                'MP Nagar' AS pod_name,
                'West' AS CLUSTER,
                'Bhopal' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '973251' AS pod_id,
                'Badi Bhamori' AS pod_name,
                'West' AS CLUSTER,
                'Indore' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1382352' AS pod_id,
                'Bombay Hospital' AS pod_name,
                'West' AS CLUSTER,
                'Indore' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1382165' AS pod_id,
                'Navlakha - Mim' AS pod_name,
                'West' AS CLUSTER,
                'Indore' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1386817' AS pod_id,
                'Saket Square' AS pod_name,
                'West' AS CLUSTER,
                'Indore' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1388386' AS pod_id,
                'Usha Nagar' AS pod_name,
                'West' AS CLUSTER,
                'Indore' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1395733' AS pod_id,
                'Adajan gam' AS pod_name,
                'West' AS CLUSTER,
                'Surat' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1382355' AS pod_id,
                'Bharthana' AS pod_name,
                'West' AS CLUSTER,
                'Surat' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1385948' AS pod_id,
                'Majura Gate' AS pod_name,
                'West' AS CLUSTER,
                'Surat' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1397042' AS pod_id,
                'Mota Varcha' AS pod_name,
                'West' AS CLUSTER,
                'Surat' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1397039' AS pod_id,
                'Palanpur Gam' AS pod_name,
                'West' AS CLUSTER,
                'Surat' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1387706' AS pod_id,
                'Punagam' AS pod_name,
                'West' AS CLUSTER,
                'Surat' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1394674' AS pod_id,
                'Vesu pod' AS pod_name,
                'West' AS CLUSTER,
                'Surat' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1385567' AS pod_id,
                'Diwalipura' AS pod_name,
                'West' AS CLUSTER,
                'Vadodara' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1388315' AS pod_id,
                'Gotri Road' AS pod_name,
                'West' AS CLUSTER,
                'Vadodara' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1391902' AS pod_id,
                'Nilambar Palms' AS pod_name,
                'West' AS CLUSTER,
                'Vadodara' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1389255' AS pod_id,
                'Ratri Bazaar' AS pod_name,
                'West' AS CLUSTER,
                'Vadodara' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1387082' AS pod_id,
                'Yakutpura' AS pod_name,
                'West' AS CLUSTER,
                'Vadodara' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1392084' AS pod_id,
                'Byramji' AS pod_name,
                'West' AS CLUSTER,
                'Nagpur' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1393571' AS pod_id,
                'Mahal pod' AS pod_name,
                'West' AS CLUSTER,
                'Nagpur' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1392532' AS pod_id,
                'Manish Nagar' AS pod_name,
                'West' AS CLUSTER,
                'Nagpur' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1397035' AS pod_id,
                'Wardhaman Nagar' AS pod_name,
                'West' AS CLUSTER,
                'Nagpur' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1388383' AS pod_id,
                'Bandapura' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'akshay.dash@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '854379' AS pod_id,
                'Kalyan Nagar3' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'akshay.dash@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1389251' AS pod_id,
                'Kannamangala' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'akshay.dash@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1380447' AS pod_id,
                'Seegehalli' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'akshay.dash@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1384139' AS pod_id,
                'Tin Factory' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'akshay.dash@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1383715' AS pod_id,
                'Upkar Layout' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'akshay.dash@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '762610' AS pod_id,
                'Marathahalli 2' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'akshay.dash@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '649831' AS pod_id,
                'Bellandur' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'Manohar.3@Swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1382655' AS pod_id,
                'Doodswarth Enclave' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'Manohar.3@Swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1370332' AS pod_id,
                'Gunjur' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'Manohar.3@Swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1380521' AS pod_id,
                'Jhonson Mrkt' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'Manohar.3@Swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1346768' AS pod_id,
                'Mahadevpura' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'Manohar.3@Swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1393564' AS pod_id,
                'Sg Palya' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'Manohar.3@Swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1382254' AS pod_id,
                'Yemalur' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'Manohar.3@Swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1388998' AS pod_id,
                'Adarsh Palm Retreat' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'prakash.t1@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1381021' AS pod_id,
                'Chandra Layt' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'prakash.t1@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1387561' AS pod_id,
                'Gandhipura' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'prakash.t1@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1390216' AS pod_id,
                'Iblur' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'prakash.t1@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1395425' AS pod_id,
                'Kalamandir' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'prakash.t1@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1382350' AS pod_id,
                'Kartik Nagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'prakash.t1@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1388382' AS pod_id,
                'Koramangala 1St Block' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'prakash.t1@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '901839' AS pod_id,
                'Koramangala 2' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'prakash.t1@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1380522' AS pod_id,
                'Thubarahalli' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'prakash.t1@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1397048' AS pod_id,
                'HSR' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                '' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1386385' AS pod_id,
                'Bengaluru Badootaa' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                '' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1181690' AS pod_id,
                'Chramjpet3' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                '' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1190774' AS pod_id,
                'Jp Nagar 5' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                '' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1398437' AS pod_id,
                'Kengeri Satellite Town' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                '' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1397796' AS pod_id,
                'Ns Palya' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                '' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1382349' AS pod_id,
                'Ranka Colony' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                '' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1334211' AS pod_id,
                'Sai Enclave' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                '' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1395434' AS pod_id,
                'Hoodi' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'richard.a@scootsy.com' AS com,
                'yashwanth.s@swiggy.in ' AS dch
   UNION SELECT '1395721' AS pod_id,
                'Kodihalli - Mega POD' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'richard.a@scootsy.com' AS com,
                'yashwanth.s@swiggy.in ' AS dch
   UNION SELECT '1396284' AS pod_id,
                'Koramanagala' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'richard.a@scootsy.com' AS com,
                'yashwanth.s@swiggy.in ' AS dch),
     lfr AS
  (SELECT lfr.reminder_id,
          fr.organization,
          fr.tz_offset AS tz_offset_sec,
          fr.form_id,
          l.location_name AS LOCATION,
          (to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset)::date AS reminded_date,
          row_number() OVER (PARTITION BY fr.form_id,
                                          l.location_name,
                                          (to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset)::date
                             ORDER BY to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset) AS reminder_no,
                            to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset AS reminded_at,
                                                                          to_timestamp(lfr.reminder_window_end/1000) + interval '1 sec'*fr.tz_offset AS reminder_window_end,
                                                                                                                                lfr.form_response_id,
                                                                                                                                CASE
                                                                                                                                    WHEN responded_at = 0 THEN NULL
                                                                                                                                    ELSE to_timestamp(lfr.responded_at/1000) + interval '1 sec'*fr.tz_offset
                                                                                                                                END AS responded_at
   FROM location_form_reminders lfr
   JOIN form_reminders fr ON fr.id = lfr.reminder_id
   JOIN locations l ON lfr.location_id = l.id
   WHERE l.location_name NOT ILIKE 'KNOW'
     AND l.location_name NOT ILIKE 'HQ'
     AND l.location_name NOT ILIKE '%HO'
     AND to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset > date_trunc('Day', CURRENT_TIMESTAMP + interval '1 sec'*fr.tz_offset) - interval '4 weeks'
     AND fr.form_id IN ('-O3WHxW8vkcfCKYmKK2Y',
                        '-O0Cw32tUETcxfnzf2PR',
                        '-O9xEQ5ujY1RFVuP6c-G',
                        '-O9xFFjif-72YtWYQIqn',
                        '-O11A2dcpiaMx8pQedRf',
                        '-O11ADimkVVHNqz_oeMT',
                        '-O8qdhuV9zaoXTpQiPOY',
                        '-O9KR9ftEE-NsUUgtCtA',
                        '-O9U-6iKlPyBJVMM6gfk',
                        '-O9AEYuBtu2p_952hrbR',
                        '-O9Dps0NIo2VS7s5NPuh',
                        '-OAvuQACgKHCcdHFkm0L',
                        '-OB4CVmT_YAytFR2fty7',
                        '-OB4xcGu1NqT84w0lAWQ',
                        '-O9xC1H6RHlhY6rnKKSW',
                        '-O9U1GGkwZWt_Vs6okDW',
                        '-OB4xxAJqHUO99TRB_io',
                        '-OB4z2473dKeZ34McBIV',
                        '-OB4zWin85ZrjPUjH0RV',
                        '-OB4zm7TVqXaKK3J0vAX',
                        '-OB5-5PzkC26eek0Bk-1',
                        '-OB5-Q1oguPmrJlRlBnH',
                        '-OB5-kLCkZWwy65-Ek6h',
                        '-OB505iZAJ8wJ0zZxcFM',
                        '-O3CRSzHs_yr8MeznWkv',
                        '-OB51eSXMa_nSoibv6yS',
                        '-OB525WEclHOXV6JYtJn',
                        '-OB51wGxzBWxhStUNtqv',
                        '-OB52IvLT3rJTvAM7wLT',
                        '-OB52TuE5WfUdYkJdmrE',
                        '-OB52jx59NEjUjPBixqy',
                        '-OB52ttmR2iTHizVPXwE',
                        '-OB55VCsN1K47jdOc-N2',
                        '-OB5622pYYZHwe2fCC1W',
                        '-OB56cNfUDEhTxUPhJ4S',
                        '-OB56mQetguLSxb-mTv6',
                        '-OB57bk-9BG-rX7wAceu',
                        '-OAIHk3YCxnTfjV_fyGr',
                        '-OAIJndZxwVht8750Zc6',
                        '-OAIsM27j29lvnM9Br5O',
                        '-OAIx7irPIBo-9cKLh_y',
                        '-OALkeIDkVHTQtxyEVne',
                        '-OALrG4eIk_Kaw-LaJG6',
                        '-OB8utwNF_o5UKdxabUc',
                        '-O9xI_JjhMrVzTAXkh_F',
                        '-OAvN4-5jv-XvXPhQEeM',
                        '-OAvPLR9pQLC_wvRpX0Y',
                        '-OAvQgdymG5aSTHcrVQR',
                        '-OAvVUTteJqBgqdYYJgq',
                        '-OAvVhmAOQCKn9Ln_JC-',
                        '-OAvVvs7yNtCfVItyUr4',
                        '-OAvWIJh_dc1cSU8uJgq',
                        '-OAvWV2dPw9S0L6KWBlb',
                        '-OAvb8LGJYxjlH_YrSRb',
                        '-OAvWvojjYv0Cxl9uTai',
                        '-OAvuXQ5wpvOziRxyIG5',
                        '-OAw2sT8UNJSi4Jcc4NA',
                        '-OBAL68W_bLx6qrgfVjm',
                        '-OB0_uO6Q4lBeasMViQT',
                        '-OB56yx-t8HP7oBY0JQX',
                        '-OB0_OEwgHSkOq9KOr7P')),
     fs AS
  (SELECT fs.*
   FROM form_submissions fs
   WHERE fs.location NOT ILIKE 'KNOW'
     AND fs.location NOT ILIKE 'HQ'
     AND fs.location NOT ILIKE '%HO'
     AND fs.submit_date AT TIME ZONE 'Asia/Kolkata' > date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata') - interval '4 weeks'
     AND fs.form_id IN ('-O3WHxW8vkcfCKYmKK2Y',
                        '-O0Cw32tUETcxfnzf2PR',
                        '-O9xEQ5ujY1RFVuP6c-G',
                        '-O9xFFjif-72YtWYQIqn',
                        '-O11A2dcpiaMx8pQedRf',
                        '-O11ADimkVVHNqz_oeMT',
                        '-O8qdhuV9zaoXTpQiPOY',
                        '-O9KR9ftEE-NsUUgtCtA',
                        '-O9U-6iKlPyBJVMM6gfk',
                        '-O9AEYuBtu2p_952hrbR',
                        '-O9Dps0NIo2VS7s5NPuh',
                        '-OAvuQACgKHCcdHFkm0L',
                        '-OB4CVmT_YAytFR2fty7',
                        '-OB4xcGu1NqT84w0lAWQ',
                        '-O9xC1H6RHlhY6rnKKSW',
                        '-O9U1GGkwZWt_Vs6okDW',
                        '-OB4xxAJqHUO99TRB_io',
                        '-OB4z2473dKeZ34McBIV',
                        '-OB4zWin85ZrjPUjH0RV',
                        '-OB4zm7TVqXaKK3J0vAX',
                        '-OB5-5PzkC26eek0Bk-1',
                        '-OB5-Q1oguPmrJlRlBnH',
                        '-OB5-kLCkZWwy65-Ek6h',
                        '-OB505iZAJ8wJ0zZxcFM',
                        '-O3CRSzHs_yr8MeznWkv',
                        '-OB51eSXMa_nSoibv6yS',
                        '-OB525WEclHOXV6JYtJn',
                        '-OB51wGxzBWxhStUNtqv',
                        '-OB52IvLT3rJTvAM7wLT',
                        '-OB52TuE5WfUdYkJdmrE',
                        '-OB52jx59NEjUjPBixqy',
                        '-OB52ttmR2iTHizVPXwE',
                        '-OB55VCsN1K47jdOc-N2',
                        '-OB5622pYYZHwe2fCC1W',
                        '-OB56cNfUDEhTxUPhJ4S',
                        '-OB56mQetguLSxb-mTv6',
                        '-OB57bk-9BG-rX7wAceu',
                        '-OAIHk3YCxnTfjV_fyGr',
                        '-OAIJndZxwVht8750Zc6',
                        '-OAIsM27j29lvnM9Br5O',
                        '-OAIx7irPIBo-9cKLh_y',
                        '-OALkeIDkVHTQtxyEVne',
                        '-OALrG4eIk_Kaw-LaJG6',
                        '-OB8utwNF_o5UKdxabUc',
                        '-O9xI_JjhMrVzTAXkh_F',
                        '-OAvN4-5jv-XvXPhQEeM',
                        '-OAvPLR9pQLC_wvRpX0Y',
                        '-OAvQgdymG5aSTHcrVQR',
                        '-OAvVUTteJqBgqdYYJgq',
                        '-OAvVhmAOQCKn9Ln_JC-',
                        '-OAvVvs7yNtCfVItyUr4',
                        '-OAvWIJh_dc1cSU8uJgq',
                        '-OAvWV2dPw9S0L6KWBlb',
                        '-OAvb8LGJYxjlH_YrSRb',
                        '-OAvWvojjYv0Cxl9uTai',
                        '-OAvuXQ5wpvOziRxyIG5',
                        '-OAw2sT8UNJSi4Jcc4NA',
                        '-OBAL68W_bLx6qrgfVjm',
                        '-OB0_uO6Q4lBeasMViQT',
                        '-OB56yx-t8HP7oBY0JQX',
                        '-OB0_OEwgHSkOq9KOr7P')),
     fr AS
  (SELECT fs.form_id,
          fs.submit_date,
          fs.response_id,
          fr.response->>'name' AS LOCATION,
                        (fs.submit_date AT TIME ZONE 'Asia/Kolkata')::date AS submitted_date,
                        row_number() OVER (PARTITION BY fs.form_id,
                                                        (fs.submit_date AT TIME ZONE 'Asia/Kolkata')::date,
                                                        fr.response->>'name'
                                           ORDER BY fs.submit_date) AS submission_no
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   WHERE fr.question_type = 'location' )
SELECT lfr.organization AS "Organization",
       lm.cluster AS "Cluster",
       lm.city AS "City",
       coalesce(lm.pod_id, regexp_replace(lfr."location", '([0-9]+).*', '\1')) AS "Pod ID",
       lm.pod_name AS "Pod Name",
       lm.com AS "COM",
       lm.dch AS "DCH",
       lfr.reminded_date AS "Date",
	   CASE
           WHEN (lfr.reminded_at)::TIME BETWEEN '06:00:01' AND '12:00:01' THEN '1 - Morning'
           WHEN (lfr.reminded_at)::TIME BETWEEN '12:00:01' AND '20:00:01' THEN '2 - Afternoon'
           ELSE '3 - Night'
       END AS "Shift",
       lfr.form_id AS "Routine KNID",
       n.title AS "Routine Name",
       lfr.reminded_at AS "Reminded At",
       CASE
           WHEN date_trunc('Week', lfr.reminded_at) = date_trunc('Week', CURRENT_TIMESTAMP + interval '1 sec'*lfr.tz_offset_sec) - interval '4 weeks' THEN 'Wk -4'
           WHEN date_trunc('Week', lfr.reminded_at) = date_trunc('Week', CURRENT_TIMESTAMP + interval '1 sec'*lfr.tz_offset_sec) - interval '3 weeks' THEN 'Wk -3'
           WHEN date_trunc('Week', lfr.reminded_at) = date_trunc('Week', CURRENT_TIMESTAMP + interval '1 sec'*lfr.tz_offset_sec) - interval '2 weeks' THEN 'Wk -2'
           WHEN date_trunc('Week', lfr.reminded_at) = date_trunc('Week', CURRENT_TIMESTAMP + interval '1 sec'*lfr.tz_offset_sec) - interval '1 weeks' THEN 'Wk -1'
           ELSE 'Day -'||ceiling((extract(epoch
                                          FROM (CURRENT_TIMESTAMP + interval '1 sec'*lfr.tz_offset_sec)::date)-extract(epoch
                                                                                                                       FROM lfr.reminded_at::date))/86400)||' '||to_char(lfr.reminded_at, 'DD-Mon')
       END AS "Period Descriptor",
       CASE
           WHEN lfr.form_response_id IS NOT NULL THEN 'Compliant'
           WHEN fr.response_id IS NULL THEN 'Missed'
           ELSE 'Done Late'
       END AS "Status",
       CASE
           WHEN lfr.form_response_id IS NOT NULL THEN 1
           WHEN fr.response_id IS NULL THEN 0
           ELSE 0.5
       END AS "Compliance Score",
       CASE
           WHEN coalesce(lfr.form_response_id, fr.response_id) IS NULL THEN 0.0
           ELSE 1.0
       END AS "Completion Score",
       coalesce(lfr.form_response_id, fr.response_id) AS "Submission KNID"
FROM lfr
JOIN nuggets n ON lfr.form_id = n.id
LEFT OUTER JOIN fr ON fr.form_id = lfr.form_id
AND (fr.submit_date + interval '1 sec'*lfr.tz_offset_Sec)::date = (lfr.reminded_at)::date
AND fr.location = lfr.location
AND fr.submission_no = lfr.reminder_no
LEFT OUTER JOIN lm ON regexp_replace(lfr."location", '([0-9]+).*', '\1') = lm.pod_id
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
		 17
ORDER BY 11,
         10,
         1,
         2,
         3,
         4
```

---

## Instamart Pod Yday Routine Compliance_Yday Checklist Compliance.sql

**Tables referenced:** form_reminders, form_submissions, fs, lfr, lm, location_form_reminders, locations, nuggets

**Original Query:**

```sql
-- Data Source: Instamart Pod Yday Routine Compliance
-- Dashboard: Yday Checklist Compliance
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:57:59
-- ============================================================

WITH lm AS
  (SELECT '1113109' AS pod_id,
          'Antopehill' AS pod_name,
          'West' AS CLUSTER,
          'Mumbai' AS city,
          'durvesh.gholap@swiggy.in' AS com,
          'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1396283' AS pod_id,
                'Byculla' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1385841' AS pod_id,
                'Century Bazaar' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1135722' AS pod_id,
                'Chowpatty' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1383130' AS pod_id,
                'Dhobi Talao' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1295148' AS pod_id,
                'Juhu' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1396295' AS pod_id,
                'Sion East' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1396282' AS pod_id,
                'Tardeo Police Station' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1311101' AS pod_id,
                'Wadala' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '810366' AS pod_id,
                'Andheri East' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'manoj.gahlot@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '969383' AS pod_id,
                'Bandra West' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'manoj.gahlot@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1062417' AS pod_id,
                'Dadar' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'manoj.gahlot@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1392531' AS pod_id,
                'Lower Parel' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'manoj.gahlot@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1381967' AS pod_id,
                'Mahim' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'manoj.gahlot@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1390224' AS pod_id,
                'Model Colony Mumbai' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'manoj.gahlot@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1397051' AS pod_id,
                'Vile Parle' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'manoj.gahlot@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1384969' AS pod_id,
                'Chandivali' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sagar.kudtarkar@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1238358' AS pod_id,
                'Jvlr' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sagar.kudtarkar@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1391897' AS pod_id,
                'Postal Colony Chembur' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sagar.kudtarkar@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1135720' AS pod_id,
                'Powai2' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sagar.kudtarkar@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1387703' AS pod_id,
                'Rk Studios' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sagar.kudtarkar@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '649837' AS pod_id,
                'Kalina' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sagar.kudtarkar@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1335483' AS pod_id,
                'Seawoods (Navi Mumbai)' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sagar.kudtarkar@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1380622' AS pod_id,
                'Seven Hills' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sagar.kudtarkar@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1383573' AS pod_id,
                'Shiravane' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sagar.kudtarkar@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1382256' AS pod_id,
                'Gokuldham' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shadab.husain@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1135721' AS pod_id,
                'Goregaon_2' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shadab.husain@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1239162' AS pod_id,
                'Inorbit Mall Malad West' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shadab.husain@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1190779' AS pod_id,
                'Kandivali East' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shadab.husain@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1231809' AS pod_id,
                'Malad West' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shadab.husain@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1388686' AS pod_id,
                'Pragati Nagar' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shadab.husain@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1382439' AS pod_id,
                'Thakur Village' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shadab.husain@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1314371' AS pod_id,
                'Vasai Virar' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shadab.husain@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '810365' AS pod_id,
                'Versova' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1319696' AS pod_id,
                'Bandra West (Khar)' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1238359' AS pod_id,
                'Lokhandwala' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1382657' AS pod_id,
                'Oshiwara' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1190780' AS pod_id,
                'Vileparle' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1295147' AS pod_id,
                'Vileparle East' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1381561' AS pod_id,
                'Hawaiian Village' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sonuaniruddh.sahani@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1396296' AS pod_id,
                'Hiranandani Mbc Park' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sonuaniruddh.sahani@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1381443' AS pod_id,
                'Majiwada' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sonuaniruddh.sahani@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1181694' AS pod_id,
                'Thane2' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sonuaniruddh.sahani@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1267915' AS pod_id,
                'Thane Hiranandani Estate' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sonuaniruddh.sahani@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1336659' AS pod_id,
                'Thane West' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sonuaniruddh.sahani@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1381643' AS pod_id,
                'Uthalsar' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sonuaniruddh.sahani@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '929911' AS pod_id,
                'Yojit Estates' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'sonuaniruddh.sahani@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1084119' AS pod_id,
                'Belapur' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1389632' AS pod_id,
                'Gaothan' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1385645' AS pod_id,
                'Ghansoli' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1381966' AS pod_id,
                'Indira Nagar' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1082435' AS pod_id,
                'Kharghar' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1380959' AS pod_id,
                'Nmims Navi Mumbai' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1238356' AS pod_id,
                'Panvel' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1388688' AS pod_id,
                'Sanpada' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1386846' AS pod_id,
                'Taloja Jail Road' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1381500' AS pod_id,
                'Telecom Factory' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1398445' AS pod_id,
                'Vashi' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1388687' AS pod_id,
                'Bhayander' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'tejas.shetty@scootsy.com' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '762615' AS pod_id,
                'Borivali' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'tejas.shetty@scootsy.com' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1237261' AS pod_id,
                'Borivali East' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'tejas.shetty@scootsy.com' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1062418' AS pod_id,
                'Dahisar West' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'tejas.shetty@scootsy.com' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1237262' AS pod_id,
                'Kandivali West' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'tejas.shetty@scootsy.com' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1346590' AS pod_id,
                'Mira Hubtown' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'tejas.shetty@scootsy.com' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1230883' AS pod_id,
                'Oberoi Mall' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'tejas.shetty@scootsy.com' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1381833' AS pod_id,
                'Unique Gardens' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'tejas.shetty@scootsy.com' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1390223' AS pod_id,
                'Chikan Ghar' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1381834' AS pod_id,
                'Container Yard' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1062416' AS pod_id,
                'Ghatkopar East' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1388387' AS pod_id,
                'Kalyan East' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1386534' AS pod_id,
                'Katai Pipeline Road' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1395728' AS pod_id,
                'Katai Village' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '788745' AS pod_id,
                'Bhandup' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1278165' AS pod_id,
                'Mulund West' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1298955' AS pod_id,
                'Rcity Mall, Ghatkopar West' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1238357' AS pod_id,
                'Sagarli Gaon' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '810367' AS pod_id,
                'Vikhroli' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'vasudev.chawla@swiggy.in' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1398760' AS pod_id,
                'Matunga East' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                '' AS com,
                'ankit.gupta3@swiggy.in' AS dch
   UNION SELECT '1383571' AS pod_id,
                'Arhat Bazaar' AS pod_name,
                'North' AS CLUSTER,
                'Dehradun' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1393569' AS pod_id,
                'Doon It Park' AS pod_name,
                'North' AS CLUSTER,
                'Dehradun' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1391903' AS pod_id,
                'Isbt' AS pod_name,
                'North' AS CLUSTER,
                'Dehradun' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1381970' AS pod_id,
                'Jakhan' AS pod_name,
                'North' AS CLUSTER,
                'Dehradun' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1388685' AS pod_id,
                'Jogiwala' AS pod_name,
                'North' AS CLUSTER,
                'Dehradun' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1388316' AS pod_id,
                'Karanpur' AS pod_name,
                'North' AS CLUSTER,
                'Dehradun' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1394449' AS pod_id,
                'Saharanpur Road' AS pod_name,
                'North' AS CLUSTER,
                'Dehradun' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1398750' AS pod_id,
                'Ashok Vihar' AS pod_name,
                'North' AS CLUSTER,
                'Kanpur' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1398751' AS pod_id,
                'Kakadeo' AS pod_name,
                'North' AS CLUSTER,
                'Kanpur' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1397090' AS pod_id,
                'Geeta Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Kanpur' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1398443' AS pod_id,
                'Antas Mall' AS pod_name,
                'North' AS CLUSTER,
                'Lucknow' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1309583' AS pod_id,
                'Ashiana Road' AS pod_name,
                'North' AS CLUSTER,
                'Lucknow' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1339714' AS pod_id,
                'Jankipuram' AS pod_name,
                'North' AS CLUSTER,
                'Lucknow' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1398442' AS pod_id,
                'Lucknow High Court' AS pod_name,
                'North' AS CLUSTER,
                'Lucknow' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1347753' AS pod_id,
                'Nadan Mahal Road' AS pod_name,
                'North' AS CLUSTER,
                'Lucknow' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1382963' AS pod_id,
                'Sector-C' AS pod_name,
                'North' AS CLUSTER,
                'Lucknow' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1397032' AS pod_id,
                'South City' AS pod_name,
                'North' AS CLUSTER,
                'Lucknow' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1394452' AS pod_id,
                'Chetganj' AS pod_name,
                'North' AS CLUSTER,
                'Varanasi' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1396292' AS pod_id,
                'Naria' AS pod_name,
                'North' AS CLUSTER,
                'Varanasi' AS city,
                'ashish.shukla@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1388388' AS pod_id,
                'Alpha 1' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'bhuvaneshwar.kumar@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1384147' AS pod_id,
                'Baraula' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'bhuvaneshwar.kumar@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1385647' AS pod_id,
                'Felix Hospital' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'bhuvaneshwar.kumar@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '406773' AS pod_id,
                'Sec46' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'bhuvaneshwar.kumar@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1386387' AS pod_id,
                'Sec 132' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'bhuvaneshwar.kumar@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1388200' AS pod_id,
                'Sec 50 B Block' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'bhuvaneshwar.kumar@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1397625' AS pod_id,
                'Noida Expressway' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'bhuvaneshwar.kumar@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1389634' AS pod_id,
                'Gaur City 2' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'farukh.1@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1383251' AS pod_id,
                'Cisf' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'farukh.1@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1390227' AS pod_id,
                'Eco City' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'farukh.1@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1386450' AS pod_id,
                'Gda Market Vaishali' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'farukh.1@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1385946' AS pod_id,
                'Jaipuria Mall' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'farukh.1@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1383133' AS pod_id,
                'Sector 59' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'farukh.1@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1388198' AS pod_id,
                'Sector 62' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'farukh.1@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1387080' AS pod_id,
                'Pvr Vvip Ghaziabad' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'rahul.singh02@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1394453' AS pod_id,
                'Raj Nagar Gzb' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'rahul.singh02@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1387081' AS pod_id,
                'Tech Zone 4' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'rahul.singh02@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1398130' AS pod_id,
                'Hazipur Sector 104' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'rahul.singh02@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1386943' AS pod_id,
                'Mayur Vihar Phase 3' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'rahul.singh02@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1388531' AS pod_id,
                'Sector 122' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'rahul.singh02@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1383134' AS pod_id,
                'Sector 44' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'rahul.singh02@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1382167' AS pod_id,
                'Sector 76' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'rahul.singh02@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1395430' AS pod_id,
                'Sector 9' AS pod_name,
                'North' AS CLUSTER,
                'Noida' AS city,
                'rahul.singh02@swiggy.in' AS com,
                'ankit.jain03@swiggy.in' AS dch
   UNION SELECT '1390221' AS pod_id,
                'Chrompet 1' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'balaji.p1@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1390222' AS pod_id,
                'George Town' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'balaji.p1@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1398439' AS pod_id,
                'Jawahar Nagar' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'balaji.p1@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1150192' AS pod_id,
                'Mylapores' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'balaji.p1@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386091' AS pod_id,
                'Nolambur New' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'balaji.p1@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '854384' AS pod_id,
                'Pallavaram' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'balaji.p1@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386974' AS pod_id,
                'Pursaiwakam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'balaji.p1@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1237710' AS pod_id,
                'Villivakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'balaji.p1@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386264' AS pod_id,
                'Tambaram/ Tambaram West' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'karthick.r2@scootsy.com' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1397045' AS pod_id,
                'Sreekaryam' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thiruvananthapuram' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1394675' AS pod_id,
                'Kazhakootam' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thiruvananthapuram' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1381968' AS pod_id,
                'Kulathoor' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thiruvananthapuram' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1382059' AS pod_id,
                'Palayam' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thiruvananthapuram' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1387569' AS pod_id,
                'Poojappura' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thiruvananthapuram' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1388389' AS pod_id,
                'Sasthamangalam' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thiruvananthapuram' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1396291' AS pod_id,
                'Sreekaryam' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thiruvananthapuram' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1394676' AS pod_id,
                'Thampanoor' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thiruvananthapuram' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1395734' AS pod_id,
                'NehruNagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thrissur' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1395735' AS pod_id,
                'Punkunnam' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Thrissur' AS city,
                'midhun.prakashan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1387907' AS pod_id,
                'Ambatur' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1382426' AS pod_id,
                'Anna Nagar Main' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1393566' AS pod_id,
                'Ayappanthangal' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '836516' AS pod_id,
                'Ekkatuthungul' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386449' AS pod_id,
                'Manapakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1393567' AS pod_id,
                'Poonamalee' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386266' AS pod_id,
                'Porur' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1396287' AS pod_id,
                'Puthagaram' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1380670' AS pod_id,
                'Vijaya Nagar' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1230880' AS pod_id,
                'Virugambakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1398449' AS pod_id,
                'Rockfort' AS pod_name,
                'TN' AS CLUSTER,
                'Trichy' AS city,
                'muthuvel.m@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1381276' AS pod_id,
                'Alandur' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'pandiyarajan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1002694' AS pod_id,
                'Kovilambakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'pandiyarajan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1394671' AS pod_id,
                'Kuberan Nagar' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'pandiyarajan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1381753' AS pod_id,
                'Madambakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'pandiyarajan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1389252' AS pod_id,
                'Pammal' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'pandiyarajan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1397026' AS pod_id,
                'Parasakthi nagar' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'pandiyarajan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1349401' AS pod_id,
                'Raghava Nagar' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'pandiyarajan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1393568' AS pod_id,
                'Urapakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'pandiyarajan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1397630' AS pod_id,
                'Velachery' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'pandiyarajan@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1265810' AS pod_id,
                'Balaji Nagar' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1388683' AS pod_id,
                'Kotivakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '810362' AS pod_id,
                'Perungudi 2' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386941' AS pod_id,
                'T Nagar' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1369819' AS pod_id,
                'Thiruvanmiyur' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1237711' AS pod_id,
                'Peelamedu' AS pod_name,
                'TN' AS CLUSTER,
                'Coimbatore' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1388684' AS pod_id,
                'Rs Puram Main' AS pod_name,
                'TN' AS CLUSTER,
                'Coimbatore' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1383850' AS pod_id,
                'Saibaba Colony' AS pod_name,
                'TN' AS CLUSTER,
                'Coimbatore' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1397027' AS pod_id,
                'Saravanampatti' AS pod_name,
                'TN' AS CLUSTER,
                'Coimbatore' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1396288' AS pod_id,
                'Singanallur' AS pod_name,
                'TN' AS CLUSTER,
                'Coimbatore' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1392529' AS pod_id,
                'Trichy Link Road' AS pod_name,
                'TN' AS CLUSTER,
                'Coimbatore' AS city,
                'ramanan.ramdass@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1395426' AS pod_id,
                'Alwarpet' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'shivaraj.j@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1383824' AS pod_id,
                'Karapakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'shivaraj.j@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1385476' AS pod_id,
                'Medavakkam New' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'shivaraj.j@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386813' AS pod_id,
                'Mogappair East' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'shivaraj.j@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386448' AS pod_id,
                'Tirumurthy Nagar' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'shivaraj.j@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '969381' AS pod_id,
                'Vadapalani' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'shivaraj.j@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1389007' AS pod_id,
                'Lawspet' AS pod_name,
                'TN' AS CLUSTER,
                'Pondicherry' AS city,
                'shivaraj.j@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1392533' AS pod_id,
                'Mudaliarpet' AS pod_name,
                'TN' AS CLUSTER,
                'Pondicherry' AS city,
                'shivaraj.j@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1393570' AS pod_id,
                'Aluva' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386092' AS pod_id,
                'Infopark' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1393018' AS pod_id,
                'Kacheripady' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1383382' AS pod_id,
                'Kakkanad' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386715' AS pod_id,
                'Kaloor' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1387563' AS pod_id,
                'Padivattom' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1382427' AS pod_id,
                'Peeta Metro Station' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1381849' AS pod_id,
                'Perumanoor' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1397629' AS pod_id,
                'Ponekkara' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1319695' AS pod_id,
                'Thengod' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1381277' AS pod_id,
                'Vidya Nagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kochi' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1397030' AS pod_id,
                'Govindapuram' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kozhikode' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1396290' AS pod_id,
                'Velliparamba' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kozhikode' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1388451' AS pod_id,
                'West Hills' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Kozhikode' AS city,
                'suresh.pk@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1380531' AS pod_id,
                'Kelambakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1381832' AS pod_id,
                'Natham' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1385475' AS pod_id,
                'Padur' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1388138' AS pod_id,
                'Perumbakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1395723' AS pod_id,
                'Rajakilpakkam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1391892' AS pod_id,
                'Semmencheri' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386267' AS pod_id,
                'Sholinganallur' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1386265' AS pod_id,
                'Thuraipakam' AS pod_name,
                'TN' AS CLUSTER,
                'Chennai' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1395732' AS pod_id,
                'Alagapuram' AS pod_name,
                'TN' AS CLUSTER,
                'Salem' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1398447' AS pod_id,
                'Gugai' AS pod_name,
                'TN' AS CLUSTER,
                'Salem' AS city,
                'vimalrajesh.vs@swiggy.in' AS com,
                'gajendraprabhu.g@swiggy.in' AS dch
   UNION SELECT '1336431' AS pod_id,
                'Airoli' AS pod_name,
                'West' AS CLUSTER,
                'Mumbai' AS city,
                'swapnil.rathod@swiggy.in' AS com,
                'jeetendra.tiwari@swiggy.in' AS dch
   UNION SELECT '592956' AS pod_id,
                'Alwal' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1398441' AS pod_id,
                'AMR Planet' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1396289' AS pod_id,
                'Anand Bagh' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '988469' AS pod_id,
                'A.S Rao Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1396294' AS pod_id,
                'Boduppal' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1155153' AS pod_id,
                'Bowenpally' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1388385' AS pod_id,
                'Damaiguda' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1388312' AS pod_id,
                'Kompally' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '816649' AS pod_id,
                'Tarnaka' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1393828' AS pod_id,
                'West Marredpally' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'lakkaraju.mahesh@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1381355' AS pod_id,
                'Barkatpura' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'mogili.reddy@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1385839' AS pod_id,
                'Gangaputra Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'Mogili.reddy@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1382255' AS pod_id,
                'Musheerabad' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'Mogili.reddy@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1386716' AS pod_id,
                'New Bolarum' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'Mogili.reddy@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1237254' AS pod_id,
                'Yapral' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'Mogili.reddy@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1388311' AS pod_id,
                'Aparna Hill Park' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'mohammed.abdul@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1387634' AS pod_id,
                'Beeramguda' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'mohammed.abdul@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1380712' AS pod_id,
                'Botanical Garden' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'mohammed.abdul@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1381356' AS pod_id,
                'Hitech City' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'mohammed.abdul@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '737088' AS pod_id,
                'Madhapur' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'mohammed.abdul@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1385563' AS pod_id,
                'Nanakaramguda (Relocation)' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'mohammed.abdul@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1396027' AS pod_id,
                'Pragathi Nagar Phase 1' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'mohammed.abdul@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1084118' AS pod_id,
                'Puppalaguda2' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'mohammed.abdul@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1381278' AS pod_id,
                'Chinthal' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '587699' AS pod_id,
                'Gcw' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1061926' AS pod_id,
                'Kondapur' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1223630' AS pod_id,
                'Kondapur-2' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1386094' AS pod_id,
                'Kothaguda' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1397057' AS pod_id,
                'Madhapur' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '810364' AS pod_id,
                'Miyapur' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1181691' AS pod_id,
                'Nizampet5' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1386717' AS pod_id,
                'Suchitra' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1386269' AS pod_id,
                'Tcs Synergy Park' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'polavarapu.aravind@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1387564' AS pod_id,
                'Bachupally 2' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1381160' AS pod_id,
                'Gopanpally' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1261840' AS pod_id,
                'Hafeezpet' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1383129' AS pod_id,
                'Kukatpally' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1237255' AS pod_id,
                'Nalagandla' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1082432' AS pod_id,
                'Nizampet4' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1238352' AS pod_id,
                'Nizampet 6' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1389637' AS pod_id,
                'Pjr Layout' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1393827' AS pod_id,
                'Satadar Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1386815' AS pod_id,
                'Tellapur' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1386093' AS pod_id,
                'Venkata Ramana Colony' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'regunta.sudhakar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1386816' AS pod_id,
                'Attapur' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1391894' AS pod_id,
                'B N Reddy Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1387078' AS pod_id,
                'Bandlaguda' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1398749' AS pod_id,
                'Chanchalguda' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1311100' AS pod_id,
                'Charminar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1392530' AS pod_id,
                'Chintalkunta' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1181692' AS pod_id,
                'Kharmanghat_Kothapet_2' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1295144' AS pod_id,
                'Kodandaram Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '762613' AS pod_id,
                'Kothapet' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1397628' AS pod_id,
                'Mahesh Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1238351' AS pod_id,
                'New Malakpet' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'syed.zubairali@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1380523' AS pod_id,
                'Abhyudaya Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'tattikota.kumar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1396293' AS pod_id,
                'Alkapuri Township' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'tattikota.kumar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1382981' AS pod_id,
                'Arvind Nagar Colony' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'tattikota.kumar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1386268' AS pod_id,
                'Datar Manzil' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'tattikota.kumar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1387566' AS pod_id,
                'Narsinghi' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'tattikota.kumar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1223632' AS pod_id,
                'Puppalaguda-3' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'tattikota.kumar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1398453' AS pod_id,
                'Sheikpet' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'tattikota.kumar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1386533' AS pod_id,
                'Vikas Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'tattikota.kumar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1387565' AS pod_id,
                'Waverock' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'tattikota.kumar@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1389688' AS pod_id,
                'Allwyn Colony' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1380448' AS pod_id,
                'Balkampet' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1385944' AS pod_id,
                'Habsiguda' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1383572' AS pod_id,
                'Jublee Hills Checkpost' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1389638' AS pod_id,
                'Kalpataru' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '988472' AS pod_id,
                'Lakdikapul' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1382391' AS pod_id,
                'Masjid Banda' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1267913' AS pod_id,
                'Mithila Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1229994' AS pod_id,
                'Punjagutta' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1155152' AS pod_id,
                'Secunderabad-2' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '886521' AS pod_id,
                'Yosufguda' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                'vantipalli.sandeep@swiggy.in' AS com,
                'karthick.s@swiggy.in' AS dch
   UNION SELECT '1380621' AS pod_id,
                'Beck Bagan' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'abhishek.das1@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1169284' AS pod_id,
                'Haltu 1' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'abhishek.das1@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1384141' AS pod_id,
                'Itc Topsia' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'abhishek.das1@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1385840' AS pod_id,
                'Kasba' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'abhishek.das1@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1391896' AS pod_id,
                'Manicktala' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'abhishek.das1@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1384877' AS pod_id,
                'Satgram' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'abhishek.das1@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1135719' AS pod_id,
                'Tartala' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'abhishek.das1@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '901840' AS pod_id,
                'Tollygunge' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'abhishek.das1@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1396286' AS pod_id,
                'Bapuji Nagar' AS pod_name,
                'East' AS CLUSTER,
                'Bhubaneswar' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1389257' AS pod_id,
                'District Centre' AS pod_name,
                'East' AS CLUSTER,
                'Bhubaneswar' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1391904' AS pod_id,
                'Kiit' AS pod_name,
                'East' AS CLUSTER,
                'Bhubaneswar' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1237258' AS pod_id,
                'Garia' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1380524' AS pod_id,
                'Golf Green' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1167234' AS pod_id,
                'Haltu 2' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1388313' AS pod_id,
                'Lake Town' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1386270' AS pod_id,
                'Patuli' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1314370' AS pod_id,
                'Rajpur Sonapur' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1386096' AS pod_id,
                'Tiljala' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '867467' AS pod_id,
                'Ultadanga' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'samiul.basier@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1395725' AS pod_id,
                '45 Pally' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sohrab.ahmad@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1387079' AS pod_id,
                'Jagdishpur' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sohrab.ahmad@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1386097' AS pod_id,
                'Mani Square' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sohrab.ahmad@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1237259' AS pod_id,
                'New Town' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sohrab.ahmad@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1391895' AS pod_id,
                'Purabanchal' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sohrab.ahmad@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1387910' AS pod_id,
                'Rajarhat' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sohrab.ahmad@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '867466' AS pod_id,
                'Arjunpur' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1373486' AS pod_id,
                'Eco Park (New Town)' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1389000' AS pod_id,
                'Madhyamgram' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1382982' AS pod_id,
                'Manickpore' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1386913' AS pod_id,
                'Nagerbazar' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1395726' AS pod_id,
                'Rathtala' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1388197' AS pod_id,
                'Salt Lake Sector V' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1397622' AS pod_id,
                'Sinthi' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1382353' AS pod_id,
                'Talbagan' AS pod_name,
                'East' AS CLUSTER,
                'Kolkata' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1395730' AS pod_id,
                'Kadru' AS pod_name,
                'East' AS CLUSTER,
                'Ranchi' AS city,
                'sujay.poddar@swiggy.in' AS com,
                'markand.vyas1@swiggy.in' AS dch
   UNION SELECT '1397024' AS pod_id,
                'Bagaluru Road' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1382164' AS pod_id,
                'Bellahalli' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1396660' AS pod_id,
                'Bhartiya City' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '762611' AS pod_id,
                'Rk Hegde Nagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1390217' AS pod_id,
                'Kyalasanahalli' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1382656' AS pod_id,
                'Nagavara' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1386386' AS pod_id,
                'Puttanahalli' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1393565' AS pod_id,
                'Singapura' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '565140' AS pod_id,
                'Ylk' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1386712' AS pod_id,
                'Yelahanka New Town' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'kiran.r1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1387633' AS pod_id,
                'Cooke Town' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'rajat.jaiswal1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1382412' AS pod_id,
                'Dasappa Layout' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'rajat.jaiswal1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '816648' AS pod_id,
                'Ulsoor' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'rajat.jaiswal1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1386532' AS pod_id,
                'Hbr Layout' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'rajat.jaiswal1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1390218' AS pod_id,
                'Hrbr Layout' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'rajat.jaiswal1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1395722' AS pod_id,
                'Murgesh palya' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'rajat.jaiswal1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1394669' AS pod_id,
                'P and T Layout' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'rajat.jaiswal1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1313712' AS pod_id,
                'Shivaji Nagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'rajat.jaiswal1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1385942' AS pod_id,
                'Thigalarapalya' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'rajat.jaiswal1@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '788742' AS pod_id,
                'Banashankari' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'sangamesh.k@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '911032' AS pod_id,
                'Chamrajpet 1' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'sangamesh.k@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1380899' AS pod_id,
                'Hoshalli Extension' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'sangamesh.k@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1190778' AS pod_id,
                'Indiranagar 5' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'sangamesh.k@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1237709' AS pod_id,
                'Kumaraswamy Layout' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'sangamesh.k@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '911033' AS pod_id,
                'Laggere' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'sangamesh.k@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1396285' AS pod_id,
                'RR Nagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'sangamesh.k@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1387077' AS pod_id,
                'Uttarahalli' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'sangamesh.k@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1390219' AS pod_id,
                'Vajrahalli' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'sangamesh.k@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1380898' AS pod_id,
                'Bt Purshottam Layout' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'wilsonpeter.g@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1238349' AS pod_id,
                'Horamavu' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'wilsonpeter.g@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1082430' AS pod_id,
                'Kalyan Nagar 5' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'wilsonpeter.g@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1373485' AS pod_id,
                'Kr Puram' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'wilsonpeter.g@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1381969' AS pod_id,
                'Lingarajapuram' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'wilsonpeter.g@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '593243' AS pod_id,
                'Kng2' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'wilsonpeter.g@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1394670' AS pod_id,
                'Sobha Garrison' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'wilsonpeter.g@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1381559' AS pod_id,
                'Vivekananda Nagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'wilsonpeter.g@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1396467' AS pod_id,
                'Yeshwantpur' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'wilsonpeter.g@swiggy.in' AS com,
                'nasir.shariff@swiggy.in' AS dch
   UNION SELECT '1395427' AS pod_id,
                'Brindavan Gardens' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Guntur' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1394684' AS pod_id,
                'Medical College' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Guntur' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1398748' AS pod_id,
                'Gorantla' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Guntur' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1382259' AS pod_id,
                'Autonagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vijayawada' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1387707' AS pod_id,
                'Bhavanipuram' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vijayawada' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1388390' AS pod_id,
                'Labipet' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vijayawada' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1399348' AS pod_id,
                'Mytri Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vijayawada' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1382660' AS pod_id,
                'Payakapuram' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vijayawada' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1391901' AS pod_id,
                'Ramavarapadu' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vijayawada' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1398450' AS pod_id,
                'Tadepalle' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vijayawada' AS city,
                'kuncha.reddy@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1395433' AS pod_id,
                'Public Garden' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Warangal' AS city,
                'mohammed.abdul@swiggy.in' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1382440' AS pod_id,
                'Dwarka Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vizag' AS city,
                'thigutla.srinath@scootsy.com' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1388113' AS pod_id,
                'Madhurwada' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vizag' AS city,
                'thigutla.srinath@scootsy.com' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1381358' AS pod_id,
                'Mvp Double Road' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vizag' AS city,
                'thigutla.srinath@scootsy.com' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1345681' AS pod_id,
                'Nad Junction' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vizag' AS city,
                'thigutla.srinath@scootsy.com' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1309584' AS pod_id,
                'Nawab Nagar' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vizag' AS city,
                'thigutla.srinath@scootsy.com' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1395432' AS pod_id,
                'TPT Colony' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Vizag' AS city,
                'thigutla.srinath@scootsy.com' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1398448' AS pod_id,
                'VK Puram' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Tirupati' AS city,
                'thigutla.srinath@scootsy.com ' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1397621' AS pod_id,
                'Alwal' AS pod_name,
                'AP & TS' AS CLUSTER,
                'Hyderabad' AS city,
                '' AS com,
                'nishanth.s@swiggy.in' AS dch
   UNION SELECT '1388112' AS pod_id,
                'Beml' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '565139' AS pod_id,
                'Cvr' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1388682' AS pod_id,
                'Guttahalli' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1231805' AS pod_id,
                'Hebbal' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1393563' AS pod_id,
                'Kaggadasapura' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1382868' AS pod_id,
                'Nanjappa Circle' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1229990' AS pod_id,
                'Sahakar Nagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '816646' AS pod_id,
                'Sanjay Nagar 1' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1216213' AS pod_id,
                'Sanjay Nagar 5' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '969380' AS pod_id,
                'Sanjay Nagar 3' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'eshwar.v@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1384788' AS pod_id,
                'Balagere' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'hariprasad.a@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1392080' AS pod_id,
                'Bda Complex Hsr' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'hariprasad.a@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '788740' AS pod_id,
                'Krg3' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'hariprasad.a@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1113105' AS pod_id,
                'Hsr 2' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'hariprasad.a@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1231052' AS pod_id,
                'Hsr 3' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'hariprasad.a@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1386090' AS pod_id,
                'Hsr Sec 2' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'hariprasad.a@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1387562' AS pod_id,
                'Panathur' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'hariprasad.a@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1395720' AS pod_id,
                'Somasoundarapalya' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'hariprasad.a@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1387560' AS pod_id,
                'Anantnagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1239157' AS pod_id,
                'Begur' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1385835' AS pod_id,
                'Beratena Agrahara' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1393562' AS pod_id,
                'DLF Woodland' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1388681' AS pod_id,
                'Hulimavu' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1382870' AS pod_id,
                'Mylasandra' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1384787' AS pod_id,
                'Neeladri Nagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1380710' AS pod_id,
                'Rayasandra' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1381848' AS pod_id,
                'Vinayaka Nagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1398444' AS pod_id,
                'Attavar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Mangalore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1394683' AS pod_id,
                'Kottara' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Mangaluru' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1386098' AS pod_id,
                'Chamundi Temple' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Mysore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1397623' AS pod_id,
                'Mysore East' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Mysore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1395429' AS pod_id,
                'Mysore University' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Mysore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1239166' AS pod_id,
                'Vani Vilas' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Mysore' AS city,
                'pradeep.gowda@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1374258' AS pod_id,
                'Bhoganhalli (Kadubeesanahalli)' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'shaik.mansoor2@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1392421' AS pod_id,
                'CARMELARAM' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'shaik.mansoor2@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1382707' AS pod_id,
                'Gottigere' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'shaik.mansoor2@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1392660' AS pod_id,
                'Haralur Megapod' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'shaik.mansoor2@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1385836' AS pod_id,
                'Kasavanahalli' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'shaik.mansoor2@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1381157' AS pod_id,
                'Mullur' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'shaik.mansoor2@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1386714' AS pod_id,
                'Orr - Rmz' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'shaik.mansoor2@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1387903' AS pod_id,
                'Salapuria Sancity' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'shaik.mansoor2@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '854382' AS pod_id,
                'Sarjapur 2' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'shaik.mansoor2@swiggy.in' AS com,
                'rakesh.i@swiggy.in' AS dch
   UNION SELECT '1382494' AS pod_id,
                'Jangpura' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lallan.prasad@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1383851' AS pod_id,
                'Lodi Colony' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lallan.prasad@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1394450' AS pod_id,
                'Mehroli' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lallan.prasad@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1387704' AS pod_id,
                'Nfc' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lallan.prasad@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '810368' AS pod_id,
                'Munirika' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lallan.prasad@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1391898' AS pod_id,
                'Gur Mandi' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lokesh.punia@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1062419' AS pod_id,
                'Karol Bagh2' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lokesh.punia@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1229997' AS pod_id,
                'Patel Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lokesh.punia@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1062023' AS pod_id,
                'Rohini' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lokesh.punia@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1388196' AS pod_id,
                'Adarsh Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Jaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1382290' AS pod_id,
                'Bani Park' AS pod_name,
                'North' AS CLUSTER,
                'Jaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1382166' AS pod_id,
                'Krishna Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Jaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1346769' AS pod_id,
                'Lalkothi' AS pod_name,
                'North' AS CLUSTER,
                'Jaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1381754' AS pod_id,
                'Mansarovar' AS pod_name,
                'North' AS CLUSTER,
                'Jaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1387909' AS pod_id,
                'Ns Road' AS pod_name,
                'North' AS CLUSTER,
                'Jaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1386095' AS pod_id,
                'Patrika Gate' AS pod_name,
                'North' AS CLUSTER,
                'Jaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1395724' AS pod_id,
                'Pratap Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Jaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1398451' AS pod_id,
                'Pahada' AS pod_name,
                'North' AS CLUSTER,
                'Udaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1397089' AS pod_id,
                'Surajpole' AS pod_name,
                'North' AS CLUSTER,
                'Udaipur' AS city,
                'Raj.dashlaniya@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1229998' AS pod_id,
                'Safdarjung Enclave' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Santosh.v@scootsy.com ' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1382964' AS pod_id,
                'Saket Metro Station' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Santosh.v@scootsy.com ' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1384512' AS pod_id,
                'Yusuf Sarai' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Santosh.v@scootsy.com ' AS com,
                'sparsh.agarwal@swiggy.in' AS dch
   UNION SELECT '1380671' AS pod_id,
                'Babarpur' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'anil.sarswat@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1388689' AS pod_id,
                'Dilshad Colony' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'anil.sarswat@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1099459' AS pod_id,
                'Dilshad Garden 2' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'anil.sarswat@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1385945' AS pod_id,
                'Keventers' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'anil.sarswat@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1384511' AS pod_id,
                'Pv Ranikhet' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'anil.sarswat@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1381835' AS pod_id,
                'Rajendra Place' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'anil.sarswat@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '816651' AS pod_id,
                'Vardhman Mall' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'anil.sarswat@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1383826' AS pod_id,
                'Budella' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'arpita.sharma@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '762550' AS pod_id,
                'Janakpuri' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'arpita.sharma@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1062420' AS pod_id,
                'Janakpuri_ Rajouri' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'arpita.sharma@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1387705' AS pod_id,
                'Nawada' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'arpita.sharma@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1383383' AS pod_id,
                'Pochanpur' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'arpita.sharma@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1388690' AS pod_id,
                'Rajapuri' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'arpita.sharma@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '649851' AS pod_id,
                'Rajouri' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'arpita.sharma@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1383384' AS pod_id,
                'Shubham Enclave' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'arpita.sharma@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1398755' AS pod_id,
                'AIIMS' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lallan.prasad@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1389690' AS pod_id,
                'Cr Park' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lallan.prasad@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '406774' AS pod_id,
                'Malviya' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lallan.prasad@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1386536' AS pod_id,
                'Vasant Square Mall' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lallan.prasad@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1294674' AS pod_id,
                'Diving Road' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lokesh.punia@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1386271' AS pod_id,
                'Kohat Enclave' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lokesh.punia@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1390225' AS pod_id,
                'Shakti Vihar' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lokesh.punia@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1386535' AS pod_id,
                'Subhash Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'lokesh.punia@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1382871' AS pod_id,
                'Chandar Vihar' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Mithlesh.kumar@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1386719' AS pod_id,
                'Cp' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Mithlesh.kumar@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1384143' AS pod_id,
                'Kakrola Dwarka' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Mithlesh.kumar@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '649841' AS pod_id,
                'Laxmi N' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Mithlesh.kumar@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1099458' AS pod_id,
                'Laxmi Nagar2' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Mithlesh.kumar@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1381851' AS pod_id,
                'Mahavir Enclave' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Mithlesh.kumar@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1230886' AS pod_id,
                'Mayur Vihar 2' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Mithlesh.kumar@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1325203' AS pod_id,
                'Timarpur' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Mithlesh.kumar@swiggy.in' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1386948' AS pod_id,
                'East Of Kailash' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Pankaj.Kumar08@scootsy.com ' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1267917' AS pod_id,
                'Kailash Colony' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Pankaj.Kumar08@scootsy.com ' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1382291' AS pod_id,
                'Masjid Moth' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Pankaj.Kumar08@scootsy.com ' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1381357' AS pod_id,
                'Jasola' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Santosh.v@scootsy.com ' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1261842' AS pod_id,
                'Kirti Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Vijay.t@scootsy.com' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1099457' AS pod_id,
                'Tilak Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Vijay.t@scootsy.com' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1389689' AS pod_id,
                'Uttam Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Delhi' AS city,
                'Vijay.t@scootsy.com' AS com,
                'sparsh.agarwal@swiggy.in ' AS dch
   UNION SELECT '1393826' AS pod_id,
                'Nehru Colony' AS pod_name,
                'North' AS CLUSTER,
                'Faridabad' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1347907' AS pod_id,
                'Sector 12' AS pod_name,
                'North' AS CLUSTER,
                'Faridabad' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1391900' AS pod_id,
                'Sector 20B' AS pod_name,
                'North' AS CLUSTER,
                'Faridabad' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1390226' AS pod_id,
                'Sector 21 A' AS pod_name,
                'North' AS CLUSTER,
                'Faridabad' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1391899' AS pod_id,
                'Sector 37' AS pod_name,
                'North' AS CLUSTER,
                'Faridabad' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1394451' AS pod_id,
                'Sector 14 Main' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1381563' AS pod_id,
                'Sector 20 Ggn' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1298919' AS pod_id,
                'Sector 28' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1381279' AS pod_id,
                'Greenwood City' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1384144' AS pod_id,
                'Sikandapura Le Meridian' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'adrita.dutta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1380623' AS pod_id,
                'Dlf Cyber Hub' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'apurv.gupta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1395428' AS pod_id,
                'DLF Sec 54' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'apurv.gupta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1265812' AS pod_id,
                'Jharsa Road (Sec 39)' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'apurv.gupta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1384513' AS pod_id,
                'Om Vihar' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'apurv.gupta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1385646' AS pod_id,
                'Samaspur' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'apurv.gupta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1389005' AS pod_id,
                'Sector 104, Gurgaon' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'apurv.gupta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1389006' AS pod_id,
                'Sector 10A' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'apurv.gupta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1383827' AS pod_id,
                'Sector 39 Jharsa(Franchisee)' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'apurv.gupta@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1397088' AS pod_id,
                'Golden Temple' AS pod_name,
                'North' AS CLUSTER,
                'Amritsar' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1385943' AS pod_id,
                'Gillco Parkhills' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1397025' AS pod_id,
                'Kurali Road' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1385562' AS pod_id,
                'Peermuchalla' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1387904' AS pod_id,
                'Phse 3B' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1387905' AS pod_id,
                'Sec 10 Panchkula' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1387906' AS pod_id,
                'Sec 67 Chandigarh' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1389004' AS pod_id,
                'Sec 7 Panchkula' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1383823' AS pod_id,
                'Sector 23' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1339713' AS pod_id,
                'Sector 63' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1390220' AS pod_id,
                'Shivalik City' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1381441' AS pod_id,
                'Sub City Center' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1386912' AS pod_id,
                'Sunny Enclave' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1388997' AS pod_id,
                'Vip Road' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1348435' AS pod_id,
                'Zirakpur' AS pod_name,
                'North' AS CLUSTER,
                'Chandigarh' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1395727' AS pod_id,
                'Hargobind Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Ludhiana' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1397034' AS pod_id,
                'Pritam Nagar' AS pod_name,
                'North' AS CLUSTER,
                'Ludhiana' AS city,
                'charanjeet.s@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1381444' AS pod_id,
                'Sector 88' AS pod_name,
                'North' AS CLUSTER,
                'Faridabad' AS city,
                'lokesh.patel@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1382659' AS pod_id,
                'Av Phase 3' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'lokesh.patel@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1384146' AS pod_id,
                'Choma Village' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'lokesh.patel@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1239163' AS pod_id,
                'Dlf Phase 1 (Sec 42)' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'lokesh.patel@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1397028' AS pod_id,
                'Gehlot Farm' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'lokesh.patel@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1389633' AS pod_id,
                'Sapphire Mall' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'lokesh.patel@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1392083' AS pod_id,
                'Sector 53' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'lokesh.patel@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1278169' AS pod_id,
                'Sector 67' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'lokesh.patel@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1382258' AS pod_id,
                'Tulip Society Sec 70' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'lokesh.patel@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '762551' AS pod_id,
                'Spencer' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'Mithun.kumar@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1387911' AS pod_id,
                'Sector 57' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'Mithun.kumar@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1387568' AS pod_id,
                'Vatika City Ggn' AS pod_name,
                'North' AS CLUSTER,
                'Gurgaon' AS city,
                'Mithun.kumar@swiggy.in' AS com,
                'utkarsh.maarut@swiggy.in' AS dch
   UNION SELECT '1382708' AS pod_id,
                'Airport Road' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'anil.thakare1@swiggy.in ' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1385566' AS pod_id,
                'Alpha Homes' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'anil.thakare1@swiggy.in ' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1383135' AS pod_id,
                'Aundh Gaon' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'anil.thakare1@swiggy.in ' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1386537' AS pod_id,
                'Goodwill Square Lohegaon' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'anil.thakare1@swiggy.in ' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1385564' AS pod_id,
                'Kalyani Nagar' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'anil.thakare1@swiggy.in ' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1382710' AS pod_id,
                'Sayaji Hotel' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'anil.thakare1@swiggy.in ' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1390228' AS pod_id,
                'Shivrajnagar' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'anil.thakare1@swiggy.in ' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1380714' AS pod_id,
                'Wagholi' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'anil.thakare1@swiggy.in ' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1394682' AS pod_id,
                'Alto Porvorim' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1386814' AS pod_id,
                'Baga' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1392081' AS pod_id,
                'Cujira Ward' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1386942' AS pod_id,
                'Dabolim' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1385837' AS pod_id,
                'Mapusa' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1390351' AS pod_id,
                'Margao' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1113107' AS pod_id,
                'North Goa' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1386927' AS pod_id,
                'Panji' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1382351' AS pod_id,
                'Porvorim' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1392082' AS pod_id,
                'Siolim Goa' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1381971' AS pod_id,
                'Taliegao' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1387908' AS pod_id,
                'Vagator' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Goa' AS city,
                'brandon.viegas@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1383574' AS pod_id,
                'Atma Nagar' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1388453' AS pod_id,
                'Balewadi' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1393573' AS pod_id,
                'Dattawadi' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1389002' AS pod_id,
                'Dhankawadi' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1278175' AS pod_id,
                'Hinjewadi It Park' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1385565' AS pod_id,
                'Hinjewadi Phase 1' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1382965' AS pod_id,
                'Hinjewadi Phase 3' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1393574' AS pod_id,
                'Kunal Icon Pimple Saudagar' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1383575' AS pod_id,
                'Mohan Nagar Society' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1386163' AS pod_id,
                'Nanded City' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1390229' AS pod_id,
                'Pashan Gaon' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1385649' AS pod_id,
                'Pranjali Patil Nagar' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1389254' AS pod_id,
                'Ravet' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1389001' AS pod_id,
                'Samarth Colony' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1393575' AS pod_id,
                'Vikas Udyan' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '737089' AS pod_id,
                'Warje' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'chandrakant.g@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1384148' AS pod_id,
                'Azad Chowk Kothrud' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1394673' AS pod_id,
                'Bhekrai' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1383853' AS pod_id,
                'Hadapsar' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1382354' AS pod_id,
                'Kausar Bagh' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '713116' AS pod_id,
                'Kharadi' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1389691' AS pod_id,
                'Kharadi 2' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1381445' AS pod_id,
                'Manjari' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1382709' AS pod_id,
                'Nyati' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1397626' AS pod_id,
                'Kharadi' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1388314' AS pod_id,
                'Wanwadi New' AS pod_name,
                'Pune & Goa' AS CLUSTER,
                'Pune' AS city,
                'mahavir.koli@swiggy.in' AS com,
                'vijay.dighe@swiggy.in' AS dch
   UNION SELECT '1397037' AS pod_id,
                'Adgaon' AS pod_name,
                'West' AS CLUSTER,
                'Nashik' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1388452' AS pod_id,
                'Bombay Naka' AS pod_name,
                'West' AS CLUSTER,
                'Nashik' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1389256' AS pod_id,
                'College Road' AS pod_name,
                'West' AS CLUSTER,
                'Nashik' AS city,
                'durvesh.gholap@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1383570' AS pod_id,
                'Bodakdev' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1393824' AS pod_id,
                'Celebration Mall' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1385348' AS pod_id,
                'Gurukul' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1388195' AS pod_id,
                'Motera' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1385642' AS pod_id,
                'Navrangpura' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1386812' AS pod_id,
                'Panchwati' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1385834' AS pod_id,
                'Prahladnagar' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1387076' AS pod_id,
                'Sargasan Gandhinagar' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1397023' AS pod_id,
                'Science City' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1388194' AS pod_id,
                'Vandematram' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1386811' AS pod_id,
                'Vejalpur' AS pod_name,
                'West' AS CLUSTER,
                'Ahmedabad' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1395731' AS pod_id,
                'Civil Hospital' AS pod_name,
                'West' AS CLUSTER,
                'Rajkot' AS city,
                'nishant.kumarsingh@scootsy.com' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1393825' AS pod_id,
                'Aashima Mall' AS pod_name,
                'West' AS CLUSTER,
                'Bhopal' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1397619' AS pod_id,
                'Anand nagar' AS pod_name,
                'West' AS CLUSTER,
                'Bhopal' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1399345' AS pod_id,
                'MP Nagar' AS pod_name,
                'West' AS CLUSTER,
                'Bhopal' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '973251' AS pod_id,
                'Badi Bhamori' AS pod_name,
                'West' AS CLUSTER,
                'Indore' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1382352' AS pod_id,
                'Bombay Hospital' AS pod_name,
                'West' AS CLUSTER,
                'Indore' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1382165' AS pod_id,
                'Navlakha - Mim' AS pod_name,
                'West' AS CLUSTER,
                'Indore' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1386817' AS pod_id,
                'Saket Square' AS pod_name,
                'West' AS CLUSTER,
                'Indore' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1388386' AS pod_id,
                'Usha Nagar' AS pod_name,
                'West' AS CLUSTER,
                'Indore' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1395733' AS pod_id,
                'Adajan gam' AS pod_name,
                'West' AS CLUSTER,
                'Surat' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1382355' AS pod_id,
                'Bharthana' AS pod_name,
                'West' AS CLUSTER,
                'Surat' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1385948' AS pod_id,
                'Majura Gate' AS pod_name,
                'West' AS CLUSTER,
                'Surat' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1397042' AS pod_id,
                'Mota Varcha' AS pod_name,
                'West' AS CLUSTER,
                'Surat' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1397039' AS pod_id,
                'Palanpur Gam' AS pod_name,
                'West' AS CLUSTER,
                'Surat' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1387706' AS pod_id,
                'Punagam' AS pod_name,
                'West' AS CLUSTER,
                'Surat' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1394674' AS pod_id,
                'Vesu pod' AS pod_name,
                'West' AS CLUSTER,
                'Surat' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1385567' AS pod_id,
                'Diwalipura' AS pod_name,
                'West' AS CLUSTER,
                'Vadodara' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1388315' AS pod_id,
                'Gotri Road' AS pod_name,
                'West' AS CLUSTER,
                'Vadodara' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1391902' AS pod_id,
                'Nilambar Palms' AS pod_name,
                'West' AS CLUSTER,
                'Vadodara' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1389255' AS pod_id,
                'Ratri Bazaar' AS pod_name,
                'West' AS CLUSTER,
                'Vadodara' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1387082' AS pod_id,
                'Yakutpura' AS pod_name,
                'West' AS CLUSTER,
                'Vadodara' AS city,
                'piyush.singh1@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1392084' AS pod_id,
                'Byramji' AS pod_name,
                'West' AS CLUSTER,
                'Nagpur' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1393571' AS pod_id,
                'Mahal pod' AS pod_name,
                'West' AS CLUSTER,
                'Nagpur' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1392532' AS pod_id,
                'Manish Nagar' AS pod_name,
                'West' AS CLUSTER,
                'Nagpur' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1397035' AS pod_id,
                'Wardhaman Nagar' AS pod_name,
                'West' AS CLUSTER,
                'Nagpur' AS city,
                'shivsharan.yadav@swiggy.in' AS com,
                'vilash.arjun@swiggy.in' AS dch
   UNION SELECT '1388383' AS pod_id,
                'Bandapura' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'akshay.dash@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '854379' AS pod_id,
                'Kalyan Nagar3' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'akshay.dash@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1389251' AS pod_id,
                'Kannamangala' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'akshay.dash@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1380447' AS pod_id,
                'Seegehalli' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'akshay.dash@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1384139' AS pod_id,
                'Tin Factory' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'akshay.dash@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1383715' AS pod_id,
                'Upkar Layout' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'akshay.dash@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '762610' AS pod_id,
                'Marathahalli 2' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'akshay.dash@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '649831' AS pod_id,
                'Bellandur' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'Manohar.3@Swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1382655' AS pod_id,
                'Doodswarth Enclave' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'Manohar.3@Swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1370332' AS pod_id,
                'Gunjur' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'Manohar.3@Swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1380521' AS pod_id,
                'Jhonson Mrkt' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'Manohar.3@Swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1346768' AS pod_id,
                'Mahadevpura' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'Manohar.3@Swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1393564' AS pod_id,
                'Sg Palya' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'Manohar.3@Swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1382254' AS pod_id,
                'Yemalur' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'Manohar.3@Swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1388998' AS pod_id,
                'Adarsh Palm Retreat' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'prakash.t1@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1381021' AS pod_id,
                'Chandra Layt' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'prakash.t1@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1387561' AS pod_id,
                'Gandhipura' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'prakash.t1@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1390216' AS pod_id,
                'Iblur' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'prakash.t1@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1395425' AS pod_id,
                'Kalamandir' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'prakash.t1@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1382350' AS pod_id,
                'Kartik Nagar' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'prakash.t1@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1388382' AS pod_id,
                'Koramangala 1St Block' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'prakash.t1@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '901839' AS pod_id,
                'Koramangala 2' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'prakash.t1@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1380522' AS pod_id,
                'Thubarahalli' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'prakash.t1@swiggy.in' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1397048' AS pod_id,
                'HSR' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                '' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1386385' AS pod_id,
                'Bengaluru Badootaa' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                '' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1181690' AS pod_id,
                'Chramjpet3' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                '' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1190774' AS pod_id,
                'Jp Nagar 5' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                '' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1398437' AS pod_id,
                'Kengeri Satellite Town' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                '' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1397796' AS pod_id,
                'Ns Palya' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                '' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1382349' AS pod_id,
                'Ranka Colony' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                '' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1334211' AS pod_id,
                'Sai Enclave' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                '' AS com,
                'yashwanth.s@swiggy.in' AS dch
   UNION SELECT '1395434' AS pod_id,
                'Hoodi' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'richard.a@scootsy.com' AS com,
                'yashwanth.s@swiggy.in ' AS dch
   UNION SELECT '1395721' AS pod_id,
                'Kodihalli - Mega POD' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'richard.a@scootsy.com' AS com,
                'yashwanth.s@swiggy.in ' AS dch
   UNION SELECT '1396284' AS pod_id,
                'Koramanagala' AS pod_name,
                'KA & KL' AS CLUSTER,
                'Bangalore' AS city,
                'richard.a@scootsy.com' AS com,
                'yashwanth.s@swiggy.in ' AS dch),
     lfr AS
  (SELECT lfr.reminder_id,
          fr.organization,
          fr.tz_offset AS tz_offset_sec,
          fr.form_id,
          l.location_name AS LOCATION,
          to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset AS reminded_at,
          to_timestamp(lfr.reminder_window_end/1000) + interval '1 sec'*fr.tz_offset AS reminder_window_end,
          lfr.form_response_id,
          CASE
              WHEN responded_at = 0 THEN NULL
              ELSE to_timestamp(lfr.responded_at/1000) + interval '1 sec'*fr.tz_offset
          END AS responded_at
   FROM location_form_reminders lfr
   JOIN form_reminders fr ON fr.id = lfr.reminder_id
   JOIN locations l ON lfr.location_id = l.id
   WHERE l.location_name NOT ILIKE 'KNOW'
     AND l.location_name NOT ILIKE 'HQ'
     AND l.location_name NOT ILIKE '%HO'
     AND to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*fr.tz_offset between date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata') - interval '1 day' and date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')
     AND fr.form_id IN ('-O3WHxW8vkcfCKYmKK2Y',
                        '-O0Cw32tUETcxfnzf2PR',
                        '-O9xEQ5ujY1RFVuP6c-G',
                        '-O9xFFjif-72YtWYQIqn',
                        '-O11A2dcpiaMx8pQedRf',
                        '-O11ADimkVVHNqz_oeMT',
                        '-O8qdhuV9zaoXTpQiPOY',
                        '-O9KR9ftEE-NsUUgtCtA',
                        '-O9U-6iKlPyBJVMM6gfk',
                        '-O9AEYuBtu2p_952hrbR',
                        '-O9Dps0NIo2VS7s5NPuh',
                        '-OAvuQACgKHCcdHFkm0L',
                        '-OB4CVmT_YAytFR2fty7',
                        '-OB4xcGu1NqT84w0lAWQ',
                        '-O9xC1H6RHlhY6rnKKSW',
                        '-O9U1GGkwZWt_Vs6okDW',
                        '-OB4xxAJqHUO99TRB_io',
                        '-OB4z2473dKeZ34McBIV',
                        '-OB4zWin85ZrjPUjH0RV',
                        '-OB4zm7TVqXaKK3J0vAX',
                        '-OB5-5PzkC26eek0Bk-1',
                        '-OB5-Q1oguPmrJlRlBnH',
                        '-OB5-kLCkZWwy65-Ek6h',
                        '-OB505iZAJ8wJ0zZxcFM',
                        '-O3CRSzHs_yr8MeznWkv',
                        '-OB51eSXMa_nSoibv6yS',
                        '-OB525WEclHOXV6JYtJn',
                        '-OB51wGxzBWxhStUNtqv',
                        '-OB52IvLT3rJTvAM7wLT',
                        '-OB52TuE5WfUdYkJdmrE',
                        '-OB52jx59NEjUjPBixqy',
                        '-OB52ttmR2iTHizVPXwE',
                        '-OB55VCsN1K47jdOc-N2',
                        '-OB5622pYYZHwe2fCC1W',
                        '-OB56cNfUDEhTxUPhJ4S',
                        '-OB56mQetguLSxb-mTv6',
                        '-OB57bk-9BG-rX7wAceu',
                        '-OAIHk3YCxnTfjV_fyGr',
                        '-OAIJndZxwVht8750Zc6',
                        '-OAIsM27j29lvnM9Br5O',
                        '-OAIx7irPIBo-9cKLh_y',
                        '-OALkeIDkVHTQtxyEVne',
                        '-OALrG4eIk_Kaw-LaJG6',
                        '-OB8utwNF_o5UKdxabUc',
                        '-O9xI_JjhMrVzTAXkh_F',
                        '-OAvN4-5jv-XvXPhQEeM',
                        '-OAvPLR9pQLC_wvRpX0Y',
                        '-OAvQgdymG5aSTHcrVQR',
                        '-OAvVUTteJqBgqdYYJgq',
                        '-OAvVhmAOQCKn9Ln_JC-',
                        '-OAvVvs7yNtCfVItyUr4',
                        '-OAvWIJh_dc1cSU8uJgq',
                        '-OAvWV2dPw9S0L6KWBlb',
                        '-OAvb8LGJYxjlH_YrSRb',
                        '-OAvWvojjYv0Cxl9uTai',
                        '-OAvuXQ5wpvOziRxyIG5',
                        '-OAw2sT8UNJSi4Jcc4NA',
                        '-OBAL68W_bLx6qrgfVjm',
                        '-OB0_uO6Q4lBeasMViQT',
                        '-OB56yx-t8HP7oBY0JQX',
                        '-OB0_OEwgHSkOq9KOr7P')
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9),
     fs AS
  (SELECT DISTINCT ON ((submit_date AT TIME ZONE 'Asia/Kolkata')::date,
                       form_id) fs.*
   FROM form_submissions fs
   WHERE fs.location NOT ILIKE 'KNOW'
     AND fs.location NOT ILIKE 'HQ'
     AND fs.location NOT ILIKE '%HO'
     AND fs.submit_date AT TIME ZONE 'Asia/Kolkata' between date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata') - interval '1 day' and date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')
     AND fs.form_id IN ('-O3WHxW8vkcfCKYmKK2Y',
                        '-O0Cw32tUETcxfnzf2PR',
                        '-O9xEQ5ujY1RFVuP6c-G',
                        '-O9xFFjif-72YtWYQIqn',
                        '-O11A2dcpiaMx8pQedRf',
                        '-O11ADimkVVHNqz_oeMT',
                        '-O8qdhuV9zaoXTpQiPOY',
                        '-O9KR9ftEE-NsUUgtCtA',
                        '-O9U-6iKlPyBJVMM6gfk',
                        '-O9AEYuBtu2p_952hrbR',
                        '-O9Dps0NIo2VS7s5NPuh',
                        '-OAvuQACgKHCcdHFkm0L',
                        '-OB4CVmT_YAytFR2fty7',
                        '-OB4xcGu1NqT84w0lAWQ',
                        '-O9xC1H6RHlhY6rnKKSW',
                        '-O9U1GGkwZWt_Vs6okDW',
                        '-OB4xxAJqHUO99TRB_io',
                        '-OB4z2473dKeZ34McBIV',
                        '-OB4zWin85ZrjPUjH0RV',
                        '-OB4zm7TVqXaKK3J0vAX',
                        '-OB5-5PzkC26eek0Bk-1',
                        '-OB5-Q1oguPmrJlRlBnH',
                        '-OB5-kLCkZWwy65-Ek6h',
                        '-OB505iZAJ8wJ0zZxcFM',
                        '-O3CRSzHs_yr8MeznWkv',
                        '-OB51eSXMa_nSoibv6yS',
                        '-OB525WEclHOXV6JYtJn',
                        '-OB51wGxzBWxhStUNtqv',
                        '-OB52IvLT3rJTvAM7wLT',
                        '-OB52TuE5WfUdYkJdmrE',
                        '-OB52jx59NEjUjPBixqy',
                        '-OB52ttmR2iTHizVPXwE',
                        '-OB55VCsN1K47jdOc-N2',
                        '-OB5622pYYZHwe2fCC1W',
                        '-OB56cNfUDEhTxUPhJ4S',
                        '-OB56mQetguLSxb-mTv6',
                        '-OB57bk-9BG-rX7wAceu',
                        '-OAIHk3YCxnTfjV_fyGr',
                        '-OAIJndZxwVht8750Zc6',
                        '-OAIsM27j29lvnM9Br5O',
                        '-OAIx7irPIBo-9cKLh_y',
                        '-OALkeIDkVHTQtxyEVne',
                        '-OALrG4eIk_Kaw-LaJG6',
                        '-OB8utwNF_o5UKdxabUc',
                        '-O9xI_JjhMrVzTAXkh_F',
                        '-OAvN4-5jv-XvXPhQEeM',
                        '-OAvPLR9pQLC_wvRpX0Y',
                        '-OAvQgdymG5aSTHcrVQR',
                        '-OAvVUTteJqBgqdYYJgq',
                        '-OAvVhmAOQCKn9Ln_JC-',
                        '-OAvVvs7yNtCfVItyUr4',
                        '-OAvWIJh_dc1cSU8uJgq',
                        '-OAvWV2dPw9S0L6KWBlb',
                        '-OAvb8LGJYxjlH_YrSRb',
                        '-OAvWvojjYv0Cxl9uTai',
                        '-OAvuXQ5wpvOziRxyIG5',
                        '-OAw2sT8UNJSi4Jcc4NA',
                        '-OBAL68W_bLx6qrgfVjm',
                        '-OB0_uO6Q4lBeasMViQT',
                        '-OB56yx-t8HP7oBY0JQX',
                        '-OB0_OEwgHSkOq9KOr7P')
   ORDER BY (submit_date AT TIME ZONE 'Asia/Kolkata')::date,
            form_id,
            submit_date)
SELECT lfr.organization AS "Organization",
       lm.cluster AS "Cluster",
       lm.city AS "City",
       coalesce(lm.pod_id, regexp_replace(lfr."location", '([0-9]+).*', '\1')) AS "Pod ID",
       lm.pod_name AS "Pod Name",
       lm.com AS "COM",
       lm.dch AS "DCH",
       (lfr.reminded_at)::date AS "Date",
       lfr.form_id AS "Routine KNID",
       n.title AS "Routine Name",
       lfr.reminded_at AS "Reminded At",
	   case when (lfr.reminded_at)::time between '06:00:01' and '12:00:01' then '1 - Morning'
	   when (lfr.reminded_at)::time between '12:00:01' and '20:00:01' then '2 - Afternoon'
	   else '3 - Night' end as "Shift",	   
                                   CASE
                                       WHEN fs.submit_date IS NULL THEN 'Missed'
                                       WHEN fs.submit_date <= lfr.reminder_window_end THEN 'Compliant'
                                       WHEN fs.submit_date > lfr.reminder_window_end THEN 'Done Late'
                                       ELSE NULL
                                   END AS "Status",
                                   CASE
                                       WHEN fs.submit_date IS NULL THEN 0
                                       WHEN fs.submit_date <= lfr.reminder_window_end THEN 1
                                       WHEN fs.submit_date > lfr.reminder_window_end THEN 0.5
                                       ELSE NULL
                                   END AS "Compliance Score",
                                   CASE
                                       WHEN fs.submit_date IS NULL THEN 0.0
                                       ELSE 1.0
                                   END AS "Completion Score",
                                   fs.response_id AS "Submission KNID"
FROM lfr
JOIN nuggets n ON lfr.form_id = n.id
LEFT OUTER JOIN fs ON fs.form_id = lfr.form_id
AND (fs.submit_date + interval '1 sec'*lfr.tz_offset_Sec)::date = (lfr.reminded_at)::date
LEFT OUTER JOIN lm ON regexp_replace(lfr."location", '([0-9]+).*', '\1') = lm.pod_id
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
		 16
ORDER BY 11, 10, 1, 2, 3, 4
```

---

## Instamart SCORM Quiz Scores_Instamart SCORM Quiz Scores.sql

**Tables referenced:** courses, scorm_progress, user_details

**Columns needing snake_case conversion:**

- `userTags` -> `user_tags` (alias: `user_tags AS "userTags"`)


**Original Query:**

```sql
-- Data Source: Instamart SCORM Quiz Scores
-- Dashboard: Instamart SCORM Quiz Scores
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:59:33
-- ============================================================

SELECT parent_id AS "Course ID",
       c.name AS "Course Title",
       ud.identifier AS "Employee ID",
	   ud.first_name||' '||ud.last_name AS "Employee Name",
       initcap(PROFILE -> 'userTags' -> 'role' -> 0 ->> 'value') AS "Role",
                                           initcap(PROFILE -> 'userTags' -> 'city' -> 0 ->> 'value') AS "City",
                                                                               initcap(PROFILE -> 'userTags' -> 'store' -> 0 ->> 'value') AS "Store",
       to_timestamp(max(session_start_at)/1000) AT TIME ZONE 'Asia/Kolkata' AS "Latest Attempt At",
                                                             max(score) AS "Score %"
FROM scorm_progress sp
JOIN user_details ud ON sp.user_id = ud.uuid
JOIN courses c ON sp.parent_id = c.id
WHERE ud.organization = 'swiggy-mart-whirlpool'
  AND completion_status = 'completed'
GROUP BY 1,
         2,
         3,
         4, 5, 6, 7
ORDER BY 2,
        8,6, 7, 5 desc
```

---

## Instamart SM Gemba Adoption_GEMBA Walk Adoption.sql

**Tables referenced:** expected_sm, form_responses, form_submissions, fs, generate_series, location_map, nuggets, public.locations, public.user_details, sm_compliance, sm_forms, sm_responses

**Original Query:**

```sql
-- Data Source: Instamart SM Gemba Adoption
-- Dashboard: GEMBA Walk Adoption
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:58:07
-- ============================================================

WITH sm_forms AS
  (SELECT id AS form_knid,
          'Walk to Elevate - SM' AS form_name
   FROM nuggets
   WHERE organization = 'swiggy-mart-whirlpool'
     AND classification_type = 'form'
     AND title LIKE 'Walk to Elevate - SM%'),
     expected_sm AS
  (SELECT *
   FROM
     (SELECT date::date
      FROM generate_series(@{{:Date Range.START}}::timestamp, least(current_timestamp at time zone 'Asia/Kolkata', @{{:Date Range.END}}::timestamp), '1 day'::interval) AS date) AS cal
   CROSS JOIN
     (SELECT SUBSTRING(location_name
                       FROM '\d+') AS pod
      FROM public.locations
      WHERE location_name ~ '^\d{3}'
        AND organization = 'swiggy-mart-whirlpool'
        AND is_active = TRUE) outlets
   CROSS JOIN
     (SELECT 'Walk to Elevate - SM' AS form)),
     fs AS
  (SELECT DISTINCT ON (fs.response_id) (fs.submit_date AT TIME ZONE 'Asia/Kolkata')::date AS date,
                      'Walk to Elevate - SM' AS form,
                      fs.response_id,
                      fs.sno,
                      fs.location,
                      fs.id
   FROM form_submissions fs
   WHERE fs.form_id IN
       (SELECT form_knid
        FROM sm_forms)
     AND submit_date AT TIME ZONE 'Asia/Kolkata' BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + interval '1 day'
   ORDER BY fs.response_id,
            fs.id),
    sm_responses AS
  (SELECT fs.date,
          form,
          response_id,
          sno,
          SUBSTRING(COALESCE(fr.response->>'name', fs.location)
                    FROM '\d+') AS pod
   FROM fs
   LEFT OUTER JOIN form_responses fr ON fs.id = fr.form_submit_id
   AND fr.response->>'name' IS NOT NULL
   AND fr.response->>'id' IS NOT NULL
   WHERE COALESCE(fr.response->>'name', fs.location) ~ '^\d{3}' ),
     sm_compliance AS
  (SELECT expected_sm.date AS "Date",
          expected_sm.form AS "Form",
          expected_sm.pod AS "Pod ID",
          CASE
              WHEN sm_responses.response_id IS NOT NULL THEN 1
              ELSE 0
          END AS "Compliance",
          CASE
              WHEN sm_responses.response_id IS NOT NULL THEN 'Completed'
              ELSE 'Missed'
          END AS "Status",
          sm_responses.sno AS "Submission No",
          sm_responses.response_id AS "Submission KNID"
   FROM expected_sm
   LEFT OUTER JOIN sm_responses ON expected_sm.date = sm_responses.date
   AND expected_sm.form = sm_responses.form
   AND expected_sm.pod = sm_responses.pod
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7),
     location_map AS
  (SELECT DISTINCT ON (SUBSTRING(job_location
                                 FROM '\d+')) SUBSTRING(job_location
                                                        FROM '\d+') AS pod,
                      division,
                      sub_division
   FROM public.user_details
   WHERE job_location ~ '^\d{3}'
     AND is_active = TRUE
   ORDER BY SUBSTRING(job_location
                      FROM '\d+'),
            created_at DESC)
SELECT compliance."Date",
date_trunc('Week', compliance."Date") as "Week Start",
       compliance."Form",
       compliance."Pod ID" AS "Location",
       location_map.division AS "Region",
       location_map.sub_division AS "City",
       compliance."Status",
       compliance."Compliance",
       compliance."Submission No",
       compliance."Submission KNID"
FROM sm_compliance AS compliance
LEFT OUTER JOIN location_map ON compliance."Pod ID" = location_map.pod
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,10
ORDER BY 1,
         2,
         3,
         4,
         5,
		 6
```

---

## Instamart SM Onboarding Journey Report_SM Onboarding Report.sql

**Tables referenced:** best_answer, c, completed_at, completed_courses, conf_score, feedback_score, ke_score, lj_completed, max_attempt, nps_rating, pass_score, public.courses, public.users, rel_score, responses, scores, sent_users, time_spent, timeline

**Columns needing snake_case conversion:**

- `cardId` -> `card_id` (alias: `card_id AS "cardId"`)

- `completedAt` -> `completed_at` (alias: `completed_at AS "completedAt"`)

- `courseID` -> `course_id` (alias: `course_id AS "courseID"`)

- `courseId` -> `course_id` (alias: `course_id AS "courseId"`)

- `createdAT` -> `created_at` (alias: `created_at AS "createdAT"`)

- `createdAt` -> `created_at` (alias: `created_at AS "createdAt"`)

- `firstName` -> `first_name` (alias: `first_name AS "firstName"`)

- `isActive` -> `is_active` (alias: `is_active AS "isActive"`)

- `isCorrect` -> `is_correct` (alias: `is_correct AS "isCorrect"`)

- `lastName` -> `last_name` (alias: `last_name AS "lastName"`)

- `lessonId` -> `lesson_id` (alias: `lesson_id AS "lessonId"`)

- `nuggetId` -> `nugget_id` (alias: `nugget_id AS "nuggetId"`)

- `passPercent` -> `pass_percent` (alias: `pass_percent AS "passPercent"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `sessionEndTime` -> `session_end_time` (alias: `session_end_time AS "sessionEndTime"`)

- `sessionStartTime` -> `session_start_time` (alias: `session_start_time AS "sessionStartTime"`)

- `startedAt` -> `started_at` (alias: `started_at AS "startedAt"`)

- `subDivision` -> `sub_division` (alias: `sub_division AS "subDivision"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Instamart SM Onboarding Journey Report
-- Dashboard: SM Onboarding Report
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:53:43
-- ============================================================

WITH
  c AS (
  SELECT
    *
  FROM
    public.courses
  WHERE
    id IN ('cz6ZwucVA3eBynFoEfWYXi',
      '3NUthDa2BDjj2V4m9kx1f1',
      '336cWDHj1L5iSYFNct5LC2',
      'eF49CT23yp6TFx1NJSMCWh',
      'eBZaCzrXzNLZNRa6AGNMbG',
      '1G8yAXpVET3oUz8Y4xwxsi',
      'jD8SZ6Z7fnbQXffSibFp7u',
      'b2J7wQLhzvbVRVQbT5V9TE',
      'sX7ntMbuGjCZxzu1e9NNCF',
      '6jLawEzdUbVp23Da8ydErT')),
  sent_users AS (
  SELECT
    u.userId,
    u.identifier AS `Identifier`,
    CONCAT(u.firstName, ' ', u.lastName) AS `Full Name`,
    CASE
      WHEN u.isActive = TRUE THEN 'Active'
      ELSE 'Inactive'
  END
    AS `Employee Status`,
    u.department AS `Department`,
    u.designation AS `Designation`,
    u.division AS `Division`,
    u.subDivision AS `Sub Division`,
    u.joblocation AS `Location`,
    MIN(ra.createdAt) AS `Distributed At`
  FROM
    public.users u
  JOIN
    `analytics.lms_raw_analytics` ra
  ON
    ra.userId = u.userId
  WHERE
    ra.courseId = 'cz6ZwucVA3eBynFoEfWYXi'
    AND ra.createdAT > '2025-10-24'
    AND ra.event IN ('sent',
      'created')
    AND (u.email NOT LIKE '%knownuggets.com'
      OR u.email IS NULL)
  GROUP BY
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9),
  timeline AS (
  SELECT
    ra.courseId,
    ra.userId,
    MIN(CASE
        WHEN ra.event IN ('sent', 'created') AND ra.nuggetId = ra.courseId THEN ra.createdAt
        ELSE NULL
    END
      ) AS sentAt,
    MIN(CASE
        WHEN ra.event IN ('started') THEN ra.createdAt
        ELSE NULL
    END
      ) AS startedAt,
    MIN(CASE
        WHEN ra.event IN ('consumed') AND ra.nuggetId = ra.courseId THEN ra.createdAt
        ELSE NULL
    END
      ) AS completedAt
  FROM
    `analytics.lms_raw_analytics` ra
  JOIN
    c
  ON
    ra.courseId = c.id
  WHERE
    ra.userId IN (
    SELECT
      DISTINCT userId
    FROM
      sent_users)
    AND ra.createdAt > '2025-10-24'
  GROUP BY
    1,
    2),
  completed_courses AS (
  SELECT
    ra.courseId,
    ra.userId,
    MIN(ra.createdAt) AS completedAt
  FROM
    `analytics.lms_raw_analytics` ra
  JOIN
    c
  ON
    ra.courseId = c.id
  WHERE
    ra.event IN ('consumed')
    AND ra.nuggetId = ra.courseId
    AND userId IN (
    SELECT
      userId
    FROM
      sent_users)
  GROUP BY
    1,
    2),
  lj_completed AS (
  SELECT
    userId,
    COUNT(DISTINCT(courseId))
  FROM
    completed_courses
  GROUP BY
    1
  HAVING
    COUNT(DISTINCT(courseId)) = 10),
  completed_at AS(
  SELECT
    completed_courses.userId,
    MAX(completedAt) AS lj_completed_at
  FROM
    completed_courses
  JOIN
    lj_completed
  ON
    completed_courses.userId = lj_completed.userId
  GROUP BY
    1),
  time_spent AS (
  SELECT
    cba.userId,
    SUM(TIMESTAMP_DIFF(TIMESTAMP(sessionEndTime), TIMESTAMP(sessionStartTime), second)) AS in_app_sec
  FROM
    `whirlpool-galaxy.analytics.lms_callback_analytics` cba
  JOIN
    c
  ON
    cba.courseId = c.id
  JOIN
    sent_users
  ON
    sent_users.`Distributed At` IS NOT NULL
    AND cba.userId = sent_users.userId
  GROUP BY
    1),
  conf_score AS (
  SELECT
    l.userId AS user_id,
    SUM(CAST(JSON_VALUE(r, '$.response') AS int))*1.00/COUNT(CAST(JSON_VALUE(r, '$.question') AS int))/5 AS conf_score
  FROM
    `whirlpool-galaxy.analytics.survey_responses` s
  JOIN
    lj_completed l
  ON
    s.userId = l.userId,
    s.data AS r
  WHERE
    courseId IN ('6jLawEzdUbVp23Da8ydErT')
    AND CAST(JSON_VALUE(r, '$.question') AS int) IN (5)
  GROUP BY
    1),
  rel_score AS (
  SELECT
    l.userId AS user_id,
    SUM(CAST(JSON_VALUE(r, '$.response') AS int))*1.00/COUNT(CAST(JSON_VALUE(r, '$.question') AS int))/5 AS rel_score
  FROM
    `whirlpool-galaxy.analytics.survey_responses` s
  JOIN
    lj_completed l
  ON
    s.userId = l.userId,
    s.data AS r
  WHERE
    courseId IN ('6jLawEzdUbVp23Da8ydErT')
    AND CAST(JSON_VALUE(r, '$.question') AS int) IN (6)
  GROUP BY
    1),
  feedback_score AS (
  SELECT
    l.userId AS user_id,
    SUM(CAST(JSON_VALUE(r, '$.response') AS int))*1.00/COUNT(CAST(JSON_VALUE(r, '$.question') AS int)) AS feedback_score
  FROM
    `whirlpool-galaxy.analytics.survey_responses` s
  JOIN
    lj_completed l
  ON
    s.userId = l.userId,
    s.data AS r
  WHERE
    courseId IN ('6jLawEzdUbVp23Da8ydErT')
    AND CAST(JSON_VALUE(r, '$.question') AS int) IN (0,
      1,
      2,
      3,
      4)
  GROUP BY
    1),
  nps_rating AS (
  SELECT
    l.userId AS user_id,
    SUM(CAST(JSON_VALUE(r, '$.response') AS int))*1.00/COUNT(CAST(JSON_VALUE(r, '$.question') AS int)) AS nps
  FROM
    `whirlpool-galaxy.analytics.survey_responses` s
  JOIN
    lj_completed l
  ON
    s.userId = l.userId,
    s.data AS r
  WHERE
    courseId IN ('6jLawEzdUbVp23Da8ydErT')
    AND CAST(JSON_VALUE(r, '$.question') AS int) IN (7)
  GROUP BY
    1),
  responses AS (
  SELECT
    l.userId AS user_id,
    MAX(CASE
        WHEN CAST(JSON_VALUE(r, '$.question') AS int) = 0 THEN CAST(JSON_VALUE(r, '$.response') AS int)
        ELSE NULL
    END
      ) AS `Knowledge of trainer`,
    MAX(CASE
        WHEN CAST(JSON_VALUE(r, '$.question') AS int) = 1 THEN CAST(JSON_VALUE(r, '$.response') AS int)
        ELSE NULL
    END
      ) AS `Trainer's ability to explain`,
    MAX(CASE
        WHEN CAST(JSON_VALUE(r, '$.question') AS int) = 2 THEN CAST(JSON_VALUE(r, '$.response') AS int)
        ELSE NULL
    END
      ) AS `Trainer's ability to answer`,
    MAX(CASE
        WHEN CAST(JSON_VALUE(r, '$.question') AS int) = 3 THEN CAST(JSON_VALUE(r, '$.response') AS int)
        ELSE NULL
    END
      ) AS `Pace of the training`,
    MAX(CASE
        WHEN CAST(JSON_VALUE(r, '$.question') AS int) = 4 THEN CAST(JSON_VALUE(r, '$.response') AS int)
        ELSE NULL
    END
      ) AS `Overall Feedback`
  FROM
    `whirlpool-galaxy.analytics.survey_responses` s
  JOIN
    lj_completed l
  ON
    s.userId = l.userId,
    s.data AS r
  WHERE
    courseId IN ('6jLawEzdUbVp23Da8ydErT')
  GROUP BY
    1),
  max_attempt AS (
  SELECT
    l.userId,
    courseId,
    cardId,
    MAX(attempt) AS last_attempt
  FROM
    `whirlpool-galaxy.analytics.quiz_responses` q
  JOIN
    lj_completed l
  ON
    q.userId = l.userId
  WHERE
    courseId IN ('sX7ntMbuGjCZxzu1e9NNCF')
    AND cardId IN ('vF7zKFq5QvJwQsmaaRzSNf')
  GROUP BY
    1,
    2,
    3),
  best_answer AS (
  SELECT
    q.userId,
    q.courseId,
    q.cardId,
    q.questionId,
    ma.last_attempt,
    MAX(q.isCorrect) AS best_answer
  FROM
    `whirlpool-galaxy.analytics.quiz_responses` q
  JOIN
    max_attempt ma
  ON
    q.userId = ma.userId
    AND q.courseID = ma.courseId
    AND q.cardId = ma.cardId
    AND q.attempt = ma.last_attempt
  WHERE
    q.courseId IN ('sX7ntMbuGjCZxzu1e9NNCF')
    AND q.cardId IN ('vF7zKFq5QvJwQsmaaRzSNf')
  GROUP BY
    1,
    2,
    3,
    4,
    5),
  ke_score AS (
  SELECT
    q.userId AS user_id,
    last_attempt,
    COUNT(DISTINCT(CASE
          WHEN ba.best_answer = TRUE THEN q.questionId
          ELSE NULL
      END
        ))*1.00/COUNT(DISTINCT(ba.questionId)) AS ke_score
  FROM
    `whirlpool-galaxy.analytics.quiz_responses` q
  JOIN
    best_answer ba
  ON
    q.userId = ba.userId
    AND q.courseID = ba.courseId
    AND q.cardId = ba.cardId
    AND q.questionId = ba.questionId
  WHERE
    q.courseId IN ('sX7ntMbuGjCZxzu1e9NNCF')
    AND q.cardId IN ('vF7zKFq5QvJwQsmaaRzSNf')
  GROUP BY
    1,
    2),
  pass_score AS (
  SELECT
    CAST(JSON_VALUE(settings, '$.passPercent') AS int) AS `Pass Score`
  FROM
    `whirlpool-galaxy.public.lesson_cards` lc
  JOIN
    `whirlpool-galaxy.public.lessons` l
  ON
    lc.lessonId = l.id
  WHERE
    l.courseId = 'sX7ntMbuGjCZxzu1e9NNCF'
    AND lc.Id IN ('vF7zKFq5QvJwQsmaaRzSNf')),
  scores AS (
  SELECT
    ke_score.user_id AS userId,
    ke_score.last_attempt AS `Count of Attempts`,
    ke_score.ke_score*10 AS `KE Score`,
    pass_score.`Pass Score`/10 AS `Pass Score`,
    conf_score.conf_score*10 AS `Confidence Score`,
    rel_score.rel_score*10 AS `Relevance Score`,
    (ke_score.ke_score + conf_score.conf_score + rel_score.rel_score)*10/3 AS `JRI`,
    feedback_score.feedback_score AS `Avg Feedback Score`,
    nps_rating.nps AS `NPS Rating`
  FROM
    ke_score
  LEFT OUTER JOIN
    conf_score
  ON
    ke_Score.user_id = conf_score.user_id
  LEFT OUTER JOIN
    rel_score
  ON
    ke_score.user_id = rel_score.user_id
  LEFT OUTER JOIN
    feedback_score
  ON
    ke_Score.user_id = feedback_score.user_id
  LEFT OUTER JOIN
    nps_rating
  ON
    ke_score.user_id = nps_rating.user_id
  JOIN
    pass_score
  ON
    TRUE)
SELECT
  sent_users.*,
  COUNT(DISTINCT(CASE
        WHEN timeline.completedAt IS NOT NULL THEN timeline.courseId
        ELSE NULL
    END
      )) AS `No of Courses Completed`,
  COUNT(DISTINCT(CASE
        WHEN timeline.completedAt IS NOT NULL THEN timeline.courseId
        ELSE NULL
    END
      ))*100/10 AS `Completion %`,
  CAST(sent_users.`Distributed At` AS Date) AS `Started Date`,
  CAST(completed_at.lj_completed_at AS Date) AS `Completed Date`,
  (time_spent.in_app_sec)/60 AS `In App Mins`,
  scores.`Count of Attempts`,
  scores.`Pass Score`,
  scores.`KE Score`,
  scores.`Confidence Score`,
  scores.`Relevance Score`,
  scores.`JRI`,
  scores.`Avg Feedback Score`,
  scores.`NPS Rating`,
  CASE
    WHEN completed_at.lj_completed_at IS NOT NULL THEN DATE_DIFF(CAST(MIN(completed_at.lj_completed_at) AS Date), CAST(sent_users.`Distributed At` AS Date), DAY)
    ELSE NULL
END
  AS `Avg Training Days`,
  responses.`Knowledge of trainer`,
  responses.`Trainer's ability to explain`,
  responses.`Trainer's ability to answer`,
  responses.`Pace of the training`,
  responses.`Overall Feedback`
FROM
  sent_users
LEFT OUTER JOIN
  timeline
ON
  timeline.userId = sent_users.userId
LEFT OUTER JOIN
  completed_at
ON
  sent_users.userId = completed_at.userId
LEFT OUTER JOIN
  time_spent
ON
  sent_users.userId = time_spent.userId
LEFT OUTER JOIN
  scores
ON
  scores.userId = sent_users.userId
LEFT OUTER JOIN
  responses
ON
  responses.user_Id = sent_users.userId
GROUP BY
  1,
  2,
  3,
  4,
  5,
  6,
  7,
  8,
  9,
  10,
  13,
  14,
  15,
  16,
  17,
  18,
  19,
  20,
  21,
  22,
  23,
  25,
  26,
  27,
  28,
  29,
  completed_at.lj_completed_at
ORDER BY
  `Employee Status`,
  `No of Courses Completed` DESC,
  `Division`,
  `Sub Division`,
  `Location`,
  `Full Name`
```

---

## Instamart User Creation Testing_Instamart User Creation Testing.sql

**Tables referenced:** user_details

**Columns needing snake_case conversion:**

- `userTags` -> `user_tags` (alias: `user_tags AS "userTags"`)


**Original Query:**

```sql
-- Data Source: Instamart User Creation Testing
-- Dashboard: Instamart User Creation Testing
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:59:28
-- ============================================================

SELECT 
       identifier AS "Swiggy ID",
       phone_number AS "Mobile Number",
	   CASE
           WHEN organization = 'whirlpool-loctoc' THEN 'Staging'
           WHEN organization = 'swiggy-mart-whirlpool' THEN 'Production'
           ELSE NULL
       END AS "Environment",
	   case when is_active = 'true' then 'Active' else 'Inactive' end as "Status",
       first_name||' '||last_name AS "Name",
       to_timestamp(created_at/1000) AT TIME ZONE 'Asia/Kolkata' AS "Created At", (jsonb_each(PROFILE->'userTags')).key AS "Tag Type",
       jsonb_array_elements((jsonb_each(PROFILE->'userTags')).value)->>'value' AS "Tag",
	   uuid AS "KNOW ID"
FROM user_details
WHERE created_at > 1708401600000
  AND phone_number IS NOT NULL
ORDER BY created_at DESC
```

---

## New Instamart Onboarding Nuggets Share Report_Instamart Onboarding Nuggets Share Report.sql

**Tables referenced:** analytics.nuggets_user_share_requests, learning_journey, user_details

**Columns needing snake_case conversion:**

- `userTags` -> `user_tags` (alias: `user_tags AS "userTags"`)


**Original Query:**

```sql
-- Data Source: New Instamart Onboarding Nuggets Share Report
-- Dashboard: Instamart Onboarding Nuggets Share Report
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:59:34
-- ============================================================

SELECT identifier AS "Employee ID",
first_name||' '||last_name as "Employee Name",
initcap(PROFILE -> 'userTags' -> 'role' -> 0 ->> 'value') AS "Role",
                                           initcap(PROFILE -> 'userTags' -> 'city' -> 0 ->> 'value') AS "City",
                                                                               initcap(PROFILE -> 'userTags' -> 'store' -> 0 ->> 'value') AS "Store",
       to_timestamp(ud.created_at/1000) AT TIME ZONE 'Asia/Kolkata' AS "ID Created on KNOW at",
                                                     nusr.nugget_id AS "LJ KNID",
                                                     lj.name AS "LJ Name",
                                                     nusr.completed_at AT TIME ZONE 'Asia/Kolkata' AS "LJ Shared at"
FROM user_details ud
JOIN analytics.nuggets_user_share_requests nusr ON ud.uuid = nusr.user_id
JOIN learning_journey lj ON nusr.nugget_id = lj.id
WHERE to_timestamp(ud.created_at/1000) AT TIME ZONE 'Asia/Kolkata' > (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '30 days')::date
ORDER BY 2,
         1,
         3,
         5
```

---

## Pod_Compliance_audit_POD Audit - Master.sql

**Tables referenced:** checkpoint_master_sheet_table, location_map, locations, role_holders, roles, user_Details, user_details

**Original Query:**

```sql
-- Data Source: Pod_Compliance_audit
-- Dashboard: POD Audit - Master
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:56:35
-- ============================================================

WITH location_map AS (
    SELECT DISTINCT ON (division, sub_division, regexp_replace(job_location, '([0-9]+).*', '\1'))
        division AS region,
        sub_division AS city,
        regexp_replace(job_location, '([0-9]+).*', '\1') AS pod
    FROM user_Details
    WHERE (regexp_replace(job_location, '([0-9]+).*', '\1') IS NOT NULL
           OR regexp_replace(job_location, '([0-9]+).*', '\1') != '')
      AND is_active = TRUE
    ORDER BY 1, 2, 3, created_at DESC
),
role_map AS (
    SELECT 
        l.region, 
        l.city, 
        l.pod, 
        MAX(CASE WHEN r.name = 'Cluster Ops Manager' THEN ud.first_name || ' ' || ud.last_name END) AS com,
        MAX(CASE WHEN r.name = 'Deputy City Head' THEN ud.first_name || ' ' || ud.last_name END) AS dch
    FROM location_map l
    LEFT JOIN locations loc ON l.pod = regexp_replace(loc.location_name, '([0-9]+).*', '\1')
    LEFT JOIN role_holders rh ON loc.id = rh.location_id AND rh.is_active = TRUE
    LEFT JOIN roles r ON r.id = rh.role_id AND r.name IN ('Cluster Ops Manager', 'Deputy City Head')
    LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid AND ud.is_active = TRUE
    GROUP BY l.region, l.city, l.pod
)
SELECT lm.region AS "Region",
       initcap(lm.city) AS "City",
       lm.pod AS "Pod",
	   initcap(cms.store_id) as "Pod Name",
       cms.audit_type AS "Audit Type",
       cms.audit_main_theme AS "Audit",
       audit_submission_number AS "Audit Report No",
       auditor_name AS "Auditor",
       to_timestamp(cms.audit_started_at/1000) AT TIME ZONE 'Asia/Kolkata' AS "Audit Started At",
                                                            audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
                                                                                            theme AS "Theme",
                                                                                            CHECKPOINT AS "Attribute",
                                                                                                          criticality AS "Criticality",
                                                                                                          RESULT AS "Result",
                                                                                                                    CASE
                                                                                                                        WHEN result_score = '' THEN NULL
                                                                                                                        ELSE result_score::numeric
                                                                                                                    END AS "Actual Score",
                                                                                                                    CASE
                                                                                                                        WHEN result_score = '' THEN NULL
                                                                                                                        ELSE max_score::numeric
                                                                                                                    END AS "Max Score",
                                                                                                                    auditor_observations AS "Observations",
                                                                                                                    total_follow_up_tasks AS "Assigned Action Count",
                                                                                                                    total_closed_follow_up_tasks AS "Closed Action Count",
                                                                                                                    audit_submission_knid AS "Audit Report KNID",
                                                                                                                    checkpoint_knid AS "Attribute KNID"
FROM checkpoint_master_sheet_table cms
left outer JOIN location_map lm ON regexp_replace(cms.store_id, '([0-9]+).*', '\1') = lm.pod
WHERE cms.audit_main_theme ILIKE 'Pod Compliance%'
AND audit_submitted_at AT TIME ZONE 'Asia/Kolkata' BETWEEN @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
ORDER BY 1,
         2,
         3,
         4,
         5,
         8 DESC
```

---

## Swiggy Course Reports_Swiggy Course Report.sql

**Tables referenced:** analytic_requests, analytics, course_assesments_settings, courses, lateral, lesson_cards, lessons, nup_users_with_pagination, quiz, quiz_responses, user_details

**Columns needing snake_case conversion:**

- `inProgress` -> `in_progress` (alias: `in_progress AS "inProgress"`)


**Original Query:**

```sql
-- Data Source: Swiggy Course Reports
-- Dashboard: Swiggy Course Report
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:53:23
-- ============================================================

with lessons_cards as (
SELECT jsonb_object_agg(lesson_cards_map.id, cards) as lesson_cards_map
FROM (
	  SELECT 
	    l.id,
	    jsonb_object_agg(lc.id, true) AS cards
	  FROM lesson_cards lc
	  JOIN lessons l ON lc.lesson_id = l.id
	  WHERE l.course_id = @{{:Course Name}}
	  GROUP BY l.id
	) AS lesson_cards_map
),
course_assesments_settings as (
	select 
	  l.course_id,
	  jsonb_object_agg(lc.id, jsonb_build_object('assesment_name', lc.title,'settings', lc.settings)) as card_settings
	from lesson_cards lc
	join lessons l on lc.lesson_id = l.id
	where l.course_id = @{{:Course Name}}
	  and lc.type = 'quiz'
	group by l.course_id
),
nup_users_with_pagination as (
	select nup.*
	from analytics."nuggets_user_progress_@{{:Course Name.IGNOREQUOTES}}" nup
   where created_at between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'-- where nup.user_id in (select uuid from user_details ud where ud.identifier = 'Temp-78898')
	order by case nup.status
    when 'passed' then 1
    when 'completed' then 2
    when 'inProgress' then 3
    else 4
  end, nup.updated_at desc -- limit 1 offset 0
),
analytic_requests as (
	select t.user_id, jsonb_object_agg(t.nugget_id, t.analytics_by_event) as analytics_by_event 
	from (
	select ar.user_id, ar.nugget_id, jsonb_object_agg(event_id, jsonb_build_object(ar.analytics_id, ar.created_at)) as analytics_by_event
	from analytics."analytics_raw_@{{:Course Name.IGNOREQUOTES}}" ar
	join nup_users_with_pagination nup on nup.user_id = ar.user_id and nup.share_id = ar.share_id
	where ar.event_id in (5,3)
	group by 1,2) t
	group by 1
),
quiz_responses as (
select
  user_id,
  jsonb_object_agg(card_id, shares) as card_share_attempt_data
from (
  select
    user_id,
    card_id,
    jsonb_object_agg(share_id, attempts) as shares
  from (
    select
      user_id,
      card_id,
      share_id,
      jsonb_object_agg(attempt::text, questions) as attempts
    from (
      select
        ar.user_id,
        ar.card_id,
        ar.share_id,
        ar.attempt,
        jsonb_object_agg(ar.question_id::text, ar.is_correct) as questions
      from quiz."quiz_responses_@{{:Course Name.IGNOREQUOTES}}" ar
      join nup_users_with_pagination nup on (nup.user_id = ar.user_id and nup.share_id = ar.share_id)
      group by ar.user_id, ar.card_id, ar.share_id, ar.attempt
    ) q1
    group by user_id, card_id, share_id
  ) q2
  group by user_id, card_id
) q3
group by user_id
)
select ud.identifier as "Identifier", 
	   ud.first_name as "First Name", 
	   ud.last_name as "Last Name", 
	   ud.designation as "Designation", 
	   ud.department as "Department",
	   ud.division as "Division",
	   ud.sub_division as "Sub Division",
	   ud.job_location as "Location",
	   case when ud.is_active = true then 'Active' else 'In-Active' end as "Employee Status", 
	   c.name as "Course Name",
	   case when c.status = 'revoked' then 'Revoked' else 'Shared' end as "Course Status",
	   processed.*,
	   c.id as "Course ID"
from course_assesments_settings cas, lessons_cards lc, nup_users_with_pagination nup
join courses c on c.id = nup.nugget_id
join user_details ud on ud.uuid = nup.user_id
left join quiz_responses qr on qr.user_id = ud.uuid
left join analytic_requests ar on ar.user_id = nup.user_id
cross join lateral analytics.process_nuggets_user_progress(
	to_jsonb(nup),
	ar.analytics_by_event, 
	cas.card_settings, 
	lc.lesson_cards_map,
	qr.card_share_attempt_data
) as processed
```

---

## Swiggy IM Learn_Learn.sql

**Tables referenced:** data_team.swiggy_im_learn

**Original Query:**

```sql
-- Data Source: Swiggy IM Learn
-- Dashboard: Learn
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:52:53
-- ============================================================

select * from data_team.swiggy_im_learn il
where il.shared_at BETWEEN @{{:Date Range.START}}::timestamp 
                      AND @{{:Date Range.END}}::timestamp + interval '1 day'
```

---

## Swiggy Polls_Polls Dashboard.sql

**Tables referenced:** lm, public.locations, public.poll_questions, public.polls_responses, public.role_holders, public.roles, public.users, role_mapping

**Columns needing snake_case conversion:**

- `createdAt` -> `created_at` (alias: `created_at AS "createdAt"`)

- `firstName` -> `first_name` (alias: `first_name AS "firstName"`)

- `isActive` -> `is_active` (alias: `is_active AS "isActive"`)

- `jobLocation` -> `job_location` (alias: `job_location AS "jobLocation"`)

- `organizationId` -> `organization_id` (alias: `organization_id AS "organizationId"`)

- `pollId` -> `poll_id` (alias: `poll_id AS "pollId"`)

- `questionIdx` -> `question_idx` (alias: `question_idx AS "questionIdx"`)

- `questionText` -> `question_text` (alias: `question_text AS "questionText"`)

- `questionType` -> `question_type` (alias: `question_type AS "questionType"`)

- `sectionName` -> `section_name` (alias: `section_name AS "sectionName"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Swiggy Polls
-- Dashboard: Polls Dashboard
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:54:21
-- ============================================================

WITH role_mapping AS
  (SELECT l.id AS store_id,
          l.location_name AS store_name,
          r.name AS ROLE,
          u.firstName AS holder
   FROM public.locations l
   LEFT JOIN public.role_holders rh ON rh.location_id = l.id
   AND rh.is_active = TRUE
   LEFT JOIN public.roles r ON r.id = rh.role_id
   AND r.name IN ('Cluster Ops Manager',
                  'Deputy City Head')
   LEFT JOIN public.users u ON rh.role_holder_id = u.userId
   AND u.isActive = TRUE
   WHERE l.organization = 'swiggy-mart-whirlpool'
     AND l.is_active = TRUE ),
     lm AS
  (SELECT store_id,
          store_name,
          MAX(CASE
                  WHEN ROLE = 'Cluster Ops Manager' THEN holder
              END) AS COM,
          MAX(CASE
                  WHEN ROLE = 'Deputy City Head' THEN holder
              END) AS DCH
   FROM role_mapping
   GROUP BY store_id,
            store_name),
     user_location AS
  (SELECT rh.role_holder_id AS userId,
          rh.location_id AS store_id
   FROM public.role_holders rh
   WHERE rh.is_active = TRUE )
SELECT r.createdAt,
                q.organizationId,
                r.pollId,
                r.userId,
                u.identifier AS user_identifier,
				u.jobLocation,
				lm.DCH,
				lm.COM,
                q.sectionName,
                q.questionIdx,
                q.questionType,
                q.questionText,
                SAFE_CAST(JSON_EXTRACT_SCALAR(r.response, '$') AS INT64) AS response,
                SAFE_CAST(JSON_EXTRACT_SCALAR(q.rating, '$.max') AS INT64) AS max_value,
                SAFE_CAST(JSON_EXTRACT_SCALAR(q.rating, '$.min') AS INT64) AS min_value,
				CASE 
        WHEN SAFE_CAST(JSON_EXTRACT_SCALAR(r.response, '$') AS INT64) < 
             0.5 * SAFE_CAST(JSON_EXTRACT_SCALAR(q.rating, '$.max') AS INT64)
        THEN 'Below 50%'
        ELSE 'OK'
    END AS nps_flag
FROM public.polls_responses r
JOIN public.poll_questions q ON r.pollId = q.pollId
AND r.questionIdx = q.questionIdx
JOIN public.users u ON r.userId = u.userId
left outer JOIN lm on u.jobLocation = lm.store_id
WHERE q.sectionName LIKE '%NPS Survey%'
  AND TIMESTAMP_TRUNC(r.createdAt, DAY) BETWEEN TIMESTAMP(@{{:Date Range.START}}) AND TIMESTAMP_ADD(TIMESTAMP(@{{:Date Range.END}}), INTERVAL 1 DAY)
ORDER BY r.createdAt DESC
```

---

## com_scoring_Walk to Elevate - COM.sql

**Tables referenced:** checkpoint_master_sheet_table, location_map, locations, role_holders, role_map, roles, user_Details, user_details

**Original Query:**

```sql
-- Data Source: com_scoring
-- Dashboard: Walk to Elevate - COM
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:56:37
-- ============================================================

WITH location_map AS (
    SELECT DISTINCT ON (division, sub_division, regexp_replace(job_location, '([0-9]+).*', '\1'))
        division AS region,
        sub_division AS city,
        regexp_replace(job_location, '([0-9]+).*', '\1') AS pod
    FROM user_Details
    WHERE (regexp_replace(job_location, '([0-9]+).*', '\1') IS NOT NULL
           OR regexp_replace(job_location, '([0-9]+).*', '\1') != '')
      AND is_active = TRUE
    ORDER BY 1, 2, 3, created_at DESC
),
role_map AS (
    SELECT 
        l.region, 
        l.city, 
        l.pod, 
        MAX(CASE WHEN r.name = 'Cluster Ops Manager' THEN ud.first_name || ' ' || ud.last_name END) AS com,
        MAX(CASE WHEN r.name = 'Deputy City Head' THEN ud.first_name || ' ' || ud.last_name END) AS dch
    FROM location_map l
    LEFT JOIN locations loc ON l.pod = regexp_replace(loc.location_name, '([0-9]+).*', '\1')
    LEFT JOIN role_holders rh ON loc.id = rh.location_id AND rh.is_active = TRUE
    LEFT JOIN roles r ON r.id = rh.role_id AND r.name IN ('Cluster Ops Manager', 'Deputy City Head')
    LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid AND ud.is_active = TRUE
    GROUP BY l.region, l.city, l.pod
)
SELECT 
    lm.region AS "Region",
    INITCAP(lm.city) AS "City",
    lm.pod AS "Pod",
    INITCAP(cms.store_id) AS "Pod Name",
    rm.com AS "Cluster Ops Manager",
    rm.dch AS "DCH",
    cms.audit_type AS "Audit Type",
    cms.audit_main_theme AS "Audit",
    audit_submission_number AS "Audit Report No",
    auditor_name AS "Auditor",
    TO_TIMESTAMP(cms.audit_started_at / 1000) AT TIME ZONE 'Asia/Kolkata' AS "Audit Started At",
    audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
    theme AS "Theme",
    CHECKPOINT AS "Attribute",
    criticality AS "Criticality",
    RESULT AS "Result",
    CASE WHEN result_score = '' THEN NULL ELSE result_score::numeric END AS "Actual Score",
    CASE WHEN result_score = '' THEN NULL ELSE max_score::numeric END AS "Max Score",
    auditor_observations AS "Observations",
    total_follow_up_tasks AS "Assigned Action Count",
    total_closed_follow_up_tasks AS "Closed Action Count",
    audit_submission_knid AS "Audit Report KNID",
    checkpoint_knid AS "Attribute KNID"
FROM checkpoint_master_sheet_table cms
LEFT JOIN location_map lm ON regexp_replace(cms.store_id, '([0-9]+).*', '\1') = lm.pod
LEFT JOIN role_map rm ON lm.pod = rm.pod
WHERE cms.audit_main_theme = 'Walk to Elevate - COMs'
AND audit_submitted_at AT TIME ZONE 'Asia/Kolkata' BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + INTERVAL '1 day'
ORDER BY 1, 2, 3, 4, 5, 8 DESC
```

---

## com_scoring_summary_Walk to Elevate - COM.sql

**Tables referenced:** Pod, acl, audit_summary, checkpoint_master_sheet_table, compliance_data, form_submissions, lm, locations, lr, role_holders, roles, user_details

**Original Query:**

```sql
-- Data Source: com_scoring_summary
-- Dashboard: Walk to Elevate - COM
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:56:36
-- ============================================================

WITH acl AS (
    SELECT regexp_replace(l.location_name, '([0-9]+).*', '\1') AS store_id 
    FROM locations l 
    WHERE organization = 'swiggy-mart-whirlpool'
    AND is_active = TRUE
),
lr AS (
    SELECT acl.store_id,
           l.location_name AS store_name,
           r.name AS role,
           ud.uuid AS holder_id,
           ud.first_name || ' ' || ud.last_name AS holder
    FROM acl
    JOIN locations l ON acl.store_id = regexp_replace(l.location_name, '([0-9]+).*', '\1')
    LEFT JOIN role_holders rh ON l.id = rh.location_id AND rh.is_active = TRUE
    LEFT JOIN roles r ON r.id = rh.role_id AND r.name IN ('Cluster Ops Manager', 'Deputy City Head')
    LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
    WHERE l.organization = 'swiggy-mart-whirlpool'
    AND l.is_active = TRUE
    AND ud.is_active = TRUE
    AND r.name IN ('Cluster Ops Manager', 'Deputy City Head')
    ORDER BY 1, 2
),
lm AS (
    SELECT lr.store_id AS pod_id,
           lr.store_name AS pod_name,
           ud.division AS cluster,
           ud.sub_division AS city,
           MAX(CASE WHEN role = 'Cluster Ops Manager' THEN holder ELSE NULL END) AS com,
           MAX(CASE WHEN role = 'Cluster Ops Manager' THEN holder_id ELSE NULL END) AS com_knid,
           MAX(CASE WHEN role = 'Deputy City Head' THEN holder ELSE NULL END) AS dch,
           MAX(CASE WHEN role = 'Deputy City Head' THEN holder_id ELSE NULL END) AS dch_knid
    FROM lr
    JOIN (
        SELECT DISTINCT ON (job_location) job_location,
               division,
               sub_division
        FROM user_details
        WHERE regexp_replace(job_location, '([0-9]+).*', '\1') IS NOT NULL
        AND division IS NOT NULL
        ORDER BY job_location, created_at DESC
    ) ud ON lr.store_name = ud.job_location
    GROUP BY 1, 2, 3, 4
    ORDER BY 1
),
compliance_data AS (
    SELECT cms.store_id,
           COUNT(*) AS total_audits,
           SUM(CASE WHEN cms.result = 'Yes' THEN 1 ELSE 0 END) AS compliant_audits
    FROM checkpoint_master_sheet_table cms
    WHERE cms.audit_main_theme = 'Walk to Elevate - COMs'
    AND cms.audit_submitted_at AT TIME ZONE 'Asia/Kolkata' BETWEEN @{{:com_scoring.Date Range.START}}::timestamp AND @{{:com_scoring.Date Range.END}}::timestamp + INTERVAL '1 day'
    GROUP BY cms.store_id
),
audit_summary AS (
    SELECT 
        l.pod_id, 
        COALESCE(SUM(c.compliant_audits) * 100.0 / NULLIF(SUM(c.total_audits), 0), 0) AS compliance_score,
        COUNT(DISTINCT cms.audit_submission_knid) * 100.0 / NULLIF((SELECT COUNT(DISTINCT store_id) 
                                                                    FROM checkpoint_master_sheet_table 
                                                                    WHERE audit_submitted_at AT TIME ZONE 'Asia/Kolkata' BETWEEN @{{:com_scoring.Date Range.START}}::timestamp AND @{{:com_scoring.Date Range.END}}::timestamp + INTERVAL '1 day'), 1) 
        AS completion_score
    FROM lm l
    LEFT JOIN compliance_data c ON l.pod_name = c.store_id
    LEFT JOIN (
        SELECT DISTINCT store_id, audit_submission_knid
        FROM checkpoint_master_sheet_table
        WHERE audit_submitted_at AT TIME ZONE 'Asia/Kolkata' BETWEEN @{{:com_scoring.Date Range.START}}::timestamp AND @{{:com_scoring.Date Range.END}}::timestamp + INTERVAL '1 day'
    ) cms ON c.store_id = cms.store_id
    WHERE cms.audit_submission_knid IS NOT NULL
    GROUP BY l.pod_id
)
SELECT 
    lm.cluster AS "Region",
    INITCAP(lm.city) AS "City",
    lm.pod_id AS "Pod",
    INITCAP(cms.store_id) AS "Pod Name",
    lm.com AS "Cluster Ops Manager (COM)",
    lm.dch AS "Deputy City Head (DCH)",
    cms.audit_type AS "Audit Type",
    cms.audit_main_theme AS "Audit",
    audit_submission_number AS "Audit Report No",
    auditor_name AS "Auditor",
    TO_TIMESTAMP(cms.audit_started_at/1000) AT TIME ZONE 'Asia/Kolkata' AS "Audit Started At",
    audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
    fs.approx_distance_in_km AS "Audit Distance from Pod",
    SUM(CASE WHEN result_score = '' THEN NULL ELSE result_score::NUMERIC END) /
        SUM(CASE WHEN result_score = '' THEN NULL ELSE max_score::NUMERIC END) AS "Audit Score",
    SUM(total_follow_up_tasks) AS "Assigned Action Count",
    SUM(total_closed_follow_up_tasks) AS "Closed Action Count",
    a.compliance_score AS "Compliance Score",
    a.completion_score AS "Completion Score",
    audit_submission_knid AS "Audit Report KNID"
FROM checkpoint_master_sheet_table cms
JOIN form_submissions fs ON cms.audit_submission_knid = fs.response_id
LEFT OUTER JOIN lm ON regexp_replace(cms.store_id, '([0-9]+).*', '\1') = lm.pod_id
LEFT JOIN audit_summary a ON lm.pod_id = a.pod_id
WHERE cms.audit_main_theme = 'Walk to Elevate - COMs'
AND audit_submitted_at AT TIME ZONE 'Asia/Kolkata' BETWEEN @{{:com_scoring.Date Range.START}}::timestamp AND @{{:com_scoring.Date Range.END}}::timestamp + INTERVAL '1 day'
AND cms.store_id IS NOT NULL
AND lm.pod_id IS NOT NULL
AND lm.com IS NOT NULL
AND audit_submission_knid IS NOT NULL
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, fs.approx_distance_in_km, a.completion_score, cms.audit_submission_knid, 17
ORDER BY 1, 2, 3, 4, 5, 8 DESC
```

---

## pod_compliance_audit_summary_POD Audit - Master.sql

**Tables referenced:** Pod, acl, audit_summary, checkpoint_master_sheet_table, compliance_data, form_submissions, lm, locations, lr, role_holders, roles, user_details

**Original Query:**

```sql
-- Data Source: pod_compliance_audit_summary
-- Dashboard: POD Audit - Master
-- Category: Swiggy Instamart
-- Extracted: 2026-01-29 16:56:36
-- ============================================================

WITH acl AS (
    SELECT regexp_replace(l.location_name, '([0-9]+).*', '\1') AS store_id 
    FROM locations l 
    WHERE organization = 'swiggy-mart-whirlpool'
    AND is_active = TRUE
),
lr AS (
    SELECT acl.store_id,
           l.location_name AS store_name,
           r.name AS role,
           ud.uuid AS holder_id,
           ud.first_name || ' ' || ud.last_name AS holder
    FROM acl
    JOIN locations l ON acl.store_id = regexp_replace(l.location_name, '([0-9]+).*', '\1')
    LEFT JOIN role_holders rh ON l.id = rh.location_id AND rh.is_active = TRUE
    LEFT JOIN roles r ON r.id = rh.role_id AND r.name IN ('Cluster Ops Manager', 'Deputy City Head')
    LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
    WHERE l.organization = 'swiggy-mart-whirlpool'
    AND l.is_active = TRUE
    AND ud.is_active = TRUE
    AND r.name IN ('Cluster Ops Manager', 'Deputy City Head')
    ORDER BY 1, 2
),
lm AS (
    SELECT lr.store_id AS pod_id,
           lr.store_name AS pod_name,
           ud.division AS cluster,
           ud.sub_division AS city,
           MAX(CASE WHEN role = 'Cluster Ops Manager' THEN holder ELSE NULL END) AS com,
           MAX(CASE WHEN role = 'Cluster Ops Manager' THEN holder_id ELSE NULL END) AS com_knid,
           MAX(CASE WHEN role = 'Deputy City Head' THEN holder ELSE NULL END) AS dch,
           MAX(CASE WHEN role = 'Deputy City Head' THEN holder_id ELSE NULL END) AS dch_knid
    FROM lr
    JOIN (
        SELECT DISTINCT ON (job_location) job_location,
               division,
               sub_division
        FROM user_details
        WHERE regexp_replace(job_location, '([0-9]+).*', '\1') IS NOT NULL
        AND division IS NOT NULL
        ORDER BY job_location, created_at DESC
    ) ud ON lr.store_name = ud.job_location
    GROUP BY 1, 2, 3, 4
    ORDER BY 1
),
compliance_data AS (
    SELECT cms.store_id,
           COUNT(*) AS total_audits,
            SUM(CASE 
            WHEN cms.result = 'Fully Compliant' THEN 1.0  -- 100%
            WHEN cms.result = 'Partial Compliant' THEN 0.5  -- 50%
            ELSE 0.0  -- Non Compliant = 0%
        END) AS compliant_audits
    FROM checkpoint_master_sheet_table cms
    WHERE cms.audit_main_theme ILIKE 'Pod Compliance%'
    AND cms.audit_submitted_at AT TIME ZONE 'Asia/Kolkata' BETWEEN @{{:Pod_Compliance_audit.Date Range.START}}::timestamp AND @{{:Pod_Compliance_audit.Date Range.END}}::timestamp + INTERVAL '1 day'
    GROUP BY cms.store_id
),
audit_summary AS (
    SELECT 
        l.pod_id, 
        COALESCE(SUM(c.compliant_audits) * 100.0 / NULLIF(SUM(c.total_audits), 0), 0) AS compliance_score,
        COUNT(DISTINCT cms.audit_submission_knid) * 100.0 / NULLIF((SELECT COUNT(DISTINCT store_id) 
                                                                    FROM checkpoint_master_sheet_table 
                                                                    WHERE audit_submitted_at AT TIME ZONE 'Asia/Kolkata' BETWEEN @{{:Pod_Compliance_audit.Date Range.START}}::timestamp AND @{{:Pod_Compliance_audit.Date Range.END}}::timestamp + INTERVAL '1 day'), 1) 
        AS completion_score
    FROM lm l
    LEFT JOIN compliance_data c ON l.pod_name = c.store_id
    LEFT JOIN (
        SELECT DISTINCT store_id, audit_submission_knid
        FROM checkpoint_master_sheet_table
        WHERE audit_submitted_at AT TIME ZONE 'Asia/Kolkata' BETWEEN @{{:Pod_Compliance_audit.Date Range.START}}::timestamp AND @{{:Pod_Compliance_audit.Date Range.END}}::timestamp + INTERVAL '1 day'
    ) cms ON c.store_id = cms.store_id
    WHERE cms.audit_submission_knid IS NOT NULL
    GROUP BY l.pod_id
)
SELECT 
    lm.cluster AS "Region",
    INITCAP(lm.city) AS "City",
    lm.pod_id AS "Pod",
    INITCAP(cms.store_id) AS "Pod Name",
    lm.com AS "Cluster Ops Manager (COM)",
    lm.dch AS "Deputy City Head (DCH)",
    cms.audit_type AS "Audit Type",
    cms.audit_main_theme AS "Audit",
    audit_submission_number AS "Audit Report No",
    auditor_name AS "Auditor",
    TO_TIMESTAMP(cms.audit_started_at/1000) AT TIME ZONE 'Asia/Kolkata' AS "Audit Started At",
    audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
    fs.approx_distance_in_km AS "Audit Distance from Pod",
    SUM(CASE WHEN result_score = '' THEN NULL ELSE result_score::NUMERIC END) /
        SUM(CASE WHEN result_score = '' THEN NULL ELSE max_score::NUMERIC END) AS "Audit Score",
    SUM(total_follow_up_tasks) AS "Assigned Action Count",
    SUM(total_closed_follow_up_tasks) AS "Closed Action Count",
    a.compliance_score AS "Compliance Score",
    a.completion_score AS "Completion Score",
    audit_submission_knid AS "Audit Report KNID"
FROM checkpoint_master_sheet_table cms
JOIN form_submissions fs ON cms.audit_submission_knid = fs.response_id
LEFT OUTER JOIN lm ON regexp_replace(cms.store_id, '([0-9]+).*', '\1') = lm.pod_id
LEFT JOIN audit_summary a ON lm.pod_id = a.pod_id
WHERE cms.audit_main_theme ILIKE 'Pod Compliance%'
AND audit_submitted_at AT TIME ZONE 'Asia/Kolkata' BETWEEN @{{:Pod_Compliance_audit.Date Range.START}}::timestamp AND @{{:Pod_Compliance_audit.Date Range.END}}::timestamp + INTERVAL '1 day'
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, fs.approx_distance_in_km, a.completion_score, cms.audit_submission_knid, 17
ORDER BY 1, 2, 3, 4, 5, 8 DESC
```

---
