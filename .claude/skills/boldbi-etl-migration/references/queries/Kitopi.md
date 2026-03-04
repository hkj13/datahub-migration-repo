# Kitopi

> Auto-generated on 2026-03-04 08:13

**Total queries:** 14

---

## Kitopi - Deviation Report_Deviation Report.sql

**Tables referenced:** Dish, chiller_freezer_1, chiller_freezer_2, chiller_freezer_3, cold_holding_1, cold_holding_2, cooking_reheating_1, hot_holding_1, hot_holding_2, ice_bath_1, ice_bath_2, ice_bath_3, kitopi.blast_chiller_and_ice_bath_sheet1, kitopi.blast_chiller_and_ice_bath_sheet2, kitopi.events_cold_holding_temperature_log_sheet1, kitopi.events_cold_holding_temperature_log_sheet2, kitopi.events_hot_holding_temperature_log_sheet1, kitopi.events_hot_holding_temperature_log_sheet2, kitopi.frm2_vegetable_sanitation_monitoring_records_sheet1, kitopi.frm_15_pot_wash_dish_wash_machine_verification_chklst_sheet1, kitopi.frm_15_pot_wash_dish_wash_machine_verification_chklst_sheet2, kitopi.frm_15_pot_wash_dish_wash_machine_verification_chklst_sheet3, kitopi.frm_1_inspection_receiving_inspection_rejection_log_sheet1, kitopi.frm_chiller_freezer_temperature_log_sheet1, kitopi.frm_chiller_freezer_temperature_log_sheet2, kitopi.frm_chiller_freezer_temperature_log_sheet3, kitopi.frm_cooking_baking_reheating_sheet1, kitopi.frm_cooking_baking_reheating_sheet2, kitopi.rice_p_h_sheet1, kitopi.thawing_monitoring_record_sheet1, kitopi.thawing_monitoring_record_sheet2, kitopi.weekly_thermometer_p_h_calibration_record_sheet1, kitopi.weekly_thermometer_p_h_calibration_record_sheet2, kitopi.weekly_thermometer_p_h_calibration_record_sheet3, potwash_1, potwash_2, potwash_3, receiving_2, receiving_3, rice_ph_1, rice_ph_2, start, table, thawing_fail_1, thawing_fail_2, vegetable_sanitation_1, vegetable_sanitation_2

**Columns needing snake_case conversion:**

- `pH` -> `p_h` (alias: `p_h AS "pH"`)


**Original Query:**

```sql
-- Data Source: Kitopi - Deviation Report
-- Dashboard: Deviation Report
-- Category: Kitopi
-- Extracted: 2026-01-29 16:54:16
-- ============================================================

WITH cooking_reheating_1 AS (
  SELECT 
    s1."Form Name",
   s1."Location",
    s1."Sent At",
    'Total Records where Cooking Validation = Fail:' AS metric,
    COUNT(DISTINCT CASE 
      WHEN s2."Core Temperature (°C)"::numeric < 75 
      THEN s2."Submission Number"  
      ELSE NULL 
    END) AS value,
  s1."Response Link",
  max(s2."Core Temperature (°C)") as response
  FROM kitopi.frm_cooking_baking_reheating_sheet2 s2
  JOIN kitopi.frm_cooking_baking_reheating_sheet1 s1 
    ON s2."Submission Number" = s1."Submission Number"
  WHERE s2."Core Temperature (°C)" != ''
  GROUP BY 1, 2, 3,
    s1."Response Link"
),

thawing_fail_1 AS (
  SELECT 
    t1."Form Name",
    t1."Location",
    t1."Sent At",
    'Are all items consumed with 2 days from start of thawing' AS metric,
     COUNT(DISTINCT CASE 
  WHEN (
    to_timestamp(NULLIF(NULLIF(t2."Date & Time Consumed (Thawing End)", ''), ', '), 'DD Mon YY, HH:MI AM')
    -
    to_timestamp(NULLIF(NULLIF(t2."Date & Time Placed in Chiller", ''), ', '), 'DD Mon YY, HH:MI AM')
  ) > INTERVAL '2 days'
  THEN t2."Submission Number"
END) AS value,
    t1."Response Link",
  null as response
  FROM kitopi.thawing_monitoring_record_sheet2 t2
  JOIN kitopi.thawing_monitoring_record_sheet1 t1 
    ON t2."Submission Number" = t1."Submission Number"
  WHERE t2."Date & Time Placed in Chiller" != '' 
    AND t2."Date & Time Consumed (Thawing End)" != ''
  GROUP BY 1, 2, 3,t1."Response Link"
),

thawing_fail_2 AS (
  SELECT 
    t1."Form Name",
    t1."Location",
    t1."Sent At",
    'Are all items consumed before original expiry date' AS metric,
    COUNT(DISTINCT CASE 
      WHEN t2."Date & Time Consumed (Thawing End)"::timestamp 
           >= t2."Original Expiry Date of Item"::timestamp
      THEN t2."Submission Number"
      ELSE NULL
    END) AS value,
  t1."Response Link",
    null as response
  FROM kitopi.thawing_monitoring_record_sheet2 t2
  JOIN kitopi.thawing_monitoring_record_sheet1 t1 
    ON t2."Submission Number" = t1."Submission Number"
  WHERE t2."Date & Time Consumed (Thawing End)" != '' 
    AND t2."Original Expiry Date of Item" != ''
  GROUP BY 1, 2, 3,t1."Response Link"
),
receiving_2 AS (
  SELECT 
    t."Form Name",
    t."Location",
    t."Sent At",
    'Total Records where Frozen Products NOT at least -18°C:' AS metric,
    COUNT(DISTINCT CASE 
      WHEN t."Are all frozen products at least - 18 C (no defrosting sign) ?" ILIKE 'No'
      THEN t."Submission Number"
      ELSE NULL
    END) AS value,
  t."Response Link",
    max("Are all frozen products at least - 18 C (no defrosting sign) ?") as response
  FROM kitopi.frm_1_inspection_receiving_inspection_rejection_log_sheet1 t
  WHERE t."Are all frozen products at least - 18 C (no defrosting sign) ?" != ''
  GROUP BY 1, 2, 3, t."Response Link"
),
receiving_3 AS (
  SELECT 
    t."Form Name",
    t."Location",
    t."Sent At",
    'Total Records where Chilled Products NOT below 5°C:' AS metric,
    COUNT(DISTINCT CASE 
      WHEN t."Are all chilled products checked below 5 C ?" ILIKE 'No'
      THEN t."Submission Number"
      ELSE NULL
    END) AS value,
  t."Response Link",
    max(t."Are all chilled products checked below 5 C ?") as response
  FROM kitopi.frm_1_inspection_receiving_inspection_rejection_log_sheet1 t
  WHERE t."Are all chilled products checked below 5 C ?" != ''
  GROUP BY 1, 2, 3,  t."Response Link"
),
vegetable_sanitation_1 AS (
  SELECT
    t."Form Name",
    t."Location",
    t."Sent At",
    'Total Records where Soaking Time is less than required limit:' AS metric,
    COUNT(DISTINCT CASE
      WHEN (
        -- KG 7.1: needs ≥ 1 min
        (t."Select type of chemical used" = 'KG 7.1 ( Lactic Acid Based)' AND t."Soaking time (in mins) select as applies"::numeric < 1)
        OR
        -- Rezoxy: needs ≥ 2 min
        (t."Select type of chemical used" = 'Rezoxy (Hydrogen Peroxide Based)' AND t."Soaking time (in mins) select as applies"::numeric < 2)
        OR
        -- Chlorine Tablet: needs ≥ 10 min (default - based on FOR CK and FOR SK lowest standard)
        (t."Select type of chemical used" = 'v Chlorine Tablet' AND t."Soaking time (in mins) select as applies"::numeric < 10)
        OR
        -- Suma Eden D4.5: needs ≥ 2 min
        (t."Select type of chemical used" = 'Suma Eden D4.5' AND t."Soaking time (in mins) select as applies"::numeric < 2)
        OR
        -- Partek Solution: needs ≥ 2 min
        (t."Select type of chemical used" = 'Partek Solution' AND t."Soaking time (in mins) select as applies"::numeric < 2)
      )
      THEN t."Submission Number"
      ELSE NULL
    END) AS value,
  t."Response Link",
    null as response
  FROM kitopi.frm2_vegetable_sanitation_monitoring_records_sheet1 t
  WHERE t."Select type of chemical used" IN (
          'Rezoxy (Hydrogen Peroxide Based)',
          'v Chlorine Tablet',
          'KG 7.1 ( Lactic Acid Based)',
          'Suma Eden D4.5',
          'Partek Solution'
        )
    AND t."Soaking time (in mins) select as applies" != ''
  GROUP BY 1, 2, 3, t."Response Link"
),
vegetable_sanitation_2 AS (
  SELECT
    t."Form Name",
    t."Location",
    t."Sent At",
    'Total Records where Incorrect Chemical Concentration was used:' AS metric,
    COUNT(DISTINCT CASE
    WHEN (
        -- KG 7.1: pH should be 2-3
        (t."Select type of chemical used" = 'KG 7.1 ( Lactic Acid Based)'
         AND (
              t."Concentration (put number as shown in Strip) (PPM/pH) (Type the"::numeric < 2
              OR t."Concentration (put number as shown in Strip) (PPM/pH) (Type the"::numeric > 3
             )
        )
        OR
        -- Rezoxy: must be 5000 ppm
        (t."Select type of chemical used" = 'Rezoxy (Hydrogen Peroxide Based)'
         AND t."Concentration (put number as shown in Strip) (PPM/pH) (Type the"::numeric != 5000
        )
        OR
        -- Chlorine Tablet: only 25, 50, 100 ppm allowed
        (t."Select type of chemical used" = 'v Chlorine Tablet'
         AND t."Concentration (put number as shown in Strip) (PPM/pH) (Type the"::numeric NOT IN (25, 50, 100)
        )
        OR
        -- Suma Eden D4.5: pH should be 2-3
        (t."Select type of chemical used" = 'Suma Eden D4.5'
         AND (
              t."Concentration (put number as shown in Strip) (PPM/pH) (Type the"::numeric < 2
              OR t."Concentration (put number as shown in Strip) (PPM/pH) (Type the"::numeric > 3
             )
        )
        OR
        -- Partek Solution: 60-80 ppm
        (t."Select type of chemical used" = 'Partek Solution'
         AND (
              t."Concentration (put number as shown in Strip) (PPM/pH) (Type the"::numeric < 60
              OR t."Concentration (put number as shown in Strip) (PPM/pH) (Type the"::numeric > 80
             )
        )
    )
    THEN t."Submission Number"
END) AS value,
  t."Response Link",
    null as response
  FROM kitopi.frm2_vegetable_sanitation_monitoring_records_sheet1 t
  WHERE t."Select type of chemical used" IN (
          'Rezoxy (Hydrogen Peroxide Based)',
          'v Chlorine Tablet',
          'KG 7.1 ( Lactic Acid Based)',
          'Suma Eden D4.5',
          'Partek Solution'
        )
    AND t."Concentration (put number as shown in Strip) (PPM/pH) (Type the" != ''
  GROUP BY 1, 2, 3, t."Response Link"
),
chiller_freezer_1 AS (
    SELECT
    t1."Form Name",
    t1."Location",
    t1."Sent At",
    'Total Records where Chiller > 5°C or Freezer > -18°C:' AS metric,
    COUNT(DISTINCT CASE
      WHEN (
        (t2."Chiller Temperature (C)" != '' AND t2."Chiller Temperature (C)"::numeric > 5)
        OR
        (t3."Temperature (C)" != '' AND t3."Temperature (C)"::numeric > -18)
      )
      THEN t1."Submission Number"
    END) AS value,
  t1."Response Link",
MAX(
      CASE
        WHEN t2."Chiller Temperature (C)" != '' AND t2."Chiller Temperature (C)"::numeric > 5
          THEN t2."Chiller Temperature (C)"
        WHEN t3."Temperature (C)" != '' AND t3."Temperature (C)"::numeric > -18
          THEN t3."Temperature (C)"
      END
    ) AS response
  FROM kitopi.frm_chiller_freezer_temperature_log_sheet1 t1
  LEFT JOIN kitopi.frm_chiller_freezer_temperature_log_sheet2 t2
    ON t1."Submission Number" = t2."Submission Number"
  LEFT JOIN kitopi.frm_chiller_freezer_temperature_log_sheet3 t3
    ON t1."Submission Number" = t3."Submission Number"
  WHERE (t2."Chiller Temperature (C)" != '' OR t3."Temperature (C)" != '')
  GROUP BY 1, 2, 3,  t1."Response Link"
),
chiller_freezer_2 AS (
  SELECT
    t1."Form Name",
    t1."Location",
    t1."Sent At",
    'Total Records where chiller/freezer counts do not match actual logs:' AS metric,
    COUNT(DISTINCT CASE
      WHEN (
        -- Compare chillers count
        (t1."Total Number of chillers in the location"::numeric != COALESCE(chiller_count, 0))
        OR
        -- Compare freezers count
        (t1."Total Number of Freezers in the location ( Put 0 if no freezer)"::numeric != COALESCE(freezer_count, 0))
      )
      THEN t1."Submission Number"
    END) AS value,
  t1."Response Link",
    null as response
  FROM kitopi.frm_chiller_freezer_temperature_log_sheet1 t1
  LEFT JOIN (
    SELECT "Submission Number", COUNT(*) AS chiller_count
    FROM kitopi.frm_chiller_freezer_temperature_log_sheet2
    WHERE "Chiller Temperature (C)" != ''
    GROUP BY "Submission Number"
  ) ch ON t1."Submission Number" = ch."Submission Number"
  LEFT JOIN (
    SELECT "Submission Number", COUNT(*) AS freezer_count
    FROM kitopi.frm_chiller_freezer_temperature_log_sheet3
    WHERE "Temperature (C)" != ''
    GROUP BY "Submission Number"
  ) fr ON t1."Submission Number" = fr."Submission Number"
  WHERE t1."Total Number of chillers in the location" != ''
    AND t1."Total Number of Freezers in the location ( Put 0 if no freezer)" != ''
  GROUP BY 1, 2, 3,  t1."Response Link"
),
chiller_freezer_3 AS (
  SELECT
    t."Form Name",
    t."Location",
    t."Sent At",
    'Total Records where temperature checks exceeded 4-hour gap:' AS metric,
    COUNT(DISTINCT t."Submission Number") AS value,
    t."Response Link",
    null as response
  FROM (
    SELECT
      f1."Form Name",
      f1."Location",
      f1."Sent At",
      f1."Submission Number",
	  f1."Response Link",
      LAG(f1."Sent At") OVER (PARTITION BY f1."Location", DATE(f1."Sent At") ORDER BY f1."Sent At") AS prev_sent_at
    FROM kitopi.frm_chiller_freezer_temperature_log_sheet1 f1
    WHERE f1."Sent At" IS NOT NULL
  ) t
  WHERE t.prev_sent_at IS NOT NULL
    AND EXTRACT(EPOCH FROM (t."Sent At" - t.prev_sent_at)) / 3600 > 4
  GROUP BY t."Form Name", t."Location", t."Sent At",t."Response Link"
),
ice_bath_1 AS (SELECT
    t."Form Name",
    l."Location",
    t."Sent At",
    'Total records where cooling took more than 6 hours:' AS metric,
    COUNT(DISTINCT t."Submission Number") AS value,
			   t."Response Link",
    null as response
  FROM kitopi.blast_chiller_and_ice_bath_sheet2 t
  JOIN kitopi.blast_chiller_and_ice_bath_sheet1 l
    ON t."Submission Number" = l."Submission Number"
  WHERE t."Time when placed in ice / Blast Chiller" IS NOT NULL
    AND t."Time below When food was found below 5 °C" IS NOT NULL
    AND EXTRACT(EPOCH FROM (
          t."Time below When food was found below 5 °C"::timestamp 
          - t."Time when placed in ice / Blast Chiller"::timestamp
        )) / 3600 > 6
  GROUP BY t."Form Name", l."Location", t."Sent At", t."Response Link"),
ice_bath_2 AS (  SELECT
    t."Form Name",
    l."Location",
    t."Sent At",
    'Total records where temp after 2 hours > 21°C:' AS metric,
    COUNT(DISTINCT t."Submission Number") AS value,
			   t."Response Link",
    null as response
  FROM kitopi.blast_chiller_and_ice_bath_sheet2 t
  JOIN kitopi.blast_chiller_and_ice_bath_sheet1 l
    ON t."Submission Number" = l."Submission Number"
  WHERE t."Temperature after 2 Hours of keeping ice  / blast chiller" IS NOT NULL
    AND t."Temperature after 2 Hours of keeping ice  / blast chiller"::numeric > 21
  GROUP BY t."Form Name", l."Location", t."Sent At",t."Response Link"),
  
ice_bath_3 AS ( SELECT
    t."Form Name",
    l."Location",
    t."Sent At",
    'Total records where temp after 4 hours > 4°C:' AS metric,
    COUNT(DISTINCT t."Submission Number") AS value,
			   t."Response Link",
    null as response
  FROM kitopi.blast_chiller_and_ice_bath_sheet2 t
  JOIN kitopi.blast_chiller_and_ice_bath_sheet1 l
    ON t."Submission Number" = l."Submission Number"
  WHERE t."Temperature after 4 hours (Keeping inside the Chiller)" IS NOT NULL
    AND t."Temperature after 4 hours (Keeping inside the Chiller)"::numeric > 4
  GROUP BY t."Form Name", l."Location", t."Sent At", t."Response Link"),
  
hot_holding_1 as (SELECT
    t."Form Name",
    l."Sender Location" as "Location",
    t."Sent At",
    'Total records where food temperature below required limit:' AS metric,
    COUNT(DISTINCT t."Submission Number") AS value,
				  t."Response Link",
    max(t."Product Temperature in °C") as response
  FROM kitopi.events_hot_holding_temperature_log_sheet2 t
   JOIN kitopi.events_hot_holding_temperature_log_sheet1 l
    ON t."Submission Number" = l."Submission Number"
  WHERE t."Product Temperature in °C" IS NOT NULL
    AND (
         (t."Sender Division" = 'UAE' AND t."Product Temperature in °C"::numeric < 60)
         OR
         (t."Sender Division" <> 'UAE' AND t."Product Temperature in °C"::numeric < 65)
        )
  GROUP BY t."Form Name", l."Sender Location", t."Sent At", t."Response Link"),
hot_holding_2 as (SELECT
    t."Form Name",
    t."Sender Location" as "Location",
    t."Sent At",
    'Total records where hot holding check gap exceeded 2 hours:' AS metric,
    COUNT(*) AS value,
				  t."Response Link",
    null as response
  FROM (
    SELECT
      l."Form Name",
      l."Sender Location",
      l."Sent At",
	 l."Response Link",
      EXTRACT(EPOCH FROM (l."Sent At" - LAG(l."Sent At") OVER (PARTITION BY l."Sender Location" ORDER BY l."Sent At"))) / 3600 AS gap_hours
    FROM kitopi.events_hot_holding_temperature_log_sheet1 l
  ) t
  WHERE t.gap_hours > 2
  GROUP BY t."Form Name", t."Sender Location", t."Sent At",	t."Response Link"),
  cold_holding_1 as ( SELECT
    t."Form Name",
    l."Sender Location" AS "Location",
    t."Sent At",
    'Total records where cold holding food temperature exceeded 5°C:' AS metric,
    COUNT(DISTINCT t."Submission Number") AS value,
					 t."Response Link",
    max(t."Product Temperature in °C") as response
  FROM kitopi.events_cold_holding_temperature_log_sheet2 t
  JOIN kitopi.events_cold_holding_temperature_log_sheet1 l
    ON t."Submission Number" = l."Submission Number"
  WHERE t."Product Temperature in °C" IS NOT NULL
    AND t."Product Temperature in °C"::numeric >= 5
  GROUP BY t."Form Name", l."Sender Location", t."Sent At", t."Response Link"),
  cold_holding_2 as (SELECT
    t."Form Name",
    t."Location",
    t."Sent At",
    'Total records where cold holding check gap exceeded 4 hours:' AS metric,
    COUNT(*) AS value,
					 t."Response Link",
    null as response
  FROM (
    SELECT
      l."Form Name",
      l."Sender Location" AS "Location",
      l."Sent At",
	 l."Response Link",
      EXTRACT(EPOCH FROM (l."Sent At" - LAG(l."Sent At") OVER (PARTITION BY l."Sender Location" ORDER BY l."Sent At"))) / 3600 AS gap_hours
    FROM kitopi.events_cold_holding_temperature_log_sheet1 l
  ) t
  WHERE t.gap_hours > 4
  GROUP BY t."Form Name", t."Location", t."Sent At", t."Response Link"),
  rice_ph_1 as ( SELECT
    t."Form Name",
    t."Sender Location" AS "Location",
    t."Sent At",
    'Total records where Rice pH is >= 4.6:' AS metric,
    COUNT(DISTINCT t."Submission Number") AS value,
				t."Response Link",
    max(t."pH Value of Rice") as response
  FROM kitopi.rice_p_h_sheet1 t
  WHERE t."pH Value of Rice" ~ '^[0-9]+(\.[0-9]+)?$'
  AND t."pH Value of Rice"::numeric >= 4.6
  GROUP BY t."Form Name", t."Sender Location", t."Sent At",	t."Response Link"),
  rice_ph_2 as (SELECT
    t."Form Name",
    t."Location",
    t."Sent At",
    'Total records where Rice pH check gap exceeded 4 hours:' AS metric,
    COUNT(*) AS value,
				t."Response Link",
    null as response
  FROM (
    SELECT
      r."Form Name",
      r."Sender Location" AS "Location",
      r."Sent At",
	r."Response Link",
      EXTRACT(EPOCH FROM (r."Sent At" - LAG(r."Sent At") OVER (PARTITION BY r."Sender Location" ORDER BY r."Sent At"))) / 3600 AS gap_hours
    FROM kitopi.rice_p_h_sheet1 r
  ) t
  WHERE t.gap_hours > 4
  GROUP BY t."Form Name", t."Location", t."Sent At",t."Response Link"),
  /*
  potwash_1 AS (
  SELECT
    t."Form Name",
    t."Sender Location" AS "Location",
    DATE(t."Sent At") AS "Sent At",
    'Are two forms submitted daily' AS metric,
    CASE WHEN COUNT(t."Submission Number") >= 2 THEN 0 ELSE 1 END AS value
  FROM kitopi.frm_15_pot_wash_dish_wash_machine_verification_chklst_sheet1 t
  GROUP BY t."Form Name", t."Sender Location", DATE(t."Sent At")
),

potwash_2 AS (
  -- inner prefilter to ensure only strictly numeric values go to numeric cast
  SELECT
    t."Form Name",
    t."Sender Location" AS "Location",
    t."Sent At",
    'Dishwash machine temp is logged >71 C' AS metric,
    COUNT(DISTINCT t."Submission Number") AS value
  FROM (
    SELECT
      *,
      trim(t."Final Rinse Temperature reading from Dish Temp thermometer (C)") AS temp_str
    FROM kitopi.frm_15_pot_wash_dish_wash_machine_verification_chklst_sheet2 t
  ) t
  WHERE t.temp_str ~ '^[0-9]+(\.[0-9]+)?$'          
    AND t.temp_str::numeric <= 71                   
  GROUP BY t."Form Name", t."Sender Location", t."Sent At"
),

potwash_3 AS (
  SELECT
    t."Form Name",
    t."Sender Location" AS "Location",
    t."Sent At",
    'Concentration is recorded >200' AS metric,
    COUNT(DISTINCT t."Submission Number") AS value
  FROM (
    SELECT
      *,
      trim(t."Concentration of chemical sanitizer (200 PPM - 400 PPM) only nu") AS conc_str
    FROM kitopi.frm_15_pot_wash_dish_wash_machine_verification_chklst_sheet3 t
  ) t
  WHERE t.conc_str ~ '^[0-9]+(\.[0-9]+)?$'
    AND t.conc_str::numeric < 200
  GROUP BY t."Form Name", t."Sender Location", t."Sent At"
)*/
weekly_calibration_1 as (
SELECT
    t2."Form Name",
    t2."Sender Location" AS "Location",
    DATE(t2."Sent At") AS "Sent At",
    'If probes are logged as between -1 to 1 °C and pH meter is marked 4 and 7' AS metric,
    CASE 
      WHEN (
        -- Ice Point reading check from table 3
        t3."Ice Point Method- Actual Reading °C (-1C to 1C)" ~ '^[-]?[0-9]+(\.[0-9]+)?$'
        AND t3."Ice Point Method- Actual Reading °C (-1C to 1C)"::numeric BETWEEN -1 AND 1
        
        -- pH 7 reading check from table 2
        AND t2."7.01 pH Buffer Solution - Actual Reading" ~ '^[0-9]+(\.[0-9]+)?$'
        AND t2."7.01 pH Buffer Solution - Actual Reading"::numeric BETWEEN 7 AND 7.1
        
        -- pH 4 reading check from table 2
        AND t2."4.01 pH Buffer Solution - Actual Reading" ~ '^[0-9]+(\.[0-9]+)?$'
        AND t2."4.01 pH Buffer Solution - Actual Reading"::numeric BETWEEN 4 AND 4.1
      )
      THEN 0 ELSE 1
    END AS value,
  t2."Response Link",
    null as response
  FROM kitopi.weekly_thermometer_p_h_calibration_record_sheet2 t2
  JOIN kitopi.weekly_thermometer_p_h_calibration_record_sheet3 t3
    ON t2."Submission Number" = t3."Submission Number"),
weekly_calibration_2 as (
SELECT
    t."Form Name",
    t."Sender Location" AS "Location",
    DATE_TRUNC('week', t."Sent At") AS "Sent At",
    'If record submitted weekly or not' AS metric,
    CASE WHEN COUNT(t."Submission Number") >= 1 THEN 0 ELSE 1 END AS value,
  t."Response Link",
    null as response
  FROM kitopi.weekly_thermometer_p_h_calibration_record_sheet1 t
  GROUP BY t."Form Name", t."Sender Location", t."Response Link",DATE_TRUNC('week', t."Sent At"))
SELECT *
FROM (
  SELECT * FROM cooking_reheating_1
  UNION ALL
  SELECT * FROM thawing_fail_1
  UNION ALL
  SELECT * FROM thawing_fail_2
  UNION ALL
  SELECT * FROM receiving_2
  UNION ALL
  SELECT * FROM receiving_3
  UNION ALL
  SELECT * FROM vegetable_sanitation_1 
  UNION ALL
  SELECT * FROM vegetable_sanitation_2
  UNION ALL
  SELECT * FROM chiller_freezer_1
  UNION ALL
  SELECT * FROM chiller_freezer_2
  UNION ALL
  SELECT * FROM chiller_freezer_3
  UNION ALL
  SELECT * FROM ice_bath_1
  UNION ALL
  SELECT * FROM ice_bath_2
  UNION ALL
  SELECT * FROM ice_bath_3
  UNION ALL
  SELECT * FROM hot_holding_1
  UNION ALL
  SELECT * FROM hot_holding_2
  UNION ALL
  SELECT * FROM cold_holding_1
  UNION ALL
  SELECT * FROM cold_holding_2
  UNION ALL
  SELECT * FROM rice_ph_1
  UNION ALL
  SELECT * FROM rice_ph_2
 /* UNION ALL
  SELECT * FROM potwash_1
  UNION ALL
  SELECT * FROM potwash_2
  UNION ALL
  SELECT * FROM potwash_3*/
) final_result
WHERE "Sent At" between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
  AND "Location" IS NOT NULL                
ORDER BY "Location", "Sent At", metric
```

