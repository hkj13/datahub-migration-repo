# HomePRo

> Auto-generated on 2026-03-04 08:13

**Total queries:** 4

---

## Form Submissions_Forms with No Deadline.sql

**Tables referenced:** LATERAL, form_categories, form_responses, form_submissions, forms, fr, fr_location, fs, jsonb_object_keys, location_acl, nuggets, organizations, question_definitions, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `nuggetCategories` -> `nugget_categories` (alias: `nugget_categories AS "nuggetCategories"`)


**Original Query:**

```sql
-- Data Source: Form Submissions
-- Dashboard: Forms with No Deadline
-- Category: HomePRo
-- Extracted: 2026-01-29 16:54:56
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
   WHERE submit_date + td.diff between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1day'
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
	 f.name as folder
FROM location_acl la
LEFT OUTER JOIN fr ON fr.location = la.job_location
LEFT OUTER JOIN forms ON fr.form_id = forms.id
LEFT OUTER JOIN td ON fr.organization = td.organization
LEFT OUTER JOIN user_details ud ON fr.user_id = ud.uuid
LEFT JOIN nuggets n on fr.form_id = n.id
LEFT JOIN LATERAL (
  SELECT category_id
  FROM jsonb_object_keys(n.details->'nuggetCategories') AS category_id
) cat_id ON n.details IS NOT NULL AND n.details ? 'nuggetCategories'
LEFT JOIN form_categories f ON cat_id.category_id = f.category_id
ORDER BY 1,
         6,
         5
```

---

## HomeProQuestions_Question Summary.sql

**Tables referenced:** RAW, final_definition, form_responses, form_submissions, forms, fr, fr_location, fs, jsonb_Each, jsonb_each, metadata, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: HomeProQuestions
-- Dashboard: Question Summary
-- Category: HomePRo
-- Extracted: 2026-01-29 16:55:25
-- ============================================================

