# Landers

> Auto-generated on 2026-03-04 08:13

**Total queries:** 1

---

## Routine Compliance Landers_Routine Compliance.sql

**Tables referenced:** form_compliance_v2, form_submissions, location_acl, organizations, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Routine Compliance Landers
-- Dashboard: Routine Compliance
-- Category: Landers
-- Extracted: 2026-01-29 16:52:49
-- ============================================================

SELECT
    "QueryTable 1"."Organization"      AS "Organization",
    "QueryTable 1"."Date"              AS "Date",
    "QueryTable 1"."Routine KNID"      AS "Routine KNID",
    "QueryTable 1"."Routine Name"      AS "Routine Name",
    "QueryTable 1"."Location"          AS "Location",
    "QueryTable 1"."Reminded At"       AS "Reminded At",
    "QueryTable 1"."Responded At"      AS "Responded At",
    "QueryTable 1"."Compliance"        AS "Compliance",
    "QueryTable 1"."Submission KNID"   AS "Submission KNID",
    "QueryTable 1"."Routine #"         AS "Routine #",
    "QueryTable 1"."Date Mod"          AS "Date Mod",
    "QueryTable 1"."Start Date"        AS "Start Date",
    "QueryTable 1"."End Date"          AS "End Date",
    "QueryTable 1"."Department"        AS "Department"
FROM (
    WITH location_acl AS (
        SELECT DISTINCT job_location
        FROM user_details
        WHERE organization = @{{:OrganizationParameter}}
          AND is_active = TRUE
          AND job_location NOT IN ('KNOW', 'All', 'HO')
          AND (
                (SELECT is_super_admin
                 FROM user_details
                 WHERE uuid = @{{:UuidParameter}})
             OR uuid IN (
                    SELECT DISTINCT ug1.user_id
                    FROM user_groups ug1
                    WHERE ug1.group_id IN (
                        SELECT ug2.group_id
                        FROM user_groups ug2
                        WHERE ug2.user_id = @{{:UuidParameter}}
                          AND ug2.has_access = TRUE
                    )
                    AND ug1.is_active = TRUE
             )
          )
    ),
    td AS (
        SELECT id AS organization,
               interval '1 min' * tzoffset AS diff
        FROM organizations
        WHERE id = @{{:OrganizationParameter}}
    )
    SELECT
        fc.*,
        to_char(fc."Date", 'YYYY-MM-DD') AS "Date Mod",
        to_char(@{{:Date Range.START}}::date, 'YYYY-Mon-DD') AS "Start Date",
        to_char(@{{:Date Range.END}}::date, 'YYYY-Mon-DD')   AS "End Date",
        ud.department AS "Department"
    FROM form_compliance_v2 fc
    JOIN location_acl
        ON fc."Location" = location_acl.job_location
    LEFT JOIN (
        SELECT DISTINCT ON (response_id) response_id, user_id
        FROM form_submissions
        WHERE response_id IS NOT NULL
        ORDER BY response_id, id DESC
    ) fs ON fc."Submission KNID" = fs.response_id
    LEFT JOIN user_details ud
        ON fs.user_id = ud.uuid
    WHERE fc."Organization" = @{{:OrganizationParameter}}
      AND fc."Reminded At" BETWEEN
            @{{:Date Range.START}}::timestamp
        AND @{{:Date Range.END}}::timestamp + interval '1 day'
    ORDER BY 1, 5, 2 DESC, 6 DESC, 4
) "QueryTable 1"
```

---