---

## Kitopi Audit Details_Audits.sql

**Tables referenced:** kitopi.audit_details, location_acl, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Kitopi Audit Details
-- Dashboard: Audits
-- Category: Kitopi
-- Extracted: 2026-01-29 16:54:59
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'HQ',
                              'Head Office',
                              'All')
     AND job_location NOT ILIKE 'Head Office%'
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
               AND ug1.is_active = TRUE)))
			   select *
			   from kitopi.audit_details au
			   join location_acl on au."Location" = location_acl.job_location
			   where "Audit Date" between @{{:Kitopi Audit Summary.Date Range.START}}::timestamp 
			   and @{{:Kitopi Audit Summary.Date Range.END}}::timestamp + interval '1 day'
```

---

## Kitopi Audit Summary_Audits.sql

**Tables referenced:** kitopi.audit_summary, location_acl, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Kitopi Audit Summary
-- Dashboard: Audits
-- Category: Kitopi
-- Extracted: 2026-01-29 16:54:59
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'HQ',
                              'Head Office',
                              'All')
     AND job_location NOT ILIKE 'Head Office%'
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
               AND ug1.is_active = TRUE)))
			 select *
			 from kitopi.audit_summary au_s
			 join location_acl on au_s."Location" = location_acl.job_location
			 where "Audit Date" between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
```

---

## Kitopi Daily Compliance Report_Daily Compliance Report.sql

**Tables referenced:** base, form_compliance_v2, location_acl, location_map, location_off_days, organizations, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Kitopi Daily Compliance Report
-- Dashboard: Daily Compliance Report
-- Category: Kitopi
-- Extracted: 2026-01-29 16:52:23
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'kitopi-pegasus'
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'HQ',
                              'Head Office',
                              'All')
     AND job_location NOT ILIKE 'Head Office%'
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
                  WHERE ug2.user_id = @{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
     location_map AS
  (SELECT DISTINCT ON (job_location) job_location,
                      division AS country,
                      sub_division AS team,
   designation as cluster
   FROM user_details
   WHERE is_active = 'true'
     AND organization = 'kitopi-pegasus'
     AND job_type IN ('CK',
                      'SK',
                      'Kitchen',
                      'Warehouse', 'Sk')
   ORDER BY job_location,
            created_at ASC),
     location_off_days AS
  (SELECT 'KSA AWJ Warehouse' AS LOCATION,
          'Fri' AS off_day
   UNION SELECT 'Shobak-CPP' AS LOCATION,
          'Fri' AS off_day
   UNION SELECT 'Shobak Warehouse' AS LOCATION,
          'Fri' AS off_day
   UNION SELECT 'KUW CK1' AS LOCATION,
          'Mon' AS off_day
   UNION SELECT 'BAH CK' AS LOCATION,
          'Wed' AS off_day
   UNION SELECT 'KSA-CK2' AS LOCATION,
          'Thu' AS off_day
   UNION SELECT 'QAR-CK1' AS LOCATION,
          'Fri' AS off_day
     UNION SELECT 'Kava and Chai American University of Sharjah' AS LOCATION,
                'Fri' AS off_day
  UNION SELECT 'Kava and Chai American University of Sharjah' AS LOCATION,
                'Sat' AS off_day
  UNION SELECT 'Kava and Chai American University of Sharjah' AS LOCATION,
                'Sun' AS off_day
  UNION SELECT 'Kava and Chai CE Kiosk Sharjah' AS LOCATION,
                'Sat' AS off_day
   UNION SELECT 'Kava and Chai CE Kiosk Sharjah' AS LOCATION,
                'Sun' AS off_day
   UNION SELECT 'KUW Warehouse' AS LOCATION,
                'Fri' AS off_day
   UNION SELECT 'Bahrain Warehouse' AS LOCATION,
                'Fri' AS off_day
   UNION SELECT 'Riyadh Warehouse' AS LOCATION,
                'Fri' AS off_day
   UNION SELECT 'KSA Nakheel CK' AS LOCATION,
                'Fri' AS off_day
   UNION SELECT 'Gogreek Ripemarket' AS LOCATION,
                'Mon' AS off_day
    UNION SELECT 'Gogreek Ripemarket' AS LOCATION,
                'Tue' AS off_day
    UNION SELECT 'Gogreek Ripemarket' AS LOCATION,
                'Wed' AS off_day
    UNION SELECT 'Gogreek Ripemarket' AS LOCATION,
                'Thu' AS off_day
    UNION SELECT 'Gogreek Ripemarket' AS LOCATION,
                'Fri' AS off_day
   UNION SELECT 'Calipoke Ripemarket' AS LOCATION,
                'Mon' AS off_day
    UNION SELECT 'Calipoke Ripemarket' AS LOCATION,
                'Tue' AS off_day
    UNION SELECT 'Calipoke Ripemarket' AS LOCATION,
                'Wed' AS off_day
    UNION SELECT 'Calipoke Ripemarket' AS LOCATION,
                'Thu' AS off_day
    UNION SELECT 'Calipoke Ripemarket' AS LOCATION,
                'Fri' AS off_day),
     td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'kitopi-pegasus'),
     base AS
  (SELECT "Organization",
   "Date",
   to_char("Date", 'Dy') as "Reminded Day",
   location_map.country AS "Country",
                      location_map.team AS "Team",
   location_map.cluster as "Cluster",
   "Location",
   split_part("Routine Name", ' - ', 1) AS "Routine Name",
   "Routine KNID",
  row_number() OVER (PARTITION BY ("Reminded At")::date,
                                                      split_part("Routine Name", ' - ', 1),
                                                     "Location"
                                         ORDER BY "Reminded At") AS "Routine #",
   "Reminded At",
   "Responded At",
   "Compliance",
   "Submission KNID"
   FROM form_compliance_v2 fc
   JOIN location_acl ON fc."Location" = location_acl.job_location
    JOIN location_map ON fc."Location" = location_map.job_location
     WHERE fc."Organization" ='kitopi-pegasus'
     AND "Reminded At" BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP
   ORDER BY "Organization",
            split_part("Routine Name", ' - ', 1),
           "Location", "Reminded At", "Responded At")
SELECT base.*
FROM base
LEFT OUTER JOIN location_off_days lod ON base."Location" = lod.location
AND base."Reminded Day" = lod.off_day
WHERE lod.location IS NULL
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10,
         11,
         12, 13, 14
		 ORDER by 1, 4, 5, 6, 7, 2, 11, 8
```

---

## Kitopi Follow up Tasks Summary_Follow Ups.sql

**Tables referenced:** kitopi.follow_up_tasks_summary, location_acl, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Kitopi Follow up Tasks Summary
-- Dashboard: Follow Ups
-- Category: Kitopi
-- Extracted: 2026-01-29 16:52:35
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'HQ',
                              'Head Office',
                              'All')
     AND job_location NOT ILIKE 'Head Office%'
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
                  WHERE ug2.user_id = @{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE)))
			   select distinct on(fu."Task KNID")*
			   from kitopi.follow_up_tasks_summary fu
			   JOIN location_acl on fu."Location" = location_acl.job_location
			   where fu."Audit Date" between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
```

---

## Kitopi Forms Submissions New_Form Submissions.sql

**Tables referenced:** RAW, final_definition, form_responses, form_submissions, forms, fr, fr_location, fs, jsonb_Each, jsonb_each, metadata, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Kitopi Forms Submissions New
-- Dashboard: Form Submissions
-- Category: Kitopi
-- Extracted: 2026-01-29 16:55:04
-- ============================================================

WITH /*location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'kitopi-pegasus'
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'All')
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
                  WHERE ug2.user_id = @{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
     location_map AS
  (SELECT DISTINCT ON (job_location) job_location,
                      division AS country,
                      sub_division AS team,
                      designation AS CLUSTER
   FROM user_details
   WHERE is_active = 'true'
     AND organization = 'kitopi-pegasus'
     AND job_type IN ('CK',
                      'SK',
                      'Kitchen',
                      'Warehouse')
   ORDER BY job_location,
            created_at ASC),*/
     td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'kitopi-pegasus'),
     forms AS
  (SELECT id AS form_knid,
          split_part(regexp_replace(title, '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', ''), ' - ', 1) AS form_name,
          organization
   FROM nuggets
   WHERE  split_part(regexp_replace(title, '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', ''), ' - ', 1) in (@{{:Form Title}})
   AND organization = 'kitopi-pegasus'
     AND (is_deleted = 'false'
          OR is_deleted IS NULL)
     AND classification_type = 'form'),
     fs AS
  (SELECT DISTINCT ON (response_id) fs2.*,
                      form_name
   FROM form_submissions fs2
   JOIN forms ON forms.form_knid = fs2.form_id
   JOIN td ON fs2.organization = td.organization
   WHERE submit_date + td.diff BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + interval '1 day'
   ORDER BY response_id,
            fs2.id),
			fr_location AS
  (SELECT DISTINCT ON (fs.response_id) fs.response_id,
                      fr.response->>'name' AS fr_location
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   JOIN question_definitions qd ON fr.question_id = qd.question_id
   AND fs.form_id = qd.nugget_id
   WHERE qd.question_type = 'location'
   and  fr.response->>'name' in (@{{:Location}})
   ORDER BY fs.response_id,
            fs.id,
            qd.section_id,
            qd.sqno::numeric),
     metadata AS
  (SELECT fs.id,
   fs.response_Id,
          fs.form_id,
   fs.form_name,
   fs.sno,
   fs.submit_date,
          fs.organization,
          fs.user_id,
          COALESCE(fr_location.fr_location, fs.location) AS LOCATION
   FROM fs
   LEFT OUTER JOIN fr_location ON fs.response_id = fr_location.response_id
where COALESCE(fr_location.fr_location, fs.location) in (@{{:Location}}) ),
     qd_non_table_non_logic AS
  (SELECT organization,
          nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          CASE
              WHEN qd.question_type = 'section' THEN 0
              ELSE sqno::integer*10000
          END AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          question_id AS qid,
          question_type AS q_type,
          question AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   WHERE question_type NOT IN ('table')),
     qdntwl_prework AS
  (SELECT *,
          jsonb_array_elements(definition -> 'logic') -> 'questions' q
   FROM forms
   JOIN question_definitions qd ON qd.nugget_id = forms.form_knid
   WHERE qd.definition -> 'logic' IS NOT NULL),
     qd_non_table_with_logic AS
  (SELECT organization,
          nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::integer*10000+(def.value->>'order')::integer AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          def.key AS qid,
          def.value->>'question_type' AS q_type,
                      def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
     qd_table AS
  (SELECT organization,
          nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::integer*10000+(def.value->>'order')::integer AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          def.key AS qid,
          def.value->>'question_type' AS q_type,
                      def.value->>'question' AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   CROSS JOIN jsonb_each(definition -> 'questions') def
   WHERE qd.question_type IN ('table')),
     final_definition AS
  (SELECT *
   FROM qd_non_table_non_logic
   UNION SELECT *
   FROM qd_non_table_with_logic
   UNION SELECT *
   FROM qd_table
   ORDER BY 1,
            2,
            3,
            5 DESC, 7 DESC),
     fr AS
  (SELECT form_submit_id,
          form_id,
          form_name,
          sno,
          submit_date,
          user_id,
          response_id,
          question_id AS parent_qid,
          question_id AS qid,
          question_type,
          response,
          1 AS rn
   FROM form_responses fr
    JOIN metadata ON metadata.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                form_name,
                sno,
                submit_date,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                question_type,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             form_id,
             form_name,
             sno,
             submit_date,
             user_id,
             response_id,
             question_id,
             question_type,
             base.value,
             base.ordinality AS rn
      FROM form_responses fr
      JOIN metadata ON metadata.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
     
     RAW AS
  (SELECT form_name AS "Form Title",
          fr.submit_date + td.diff AS "Submitted At",
          fr.sno AS "Submission No",
          fd.section_no AS "Section No",
          fd.q_no AS "Question No",
          fd.parent_question AS "Parent Question",
          fd.question AS "Question",
          fd.q_type AS "Question Type",
          rn AS "Row Number",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'linear_scale',
                                 'audit') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('checkboxes') THEN array_to_string(ARRAY
                                                                      (SELECT jsonb_array_elements_text(fr.response->'selected')
                                                                       UNION SELECT CASE
                                                                                        WHEN fr.response->>'otherText' IS NOT NULL THEN fr.response->>'otherText'
                                                                                        ELSE NULL
                                                                                    END), ', ')
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) + td.diff, 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed',
                                 'upload_image',
                                 'upload_video') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS "Response",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS "Section Response",
          fd.form_knid AS "Form KNID",
          fr.response_id AS "Response KNID"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   JOIN td ON fd.organization = td.organization
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13
   ORDER BY 1,
            2,
            3)
SELECT metadata.location AS "Form Location",
       raw.*,
	   case when raw."Question Type" ilike '%text%' and raw."Response" ~ '^[+-]?[0-9]*\.?[0-9]+$' then raw."Response"::numeric else null end as "Num Response",
       ud.identifier AS "Submitter ID",
       ud.uuid AS "Submitter KNID",
       ud.first_name||' '||ud.last_name AS "Submitter Name",
       ud.division AS "Submitter Division",
       ud.sub_division AS "Submitter Sub Division",
       ud.job_location AS "Submitter Location",
       ud.department AS "Submitter Department",
       ud.designation AS "Submitter Designation",
       ud.job_type AS "Submitter Job Type"
FROM RAW
JOIN metadata ON raw."Response KNID" = metadata.response_id
AND raw."Form KNID"= metadata.form_id
LEFT OUTER JOIN user_details ud ON metadata.user_id = ud.uuid
WHERE raw."Question Type" IN ('dropdown',
                              'multiple_choice',
                              'linear_scale',
                              'audit')
or (raw."Question Type" ilike '%text%' and raw."Response" ~ '^[+-]?[0-9]*\.?[0-9]+$')
ORDER BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9
```

---

## Kitopi Forms Submissions_Forms.sql

**Tables referenced:** form_responses, form_submissions, forms, fr, fr_location, fs, location_acl, location_map, nuggets, organizations, question_definitions, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Kitopi Forms Submissions
-- Dashboard: Forms
-- Category: Kitopi
-- Extracted: 2026-01-29 16:58:28
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
   and is_active = 'true'
   and job_location not in ('KNOW', 'All')
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
			    location_map AS
  (SELECT DISTINCT ON (job_location) job_location,
                      division AS country,
                      sub_division AS team,
   designation as cluster
   FROM user_details
   WHERE is_active = 'true'
     AND organization = 'kitopi-pegasus'
     AND job_type IN ('CK',
                      'SK',
                      'Kitchen',
                      'Warehouse')
   ORDER BY job_location,
            created_at ASC),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = @{{:OrganizationParameter}}),
			   forms as (select id, split_part(title, ' - ', 1) as title from nuggets where organization = @{{:OrganizationParameter}}
						 and (is_deleted = 'false' or is_deleted is null)
						 and classification_type = 'form'
						and title not ilike 'Issue Creation%'
						and title not ilike 'Issue Closure%'
						and id not ilike 'compliment%'
						and id not ilike 'leave%'),
						fs AS
  (SELECT DISTINCT ON (response_id) fs2.*
   FROM form_submissions fs2
   JOIN forms ON forms.id = fs2.form_id
   JOIN td ON fs2.organization = td.organization
   WHERE submit_date + td.diff between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
   ORDER BY response_id,
            fs2.id),
     fr_location AS
  (SELECT DISTINCT ON (fs.response_id) fs.response_id,
                      fr.response->>'name' AS fr_location
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   JOIN question_definitions qd ON fr.question_id = qd.question_id
   AND fs.form_id = qd.nugget_id
   WHERE qd.question_type = 'location'
   ORDER BY fs.response_id,
            fs.id,
            qd.section_id,
            qd.sqno),
     fr AS
  (SELECT fs.response_Id,
          fs.form_id,
          fs.id,
          fs.sno,
          fs.submit_date,
          fs.organization,
          fs.user_id,
          CASE
              WHEN fr_location.fr_location IS NULL THEN fs.location
              ELSE fr_location.fr_location
          END AS LOCATION
   FROM fs
   LEFT OUTER JOIN fr_location ON fs.response_id = fr_location.response_id)
SELECT forms.title AS "Form Title",
       forms.id AS "Form KNID",
       fr.response_id AS "Response KNID",
       fr.sno AS "Submission No",
       fr.submit_date + td.diff AS "Submitted At",
       fr.location AS "Form Location",
	   location_map.country as "Country",
	   location_map.team as "Team",
	   location_map.cluster as "Cluster",
       ud.identifier AS "Submitter ID",
       ud.uuid AS "Submitter KNID",
       ud.first_name||' '||ud.last_name AS "Submitter Name",
       ud.division AS "Submitter Division",
       ud.sub_division AS "Submitter Sub Division",
       ud.job_location AS "Submitter Location",
       ud.department AS "Submitter Department",
       ud.designation AS "Submitter Designation",
       ud.job_type AS "Submitter Job Type"
FROM location_acl la
join location_map on la.job_location = location_map.job_location
LEFT OUTER JOIN fr ON fr.location = la.job_location
LEFT OUTER JOIN forms ON fr.form_id = forms.id
LEFT OUTER JOIN td ON fr.organization = td.organization
LEFT OUTER JOIN user_details ud ON fr.user_id = ud.uuid
group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18
having fr.submit_date + td.diff is not null
ORDER BY 1, 7, 8, 9,
         6,
         5
```

---

## Kitopi MDA Audits_MDA.sql

**Tables referenced:** LOCATION, base, brand, joy, summary

**Columns needing snake_case conversion:**

- `auditMaxScore` -> `audit_max_score` (alias: `audit_max_score AS "auditMaxScore"`)

- `auditScore` -> `audit_score` (alias: `audit_score AS "auditScore"`)

- `auditStatus` -> `audit_status` (alias: `audit_status AS "auditStatus"`)

- `formAuditResults` -> `form_audit_results` (alias: `form_audit_results AS "formAuditResults"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `groupId` -> `group_id` (alias: `group_id AS "groupId"`)

- `groupTitle` -> `group_title` (alias: `group_title AS "groupTitle"`)

- `groupType` -> `group_type` (alias: `group_type AS "groupType"`)

- `isCritical` -> `is_critical` (alias: `is_critical AS "isCritical"`)

- `maxScore` -> `max_score` (alias: `max_score AS "maxScore"`)

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `questionIdRef` -> `question_id_ref` (alias: `question_id_ref AS "questionIdRef"`)

- `questionTitle` -> `question_title` (alias: `question_title AS "questionTitle"`)

- `questionType` -> `question_type` (alias: `question_type AS "questionType"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)

- `rowIdx` -> `row_idx` (alias: `row_idx AS "rowIdx"`)

- `startedAt` -> `started_at` (alias: `started_at AS "startedAt"`)

- `submissionsRefId` -> `submissions_ref_id` (alias: `submissions_ref_id AS "submissionsRefId"`)

- `submittedAt` -> `submitted_at` (alias: `submitted_at AS "submittedAt"`)


**Original Query:**