WITH /*location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'kitopi-pegasus'
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
                  WHERE ug2.user_id = @{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
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
            created_at ASC),*/
     td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'homepro-fireworks'),
     forms AS
  (SELECT id AS form_knid,
          split_part(regexp_replace(title, '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', ''), ' - ', 1) AS form_name,
          organization
   FROM nuggets
  where organization = 'homepro-fireworks'
     AND (is_deleted = 'false'
          OR is_deleted IS NULL)),
     fs AS
  (SELECT DISTINCT ON (response_id) fs2.*,
                      form_name
   FROM form_submissions fs2
   JOIN forms ON forms.form_knid = fs2.form_id
   JOIN td ON fs2.organization = td.organization
   WHERE submit_date + td.diff BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + interval '1 day'
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
   and  fr.response->>'name' in (@{{:Location}})
   ORDER BY fs.response_id,
            fs.id,
            qd.section_id,
            qd.sqno::numeric),
     metadata AS
  (SELECT fs.id,
   fs.response_Id,
          fs.form_id,
   fs.form_name,
   fs.sno,
   fs.submit_date,
          fs.organization,
          fs.user_id,
          COALESCE(fr_location.fr_location, fs.location) AS LOCATION
   FROM fs
   LEFT OUTER JOIN fr_location ON fs.response_id = fr_location.response_id
where COALESCE(fr_location.fr_location, fs.location) in (@{{:Location}}) ),
     qd_non_table_non_logic AS
  (SELECT organization,
          nugget_id AS form_knid,
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
  (SELECT organization,
          nugget_id AS form_knid,
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
  (SELECT organization,
          nugget_id AS form_knid,
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
    JOIN metadata ON metadata.id = fr.form_submit_id
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
      JOIN metadata ON metadata.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
     
     RAW AS
  (SELECT form_name AS "Form Title",
          fr.submit_date + td.diff AS "Submitted At",
          fr.sno AS "Submission No",
          fd.section_no AS "Section No",
          fd.q_no AS "Question No",
          fd.parent_question AS "Parent Question",
          fd.question AS "Question",
          fd.q_type AS "Question Type",
          rn AS "Row Number",
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
              WHEN fd.q_type IN ('upload_mixed',
                                 'upload_image',
                                 'upload_video') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS "Response",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS "Section Response",
          fd.form_knid AS "Form KNID",
          fr.response_id AS "Response KNID"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   JOIN td ON fd.organization = td.organization
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
            13
   ORDER BY 1,
            2,
            3)
SELECT metadata.location AS "Form Location",
       raw.*,
	   case when raw."Question Type" ilike '%text%' and raw."Response" ~ '^[+-]?[0-9]*\.?[0-9]+$' then raw."Response"::numeric else null end as "Num Response",
       ud.identifier AS "Submitter ID",
       ud.uuid AS "Submitter KNID",
       ud.first_name||' '||ud.last_name AS "Submitter Name",
       ud.division AS "Submitter Division",
       ud.sub_division AS "Submitter Sub Division",
       ud.job_location AS "Submitter Location",
       ud.department AS "Submitter Department",
       ud.designation AS "Submitter Designation",
       ud.job_type AS "Submitter Job Type"
FROM RAW
JOIN metadata ON raw."Response KNID" = metadata.response_id
AND raw."Form KNID"= metadata.form_id
LEFT OUTER JOIN user_details ud ON metadata.user_id = ud.uuid
WHERE raw."Question Type" IN ('dropdown',
                              'multiple_choice',
                              'linear_scale',
                              'audit')
or (raw."Question Type" ilike '%text%' and raw."Response" ~ '^[+-]?[0-9]*\.?[0-9]+$')
ORDER BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9
```

---

## homeprochecklistcompletion_Checklists.sql

**Tables referenced:** acl, hp.checklist_completions, locations, role_holders, roles, user_details, user_groups, user_roles

**Original Query:**

```sql
-- Data Source: homeprochecklistcompletion
-- Dashboard: Checklists
-- Category: HomePRo
-- Extracted: 2026-01-29 16:55:36
-- ============================================================

WITH acl AS (
  SELECT DISTINCT store_id
  FROM (
    SELECT LEFT(l.location_name, 4) AS store_id
    FROM role_holders rh
    JOIN locations l ON rh.location_id = l.id AND rh.is_active = 'true'
    WHERE rh.role_holder_id = @{{:UuidParameter}}
      AND role_holder_type = 'user'
      AND SUBSTRING(l.location_name FROM 2 FOR 3) ~ '^\d{3}$'

    UNION

    SELECT LEFT(l.location_name, 4) AS store_id
    FROM role_holders rh
    JOIN locations l ON rh.location_id = l.id AND rh.is_active = true
    JOIN user_groups ug ON rh.role_holder_id = ug.group_id
    WHERE ug.user_id = @{{:UuidParameter}}
      AND role_holder_type = 'group'
      AND SUBSTRING(l.location_name FROM 2 FOR 3) ~ '^\d{3}$'

    UNION

    SELECT LEFT(job_location, 4) AS store_id
    FROM user_details
    WHERE organization = 'homepro-fireworks'
      AND is_active = 'true'
      AND SUBSTRING(job_location FROM 2 FOR 3) ~ '^\d{3}$'
      AND (
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
  ) l
),

user_roles AS (
  SELECT DISTINCT 
    LEFT(loc.location_name, 4) AS store_id, 
    roles.name AS role
  FROM role_holders rh
  JOIN locations loc ON rh.location_id = loc.id
  JOIN roles ON rh.role_id = roles.id
where rh.is_active = true
  AND rh.role_holder_id = @{{:UuidParameter}}
    AND roles.name IS NOT NULL
)

SELECT 
  cc.*,
  ur.role
FROM acl
LEFT JOIN hp.checklist_completions cc ON acl.store_id = LEFT(cc."location", 4)
LEFT JOIN user_roles ur ON ur.store_id = acl.store_id
WHERE cc."Date" >= @{{:Date Range.START}}::timestamp
  AND cc."Date" < @{{:Date Range.END}}::timestamp + interval '1 day'
  and "District" not ilike '%Management Trainee%'
GROUP BY 
  1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18
```

---

## homeprochecklists_Forms with Deadline.sql

**Tables referenced:** LATERAL, data_team.hp_checklists, f, fc, form_categories, jsonb_object_keys, lacl, locations, nugget_collaborators, nuggets, role_holders, their, u, user_details, user_groups

**Columns needing snake_case conversion:**

- `nuggetCategories` -> `nugget_categories` (alias: `nugget_categories AS "nuggetCategories"`)

- `userTags` -> `user_tags` (alias: `user_tags AS "userTags"`)


**Original Query:**

```sql
-- Data Source: homeprochecklists
-- Dashboard: Forms with Deadline
-- Category: HomePRo
-- Extracted: 2026-01-29 16:52:38
-- ============================================================

WITH u AS (
  SELECT uuid,
         designation,
         job_location,
         is_super_admin,
         profile->'userTags'->'hp_dept'->0->>'value' AS hp_dept
  FROM user_details
  WHERE organization = 'homepro-fireworks'
    AND uuid = @{{:UuidParameter}}
),
f AS (
  SELECT id, author,
  details->'nuggetCategories' AS cats
  FROM nuggets
  WHERE classification_type = 'form'
    AND is_deleted = 'false'
    AND organization = 'homepro-fireworks'
),
fc AS (
  -- direct user collaborators
  SELECT nugget_id AS form_id, collaborator_id AS c_id
  FROM nugget_collaborators
  WHERE collaborator_type = 'user'
    AND collaborator_id = @{{:UuidParameter}}
  UNION
  -- group collaborators expanded to users
  SELECT nc.nugget_id AS form_id, ug.user_id AS c_id
  FROM nugget_collaborators nc
  JOIN user_groups ug ON nc.collaborator_id = ug.group_id
  WHERE nc.collaborator_type = 'group'
    AND ug.is_active = 'true'
    AND ug.user_id = @{{:UuidParameter}}
  UNION
  -- authorship
  SELECT id AS form_id, author AS c_id
  FROM f
  WHERE author = @{{:UuidParameter}}
),
lacl AS (
  SELECT DISTINCT store_id FROM (
    SELECT l.location_name AS store_id
    FROM role_holders rh
    JOIN locations l ON rh.location_id = l.id
    WHERE rh.is_active = 'true'
      AND rh.role_holder_id = @{{:UuidParameter}}
      AND role_holder_type = 'user'
      AND l.is_active = 'true'
    UNION
    SELECT LEFT(l.location_name, 4) AS store_id
    FROM role_holders rh
    JOIN locations l ON rh.location_id = l.id
    JOIN user_groups ug ON rh.role_holder_id = ug.group_id
    WHERE ug.user_id = @{{:UuidParameter}}
      AND rh.is_active = TRUE
      AND l.is_active = 'true'
      AND role_holder_type = 'group'
    UNION
    SELECT LEFT(job_location, 4) AS store_id
    FROM user_details
    WHERE uuid = @{{:UuidParameter}}
      AND is_active = 'true'
      AND organization = 'homepro-fireworks'
      AND (
        (SELECT is_super_admin FROM user_details WHERE uuid = @{{:UuidParameter}})
        OR uuid IN (
          SELECT user_id
          FROM user_groups ug1
          WHERE ug1.group_id IN (
            SELECT group_id
            FROM user_groups ug2
            WHERE ug2.user_id = @{{:UuidParameter}}
              AND ug2.has_access = TRUE
          )
          AND ug1.is_active = TRUE
        )
      )
  ) l
)
SELECT cc.*,
       fcat.name AS folder,
       CASE
    -- Head Office
    WHEN cc."Location" ILIKE '%H090%' THEN 'Head Office'

    /* =======================
       DM.1-SKS
       ======================= */
    WHEN cc."Location" ILIKE '%S097%' THEN 'DM.1-SKS'
    WHEN cc."Location" ILIKE '%S102%' THEN 'DM.1-SKS'
    WHEN cc."Location" ILIKE '%S063%' THEN 'DM.1-SKS'
    WHEN cc."Location" ILIKE '%S051%' THEN 'DM.1-SKS'
    WHEN cc."Location" ILIKE '%S026%' THEN 'DM.1-SKS'
    WHEN cc."Location" ILIKE '%S076%' THEN 'DM.1-SKS'

    /* =======================
       DM.2-SCS
       ======================= */
    WHEN cc."Location" ILIKE '%S104%' THEN 'DM.2-SCS'
    WHEN cc."Location" ILIKE '%S085%' THEN 'DM.2-SCS'
    WHEN cc."Location" ILIKE '%S103%' THEN 'DM.2-SCS'
    WHEN cc."Location" ILIKE '%S106%' THEN 'DM.2-SCS'
    WHEN cc."Location" ILIKE '%S049%' THEN 'DM.2-SCS'
    WHEN cc."Location" ILIKE '%S069%' THEN 'DM.2-SCS'

    /* =======================
       DM.3-PYP
       ======================= */
    WHEN cc."Location" ILIKE '%S025%' THEN 'DM.3-PYP'
    WHEN cc."Location" ILIKE '%S068%' THEN 'DM.3-PYP'
    WHEN cc."Location" ILIKE '%S023%' THEN 'DM.3-PYP'
    WHEN cc."Location" ILIKE '%S078%' THEN 'DM.3-PYP'
    WHEN cc."Location" ILIKE '%S054%' THEN 'DM.3-PYP'
    WHEN cc."Location" ILIKE '%S117%' THEN 'DM.3-PYP'

    /* =======================
       DM.4-SSS
       ======================= */
    WHEN cc."Location" ILIKE '%S028%' THEN 'DM.4-SSS'
    WHEN cc."Location" ILIKE '%S043%' THEN 'DM.4-SSS'
    WHEN cc."Location" ILIKE '%S046%' THEN 'DM.4-SSS'
    WHEN cc."Location" ILIKE '%S053%' THEN 'DM.4-SSS'
    WHEN cc."Location" ILIKE '%S066%' THEN 'DM.4-SSS'
    WHEN cc."Location" ILIKE '%S099%' THEN 'DM.4-SSS'

    /* =======================
       DM.5-SSY
       ======================= */
    WHEN cc."Location" ILIKE '%S107%' THEN 'DM.5-SSY'
    WHEN cc."Location" ILIKE '%S044%' THEN 'DM.5-SSY'
    WHEN cc."Location" ILIKE '%M015%' THEN 'DM.5-SSY'
    WHEN cc."Location" ILIKE '%S018%' THEN 'DM.5-SSY'
    WHEN cc."Location" ILIKE '%S075%' THEN 'DM.5-SSY'
    WHEN cc."Location" ILIKE '%S084%' THEN 'DM.5-SSY'
    WHEN cc."Location" ILIKE '%S100%' THEN 'DM.5-SSY'

    /* =======================
       DM.6-SMH
       ======================= */
    WHEN cc."Location" ILIKE '%S014%' THEN 'DM.6-SMH'
    WHEN cc."Location" ILIKE '%S061%' THEN 'DM.6-SMH'
    WHEN cc."Location" ILIKE '%S077%' THEN 'DM.6-SMH'
    WHEN cc."Location" ILIKE '%S115%' THEN 'DM.6-SMH'
    WHEN cc."Location" ILIKE '%S060%' THEN 'DM.6-SMH'
    WHEN cc."Location" ILIKE '%S067%' THEN 'DM.6-SMH'
    WHEN cc."Location" ILIKE '%S088%' THEN 'DM.6-SMH'

    /* =======================
       DM.7-SSH
       ======================= */
    WHEN cc."Location" ILIKE '%S040%' THEN 'DM.7-SSH'
    WHEN cc."Location" ILIKE '%M022%' THEN 'DM.7-SSH'
    WHEN cc."Location" ILIKE '%S012%' THEN 'DM.7-SSH'
    WHEN cc."Location" ILIKE '%S032%' THEN 'DM.7-SSH'
    WHEN cc."Location" ILIKE '%S071%' THEN 'DM.7-SSH'
    WHEN cc."Location" ILIKE '%S111%' THEN 'DM.7-SSH'
    WHEN cc."Location" ILIKE '%S109%' THEN 'DM.7-SSH'

    /* =======================
       DM.8-KCN
       ======================= */
    WHEN cc."Location" ILIKE '%S086%' THEN 'DM.8-KCN'
    WHEN cc."Location" ILIKE '%S024%' THEN 'DM.8-KCN'
    WHEN cc."Location" ILIKE '%S105%' THEN 'DM.8-KCN'
    WHEN cc."Location" ILIKE '%S010%' THEN 'DM.8-KCN'
    WHEN cc."Location" ILIKE '%S052%' THEN 'DM.8-KCN'

    /* =======================
       DM.9-RDK
       ======================= */
    WHEN cc."Location" ILIKE '%S015%' THEN 'DM.9-RDK'
    WHEN cc."Location" ILIKE '%S016%' THEN 'DM.9-RDK'
    WHEN cc."Location" ILIKE '%S065%' THEN 'DM.9-RDK'
    WHEN cc."Location" ILIKE '%S113%' THEN 'DM.9-RDK'
    WHEN cc."Location" ILIKE '%M012%' THEN 'DM.9-RDK'
    WHEN cc."Location" ILIKE '%S096%' THEN 'DM.9-RDK'

    /* =======================
       DM.10-UTT
       ======================= */
    WHEN cc."Location" ILIKE '%M010%' THEN 'DM.10-UTT'
    WHEN cc."Location" ILIKE '%S027%' THEN 'DM.10-UTT'
    WHEN cc."Location" ILIKE '%S038%' THEN 'DM.10-UTT'
    WHEN cc."Location" ILIKE '%S064%' THEN 'DM.10-UTT'
    WHEN cc."Location" ILIKE '%S072%' THEN 'DM.10-UTT'
    WHEN cc."Location" ILIKE '%S603%' THEN 'DM.10-UTT'

    /* =======================
       DM.11-SPK
       ======================= */
    WHEN cc."Location" ILIKE '%S058%' THEN 'DM.11-SPK'
    WHEN cc."Location" ILIKE '%M017%' THEN 'DM.11-SPK'
    WHEN cc."Location" ILIKE '%S114%' THEN 'DM.11-SPK'
    WHEN cc."Location" ILIKE '%S056%' THEN 'DM.11-SPK'
    WHEN cc."Location" ILIKE '%S034%' THEN 'DM.11-SPK'
    WHEN cc."Location" ILIKE '%S604%' THEN 'DM.11-SPK'

    /* =======================
       DM.12-PRP
       ======================= */
    WHEN cc."Location" ILIKE '%S017%' THEN 'DM.12-PRP'
    WHEN cc."Location" ILIKE '%S022%' THEN 'DM.12-PRP'
    WHEN cc."Location" ILIKE '%S083%' THEN 'DM.12-PRP'
    WHEN cc."Location" ILIKE '%S019%' THEN 'DM.12-PRP'
    WHEN cc."Location" ILIKE '%S059%' THEN 'DM.12-PRP'

    /* =======================
       DM.13-SWP
       ======================= */
    WHEN cc."Location" ILIKE '%S011%' THEN 'DM.13-SWP'
    WHEN cc."Location" ILIKE '%S035%' THEN 'DM.13-SWP'
    WHEN cc."Location" ILIKE '%S074%' THEN 'DM.13-SWP'
    WHEN cc."Location" ILIKE '%S108%' THEN 'DM.13-SWP'
    WHEN cc."Location" ILIKE '%S112%' THEN 'DM.13-SWP'

    /* =======================
       DM.14-MKS
       ======================= */
    WHEN cc."Location" ILIKE '%S013%' THEN 'DM.14-MKS'
    WHEN cc."Location" ILIKE '%S033%' THEN 'DM.14-MKS'
    WHEN cc."Location" ILIKE '%S036%' THEN 'DM.14-MKS'
    WHEN cc."Location" ILIKE '%S045%' THEN 'DM.14-MKS'
    WHEN cc."Location" ILIKE '%S062%' THEN 'DM.14-MKS'

    /* =======================
       DM.15-STK
       ======================= */
    WHEN cc."Location" ILIKE '%S047%' THEN 'DM.15-STK'
    WHEN cc."Location" ILIKE '%S079%' THEN 'DM.15-STK'
    WHEN cc."Location" ILIKE '%M009%' THEN 'DM.15-STK'
    WHEN cc."Location" ILIKE '%S020%' THEN 'DM.15-STK'
    WHEN cc."Location" ILIKE '%S050%' THEN 'DM.15-STK'

    /* =======================
       DM.16-WCS
       ======================= */
    WHEN cc."Location" ILIKE '%M001%' THEN 'DM.16-WCS'
    WHEN cc."Location" ILIKE '%M020%' THEN 'DM.16-WCS'
    WHEN cc."Location" ILIKE '%M023%' THEN 'DM.16-WCS'
    WHEN cc."Location" ILIKE '%S030%' THEN 'DM.16-WCS'
    WHEN cc."Location" ILIKE '%S081%' THEN 'DM.16-WCS'
    WHEN cc."Location" ILIKE '%S116%' THEN 'DM.16-WCS'
    WHEN cc."Location" ILIKE '%S073%' THEN 'DM.16-WCS'

    /* =======================
       DM.17-PWP
       ======================= */
    WHEN cc."Location" ILIKE '%M004%' THEN 'DM.17-PWP'
    WHEN cc."Location" ILIKE '%M024%' THEN 'DM.17-PWP'
    WHEN cc."Location" ILIKE '%M016%' THEN 'DM.17-PWP'
    WHEN cc."Location" ILIKE '%S042%' THEN 'DM.17-PWP'
    WHEN cc."Location" ILIKE '%M013%' THEN 'DM.17-PWP'
    WHEN cc."Location" ILIKE '%S031%' THEN 'DM.17-PWP'
    WHEN cc."Location" ILIKE '%S110%' THEN 'DM.17-PWP'

    /* =======================
       DM.18-WPS
       ======================= */
    WHEN cc."Location" ILIKE '%M002%' THEN 'DM.18-WPS'
    WHEN cc."Location" ILIKE '%M003%' THEN 'DM.18-WPS'
    WHEN cc."Location" ILIKE '%M011%' THEN 'DM.18-WPS'
    WHEN cc."Location" ILIKE '%M014%' THEN 'DM.18-WPS'
    WHEN cc."Location" ILIKE '%M021%' THEN 'DM.18-WPS'
    WHEN cc."Location" ILIKE '%S037%' THEN 'DM.18-WPS'

    /* =======================
       DM.19-NYI
       ======================= */
    WHEN cc."Location" ILIKE '%M019%' THEN 'DM.19-NYI'
    WHEN cc."Location" ILIKE '%M025%' THEN 'DM.19-NYI'
    WHEN cc."Location" ILIKE '%M026%' THEN 'DM.19-NYI'
    WHEN cc."Location" ILIKE '%M018%' THEN 'DM.19-NYI'
    WHEN cc."Location" ILIKE '%S041%' THEN 'DM.19-NYI'

    /* =======================
       DM.20-KNW
       ======================= */
    WHEN cc."Location" ILIKE '%M005%' THEN 'DM.20-KNW'
    WHEN cc."Location" ILIKE '%M007%' THEN 'DM.20-KNW'
    WHEN cc."Location" ILIKE '%M008%' THEN 'DM.20-KNW'
    WHEN cc."Location" ILIKE '%S057%' THEN 'DM.20-KNW'
    WHEN cc."Location" ILIKE '%S055%' THEN 'DM.20-KNW'

    /* =======================
       DM-Co MC
       ======================= */
    WHEN cc."Location" ILIKE '%S039%' THEN 'DM-Co MC.1-WNW'
    WHEN cc."Location" ILIKE '%S048%' THEN 'DM-Co MC.2-MTL'
    WHEN cc."Location" ILIKE '%S082%' THEN 'DM-Co MC.3-JWK'
    WHEN cc."Location" ILIKE '%S006%' THEN 'DM-Co MC.4-NPS'
    WHEN cc."Location" ILIKE '%M006%' THEN 'DM-Co MC.5-PRS'
    WHEN cc."Location" ILIKE '%S098%' THEN 'DM-Co MC.6-KKK'
    WHEN cc."Location" ILIKE '%S009%' THEN 'DM-Co MC.7-OSK'
    WHEN cc."Location" ILIKE '%S091%' THEN 'DM-Co MC.8-PTT'
    WHEN cc."Location" ILIKE '%S101%' THEN 'DM-Co MC.9-TPT'
    WHEN cc."Location" ILIKE '%S021%' THEN 'DM-Co MC.10-DNK'

    ELSE 'Unknown - Update the Master'
END AS "District"

FROM data_team.hp_checklists cc
JOIN f ON cc."Routine KNID" = f.id
JOIN u ON TRUE  
LEFT JOIN LATERAL (
    SELECT category_id
    FROM jsonb_object_keys(f.cats) AS category_id
) cat_id ON TRUE
LEFT JOIN form_categories fcat ON cat_id.category_id = fcat.category_id
WHERE (
    cc."Location" ~ '^[A-Za-z0-9]+ - .+'   -- standard code + name
    OR cc."Location" ilike '%H090%'             -- exception store
  )
  and cc."Reminded At" BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP 
  AND (
        -- 1. Super admin sees all
        u.is_super_admin = TRUE
        -- 2. DM/GM sees responses from their locations
        OR (
            u.designation IN ('DM', 'GM')
            AND LEFT(cc."Location", 4) IN (SELECT store_id FROM lacl)
        )
        -- 3. H090 or DM COMC sees responses to forms they contributed to
        OR (
            (u.job_location = 'H090' OR u.hp_dept ILIKE 'dm comc%')
            AND cc."Routine KNID" IN (SELECT form_id FROM fc)
        )
    )
```

---
