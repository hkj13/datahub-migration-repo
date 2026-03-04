# Maestro Pizza

> Auto-generated on 2026-03-04 08:13

**Total queries:** 8

---

## AM Compliance_Main Dashboard.sql

**Tables referenced:** all_forms_per_am, am_locations, am_weekly, filtered_submissions, form_submissions, generate_series, locations, nuggets, nuggets_map, role_holders, roles, user_details

**Original Query:**

```sql
-- Data Source: AM Compliance
-- Dashboard: Main Dashboard
-- Category: Maestro Pizza
-- Extracted: 2026-01-29 16:52:26
-- ============================================================

-- Step 1: Map AM/RM per location
WITH am_locations AS (
    SELECT
        l.id AS store_id,
        MAX(CASE WHEN r.name = 'Area Manager'
            THEN ud.first_name || ' ' || ud.last_name END) AS am_name,
        MAX(CASE WHEN r.name = 'Regional Manager'
            THEN ud.first_name || ' ' || ud.last_name END) AS rm_name
    FROM locations l
    JOIN role_holders rh
        ON rh.location_id = l.id
       AND rh.is_active = TRUE
    JOIN roles r
        ON r.id = rh.role_id
       AND r.name IN ('Area Manager', 'Regional Manager')
    JOIN user_details ud
        ON ud.uuid = rh.role_holder_id
       AND ud.is_active = TRUE
    WHERE l.organization = 'maestropizza-ksa-cartwheel'
      AND l.is_active = TRUE
  and location_name not in ('Buraidah HO',
'Jeddah HO',
'Abha HO',
'Riyadh HO',
'Dammam HO',
'Makkah HO')
    GROUP BY l.id
  
),

-- Step 2: Forms we care about
nuggets_map AS (
    SELECT id AS form_id, title AS form_name
    FROM nuggets
    WHERE title ILIKE 'Area Manager: Opening Visit%'
       OR title ILIKE 'Area Manager: Closing Visit%'
       OR title ILIKE 'Area Manager: PRP%'
       OR title ILIKE 'Area Manager Audit Visit%'
),

-- Step 3: Submissions strictly inside client-passed date window
filtered_submissions AS (
    SELECT
        (fs.submit_date AT TIME ZONE 'Asia/Riyadh') AS submit_date,
        fs.location_id,
        fs.form_id
    FROM form_submissions fs
    WHERE fs.organization = 'maestropizza-ksa-cartwheel'
      AND fs.submit_date >= @{{:Maestro Routine Compliance-copy_1765953034.Date Range.START}}::timestamp
      AND fs.submit_date < (
            @{{:Maestro Routine Compliance-copy_1765953034.Date Range.END}}::timestamp
            + interval '1 day'
        )
      AND fs.form_id IN (SELECT form_id FROM nuggets_map)
),

-- Step 4: Aggregate submissions per AM × RM × Form × KSA Week (Sunday start)
am_weekly AS (
    SELECT
        al.am_name,
        al.rm_name,
        nm.form_name,
        (
            date_trunc('week', fs.submit_date + interval '1 day')
            - interval '1 day'
        )::date AS week_start,
        COUNT(DISTINCT fs.location_id) AS submission_count
    FROM filtered_submissions fs
    JOIN am_locations al
        ON fs.location_id = al.store_id
    JOIN nuggets_map nm
        ON fs.form_id = nm.form_id
    GROUP BY 1,2,3,4
),

-- Step 5: Generate all AM × RM × Form × KSA Week combinations
all_forms_per_am AS (
    SELECT
        al.am_name,
        al.rm_name,
        nm.form_name,
        (
            date_trunc('week', d + interval '1 day')
            - interval '1 day'
        )::date AS week_start
    FROM am_locations al
    CROSS JOIN nuggets_map nm
    CROSS JOIN generate_series(
        @{{:Maestro Routine Compliance-copy_1765953034.Date Range.START}}::date,
        @{{:Maestro Routine Compliance-copy_1765953034.Date Range.END}}::date,
        interval '1 day'
    ) d
    GROUP BY 1,2,3,4
)

-- Step 6: Final compliance calculation
SELECT
    af.am_name        AS "Area Manager",
    af.rm_name        AS "Regional Manager",
    af.week_start     AS "Week (Sunday)",
    af.form_name      AS "Form",
    COALESCE(aw.submission_count, 0) AS submission_count,
    2 AS expected_submissions,
    CASE
        WHEN COALESCE(aw.submission_count, 0) >= 2
            THEN 1.0
        ELSE COALESCE(aw.submission_count, 0) / 2.0
    END AS compliance
FROM all_forms_per_am af
LEFT JOIN am_weekly aw
    ON af.am_name   = aw.am_name
   AND af.rm_name   = aw.rm_name
   AND af.form_name = aw.form_name
   AND af.week_start = aw.week_start
ORDER BY af.week_start DESC, af.am_name, af.form_name
```

