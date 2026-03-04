# Galaxy Demo

> Auto-generated on 2026-03-04 08:13

**Total queries:** 2

---

## Galaxy Demo Attendance Data_Attendance.sql

**Tables referenced:** organizations, shift_attendance, td

**Original Query:**

```sql
-- Data Source: Galaxy Demo Attendance Data
-- Dashboard: Attendance
-- Category: Galaxy Demo
-- Extracted: 2026-01-29 16:56:38
-- ============================================================

With td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = 'loctoc-com')
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
join td on shift_attendance."organization" = td.organization
where shift_attendance."organization" = 'loctoc-com'
and shift_attendance."Scheduled Start Time" between '2023-09-05' and '2023-09-20'
```

---

## Galaxy Demo Routine Compliance_Routine Compliance.sql

**Tables referenced:** form_compliance_v2, organizations

**Original Query:**

```sql
-- Data Source: Galaxy Demo Routine Compliance
-- Dashboard: Routine Compliance
-- Category: Galaxy Demo
-- Extracted: 2026-01-29 16:53:40
-- ============================================================

With td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = 'loctoc-com')
select fc.*, to_char("Date", 'YYYY-MM-DD') as "Date Mod"
from form_compliance_v2 fc
where fc."Organization" ='loctoc-com'	 and "Routine KNID" in ('-NVi6Gmc76u3r3jnSeDA', '-N3x9w-9QyjjhmoSrEFh', '-NViH7o9rYGnzQWg5R1t')
	 and "Location" not in ('HQ', 'KNOW')
	 and "Date" between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
order by 1, 5, 2 desc, 6 desc, 4
```

---
