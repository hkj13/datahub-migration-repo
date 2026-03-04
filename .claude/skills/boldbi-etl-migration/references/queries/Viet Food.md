# Viet Food

> Auto-generated on 2026-03-04 08:13

**Total queries:** 2

---

## Routine - Viet_Routine Compliance - Viet.sql

**Tables referenced:** form_compliance_v2, location_acl, organizations, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Routine - Viet
-- Dashboard: Routine Compliance - Viet
-- Category: Viet Food
-- Extracted: 2026-01-29 16:55:07
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
	 and fc."Reminded At" >= date_trunc('Month', @{{:Date Range.START}}::timestamp)
order by 1, 5, 2 desc, 6 desc, 4)"QueryTable 1"
```

---

## Viet Issues_Issues.sql

**Tables referenced:** alamar_dominos_maintenance_requests_table, issue_list, issues, user_acl, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Viet Issues
-- Dashboard: Issues
-- Category: Viet Food
-- Extracted: 2026-01-29 16:54:51
-- ============================================================

WITH user_acl AS (
  SELECT uuid, organization
  FROM user_details
  WHERE organization = @{{:OrganizationParameter}}
    AND is_active = 'true'
    AND (
      (SELECT is_super_admin
       FROM user_details
       WHERE uuid = @{{:UuidParameter}})
      OR uuid IN (
        SELECT DISTINCT user_id
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
    AND phone_number NOT ILIKE '+9111%'
),

issue_list AS (
  SELECT 
    issues.sno AS "Ticket No",
    reporter.division AS "Country",
    --reporter.region AS "Region",
    reporter.sub_division AS "City",
    issues.location AS "Location",
    issues.severity AS "Severity",
    reporter.first_name || ' ' || reporter.last_name AS "Requester",
    reporter.identifier AS "Requested ID",
    reporter.uuid AS "Requester UUID",
    REPLACE(issues.category_name, ' Maintenance', '') AS "Request Type",
    CASE
      WHEN issues.status = 'open' THEN 'Pending'
      ELSE 'Store Acknowledged'
    END AS "Current Status",
    TO_TIMESTAMP(issues.created_at::bigint / 1000) AT TIME ZONE 'Asia/Dubai' AS "Requested At",
    TO_TIMESTAMP(issues.closed_at::bigint / 1000) AT TIME ZONE 'Asia/Dubai' AS "Responded At",
    TO_TIMESTAMP(issues.closed_at::bigint / 1000) AT TIME ZONE 'Asia/Dubai' AS "Acknowledged At",
    issues.id AS issue_knid,
    issues.category_id AS issue_category_knid
  FROM issues
  LEFT JOIN user_details reporter ON issues.author = reporter.uuid
  LEFT JOIN user_details resolver ON issues.closed_by = resolver.uuid
  WHERE issues.organization = 'Viet-Food-cartwheel'
    AND TO_TIMESTAMP(issues.created_at::bigint / 1000) AT TIME ZONE 'Asia/Dubai'
        BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + INTERVAL '1 day'
    AND issues.is_deleted != 'true'
)

-- Uncomment and fix below parts if needed:
--, issues_q AS (...)
--, issues_expanded AS (...)
--, cost_q AS (...)
--, costs AS (...)
--, completed_q AS (...)
--, completed_status AS (...)

SELECT requests.*
FROM user_acl
JOIN (
  -- select *, null as "Location", null as "Severity", NULL AS "issue_knid" from alamar_dominos_maintenance_requests_table requests
  -- union
  SELECT 
    "Ticket No",
    "Country",
    --"Region",
    "City",
    "Requester",
    "Requested ID",
    "Requester UUID",
    "Request Type",
    "Current Status",
    "Requested At",
    "Responded At",
    "Acknowledged At",
    "Location",
    "Severity",
    issue_knid
  FROM issue_list
  WHERE "Country" NOT ILIKE 'KNOW'
) requests ON user_acl.uuid = requests."Requester UUID"
```

---
