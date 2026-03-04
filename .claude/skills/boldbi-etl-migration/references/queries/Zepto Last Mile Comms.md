# Zepto Last Mile Comms

> Auto-generated on 2026-03-04 08:13

**Total queries:** 2

---

## Zepto Last Mile Comms Report (BQ)_Zepto Last Mile Comms Report.sql

**Tables referenced:** pipelines.lm_comms_report_from_mar

**Columns needing snake_case conversion:**

- `messageKNID` -> `message_knid` (alias: `message_knid AS "messageKNID"`)

- `messageTitle` -> `message_title` (alias: `message_title AS "messageTitle"`)

- `messageType` -> `message_type` (alias: `message_type AS "messageType"`)


**Original Query:**

```sql
-- Data Source: Zepto Last Mile Comms Report (BQ)
-- Dashboard: Zepto Last Mile Comms Report
-- Category: Zepto Last Mile Comms
-- Extracted: 2026-01-29 16:59:24
-- ============================================================

SELECT DAY AS `Date`,
              city AS `City`,
              messageType AS `Message Type`,
              messageKNID AS `Message KNID`,
              messageTitle AS `Message Title`,
              count(CASE
                        WHEN parse_json(analytics).`1` IS NOT NULL THEN messageKNID
                        ELSE NULL
                    END) AS `Sent`,
              count(CASE
                        WHEN parse_json(analytics).`2` IS NOT NULL THEN messageKNID
                        ELSE NULL
                    END) AS `Received`,
              count(CASE
                        WHEN parse_json(analytics).`5` IS NOT NULL THEN messageKNID
                        ELSE NULL
                    END) AS `Started`,
              count(CASE
                        WHEN parse_json(analytics).`3` IS NOT NULL THEN messageKNID
                        ELSE NULL
                    END) AS `Consumed`,
              count(CASE
                        WHEN parse_json(analytics).`4` IS NOT NULL THEN messageKNID
                        ELSE NULL
                    END) AS `Acknowledged`,
              count(CASE
                        WHEN parse_json(analytics).`6` IS NOT NULL THEN messageKNID
                        ELSE NULL
                    END) AS `Liked`
FROM pipelines.lm_comms_report_from_mar
WHERE TIMESTAMP_ADD(cast(DAY AS TIMESTAMP), INTERVAL 330 MINUTE) BETWEEN cast(@{{:Date Range.START}} AS TIMESTAMP) AND cast(TIMESTAMP_ADD(@{{:Date Range.END}}, INTERVAL 1 DAY) AS TIMESTAMP)
GROUP BY 1,
         2,
         3,
         4,
         5
		 order by `Date` desc, `Message Type`, `City`, `Sent` desc, `Received` desc, `Message Title`
```

---

## Zepto Last Mile Undelivered Report_Zepto Announcements - Undelivered Yesterday.sql

**Tables referenced:** analytics_requests, n, nuggets, received, sent, share_progress, user_details

**Original Query:**

```sql
-- Data Source: Zepto Last Mile Undelivered Report
-- Dashboard: Zepto Announcements - Undelivered Yesterday
-- Category: Zepto Last Mile Comms
-- Extracted: 2026-01-29 16:59:00
-- ============================================================

WITH n AS
  (SELECT n.id,
          n.title
   FROM share_progress sp
   JOIN nuggets n ON sp.nugget_id = n.id
   WHERE sp.created_at AT TIME ZONE 'Asia/Kolkata' BETWEEN current_date - interval '1 day' AND current_date
   GROUP BY 1,
            2),
     sent AS
  (SELECT ar.nugget_id,
          n.title,
          ar.user_id
   FROM analytics_requests ar
   JOIN n ON ar.nugget_id = n.id
   WHERE event_id = 1
     AND updated_at AT TIME ZONE 'Asia/Kolkata' >current_date - interval '1 day'),
     received AS
  (SELECT ar.nugget_id,
          sent.title,
          ar.user_id
   FROM analytics_requests ar
   JOIN sent ON ar.nugget_id = sent.nugget_id
   AND ar.user_id = sent.user_id
   WHERE event_id = 2)
SELECT sent.nugget_id AS message_knid,
       sent.title AS message_title,
       ud.identifier AS rider_id,
       left(ud.identifier, 3) AS city
FROM sent
LEFT OUTER JOIN received ON sent.nugget_id = received.nugget_id
AND sent.user_id = received.user_id
LEFT OUTER JOIN user_details ud ON sent.user_id = ud.uuid
WHERE received.nugget_id IS NULL
  OR received.user_id IS NULL
ORDER BY 1,
         2,
         3,
         4
```

---