```sql
-- Data Source: Kitopi MDA Audits
-- Dashboard: MDA
-- Category: Kitopi
-- Extracted: 2026-01-29 16:53:01
-- ============================================================

WITH base AS (
  SELECT
    fn.organization AS `Organization`,
    fs.formId AS `Audit KNID`,
    CASE
      WHEN fn.title LIKE '% - (INTL|UAE)' THEN REGEXP_REPLACE(fn.title, '(?i)( - (INTL|UAE)).*$', '')
      WHEN fn.title LIKE '%-2024)' THEN REGEXP_REPLACE(fn.title, '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '')
      ELSE fn.title
    END AS `Audit`,
    fs.responseId AS `Audit Report KNID`,
    fs.sno AS `Audit Report No`,
    TIMESTAMP_ADD(fs.startedAt, INTERVAL 4 HOUR) AS `Started At`,
    TIMESTAMP_ADD(fs.submittedAt, INTERVAL 4 HOUR) AS `Submitted At`,
    CAST(fq.seq AS NUMERIC) AS `Seq`,
    fq.groupId AS `Group KNID`,
    fq.groupTitle AS `Group`,
    fq.groupType AS `Group Type`,
    fq.questionId AS `Checkpoint KNID`,
    fq.questionTitle AS `Checkpoint`,
    fq.questionType AS `Checkpoint Type`,
    JSON_EXTRACT_SCALAR(fq.details, '$.description') AS `Checkpoint Description`,
    JSON_EXTRACT_SCALAR(fq.details, '$.isCritical') AS `Criticality`,
    fr.rowIdx + 1 AS `Row No`,
    CASE
      WHEN fq.questionType IN ('dropdown','multiple_choice','linear_scale','audit')
        AND CAST(JSON_EXTRACT_SCALAR(fr.response.selected, '$.0') AS STRING) IS NOT NULL
        AND CAST(JSON_EXTRACT_SCALAR(fr.response.selected, '$.0') AS STRING) != ''
        THEN CAST(JSON_EXTRACT_SCALAR(fr.response.selected, '$.0') AS STRING)

      WHEN fq.questionType IN ('dropdown','multiple_choice','linear_scale','audit')
        THEN CAST(JSON_EXTRACT_SCALAR(fr.response, '$.otherText') AS STRING)

      WHEN fq.questionType IN ('long_text_field','single_text_field','qr_code','formula')
        THEN CAST(JSON_EXTRACT_SCALAR(fr.response, '$.0') AS STRING)

      WHEN fq.questionType IN ('signature','location')
        THEN CAST(JSON_EXTRACT_SCALAR(fr.response, '$.name') AS STRING)

      ELSE CAST(JSON_EXTRACT_SCALAR(fr.response, '$.0') AS STRING)
    END AS `Result`,

    JSON_EXTRACT_SCALAR(fr.response, '$.remarks') AS `Auditor Observations`,
    JSON_EXTRACT_SCALAR(fr.response, '$.images[0].response') AS `Evidence Image`,

    CASE
      WHEN JSON_EXTRACT_SCALAR(fr.response, '$.score') = '' THEN NULL
      ELSE CAST(JSON_EXTRACT_SCALAR(fr.response, '$.maxScore') AS FLOAT64)
    END AS `Max Score`,

    CASE
      WHEN JSON_EXTRACT_SCALAR(fr.response, '$.score') = '' THEN NULL
      ELSE CAST(JSON_EXTRACT_SCALAR(fr.response, '$.score') AS FLOAT64)
    END AS `Actual Score`,

    CASE
      WHEN JSON_EXTRACT_SCALAR(fr.response, '$.score') = '' THEN NULL
      WHEN CAST(JSON_EXTRACT_SCALAR(fr.response, '$.score') AS FLOAT64)
           < CAST(JSON_EXTRACT_SCALAR(fr.response, '$.maxScore') AS FLOAT64)
        THEN 1
      ELSE 0
    END AS `NC_Count`,
    CASE
      WHEN fq.questionType IN ('dropdown','multiple_choice','linear_scale','audit')
      THEN SAFE_CAST(
        JSON_EXTRACT_SCALAR(
          SAFE.PARSE_JSON(
            public.get_question_level_tasks_info(
              TO_JSON_STRING(fr.response),
              fq.questionType
            )
          ),
          '$.total_number_of_followup_tasks'
        ) AS INT64
      )
      ELSE NULL
    END AS `Total Follow Up Tasks`,

    CASE
      WHEN fq.questionType IN ('dropdown','multiple_choice','linear_scale','audit')
      THEN SAFE_CAST(
        JSON_EXTRACT_SCALAR(
          SAFE.PARSE_JSON(
            public.get_question_level_tasks_info(
              TO_JSON_STRING(fr.response),
              fq.questionType
            )
          ),
          '$.number_of_open_tasks'
        ) AS INT64
      )
      ELSE NULL
    END AS `Open Follow Up Tasks`,

    CASE
      WHEN fq.questionType IN ('dropdown','multiple_choice','linear_scale','audit')
      THEN
        SAFE_CAST(
          JSON_EXTRACT_SCALAR(
            SAFE.PARSE_JSON(
              public.get_question_level_tasks_info(
                TO_JSON_STRING(fr.response),
                fq.questionType
              )
            ),
            '$.total_number_of_followup_tasks'
          ) AS INT64
        )
        -
        SAFE_CAST(
          JSON_EXTRACT_SCALAR(
            SAFE.PARSE_JSON(
              public.get_question_level_tasks_info(
                TO_JSON_STRING(fr.response),
                fq.questionType
              )
            ),
            '$.number_of_open_tasks'
          ) AS INT64
        )
      ELSE NULL
    END AS `Closed Follow Up Tasks`

  FROM `.public.form_responses` fr
  JOIN `.public.form_submissions` fs ON fr.submissionsRefId = fs.id
  JOIN `.public.form_questions` fq ON fr.questionIdRef = fq.id
  JOIN `.public.form_nuggets` fn ON fs.formId = fn.id

  WHERE
    (fn.title LIKE 'A.5 Mystery%' OR fn.title LIKE 'A.6 Mystery%')
    AND TIMESTAMP_ADD(fs.submittedAt, INTERVAL 4 HOUR)
        BETWEEN TIMESTAMP_ADD(CAST(@{{:Date Range.START}} AS TIMESTAMP), INTERVAL 4 HOUR)
            AND TIMESTAMP_ADD(CAST(@{{:Date Range.END}} AS TIMESTAMP), INTERVAL 28 HOUR)
    AND TIMESTAMP_ADD(fr.submittedAt, INTERVAL 4 HOUR)
        BETWEEN TIMESTAMP_ADD(CAST(@{{:Date Range.START}} AS TIMESTAMP), INTERVAL 4 HOUR)
            AND TIMESTAMP_ADD(CAST(@{{:Date Range.END}} AS TIMESTAMP), INTERVAL 28 HOUR)
    AND fq.questionType NOT IN ('nested','section')

  GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26
),

summary AS (
  SELECT
    fr.responseId AS `Audit Report KNID`,
    CAST(MAX(JSON_VALUE(response.auditScore)) AS FLOAT64)
      / CAST(MAX(JSON_VALUE(response.auditMaxScore)) AS FLOAT64) AS `Audit Score`,
    INITCAP(MAX(JSON_VALUE(response.auditStatus))) AS `Audit Status`
  FROM `.public.form_responses` fr
  WHERE fr.questionId = 'formAuditResults'
    AND TIMESTAMP_ADD(fr.submittedAt, INTERVAL 4 HOUR)
        BETWEEN TIMESTAMP_ADD(CAST(@{{:Date Range.START}} AS TIMESTAMP), INTERVAL 4 HOUR)
            AND TIMESTAMP_ADD(CAST(@{{:Date Range.END}} AS TIMESTAMP), INTERVAL 28 HOUR)
    AND fr.responseId IN (SELECT `Audit Report KNID` FROM base)
  GROUP BY 1
),

LOCATION AS (
  SELECT
    `Audit Report KNID`,
    MAX(`Result`) AS `Location`
  FROM base
  WHERE `Checkpoint Type` = 'location'
    AND `Seq` < 200
  GROUP BY 1
),

brand AS (
  SELECT
    `Audit Report KNID`,
    MAX(
      CASE
        WHEN `Checkpoint` LIKE 'Brand%' OR `Checkpoint` LIKE 'Restaurant Name%'
        THEN `Result`
      END
    ) AS `Brand`
  FROM base
  GROUP BY 1
),

joy AS (
  SELECT
    `Audit Report KNID`,
    COUNT(DISTINCT CASE WHEN `Checkpoint Type` = 'dropdown' THEN `Checkpoint KNID` END)
      AS `Joy Points Checked`,
    SUM(CASE WHEN `Result` = 'Yes' THEN 1 ELSE 0 END)
      AS `Joy Points Compliant`,
    MAX(CASE WHEN `Checkpoint Type` = 'linear_scale' THEN CAST(`Result` AS FLOAT64) END)
      AS `Joy Rating`
  FROM base
  WHERE `Group` LIKE 'JOY%'
  GROUP BY 1
)

SELECT
  location.`Location`,
  brand.`Brand`,
  summary.`Audit Score`,
  summary.`Audit Status`,
  base.*,
  joy.`Joy Points Checked`,
  joy.`Joy Points Compliant`,
  joy.`Joy Points Compliant` / joy.`Joy Points Checked` AS `Joy Compliance`,
  joy.`Joy Rating`
FROM base
LEFT JOIN summary  ON base.`Audit Report KNID` = summary.`Audit Report KNID`
LEFT JOIN joy      ON base.`Audit Report KNID` = joy.`Audit Report KNID`
LEFT JOIN brand    ON base.`Audit Report KNID` = brand.`Audit Report KNID`
LEFT JOIN LOCATION ON base.`Audit Report KNID` = location.`Audit Report KNID`
ORDER BY 6,1,2,8,12,13
```

---

## Kitopi MDA Follow up Tasks Summary_MDA.sql

**Tables referenced:** checkpoint_master_sheet_table, cms, cmscp, forms, fu, nuggets, organizations, question_definitions, t, tasks, td, tfq, user_details

**Columns needing snake_case conversion:**

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `formDetails` -> `form_details` (alias: `form_details AS "formDetails"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)


**Original Query:**

```sql
-- Data Source: Kitopi MDA Follow up Tasks Summary
-- Dashboard: MDA
-- Category: Kitopi
-- Extracted: 2026-01-29 16:54:41
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'kitopi-pegasus'),
     forms AS
  (SELECT audit_main_theme,
          audit_submission_knid
   FROM checkpoint_master_sheet_table cms
   JOIN td ON cms.organization_id = td.organization
   WHERE audit_type = 'MDA'
     AND audit_submitted_at + td.diff BETWEEN@{{:Kitopi MDA Audits.Date Range.START}}::timestamp AND @{{:Kitopi MDA Audits.Date Range.END}}::timestamp
     AND cms.organization_id = 'kitopi-pegasus'
   GROUP BY 1,
            2),
     t AS
  (SELECT t.id AS "Task KNID",
          t.organization AS "Org",
          t.ext_id AS "Task ID",
          t.title AS "Task",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Closed'
              WHEN t.status ILIKE 'notStarted'
                   AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 'Overdue'
              WHEN t.status ILIKE 'notStarted'
                   AND to_timestamp(t.deadline/1000) >= CURRENT_TIMESTAMP THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened') THEN 'In Progress'
          END AS "Status",
          CASE
              WHEN t.details->'formDetails'->>'name' ~* ' - (INTL|UAE)' THEN regexp_replace(t.details->'formDetails'->>'name', '(?i)( - (INTL|UAE)).*$', '')
              WHEN t.details->'formDetails'->>'name' ~ '\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$' THEN regexp_replace(t.details->'formDetails'->>'name', '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '')
              ELSE t.details->'formDetails'->>'name'
          END AS "Trigger Form",
          t.details->'formDetails'->>'formId' AS "Trigger Form KNID",
                                     t.details->'formDetails'->>'responseId' AS "Trigger Form Submission KNID",
                                                                t.details->'formDetails'->>'sno' AS "Trigger Form Submission No",
                                                                                           initcap(t.details->>'authorName') AS "Assigned By",
                                                                                           initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                           initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                           initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                           to_timestamp(t.created_at/1000) + td.diff AS "Assigned At",
                                                                                           to_timestamp(t.deadline/1000) + td.diff AS "Deadline",
                                                                                           CASE
                                                                                               WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) + td.diff
                                                                                           END AS "Started At",
                                                                                           CASE
                                                                                               WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) + td.diff
                                                                                               ELSE NULL
                                                                                           END AS "Completed At",
                                                                                           CASE
                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                    OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) + td.diff
                                                                                               ELSE NULL
                                                                                           END AS "Reopened At",
                                                                                           CASE
                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                               ELSE 0
                                                                                           END AS "Overdue Count",
                                                                                           CASE
                                                                                               WHEN t.status ILIKE 'notStarted'
                                                                                                    AND to_timestamp(t.deadline/1000) >= CURRENT_TIMESTAMP THEN 1
                                                                                               ELSE 0
                                                                                           END AS "Not Started Count",
                                                                                           CASE
                                                                                               WHEN (t.status ILIKE 'started'
                                                                                                     OR t.status ILIKE 'reopened')
                                                                                                    AND to_timestamp(t.deadline/1000) >= CURRENT_TIMESTAMP THEN 1
                                                                                               ELSE 0
                                                                                           END AS "In Progress Count",
                                                                                           CASE
                                                                                               WHEN t.status ILIKE 'completed' THEN 1
                                                                                               ELSE 0
                                                                                           END AS "Completed Count",
                                                                                           CASE
                                                                                               WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                               ELSE 0
                                                                                           END AS "Reopened Count",
                                                                                           split_part(t.details->'formDetails'->>'path', '/', 1) AS theme_knid,
                                                                                           split_part(t.details->'formDetails'->>'path', '/', 2) AS checkpoint_knid
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   JOIN td ON t.organization = td.organization
   WHERE t.organization = 'kitopi-pegasus'
     AND t.is_deleted = 'false'
     AND t.details->'formDetails'->>'responseId' IN
       (SELECT audit_submission_knid
        FROM forms)),
     tfq AS
  (SELECT qd.nugget_id AS form_knid,
          qd.question_id AS theme_knid,
          qd.question AS theme,
          q.key AS checkpoint_knid,
          q.value->>'question' AS CHECKPOINT
   FROM question_definitions qd
   JOIN nuggets n ON qd.nugget_id = n.id,
                     LATERAL jsonb_each(qd.definition->'questions') AS q
   WHERE n.title IN
       (SELECT audit_main_theme
        FROM forms)
     AND qd.question_type = 'nested'),
     cms AS
  (SELECT store_id,
          cms.audit_submission_knid,
          audit_submitted_at
   FROM checkpoint_master_sheet_table cms
   JOIN forms ON cms.audit_submission_knid = forms.audit_submission_knid
   GROUP BY 1,
            2,
            3),
     fu AS
  (SELECT cms.store_id AS "Location",
          "Trigger Form",
          "Trigger Form Submission No",
          cms.audit_submitted_at + td.diff AS "Audit Date",
          tfq.theme AS "Theme",
          tfq.checkpoint AS "Checkpoint",
          "Status",
          "Assigned At",
          "Deadline",
          "Started At",
          "Completed At",
          "Reopened At",
          "Assigned By",
          "Started By",
          "Completed By",
          "Reopened By",
          "Overdue Count",
          "Not Started Count",
          "In Progress Count",
          "Completed Count",
          "Reopened Count",
          "Task KNID",
          "Org",
          "Task ID",
          "Task",
          "Trigger Form KNID",
          "Trigger Form Submission KNID",
          tfq.theme_knid AS "Theme KNID",
          tfq.checkpoint_knid AS "Checkpoint KNID"
   FROM t
   LEFT OUTER JOIN tfq ON t."Trigger Form KNID" = tfq.form_knid
   AND t.theme_knid = tfq.theme_knid
   AND t.checkpoint_knid = tfq.checkpoint_knid
   LEFT OUTER JOIN cms ON t."Trigger Form Submission KNID" = cms.audit_submission_knid
   JOIN td ON t."Org" = td.organization
   ORDER BY 10 DESC, 9 DESC, 1,
                             2,
                             3,
                             4,
                             5,
                             7,
                             8),
     cmscp AS
  (SELECT cms.audit_submission_knid,
          checkpoint_knid,
          RESULT,
          auditor_observations
   FROM checkpoint_master_sheet_table cms
   JOIN forms ON cms.audit_submission_knid = forms.audit_submission_knid)
SELECT fu."Location",
       fu."Trigger Form",
       fu."Trigger Form Submission No",
       fu."Audit Date",
       fu."Theme",
       fu."Checkpoint",
       cmscp.result AS "Result",
       cmscp.auditor_observations AS "Observation",
       fu."Status",
       fu."Assigned At",
       fu."Deadline",
       fu."Started At",
       fu."Completed At",
       fu."Reopened At",
       fu."Assigned By",
       fu."Started By",
       fu."Completed By",
       fu."Reopened By",
       fu."Overdue Count",
       fu."Not Started Count",
       fu."In Progress Count",
       fu."Completed Count",
       fu."Reopened Count",
       fu."Task KNID",
       fu."Org",
       fu."Task",
       fu."Trigger Form KNID",
       fu."Trigger Form Submission KNID",
       fu."Theme KNID",
       fu."Checkpoint KNID"
FROM fu
LEFT OUTER JOIN cmscp ON fu."Trigger Form Submission KNID" = cmscp.audit_submission_knid
AND fu."Checkpoint KNID" = cmscp.checkpoint_knid
ORDER BY 7 DESC,
         14 DESC,
         13 DESC,
         1,
         2,
         3,
         4,
         5,
         8,
         10
```

---

## Kitopi QIR Daily Email_QIR Daily Email.sql

**Tables referenced:** RAW, closure, closure_final_definition, closure_forms, closure_fr, closure_fs, closure_qd_non_table_non_logic, closure_qd_non_table_with_logic, closure_qd_table, closure_qdntwl_prework, closure_raw, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, qir, question_definitions, supplier, supplier_qd, supplier_type, supplier_type_qd, t, tasks, td, user_details

**Columns needing snake_case conversion:**

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `formDetails` -> `form_details` (alias: `form_details AS "formDetails"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `resolvedPayload` -> `resolved_payload` (alias: `resolved_payload AS "resolvedPayload"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)

- `userName` -> `user_name` (alias: `user_name AS "userName"`)


**Original Query:**

```sql
-- Data Source: Kitopi QIR Daily Email
-- Dashboard: QIR Daily Email
-- Category: Kitopi
-- Extracted: 2026-01-29 16:57:58
-- ============================================================

WITH td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'kitopi-pegasus'),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE (title ILIKE 'Quality Incident Reporting Form%' or id = '-O5bb7zJztQsIeiIHIkm')
     AND is_deleted = 'false'),
     supplier_qd AS
  (SELECT qd.nugget_id AS form_id,
          jsonb_object_keys((jsonb_array_elements(definition->'logic'))->'questions') qids
   FROM question_definitions qd
   JOIN forms qf ON qd.nugget_id = qf.form_knid
   WHERE qd.question = 'Item Supplied by'),
     supplier AS
  (SELECT DISTINCT ON (response_id) fs.response_id,
                      CASE
                          WHEN fr.response->>'name' IS NOT NULL THEN fr.response->>'name'
                          ELSE fr.response->>0
                      END AS "Item Supplied By"
   FROM form_responses fr
   JOIN form_submissions fs ON fr.form_submit_id = fs.id
   JOIN td ON fs.organization = td.organization
   WHERE fr.question_id IN
       (SELECT qids
        FROM supplier_qd)
     AND fs.submit_date + td.diff > current_date + td.diff - interval '60 days'
   ORDER BY response_id,
            fs.id DESC),
     supplier_type_qd AS
  (SELECT qd.nugget_id AS form_id,
          question_id AS qids
   FROM question_definitions qd
   JOIN forms qf ON qd.nugget_id = qf.form_knid
   WHERE qd.question = 'Item Supplied by'),
     supplier_type AS
  (SELECT DISTINCT ON (response_id) fs.response_id,
                      fr.response->'selected'->>0 AS "Supplier Type"
   FROM form_responses fr
   JOIN form_submissions fs ON fr.form_submit_id = fs.id
   JOIN td ON fs.organization = td.organization
   WHERE fr.question_id IN
       (SELECT qids
        FROM supplier_type_qd)
     AND fs.submit_date + td.diff > current_date + td.diff - interval '60 days'
   ORDER BY response_id,
            fs.id DESC),
     qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT nugget_id AS form_knid,
                                                                  CASE
                                                                      WHEN qd.section_id = 'section' THEN 1
                                                                      ELSE replace(section_id, 'section-', '')::integer
                                                                  END AS section_no,
                                                                  CASE
                                                                      WHEN qd.question_type = 'section' THEN 0
                                                                      ELSE sqno::integer*10000
                                                                  END AS q_no,
                                                                  section_id,
                                                                  question_id AS parent_qid,
                                                                  question_type AS parent_q_type,
                                                                  question_id AS qid,
                                                                  question_type AS q_type,
                                                                  question AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   WHERE question_type NOT IN ('table')),
     qdntwl_prework AS
  (SELECT *,
          jsonb_array_elements(definition -> 'logic') -> 'questions' q
   FROM forms
   JOIN question_definitions qd ON qd.nugget_id = forms.form_knid
   WHERE qd.definition -> 'logic' IS NOT NULL),
     qd_non_table_with_logic AS
  (/*Non Table type Questions in Forms with Logic - SqNo will be in between the parent SqNo for sub questions*/ SELECT nugget_id AS form_knid,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
     qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT nugget_id AS form_knid,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question_type AS parent_q_type,
                                                                                                        def.key AS qid,
                                                                                                        def.value->>'question_type' AS q_type,
                                                                                                                    def.value->>'question' AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   CROSS JOIN jsonb_each(definition -> 'questions') def
   WHERE qd.question_type IN ('table')),
     final_definition AS
  (SELECT *
   FROM qd_non_table_non_logic
   UNION SELECT *
   FROM qd_non_table_with_logic
   UNION SELECT *
   FROM qd_table
   ORDER BY 1,
            2,
            3,
            5 DESC, 7 DESC),
     fs AS
  (SELECT DISTINCT ON (response_id) *
   FROM forms
   JOIN form_submissions fs ON forms.form_knid = fs.form_id
   JOIN td ON td.organization = fs.organization
   WHERE submit_date + td.diff > current_date + td.diff - interval '60 days'
   ORDER BY response_id,
            id DESC),
     fr AS
  (SELECT *
   FROM form_responses fr
   JOIN fs ON fr.form_submit_id = fs.id),
     RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.question,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('checkboxes') THEN array_to_string(ARRAY
                                                                      (SELECT jsonb_array_elements_text(fr.response->'selected')), ', ')
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Dubai', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS response,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS section_response,
          form_name,
          fd.form_knid,
          fr.response_id
   FROM final_definition fd
   JOIN fr ON fr.question_id = fd.qid
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9
   ORDER BY 1,
            2,
            3), qir AS
  (SELECT response_id,
          max(CASE
                  WHEN section_no = 1 THEN section_response->'sender'->>'userName'
                  ELSE NULL
              END) AS "Reporting Kitchen",
          max(CASE
                  WHEN question ILIKE 'Country' THEN response
                  ELSE NULL
              END) AS "Country",
          max(CASE
                  WHEN question ILIKE 'Complaint Type' THEN response
                  ELSE NULL
              END) AS "Complaint Type",
          max(CASE
                  WHEN question ILIKE '%TASTE%' THEN response
                  ELSE NULL
              END) AS "Taste Issues",
          max(CASE
                  WHEN question ILIKE '%APPEARENCE%'
                       OR question ILIKE '%Appearance%' THEN response
                  ELSE NULL
              END) AS "Appearance Issues",
          max(CASE
                  WHEN question ILIKE '%Smell%' THEN response
                  ELSE NULL
              END) AS "Smell Issues",
          max(CASE
                  WHEN question ILIKE '%Texture%' THEN response
                  ELSE NULL
              END) AS "Texture Issues",
          max(CASE
                  WHEN question ILIKE '%Consistency%' THEN response
                  ELSE NULL
              END) AS "Consistency Issues",
          max(CASE
                  WHEN question ILIKE '%Other quality%' THEN response
                  ELSE NULL
              END) AS "Other Issues",
          max(CASE
                  WHEN question ILIKE '%Packaging Material%' THEN response
                  ELSE NULL
              END) AS "Packaging Issues",
          max(CASE
                  WHEN question ILIKE '%food safety%' THEN response
                  ELSE NULL
              END) AS "Food Safety Issues",
          max(CASE
                  WHEN question ILIKE 'Specify the issue%' THEN response
                  ELSE NULL
              END) AS "Issue Description",
          max(CASE
                  WHEN question ILIKE '%Brand%' THEN response
                  ELSE NULL
              END) AS "Brands",
          max(CASE
                  WHEN question ILIKE '%Transfer Order%' THEN response
                  ELSE NULL
              END) AS "TO / Inv No",
          max(CASE
                  WHEN question ILIKE '%ERP Code%' THEN response
                  ELSE NULL
              END) AS "ERP Code",
          max(CASE
                  WHEN question ILIKE '%Product Name%' THEN response
                  ELSE NULL
              END) AS "Product Name",
          max(CASE
                  WHEN question ILIKE 'Qty Delivered' THEN response
                  ELSE NULL
              END) AS "Delivered Qty",
          max(CASE
                  WHEN question ILIKE 'Qty Rejected%' THEN response
                  ELSE NULL
              END) AS "Rejected Qty"
   FROM RAW
   GROUP BY 1),
                t AS
  ( SELECT t.id AS "Task KNID",
           t.organization AS "Org",
           t.ext_id AS "Task ID",
           qir.*,
           supplier_type."Supplier Type",
           supplier."Item Supplied By",
           t.title AS "Task",
           CASE
               WHEN t.status ILIKE 'completed' THEN 'Completed'
               WHEN t.status ILIKE 'notStarted'
                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 'Overdue'
               WHEN t.status ILIKE 'notStarted'
                    AND to_timestamp(t.deadline/1000) >= CURRENT_TIMESTAMP THEN 'Not Started'
               WHEN (t.status ILIKE 'started'
                     OR t.status ILIKE 'reopened') THEN 'In Progress'
           END AS "Status",
           CASE
               WHEN t.details->'formDetails'->>'name' ~* ' - (INTL|UAE)' THEN regexp_replace(t.details->'formDetails'->>'name', '(?i)( - (INTL|UAE)).*$', '')
               WHEN t.details->'formDetails'->>'name' ~ '\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$' THEN regexp_replace(t.details->'formDetails'->>'name', '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '')
               ELSE t.details->'formDetails'->>'name'
           END AS "Trigger Form",
           t.details->'formDetails'->>'formId' AS "Trigger Form KNID",
                                      t.details->'formDetails'->>'responseId' AS "Trigger Form Submission KNID",
                                                                 t.details->'formDetails'->>'sno' AS "Trigger Form Submission No",
                                                                                            initcap(t.details->>'authorName') AS "Assigned By",
                                                                                            initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                            initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                            initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                            to_timestamp(t.created_at/1000) + td.diff AS "Assigned At",
                                                                                            to_timestamp(t.deadline/1000) + td.diff AS "Deadline",
                                                                                            CASE
                                                                                                WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) + td.diff
                                                                                            END AS "Started At",
                                                                                            CASE
                                                                                                WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) + td.diff
                                                                                                ELSE NULL
                                                                                            END AS "Completed At",
                                                                                            CASE
                                                                                                WHEN t.status ILIKE 'completed'
                                                                                                     OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) + td.diff
                                                                                                ELSE NULL
                                                                                            END AS "Reopened At",
                                                                                            CASE
                                                                                                WHEN t.status NOT ILIKE 'completed'
                                                                                                     AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                ELSE 0
                                                                                            END AS "Overdue Count",
                                                                                            CASE
                                                                                                WHEN t.status ILIKE 'notStarted'
                                                                                                     AND to_timestamp(t.deadline/1000) >= CURRENT_TIMESTAMP THEN 1
                                                                                                ELSE 0
                                                                                            END AS "Not Started Count",
                                                                                            CASE
                                                                                                WHEN (t.status ILIKE 'started'
                                                                                                      OR t.status ILIKE 'reopened')
                                                                                                     AND to_timestamp(t.deadline/1000) >= CURRENT_TIMESTAMP THEN 1
                                                                                                ELSE 0
                                                                                            END AS "In Progress Count",
                                                                                            CASE
                                                                                                WHEN t.status ILIKE 'completed' THEN 1
                                                                                                ELSE 0
                                                                                            END AS "Completed Count",
                                                                                            CASE
                                                                                                WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                                ELSE 0
                                                                                            END AS "Reopened Count",
                                                                                            t.details->>'comment' AS "Completion Comment",
                                                                                                        t.details->'resolvedPayload'->'images'->0->>'url' AS "Completion Image"
   FROM tasks t
   JOIN forms ON t.details->'formDetails'->>'formId' = forms.form_knid
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   LEFT OUTER JOIN supplier ON t.details->'formDetails'->>'responseId' = supplier.response_id
   LEFT OUTER JOIN supplier_type ON t.details->'formDetails'->>'responseId' = supplier_type.response_id
   LEFT OUTER JOIN qir ON t.details->'formDetails'->>'responseId' = qir.response_id
   JOIN td ON t.organization = td.organization
   WHERE t.organization = 'kitopi-pegasus'
     AND t.is_deleted = 'false'
     AND t.details->'formDetails'->>'formId' IS NOT NULL
     AND to_timestamp(t.created_at/1000) + td.diff > current_date + td.diff - interval '60 days'),
                closure_forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ILIKE 'Quality incident report NCR%'),
                closure_qd_non_table_non_logic AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          CASE
              WHEN qd.question_type = 'section' THEN 0
              ELSE sqno::integer*10000
          END AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          question_id AS qid,
          question_type AS q_type,
          question AS question
   FROM closure_forms
   JOIN question_definitions qd ON closure_forms.form_knid = qd.nugget_id
   WHERE question_type NOT IN ('table')),
                closure_qdntwl_prework AS
  (SELECT *,
          jsonb_array_elements(definition -> 'logic') -> 'questions' q
   FROM closure_forms
   JOIN question_definitions qd ON qd.nugget_id = closure_forms.form_knid
   WHERE qd.definition -> 'logic' IS NOT NULL),
                closure_qd_non_table_with_logic AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::integer*10000+(def.value->>'order')::integer AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          def.key AS qid,
          def.value->>'question_type' AS q_type,
                      def.value->>'question' AS question
   FROM closure_qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
                closure_qd_table AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::integer*10000+(def.value->>'order')::integer AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          def.key AS qid,
          def.value->>'question_type' AS q_type,
                      def.value->>'question' AS question
   FROM closure_forms
   JOIN question_definitions qd ON closure_forms.form_knid = qd.nugget_id
   CROSS JOIN jsonb_each(definition -> 'questions') def
   WHERE qd.question_type IN ('table')),
                closure_final_definition AS
  (SELECT *
   FROM closure_qd_non_table_non_logic
   UNION SELECT *
   FROM closure_qd_non_table_with_logic
   UNION SELECT *
   FROM closure_qd_table
   ORDER BY 1,
            2,
            3,
            5 DESC, 7 DESC),
                closure_fs AS
  (SELECT DISTINCT ON (parent_nugget_id) form_submissions.*,
                      form_name
   FROM closure_forms
   JOIN form_submissions ON closure_forms.form_knid = form_submissions.form_id
   WHERE parent_nugget_id IN
       (SELECT "Task KNID"
        FROM t)
   ORDER BY parent_nugget_id,
            id DESC),
                closure_fr AS
  (SELECT form_submit_id,
          form_id,
          form_name,
          sno,
          submit_date,
          user_id,
          response_id,
          parent_nugget_id AS task_id,
          question_id AS parent_qid,
          question_id AS qid,
          question_type,
          response,
          1 AS rn
   FROM form_responses fr
   JOIN closure_fs ON closure_fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                form_name,
                sno,
                submit_date,
                user_id,
                response_id,
                parent_nugget_id AS task_id,
                question_id AS parent_qid,
                res.key AS qid,
                question_type,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             form_id,
             form_name,
             sno,
             submit_date,
             user_id,
             response_id,
             parent_nugget_id,
             question_id,
             question_type,
             base.value,
             base.ordinality AS rn
      FROM form_responses fr
      JOIN closure_fs ON closure_fs.id = fr.form_submit_id,
                         jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
                closure_raw AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.parent_question,
          fd.question,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'linear_scale',
                                 'audit') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('checkboxes') THEN array_to_string(ARRAY
                                                                      (SELECT jsonb_array_elements_text(fr.response->'selected')
                                                                       UNION SELECT CASE
                                                                                        WHEN fr.response->>'otherText' IS NOT NULL THEN fr.response->>'otherText'
                                                                                        ELSE NULL
                                                                                    END), ', ')
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000), 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('user') THEN fr.response::text
              WHEN fd.q_type IN ('upload_mixed',
                                 'upload_image',
                                 'upload_video') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location',
                                 'division',
                                 'sub_division') THEN fr.response ->> 'name'
              ELSE NULL
          END AS response,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS section_response,
          rn,
          form_name,
          fd.form_knid,
          fr.response_id,
          fr.task_id,
          fr.submit_date AS submit_date
   FROM closure_final_definition fd
   JOIN closure_fr fr ON fr.qid = fd.qid
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13
   ORDER BY 1,
            2,
            3),
                closure AS
  ( SELECT task_id,
           response_id AS "Closure Response KNID",
           sno AS "Closure Response No",
           max(CASE
                   WHEN question = 'Investigation Completed ( select Yes / No)' THEN response
                   ELSE NULL
               END) AS "Investigation Completed?",
           max(CASE
                   WHEN question = 'Was rejected product returned in 24 hours ? (Yes./No)' THEN response
                   ELSE NULL
               END) AS "Was rejected product returned in 24 hours?",
           max(CASE
                   WHEN question = 'Investigation Completion Time and Date' THEN response
                   ELSE NULL
               END) AS "Investigation Completion Time and Date",
           max(CASE
                   WHEN question = 'Investigation Outcome' THEN response
                   ELSE NULL
               END) AS "Investigation Outcome",
           max(CASE
                   WHEN question = 'Root cause  identified' THEN response
                   ELSE NULL
               END) AS "Root Cause",
           max(CASE
                   WHEN question = 'Action Taken' THEN response
                   ELSE NULL
               END) AS "Action Taken",
           max(CASE
                   WHEN question = 'Stafclosure_fs Name who prepared / supplied product' THEN response
                   ELSE NULL
               END) AS "Staff Name",
           max(CASE
                   WHEN question = 'Suggested Corrective and preventive action' THEN response
                   ELSE NULL
               END) AS "Suggested Action",
           max(CASE
                   WHEN question = 'What were the finding of investigation ? ( give details)' THEN response
                   ELSE NULL
               END) AS "Investigation Findings",
           max(CASE
                   WHEN question = 'What is the reason of marking it as invalid?' THEN response
                   ELSE NULL
               END) AS "Reason for Invalid"
   FROM closure_raw
   GROUP BY 1,
            2,
            3)
