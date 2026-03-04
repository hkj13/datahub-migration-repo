# FBH

> Auto-generated on 2026-03-04 08:13

**Total queries:** 3

---

## Audit Details temp_Audits - FBH Temp.sql

**Tables referenced:** audit_submitted_at, base, public.fbh_checkpoint_master_sheet_table_tmp

**Original Query:**

```sql
-- Data Source: Audit Details temp
-- Dashboard: Audits - FBH Temp
-- Category: FBH
-- Extracted: 2026-01-29 16:52:45
-- ============================================================

WITH base AS
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
   FROM public.fbh_checkpoint_master_sheet_table_tmp cms
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

## Audit Summary fbh temp_Audits - FBH Temp.sql

**Tables referenced:** audit_submitted_at, base, public.fbh_checkpoint_master_sheet_table_tmp

**Original Query:**

```sql
-- Data Source: Audit Summary fbh temp
-- Dashboard: Audits - FBH Temp
-- Category: FBH
-- Extracted: 2026-01-29 16:52:46
-- ============================================================

WITH  base AS
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
   FROM public.fbh_checkpoint_master_sheet_table_tmp cms)
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
FROM base 
group by 1, 2, 3, 4, 5, 6, 7, 14
ORDER BY 1,
         2,
         4
```

---

## Routine Compliance FBH_Routine Compliance.sql

**Tables referenced:** form_compliance_v2, location_acl, organizations, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Routine Compliance FBH
-- Dashboard: Routine Compliance
-- Category: FBH
-- Extracted: 2026-01-29 16:53:59
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
	 and fc."Reminded At" between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp
order by 1, 5, 2 desc, 6 desc, 4)"QueryTable 1"
```

---
