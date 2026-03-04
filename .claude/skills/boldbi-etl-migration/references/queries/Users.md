# Users

> Auto-generated on 2026-03-04 08:13

**Total queries:** 1

---

## Test_Test.sql

**Tables referenced:** user_details

**Original Query:**

```sql
-- Data Source: Test
-- Dashboard: Test
-- Category: Users
-- Extracted: 2026-01-29 16:59:31
-- ============================================================

select * from user_details where organization =@{{:OrganizationParameter}} and is_active = 'true' and email is not null
and uuid != @{{:UuidParameter}}
```

---
