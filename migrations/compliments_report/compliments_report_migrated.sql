-- Data Source: Compliments Report
-- Dashboard: Compliments Report
-- Category: Generic
-- Migration Date: 2026-03-04
-- Database: generic
-- ============================================================
-- MIGRATED QUERY - DataHub (generic_public schema)
-- ============================================================
-- Changes:
--   Table: user_details -> generic_public.user_details (5 occurrences)
--   Table: user_groups -> generic_public.user_groups (2 occurrences)
--   Table: organizations -> generic_public.organizations (1 occurrence)
--   Table: form_responses -> generic_public.form_responses (1 occurrence)
--   Table: form_submissions -> generic_public.form_submissions (1 occurrence)
--   Columns: No changes needed (all already snake_case; 'userId' refs are JSON keys)
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM generic_public.user_details
   WHERE organization = @{{:OrganizationParameter}}
   and is_active = 'true'
  and job_location not in ('KNOW', 'HQ', 'Head Office', 'All')
   and job_location not ilike 'Head Office%'
   AND (
            (SELECT is_super_admin
             FROM generic_public.user_details
             WHERE uuid = @{{:UuidParameter}})
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM generic_public.user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM generic_public.user_groups ug2
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
td as (select id as organization, interval '1 min'*tzoffset as diff from generic_public.organizations where id = @{{:OrganizationParameter}}),
base  as (SELECT (submit_date + td.diff)::date AS date,
          max(CASE
                  WHEN question_id = 'section-1' THEN response -> 'sender' ->> 'userId'
                  ELSE NULL
              END) AS giver,
          max(CASE
                  WHEN question_id = '-notes' THEN response ->> 0
                  ELSE NULL
              END) AS compliment,
          max(CASE
                  WHEN question_id = '-compliment-type' THEN response -> 'selected' ->> 0
                  ELSE NULL
              END) AS compliment_type,
          max(CASE
                  WHEN question_id = '-compliment-to' THEN response -> 0 -> 'contact' ->> 'userId'
                  ELSE NULL
              END) AS recipient,
          form_submissions.id AS compliment_id
   FROM generic_public.form_responses
   JOIN generic_public.form_submissions ON form_responses.form_submit_id = form_submissions.id
      join td on form_submissions.organization = td.organization
   WHERE submit_date + td.diff > current_timestamp - interval '6 months'
     AND form_submissions.form_id = '-compliment-form'
     AND form_submissions.organization = @{{:OrganizationParameter}}
        GROUP BY 1,
            form_submit_id,
            6)

        SELECT base.date AS "Compliment Date",
       base.compliment_type AS "Compliment Type",
       base.compliment AS "Compliment",
       recipient_details.first_name||recipient_details.last_name AS "Compliment Recipient Name",
       recipient_details.identifier AS "Compliment Recipient Employee ID",
       recipient_details.designation as "Compliment Recipient Designation",
       recipient_details.job_location AS "Compliment Recipient Outlet",
       giver_details.first_name||giver_details.last_name AS "Compliment Giver Name",
       giver_details.identifier AS "Compliment Giver Employee ID",
       giver_details.designation as "Compliment Giver Designation",
       giver_details.job_location AS "Compliment Giver Outlet",
       base.compliment_id AS "Compliment Submit ID (KNOW Internal)"
       from base
       JOIN generic_public.user_details giver_details ON base.giver = giver_details.uuid
JOIN generic_public.user_details recipient_details ON base.recipient = recipient_details.uuid
join location_acl loc on loc.job_location = giver_details.job_location or loc.job_location = recipient_details.job_location
order by 1 desc, 2, 4, 8