---

## Maestro Audit Details_Audits.sql

**Tables referenced:** ROLES, audit_submitted_at, base, checkpoint_master_sheet_table, lm, location_acl, locations, lr, organizations, role_holders, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Maestro Audit Details
-- Dashboard: Audits
-- Category: Maestro Pizza
-- Extracted: 2026-01-29 16:54:04
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
			   lr AS
  (SELECT l.id AS store_id,
          r.name AS ROLE,
          ud.first_name || ' ' || ud.last_name AS holder
   FROM locations l
   LEFT JOIN role_holders rh ON rh.location_id = l.id
   AND rh.is_active = TRUE
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Area Manager',
                  'Regional Manager')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = TRUE
   WHERE l.organization = 'maestropizza-ksa-cartwheel'
     AND l.is_active = TRUE ),
     lm AS
  (SELECT store_id,
          MAX(CASE
                  WHEN ROLE = 'Area Manager' THEN holder
              END) AS "AM",
          MAX(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder
              END) AS "RM"
   FROM lr
   GROUP BY store_id),
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
       base.store_id AS "Location",
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
       "Audit No in Year",
	   lm."AM",
	   lm."RM"
FROM base
join lm on base.store_id = lm.store_id
group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,20,21
ORDER BY 1,
         2,
         4
```

---

## Maestro Audit Summary_Audits.sql

**Tables referenced:** ROLES, audit_submitted_at, base, checkpoint_master_sheet_table, lm, location_acl, locations, lr, organizations, role_holders, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Maestro Audit Summary
-- Dashboard: Audits
-- Category: Maestro Pizza
-- Extracted: 2026-01-29 16:54:05
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
			   lr AS
  (SELECT l.id AS store_id,
          r.name AS ROLE,
          ud.first_name || ' ' || ud.last_name AS holder
   FROM locations l
   LEFT JOIN role_holders rh ON rh.location_id = l.id
   AND rh.is_active = TRUE
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Area Manager',
                  'Regional Manager')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = TRUE
   WHERE l.organization = 'maestropizza-ksa-cartwheel'
     AND l.is_active = TRUE ),
     lm AS
  (SELECT store_id,
          MAX(CASE
                  WHEN ROLE = 'Area Manager' THEN holder
              END) AS "AM",
          MAX(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder
              END) AS "RM"
   FROM lr
   GROUP BY store_id),
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
       base.store_id AS "Location",
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
       "Audit No in Year",
	   lm."AM",
	   lm."RM"
FROM location_acl acl
LEFT OUTER JOIN base ON acl.job_location = base.store_id
LEFT OUTER JOIN lm ON lm.store_id = base.store_id
group by 1, 2, 3, 4, 5, 6, 7, 14,15,16
ORDER BY 1,
         2,
         4
```

---

## Maestro KSA Yes No Compliance_Main Dashboard.sql