SELECT t.*,
       closure.*
FROM t
LEFT OUTER JOIN closure ON t."Task KNID" = closure.task_id
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10,
         11,
         12,
         13,
         14,
         15,
         16,
         17,
         18,
         19,
         20,
         21,
         22,
         23,
         24,
         25,
         26,
         27,
         28,
         29,
         30,
         31,
         32,
         33,
         34,
         35,
         36,
         37,
         38,
         39,
         40,
         41,
         42,
         43,
         44,
         45,
         46,
         47,
         48,
         49,
         50,
         51,
         52,
         53,
         54,
         55,
         56,
         57,
         58,
         59
```

---

## Kitopi QIR Follow up Tasks Summary_QIR Follow Ups.sql

**Tables referenced:** kitopi.qir_follow_up_tasks_summary

**Original Query:**

```sql
-- Data Source: Kitopi QIR Follow up Tasks Summary
-- Dashboard: QIR Follow Ups
-- Category: Kitopi
-- Extracted: 2026-01-29 16:55:00
-- ============================================================

select *
from kitopi.qir_follow_up_tasks_summary
where "Assigned At" between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
```

---

## Kitopi Routine Compliance-copy_1736352103_Routine Compliance - Link fix.sql

**Tables referenced:** base, form_compliance_v2, location_acl, location_map, location_off_days, organizations, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Kitopi Routine Compliance-copy_1736352103
-- Dashboard: Routine Compliance - Link fix
-- Category: Kitopi
-- Extracted: 2026-01-29 16:57:13
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'kitopi-pegasus'
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'HQ',
                              'Head Office',
                              'All')
     AND job_location NOT ILIKE 'Head Office%'
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
                  WHERE ug2.user_id = @{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
     location_map AS
  (SELECT DISTINCT ON (job_location) job_location,
                      division AS country,
                      sub_division AS team,
   designation as cluster
   FROM user_details
   WHERE is_active = 'true'
     AND organization = 'kitopi-pegasus'
     AND job_type IN ('CK',
                      'SK',
                      'Kitchen',
                      'Warehouse', 'Sk')
   ORDER BY job_location,
            created_at ASC),
     location_off_days AS
  (SELECT 'KSA AWJ Warehouse' AS LOCATION,
          'Fri' AS off_day
   UNION SELECT 'Shobak-CPP' AS LOCATION,
          'Fri' AS off_day
   UNION SELECT 'Shobak Warehouse' AS LOCATION,
          'Fri' AS off_day
   UNION SELECT 'KUW CK1' AS LOCATION,
          'Mon' AS off_day
   UNION SELECT 'BAH CK' AS LOCATION,
          'Wed' AS off_day
   UNION SELECT 'KSA-CK2' AS LOCATION,
          'Thu' AS off_day
   UNION SELECT 'QAR-CK1' AS LOCATION,
          'Fri' AS off_day
     UNION SELECT 'Kava and Chai American University of Sharjah' AS LOCATION,
                'Fri' AS off_day
  UNION SELECT 'Kava and Chai American University of Sharjah' AS LOCATION,
                'Sat' AS off_day
  UNION SELECT 'Kava and Chai American University of Sharjah' AS LOCATION,
                'Sun' AS off_day
  UNION SELECT 'Kava and Chai CE Kiosk Sharjah' AS LOCATION,
                'Sat' AS off_day
   UNION SELECT 'Kava and Chai CE Kiosk Sharjah' AS LOCATION,
                'Sun' AS off_day
   UNION SELECT 'KUW Warehouse' AS LOCATION,
                'Fri' AS off_day
   UNION SELECT 'Bahrain Warehouse' AS LOCATION,
                'Fri' AS off_day
   UNION SELECT 'Riyadh Warehouse' AS LOCATION,
                'Fri' AS off_day
   UNION SELECT 'KSA Nakheel CK' AS LOCATION,
                'Fri' AS off_day
   UNION SELECT 'Gogreek Ripemarket' AS LOCATION,
                'Mon' AS off_day
    UNION SELECT 'Gogreek Ripemarket' AS LOCATION,
                'Tue' AS off_day
    UNION SELECT 'Gogreek Ripemarket' AS LOCATION,
                'Wed' AS off_day
    UNION SELECT 'Gogreek Ripemarket' AS LOCATION,
                'Thu' AS off_day
    UNION SELECT 'Gogreek Ripemarket' AS LOCATION,
                'Fri' AS off_day
   UNION SELECT 'Calipoke Ripemarket' AS LOCATION,
                'Mon' AS off_day
    UNION SELECT 'Calipoke Ripemarket' AS LOCATION,
                'Tue' AS off_day
    UNION SELECT 'Calipoke Ripemarket' AS LOCATION,
                'Wed' AS off_day
    UNION SELECT 'Calipoke Ripemarket' AS LOCATION,
                'Thu' AS off_day
    UNION SELECT 'Calipoke Ripemarket' AS LOCATION,
                'Fri' AS off_day),
     td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'kitopi-pegasus'),
     base AS
  (SELECT "Organization",
   "Date",
   to_char("Date", 'Dy') as "Reminded Day",
   location_map.country AS "Country",
                      location_map.team AS "Team",
   location_map.cluster as "Cluster",
   "Location",
   split_part("Routine Name", ' - ', 1) AS "Routine Name",
   "Routine KNID" as "Form KNIDa",
  row_number() OVER (PARTITION BY ("Reminded At")::date,
                                                      split_part("Routine Name", ' - ', 1),
                                                     "Location"
                                         ORDER BY "Reminded At") AS "Routine #",
   to_char("Date", 'DD-Mon') as "Da",
   "Reminded At",
   "Responded At",
   "Compliance",
   "Submission KNID"
   FROM form_compliance_v2 fc
   JOIN location_acl ON fc."Location" = location_acl.job_location
    JOIN location_map ON fc."Location" = location_map.job_location
     WHERE fc."Organization" ='kitopi-pegasus'
     AND "Reminded At" BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP
   ORDER BY "Organization",
            split_part("Routine Name", ' - ', 1),
           "Location", "Reminded At", "Responded At")
SELECT base.*
FROM base
LEFT OUTER JOIN location_off_days lod ON base."Location" = lod.location
AND base."Reminded Day" = lod.off_day
WHERE lod.location IS NULL
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10,
         11,
         12, 13, 14, 15
		 ORDER by 1, 4, 5, 6, 7, 2, 11, 8
```

---

## Kitopi Routine Compliance_Routine Compliance.sql

