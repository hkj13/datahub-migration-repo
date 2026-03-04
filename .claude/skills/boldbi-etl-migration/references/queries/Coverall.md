# Coverall

> Auto-generated on 2026-03-04 08:13

**Total queries:** 1

---

## Coverall Latest Form Responses_Latest Form Responses.sql

**Tables referenced:** form_submissions, fs, nuggets, organizations, td, user_details

**Original Query:**

```sql
-- Data Source: Coverall Latest Form Responses
-- Dashboard: Latest Form Responses
-- Category: Coverall
-- Extracted: 2026-01-29 16:55:01
-- ============================================================

WITH td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Coverall-butterfly'),
     fs AS
  (SELECT DISTINCT ON (response_id) *
   FROM form_submissions fs
   WHERE organization = 'Coverall-butterfly'
   ORDER BY response_id,
            submit_date)
SELECT DISTINCT ON (fs.form_id) n.id AS "Form KNID",
                   n.title AS "Form Name",
                   fs.submit_date + td.diff AS "Latest Submission At",
                   ud.first_name||' '||ud.last_name AS "Submitted By"
FROM fs
JOIN nuggets n ON fs.form_id = n.id
JOIN user_details ud ON fs.user_id = ud.uuid
JOIN td ON fs.organization = td.organization
ORDER BY fs.form_id,
         fs.submit_date DESC
```

---