**Tables referenced:** RAW, ROLES, _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, lm, location_acl, location_questions, locations, lr, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, role_holders, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Maestro KSA Yes No Compliance
-- Dashboard: Main Dashboard
-- Category: Maestro Pizza
-- Extracted: 2026-01-29 16:52:25
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location,max(division) as division,max(sub_division) as sub_division
   FROM user_details
   WHERE organization = 'maestropizza-ksa-cartwheel'
   and is_active = 'true'
   and job_location not in ('KNOW', 'All', 'HO')
     AND (
    (SELECT is_super_admin FROM user_details WHERE uuid = @{{:Maestro Routine Compliance-copy_1765953034.UuidParameter}})
    OR 
    division IN (SELECT division FROM user_details WHERE uuid = @{{:Maestro Routine Compliance-copy_1765953034.UuidParameter}})
    OR
    uuid IN (
        SELECT DISTINCT user_id FROM user_groups ug1
        WHERE ug1.group_id IN (
            SELECT group_id FROM user_groups ug2
            WHERE ug2.user_id = @{{:Maestro Routine Compliance-copy_1765953034.UuidParameter}}
            AND ug2.has_access = TRUE
		    AND ug1.is_active = TRUE
            AND ug2.is_active = TRUE
        )
    )
)
  group by 1),
  lr AS
  (SELECT l.id AS store_id,
          r.name AS ROLE,
          ud.first_name || ' ' || ud.last_name AS holder
   FROM locations l
   LEFT JOIN role_holders rh ON rh.location_id = l.id
   AND rh.is_active = TRUE
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Area Manager',
                  'Regional Manager')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = TRUE
   WHERE l.organization = 'maestropizza-ksa-cartwheel'
     AND l.is_active = TRUE ),
     lm AS
  (SELECT store_id,
          MAX(CASE
                  WHEN ROLE = 'Area Manager' THEN holder
              END) AS "AM",
          MAX(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder
              END) AS "RM"
   FROM lr
   GROUP BY store_id),td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'maestropizza-ksa-cartwheel'
   GROUP BY 1,
            2),
     forms AS (
    SELECT id AS form_knid,
           title AS form_name
    FROM nuggets n
    WHERE organization = 'maestropizza-ksa-cartwheel'
      AND (
           title ILIKE 'Daily Opening Record%'
        OR title ILIKE 'PRP Opening Checklist%'
        OR title ILIKE 'Daily Leftover Dough Record%'
        OR title ILIKE 'PRP Evening Checklist%'
        OR title ILIKE 'Daily Closing Waste Record%'
        OR title ILIKE 'Daily Closing  Record%'
        OR title ILIKE 'Weekly Cleaning Task Record%'
        OR title ILIKE 'Façade And Signage Cleaning%'
        OR title ILIKE 'CPP Delivery Inspection Record%'
        OR title ILIKE 'Branch Manager Quality Audit%'
        OR title ILIKE 'Oven Cleaning & Top Finger Monitoring%'
        OR title ILIKE 'Branch Endorsement checklist%'
        OR title ILIKE 'Vehicle Handover Form%'
        OR title ILIKE 'Maestro Vendors Complaint Log%'
        OR title ILIKE 'Area Manager: Opening Visit%'
        OR title ILIKE 'Area Manager: Closing Visit%'
        OR title ILIKE 'Area Manager: PRP%'
        OR title ILIKE 'Area Manager Audit Visit%'
      )
      AND is_deleted = FALSE
    GROUP BY 1,2
),
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
     _fs AS
  (SELECT DISTINCT ON (response_id) form_submissions.*,
                      form_name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   ORDER BY response_id,
            id DESC),
     fs AS
  (SELECT *
   FROM _fs
   where submit_date at time zone 'Asia/Riyadh' between @{{:Maestro Routine Compliance-copy_1765953034.Date Range.START}}::timestamp and
   @{{:Maestro Routine Compliance-copy_1765953034.Date Range.END}}::timestamp + interval ' 1day'
 ),
     fr AS
  (SELECT fs.organization,
          form_submit_id,
          form_id,
          form_name,
          sno,
          submit_date + td.diff AS submit_date,
          user_id,
          response_id,
          question_id AS parent_qid,
          question_id AS qid,
          question_type,
          response,
          1 AS rn,
          LOCATION
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   JOIN td ON fs.organization = td.organization
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT organization,
                form_submit_id,
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
                rn,
                LOCATION
   FROM
     (SELECT fs.organization,
             form_submit_id,
             form_id,
             form_name,
             sno,
             submit_date + td.diff AS submit_date,
             user_id,
             response_id,
             question_id,
             question_type,
             base.value,
             base.ordinality AS rn,
             LOCATION
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id
      JOIN td ON fs.organization = td.organization,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res), /*location_questions as (
select distinct on (nugget_id) nugget_id, question_id from question_definitions qd
where nugget_id in (select form_knid from forms)
and question_type = 'location'
order by nugget_id, section_id, sqno
),
location_response as (
select form_submit_id, (response ->> 'name')::text location_name from form_responses fr
where question_id in (select question_id from location_questions)
and form_submit_id in (select id from fs)
),*/ RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.parent_question,
          fd.question,
          q_type,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'linear_scale',
                                 'audit') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('checkboxes') THEN array_to_string(ARRAY
                                                                      (SELECT jsonb_array_elements_text(fr.response->'selected')
                                                                       UNION SELECT CASE
                                                                                        WHEN fr.response->>'otherText' IS NOT NULL THEN fr.response->>'otherText'
                                                                                        ELSE NULL
                                                                                    END), ', ')
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) + td.diff, 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('user') THEN fr.response::text
              WHEN fd.q_type IN ('upload_mixed',
                                 'upload_image',
                                 'upload_video',
                                 'upload_file') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location',
                                 'division',
                                 'sub_division') THEN fr.response ->> 'name'
              ELSE NULL
          END AS response,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS section_response,
          rn,
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          ud.first_name,
          ud.department,
          ud.division,
          ud.sub_division
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   JOIN user_details ud ON ud.uuid = fr.user_id
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
            2,
            3)
            