**Tables referenced:** base, form_compliance_v2, location_acl, location_map, location_schedule, organizations, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Kitopi Routine Compliance
-- Dashboard: Routine Compliance
-- Category: Kitopi
-- Extracted: 2026-01-29 16:52:41
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'kitopi-pegasus'
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'HQ',
                              'Head Office',
                              'All')
     AND job_location NOT ILIKE 'Head Office%'
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
                  WHERE ug2.user_id = @{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
     location_map AS
  (SELECT DISTINCT ON (job_location) job_location,
                      division AS country,
                      sub_division AS team,
   designation as cluster
   FROM user_details
   WHERE is_active = 'true'
     AND organization = 'kitopi-pegasus'
     AND job_type IN ('CK',
                      'SK',
                      'Kitchen',
                      'Warehouse', 'Sk')
   ORDER BY job_location,
            created_at ASC),
    location_schedule AS
  (select '800Pizza DHCC' as location, 'Mon' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza DHCC' as location, 'Tue' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza DHCC' as location, 'Wed' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza DHCC' as location, 'Thu' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza DHCC' as location, 'Fri' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza DHCC' as location, 'Sat' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza DHCC' as location, 'Sun' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Jumeirah' as location, 'Mon' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Jumeirah' as location, 'Tue' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Jumeirah' as location, 'Wed' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Jumeirah' as location, 'Thu' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Jumeirah' as location, 'Fri' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Jumeirah' as location, 'Sat' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Jumeirah' as location, 'Sun' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Marina' as location, 'Mon' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Marina' as location, 'Tue' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Marina' as location, 'Wed' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Marina' as location, 'Thu' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Marina' as location, 'Fri' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Marina' as location, 'Sat' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Marina' as location, 'Sun' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Motor City' as location, 'Mon' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Motor City' as location, 'Tue' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Motor City' as location, 'Wed' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Motor City' as location, 'Thu' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Motor City' as location, 'Fri' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Motor City' as location, 'Sat' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select '800Pizza Motor City' as location, 'Sun' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select '800Pizza Sustainable City' as location, 'Mon' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Sustainable City' as location, 'Tue' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Sustainable City' as location, 'Wed' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Sustainable City' as location, 'Thu' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Sustainable City' as location, 'Fri' as day, '11:00:00' as open_time, '23:30:00' as close_time
union select '800Pizza Sustainable City' as location, 'Sat' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select '800Pizza Sustainable City' as location, 'Sun' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'AAQ 3' as location, 'Mon' as day, '11:00:00' as open_time, '04:00:00' as close_time
union select 'AAQ 3' as location, 'Tue' as day, '11:00:00' as open_time, '04:00:00' as close_time
union select 'AAQ 3' as location, 'Wed' as day, '11:00:00' as open_time, '04:00:00' as close_time
union select 'AAQ 3' as location, 'Thu' as day, '11:00:00' as open_time, '04:00:00' as close_time
union select 'AAQ 3' as location, 'Fri' as day, '11:00:00' as open_time, '04:00:00' as close_time
union select 'AAQ 3' as location, 'Sat' as day, '11:00:00' as open_time, '04:00:00' as close_time
union select 'AAQ 3' as location, 'Sun' as day, '11:00:00' as open_time, '04:00:00' as close_time
union select 'Abu Dhabi 1 Airport Road' as location, 'Mon' as day, '09:00:00' as open_time, '03:00:00' as close_time
union select 'Abu Dhabi 1 Airport Road' as location, 'Tue' as day, '09:00:00' as open_time, '03:00:00' as close_time
union select 'Abu Dhabi 1 Airport Road' as location, 'Wed' as day, '09:00:00' as open_time, '03:00:00' as close_time
union select 'Abu Dhabi 1 Airport Road' as location, 'Thu' as day, '09:00:00' as open_time, '03:00:00' as close_time
union select 'Abu Dhabi 1 Airport Road' as location, 'Fri' as day, '09:00:00' as open_time, '03:00:00' as close_time
union select 'Abu Dhabi 1 Airport Road' as location, 'Sat' as day, '09:00:00' as open_time, '03:00:00' as close_time
union select 'Abu Dhabi 1 Airport Road' as location, 'Sun' as day, '09:00:00' as open_time, '03:00:00' as close_time
union select 'Abu Dhabi 7' as location, 'Mon' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'Abu Dhabi 7' as location, 'Tue' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'Abu Dhabi 7' as location, 'Wed' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'Abu Dhabi 7' as location, 'Thu' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'Abu Dhabi 7' as location, 'Fri' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'Abu Dhabi 7' as location, 'Sat' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'Abu Dhabi 7' as location, 'Sun' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'Abu Hamour' as location, 'Mon' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Abu Hamour' as location, 'Tue' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Abu Hamour' as location, 'Wed' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Abu Hamour' as location, 'Thu' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Abu Hamour' as location, 'Fri' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Abu Hamour' as location, 'Sat' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Abu Hamour' as location, 'Sun' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'AD 8' as location, 'Mon' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'AD 8' as location, 'Tue' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'AD 8' as location, 'Wed' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'AD 8' as location, 'Thu' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'AD 8' as location, 'Fri' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'AD 8' as location, 'Sat' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'AD 8' as location, 'Sun' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'Adeliya SK' as location, 'Mon' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'Adeliya SK' as location, 'Tue' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'Adeliya SK' as location, 'Wed' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'Adeliya SK' as location, 'Thu' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'Adeliya SK' as location, 'Fri' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'Adeliya SK' as location, 'Sat' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'Adeliya SK' as location, 'Sun' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'AL ZAHRA SK' as location, 'Mon' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'AL ZAHRA SK' as location, 'Tue' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'AL ZAHRA SK' as location, 'Wed' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'AL ZAHRA SK' as location, 'Thu' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'AL ZAHRA SK' as location, 'Fri' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'AL ZAHRA SK' as location, 'Sat' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'AL ZAHRA SK' as location, 'Sun' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'Aljad Container' as location, 'Mon' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Aljad Container' as location, 'Tue' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Aljad Container' as location, 'Wed' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Aljad Container' as location, 'Thu' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Aljad Container' as location, 'Fri' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Aljad Container' as location, 'Sat' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Aljad Container' as location, 'Sun' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'ARDIYA 3' as location, 'Mon' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'ARDIYA 3' as location, 'Tue' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'ARDIYA 3' as location, 'Wed' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'ARDIYA 3' as location, 'Thu' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'ARDIYA 3' as location, 'Fri' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'ARDIYA 3' as location, 'Sat' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'ARDIYA 3' as location, 'Sun' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'Assima Mall RHS' as location, 'Mon' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Assima Mall RHS' as location, 'Tue' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Assima Mall RHS' as location, 'Wed' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Assima Mall RHS' as location, 'Thu' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Assima Mall RHS' as location, 'Fri' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Assima Mall RHS' as location, 'Sat' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Assima Mall RHS' as location, 'Sun' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Awani Al Bateen' as location, 'Mon' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Al Bateen' as location, 'Tue' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Al Bateen' as location, 'Wed' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Al Bateen' as location, 'Thu' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Al Bateen' as location, 'Fri' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Al Bateen' as location, 'Sat' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Al Bateen' as location, 'Sun' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Dubai Hills Mall' as location, 'Mon' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Dubai Hills Mall' as location, 'Tue' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Dubai Hills Mall' as location, 'Wed' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Dubai Hills Mall' as location, 'Thu' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Dubai Hills Mall' as location, 'Fri' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Dubai Hills Mall' as location, 'Sat' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Dubai Hills Mall' as location, 'Sun' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Dubai Mall' as location, 'Mon' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Dubai Mall' as location, 'Tue' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Dubai Mall' as location, 'Wed' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Dubai Mall' as location, 'Thu' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Dubai Mall' as location, 'Fri' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Dubai Mall' as location, 'Sat' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Dubai Mall' as location, 'Sun' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani JBR' as location, 'Mon' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani JBR' as location, 'Tue' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani JBR' as location, 'Wed' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani JBR' as location, 'Thu' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani JBR' as location, 'Fri' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani JBR' as location, 'Sat' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani JBR' as location, 'Sun' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Marina Mall' as location, 'Mon' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Marina Mall' as location, 'Tue' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Marina Mall' as location, 'Wed' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Marina Mall' as location, 'Thu' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Marina Mall' as location, 'Fri' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Marina Mall' as location, 'Sat' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Marina Mall' as location, 'Sun' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Marassi Galleria' as location, 'Mon' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Marassi Galleria' as location, 'Tue' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Marassi Galleria' as location, 'Wed' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Marassi Galleria' as location, 'Thu' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Marassi Galleria' as location, 'Fri' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Marassi Galleria' as location, 'Sat' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Awani Marassi Galleria' as location, 'Sun' as day, '09:00:00' as open_time, '23:59:59' as close_time  
union select 'Awani Meadows' as location, 'Mon' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Meadows' as location, 'Tue' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Meadows' as location, 'Wed' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Meadows' as location, 'Thu' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Meadows' as location, 'Fri' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Meadows' as location, 'Sat' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Meadows' as location, 'Sun' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Uwalk' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Uwalk' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Uwalk' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Uwalk' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Uwalk' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Uwalk' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Awani Uwalk' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'BAH CK' as location, 'Mon' as day, '06:00:00' as open_time, '15:00:00' as close_time
union select 'BAH CK' as location, 'Tue' as day, '06:00:00' as open_time, '15:00:00' as close_time
union select 'BAH CK' as location, 'Thu' as day, '06:00:00' as open_time, '15:00:00' as close_time
union select 'BAH CK' as location, 'Fri' as day, '06:00:00' as open_time, '15:00:00' as close_time
union select 'BAH CK' as location, 'Sat' as day, '06:00:00' as open_time, '15:00:00' as close_time
union select 'BAH CK' as location, 'Sun' as day, '06:00:00' as open_time, '15:00:00' as close_time
union select 'Bahrain Warehouse' as location, 'Mon' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'Bahrain Warehouse' as location, 'Tue' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'Bahrain Warehouse' as location, 'Wed' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'Bahrain Warehouse' as location, 'Thu' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'Bahrain Warehouse' as location, 'Sat' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'Bahrain Warehouse' as location, 'Sun' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'Biryani Pot Baniyas' as location, 'Mon' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Baniyas' as location, 'Tue' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Baniyas' as location, 'Wed' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Baniyas' as location, 'Thu' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Baniyas' as location, 'Fri' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Baniyas' as location, 'Sat' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Baniyas' as location, 'Sun' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Galleria' as location, 'Mon' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'Biryani Pot Galleria' as location, 'Tue' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'Biryani Pot Galleria' as location, 'Wed' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'Biryani Pot Galleria' as location, 'Thu' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'Biryani Pot Galleria' as location, 'Fri' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'Biryani Pot Galleria' as location, 'Sat' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'Biryani Pot Galleria' as location, 'Sun' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'Biryani Pot Hili' as location, 'Mon' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Hili' as location, 'Tue' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Hili' as location, 'Wed' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Hili' as location, 'Thu' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Hili' as location, 'Fri' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Hili' as location, 'Sat' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Hili' as location, 'Sun' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Jumeirah' as location, 'Mon' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Jumeirah' as location, 'Tue' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Jumeirah' as location, 'Wed' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Jumeirah' as location, 'Thu' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Jumeirah' as location, 'Fri' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Jumeirah' as location, 'Sat' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'Biryani Pot Jumeirah' as location, 'Sun' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'Box It - Saar Bahrain' as location, 'Mon' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'Box It - Saar Bahrain' as location, 'Tue' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'Box It - Saar Bahrain' as location, 'Wed' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'Box It - Saar Bahrain' as location, 'Thu' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'Box It - Saar Bahrain' as location, 'Fri' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'Box It - Saar Bahrain' as location, 'Sat' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'Box It - Saar Bahrain' as location, 'Sun' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'BUSINESS BAY 4' as location, 'Mon' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'BUSINESS BAY 4' as location, 'Tue' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'BUSINESS BAY 4' as location, 'Wed' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'BUSINESS BAY 4' as location, 'Thu' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'BUSINESS BAY 4' as location, 'Fri' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'BUSINESS BAY 4' as location, 'Sat' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'BUSINESS BAY 4' as location, 'Sun' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Cali Poke Atlantis' as location, 'Mon' as day, '09:45:00' as open_time, '18:30:00' as close_time
union select 'Cali Poke Atlantis' as location, 'Tue' as day, '09:45:00' as open_time, '18:30:00' as close_time
union select 'Cali Poke Atlantis' as location, 'Wed' as day, '09:45:00' as open_time, '18:30:00' as close_time
union select 'Cali Poke Atlantis' as location, 'Thu' as day, '09:45:00' as open_time, '18:30:00' as close_time
union select 'Cali Poke Atlantis' as location, 'Fri' as day, '09:45:00' as open_time, '18:30:00' as close_time
union select 'Cali Poke Atlantis' as location, 'Sat' as day, '09:45:00' as open_time, '18:30:00' as close_time
union select 'Cali Poke Atlantis' as location, 'Sun' as day, '09:45:00' as open_time, '18:30:00' as close_time
union select 'CaliPoke BB' as location, 'Mon' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'CaliPoke BB' as location, 'Tue' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'CaliPoke BB' as location, 'Wed' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'CaliPoke BB' as location, 'Thu' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'CaliPoke BB' as location, 'Fri' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'CaliPoke BB' as location, 'Sat' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'CaliPoke BB' as location, 'Sun' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Calipoke Bike Station' as location, 'Mon' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Calipoke Bike Station' as location, 'Tue' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Calipoke Bike Station' as location, 'Wed' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Calipoke Bike Station' as location, 'Thu' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Calipoke Bike Station' as location, 'Fri' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Calipoke Bike Station' as location, 'Sat' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Calipoke Bike Station' as location, 'Sun' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Calipoke Dubai Hill Mall' as location, 'Mon' as day, '07:00:00' as open_time, '20:00:00' as close_time
union select 'Calipoke Dubai Hill Mall' as location, 'Tue' as day, '07:00:00' as open_time, '20:00:00' as close_time
union select 'Calipoke Dubai Hill Mall' as location, 'Wed' as day, '07:00:00' as open_time, '20:00:00' as close_time
union select 'Calipoke Dubai Hill Mall' as location, 'Thu' as day, '07:00:00' as open_time, '20:00:00' as close_time
union select 'Calipoke Dubai Hill Mall' as location, 'Fri' as day, '07:00:00' as open_time, '20:00:00' as close_time
union select 'Calipoke Dubai Hill Mall' as location, 'Sat' as day, '07:00:00' as open_time, '20:00:00' as close_time
union select 'Calipoke Dubai Hill Mall' as location, 'Sun' as day, '07:00:00' as open_time, '20:00:00' as close_time
union select 'Calipoke Ripemarket' as location, 'Sat' as day, '09:00:00' as open_time, '21:00:00' as close_time
union select 'Calipoke Ripemarket' as location, 'Sun' as day, '09:00:00' as open_time, '21:00:00' as close_time
union select 'Catch22 DHM' as location, 'Mon' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Catch22 DHM' as location, 'Tue' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Catch22 DHM' as location, 'Wed' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Catch22 DHM' as location, 'Thu' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Catch22 DHM' as location, 'Fri' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Catch22 DHM' as location, 'Sat' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Catch22 DHM' as location, 'Sun' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Catch22 JBR' as location, 'Mon' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Catch22 JBR' as location, 'Tue' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Catch22 JBR' as location, 'Wed' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Catch22 JBR' as location, 'Thu' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Catch22 JBR' as location, 'Fri' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Catch22 JBR' as location, 'Sat' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Catch22 JBR' as location, 'Sun' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Catch22 Mirdiff' as location, 'Mon' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Catch22 Mirdiff' as location, 'Tue' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Catch22 Mirdiff' as location, 'Wed' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Catch22 Mirdiff' as location, 'Thu' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Catch22 Mirdiff' as location, 'Fri' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Catch22 Mirdiff' as location, 'Sat' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Catch22 Mirdiff' as location, 'Sun' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Catch22 Tahlia' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Catch22 Tahlia' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Catch22 Tahlia' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Catch22 Tahlia' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Catch22 Tahlia' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Catch22 Tahlia' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Catch22 Tahlia' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Catch22 Uwalk' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Catch22 Uwalk' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Catch22 Uwalk' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Catch22 Uwalk' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Catch22 Uwalk' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Catch22 Uwalk' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Catch22 Uwalk' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Catch 22 Zahia City Center' as location, 'Mon' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Catch 22 Zahia City Center' as location, 'Tue' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Catch 22 Zahia City Center' as location, 'Wed' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Catch 22 Zahia City Center' as location, 'Thu' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Catch 22 Zahia City Center' as location, 'Fri' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Catch 22 Zahia City Center' as location, 'Sat' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Catch 22 Zahia City Center' as location, 'Sun' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin Chin Baniyas' as location, 'Mon' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Chin Chin Baniyas' as location, 'Tue' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Chin Chin Baniyas' as location, 'Wed' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Chin Chin Baniyas' as location, 'Thu' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Chin Chin Baniyas' as location, 'Fri' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Chin Chin Baniyas' as location, 'Sat' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Chin Chin Baniyas' as location, 'Sun' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Chin Chin Diera City Center' as location, 'Mon' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin Chin Diera City Center' as location, 'Tue' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin Chin Diera City Center' as location, 'Wed' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin Chin Diera City Center' as location, 'Thu' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin Chin Diera City Center' as location, 'Fri' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin Chin Diera City Center' as location, 'Sat' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin Chin Diera City Center' as location, 'Sun' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin Chin Dubai Festival City' as location, 'Mon' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Chin Chin Dubai Festival City' as location, 'Tue' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Chin Chin Dubai Festival City' as location, 'Wed' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Chin Chin Dubai Festival City' as location, 'Thu' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Chin Chin Dubai Festival City' as location, 'Fri' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Chin Chin Dubai Festival City' as location, 'Sat' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Chin Chin Dubai Festival City' as location, 'Sun' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Chin Chin Dubai Mall' as location, 'Mon' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin Chin Dubai Mall' as location, 'Tue' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin Chin Dubai Mall' as location, 'Wed' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin Chin Dubai Mall' as location, 'Thu' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin Chin Dubai Mall' as location, 'Fri' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin Chin Dubai Mall' as location, 'Sat' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin Chin Dubai Mall' as location, 'Sun' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin Chin Granada mall' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Chin Chin Granada mall' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Chin Chin Granada mall' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Chin Chin Granada mall' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Chin Chin Granada mall' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Chin Chin Granada mall' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Chin Chin Granada mall' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Chin Chin GV' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Chin Chin GV' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Chin Chin GV' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Chin Chin GV' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Chin Chin GV' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Chin Chin GV' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Chin Chin GV' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Chin Chin Malqa' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Chin Chin Malqa' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Chin Chin Malqa' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Chin Chin Malqa' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Chin Chin Malqa' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Chin Chin Malqa' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Chin Chin Malqa' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Chin chin mushriff' as location, 'Mon' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin chin mushriff' as location, 'Tue' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin chin mushriff' as location, 'Wed' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin chin mushriff' as location, 'Thu' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin chin mushriff' as location, 'Fri' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin chin mushriff' as location, 'Sat' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Chin chin mushriff' as location, 'Sun' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'ChinChin Ajman' as location, 'Mon' as day, '06:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Ajman' as location, 'Tue' as day, '06:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Ajman' as location, 'Wed' as day, '06:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Ajman' as location, 'Thu' as day, '06:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Ajman' as location, 'Fri' as day, '06:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Ajman' as location, 'Sat' as day, '06:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Ajman' as location, 'Sun' as day, '06:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Al Ain' as location, 'Mon' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Al Ain' as location, 'Tue' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Al Ain' as location, 'Wed' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Al Ain' as location, 'Thu' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Al Ain' as location, 'Fri' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Al Ain' as location, 'Sat' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Al Ain' as location, 'Sun' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Al Zahiya' as location, 'Mon' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Al Zahiya' as location, 'Tue' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Al Zahiya' as location, 'Wed' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Al Zahiya' as location, 'Thu' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Al Zahiya' as location, 'Fri' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Al Zahiya' as location, 'Sat' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Al Zahiya' as location, 'Sun' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Chinchin Burjman' as location, 'Mon' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Chinchin Burjman' as location, 'Tue' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Chinchin Burjman' as location, 'Wed' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Chinchin Burjman' as location, 'Thu' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Chinchin Burjman' as location, 'Fri' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Chinchin Burjman' as location, 'Sat' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Chinchin Burjman' as location, 'Sun' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Chin Chin JLT' as location, 'Mon' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Chin Chin JLT' as location, 'Tue' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Chin Chin JLT' as location, 'Wed' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Chin Chin JLT' as location, 'Thu' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Chin Chin JLT' as location, 'Fri' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Chin Chin JLT' as location, 'Sat' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Chin Chin JLT' as location, 'Sun' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin JVC' as location, 'Mon' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin JVC' as location, 'Tue' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin JVC' as location, 'Wed' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin JVC' as location, 'Thu' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin JVC' as location, 'Fri' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin JVC' as location, 'Sat' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin JVC' as location, 'Sun' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Mirdiff' as location, 'Mon' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Mirdiff' as location, 'Tue' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Mirdiff' as location, 'Wed' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Mirdiff' as location, 'Thu' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Mirdiff' as location, 'Fri' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Mirdiff' as location, 'Sat' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Mirdiff' as location, 'Sun' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Muweillah' as location, 'Mon' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'ChinChin Muweillah' as location, 'Tue' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'ChinChin Muweillah' as location, 'Wed' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'ChinChin Muweillah' as location, 'Thu' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'ChinChin Muweillah' as location, 'Fri' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'ChinChin Muweillah' as location, 'Sat' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'ChinChin Muweillah' as location, 'Sun' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'Chinchin Sahara Center' as location, 'Mon' as day, '18:00:00' as open_time, '23:00:00' as close_time
union select 'Chinchin Sahara Center' as location, 'Tue' as day, '18:00:00' as open_time, '23:00:00' as close_time
union select 'Chinchin Sahara Center' as location, 'Wed' as day, '18:00:00' as open_time, '23:00:00' as close_time
union select 'Chinchin Sahara Center' as location, 'Thu' as day, '18:00:00' as open_time, '23:00:00' as close_time
union select 'Chinchin Sahara Center' as location, 'Fri' as day, '18:00:00' as open_time, '23:00:00' as close_time
union select 'Chinchin Sahara Center' as location, 'Sat' as day, '18:00:00' as open_time, '23:00:00' as close_time
union select 'Chinchin Sahara Center' as location, 'Sun' as day, '18:00:00' as open_time, '23:00:00' as close_time
union select 'ChinChin Satwa' as location, 'Mon' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Satwa' as location, 'Tue' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Satwa' as location, 'Wed' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Satwa' as location, 'Thu' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Satwa' as location, 'Fri' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Satwa' as location, 'Sat' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Satwa' as location, 'Sun' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Tecom' as location, 'Mon' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Tecom' as location, 'Tue' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Tecom' as location, 'Wed' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Tecom' as location, 'Thu' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Tecom' as location, 'Fri' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Tecom' as location, 'Sat' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'ChinChin Tecom' as location, 'Sun' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Circle Cafe Arabian Ranches' as location, 'Mon' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Circle Cafe Arabian Ranches' as location, 'Tue' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Circle Cafe Arabian Ranches' as location, 'Wed' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Circle Cafe Arabian Ranches' as location, 'Thu' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Circle Cafe Arabian Ranches' as location, 'Fri' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Circle Cafe Arabian Ranches' as location, 'Sat' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Circle Cafe Arabian Ranches' as location, 'Sun' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Circle Cafe Bay Square' as location, 'Mon' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Bay Square' as location, 'Tue' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Bay Square' as location, 'Wed' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Bay Square' as location, 'Thu' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Bay Square' as location, 'Fri' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Bay Square' as location, 'Sat' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Bay Square' as location, 'Sun' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe DHCC' as location, 'Mon' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'Circle Cafe DHCC' as location, 'Tue' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'Circle Cafe DHCC' as location, 'Wed' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'Circle Cafe DHCC' as location, 'Thu' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'Circle Cafe DHCC' as location, 'Fri' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'Circle Cafe DHCC' as location, 'Sat' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'Circle Cafe DHCC' as location, 'Sun' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'Circle Cafe DIFC' as location, 'Mon' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe DIFC' as location, 'Tue' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe DIFC' as location, 'Wed' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe DIFC' as location, 'Thu' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe DIFC' as location, 'Fri' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe DIFC' as location, 'Sat' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe DIFC' as location, 'Sun' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe JIP' as location, 'Mon' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe JIP' as location, 'Tue' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe JIP' as location, 'Wed' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe JIP' as location, 'Thu' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe JIP' as location, 'Fri' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe JIP' as location, 'Sat' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe JIP' as location, 'Sun' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Kite Beach' as location, 'Mon' as day, '13:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Kite Beach' as location, 'Tue' as day, '13:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Kite Beach' as location, 'Wed' as day, '13:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Kite Beach' as location, 'Thu' as day, '13:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Kite Beach' as location, 'Fri' as day, '13:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Kite Beach' as location, 'Sat' as day, '13:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Kite Beach' as location, 'Sun' as day, '13:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Mangrove AD' as location, 'Mon' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Mangrove AD' as location, 'Tue' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Mangrove AD' as location, 'Wed' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Mangrove AD' as location, 'Thu' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Mangrove AD' as location, 'Fri' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Mangrove AD' as location, 'Sat' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Mangrove AD' as location, 'Sun' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Marina Mall' as location, 'Mon' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Circle Cafe Marina Mall' as location, 'Tue' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Circle Cafe Marina Mall' as location, 'Wed' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Circle Cafe Marina Mall' as location, 'Thu' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Circle Cafe Marina Mall' as location, 'Fri' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Circle Cafe Marina Mall' as location, 'Sat' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Circle Cafe Marina Mall' as location, 'Sun' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Circle Cafe Mediacity' as location, 'Mon' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Mediacity' as location, 'Tue' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Mediacity' as location, 'Wed' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Mediacity' as location, 'Thu' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Mediacity' as location, 'Fri' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Mediacity' as location, 'Sat' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Mediacity' as location, 'Sun' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Saadiyat' as location, 'Mon' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Saadiyat' as location, 'Tue' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Saadiyat' as location, 'Wed' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Saadiyat' as location, 'Thu' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Saadiyat' as location, 'Fri' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Saadiyat' as location, 'Sat' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Saadiyat' as location, 'Sun' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Shorooq' as location, 'Mon' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Shorooq' as location, 'Tue' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Shorooq' as location, 'Wed' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Shorooq' as location, 'Thu' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Shorooq' as location, 'Fri' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Shorooq' as location, 'Sat' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Shorooq' as location, 'Sun' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Studio City' as location, 'Mon' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Studio City' as location, 'Tue' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Studio City' as location, 'Wed' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Studio City' as location, 'Thu' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Studio City' as location, 'Fri' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Studio City' as location, 'Sat' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'Circle Cafe Studio City' as location, 'Sun' as day, '08:00:00' as open_time, '20:00:00' as close_time
union select 'CK Najres' as location, 'Mon' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'CK Najres' as location, 'Tue' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'CK Najres' as location, 'Wed' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'CK Najres' as location, 'Thu' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'CK Najres' as location, 'Fri' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'CK Najres' as location, 'Sat' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'CK Najres' as location, 'Sun' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'Deliveroo Editions Abudhabi' as location, 'Mon' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Deliveroo Editions Abudhabi' as location, 'Tue' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Deliveroo Editions Abudhabi' as location, 'Wed' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Deliveroo Editions Abudhabi' as location, 'Thu' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Deliveroo Editions Abudhabi' as location, 'Fri' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Deliveroo Editions Abudhabi' as location, 'Sat' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Deliveroo Editions Abudhabi' as location, 'Sun' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Deliveroo Editions Uptown Mirdif' as location, 'Mon' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Deliveroo Editions Uptown Mirdif' as location, 'Tue' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Deliveroo Editions Uptown Mirdif' as location, 'Wed' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Deliveroo Editions Uptown Mirdif' as location, 'Thu' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Deliveroo Editions Uptown Mirdif' as location, 'Fri' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Deliveroo Editions Uptown Mirdif' as location, 'Sat' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Deliveroo Editions Uptown Mirdif' as location, 'Sun' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'DH Chin Chin Rak' as location, 'Mon' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'DH Chin Chin Rak' as location, 'Tue' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'DH Chin Chin Rak' as location, 'Wed' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'DH Chin Chin Rak' as location, 'Thu' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'DH Chin Chin Rak' as location, 'Fri' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'DH Chin Chin Rak' as location, 'Sat' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'DH Chin Chin Rak' as location, 'Sun' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'DHK Muweilah' as location, 'Mon' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'DHK Muweilah' as location, 'Tue' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'DHK Muweilah' as location, 'Wed' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'DHK Muweilah' as location, 'Thu' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'DHK Muweilah' as location, 'Fri' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'DHK Muweilah' as location, 'Sat' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'DHK Muweilah' as location, 'Sun' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'Diet House Sumaisma - QAR' as location, 'Mon' as day, '15:00:00' as open_time, '23:00:00' as close_time
union select 'Diet House Sumaisma - QAR' as location, 'Tue' as day, '15:00:00' as open_time, '23:00:00' as close_time
union select 'Diet House Sumaisma - QAR' as location, 'Wed' as day, '15:00:00' as open_time, '23:00:00' as close_time
union select 'Diet House Sumaisma - QAR' as location, 'Thu' as day, '15:00:00' as open_time, '23:00:00' as close_time
union select 'Diet House Sumaisma - QAR' as location, 'Fri' as day, '15:00:00' as open_time, '23:00:00' as close_time
union select 'Diet House Sumaisma - QAR' as location, 'Sat' as day, '15:00:00' as open_time, '23:00:00' as close_time
union select 'Diet House Sumaisma - QAR' as location, 'Sun' as day, '15:00:00' as open_time, '23:00:00' as close_time
union select 'DHK Pizzaro Al Ain' as location, 'Mon' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'DHK Pizzaro Al Ain' as location, 'Tue' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'DHK Pizzaro Al Ain' as location, 'Wed' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'DHK Pizzaro Al Ain' as location, 'Thu' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'DHK Pizzaro Al Ain' as location, 'Fri' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'DHK Pizzaro Al Ain' as location, 'Sat' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'DHK Pizzaro Al Ain' as location, 'Sun' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Diethouse Gharafah' as location, 'Mon' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Diethouse Gharafah' as location, 'Tue' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Diethouse Gharafah' as location, 'Wed' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Diethouse Gharafah' as location, 'Thu' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Diethouse Gharafah' as location, 'Fri' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Diethouse Gharafah' as location, 'Sat' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Diethouse Gharafah' as location, 'Sun' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'DSO Kitchen' as location, 'Mon' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'DSO Kitchen' as location, 'Tue' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'DSO Kitchen' as location, 'Wed' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'DSO Kitchen' as location, 'Thu' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'DSO Kitchen' as location, 'Fri' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'DSO Kitchen' as location, 'Sat' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'DSO Kitchen' as location, 'Sun' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'DSO2' as location, 'Mon' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'DSO2' as location, 'Tue' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'DSO2' as location, 'Wed' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'DSO2' as location, 'Thu' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'DSO2' as location, 'Fri' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'DSO2' as location, 'Sat' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'DSO2' as location, 'Sun' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'Earth Kitchen DIFC' as location, 'Mon' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Earth Kitchen DIFC' as location, 'Tue' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Earth Kitchen DIFC' as location, 'Wed' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Earth Kitchen DIFC' as location, 'Thu' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Earth Kitchen DIFC' as location, 'Fri' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Earth Kitchen DIFC' as location, 'Sat' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Earth Kitchen DIFC' as location, 'Sun' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Eatopi Dubai Hills Mall' as location, 'Mon' as day, '10:00:00' as open_time, '00:00:00' as close_time
union select 'Eatopi Dubai Hills Mall' as location, 'Tue' as day, '10:00:00' as open_time, '00:00:00' as close_time
union select 'Eatopi Dubai Hills Mall' as location, 'Wed' as day, '10:00:00' as open_time, '00:00:00' as close_time
union select 'Eatopi Dubai Hills Mall' as location, 'Thu' as day, '10:00:00' as open_time, '00:00:00' as close_time
union select 'Eatopi Dubai Hills Mall' as location, 'Fri' as day, '10:00:00' as open_time, '00:00:00' as close_time
union select 'Eatopi Dubai Hills Mall' as location, 'Sat' as day, '10:00:00' as open_time, '00:00:00' as close_time
union select 'Eatopi Dubai Hills Mall' as location, 'Sun' as day, '10:00:00' as open_time, '00:00:00' as close_time
union select 'Eatopi one central' as location, 'Mon' as day, '07:00:00' as open_time, '19:00:00' as close_time
union select 'Eatopi one central' as location, 'Tue' as day, '07:00:00' as open_time, '19:00:00' as close_time
union select 'Eatopi one central' as location, 'Wed' as day, '07:00:00' as open_time, '19:00:00' as close_time
union select 'Eatopi one central' as location, 'Thu' as day, '07:00:00' as open_time, '19:00:00' as close_time
union select 'Eatopi one central' as location, 'Fri' as day, '07:00:00' as open_time, '19:00:00' as close_time
union select 'Eatopi one central' as location, 'Sat' as day, '07:00:00' as open_time, '19:00:00' as close_time
union select 'Eatopi one central' as location, 'Sun' as day, '07:00:00' as open_time, '19:00:00' as close_time
union select 'Fat brand Forsan Mall' as location, 'Mon' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Fat brand Forsan Mall' as location, 'Tue' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Fat brand Forsan Mall' as location, 'Wed' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Fat brand Forsan Mall' as location, 'Thu' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Fat brand Forsan Mall' as location, 'Fri' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'Fat brand Forsan Mall' as location, 'Sat' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'Fat brand Forsan Mall' as location, 'Sun' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'FINTAS' as location, 'Mon' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'FINTAS' as location, 'Tue' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'FINTAS' as location, 'Wed' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'FINTAS' as location, 'Thu' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'FINTAS' as location, 'Fri' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'FINTAS' as location, 'Sat' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'FINTAS' as location, 'Sun' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'Flavour Fields' as location, 'Mon' as day, '10:00:00' as open_time, '07:00:00' as close_time
union select 'Flavour Fields' as location, 'Tue' as day, '10:00:00' as open_time, '07:00:00' as close_time
union select 'Flavour Fields' as location, 'Wed' as day, '10:00:00' as open_time, '07:00:00' as close_time
union select 'Flavour Fields' as location, 'Thu' as day, '10:00:00' as open_time, '07:00:00' as close_time
union select 'Flavour Fields' as location, 'Fri' as day, '10:00:00' as open_time, '07:00:00' as close_time
union select 'Flavour Fields' as location, 'Sat' as day, '10:00:00' as open_time, '07:00:00' as close_time
union select 'Flavour Fields' as location, 'Sun' as day, '10:00:00' as open_time, '07:00:00' as close_time
union select 'GoBrand-Edition Kitchen-Business Bay' as location, 'Mon' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'GoBrand-Edition Kitchen-Business Bay' as location, 'Tue' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'GoBrand-Edition Kitchen-Business Bay' as location, 'Wed' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'GoBrand-Edition Kitchen-Business Bay' as location, 'Thu' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'GoBrand-Edition Kitchen-Business Bay' as location, 'Fri' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'GoBrand-Edition Kitchen-Business Bay' as location, 'Sat' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'GoBrand-Edition Kitchen-Business Bay' as location, 'Sun' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'GoBrand-Edition Kitchen-Hessa Street' as location, 'Mon' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'GoBrand-Edition Kitchen-Hessa Street' as location, 'Tue' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'GoBrand-Edition Kitchen-Hessa Street' as location, 'Wed' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'GoBrand-Edition Kitchen-Hessa Street' as location, 'Thu' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'GoBrand-Edition Kitchen-Hessa Street' as location, 'Fri' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'GoBrand-Edition Kitchen-Hessa Street' as location, 'Sat' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'GoBrand-Edition Kitchen-Hessa Street' as location, 'Sun' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Gogreek Ripemarket' as location, 'Sat' as day, '09:00:00' as open_time, '21:00:00' as close_time
union select 'Gogreek Ripemarket' as location, 'Sun' as day, '09:00:00' as open_time, '21:00:00' as close_time
union select 'GoGreek Townsquare' as location, 'Mon' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'GoGreek Townsquare' as location, 'Tue' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'GoGreek Townsquare' as location, 'Wed' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'GoGreek Townsquare' as location, 'Thu' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'GoGreek Townsquare' as location, 'Fri' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'GoGreek Townsquare' as location, 'Sat' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'GoGreek Townsquare' as location, 'Sun' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'Healthy KP AlReem' as location, 'Mon' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Healthy KP AlReem' as location, 'Tue' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Healthy KP AlReem' as location, 'Wed' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Healthy KP AlReem' as location, 'Thu' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Healthy KP AlReem' as location, 'Fri' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Healthy KP AlReem' as location, 'Sat' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Healthy KP AlReem' as location, 'Sun' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Healthy KP AlQuoz' as location, 'Mon' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Healthy KP AlQuoz' as location, 'Tue' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Healthy KP AlQuoz' as location, 'Wed' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Healthy KP AlQuoz' as location, 'Thu' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Healthy KP AlQuoz' as location, 'Fri' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Healthy KP AlQuoz' as location, 'Sat' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Healthy KP AlQuoz' as location, 'Sun' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'HESSA' as location, 'Mon' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'HESSA' as location, 'Tue' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'HESSA' as location, 'Wed' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'HESSA' as location, 'Thu' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'HESSA' as location, 'Fri' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'HESSA' as location, 'Sat' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'HESSA' as location, 'Sun' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'Highjoint Alkhawneej' as location, 'Mon' as day, '14:00:00' as open_time, '03:00:00' as close_time
union select 'Highjoint Alkhawneej' as location, 'Tue' as day, '14:00:00' as open_time, '03:00:00' as close_time
union select 'Highjoint Alkhawneej' as location, 'Wed' as day, '14:00:00' as open_time, '03:00:00' as close_time
union select 'Highjoint Alkhawneej' as location, 'Thu' as day, '14:00:00' as open_time, '03:00:00' as close_time
union select 'Highjoint Alkhawneej' as location, 'Fri' as day, '14:00:00' as open_time, '03:00:00' as close_time
union select 'Highjoint Alkhawneej' as location, 'Sat' as day, '14:00:00' as open_time, '03:00:00' as close_time
union select 'Highjoint Alkhawneej' as location, 'Sun' as day, '14:00:00' as open_time, '03:00:00' as close_time
union select 'Highjoint Bluewater' as location, 'Mon' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Highjoint Bluewater' as location, 'Tue' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Highjoint Bluewater' as location, 'Wed' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Highjoint Bluewater' as location, 'Thu' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Highjoint Bluewater' as location, 'Fri' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Highjoint Bluewater' as location, 'Sat' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Highjoint Bluewater' as location, 'Sun' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Highjoint Dubai Mall' as location, 'Mon' as day, '10:00:00' as open_time, '12:00:00' as close_time
union select 'Highjoint Dubai Mall' as location, 'Tue' as day, '10:00:00' as open_time, '12:00:00' as close_time
union select 'Highjoint Dubai Mall' as location, 'Wed' as day, '10:00:00' as open_time, '12:00:00' as close_time
union select 'Highjoint Dubai Mall' as location, 'Thu' as day, '10:00:00' as open_time, '12:00:00' as close_time
union select 'Highjoint Dubai Mall' as location, 'Fri' as day, '10:00:00' as open_time, '12:00:00' as close_time
union select 'Highjoint Dubai Mall' as location, 'Sat' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Highjoint Dubai Mall' as location, 'Sun' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Highjoint Dubai Hills Mall' as location, 'Mon' as day, '10:00:00' as open_time, '12:00:00' as close_time
union select 'Highjoint Dubai Hills Mall' as location, 'Tue' as day, '10:00:00' as open_time, '12:00:00' as close_time
union select 'Highjoint Dubai Hills Mall' as location, 'Wed' as day, '10:00:00' as open_time, '12:00:00' as close_time
union select 'Highjoint Dubai Hills Mall' as location, 'Thu' as day, '10:00:00' as open_time, '12:00:00' as close_time
union select 'Highjoint Dubai Hills Mall' as location, 'Fri' as day, '10:00:00' as open_time, '12:00:00' as close_time
union select 'Highjoint Dubai Hills Mall' as location, 'Sat' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Highjoint Dubai Hills Mall' as location, 'Sun' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Highjoint Emirates Tower' as location, 'Mon' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint Emirates Tower' as location, 'Tue' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint Emirates Tower' as location, 'Wed' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint Emirates Tower' as location, 'Thu' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint Emirates Tower' as location, 'Fri' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint Emirates Tower' as location, 'Sat' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint Emirates Tower' as location, 'Sun' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint JLT' as location, 'Mon' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint JLT' as location, 'Tue' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint JLT' as location, 'Wed' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint JLT' as location, 'Thu' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint JLT' as location, 'Fri' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint JLT' as location, 'Sat' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint JLT' as location, 'Sun' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'HighJoint Manara' as location, 'Mon' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'HighJoint Manara' as location, 'Tue' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'HighJoint Manara' as location, 'Wed' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'HighJoint Manara' as location, 'Thu' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'HighJoint Manara' as location, 'Fri' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'HighJoint Manara' as location, 'Sat' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'HighJoint Manara' as location, 'Sun' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint Mirdiff City Center' as location, 'Mon' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Highjoint Mirdiff City Center' as location, 'Tue' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Highjoint Mirdiff City Center' as location, 'Wed' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Highjoint Mirdiff City Center' as location, 'Thu' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Highjoint Mirdiff City Center' as location, 'Fri' as day, '10:00:00' as open_time, '23:59:59' as close_time
--union select 'Highjoint Mirdiff City Center' as location, 'Sat' as day, '10:00:00' as open_time, '23:59:59' as close_time
--union select 'Highjoint Mirdiff City Center' as location, 'Sun' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Highjoint Motorcity' as location, 'Mon' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint Motorcity' as location, 'Tue' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint Motorcity' as location, 'Wed' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint Motorcity' as location, 'Thu' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint Motorcity' as location, 'Fri' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint Motorcity' as location, 'Sat' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Highjoint Motorcity' as location, 'Sun' as day, '12:00:00' as open_time, '02:00:00' as close_time
union select 'Hotbun Jumeirah' as location, 'Mon' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Hotbun Jumeirah' as location, 'Tue' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Hotbun Jumeirah' as location, 'Wed' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Hotbun Jumeirah' as location, 'Thu' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Hotbun Jumeirah' as location, 'Fri' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Hotbun Jumeirah' as location, 'Sat' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Hotbun Jumeirah' as location, 'Sun' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Italian KP Diera' as location, 'Mon' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Italian KP Diera' as location, 'Tue' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Italian KP Diera' as location, 'Wed' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Italian KP Diera' as location, 'Thu' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Italian KP Diera' as location, 'Fri' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Italian KP Diera' as location, 'Sat' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Italian KP Diera' as location, 'Sun' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'JABRIYA' as location, 'Mon' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'JABRIYA' as location, 'Tue' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'JABRIYA' as location, 'Wed' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'JABRIYA' as location, 'Thu' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'JABRIYA' as location, 'Fri' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'JABRIYA' as location, 'Sat' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'JABRIYA' as location, 'Sun' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'JAHRA' as location, 'Mon' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'JAHRA' as location, 'Tue' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'JAHRA' as location, 'Wed' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'JAHRA' as location, 'Thu' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'JAHRA' as location, 'Fri' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'JAHRA' as location, 'Sat' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'JAHRA' as location, 'Sun' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'Katsu & Co DIFC' as location, 'Mon' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Katsu & Co DIFC' as location, 'Tue' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Katsu & Co DIFC' as location, 'Wed' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Katsu & Co DIFC' as location, 'Thu' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Katsu & Co DIFC' as location, 'Fri' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Katsu & Co DIFC' as location, 'Sat' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Katsu & Co DIFC' as location, 'Sun' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Kava and Chai American University of Sharjah' as location, 'Mon' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'Kava and Chai American University of Sharjah' as location, 'Tue' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'Kava and Chai American University of Sharjah' as location, 'Wed' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'Kava and Chai American University of Sharjah' as location, 'Thu' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'Kava and Chai CE Kiosk Sharjah' as location, 'Mon' as day, '08:00:00' as open_time, '17:00:00' as close_time
union select 'Kava and Chai CE Kiosk Sharjah' as location, 'Tue' as day, '08:00:00' as open_time, '17:00:00' as close_time
union select 'Kava and Chai CE Kiosk Sharjah' as location, 'Wed' as day, '08:00:00' as open_time, '17:00:00' as close_time
union select 'Kava and Chai CE Kiosk Sharjah' as location, 'Thu' as day, '08:00:00' as open_time, '17:00:00' as close_time
union select 'Kava and Chai CE Kiosk Sharjah' as location, 'Fri' as day, '08:00:00' as open_time, '17:00:00' as close_time
union select 'Kava and Chai MOE' as location, 'Mon' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Kava and Chai MOE' as location, 'Tue' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Kava and Chai MOE' as location, 'Wed' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Kava and Chai MOE' as location, 'Thu' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Kava and Chai MOE' as location, 'Fri' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Kava and Chai MOE' as location, 'Sat' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'Kava and Chai MOE' as location, 'Sun' as day, '10:00:00' as open_time, '23:00:00' as close_time
union select 'KSA Awani Nahkeel Mall' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Nahkeel Mall' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Nahkeel Mall' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Nahkeel Mall' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Nahkeel Mall' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Nahkeel Mall' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Nahkeel Mall' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Riyadh Front' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Riyadh Front' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Riyadh Front' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Riyadh Front' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Riyadh Front' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Riyadh Front' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Riyadh Front' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Tahilia' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Tahilia' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Tahilia' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Tahilia' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Tahilia' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Tahilia' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani Tahilia' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani The zone' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani The zone' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani The zone' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani The zone' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani The zone' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani The zone' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Awani The zone' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA AWJ Warehouse' as location, 'Mon' as day, '10:00:00' as open_time, '17:00:00' as close_time
union select 'KSA AWJ Warehouse' as location, 'Tue' as day, '10:00:00' as open_time, '17:00:00' as close_time
union select 'KSA AWJ Warehouse' as location, 'Wed' as day, '10:00:00' as open_time, '17:00:00' as close_time
union select 'KSA AWJ Warehouse' as location, 'Thu' as day, '10:00:00' as open_time, '17:00:00' as close_time
union select 'KSA AWJ Warehouse' as location, 'Fri' as day, '10:00:00' as open_time, '17:00:00' as close_time
union select 'KSA AWJ Warehouse' as location, 'Sat' as day, '10:00:00' as open_time, '17:00:00' as close_time
union select 'KSA AWJ Warehouse' as location, 'Sun' as day, '10:00:00' as open_time, '17:00:00' as close_time
union select 'KSA Catch22 Nakheel Mall' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Catch22 Nakheel Mall' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Catch22 Nakheel Mall' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Catch22 Nakheel Mall' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Catch22 Nakheel Mall' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Catch22 Nakheel Mall' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Catch22 Nakheel Mall' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Catch22 The Zone' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Catch22 The Zone' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Catch22 The Zone' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Catch22 The Zone' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Catch22 The Zone' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Catch22 The Zone' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA Catch22 The Zone' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA CK1' as location, 'Mon' as day, '08:00:00' as open_time, '19:00:00' as close_time
union select 'KSA CK1' as location, 'Tue' as day, '08:00:00' as open_time, '19:00:00' as close_time
union select 'KSA CK1' as location, 'Wed' as day, '08:00:00' as open_time, '19:00:00' as close_time
union select 'KSA CK1' as location, 'Thu' as day, '08:00:00' as open_time, '19:00:00' as close_time
union select 'KSA CK1' as location, 'Fri' as day, '08:00:00' as open_time, '19:00:00' as close_time
union select 'KSA CK1' as location, 'Sat' as day, '08:00:00' as open_time, '19:00:00' as close_time
union select 'KSA CK1' as location, 'Sun' as day, '08:00:00' as open_time, '19:00:00' as close_time
union select 'KSA CK2' as location, 'Mon' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'KSA CK2' as location, 'Tue' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'KSA CK2' as location, 'Wed' as day,  '00:00:00' as open_time, '23:59:59' as close_time
union select 'KSA CK2' as location, 'Thu' as day,  '00:00:00' as open_time, '23:59:59' as close_time
union select 'KSA CK2' as location, 'Fri' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'KSA CK2' as location, 'Sat' as day,  '00:00:00' as open_time, '23:59:59' as close_time
union select 'KSA CK2' as location, 'Sun' as day,  '00:00:00' as open_time, '23:59:59' as close_time
union select 'KSA Jeddah Safa SK' as location, 'Mon' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'KSA Jeddah Safa SK' as location, 'Tue' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'KSA Jeddah Safa SK' as location, 'Wed' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'KSA Jeddah Safa SK' as location, 'Thu' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'KSA Jeddah Safa SK' as location, 'Fri' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'KSA Jeddah Safa SK' as location, 'Sat' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'KSA Jeddah Safa SK' as location, 'Sun' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'KSA Nakheel CK' as location, 'Mon' as day, '07:00:00' as open_time, '21:00:00' as close_time
union select 'KSA Nakheel CK' as location, 'Tue' as day, '07:00:00' as open_time, '21:00:00' as close_time
union select 'KSA Nakheel CK' as location, 'Wed' as day, '07:00:00' as open_time, '21:00:00' as close_time
union select 'KSA Nakheel CK' as location, 'Thu' as day, '07:00:00' as open_time, '21:00:00' as close_time
union select 'KSA Nakheel CK' as location, 'Fri' as day, '07:00:00' as open_time, '21:00:00' as close_time
union select 'KSA Nakheel CK' as location, 'Sat' as day, '07:00:00' as open_time, '21:00:00' as close_time
union select 'KSA Nakheel CK' as location, 'Sun' as day, '07:00:00' as open_time, '21:00:00' as close_time
union select 'KSA OF Fyfa Tahila Jeddah' as location, 'Mon' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'KSA OF Fyfa Tahila Jeddah' as location, 'Tue' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'KSA OF Fyfa Tahila Jeddah' as location, 'Wed' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'KSA OF Fyfa Tahila Jeddah' as location, 'Thu' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'KSA OF Fyfa Tahila Jeddah' as location, 'Fri' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'KSA OF Fyfa Tahila Jeddah' as location, 'Sat' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'KSA OF Fyfa Tahila Jeddah' as location, 'Sun' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'KSA OF Townsquare Jeddah' as location, 'Mon' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'KSA OF Townsquare Jeddah' as location, 'Tue' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'KSA OF Townsquare Jeddah' as location, 'Wed' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'KSA OF Townsquare Jeddah' as location, 'Thu' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'KSA OF Townsquare Jeddah' as location, 'Fri' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'KSA OF Townsquare Jeddah' as location, 'Sat' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'KSA OF Townsquare Jeddah' as location, 'Sun' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'KSA OF: Prince Sultan' as location, 'Mon' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'KSA OF: Prince Sultan' as location, 'Tue' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'KSA OF: Prince Sultan' as location, 'Wed' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'KSA OF: Prince Sultan' as location, 'Thu' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'KSA OF: Prince Sultan' as location, 'Fri' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'KSA OF: Prince Sultan' as location, 'Sat' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'KSA OF: Prince Sultan' as location, 'Sun' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'KSA OF:Ajdan Walk' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Ajdan Walk' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Ajdan Walk' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Ajdan Walk' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Ajdan Walk' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Ajdan Walk' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Ajdan Walk' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Alia Plaza' as location, 'Mon' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Alia Plaza' as location, 'Tue' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Alia Plaza' as location, 'Wed' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Alia Plaza' as location, 'Thu' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Alia Plaza' as location, 'Fri' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Alia Plaza' as location, 'Sat' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Alia Plaza' as location, 'Sun' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Aramco' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Aramco' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Aramco' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Aramco' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Aramco' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Aramco' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Aramco' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Centro' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Centro' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Centro' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Centro' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Centro' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Centro' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Centro' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Corniche' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Corniche' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Corniche' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Corniche' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Corniche' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Corniche' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Corniche' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Manar' as location, 'Mon' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Manar' as location, 'Tue' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Manar' as location, 'Wed' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Manar' as location, 'Thu' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Manar' as location, 'Fri' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Manar' as location, 'Sat' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Manar' as location, 'Sun' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Mercato' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Mercato' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Mercato' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Mercato' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Mercato' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Mercato' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Mercato' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Quadisiya' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Quadisiya' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Quadisiya' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Quadisiya' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Quadisiya' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Quadisiya' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Quadisiya' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Rubeen plaza' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Rubeen plaza' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Rubeen plaza' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Rubeen plaza' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Rubeen plaza' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Rubeen plaza' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Rubeen plaza' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Tahila' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Tahila' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Tahila' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Tahila' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Tahila' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Tahila' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KSA OF:Tahila' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'KUW CK1' as location, 'Mon' as day, '07:00:00' as open_time, '16:00:00' as close_time
union select 'KUW CK1' as location, 'Tue' as day, '07:00:00' as open_time, '16:00:00' as close_time
union select 'KUW CK1' as location, 'Wed' as day, '07:00:00' as open_time, '16:00:00' as close_time
union select 'KUW CK1' as location, 'Thu' as day, '07:00:00' as open_time, '16:00:00' as close_time
union select 'KUW CK1' as location, 'Fri' as day, '07:00:00' as open_time, '16:00:00' as close_time
union select 'KUW CK1' as location, 'Sat' as day, '07:00:00' as open_time, '16:00:00' as close_time
union select 'KUW CK1' as location, 'Sun' as day, '07:00:00' as open_time, '16:00:00' as close_time
union select 'KUW CK2' as location, 'Mon' as day, '21:00:00' as open_time, '23:59:59' as close_time
union select 'KUW CK2' as location, 'Tue' as day, '21:00:00' as open_time, '23:59:59' as close_time
union select 'KUW CK2' as location, 'Wed' as day, '21:00:00' as open_time, '23:59:59' as close_time
union select 'KUW CK2' as location, 'Thu' as day, '21:00:00' as open_time, '23:59:59' as close_time
union select 'KUW CK2' as location, 'Fri' as day, '21:00:00' as open_time, '23:59:59' as close_time
union select 'KUW CK2' as location, 'Sat' as day, '21:00:00' as open_time, '23:59:59' as close_time
union select 'KUW CK2' as location, 'Sun' as day, '21:00:00' as open_time, '23:59:59' as close_time
union select 'KUW Warehouse' as location, 'Mon' as day, '06:00:00' as open_time, '15:00:00' as close_time
union select 'KUW Warehouse' as location, 'Tue' as day, '06:00:00' as open_time, '15:00:00' as close_time
union select 'KUW Warehouse' as location, 'Wed' as day, '06:00:00' as open_time, '15:00:00' as close_time
union select 'KUW Warehouse' as location, 'Thu' as day, '06:00:00' as open_time, '15:00:00' as close_time
union select 'KUW Warehouse' as location, 'Sat' as day, '06:00:00' as open_time, '15:00:00' as close_time
union select 'KUW Warehouse' as location, 'Sun' as day, '06:00:00' as open_time, '15:00:00' as close_time
union select 'Manar SK' as location, 'Mon' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Manar SK' as location, 'Tue' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Manar SK' as location, 'Wed' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Manar SK' as location, 'Thu' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Manar SK' as location, 'Fri' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Manar SK' as location, 'Sat' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Manar SK' as location, 'Sun' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Marina 3' as location, 'Mon' as day, '09:00:00' as open_time, '04:00:00' as close_time
union select 'Marina 3' as location, 'Tue' as day, '09:00:00' as open_time, '04:00:00' as close_time
union select 'Marina 3' as location, 'Wed' as day, '09:00:00' as open_time, '04:00:00' as close_time
union select 'Marina 3' as location, 'Thu' as day, '09:00:00' as open_time, '04:00:00' as close_time
union select 'Marina 3' as location, 'Fri' as day, '09:00:00' as open_time, '04:00:00' as close_time
union select 'Marina 3' as location, 'Sat' as day, '09:00:00' as open_time, '04:00:00' as close_time
union select 'Marina 3' as location, 'Sun' as day, '09:00:00' as open_time, '04:00:00' as close_time
union select 'MEDIA CITY' as location, 'Mon' as day, '11:00:00' as open_time, '04:00:00' as close_time
union select 'MEDIA CITY' as location, 'Tue' as day, '11:00:00' as open_time, '04:00:00' as close_time
union select 'MEDIA CITY' as location, 'Wed' as day, '11:00:00' as open_time, '04:00:00' as close_time
union select 'MEDIA CITY' as location, 'Thu' as day, '11:00:00' as open_time, '04:00:00' as close_time
union select 'MEDIA CITY' as location, 'Fri' as day, '11:00:00' as open_time, '04:00:00' as close_time
union select 'MEDIA CITY' as location, 'Sat' as day, '11:00:00' as open_time, '04:00:00' as close_time
union select 'MEDIA CITY' as location, 'Sun' as day, '11:00:00' as open_time, '04:00:00' as close_time
union select 'Mirdiff SK' as location, 'Mon' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Mirdiff SK' as location, 'Tue' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Mirdiff SK' as location, 'Wed' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Mirdiff SK' as location, 'Thu' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Mirdiff SK' as location, 'Fri' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Mirdiff SK' as location, 'Sat' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Mirdiff SK' as location, 'Sun' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'MOTOR CITY 3' as location, 'Mon' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'MOTOR CITY 3' as location, 'Tue' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'MOTOR CITY 3' as location, 'Wed' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'MOTOR CITY 3' as location, 'Thu' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'MOTOR CITY 3' as location, 'Fri' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'MOTOR CITY 3' as location, 'Sat' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'MOTOR CITY 3' as location, 'Sun' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'MUSSAFAH' as location, 'Mon' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'MUSSAFAH' as location, 'Tue' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'MUSSAFAH' as location, 'Wed' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'MUSSAFAH' as location, 'Thu' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'MUSSAFAH' as location, 'Fri' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'MUSSAFAH' as location, 'Sat' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'MUSSAFAH' as location, 'Sun' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'OF Dan plaza' as location, 'Mon' as day, '06:00:00' as open_time, '18:00:00' as close_time
union select 'OF Dan plaza' as location, 'Tue' as day, '06:00:00' as open_time, '18:00:00' as close_time
union select 'OF Dan plaza' as location, 'Wed' as day, '06:00:00' as open_time, '18:00:00' as close_time
union select 'OF Dan plaza' as location, 'Thu' as day, '06:00:00' as open_time, '18:00:00' as close_time
union select 'OF Dan plaza' as location, 'Fri' as day, '06:00:00' as open_time, '18:00:00' as close_time
union select 'OF Dan plaza' as location, 'Sat' as day, '06:00:00' as open_time, '18:00:00' as close_time
union select 'OF Dan plaza' as location, 'Sun' as day, '06:00:00' as open_time, '18:00:00' as close_time
union select 'OF IMPZ' as location, 'Mon' as day, '10:00:00' as open_time, '09:59:59' as close_time
union select 'OF IMPZ' as location, 'Tue' as day, '10:00:00' as open_time, '09:59:59' as close_time
union select 'OF IMPZ' as location, 'Wed' as day, '10:00:00' as open_time, '09:59:59' as close_time
union select 'OF IMPZ' as location, 'Thu' as day, '10:00:00' as open_time, '09:59:59' as close_time
union select 'OF IMPZ' as location, 'Fri' as day, '10:00:00' as open_time, '09:59:59' as close_time
union select 'OF IMPZ' as location, 'Sat' as day, '10:00:00' as open_time, '09:59:59' as close_time
union select 'OF IMPZ' as location, 'Sun' as day, '10:00:00' as open_time, '09:59:59' as close_time   
union select 'OF Joy Avenue' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'OF Joy Avenue' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'OF Joy Avenue' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'OF Joy Avenue' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'OF Joy Avenue' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'OF Joy Avenue' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'OF Joy Avenue' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Of Riyadh Park' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Of Riyadh Park' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Of Riyadh Park' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Of Riyadh Park' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Of Riyadh Park' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Of Riyadh Park' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Of Riyadh Park' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'OF: Al Danah' as location, 'Mon' as day, '07:00:00' as open_time, '04:00:00' as close_time
union select 'OF: Al Danah' as location, 'Tue' as day, '07:00:00' as open_time, '04:00:00' as close_time
union select 'OF: Al Danah' as location, 'Wed' as day, '07:00:00' as open_time, '04:00:00' as close_time
union select 'OF: Al Danah' as location, 'Thu' as day, '07:00:00' as open_time, '04:00:00' as close_time
union select 'OF: Al Danah' as location, 'Fri' as day, '07:00:00' as open_time, '04:00:00' as close_time
union select 'OF: Al Danah' as location, 'Sat' as day, '07:00:00' as open_time, '04:00:00' as close_time
union select 'OF: Al Danah' as location, 'Sun' as day, '07:00:00' as open_time, '04:00:00' as close_time
union select 'OF: Boulevard' as location, 'Mon' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Boulevard' as location, 'Tue' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Boulevard' as location, 'Wed' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Boulevard' as location, 'Thu' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Boulevard' as location, 'Fri' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Boulevard' as location, 'Sat' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Boulevard' as location, 'Sun' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Eppco' as location, 'Mon' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'OF: Eppco' as location, 'Tue' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'OF: Eppco' as location, 'Wed' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'OF: Eppco' as location, 'Thu' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'OF: Eppco' as location, 'Fri' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'OF: Eppco' as location, 'Sat' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'OF: Eppco' as location, 'Sun' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'OF: JBR' as location, 'Mon' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'OF: JBR' as location, 'Tue' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'OF: JBR' as location, 'Wed' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'OF: JBR' as location, 'Thu' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'OF: JBR' as location, 'Fri' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'OF: JBR' as location, 'Sat' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'OF: JBR' as location, 'Sun' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Media City' as location, 'Mon' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Media City' as location, 'Tue' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Media City' as location, 'Wed' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Media City' as location, 'Thu' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Media City' as location, 'Fri' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Media City' as location, 'Sat' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Media City' as location, 'Sun' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Motor City' as location, 'Mon' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Motor City' as location, 'Tue' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Motor City' as location, 'Wed' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Motor City' as location, 'Thu' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Motor City' as location, 'Fri' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Motor City' as location, 'Sat' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'OF: Motor City' as location, 'Sun' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'OF:Dubai Hills' as location, 'Mon' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'OF:Dubai Hills' as location, 'Tue' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'OF:Dubai Hills' as location, 'Wed' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'OF:Dubai Hills' as location, 'Thu' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'OF:Dubai Hills' as location, 'Fri' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'OF:Dubai Hills' as location, 'Sat' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'OF:Dubai Hills' as location, 'Sun' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'OF:Festival City' as location, 'Mon' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'OF:Festival City' as location, 'Tue' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'OF:Festival City' as location, 'Wed' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'OF:Festival City' as location, 'Thu' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'OF:Festival City' as location, 'Fri' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'OF:Festival City' as location, 'Sat' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'OF:Festival City' as location, 'Sun' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'OF:Outlet Village' as location, 'Mon' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'OF:Outlet Village' as location, 'Tue' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'OF:Outlet Village' as location, 'Wed' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'OF:Outlet Village' as location, 'Thu' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'OF:Outlet Village' as location, 'Fri' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'OF:Outlet Village' as location, 'Sat' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'OF:Outlet Village' as location, 'Sun' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'OF:Shakboot' as location, 'Mon' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'OF:Shakboot' as location, 'Tue' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'OF:Shakboot' as location, 'Wed' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'OF:Shakboot' as location, 'Thu' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'OF:Shakboot' as location, 'Fri' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'OF:Shakboot' as location, 'Sat' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'OF:Shakboot' as location, 'Sun' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'Operation Falafel Galleria' as location, 'Mon' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Operation Falafel Galleria' as location, 'Tue' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Operation Falafel Galleria' as location, 'Wed' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Operation Falafel Galleria' as location, 'Thu' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Operation Falafel Galleria' as location, 'Fri' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Operation Falafel Galleria' as location, 'Sat' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Operation Falafel Galleria' as location, 'Sun' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Pizzaro Al Barsha' as location, 'Mon' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Al Barsha' as location, 'Tue' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Al Barsha' as location, 'Wed' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Al Barsha' as location, 'Thu' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Al Barsha' as location, 'Fri' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Al Barsha' as location, 'Sat' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Al Barsha' as location, 'Sun' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Al Shaab' as location, 'Mon' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Pizzaro Al Shaab' as location, 'Tue' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Pizzaro Al Shaab' as location, 'Wed' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Pizzaro Al Shaab' as location, 'Thu' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Pizzaro Al Shaab' as location, 'Fri' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Pizzaro Al Shaab' as location, 'Sat' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Pizzaro Al Shaab' as location, 'Sun' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Pizzaro Arjan' as location, 'Mon' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Arjan' as location, 'Tue' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Arjan' as location, 'Wed' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Arjan' as location, 'Thu' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Arjan' as location, 'Fri' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Arjan' as location, 'Sat' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Arjan' as location, 'Sun' as day, '11:00:00' as open_time, '03:45:00' as close_time 
union select 'Pizzaro DHK Ajman' as location, 'Mon' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro DHK Ajman' as location, 'Tue' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro DHK Ajman' as location, 'Wed' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro DHK Ajman' as location, 'Thu' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro DHK Ajman' as location, 'Fri' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro DHK Ajman' as location, 'Sat' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro DHK Ajman' as location, 'Sun' as day, '11:00:00' as open_time, '01:00:00' as close_time 
union select 'PIzzaro DHK RAK' as location, 'Mon' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'PIzzaro DHK RAK' as location, 'Tue' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'PIzzaro DHK RAK' as location, 'Wed' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'PIzzaro DHK RAK' as location, 'Thu' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'PIzzaro DHK RAK' as location, 'Fri' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'PIzzaro DHK RAK' as location, 'Sat' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'PIzzaro DHK RAK' as location, 'Sun' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro Emirates zoo' as location, 'Mon' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'Pizzaro Emirates zoo' as location, 'Tue' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'Pizzaro Emirates zoo' as location, 'Wed' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'Pizzaro Emirates zoo' as location, 'Thu' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'Pizzaro Emirates zoo' as location, 'Fri' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'Pizzaro Emirates zoo' as location, 'Sat' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'Pizzaro Emirates zoo' as location, 'Sun' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'Pizzaro Khalifa City' as location, 'Mon' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Khalifa City' as location, 'Tue' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Khalifa City' as location, 'Wed' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Khalifa City' as location, 'Thu' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Khalifa City' as location, 'Fri' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Khalifa City' as location, 'Sat' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro Khalifa City' as location, 'Sun' as day, '11:00:00' as open_time, '03:45:00' as close_time
union select 'Pizzaro KP AlQuoz' as location, 'Mon' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro KP AlQuoz' as location, 'Tue' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro KP AlQuoz' as location, 'Wed' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro KP AlQuoz' as location, 'Thu' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro KP AlQuoz' as location, 'Fri' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro KP AlQuoz' as location, 'Sat' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro KP AlQuoz' as location, 'Sun' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro Shakhbout' as location, 'Mon' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro Shakhbout' as location, 'Tue' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro Shakhbout' as location, 'Wed' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro Shakhbout' as location, 'Thu' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro Shakhbout' as location, 'Fri' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro Shakhbout' as location, 'Sat' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Pizzaro Shakhbout' as location, 'Sun' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Poke Poke Gate Avenue' as location, 'Mon' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Poke Poke Gate Avenue' as location, 'Tue' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Poke Poke Gate Avenue' as location, 'Wed' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Poke Poke Gate Avenue' as location, 'Thu' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Poke Poke Gate Avenue' as location, 'Fri' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Poke Poke Gate Avenue' as location, 'Sat' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Poke Poke Gate Avenue' as location, 'Sun' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Poke Poke Jumeirah Street' as location, 'Mon' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Poke Poke Jumeirah Street' as location, 'Tue' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Poke Poke Jumeirah Street' as location, 'Wed' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Poke Poke Jumeirah Street' as location, 'Thu' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Poke Poke Jumeirah Street' as location, 'Fri' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Poke Poke Jumeirah Street' as location, 'Sat' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'Poke Poke Jumeirah Street' as location, 'Sun' as day, '10:00:00' as open_time, '23:59:59' as close_time
union select 'QAR - Lagoona Mall' as location, 'Mon' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'QAR - Lagoona Mall' as location, 'Tue' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'QAR - Lagoona Mall' as location, 'Wed' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'QAR - Lagoona Mall' as location, 'Thu' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'QAR - Lagoona Mall' as location, 'Fri' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'QAR - Lagoona Mall' as location, 'Sat' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'QAR - Lagoona Mall' as location, 'Sun' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'QAR CK1' as location, 'Mon' as day, '09:00:00' as open_time, '19:00:00' as close_time
union select 'QAR CK1' as location, 'Tue' as day, '09:00:00' as open_time, '19:00:00' as close_time
union select 'QAR CK1' as location, 'Wed' as day, '09:00:00' as open_time, '19:00:00' as close_time
union select 'QAR CK1' as location, 'Thu' as day, '09:00:00' as open_time, '19:00:00' as close_time
union select 'QAR CK1' as location, 'Fri' as day, '09:00:00' as open_time, '19:00:00' as close_time
union select 'QAR CK1' as location, 'Sat' as day, '09:00:00' as open_time, '19:00:00' as close_time
union select 'QAR CK1' as location, 'Sun' as day, '09:00:00' as open_time, '19:00:00' as close_time
union select 'Qatar Warehouse' as location, 'Mon' as day, '06:00:00' as open_time, '16:00:00' as close_time
union select 'Qatar Warehouse' as location, 'Tue' as day, '06:00:00' as open_time, '16:00:00' as close_time
union select 'Qatar Warehouse' as location, 'Wed' as day, '06:00:00' as open_time, '16:00:00' as close_time
union select 'Qatar Warehouse' as location, 'Thu' as day, '06:00:00' as open_time, '16:00:00' as close_time
union select 'Qatar Warehouse' as location, 'Sat' as day, '06:00:00' as open_time, '16:00:00' as close_time
union select 'Qatar Warehouse' as location, 'Sun' as day, '06:00:00' as open_time, '16:00:00' as close_time
union select 'QNCC SK' as location, 'Mon' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'QNCC SK' as location, 'Tue' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'QNCC SK' as location, 'Wed' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'QNCC SK' as location, 'Thu' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'QNCC SK' as location, 'Sat' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'QNCC SK' as location, 'Sun' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'QURTUBAH SK' as location, 'Mon' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'QURTUBAH SK' as location, 'Tue' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'QURTUBAH SK' as location, 'Wed' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'QURTUBAH SK' as location, 'Thu' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'QURTUBAH SK' as location, 'Fri' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'QURTUBAH SK' as location, 'Sat' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'QURTUBAH SK' as location, 'Sun' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'RB DHK Sharjah' as location, 'Mon' as day, '11:00:00' as open_time, '00:10:00' as close_time
union select 'RB DHK Sharjah' as location, 'Tue' as day, '11:00:00' as open_time, '00:10:00' as close_time
union select 'RB DHK Sharjah' as location, 'Wed' as day, '11:00:00' as open_time, '00:10:00' as close_time
union select 'RB DHK Sharjah' as location, 'Thu' as day, '11:00:00' as open_time, '00:10:00' as close_time
union select 'RB DHK Sharjah' as location, 'Fri' as day, '11:00:00' as open_time, '00:10:00' as close_time
union select 'RB DHK Sharjah' as location, 'Sat' as day, '11:00:00' as open_time, '00:10:00' as close_time
union select 'RB DHK Sharjah' as location, 'Sun' as day, '11:00:00' as open_time, '00:10:00' as close_time   
union select 'Retro Beach JBR' as location, 'Mon' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Retro Beach JBR' as location, 'Tue' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Retro Beach JBR' as location, 'Wed' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Retro Beach JBR' as location, 'Thu' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Retro Beach JBR' as location, 'Fri' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Retro Beach JBR' as location, 'Sat' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Retro Beach JBR' as location, 'Sun' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'RHS Khairan' as location, 'Mon' as day, '15:00:00' as open_time, '04:00:00' as close_time
union select 'RHS Khairan' as location, 'Tue' as day, '15:00:00' as open_time, '04:00:00' as close_time
union select 'RHS Khairan' as location, 'Wed' as day, '15:00:00' as open_time, '04:00:00' as close_time
union select 'RHS Khairan' as location, 'Thu' as day, '15:00:00' as open_time, '04:00:00' as close_time
union select 'RHS Khairan' as location, 'Fri' as day, '15:00:00' as open_time, '04:00:00' as close_time
union select 'RHS Khairan' as location, 'Sat' as day, '15:00:00' as open_time, '04:00:00' as close_time
union select 'RHS Khairan' as location, 'Sun' as day, '15:00:00' as open_time, '04:00:00' as close_time
union select 'Right Bite DIFC' as location, 'Mon' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Right Bite DIFC' as location, 'Tue' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Right Bite DIFC' as location, 'Wed' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Right Bite DIFC' as location, 'Thu' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Right Bite DIFC' as location, 'Fri' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Right Bite DIFC' as location, 'Sat' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Right Bite DIFC' as location, 'Sun' as day, '08:00:00' as open_time, '22:00:00' as close_time
union select 'Right Bite VISA HQ' as location, 'Mon' as day, '07:00:00' as open_time, '17:00:00' as close_time
union select 'Right Bite VISA HQ' as location, 'Tue' as day, '07:00:00' as open_time, '17:00:00' as close_time
union select 'Right Bite VISA HQ' as location, 'Wed' as day, '07:00:00' as open_time, '17:00:00' as close_time
union select 'Right Bite VISA HQ' as location, 'Thu' as day, '07:00:00' as open_time, '17:00:00' as close_time
union select 'Right Bite VISA HQ' as location, 'Fri' as day, '07:00:00' as open_time, '17:00:00' as close_time
union select 'Right Bite VISA HQ' as location, 'Sat' as day, '07:00:00' as open_time, '17:00:00' as close_time
union select 'Right Bite VISA HQ' as location, 'Sun' as day, '07:00:00' as open_time, '17:00:00' as close_time
union select 'Ripe market Container' as location, 'Mon' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Ripe market Container' as location, 'Tue' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Ripe market Container' as location, 'Wed' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Ripe market Container' as location, 'Thu' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Ripe market Container' as location, 'Fri' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Ripe market Container' as location, 'Sat' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Ripe market Container' as location, 'Sun' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Riyadh Warehouse' as location, 'Mon' as day, '10:00:00' as open_time, '16:00:00' as close_time
union select 'Riyadh Warehouse' as location, 'Tue' as day, '10:00:00' as open_time, '16:00:00' as close_time
union select 'Riyadh Warehouse' as location, 'Wed' as day, '10:00:00' as open_time, '16:00:00' as close_time
union select 'Riyadh Warehouse' as location, 'Thu' as day, '10:00:00' as open_time, '16:00:00' as close_time
union select 'Riyadh Warehouse' as location, 'Fri' as day, '10:00:00' as open_time, '16:00:00' as close_time
union select 'Riyadh Warehouse' as location, 'Sat' as day, '10:00:00' as open_time, '16:00:00' as close_time
union select 'Riyadh Warehouse' as location, 'Sun' as day, '10:00:00' as open_time, '16:00:00' as close_time
union select 'SABAH AL SALEM' as location, 'Mon' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'SABAH AL SALEM' as location, 'Tue' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'SABAH AL SALEM' as location, 'Wed' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'SABAH AL SALEM' as location, 'Thu' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'SABAH AL SALEM' as location, 'Fri' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'SABAH AL SALEM' as location, 'Sat' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'SABAH AL SALEM' as location, 'Sun' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'SALMIYA' as location, 'Mon' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'SALMIYA' as location, 'Tue' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'SALMIYA' as location, 'Wed' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'SALMIYA' as location, 'Thu' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'SALMIYA' as location, 'Fri' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'SALMIYA' as location, 'Sat' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'SALMIYA' as location, 'Sun' as day, '12:00:00' as open_time, '23:59:59' as close_time
union select 'SHARJAH 1' as location, 'Mon' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'SHARJAH 1' as location, 'Tue' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'SHARJAH 1' as location, 'Wed' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'SHARJAH 1' as location, 'Thu' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'SHARJAH 1' as location, 'Fri' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'SHARJAH 1' as location, 'Sat' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'SHARJAH 1' as location, 'Sun' as day, '08:00:00' as open_time, '03:00:00' as close_time
union select 'SHARQ' as location, 'Mon' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'SHARQ' as location, 'Tue' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'SHARQ' as location, 'Wed' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'SHARQ' as location, 'Thu' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'SHARQ' as location, 'Fri' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'SHARQ' as location, 'Sat' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'SHARQ' as location, 'Sun' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak Andalus mall' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Andalus mall' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Andalus mall' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Andalus mall' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Andalus mall' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Andalus mall' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Andalus mall' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak JView' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak JView' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak JView' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak JView' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak JView' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak JView' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak JView' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Panoramamall' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Panoramamall' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Panoramamall' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Panoramamall' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Panoramamall' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Panoramamall' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Panoramamall' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Riyadh Park' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Riyadh Park' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Riyadh Park' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Riyadh Park' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Riyadh Park' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Riyadh Park' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Riyadh Park' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Shobak Warehouse' as location, 'Mon' as day, '07:30:00' as open_time, '23:00:00' as close_time
union select 'Shobak Warehouse' as location, 'Tue' as day, '07:30:00' as open_time, '23:00:00' as close_time
union select 'Shobak Warehouse' as location, 'Wed' as day, '07:30:00' as open_time, '23:00:00' as close_time
union select 'Shobak Warehouse' as location, 'Thu' as day, '07:30:00' as open_time, '23:00:00' as close_time
union select 'Shobak Warehouse' as location, 'Sat' as day, '07:30:00' as open_time, '23:00:00' as close_time
union select 'Shobak Warehouse' as location, 'Sun' as day, '07:30:00' as open_time, '23:00:00' as close_time
union select 'Shobak Yasmin' as location, 'Mon' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak Yasmin' as location, 'Tue' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak Yasmin' as location, 'Wed' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak Yasmin' as location, 'Thu' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak Yasmin' as location, 'Fri' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak Yasmin' as location, 'Sat' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak Yasmin' as location, 'Sun' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak-Arab Mall' as location, 'Mon' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Arab Mall' as location, 'Tue' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Arab Mall' as location, 'Wed' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Arab Mall' as location, 'Thu' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Arab Mall' as location, 'Fri' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Arab Mall' as location, 'Sat' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Arab Mall' as location, 'Sun' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Awali' as location, 'Mon' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak-Awali' as location, 'Tue' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak-Awali' as location, 'Wed' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak-Awali' as location, 'Thu' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak-Awali' as location, 'Fri' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak-Awali' as location, 'Sat' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak-Awali' as location, 'Sun' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak-Aziz Mall' as location, 'Mon' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Aziz Mall' as location, 'Tue' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Aziz Mall' as location, 'Wed' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Aziz Mall' as location, 'Thu' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Aziz Mall' as location, 'Fri' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Aziz Mall' as location, 'Sat' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Aziz Mall' as location, 'Sun' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-CPP' as location, 'Mon' as day, '07:30:00' as open_time, '21:00:00' as close_time
union select 'Shobak-CPP' as location, 'Tue' as day, '07:30:00' as open_time, '21:00:00' as close_time
union select 'Shobak-CPP' as location, 'Wed' as day, '07:30:00' as open_time, '21:00:00' as close_time
union select 'Shobak-CPP' as location, 'Thu' as day, '07:30:00' as open_time, '21:00:00' as close_time
union select 'Shobak-CPP' as location, 'Sat' as day, '07:30:00' as open_time, '21:00:00' as close_time
union select 'Shobak-CPP' as location, 'Sun' as day, '07:30:00' as open_time, '21:00:00' as close_time
union select 'Shobak-Hamadaniah' as location, 'Mon' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Hamadaniah' as location, 'Tue' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Hamadaniah' as location, 'Wed' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Hamadaniah' as location, 'Thu' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Hamadaniah' as location, 'Fri' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Hamadaniah' as location, 'Sat' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Hamadaniah' as location, 'Sun' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Hera' as location, 'Mon' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Hera' as location, 'Tue' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Hera' as location, 'Wed' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Hera' as location, 'Thu' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Hera' as location, 'Fri' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Hera' as location, 'Sat' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Hera' as location, 'Sun' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-King''s Road' as location, 'Mon' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-King''s Road' as location, 'Tue' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-King''s Road' as location, 'Wed' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-King''s Road' as location, 'Thu' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-King''s Road' as location, 'Fri' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-King''s Road' as location, 'Sat' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-King''s Road' as location, 'Sun' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Makkah Mall' as location, 'Mon' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Makkah Mall' as location, 'Tue' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Makkah Mall' as location, 'Wed' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Makkah Mall' as location, 'Thu' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Makkah Mall' as location, 'Fri' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Makkah Mall' as location, 'Sat' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Makkah Mall' as location, 'Sun' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Mamsha' as location, 'Mon' as day, '14:30:00' as open_time, '01:30:00' as close_time
union select 'Shobak-Mamsha' as location, 'Tue' as day, '14:30:00' as open_time, '01:30:00' as close_time
union select 'Shobak-Mamsha' as location, 'Wed' as day, '14:30:00' as open_time, '01:30:00' as close_time
union select 'Shobak-Mamsha' as location, 'Thu' as day, '14:30:00' as open_time, '01:30:00' as close_time
union select 'Shobak-Mamsha' as location, 'Fri' as day, '14:30:00' as open_time, '01:30:00' as close_time
union select 'Shobak-Mamsha' as location, 'Sat' as day, '14:30:00' as open_time, '01:30:00' as close_time
union select 'Shobak-Mamsha' as location, 'Sun' as day, '14:30:00' as open_time, '01:30:00' as close_time
union select 'Shobak-Obhur' as location, 'Mon' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Obhur' as location, 'Tue' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Obhur' as location, 'Wed' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Obhur' as location, 'Thu' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Obhur' as location, 'Fri' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Obhur' as location, 'Sat' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Obhur' as location, 'Sun' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Rawdah' as location, 'Mon' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'Shobak-Rawdah' as location, 'Tue' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'Shobak-Rawdah' as location, 'Wed' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'Shobak-Rawdah' as location, 'Thu' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'Shobak-Rawdah' as location, 'Fri' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'Shobak-Rawdah' as location, 'Sat' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'Shobak-Rawdah' as location, 'Sun' as day, '08:00:00' as open_time, '01:30:00' as close_time
union select 'Shobak-Red Sea Mall' as location, 'Mon' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Red Sea Mall' as location, 'Tue' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Red Sea Mall' as location, 'Wed' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Red Sea Mall' as location, 'Thu' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Red Sea Mall' as location, 'Fri' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Red Sea Mall' as location, 'Sat' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Red Sea Mall' as location, 'Sun' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Salam Mall' as location, 'Mon' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Salam Mall' as location, 'Tue' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Salam Mall' as location, 'Wed' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Salam Mall' as location, 'Thu' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Salam Mall' as location, 'Fri' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Salam Mall' as location, 'Sat' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Salam Mall' as location, 'Sun' as day, '09:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Shawgiyah' as location, 'Mon' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak-Shawgiyah' as location, 'Tue' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak-Shawgiyah' as location, 'Wed' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak-Shawgiyah' as location, 'Thu' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak-Shawgiyah' as location, 'Fri' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak-Shawgiyah' as location, 'Sat' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak-Shawgiyah' as location, 'Sun' as day, '14:30:00' as open_time, '01:00:00' as close_time
union select 'Shobak-Tera Mall' as location, 'Mon' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Tera Mall' as location, 'Tue' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Tera Mall' as location, 'Wed' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Tera Mall' as location, 'Thu' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Tera Mall' as location, 'Fri' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Tera Mall' as location, 'Sat' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Tera Mall' as location, 'Sun' as day, '14:30:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Zahra' as location, 'Mon' as day, '06:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Zahra' as location, 'Tue' as day, '06:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Zahra' as location, 'Wed' as day, '06:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Zahra' as location, 'Thu' as day, '06:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Zahra' as location, 'Fri' as day, '06:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Zahra' as location, 'Sat' as day, '06:00:00' as open_time, '23:59:59' as close_time
union select 'Shobak-Zahra' as location, 'Sun' as day, '06:00:00' as open_time, '23:59:59' as close_time
union select 'SHUHADA' as location, 'Mon' as day, '12:00:00' as open_time, '04:00:00' as close_time
union select 'SHUHADA' as location, 'Tue' as day, '12:00:00' as open_time, '04:00:00' as close_time
union select 'SHUHADA' as location, 'Wed' as day, '12:00:00' as open_time, '04:00:00' as close_time
union select 'SHUHADA' as location, 'Thu' as day, '12:00:00' as open_time, '04:00:00' as close_time
union select 'SHUHADA' as location, 'Fri' as day, '12:00:00' as open_time, '04:00:00' as close_time
union select 'SHUHADA' as location, 'Sat' as day, '12:00:00' as open_time, '04:00:00' as close_time
union select 'SHUHADA' as location, 'Sun' as day, '12:00:00' as open_time, '04:00:00' as close_time
union select 'SK - Aziziya' as location, 'Mon' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Aziziya' as location, 'Tue' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Aziziya' as location, 'Wed' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Aziziya' as location, 'Thu' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Aziziya' as location, 'Fri' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Aziziya' as location, 'Sat' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Aziziya' as location, 'Sun' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Bin Omran' as location, 'Mon' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Bin Omran' as location, 'Tue' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Bin Omran' as location, 'Wed' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Bin Omran' as location, 'Thu' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Bin Omran' as location, 'Fri' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Bin Omran' as location, 'Sat' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Bin Omran' as location, 'Sun' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Umm Salal' as location, 'Mon' as day, '15:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Umm Salal' as location, 'Tue' as day, '15:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Umm Salal' as location, 'Wed' as day, '15:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Umm Salal' as location, 'Thu' as day, '15:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Umm Salal' as location, 'Fri' as day, '15:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Umm Salal' as location, 'Sat' as day, '15:00:00' as open_time, '03:00:00' as close_time
union select 'SK - Umm Salal' as location, 'Sun' as day, '15:00:00' as open_time, '03:00:00' as close_time
union select 'SK Foxhill JR' as location, 'Mon' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'SK Foxhill JR' as location, 'Tue' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'SK Foxhill JR' as location, 'Wed' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'SK Foxhill JR' as location, 'Thu' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'SK Foxhill JR' as location, 'Fri' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'SK Foxhill JR' as location, 'Sat' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'SK Foxhill JR' as location, 'Sun' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'SK-Warood Kitopi' as location, 'Mon' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'SK-Warood Kitopi' as location, 'Tue' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'SK-Warood Kitopi' as location, 'Wed' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'SK-Warood Kitopi' as location, 'Thu' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'SK-Warood Kitopi' as location, 'Fri' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'SK-Warood Kitopi' as location, 'Sat' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'SK-Warood Kitopi' as location, 'Sun' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Smoky beach JBR' as location, 'Mon' as day, '16:00:00' as open_time, '05:00:00' as close_time
union select 'Smoky beach JBR' as location, 'Tue' as day, '16:00:00' as open_time, '05:00:00' as close_time
union select 'Smoky beach JBR' as location, 'Wed' as day, '16:00:00' as open_time, '05:00:00' as close_time
union select 'Smoky beach JBR' as location, 'Thu' as day, '16:00:00' as open_time, '05:00:00' as close_time
union select 'Smoky beach JBR' as location, 'Fri' as day, '16:00:00' as open_time, '05:00:00' as close_time
union select 'Smoky beach JBR' as location, 'Sat' as day, '16:00:00' as open_time, '05:00:00' as close_time
union select 'Smoky beach JBR' as location, 'Sun' as day, '16:00:00' as open_time, '05:00:00' as close_time
union select 'Smoky Palm beach' as location, 'Mon' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'Smoky Palm beach' as location, 'Tue' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'Smoky Palm beach' as location, 'Wed' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'Smoky Palm beach' as location, 'Thu' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'Smoky Palm beach' as location, 'Fri' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'Smoky Palm beach' as location, 'Sat' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'Smoky Palm beach' as location, 'Sun' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'SPICE SAHAFA' as location, 'Mon' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'SPICE SAHAFA' as location, 'Tue' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'SPICE SAHAFA' as location, 'Wed' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'SPICE SAHAFA' as location, 'Thu' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'SPICE SAHAFA' as location, 'Fri' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'SPICE SAHAFA' as location, 'Sat' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'SPICE SAHAFA' as location, 'Sun' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Sushi Counter New York University' as location, 'Mon' as day, '11:00:00' as open_time, '22:00:00' as close_time
union select 'Sushi Counter New York University' as location, 'Tue' as day, '11:00:00' as open_time, '22:00:00' as close_time
union select 'Sushi Counter New York University' as location, 'Wed' as day, '11:00:00' as open_time, '22:00:00' as close_time
union select 'Sushi Counter New York University' as location, 'Thu' as day, '11:00:00' as open_time, '22:00:00' as close_time
union select 'Sushi Counter New York University' as location, 'Fri' as day, '11:00:00' as open_time, '22:00:00' as close_time
union select 'Sushi Counter New York University' as location, 'Sat' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'Sushi Counter New York University' as location, 'Sun' as day, '11:00:00' as open_time, '23:00:00' as close_time
union select 'SushiDo Business Bay' as location, 'Mon' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Business Bay' as location, 'Tue' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Business Bay' as location, 'Wed' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Business Bay' as location, 'Thu' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Business Bay' as location, 'Fri' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Business Bay' as location, 'Sat' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Business Bay' as location, 'Sun' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo JLT' as location, 'Mon' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo JLT' as location, 'Tue' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo JLT' as location, 'Wed' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo JLT' as location, 'Thu' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo JLT' as location, 'Fri' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo JLT' as location, 'Sat' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo JLT' as location, 'Sun' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Motor City' as location, 'Mon' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Motor City' as location, 'Tue' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Motor City' as location, 'Wed' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Motor City' as location, 'Thu' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Motor City' as location, 'Fri' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Motor City' as location, 'Sat' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Motor City' as location, 'Sun' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Rashidiya' as location, 'Mon' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Rashidiya' as location, 'Tue' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Rashidiya' as location, 'Wed' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Rashidiya' as location, 'Thu' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Rashidiya' as location, 'Fri' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Rashidiya' as location, 'Sat' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SushiDo Rashidiya' as location, 'Sun' as day, '11:00:00' as open_time, '02:00:00' as close_time
union select 'SUWAIDI' as location, 'Mon' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'SUWAIDI' as location, 'Tue' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'SUWAIDI' as location, 'Wed' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'SUWAIDI' as location, 'Thu' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'SUWAIDI' as location, 'Fri' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'SUWAIDI' as location, 'Sat' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'SUWAIDI' as location, 'Sun' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado Arabian Ranches 3' as location, 'Mon' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Arabian Ranches 3' as location, 'Tue' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Arabian Ranches 3' as location, 'Wed' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Arabian Ranches 3' as location, 'Thu' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Arabian Ranches 3' as location, 'Fri' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Arabian Ranches 3' as location, 'Sat' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Arabian Ranches 3' as location, 'Sun' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Business Bay' as location, 'Mon' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Business Bay' as location, 'Tue' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Business Bay' as location, 'Wed' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Business Bay' as location, 'Thu' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Business Bay' as location, 'Fri' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Business Bay' as location, 'Sat' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Business Bay' as location, 'Sun' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Dubai Hills' as location, 'Mon' as day, '10:00:00' as open_time, '21:00:00' as close_time
union select 'Taqado Dubai Hills' as location, 'Tue' as day, '10:00:00' as open_time, '21:00:00' as close_time
union select 'Taqado Dubai Hills' as location, 'Wed' as day, '10:00:00' as open_time, '21:00:00' as close_time
union select 'Taqado Dubai Hills' as location, 'Thu' as day, '10:00:00' as open_time, '21:00:00' as close_time
union select 'Taqado Dubai Hills' as location, 'Fri' as day, '10:00:00' as open_time, '21:00:00' as close_time
union select 'Taqado Dubai Hills' as location, 'Sat' as day, '10:00:00' as open_time, '21:00:00' as close_time
union select 'Taqado Dubai Hills' as location, 'Sun' as day, '10:00:00' as open_time, '21:00:00' as close_time
union select 'Taqado Dubai Mall' as location, 'Mon' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado Dubai Mall' as location, 'Tue' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado Dubai Mall' as location, 'Wed' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado Dubai Mall' as location, 'Thu' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado Dubai Mall' as location, 'Fri' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado Dubai Mall' as location, 'Sat' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado Dubai Mall' as location, 'Sun' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado Granada Mall' as location, 'Mon' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Granada Mall' as location, 'Tue' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Granada Mall' as location, 'Wed' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Granada Mall' as location, 'Thu' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Granada Mall' as location, 'Fri' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Granada Mall' as location, 'Sat' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Granada Mall' as location, 'Sun' as day, '16:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Hitteen Square' as location, 'Mon' as day, '16:00:00' as open_time, '04:00:00' as close_time
union select 'Taqado Hitteen Square' as location, 'Tue' as day, '16:00:00' as open_time, '04:00:00' as close_time
union select 'Taqado Hitteen Square' as location, 'Wed' as day, '16:00:00' as open_time, '04:00:00' as close_time
union select 'Taqado Hitteen Square' as location, 'Thu' as day, '16:00:00' as open_time, '04:00:00' as close_time
union select 'Taqado Hitteen Square' as location, 'Fri' as day, '16:00:00' as open_time, '04:00:00' as close_time
union select 'Taqado Hitteen Square' as location, 'Sat' as day, '16:00:00' as open_time, '04:00:00' as close_time
union select 'Taqado Hitteen Square' as location, 'Sun' as day, '16:00:00' as open_time, '04:00:00' as close_time
union select 'Taqado Irise' as location, 'Mon' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Irise' as location, 'Tue' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Irise' as location, 'Wed' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Irise' as location, 'Thu' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Irise' as location, 'Fri' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Irise' as location, 'Sat' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Irise' as location, 'Sun' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Kite Beach' as location, 'Mon' as day, '13:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Kite Beach' as location, 'Tue' as day, '13:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Kite Beach' as location, 'Wed' as day, '13:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Kite Beach' as location, 'Thu' as day, '13:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Kite Beach' as location, 'Fri' as day, '13:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Kite Beach' as location, 'Sat' as day, '13:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Kite Beach' as location, 'Sun' as day, '13:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado KP Diera' as location, 'Mon' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado KP Diera' as location, 'Tue' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado KP Diera' as location, 'Wed' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado KP Diera' as location, 'Thu' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado KP Diera' as location, 'Fri' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado KP Diera' as location, 'Sat' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado KP Diera' as location, 'Sun' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado Media City' as location, 'Mon' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Taqado Media City' as location, 'Tue' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Taqado Media City' as location, 'Wed' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Taqado Media City' as location, 'Thu' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Taqado Media City' as location, 'Fri' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Taqado Media City' as location, 'Sat' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Taqado Media City' as location, 'Sun' as day, '08:00:00' as open_time, '23:00:00' as close_time
union select 'Taqado MOE' as location, 'Mon' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado MOE' as location, 'Tue' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado MOE' as location, 'Wed' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado MOE' as location, 'Thu' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado MOE' as location, 'Fri' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado MOE' as location, 'Sat' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado MOE' as location, 'Sun' as day, '10:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado Studio City' as location, 'Mon' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Studio City' as location, 'Tue' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Studio City' as location, 'Wed' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Studio City' as location, 'Thu' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Studio City' as location, 'Fri' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Studio City' as location, 'Sat' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Studio City' as location, 'Sun' as day, '08:00:00' as open_time, '23:59:59' as close_time
union select 'Taqado Townsquare' as location, 'Mon' as day, '12:00:00' as open_time, '23:30:00' as close_time
union select 'Taqado Townsquare' as location, 'Tue' as day, '12:00:00' as open_time, '23:30:00' as close_time
union select 'Taqado Townsquare' as location, 'Wed' as day, '12:00:00' as open_time, '23:30:00' as close_time
union select 'Taqado Townsquare' as location, 'Thu' as day, '12:00:00' as open_time, '23:30:00' as close_time
union select 'Taqado Townsquare' as location, 'Fri' as day, '12:00:00' as open_time, '23:30:00' as close_time
union select 'Taqado Townsquare' as location, 'Sat' as day, '12:00:00' as open_time, '23:30:00' as close_time
union select 'Taqado Townsquare' as location, 'Sun' as day, '12:00:00' as open_time, '23:30:00' as close_time
union select 'Taqado Yarmouk' as location, 'Mon' as day, '16:00:00' as open_time, '04:00:00' as close_time
union select 'Taqado Yarmouk' as location, 'Tue' as day, '16:00:00' as open_time, '04:00:00' as close_time
union select 'Taqado Yarmouk' as location, 'Wed' as day, '16:00:00' as open_time, '04:00:00' as close_time
union select 'Taqado Yarmouk' as location, 'Thu' as day, '16:00:00' as open_time, '04:00:00' as close_time
union select 'Taqado Yarmouk' as location, 'Fri' as day, '16:00:00' as open_time, '04:00:00' as close_time
union select 'Taqado Yarmouk' as location, 'Sat' as day, '16:00:00' as open_time, '04:00:00' as close_time
union select 'Taqado Yarmouk' as location, 'Sun' as day, '16:00:00' as open_time, '04:00:00' as close_time
union select 'Taqado Yas Mall' as location, 'Mon' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Yas Mall' as location, 'Tue' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Yas Mall' as location, 'Wed' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Yas Mall' as location, 'Thu' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Yas Mall' as location, 'Fri' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Yas Mall' as location, 'Sat' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Yas Mall' as location, 'Sun' as day, '10:00:00' as open_time, '22:00:00' as close_time
union select 'Taqado Yasmin' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado Yasmin' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado Yasmin' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado Yasmin' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado Yasmin' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado Yasmin' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Taqado Yasmin' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Thumama SK' as location, 'Mon' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Thumama SK' as location, 'Tue' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Thumama SK' as location, 'Wed' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Thumama SK' as location, 'Thu' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Thumama SK' as location, 'Fri' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Thumama SK' as location, 'Sat' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'Thumama SK' as location, 'Sun' as day, '11:00:00' as open_time, '03:00:00' as close_time
union select 'UAE CK BB' as location, 'Mon' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK BB' as location, 'Tue' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK BB' as location, 'Wed' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK BB' as location, 'Thu' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK BB' as location, 'Fri' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK BB' as location, 'Sat' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK BB' as location, 'Sun' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK1' as location, 'Mon' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK1' as location, 'Tue' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK1' as location, 'Wed' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK1' as location, 'Thu' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK1' as location, 'Fri' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK1' as location, 'Sat' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK1' as location, 'Sun' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK2' as location, 'Mon' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK2' as location, 'Tue' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK2' as location, 'Wed' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK2' as location, 'Thu' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK2' as location, 'Fri' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK2' as location, 'Sat' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK2' as location, 'Sun' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK3' as location, 'Mon' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'UAE CK3' as location, 'Tue' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'UAE CK3' as location, 'Wed' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'UAE CK3' as location, 'Thu' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'UAE CK3' as location, 'Fri' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'UAE CK3' as location, 'Sat' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'UAE CK3' as location, 'Sun' as day, '06:00:00' as open_time, '02:00:00' as close_time
union select 'UAE CK6' as location, 'Mon' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK6' as location, 'Tue' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK6' as location, 'Wed' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK6' as location, 'Thu' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK6' as location, 'Fri' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK6' as location, 'Sat' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE CK6' as location, 'Sun' as day, '00:00:00' as open_time, '23:59:59' as close_time
union select 'UAE Warehouse' as location, 'Mon' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'UAE Warehouse' as location, 'Tue' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'UAE Warehouse' as location, 'Wed' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'UAE Warehouse' as location, 'Thu' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'UAE Warehouse' as location, 'Fri' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'UAE Warehouse' as location, 'Sat' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'UAE Warehouse' as location, 'Sun' as day, '08:00:00' as open_time, '18:00:00' as close_time
union select 'Wakra - QAR' as location, 'Mon' as day, '15:00:00' as open_time, '03:00:00' as close_time
union select 'Wakra - QAR' as location, 'Tue' as day, '15:00:00' as open_time, '03:00:00' as close_time
union select 'Wakra - QAR' as location, 'Wed' as day, '15:00:00' as open_time, '03:00:00' as close_time
union select 'Wakra - QAR' as location, 'Thu' as day, '15:00:00' as open_time, '03:00:00' as close_time
union select 'Wakra - QAR' as location, 'Fri' as day, '15:00:00' as open_time, '03:00:00' as close_time
union select 'Wakra - QAR' as location, 'Sat' as day, '15:00:00' as open_time, '03:00:00' as close_time
union select 'Wakra - QAR' as location, 'Sun' as day, '15:00:00' as open_time, '03:00:00' as close_time
union select 'Wokkong Alaqiq' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Alaqiq' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Alaqiq' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Alaqiq' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Alaqiq' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Alaqiq' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Alaqiq' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Albadiah' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Albadiah' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Albadiah' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Albadiah' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Albadiah' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Albadiah' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Albadiah' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Almaazer' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Almaazer' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Almaazer' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Almaazer' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Almaazer' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Almaazer' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Almaazer' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Arab Mall' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Arab Mall' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Arab Mall' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Arab Mall' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Arab Mall' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Arab Mall' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Arab Mall' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong CK' as location, 'Mon' as day, '09:00:00' as open_time, '21:00:00' as close_time
union select 'Wokkong CK' as location, 'Tue' as day, '09:00:00' as open_time, '21:00:00' as close_time
union select 'Wokkong CK' as location, 'Wed' as day, '09:00:00' as open_time, '21:00:00' as close_time
union select 'Wokkong CK' as location, 'Thu' as day, '09:00:00' as open_time, '21:00:00' as close_time
union select 'Wokkong CK' as location, 'Fri' as day, '09:00:00' as open_time, '21:00:00' as close_time
union select 'Wokkong CK' as location, 'Sat' as day, '09:00:00' as open_time, '21:00:00' as close_time
union select 'Wokkong CK' as location, 'Sun' as day, '09:00:00' as open_time, '21:00:00' as close_time
union select 'Wokkong khobar' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong khobar' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong khobar' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong khobar' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong khobar' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong khobar' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong khobar' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Nuzhah' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Nuzhah' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Nuzhah' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Nuzhah' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Nuzhah' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Nuzhah' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Nuzhah' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Odhur' as location, 'Mon' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Wokkong Odhur' as location, 'Tue' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Wokkong Odhur' as location, 'Wed' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Wokkong Odhur' as location, 'Thu' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Wokkong Odhur' as location, 'Fri' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Wokkong Odhur' as location, 'Sat' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Wokkong Odhur' as location, 'Sun' as day, '16:00:00' as open_time, '02:00:00' as close_time
union select 'Wokkong Rawabi' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Rawabi' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Rawabi' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Rawabi' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Rawabi' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Rawabi' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Rawabi' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Riviera' as location, 'Mon' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Riviera' as location, 'Tue' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Riviera' as location, 'Wed' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Riviera' as location, 'Thu' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Riviera' as location, 'Fri' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Riviera' as location, 'Sat' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Riviera' as location, 'Sun' as day, '11:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Village' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Village' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Village' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Village' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Village' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Village' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Village' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Yarmouk' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Yarmouk' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Yarmouk' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Yarmouk' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Yarmouk' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Yarmouk' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Yarmouk' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Yasmin' as location, 'Mon' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Yasmin' as location, 'Tue' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Yasmin' as location, 'Wed' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Yasmin' as location, 'Thu' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Yasmin' as location, 'Fri' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Yasmin' as location, 'Sat' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Wokkong Yasmin' as location, 'Sun' as day, '16:00:00' as open_time, '01:00:00' as close_time
union select 'Zaroob Al Ain' as location, 'Mon' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Zaroob Al Ain' as location, 'Tue' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Zaroob Al Ain' as location, 'Wed' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Zaroob Al Ain' as location, 'Thu' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Zaroob Al Ain' as location, 'Fri' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'Zaroob Al Ain' as location, 'Sat' as day, '08:00:00' as open_time, '02:00:00' as close_time
union select 'Zaroob Al Ain' as location, 'Sun' as day, '08:00:00' as open_time, '01:00:00' as close_time
union select 'Zaroob DCC' as location, 'Mon' as day, '00:10:00' as open_time, '22:00:00' as close_time
union select 'Zaroob DCC' as location, 'Tue' as day, '00:10:00' as open_time, '22:00:00' as close_time
union select 'Zaroob DCC' as location, 'Wed' as day, '00:10:00' as open_time, '22:00:00' as close_time
union select 'Zaroob DCC' as location, 'Thu' as day,'00:10:00' as open_time, '22:00:00' as close_time
union select 'Zaroob DCC' as location, 'Fri' as day,'00:10:00' as open_time, '22:00:00' as close_time
union select 'Zaroob DCC' as location, 'Sat' as day, '00:10:00' as open_time, '22:00:00' as close_time
union select 'Zaroob DCC' as location, 'Sun' as day, '00:10:00' as open_time, '22:00:00' as close_time
union select 'Zaroob DIFC' as location, 'Mon' as day, '00:00:00' as open_time, '07:00:00' as close_time
union select 'Zaroob DIFC' as location, 'Tue' as day, '00:00:00' as open_time, '07:00:00' as close_time
union select 'Zaroob DIFC' as location, 'Wed' as day, '00:00:00' as open_time, '07:00:00' as close_time
union select 'Zaroob DIFC' as location, 'Thu' as day, '00:00:00' as open_time, '07:00:00' as close_time
union select 'Zaroob DIFC' as location, 'Fri' as day, '00:00:00' as open_time, '07:00:00' as close_time
union select 'Zaroob DIFC' as location, 'Sat' as day, '00:00:00' as open_time, '07:00:00' as close_time
union select 'Zaroob DIFC' as location, 'Sun' as day, '00:00:00' as open_time, '07:00:00' as close_time
union select 'Zaroob Juffair' as location, 'Mon' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Zaroob Juffair' as location, 'Tue' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Zaroob Juffair' as location, 'Wed' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Zaroob Juffair' as location, 'Thu' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Zaroob Juffair' as location, 'Fri' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Zaroob Juffair' as location, 'Sat' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Zaroob Juffair' as location, 'Sun' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Zaroob Marasi Mall' as location, 'Mon' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Zaroob Marasi Mall' as location, 'Tue' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Zaroob Marasi Mall' as location, 'Wed' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Zaroob Marasi Mall' as location, 'Thu' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Zaroob Marasi Mall' as location, 'Fri' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Zaroob Marasi Mall' as location, 'Sat' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Zaroob Marasi Mall' as location, 'Sun' as day, '10:00:00' as open_time, '02:00:00' as close_time
union select 'Zaroob Marina' as location, 'Mon' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Zaroob Marina' as location, 'Tue' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Zaroob Marina' as location, 'Wed' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Zaroob Marina' as location, 'Thu' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Zaroob Marina' as location, 'Fri' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Zaroob Marina' as location, 'Sat' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Zaroob Marina' as location, 'Sun' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Zaroob Motorcity' as location, 'Mon' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Zaroob Motorcity' as location, 'Tue' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Zaroob Motorcity' as location, 'Wed' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Zaroob Motorcity' as location, 'Thu' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Zaroob Motorcity' as location, 'Fri' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Zaroob Motorcity' as location, 'Sat' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Zaroob Motorcity' as location, 'Sun' as day, '07:00:00' as open_time, '03:00:00' as close_time
union select 'Zaroob Zayed Town' as location, 'Mon' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'Zaroob Zayed Town' as location, 'Tue' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'Zaroob Zayed Town' as location, 'Wed' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'Zaroob Zayed Town' as location, 'Thu' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'Zaroob Zayed Town' as location, 'Fri' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'Zaroob Zayed Town' as location, 'Sat' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'Zaroob Zayed Town' as location, 'Sun' as day, '11:00:00' as open_time, '23:59:59' as close_time
union select 'Circle Cafe Kite Beach' as location, 'Mon' as day, '8:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Kite Beach' as location, 'Tue' as day, '8:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Kite Beach' as location, 'Wed' as day, '8:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Kite Beach' as location, 'Thu' as day, '8:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Kite Beach' as location, 'Fri' as day, '8:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Kite Beach' as location, 'Sat' as day, '8:00:00' as open_time, '22:00:00' as close_time
union select 'Circle Cafe Kite Beach' as location, 'Sun' as day, '8:00:00' as open_time, '22:00:00' as close_time
),
     td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'kitopi-pegasus'),   
   
   base AS  (
   SELECT "Organization",
   "Date",
   to_char("Date", 'Dy') as "Reminded Day",
   location_map.country AS "Country",
                      location_map.team AS "Team",
   location_map.cluster as "Cluster",
   "Location",
   split_part("Routine Name", ' - ', 1) AS "Routine Name",
  row_number() OVER (PARTITION BY ("Reminded At")::date,
                                                      split_part("Routine Name", ' - ', 1),
                                                     "Location"
                                         ORDER BY "Reminded At") AS "Routine #",
   "Reminded At",
   "Responded At",
   "Compliance",
   "Submission KNID",
      to_char("Date", 'YYYY-MM-DD') as "D",
   "Routine KNID" as "Form"
   FROM form_compliance_v2 fc
   JOIN location_acl ON fc."Location" = location_acl.job_location
    JOIN location_map ON fc."Location" = location_map.job_location
     WHERE fc."Organization" ='kitopi-pegasus'
     AND "Reminded At" BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP + interval '1 day'
	    ORDER BY "Organization",
            split_part("Routine Name", ' - ', 1),
           "Location", "Reminded At", "Responded At")
