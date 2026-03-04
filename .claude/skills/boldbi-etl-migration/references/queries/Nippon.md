# Nippon

> Auto-generated on 2026-03-04 08:13

**Total queries:** 1

---

## Nippon Issues_Issues.sql

**Tables referenced:** completed_status, costs, form_responses, form_submissions, issue_list, issues, issues_expanded, jsonb_each, locations, nuggets, opening, question_definitions, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Nippon Issues
-- Dashboard: Issues
-- Category: Nippon
-- Extracted: 2026-01-29 16:55:20
-- ============================================================

WITH acl AS (
  SELECT DISTINCT store
  FROM (
    SELECT l.location_name AS store
    FROM role_holders rh
    JOIN locations l ON rh.location_id = l.id AND rh.is_active = 'true'
    WHERE rh.role_holder_id = '4nhXg3bYY4DRyLffDLFRTi' AND role_holder_type = 'user'
    UNION
    SELECT l.location_name AS store
    FROM role_holders rh
    JOIN locations l ON rh.location_id = l.id AND rh.is_active = TRUE
    JOIN user_groups ug ON rh.role_holder_id = ug.group_id
    WHERE ug.user_id = '4nhXg3bYY4DRyLffDLFRTi' AND role_holder_type = 'group'
    UNION
    SELECT job_location AS store
    FROM user_details
    WHERE organization = 'nippon-hasha-cartwheel'
      AND is_active = 'true'
      AND (
        (SELECT is_super_admin FROM user_details WHERE uuid = '4nhXg3bYY4DRyLffDLFRTi')
        OR uuid IN (
          SELECT DISTINCT user_id
          FROM user_groups ug1
          WHERE ug1.group_id IN (
            SELECT group_id
            FROM user_groups ug2
            WHERE ug2.user_id = '4nhXg3bYY4DRyLffDLFRTi' AND ug2.has_access = TRUE
          )
          AND ug1.is_active = TRUE
        )
      )
  ) l
),
issue_list AS (
    SELECT issues.sno AS "Ticket No",
           reporter.division AS "Region",
         reporter.job_location as "Branch",
  issues.title as "Issues",
           reporter.sub_division AS "City",
           issues.location AS "Location",
           issues.severity AS "Severity",
           reporter.first_name || ' ' || reporter.last_name AS "Requester",
           reporter.identifier AS "Requested ID",
           reporter.uuid AS "Requester UUID",
           issues.category_name AS "Request Type",
           CASE 
               WHEN issues.status = 'open' THEN 'Pending' 
               ELSE 'Store Acknowledged' 
           END AS "Current Status",
           to_timestamp(issues.created_at::bigint/1000)  AS "Requested At",
           to_timestamp(issues.closed_at::bigint/1000)  AS "Responded At",
           to_timestamp(issues.closed_at::bigint/1000)  AS "Acknowledged At",
           issues.id AS issue_knid,
           issues.category_id AS issue_category_knid
    FROM issues
    LEFT OUTER JOIN user_details reporter ON issues.author = reporter.uuid
    LEFT OUTER JOIN user_details resolver ON issues.closed_by = resolver.uuid
    WHERE issues.organization = 'nippon-hasha-cartwheel'
      AND issues.is_deleted != 'true'
),
opening AS
  (SELECT 'nippon-hasha-cartwheel' AS organization,
          issues.id AS issue_knid,
          issues.sno AS issue_sno,
          fr.question_id AS question_knid,
          qd.qid,
          qd.qtype,
          qd.q AS question,
          CASE
              WHEN qtype IN ('dropdown',
                             'multiple_choice',
                             'checkboxes') THEN fr.response->'selected'->>0
              WHEN qtype IN ('date',
                             'datetime') THEN to_char((to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Singapore'), 'YYYY-MM-DD')
              WHEN qtype ILIKE 'upload%' THEN fr.response->0->>'response'
              ELSE fr.response->>0
          END AS response
   FROM issues
   LEFT OUTER JOIN form_submissions fs ON issues.open_form_response_id = fs.response_id
   LEFT OUTER JOIN form_responses fr ON fs.id = fr.form_submit_id
   LEFT OUTER JOIN
     (SELECT nugget_id,
             def.key AS qid,
             def.value->>'question_type' AS qtype,
                         def.value->>'question' AS q
      FROM question_definitions qds
      JOIN nuggets n ON qds.nugget_id = n.id
      CROSS JOIN jsonb_each(definition) AS def
      WHERE n.title ILIKE 'Issue Creation Form%'
        AND n.organization = 'nippon-hasha-cartwheel') qd ON fr.question_id = qd.qid
   AND fs.form_id = qd.nugget_id
   WHERE issues.organization = 'nippon-hasha-cartwheel'
     AND issues.is_deleted != 'true'
   and to_timestamp(issues.created_at::bigint/1000) between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp
   + interval '1 day'
     AND (qd.qtype NOT IN ('sign')
          OR qd.qtype IS NULL))
SELECT distinct on (issue_list."Ticket No")issue_list."Ticket No",
       issue_list."Region",
       issue_list."City",
       issue_list."Requester",
       issue_list."Requested ID",
       issue_list."Requester UUID",
	   issue_list."Issues",
	   issue_list."Branch",
  issue_list."Request Type",
       issue_list."Current Status",
       --costs."Cost",
       --completed_status."Were All Tasks Completed",
       issue_list."Requested At",
       issue_list."Responded At",
       issue_list."Acknowledged At",
       issue_list."Location",
       issue_list."Severity",
       issue_list.issue_knid,
	   MAX(CASE WHEN opening.question = 'LOCATION OF CONCERN' THEN response END) AS "Location Of Concern",
       MAX(CASE WHEN opening.question = 'TYPE OF CONCERN' THEN response END) AS "Type Of Concern"
FROM issue_list
JOIN opening on issue_list.issue_knid = opening.issue_knid
--LEFT OUTER JOIN issues_expanded ON issue_list.issue_knid = issues_expanded.issue_knid
--LEFT OUTER JOIN costs ON issue_list.issue_knid = costs.issue_knid
--LEFT OUTER JOIN completed_status ON issue_list.issue_knid = completed_status.issue_knid
where  issue_list."City" NOT IN ('KNOW')
and issue_list."Requested At" between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp
   + interval '1 day'
   group by 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16
```

---