SELECT
    form_id,
    form_name,
    lm."AM",
    lm."RM",
    location,
    response_id,                 -- one submission / response
    submit_date::date AS submit_date,

    ROUND(
        COUNT(*) FILTER (WHERE lower(response) IN ('yes','compliance','observation'))::numeric
        / NULLIF(COUNT(*) FILTER (WHERE lower(response) IN ('yes','no','compliance','non-compliance','observation')), 0),
        4
    ) AS compliance

FROM RAW
JOIN lm ON RAW.location = lm.store_id
join location_acl on raw.location = location_acl.job_location
WHERE q_type IN ('multiple_choice','audit')
  AND lower(response) IN ('yes','no','compliance','non-compliance','observation')
and location NOT IN
('Buraidah HO',
'Jeddah HO',
'Abha HO',
'Riyadh HO',
'Dammam HO',
'Makkah HO')
GROUP BY
    form_id,
    form_name,
    location,
    response_id,
    submit_date::date,
    lm."AM",
    lm."RM"


ORDER BY
    submit_date::date DESC,
    location
```

---

## Maestro Routine Compliance-copy_1760001090_Routine Compliance - UAE.sql

**Tables referenced:** ROLES, form_compliance_v2, lm, location_acl, locations, lr, organizations, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Maestro Routine Compliance-copy_1760001090
-- Dashboard: Routine Compliance - UAE
-- Category: Maestro Pizza
-- Extracted: 2026-01-29 16:54:06
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
		"QueryTable 1"."Date Mod" AS "Date Mod",
		"QueryTable 1"."division" AS "division",
		"QueryTable 1"."sub_division" AS "sub_division",
		"QueryTable 1"."AM" AS "AM",
		"QueryTable 1"."RM"AS "RM"
FROM(WITH location_acl AS
  (SELECT DISTINCT job_location,max(division) as division,max(sub_division) as sub_division
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
               AND ug1.is_active = TRUE))
  group by 1),lr AS
  (SELECT l.id AS store_id,
          r.name AS ROLE,
          ud.first_name || ' ' || ud.last_name AS holder
   FROM locations l
   LEFT JOIN role_holders rh ON rh.location_id = l.id
   AND rh.is_active = TRUE
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Area Manager',
                  'Regional Manager')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = TRUE
   WHERE l.organization = 'maestropizza-ksa-cartwheel'
     AND l.is_active = TRUE ),
     lm AS
  (SELECT store_id,
          MAX(CASE
                  WHEN ROLE = 'Area Manager' THEN holder
              END) AS "AM",
          MAX(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder
              END) AS "RM"
   FROM lr
   GROUP BY store_id),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = @{{:OrganizationParameter}})
select fc.*, to_char("Date", 'YYYY-MM-DD') as "Date Mod",location_acl.division,location_acl.sub_division,lm."AM",lm."RM"
from form_compliance_v2 fc
join location_acl on fc."Location" = location_acl.job_location
JOIN lm on fc."Location" = lm.store_id
where fc."Organization" =@{{:OrganizationParameter}}
	 AND fc."Reminded At" BETWEEN @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
	AND "Location" NOT IN ('West Kootenay''s area', 'East Kootenay''s area', 'Alberta area')
order by 1, 5, 2 desc, 6 desc, 4)"QueryTable 1"
```