SELECT base.*
FROM base
JOIN location_schedule s ON base."Location" = s.location
AND (
        -- Match same-day business hours
        base."Reminded Day" = s.day
        
        -- Match previous day if store is an overnight store (closes past midnight)
        OR (
            TO_CHAR(base."Date" - INTERVAL '1 day', 'Dy') = s.day
            AND s.close_time::TIME <= s.open_time::TIME  -- Ensures it's an overnight store
        )
    )
WHERE 
    base."Reminded At" IS NOT NULL  -- Ensure valid reminders
    AND (
        base."Reminded At"::TIME BETWEEN s.open_time::TIME and s.close_time::time
	  or (s.open_time::time >= s.close_time::time
		  and (base."Reminded At"::time >= s.open_time::time or base."Reminded At"::time <= s.close_time::time)))
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10,
         11,
         12, 13, 14, 15
		 ORDER by 1, 4, 5, 6, 7, 2, 11, 8
```

---

## kitopi-fsa-audit_FS Audits.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, location_response, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: kitopi-fsa-audit
-- Dashboard: FS Audits
-- Category: Kitopi
-- Extracted: 2026-01-29 16:56:57
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'kitopi-pegasus'
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
                  WHERE ug2.user_id = @{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))), td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'kitopi-pegasus'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = '-OI9mvNhhWYENhMWsTxa'
     AND organization = 'kitopi-pegasus'
    and is_deleted = false
   GROUP BY 1,
            2),
     qd_non_table_non_logic AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          CASE
              WHEN qd.question_type = 'section' THEN 0
              ELSE sqno::integer*10000
          END AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          question_id AS qid,
          question_type AS q_type,
          question AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   WHERE question_type NOT IN ('table')),
     qdntwl_prework AS
  (SELECT *,
          jsonb_array_elements(definition -> 'logic') -> 'questions' q
   FROM forms
   JOIN question_definitions qd ON qd.nugget_id = forms.form_knid
   WHERE qd.definition -> 'logic' IS NOT NULL),
     qd_non_table_with_logic AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::integer*10000+(def.value->>'order')::integer AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          def.key AS qid,
          def.value->>'question_type' AS q_type,
                      def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
     qd_table AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::integer*10000+(def.value->>'order')::integer AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          def.key AS qid,
          def.value->>'question_type' AS q_type,
                      def.value->>'question' AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   CROSS JOIN jsonb_each(definition -> 'questions') def
   WHERE qd.question_type IN ('table')),
     final_definition AS
  (SELECT *
   FROM qd_non_table_non_logic
   UNION SELECT *
   FROM qd_non_table_with_logic
   UNION SELECT *
   FROM qd_table
   ORDER BY 1,
            2,
            3,
            5 DESC, 7 DESC),
     _fs AS
  (SELECT DISTINCT ON (response_id) form_submissions.*,
                      form_name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   ORDER BY response_id,
            id DESC),
    fs as (
        select * from _fs
        where submit_date >= current_timestamp - interval '2 months'
    ),
     fr AS
  (SELECT fs.organization,
          form_submit_id,
          form_id,
          form_name,
          sno,
          submit_date + td.diff AS submit_date,
          user_id,
          response_id,
          question_id AS parent_qid,
          question_id AS qid,
          question_type,
          response,
          1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   JOIN td ON fs.organization = td.organization
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT organization,
                form_submit_id,
                form_id,
                form_name,
                sno,
                submit_date,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                question_type,
                res.value AS response,
                rn
   FROM
     (SELECT fs.organization,
             form_submit_id,
             form_id,
             form_name,
             sno,
             submit_date + td.diff AS submit_date,
             user_id,
             response_id,
             question_id,
             question_type,
             base.value,
             base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id
      JOIN td ON fs.organization = td.organization,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
   location_questions as (
select distinct on (nugget_id) nugget_id, question_id from question_definitions qd 
where nugget_id in (select form_knid from forms)
and question_type = 'location'
order by nugget_id, section_id, sqno
),
/*location_response as (
select form_submit_id, (response ->> 'name')::text location_name from form_responses fr 
where question_id in (select question_id from location_questions)
and form_submit_id in (select id from fs)
),*/
     RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.parent_question,
          fd.question,
          q_type,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'linear_scale',
                                 'audit') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('checkboxes') THEN array_to_string(ARRAY
                                                                      (SELECT jsonb_array_elements_text(fr.response->'selected')
                                                                       UNION SELECT CASE
                                                                                        WHEN fr.response->>'otherText' IS NOT NULL THEN fr.response->>'otherText'
                                                                                        ELSE NULL
                                                                                    END), ', ')
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) + td.diff, 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('user') THEN fr.response::text
              WHEN fd.q_type IN ('upload_mixed',
                                 'upload_image',
                                 'upload_video') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location',
                                 'division',
                                 'sub_division') THEN fr.response ->> 'name'
              ELSE NULL
          END AS response,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS section_response,
          rn,
          fr.form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fs.location as store,
          ud.first_name as name,
   ud.department,
   ud.designation,
   ud.division
         -- lr.location_name as submission_location
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   Join fs on fs.form_id = fr.form_id
   join user_details ud on fr.user_id = ud.uuid
   --join location_response lr
   --on lr.form_submit_id = fr.form_submit_id
   JOIN td ON fr.organization = td.organization
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,16,17,18
   ORDER BY 1,
            2,
            3)
            select sno,store,name,submit_date,department,designation,division,
            max(response) filter(where question = 'Violation') as Violation,
            max(response) filter(where question = 'Severity') as Severity,
            max(response) filter(where question = 'Points deducted') as points_deducted,
            ROUND(MAX(response::numeric) FILTER (WHERE question = 'Score achived'), 2) AS score_achieved
            from raw
            group by 1,2,3,4,5,6,7
```

---
