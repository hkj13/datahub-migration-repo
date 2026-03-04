# Army Navy

> Auto-generated on 2026-03-04 08:13

**Total queries:** 1

---

## Army Nave Routine_Routine Compliance.sql

**Tables referenced:** form_compliance_v2, location_acl, organizations, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Army Nave Routine
-- Dashboard: Routine Compliance
-- Category: Army Navy
-- Extracted: 2026-01-29 16:53:34
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
				"QueryTable 1"."location_type" AS "location_type"
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
select fc.*, to_char("Date", 'YYYY-MM-DD') as "Date Mod",
	 CASE
    WHEN "Location" ILIKE ANY (ARRAY[
        '%Alabang West%',
        '%Araneta%',
        '%Army Navy C5 Extension%',
        '%Banawe%',
        '%Bicutan%',
        '%Bocaue%',
        '%Cainta%',
        '%Calamba 2%',
        '%Caltex Slex%',
        '%Camp John Hay%',
        '%Commerce Ave%',
        '%Daang Hari%',
        '%Dela Rosa 1%',
        '%Dela Rosa 3%',
        '%Dewey%',
        '%Drive and Dine%',
        '%Eastwood%',
        '%Emerald Ave.%',
        '%Friendship Highway%',
        '%Hampton%',
        '%Holy Spirit%',
        '%Imus Bayan%',
        '%It Park Cebu%',
        '%Jupiter%',
        '%Katipunan%',
        '%Kawit%',
        '%Las Pinas%',
        '%Lipa%',
        '%McKinley%',
        '%Mezza%',
        '%Net Quad%',
        '%Pavilion%',
        '%Pearl Place%',
        '%Petron Marilao%',
        '%Scape%',
        '%Session Road%',
        '%Shaw%',
        '%Shell Acienda%',
        '%Silang Village%',
        '%Sta. Lucia Mall%',
        '%Subic%',
        '%Tagaytay 2%',
        '%Tarlac%',
        '%Tomas Morato%',
        '%UPT%',
        '%UST%',
        '%Valero%',
        '%Vermosa%',
        '%Visayas Ave%',
        '%White Plains%',
	    '%Governor%'
    ]) THEN '24 Hrs'
    ELSE 'Non 24 Hrs'
END AS location_type
from form_compliance_v2 fc
join location_acl on fc."Location" = location_acl.job_location
where fc."Organization" =@{{:OrganizationParameter}}
	 AND fc."Reminded At" BETWEEN @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
order by 1, 5, 2 desc, 6 desc, 4)"QueryTable 1"
```

---