---

## Maestro Routine Compliance-copy_1765953034_Main Dashboard.sql

**Tables referenced:** ROLES, form_compliance_v2, lm, location_acl, locations, lr, organizations, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Maestro Routine Compliance-copy_1765953034
-- Dashboard: Main Dashboard
-- Category: Maestro Pizza
-- Extracted: 2026-01-29 16:52:23
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location,max(division) as division,max(sub_division) as sub_division
   FROM user_details
   WHERE organization = 'maestropizza-ksa-cartwheel'
   and is_active = 'true'
   and job_location not in ('KNOW', 'All', 'HO')
     AND (
    (SELECT is_super_admin FROM user_details WHERE uuid = @{{:UuidParameter}})
    OR 
    division IN (SELECT division FROM user_details WHERE uuid = @{{:UuidParameter}})
    OR
    uuid IN (
        SELECT DISTINCT user_id FROM user_groups ug1
        WHERE ug1.group_id IN (
            SELECT group_id FROM user_groups ug2
            WHERE ug2.user_id = @{{:UuidParameter}}
            AND ug2.has_access = TRUE
		    AND ug1.is_active = TRUE
            AND ug2.is_active = TRUE
        )
    )
)
  group by 1),lr AS
  (SELECT l.id AS store_id,
          r.name AS ROLE,
          ud.first_name || ' ' || ud.last_name AS holder
   FROM locations l
   LEFT JOIN role_holders rh ON rh.location_id = l.id
   AND rh.is_active = TRUE
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Area Manager',
                  'Regional Manager')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = TRUE
   WHERE l.organization = 'maestropizza-ksa-cartwheel'
     AND l.is_active = TRUE ),
     lm AS
  (SELECT store_id,
          MAX(CASE
                  WHEN ROLE = 'Area Manager' THEN holder
              END) AS "AM",
          MAX(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder
              END) AS "RM"
   FROM lr
   GROUP BY store_id),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = 'maestropizza-ksa-cartwheel')
select fc.*, to_char("Date", 'YYYY-MM-DD') as "Date Mod",location_acl.division,location_acl.sub_division,lm."AM",lm."RM"
from form_compliance_v2 fc
join location_acl on fc."Location" = location_acl.job_location
JOIN lm on fc."Location" = lm.store_id
where fc."Organization" ='maestropizza-ksa-cartwheel'
and fc."Location" NOT IN
('Buraidah HO',
'Jeddah HO',
'Abha HO',
'Riyadh HO',
'Dammam HO',
'Makkah HO')
	 AND fc."Reminded At" at time zone 'Asia/Riyadh' BETWEEN @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
