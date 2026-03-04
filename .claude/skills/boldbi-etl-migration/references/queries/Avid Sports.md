# Avid Sports

> Auto-generated on 2026-03-04 08:13

**Total queries:** 1

---

## Shift Report-copy_1735657956_Attendance.sql

**Tables referenced:** location_acl, organizations, shift_attendance, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Shift Report-copy_1735657956
-- Dashboard: Attendance
-- Category: Avid Sports
-- Extracted: 2026-01-29 16:57:17
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
   and is_active = 'true'
  and job_location not in ('KNOW', 'HQ', 'Head Office', 'All')
   and job_location not ilike 'Head Office%'
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
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = @{{:OrganizationParameter}})
SELECT shift_attendance."Shift ID",
shift_attendance."UUID",
shift_attendance."Employee Name",
shift_attendance."Employee ID",
shift_attendance."Designation",
shift_attendance."Department",
shift_attendance."Division",
shift_attendance."Sub Division",
shift_attendance."Home Location",
shift_attendance."Job Type",
shift_attendance."organization",
shift_attendance."Employee Status",
(shift_attendance."Scheduled Start Time" + td.diff) as "Scheduled Start Time",
(shift_attendance."Scheduled End Time" + td.diff) as "Scheduled End Time",
shift_attendance."Shift Location",
shift_attendance."Scheduled Break Hours",
(shift_attendance."Actual Clockin Time" + td.diff) as "Actual Clockin Time",
(shift_attendance."Actual Clockout Time" + td.diff) as "Actual Clockout Time",
shift_attendance."Clockin Beacon",
shift_attendance."Clockin Geofence",
shift_attendance."ci_qr_location_id",
shift_attendance."Clockout Beacon",
shift_attendance."Clockout Geofence",
shift_attendance."co_qr_location_id",
shift_attendance."Actual Work Duration",
shift_attendance."Actual Break Hours",
shift_attendance."Status",
shift_attendance."Scheduled Count",
shift_attendance."Leave Count",
shift_attendance."Present Count",
shift_attendance."Late Count",
shift_attendance."Absent Count",
shift_attendance."Clockin QR Location",
shift_attendance."Clockout QR Location"
FROM shift_attendance
JOIN location_acl ON shift_attendance."Shift Location" = location_acl.job_location
join td on shift_attendance."organization" = td.organization
where shift_attendance."organization" = @{{:OrganizationParameter}}
```

---
