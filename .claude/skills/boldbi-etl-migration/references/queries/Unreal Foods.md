# Unreal Foods

> Auto-generated on 2026-03-04 08:13

**Total queries:** 1

---

## Unreal Foods - Production Checklist Report_Production Checklist Dashboard.sql

**Tables referenced:** final_calc, form_responses, form_submissions, ideal_output_master, nuggets, pivoted, question_definitions, responses, target_forms

**Original Query:**

```sql
-- Data Source: Unreal Foods - Production Checklist Report
-- Dashboard: Production Checklist Dashboard
-- Category: Unreal Foods
-- Extracted: 2026-01-29 16:52:59
-- ============================================================

WITH target_forms AS (
    SELECT DISTINCT n.id
    FROM nuggets n
    WHERE n.title ILIKE 'Production Checklist%'
      AND n.organization = 'unreal-foods-cw'
      AND EXISTS (
          SELECT 1 
          FROM question_definitions qd 
          WHERE qd.nugget_id = n.id 
      )
),

ideal_output_master AS (
    SELECT * FROM (
        VALUES
            ('Salad Counter', 'Sweet chili sauce', 2.55),
            ('Salad Counter', 'Sweet and spicy chili jam sauce', NULL),
            ('Salad Counter', 'Somtum dressing (NV)', 1.5),
            ('Salad Counter', 'Somtum dressing (veg)', 1.5),
            ('Salad Counter', 'Laab dressing (NV)', 0.5),
            ('Salad Counter', 'Laab dressing (veg)', 0.54),
            ('Salad Counter', 'Spicy salad dressing (NV)', 0.95),
            ('Salad Counter', 'Spicy salad dressing (veg)', 0.9),

            ('Curry Counter', 'Peanut sauce', 1.5),
            ('Curry Counter', 'Massaman base', 1.6),
            ('Curry Counter', 'Moo Hong', 1.7),
            ('Curry Counter', 'Yellow curry base', 1.0),

            ('Wok Counter', 'Tomyum sauce (NV)', 0.65),
            ('Wok Counter', 'Tomyum sauce veg', 0.65),
            ('Wok Counter', 'Phad Thai sauce (NV)', 3.4),
            ('Wok Counter', 'Veg Phad Thai sauce', 2.2),
            ('Wok Counter', 'Non Veg Krapao Sauce', 0.9),
            ('Wok Counter', 'Veg Krapao Sauce', 0.9),
            ('Wok Counter', 'Morning glory sauce', NULL),
            ('Wok Counter', 'Kale sauce (NV)', NULL),
            ('Wok Counter', 'Chili jam veg', NULL),

            ('Desert Counter', 'Pandan custard', 0.9),
            ('Desert Counter', 'Coconut Ice cream Base', NULL)
    ) AS t(counter_name, item_name, ideal_per_batch_kg)
),

responses AS (
    SELECT
        fs.id AS submission_id,
        DATE(fs.submit_date) AS production_date,
        qd.question,
        CASE
            WHEN fr.question_type IN ('dropdown', 'multiple_choice')
                THEN fr.response->'selected'->>0
            WHEN fr.question_type IN ('single_text_field', 'formula')
                THEN fr.response->>0
            ELSE fr.response::text
        END AS answer
    FROM form_submissions fs
    JOIN form_responses fr
        ON fr.form_submit_id = fs.id
    JOIN question_definitions qd
        ON qd.question_id = fr.question_id
    WHERE fs.form_id IN (SELECT id FROM target_forms)
       AND fs.submit_date between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + INTERVAL '1 day'
      --AND fs.submit_date >= CURRENT_DATE - INTERVAL '4 weeks'
),

pivoted AS (
    SELECT
        submission_id,
        production_date,

        MAX(answer) FILTER (WHERE question = 'Counter Name') AS counter_name,
        MAX(answer) FILTER (WHERE question = 'Item Checked') AS item_name,
        MAX(answer) FILTER (WHERE question = 'Maker Name') AS maker_name,

        COALESCE(
            MAX(answer) FILTER (WHERE question = 'Checker Name'),
            'Not Checked'
        ) AS checker_name,

        MAX(answer) FILTER (WHERE question = 'No. of batches prepared')::numeric AS batches,
        MAX(answer) FILTER (WHERE question = 'Total output quantity (in KGs)')::numeric AS actual_output_kg

    FROM responses
    GROUP BY submission_id, production_date
),

final_calc AS (
    SELECT
        p.counter_name,
        p.item_name,
        p.production_date,
        p.maker_name,
        p.checker_name,
        iom.ideal_per_batch_kg,
        p.batches,
        ROUND(p.batches * iom.ideal_per_batch_kg, 2) AS ideal_output_kg,
        p.actual_output_kg,
        CASE
            WHEN p.actual_output_kg = 0 THEN NULL
            ELSE
                (p.actual_output_kg - (p.batches * iom.ideal_per_batch_kg))
                / p.actual_output_kg
        END AS deviation_ratio
    FROM pivoted p
    LEFT JOIN ideal_output_master iom
        ON LOWER(TRIM(iom.counter_name)) = LOWER(TRIM(p.counter_name))
       AND LOWER(TRIM(iom.item_name))    = LOWER(TRIM(p.item_name))
)

SELECT
    counter_name                    AS "Counter",
    item_name                       AS "Item",
    production_date::date           AS "Date",
    maker_name                      AS "Maker Name",
    checker_name                    AS "Checker Name",
    ideal_per_batch_kg              AS "Ideal Output per batch (kg)",
    batches                         AS "Batches produced",
    ideal_output_kg                 AS "Ideal Output",
    actual_output_kg                AS "Actual Output",
    ROUND(deviation_ratio * 100, 2) AS "Deviation %",
    CASE
        WHEN deviation_ratio IS NULL THEN 'No'
        WHEN ABS(deviation_ratio) > 0.05 THEN 'Yes'
        ELSE 'No'
    END AS "Deviation Flag"
FROM final_calc
WHERE counter_name IS NOT NULL  -- Filter out incomplete submissions
ORDER BY
    production_date DESC,
    counter_name,
    item_name
```

---