order by 1, 5, 2 desc, 6 desc, 4
```

---

## Maestro Routine Compliance_Routine Compliance - KSA.sql

**Tables referenced:** ROLES, form_compliance_v2, lm, location_acl, locations, lr, organizations, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Maestro Routine Compliance
-- Dashboard: Routine Compliance - KSA
-- Category: Maestro Pizza
-- Extracted: 2026-01-29 16:53:18
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
		"QueryTable 1"."Date Mod" AS "Date Mod",
		"QueryTable 1"."division" AS "division",
		"QueryTable 1"."sub_division" AS "sub_division",
		"QueryTable 1"."AM" AS "AM",
		"QueryTable 1"."RM" AS "RM"
FROM( SELECT
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
		"QueryTable 1"."Date Mod" AS "Date Mod",
		"QueryTable 1"."division" AS "division",
		"QueryTable 1"."sub_division" AS "sub_division",
		"QueryTable 1"."AM" AS "AM",
		"QueryTable 1"."RM"AS "RM"
FROM(WITH location_acl AS
  (SELECT DISTINCT job_location,max(division) as division,max(sub_division) as sub_division
   FROM user_details
   WHERE organization = 'maestropizza-ksa-cartwheel'
   and is_active = 'true'
   and job_location not in ('KNOW', 'All', 'HO')
     AND (
    (SELECT is_super_admin FROM user_details WHERE uuid = 'mLQRjJd7VAAVSVnD37KNkH')
    OR 
    division IN (SELECT division FROM user_details WHERE uuid = 'mLQRjJd7VAAVSVnD37KNkH')
    OR
    uuid IN (
        SELECT DISTINCT user_id FROM user_groups ug1
        WHERE ug1.group_id IN (
            SELECT group_id FROM user_groups ug2
            WHERE ug2.user_id = 'mLQRjJd7VAAVSVnD37KNkH'
            AND ug2.has_access = TRUE
		    AND ug1.is_active = TRUE
            AND ug2.is_active = TRUE
        )
    )
)
  group by 1),lr AS
  (SELECT l.id AS store_id,
          r.name AS ROLE,
          ud.first_name || ' ' || ud.last_name AS holder
   FROM locations l
   LEFT JOIN role_holders rh ON rh.location_id = l.id
   AND rh.is_active = TRUE
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Area Manager',
                  'Regional Manager')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = TRUE
   WHERE l.organization = 'maestropizza-ksa-cartwheel'
     AND l.is_active = TRUE ),
     lm AS
  (SELECT store_id,
          MAX(CASE
                  WHEN ROLE = 'Area Manager' THEN holder
              END) AS "AM",
          MAX(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder
              END) AS "RM"
   FROM lr
   GROUP BY store_id),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = 'maestropizza-ksa-cartwheel')
select fc.*, to_char("Date", 'YYYY-MM-DD') as "Date Mod",location_acl.division,location_acl.sub_division,lm."AM",lm."RM"
from form_compliance_v2 fc
join location_acl on fc."Location" = location_acl.job_location
JOIN lm on fc."Location" = lm.store_id
where fc."Organization" ='maestropizza-ksa-cartwheel'
	 AND fc."Reminded At" BETWEEN @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
	AND "Location" NOT IN ('West Kootenay''s area', 'East Kootenay''s area', 'Alberta area')
order by 1, 5, 2 desc, 6 desc, 4)"QueryTable 1")"QueryTable 1"
```

---

## forms maestro ksa_Forms - KSA.sql

**Tables referenced:** ROLES, form_responses, form_submissions, forms, fr, fr_location, fs, lm, location_acl, locations, lr, nuggets, organizations, question_definitions, role_holders, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: forms maestro ksa
-- Dashboard: Forms - KSA
-- Category: Maestro Pizza
-- Extracted: 2026-01-29 16:53:42
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
			   lr AS
  (SELECT l.id AS store_id,
          r.name AS ROLE,
          ud.first_name || ' ' || ud.last_name AS holder
   FROM locations l
   LEFT JOIN role_holders rh ON rh.location_id = l.id
   AND rh.is_active = TRUE
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Area Manager',
                  'Regional Manager')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = TRUE
   WHERE l.organization = 'maestropizza-ksa-cartwheel'
     AND l.is_active = TRUE ),
     lm AS
  (SELECT store_id,
          MAX(CASE
                  WHEN ROLE = 'Area Manager' THEN holder
              END) AS "AM",
          MAX(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder
              END) AS "RM"
   FROM lr
   GROUP BY store_id),
     td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = @{{:OrganizationParameter}}),
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
	 to_char(fr.submit_date + td.diff, 'YYYY-MM-DD') as "Date",
	   lm."AM",
	   lm."RM"
FROM location_acl la
LEFT OUTER JOIN fr ON fr.location = la.job_location
LEFT OUTER JOIN forms ON fr.form_id = forms.id
LEFT OUTER JOIN td ON fr.organization = td.organization
LEFT OUTER JOIN user_details ud ON fr.user_id = ud.uuid
LEFT Join lm on la.job_location = lm.store_id
ORDER BY 1,
         6,
         5
```

---
