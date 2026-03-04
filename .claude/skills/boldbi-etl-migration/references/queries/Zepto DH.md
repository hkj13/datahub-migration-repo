# Zepto DH

> Auto-generated on 2026-03-04 08:13

**Total queries:** 25

---

## Maintenance Ticket Management_With Grid Issues - Zepto Ticket Management.sql

**Tables referenced:** public.demo_maintenance_ticket_master

**Original Query:**

```sql
-- Data Source: Maintenance Ticket Management
-- Dashboard: With Grid Issues - Zepto Ticket Management
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:59:31
-- ============================================================

select * from public.demo_maintenance_ticket_master
```

---

## Pharma Audit Checklist_QA_Pharma Audit Checklist_QA.sql

**Tables referenced:** MH, checkpoint_mapping_text, duplicate_checkpoint_ids, for, form_responses, form_submissions, public.Zepto_QMS_Checkpoint_Master_Sheet_table, question_definitions, the, trade

**Original Query:**

```sql
-- Data Source: Pharma Audit Checklist_QA
-- Dashboard: Pharma Audit Checklist_QA
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:53:09
-- ============================================================

-- HYBRID MAPPING: Text-based for 80 checkpoints + ID-based for 3 duplicates
-- When new form version is created, no changes needed (IDs for duplicates are matched by pattern)

WITH 
-- Text-based mapping for 80 unique checkpoints (excludes the 3 duplicates)
checkpoint_mapping_text(checkpoint_text, category, sub_category) AS (VALUES
    -- Display of signage board
    ('Chemist and Druggist board was displayed', 'Regulatory compliance', 'Display of signage board'),
    ('GST number mentioned in the signage board', 'Regulatory compliance', 'Display of signage board'),
    ('Name of the company & address', 'Regulatory compliance', 'Display of signage board'),
    ('Retail Sale Drug License (Form 20, 21)', 'Regulatory compliance', 'Display of signage board'),
    -- Display of Licenses
    ('FSSAI License', 'Regulatory compliance', 'Display of Licenses'),
    ('GST', 'Regulatory compliance', 'Display of Licenses'),
    ('S&E', 'Regulatory compliance', 'Display of Licenses'),
    -- Inspection book
    ('Availability of Form 35 inspection book', 'Regulatory compliance', 'Inspection book'),
    -- Registered Pharmacist (RP)
    ('RP registration certificate was displayed', 'Regulatory compliance', 'Registered Pharmacist (RP)'),
    ('RP present in every shift', 'Regulatory compliance', 'Registered Pharmacist (RP)'),
    ('Total no.of endorsed RP matches with the displayed RP  registration certificate', 'Regulatory compliance', 'Registered Pharmacist (RP)'),
    ('Any registered endorsed or competent  RP resigned during your audit period (number & name to be documented)', 'Regulatory compliance', 'Registered Pharmacist (RP)'),
    -- B2C invoice validation (excluding 3 duplicates)
    ('Invoice printed & sent to customer with product for the prescription medicines', 'Regulatory compliance', 'B2C invoice validation'),
    ('"Ship to (Patient)" text mentioned', 'Regulatory compliance', 'B2C invoice validation'),
    ('All valid Drug License number mentioned as per Drug License', 'Regulatory compliance', 'B2C invoice validation'),
    ('Address of firm mentioned as per Drug License', 'Regulatory compliance', 'B2C invoice validation'),
    ('Doctor''s name mentioned', 'Regulatory compliance', 'B2C invoice validation'),
    ('Doctor''s address mentioned', 'Regulatory compliance', 'B2C invoice validation'),
    ('Patient''s address mentioned', 'Regulatory compliance', 'B2C invoice validation'),
    ('Batch number of medicine mentioned', 'Regulatory compliance', 'B2C invoice validation'),
    ('Quantity of medicine mentioned', 'Regulatory compliance', 'B2C invoice validation'),
    ('MRP of medicine mentioned', 'Regulatory compliance', 'B2C invoice validation'),
    ('Manufacturer name of medicine mentioned', 'Regulatory compliance', 'B2C invoice validation'),
    ('HSN number of medicine mentioned', 'Regulatory compliance', 'B2C invoice validation'),
    ('Signature of RP on invoice of prescription medicine', 'Regulatory compliance', 'B2C invoice validation'),
    -- Schedule H1 register (excluding 3 duplicates)
    ('S.No. mentioned', 'Regulatory compliance', 'Schedule H1 register'),
    ('Invoice number mentioned', 'Regulatory compliance', 'Schedule H1 register'),
    ('Invoice date mentioned', 'Regulatory compliance', 'Schedule H1 register'),
    ('Medicine batch number mentioned', 'Regulatory compliance', 'Schedule H1 register'),
    ('Quantity of medicine sold mentioned', 'Regulatory compliance', 'Schedule H1 register'),
    ('Manufacture name of medicine', 'Regulatory compliance', 'Schedule H1 register'),
    ('Doctor name mentioned', 'Regulatory compliance', 'Schedule H1 register'),
    ('Doctor address mentioned', 'Regulatory compliance', 'Schedule H1 register'),
    ('Patient address mentioned', 'Regulatory compliance', 'Schedule H1 register'),
    ('Signature of on duty RP', 'Regulatory compliance', 'Schedule H1 register'),
    ('H1 registered maintained in chronological order (Daily/Monthly)', 'Regulatory compliance', 'Schedule H1 register'),
    -- Storage of medicines
    ('Are Cold chain products kept in the refrigerator', 'Regulatory compliance', 'Storage of medicines'),
    ('Are non-cold medicines stored as per temperature condition mentioned on the product label', 'Regulatory compliance', 'Storage of medicines'),
    ('Is seperate (away from trade stock) expiry & near expiry locations available', 'Regulatory compliance', 'Storage of medicines'),
    ('Expired medicine storage location marked as "Not for Sale"', 'Regulatory compliance', 'Storage of medicines'),
    ('"No Physician" samples or "Government Supply" drugs found in stock', 'Regulatory compliance', 'Storage of medicines'),
    ('No banned / recalled drug found in the premise', 'Regulatory compliance', 'Storage of medicines'),
    ('Veterinary medicines was stocked separate from the allopathic medicines and marked as "Not for Human use"', 'Regulatory compliance', 'Storage of medicines'),
    ('Ayurvedic medicine stocked separate from the allopathic medicine and signage was there', 'Regulatory compliance', 'Storage of medicines'),
    ('Homeopathic medicine stocked separate from the allopathic medicine and signage was there', 'Regulatory compliance', 'Storage of medicines'),
    ('Medical devices stored different from the allopathic medicines', 'Regulatory compliance', 'Storage of medicines'),
    ('Quarantine area is there for storage of banned and recalled medicines under lock and key and signage is available?', 'Regulatory compliance', 'Storage of medicines'),
    ('Medicines were not stored in direct sunlight', 'Regulatory compliance', 'Storage of medicines'),
    -- Storage of records
    ('Duplicate signed B2C invoice copies maintained for records (daily/monthly)', 'Regulatory compliance', 'Storage of records'),
    ('Purchase invoice copies records maintained in chronological order', 'Regulatory compliance', 'Storage of records'),
    -- Sales of banned/DPCO/Recalled medicines
    ('Are banned items not sold from the stores', 'Regulatory compliance', 'Sales of banned/DPCO/Recalled medicines'),
    ('Are recalled medicines not sold from the stores', 'Regulatory compliance', 'Sales of banned/DPCO/Recalled medicines'),
    ('State-specifc restricted (Maharastra) medicines not sold', 'Regulatory compliance', 'Sales of banned/DPCO/Recalled medicines'),
    -- Inwarding - Security check
    ('Records of Appropriateness of company address on the delivery documents with date and time', 'Operational compliance', 'Inwarding - Security check'),
    ('Inward security stamp on bill with date and time', 'Operational compliance', 'Inwarding - Security check'),
    -- Inwarding - Physical Validation
    ('Records of received materials by Inbound Lead/ Manager at receiving bay. Material Name, Supplier/ Manufacturer Name & Address, Batch Number, Expiry date, Short, Excess, Mismatch & Damage, Content strength, pack size, Maximum retail price (MRP)', 'Operational compliance', 'Inwarding - Physical Validation'),
    -- Inwarding - GRN
    ('No mismatch in purchase invocie &  GRN', 'Operational compliance', 'Inwarding - GRN'),
    ('Records of Invoice vs physical mismatch, damaged, short, excess', 'Operational compliance', 'Inwarding - GRN'),
    -- Outbound - Quality checks
    ('Quantity, MRP, Batch no, Expiry, 6 side check of items to ensure physical condition quality,item description were checked during invoicing', 'Operational compliance', 'Outbound - Quality checks'),
    ('Did RP check the prescription during dispensing?', 'Operational compliance', 'Outbound - Quality checks'),
    -- Outbound - Packing
    ('Items were packed as per the packing guidelines', 'Operational compliance', 'Outbound - Packing'),
    ('Any Handover sheet/acknowledgement copy available having list of packed items to be send to dispatch', 'Operational compliance', 'Outbound - Packing'),
    -- Cold chain management - Receiving of cold chain
    ('Check the temperature of the cold chain medicines received from MH', 'Operational compliance', 'Cold chain management - Receiving of cold chain'),
    -- Cold chain management - Storage
    ('Dedicated area for storage of the cold chain medicines with proper marking', 'Operational compliance', 'Cold chain management - Storage'),
    ('Temperature monitoring of the cold room/refrigerator shiftwise', 'Operational compliance', 'Cold chain management - Storage'),
    ('Logs to be maintained for temperature monitoring shiftwise', 'Operational compliance', 'Cold chain management - Storage'),
    -- Cold chain management - Outbound
    ('Check the consistency and temperature of the gel/ice pack to be placed in the cold chain box', 'Operational compliance', 'Cold chain management - Outbound'),
    ('Check for the temperature of the cold medicine before placing in the cold chain box and maintain the logs for the same', 'Operational compliance', 'Cold chain management - Outbound'),
    -- Cold chain management
    ('Is there back-up power supply (i.e. generator)?', 'Operational compliance', 'Cold chain management'),
    ('Calibration record of the cold chain equipment like thermal gun, temperature display and cold room temperature display were available', 'Operational compliance', 'Cold chain management'),
    -- Expired & Near-expiry
    ('Are all medicines checked physically for expiry every month end', 'Operational compliance', 'Expired & Near-expiry'),
    ('Is expired items present in the inventory', 'Operational compliance', 'Expired & Near-expiry'),
    ('Are near-expiry items pulled out from the inventory locations and kept separate from trade stock', 'Operational compliance', 'Expired & Near-expiry'),
    -- Fire Extinguisher
    ('Fire extinguisher availability, servicing record, and staff training.', 'Fire Safety & Security', 'Fire Extinguisher'),
    -- Security
    ('Verify 24x7 CCTV coverage for receiving, storage, and dispatch areas (data backup for 30 days).', 'Fire Safety & Security', 'Security'),
    -- Medical Fitness
    ('Annual medical check-up reports for staff.', 'Pharmacist Medical Record', 'Medical Fitness'),
    -- Pest Control
    ('Valid pest control AMC; check recent service record.', 'Pest Control & Hygiene', 'Pest Control'),
    ('Any Pest observed in the store premises?', 'Pest Control & Hygiene', 'Pest Control'),
    -- Housekeeping
    ('Was the floor, walls, corner cleaned?', 'Pest Control & Hygiene', 'Housekeeping'),
    ('Verify cleaning logs; ensure medicines are not kept on floor.', 'Pest Control & Hygiene', 'Housekeeping')
),

-- ID-based mapping ONLY for the 3 duplicate checkpoints
-- These IDs identify B2C vs H1 versions
-- Pattern: IDs ending in 'mo', 'D3', 'mm', 'D1', 'mk', 'D-' are B2C
-- Pattern: IDs ending in 'n0', 'MLU', 'my', 'DD', 'n4', 'MLY' are H1
duplicate_checkpoint_ids(checkpoint_knid, category, sub_category) AS (VALUES
    -- Expiry date of medicine mentioned - B2C
    ('-OfUdzPDEsx924PpmYmo', 'Regulatory compliance', 'B2C invoice validation'),
    ('-OfZOP2N9sr17sah-_D3', 'Regulatory compliance', 'B2C invoice validation'),
    -- Expiry date of medicine mentioned - H1
    ('-OfUdzPDEsx924PpmYn0', 'Regulatory compliance', 'Schedule H1 register'),
    ('-OfZOP2O2eF02qrQiMLU', 'Regulatory compliance', 'Schedule H1 register'),
    -- Medicine name mentioned - B2C
    ('-OfUdzPDEsx924PpmYmm', 'Regulatory compliance', 'B2C invoice validation'),
    ('-OfZOP2N9sr17sah-_D1', 'Regulatory compliance', 'B2C invoice validation'),
    -- Medicine name mentioned - H1
    ('-OfUdzPDEsx924PpmYmy', 'Regulatory compliance', 'Schedule H1 register'),
    ('-OfZOP2N9sr17sah-_DD', 'Regulatory compliance', 'Schedule H1 register'),
    -- Patient's name mentioned - B2C
    ('-OfUdzPDEsx924PpmYmk', 'Regulatory compliance', 'B2C invoice validation'),
    ('-OfZOP2N9sr17sah-_D-', 'Regulatory compliance', 'B2C invoice validation'),
    -- Patient's name mentioned - H1
    ('-OfUdzPDEsx924PpmYn4', 'Regulatory compliance', 'Schedule H1 register'),
    ('-OfZOP2O2eF02qrQiMLY', 'Regulatory compliance', 'Schedule H1 register')
)

SELECT 
       store_id AS "Store ID",
       MAX(CASE WHEN qd.question ILIKE '%Audited Location%' THEN 
           COALESCE(response->>'name', response->'selected'->>0, response::text)
       END) AS "Audited Location",
       MAX(CASE WHEN qd.question ILIKE '%Write Standard Store Name%' THEN 
           COALESCE(response->'selected'->>0, response::text)
       END) AS "Store Name/Location",
       city_id AS "City ID",
       audit_main_theme AS "Audit Main Theme",
       audit_date AS "Audit Date",
       audit_submission_number AS "Audit Submission Number",
       auditor_name AS "Auditor Name",
       cms.checkpoint_knid AS "Checkpoint KNID",
       CHECKPOINT AS "Checkpoint",
       RESULT AS "Result",
       REPLACE(REPLACE(MAX(auditor_observations), chr(10), ' '), chr(13), ' ') AS "Auditor Observations",
       -- Priority: ID-based mapping for duplicates, then text-based, then fallback to theme
       COALESCE(MAX(dup.category), MAX(txt.category), theme) AS "Category",
       COALESCE(MAX(dup.sub_category), MAX(txt.sub_category), theme) AS "Sub Category"
FROM public.Zepto_QMS_Checkpoint_Master_Sheet_table cms
JOIN form_submissions fs ON cms.audit_submission_knid = fs.response_id
JOIN form_responses fr ON fs.id = fr.form_submit_id
JOIN question_definitions qd ON fr.question_id = qd.question_id
-- ID-based join for 3 duplicate checkpoints
LEFT JOIN duplicate_checkpoint_ids dup ON cms.checkpoint_knid = dup.checkpoint_knid
-- Text-based join for all other checkpoints (with normalization)
LEFT JOIN checkpoint_mapping_text txt ON 
    TRIM(REGEXP_REPLACE(TRANSLATE(cms.checkpoint, E'\u201c\u201d', '""'), '\s+', ' ', 'g')) = 
    TRIM(REGEXP_REPLACE(txt.checkpoint_text, '\s+', ' ', 'g'))
WHERE audit_main_theme ILIKE '%Pharma Audit Checklist_QA%'
  AND audit_date >= date_trunc('month', CURRENT_DATE)
GROUP BY store_id, city_id, audit_main_theme, theme, audit_date,
         audit_submission_number, auditor_name,
         cms.checkpoint_knid,
         CHECKPOINT, RESULT
```

---

## WHS Zepto Audit Details_WHS - Zepto.sql

**Tables referenced:** audit_date, base, organizations, td, zepto_qms_checkpoint_master_sheet_table

**Original Query:**

```sql
-- Data Source: WHS Zepto Audit Details
-- Dashboard: WHS - Zepto
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:58:25
-- ============================================================

WITH td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Zds-indus'),
     base AS
  (SELECT organization_id,
          CASE
              WHEN result_score = '' THEN NULL
              ELSE result_score::numeric
          END AS result_score,
          CASE
              WHEN max_score = '' THEN NULL
              ELSE max_score::numeric
          END AS max_score,
          store_id,
          audit_main_theme,
          theme,
          audit_date,
          audit_submission_number,
          audit_submission_knid,
          auditor_name,
          checkpoint_knid,
          CHECKPOINT,
          case when RESULT ilike 'Non-compliance' then 'NC' else RESULT END as RESULT,
          criticality,
          auditor_observations,
          total_follow_up_tasks,
          total_closed_follow_up_tasks,
          CASE
              WHEN result_score = '' THEN 'Not checked'
              WHEN result_score::numeric < max_score::numeric THEN 'Failed'
              ELSE 'Passed'
          END AS status,
                              row_number() OVER (PARTITION BY store_id,
                                       audit_main_theme,
                                       theme, checkpoint_knid,
                                       extract('Year'
                  FROM audit_date)
                          ORDER BY audit_date) AS "Audit No in Year"
   FROM zepto_qms_checkpoint_master_sheet_table cms
   JOIN td ON cms.organization_id = td.organization
   WHERE organization_id = 'Zds-indus'
  and audit_main_theme ilike 'WHS - Zepto DH%')
SELECT organization_id AS "Org",
       store_id AS "Location",
       audit_main_theme AS "Audit",
       audit_date AS "Audit Date",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
       auditor_name AS "Auditor",
	   theme as "Theme",
       checkpoint_knid as "Checkpoint KNID",
	   checkpoint as "Checkpoint",
	   result as "Result",
	   status as "Checkpoint Status",
	   auditor_observations as "Auditor Notes",
	   result_score as "Actual Score",
	   max_score as "Max Score",
	   criticality as "Criticality",
       total_follow_up_tasks AS "Total Follow Ups",
       total_closed_follow_up_tasks AS "Total Closed Follow Ups",
       "Audit No in Year"
FROM base
group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19
ORDER BY 1,
         2,
         4
```

---

## WSH Zepto Audit Summary_WHS - Zepto.sql

**Tables referenced:** audit_date, base, organizations, td, zepto_qms_checkpoint_master_sheet_table

**Original Query:**

```sql
-- Data Source: WSH Zepto Audit Summary
-- Dashboard: WHS - Zepto
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:58:26
-- ============================================================

WITH td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Zds-indus'),
     base AS
  (SELECT organization_id,
          CASE
              WHEN result_score = '' THEN NULL
              ELSE result_score::numeric
          END AS result_score,
          CASE
              WHEN max_score = '' THEN NULL
              ELSE max_score::numeric
          END AS max_score,
          store_id,
          audit_main_theme,
          theme,
          audit_date,
          audit_submission_number,
          audit_submission_knid,
          auditor_name,
          checkpoint_knid,
          CHECKPOINT,
          case when RESULT ilike 'Non-compliance' then 'NC' else RESULT END as RESULT,
          criticality,
          auditor_observations,
          total_follow_up_tasks,
          total_closed_follow_up_tasks,
          CASE
              WHEN result_score = '' THEN 'Not checked'
              WHEN result_score::numeric < max_score::numeric THEN 'Failed'
              ELSE 'Passed'
          END AS status,
                              row_number() OVER (PARTITION BY store_id,
                                       audit_main_theme,
                                       theme, checkpoint_knid,
                                       extract('Year'
                  FROM audit_date)
                          ORDER BY audit_date) AS "Audit No in Year"
   FROM zepto_qms_checkpoint_master_sheet_table cms
   JOIN td ON cms.organization_id = td.organization
   WHERE organization_id = 'Zds-indus'
  and audit_main_theme ilike 'WHS - Zepto DH%')
  
SELECT organization_id AS "Org",
       store_id AS "Location",
       audit_main_theme AS "Audit",
       audit_date AS "Audit Date",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
       auditor_name AS "Auditor",
       sum(result_score) as "Actual Score",
	   sum(max_score) as "Max Score",
	   sum(result_score)/sum(max_score) AS "Audit Score",
       sum(total_follow_up_tasks) AS "Total Follow Ups",
       sum(total_closed_follow_up_tasks) AS "Total Closed Follow Ups",
       "Audit No in Year"
FROM base
group by 1, 2, 3, 4, 5, 6, 7, 13
ORDER BY 1,
         2,
         4
```

---

## Zepto - Trainer Feedback Dashboard_Zepto - Trainer Feedback Dashboard.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, fs.submit_date, jsonb_each, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Zepto - Trainer Feedback Dashboard
-- Dashboard: Zepto - Trainer Feedback Dashboard
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:54:22
-- ============================================================

WITH td AS (
  SELECT id AS organization,
         tzoffset,
         interval '1 min' * tzoffset AS diff
  FROM organizations
  WHERE id = 'Zds-indus'
),
forms AS (
  SELECT n.id AS form_knid, n.title AS form_name
  FROM nuggets n
  WHERE n.id = '-OWtKMjh3R4JGPRFUpcT'
    AND n.organization = 'Zds-indus'
    AND n.is_deleted = FALSE
),
qd_non_table_non_logic AS (
  SELECT qd.nugget_id AS form_knid,
         CASE WHEN qd.section_id = 'section' THEN 1 ELSE replace(qd.section_id,'section-','')::int END AS section_no,
         CASE WHEN qd.question_type = 'section' THEN 0 ELSE qd.sqno::int * 10000 END AS q_no,
         qd.section_id,
         qd.question_id AS parent_qid,
         qd.question_type AS parent_q_type,
         qd.question AS parent_question,
         qd.question_id AS qid,
         qd.question_type AS q_type,
         qd.question AS question
  FROM forms f
  JOIN question_definitions qd ON f.form_knid = qd.nugget_id
  WHERE qd.question_type NOT IN ('table')
),
qdntwl_prework AS (
  SELECT qd.*, jsonb_array_elements(qd.definition->'logic')->'questions' AS q
  FROM forms f
  JOIN question_definitions qd ON qd.nugget_id = f.form_knid
  WHERE qd.definition->'logic' IS NOT NULL
),
qd_non_table_with_logic AS (
  SELECT qd.nugget_id AS form_knid,
         CASE WHEN qd.section_id = 'section' THEN 1 ELSE replace(qd.section_id,'section-','')::int END AS section_no,
         qd.sqno::int * 10000 + (def.value->>'order')::int AS q_no,
         qd.section_id,
         qd.question_id AS parent_qid,
         qd.question_type AS parent_q_type,
         qd.question AS parent_question,
         def.key AS qid,
         def.value->>'question_type' AS q_type,
         def.value->>'question' AS question
  FROM qdntwl_prework qd
  CROSS JOIN jsonb_each(qd.q) def
  WHERE qd.definition->>'logic' IS NOT NULL
),
qd_table AS (
  SELECT qd.nugget_id AS form_knid,
         CASE WHEN qd.section_id = 'section' THEN 1 ELSE replace(qd.section_id,'section-','')::int END AS section_no,
         qd.sqno::int * 10000 + (def.value->>'order')::int AS q_no,
         qd.section_id,
         qd.question_id AS parent_qid,
         qd.question_type AS parent_q_type,
         qd.question AS parent_question,
         def.key AS qid,
         def.value->>'question_type' AS q_type,
         def.value->>'question' AS question
  FROM forms f
  JOIN question_definitions qd ON f.form_knid = qd.nugget_id
  CROSS JOIN jsonb_each(qd.definition->'questions') def
  WHERE qd.question_type IN ('table')
),
final_definition AS (
  SELECT * FROM qd_non_table_non_logic
  UNION ALL
  SELECT * FROM qd_non_table_with_logic
  UNION ALL
  SELECT * FROM qd_table
),
_fs AS (
  SELECT DISTINCT ON (fs.response_id)
         fs.*, (extract(epoch FROM fs.submit_date)*1000)::bigint AS submit_epoch
  FROM form_submissions fs
  WHERE fs.form_id IN (SELECT form_knid FROM forms) 
  ORDER BY fs.response_id, fs.id DESC
),
fs AS (
  SELECT f0.*, frm.form_name
  FROM _fs f0
  JOIN forms frm ON f0.form_id = frm.form_knid
  JOIN td ON td.organization = f0.organization
),
fr AS (
  SELECT fs.organization, fr.form_submit_id, fs.form_id, fs.form_name,
         fs.sno, (fs.submit_date + td.diff) AS submit_date, fs.submit_epoch,
         fs.user_id, fs.response_id,
         fr.question_id AS parent_qid,
         fr.question_id AS qid,
         fr.question_type,
         fr.response,
         1 AS rn,
         fs.location
  FROM form_responses fr
  JOIN fs ON fs.id = fr.form_submit_id
  JOIN td ON td.organization = fs.organization
  WHERE fr.question_type NOT IN ('table','nested')

  UNION ALL

  SELECT base1.organization, base1.form_submit_id, base1.form_id, base1.form_name,
         base1.sno, base1.submit_date, base1.submit_epoch,
         base1.user_id, base1.response_id,
         base1.question_id AS parent_qid,
         res.key AS qid,
         base1.question_type,
         res.value AS response,
         base1.rn,
         base1.location
  FROM (
    SELECT fs.organization, fr.form_submit_id, fs.form_id, fs.form_name,
           fs.sno, (fs.submit_date + td.diff) AS submit_date, fs.submit_epoch,
           fs.user_id, fs.response_id, fr.question_id, fr.question_type,
           base.value, base.ordinality AS rn, fs.location
    FROM form_responses fr
    JOIN fs ON fs.id = fr.form_submit_id
    JOIN td ON td.organization = fs.organization,
         jsonb_array_elements(fr.response) WITH ORDINALITY AS base
    WHERE fr.question_type = 'table'
  ) base1
  CROSS JOIN jsonb_each(base1.value) res
),
raw AS (
  SELECT fr.sno,
         fd.section_no,
         fd.q_no,
         fd.parent_question,
         fd.question,
         fd.q_type,
         CASE
           WHEN fd.q_type = 'section' THEN fr.response->>'status'
           WHEN fd.q_type IN ('dropdown','multiple_choice','linear_scale','audit')
                THEN fr.response->'selected'->>0
           WHEN fd.q_type = 'checkboxes'
                THEN array_to_string(ARRAY(
                      SELECT jsonb_array_elements_text(fr.response->'selected')
                      UNION SELECT CASE WHEN fr.response->>'otherText' IS NOT NULL
                                        THEN fr.response->>'otherText' ELSE NULL END
                    ), ', ')
           WHEN fd.q_type IN ('date','datetime')
                THEN to_char(to_timestamp((fr.response::bigint)/1000) + td.diff, 'YYYY-MM-DD HH24:MI:SS')
           WHEN fd.q_type IN ('long_text_field','single_text_field','qr_code','formula')
                THEN fr.response->>0
           WHEN fd.q_type IN ('user') THEN fr.response::text
           WHEN fd.q_type IN ('upload_mixed','upload_image','upload_video')
                THEN (fr.response)->0->>'response'
           WHEN fd.q_type IN ('signature','location','division','sub_division')
                THEN fr.response->>'name'
           ELSE NULL
         END AS response,
         CASE WHEN fd.q_type = 'section' THEN fr.response ELSE NULL END AS section_response,
         fr.rn,
         fr.form_name,
         fr.form_id,
         fr.response_id,
         fr.submit_date::date AS submit_date,
         fr.location,
         fr.user_id,
         ud.identifier,
         ud.division,
         ud.sub_division,
         fr.submit_epoch
  FROM final_definition fd
  JOIN fr ON fr.qid = fd.qid AND fr.form_id = fd.form_knid
  JOIN td ON td.organization = fr.organization
  LEFT JOIN user_details ud ON ud.uuid = fr.user_id
)
SELECT
  r.form_name,
  r.form_id,
  r.response_id,
  MIN(r.submit_date) AS "Submit Date",
  MIN(r.submit_epoch) AS submit_epoch,
  MIN(r.identifier) AS "Submitter Identifier",
  MIN(r.division)   AS "Division",
  MIN(r.sub_division) AS "Sub Division",
  MAX(CASE WHEN r.question ILIKE 'Enter the Trainer Name%' THEN r.response END) AS "Enter the Trainer Name",
  MAX(CASE WHEN r.question ILIKE 'Cafe Name%' THEN r.response END) AS "Cafe Name",
  MAX(CASE WHEN r.question ILIKE 'Product / Process name of which Training has been taken%' THEN r.response END) AS "Product / Process name of which Training has been taken",
  MAX(CASE WHEN r.question ILIKE 'Did the trainer demonstrate all the aspects of the product/process%' THEN NULLIF(r.response,'')::int END) AS "Did the trainer demonstrate all the aspects of the product/process?",
  MAX(CASE WHEN r.question ILIKE 'Was the training delivery style engaging and easy to follow%' THEN NULLIF(r.response,'')::int END) AS "Was the training delivery style engaging and easy to follow?",
  MAX(CASE WHEN r.question ILIKE 'Did the trainer effectively handle questions asked%' THEN NULLIF(r.response,'')::int END) AS "Did the trainer effectively handle questions asked?",
  MAX(CASE WHEN r.question ILIKE 'Do you believe this training will improve your job performance%' THEN NULLIF(r.response,'')::int END) AS "Do you believe this training will improve your job performance?",
  MAX(CASE WHEN r.question ILIKE 'Overall, how satisfied are you with the training experience%' THEN NULLIF(r.response,'')::int END) AS "Overall, how satisfied are you with the training experience?",
  MAX(CASE WHEN r.question ILIKE 'Share your feedback%Suggestions%' THEN r.response END) AS "Share your feedback / Suggestions if any"
FROM raw r
WHERE r.q_type NOT IN ('section','title_description')
GROUP BY r.form_name, r.form_id, r.response_id
ORDER BY "Submit Date" DESC, r.response_id
```

---

## Zepto Announcements_Zepto Announcements.sql

**Tables referenced:** data_team.zepto_announcements

**Original Query:**

```sql
-- Data Source: Zepto Announcements
-- Dashboard: Zepto Announcements
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:52:34
-- ============================================================

select * from data_team.zepto_announcements
```

---

## Zepto Cafe Onboarding Progress Report_Zepto Cafe Onboarding Journey Progress Report.sql

**Tables referenced:** analytics.nugget_analytics_raw, analytics.nuggets_user_share_requests, d1_consumed, d1_started, d2_consumed, d2_started, d3_consumed, d3_started, d4_consumed, d4_started, sent_users, user_details

**Original Query:**

```sql
-- Data Source: Zepto Cafe Onboarding Progress Report
-- Dashboard: Zepto Cafe Onboarding Journey Progress Report
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:53:39
-- ============================================================

WITH sent_users AS
  (SELECT DISTINCT ON (user_id) user_id,
                      share_id,
                      created_at AT TIME ZONE 'Asia/Kolkata' AS sent_at
   FROM analytics.nuggets_user_share_requests nusr
   WHERE nuggeT_id = 'rnzrbts5Qy8rBXZebGNqg5'
   ORDER BY user_id,
            created_at DESC),
     d1_started AS
  (SELECT DISTINCT nar.user_id
   FROM analytics.nugget_analytics_raw nar
   JOIN sent_users su ON su.user_id = nar.user_id
   AND su.share_id = nar.share_id
   WHERE course_id = '8kmFdEijH9E63neVjQu7Vn'
     AND nugget_id = course_id
     AND event_id = 5),
     d1_consumed AS
  (SELECT DISTINCT nar.user_id
   FROM analytics.nugget_analytics_raw nar
   JOIN sent_users su ON su.user_id = nar.user_id
   AND su.share_id = nar.share_id
   WHERE nugget_id = 'gjgk8nUwoK6NKaKJhCRDvs'
     AND event_id = 3),
     d2_started AS
  (SELECT DISTINCT nar.user_id
   FROM analytics.nugget_analytics_raw nar
   JOIN sent_users su ON su.user_id = nar.user_id
   AND su.share_id = nar.share_id
   WHERE course_id = 'oFqGvD2bp8gSa81Vgi7Q1Q'
     AND event_id = 5),
     d2_consumed AS
  (SELECT DISTINCT nar.user_id
   FROM analytics.nugget_analytics_raw nar
   JOIN sent_users su ON su.user_id = nar.user_id
   AND su.share_id = nar.share_id
   WHERE nugget_id = 'ua5Ashb32jx84b5gVk31pN'
     AND event_id = 3),
     d3_started AS
  (SELECT DISTINCT nar.user_id
   FROM analytics.nugget_analytics_raw nar
   JOIN sent_users su ON su.user_id = nar.user_id
   AND su.share_id = nar.share_id
   WHERE course_id = 'dqzooBMLZn3zQnXDUuMRXP'
     AND event_id = 5),
     d3_consumed AS
  (SELECT DISTINCT nar.user_id
   FROM analytics.nugget_analytics_raw nar
   JOIN sent_users su ON su.user_id = nar.user_id
   AND su.share_id = nar.share_id
   WHERE nugget_id = '72fLzUoiCPju6Vp6Jx3SAB'
     AND event_id = 3),
     d4_started AS
  (SELECT DISTINCT nar.user_id
   FROM analytics.nugget_analytics_raw nar
   JOIN sent_users su ON su.user_id = nar.user_id
   AND su.share_id = nar.share_id
   WHERE course_id = '2dxv36ki9RTE93y6Pe7f6c'
     AND event_id = 5),
     d4_consumed AS
  (SELECT DISTINCT nar.user_id
   FROM analytics.nugget_analytics_raw nar
   JOIN sent_users su ON su.user_id = nar.user_id
   AND su.share_id = nar.share_id
   WHERE nugget_id = '7CM12H3hWJoTKeZdqpGk8j'
     AND event_id = 3)
SELECT su.user_id AS "Employee KNID",
       ud.first_name||' '||ud.last_name AS "Employee Name",
       ud.identifier AS "Identifier",
       ud.division AS "Division",
       ud.sub_division AS "Sub Division",
       ud.job_location AS "Location",
       ud.designation AS "Designation",
       (su.sent_at AT TIME ZONE 'Asia/Kolkata')::date AS "Enrolled On",
       CASE
           WHEN d1c.user_id IS NOT NULL
                OR d2s.user_id IS NOT NULL
                OR d2c.user_id IS NOT NULL
                OR d3s.user_id IS NOT NULL
                OR d3c.user_id IS NOT NULL
                OR d4s.user_id IS NOT NULL
                OR d4c.user_id IS NOT NULL THEN 'Completed'
           WHEN d1s.user_id IS NOT NULL THEN 'In Progress'
           ELSE 'Not Started'
       END AS "D1",
       CASE
           WHEN d2c.user_id IS NOT NULL
                OR d3s.user_id IS NOT NULL
                OR d3c.user_id IS NOT NULL
                OR d4s.user_id IS NOT NULL
                OR d4c.user_id IS NOT NULL THEN 'Completed'
           WHEN d2s.user_id IS NOT NULL THEN 'In Progress'
           ELSE 'Not Started'
       END AS "D2",
       CASE
           WHEN d3c.user_id IS NOT NULL
                OR d4s.user_id IS NOT NULL
                OR d4c.user_id IS NOT NULL THEN 'Completed'
           WHEN d3s.user_id IS NOT NULL THEN 'In Progress'
           ELSE 'Not Started'
       END AS "D3",
       CASE
           WHEN d4c.user_id IS NOT NULL THEN 'Completed'
           WHEN d4s.user_id IS NOT NULL THEN 'In Progress'
           ELSE 'Not Started'
       END AS "D4",
       CASE
           WHEN d4c.user_id IS NOT NULL THEN 'Completed'
           WHEN d1c.user_id IS NOT NULL
                OR d2s.user_id IS NOT NULL
                OR d2c.user_id IS NOT NULL
                OR d3s.user_id IS NOT NULL
                OR d3c.user_id IS NOT NULL
                OR d4s.user_id IS NOT NULL
                OR d1s.user_id IS NOT NULL THEN 'In Progress'
           ELSE 'Not Started'
       END AS "Overall"
FROM sent_users su
JOIN user_details ud ON su.user_id = ud.uuid
LEFT JOIN d1_started d1s ON su.user_id = d1s.user_id
LEFT JOIN d1_consumed d1c ON su.user_id = d1c.user_id
LEFT JOIN d2_started d2s ON su.user_id = d2s.user_id
LEFT JOIN d2_consumed d2c ON su.user_id = d2c.user_id
LEFT JOIN d3_started d3s ON su.user_id = d3s.user_id
LEFT JOIN d3_consumed d3c ON su.user_id = d3c.user_id
LEFT JOIN d4_started d4s ON su.user_id = d4s.user_id
LEFT JOIN d4_consumed d4c ON su.user_id = d4c.user_id
ORDER BY 4,
         5,
         6,
         8,
         2
```

---

## Zepto Course Reports_Zepto Course Report.sql

**Tables referenced:** analytic_requests, analytics, course_assesments_settings, courses, lateral, lesson_cards, lessons, nup_users_with_pagination, quiz, quiz_responses, user_details

**Columns needing snake_case conversion:**

- `inProgress` -> `in_progress` (alias: `in_progress AS "inProgress"`)


**Original Query:**

```sql
-- Data Source: Zepto Course Reports
-- Dashboard: Zepto Course Report
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:53:59
-- ============================================================

with lessons_cards as (
SELECT jsonb_object_agg(lesson_cards_map.id, cards) as lesson_cards_map
FROM (
	  SELECT 
	    l.id,
	    jsonb_object_agg(lc.id, true) AS cards
	  FROM lesson_cards lc
	  JOIN lessons l ON lc.lesson_id = l.id
	  WHERE l.course_id = @{{:Course Name}}
	  GROUP BY l.id
	) AS lesson_cards_map
),
course_assesments_settings as (
	select 
	  l.course_id,
	  jsonb_object_agg(lc.id, jsonb_build_object('assesment_name', lc.title,'settings', lc.settings)) as card_settings
	from lesson_cards lc
	join lessons l on lc.lesson_id = l.id
	where l.course_id = @{{:Course Name}}
	  and lc.type = 'quiz'
	group by l.course_id
),
nup_users_with_pagination as (
	select nup.*
	from analytics."nuggets_user_progress_@{{:Course Name.IGNOREQUOTES}}" nup
   where created_at between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'-- where nup.user_id in (select uuid from user_details ud where ud.identifier = 'Temp-78898')
	order by case nup.status
    when 'passed' then 1
    when 'completed' then 2
    when 'inProgress' then 3
    else 4
  end, nup.updated_at desc -- limit 1 offset 0
),
analytic_requests as (
	select t.user_id, jsonb_object_agg(t.nugget_id, t.analytics_by_event) as analytics_by_event 
	from (
	select ar.user_id, ar.nugget_id, jsonb_object_agg(event_id, jsonb_build_object(ar.analytics_id, ar.created_at)) as analytics_by_event
	from analytics."analytics_raw_@{{:Course Name.IGNOREQUOTES}}" ar
	join nup_users_with_pagination nup on nup.user_id = ar.user_id and nup.share_id = ar.share_id
	where ar.event_id in (5,3)
	group by 1,2) t
	group by 1
),
quiz_responses as (
select
  user_id,
  jsonb_object_agg(card_id, shares) as card_share_attempt_data
from (
  select
    user_id,
    card_id,
    jsonb_object_agg(share_id, attempts) as shares
  from (
    select
      user_id,
      card_id,
      share_id,
      jsonb_object_agg(attempt::text, questions) as attempts
    from (
      select
        ar.user_id,
        ar.card_id,
        ar.share_id,
        ar.attempt,
        jsonb_object_agg(ar.question_id::text, ar.is_correct) as questions
      from quiz."quiz_responses_@{{:Course Name.IGNOREQUOTES}}" ar
      join nup_users_with_pagination nup on (nup.user_id = ar.user_id and nup.share_id = ar.share_id)
      group by ar.user_id, ar.card_id, ar.share_id, ar.attempt
    ) q1
    group by user_id, card_id, share_id
  ) q2
  group by user_id, card_id
) q3
group by user_id
)
select ud.identifier as "Identifier", 
	   ud.first_name as "First Name", 
	   ud.last_name as "Last Name", 
	   ud.designation as "Designation", 
	   ud.department as "Department",
	   ud.division as "Division",
	   ud.sub_division as "Sub Division",
	   ud.job_location as "Location",
	   case when ud.is_active = true then 'Active' else 'In-Active' end as "Employee Status", 
	   c.name as "Course Name",
	   case when c.status = 'revoked' then 'Revoked' else 'Shared' end as "Course Status",
	   processed.*,
	   c.id as "Course ID"
from course_assesments_settings cas, lessons_cards lc, nup_users_with_pagination nup
join courses c on c.id = nup.nugget_id
join user_details ud on ud.uuid = nup.user_id
left join quiz_responses qr on qr.user_id = ud.uuid
left join analytic_requests ar on ar.user_id = nup.user_id
cross join lateral analytics.process_nuggets_user_progress(
	to_jsonb(nup),
	ar.analytics_by_event, 
	cas.card_settings, 
	lc.lesson_cards_map,
	qr.card_share_attempt_data
) as processed
```

---

## Zepto DH Audit Details_Audits.sql

**Tables referenced:** audit_date, base, location_acl, user_details, user_groups, zepto_qms_checkpoint_master_sheet_table

**Original Query:**

```sql
-- Data Source: Zepto DH Audit Details
-- Dashboard: Audits
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:57:05
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'Zds-indus'
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
               AND ug1.is_active = TRUE))),
     base AS
  (SELECT organization_id,
          CASE
              WHEN result_score = '' THEN NULL
              ELSE result_score::numeric
          END AS result_score,
          CASE
              WHEN max_score = '' THEN NULL
              ELSE max_score::numeric
          END AS max_score,
          store_id,
   audit_type,
          audit_main_theme,
          theme,
          audit_date,
          audit_submission_number,
          audit_submission_knid,
          auditor_name,
          checkpoint_knid,
          CHECKPOINT,
          RESULT,
          criticality,
          --is_critical_question_failed,
          auditor_observations,
          total_follow_up_tasks,
          total_closed_follow_up_tasks,
          CASE
              WHEN result_score = '' THEN 'Not checked'
              WHEN result_score::numeric < max_score::numeric THEN 'Failed'
              ELSE 'Passed'
          END AS status,
                              row_number() OVER (PARTITION BY store_id,
                                       audit_main_theme,
                                       theme, checkpoint_knid,
                                       extract('Year'
                  FROM audit_date)
                          ORDER BY audit_date) AS "Audit No in Year"
   FROM zepto_qms_checkpoint_master_sheet_table cms
   join location_acl on cms.store_id = location_acl.job_location
   WHERE organization_id = 'Zds-indus'
  and audit_main_theme in (
  'Outbound Process Audit Rev.01', 
'Picking Process Audit Rev.01', 
'Dump Process Audit Rev.01', 
'Asset Audit Rev.01', 
'Consumables Audit Rev.01', 
'GHP Audit Rev.01', 
'Inbound Process Audit Rev.01', 
'Inventory QC (DEQ) Audit Rev.01', 
'Legal Compliance Audit Rev.01', 
'Material Handling Audit Rev.01', 
'RC Audit Rev.01', 
'Staging / Stacking Audit Rev.01', 
'Inventory CC Audit Rev.01', 
'Revised GHP Audit', 
'Revised DH Beat Ops', 
'Revised DH Process Audit - Part 1', 
'Revised DH Process Audit - Part 2', 
'Revised DH Material Handling Audit'
  )
  and audit_date between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval ' 1 day')
SELECT organization_id AS "Org",
       store_id AS "Location",
	   audit_type as "Type",
       audit_main_theme AS "Audit",
       audit_date AS "Audit Date",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
       auditor_name AS "Auditor",
	   theme as "Theme",
       checkpoint_knid as "Checkpoint KNID",
	   checkpoint as "Checkpoint",
	   result as "Result",
	   status as "Checkpoint Status",
	   auditor_observations as "Auditor Notes",
	   result_score as "Actual Score",
	   max_score as "Max Score",
	   criticality as "Criticality",
       total_follow_up_tasks AS "Total Follow Ups",
       total_closed_follow_up_tasks AS "Total Closed Follow Ups",
       "Audit No in Year"
FROM base
group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,20
ORDER BY 1,
         2,
         4
```

---

## Zepto DH Audit Summary_Audits.sql

**Tables referenced:** audit_date, base, location_acl, user_details, user_groups, zepto_qms_checkpoint_master_sheet_table

**Original Query:**

```sql
-- Data Source: Zepto DH Audit Summary
-- Dashboard: Audits
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:57:04
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'Zds-indus'
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
               AND ug1.is_active = TRUE))),
     base AS
  (SELECT organization_id,
          CASE
              WHEN result_score = '' THEN NULL
              ELSE result_score::numeric
          END AS result_score,
          CASE
              WHEN max_score = '' THEN NULL
              ELSE max_score::numeric
          END AS max_score,
          store_id,
   audit_type,
          audit_main_theme,
          theme,
          audit_date,
          audit_submission_number,
          audit_submission_knid,
          auditor_name,
          checkpoint_knid,
          CHECKPOINT,
          RESULT,
          criticality,
          --is_critical_question_failed,
          auditor_observations,
          total_follow_up_tasks,
          total_closed_follow_up_tasks,
          CASE
              WHEN result_score = '' THEN 'Not checked'
              WHEN result_score::numeric < max_score::numeric THEN 'Failed'
              ELSE 'Passed'
          END AS status,
                              row_number() OVER (PARTITION BY store_id,
                                       audit_main_theme,
                                       theme, checkpoint_knid,
                                       extract('Year'
                  FROM audit_date)
                          ORDER BY audit_date) AS "Audit No in Year"
   FROM zepto_qms_checkpoint_master_sheet_table cms
   join location_acl on cms.store_id = location_acl.job_location
   WHERE organization_id = 'Zds-indus'
   and audit_main_theme in (
  'Outbound Process Audit Rev.01', 
'Picking Process Audit Rev.01', 
'Dump Process Audit Rev.01', 
'Asset Audit Rev.01', 
'Consumables Audit Rev.01', 
'GHP Audit Rev.01', 
'Inbound Process Audit Rev.01', 
'Inventory QC (DEQ) Audit Rev.01', 
'Legal Compliance Audit Rev.01', 
'Material Handling Audit Rev.01', 
'RC Audit Rev.01', 
'Staging / Stacking Audit Rev.01', 
'Inventory CC Audit Rev.01', 
'Revised GHP Audit', 
'Revised DH Beat Ops', 
'Revised DH Process Audit - Part 1', 
'Revised DH Process Audit - Part 2', 
'Revised DH Material Handling Audit'
  )
  and audit_date between @{{:Zepto DH Audit Details.Date Range.START}}::timestamp and @{{:Zepto DH Audit Details.Date Range.END}}::timestamp + interval ' 1 day')
SELECT organization_id AS "Org",
       store_id AS "Location",
	   audit_type as "Type",
       audit_main_theme AS "Audit",
       audit_date AS "Audit Date",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
       auditor_name AS "Auditor",
       sum(result_score) as "Actual Score",
	   sum(max_score) as "Max Score",
	   sum(result_score)/sum(max_score) AS "Audit Score",
       count(CASE
                 WHEN criticality = 'Critical' and result_score < max_score and result_score is not null THEN checkpoint_knid
                 ELSE NULL
             END) AS "Critical Failed Count",
       sum(total_follow_up_tasks) AS "Total Follow Ups",
       sum(total_closed_follow_up_tasks) AS "Total Closed Follow Ups",
       "Audit No in Year"
FROM location_acl acl
LEFT OUTER JOIN base ON acl.job_location = base.store_id
group by 1, 2, 3, 4, 5, 6, 7, 8, 15
ORDER BY 1,
         2,
         3, 5
```

---

## Zepto DH MH LMS Pilot_Learn.sql

**Tables referenced:** looker.tmp_zds_learn

**Original Query:**

```sql
-- Data Source: Zepto DH MH LMS Pilot
-- Dashboard: Learn
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:57:41
-- ============================================================

select * from looker.tmp_zds_learn
```

---

## Zepto DH Product n Packaging_Zepto DH Pulses.sql

**Tables referenced:** base, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, metadata, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions

**Columns needing snake_case conversion:**

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `userName` -> `user_name` (alias: `user_name AS "userName"`)


**Original Query:**

```sql
-- Data Source: Zepto DH Product n Packaging
-- Dashboard: Zepto DH Pulses
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:59:07
-- ============================================================

WITH /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ILIKE 'Product & Packaging%'
     AND title NOT LIKE '%RM%'
     AND title NOT ILIKE '%Supplier%'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT forms.organization,
                                                                  nugget_id AS form_knid,
                                                                  form_name,
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
                                                                  question AS parent_question,
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
   WHERE qd.definition -> 'logic' IS NOT NULL
     AND jsonb_typeof(definition -> 'logic') = 'array'
   UNION SELECT *,
                definition -> 'logic' -> 'questions' q
   FROM forms
   JOIN question_definitions qd ON qd.nugget_id = forms.form_knid
   WHERE qd.definition -> 'logic' IS NOT NULL
     AND jsonb_typeof(definition -> 'logic') != 'array'),
                                                                                       qd_non_table_with_logic AS
  (/*Non Table type Questions in Forms with Logic - SqNo will be in between the parent SqNo for sub questions*/ SELECT qd.organization,
                                                                                                                       nugget_id AS form_knid,
                                                                                                                       form_name,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question AS parent_question,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
                                                                                       qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT forms.organization,
                                                                                                        nugget_id AS form_knid,
                                                                                                        form_name,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question AS parent_question,
                                                                                                        question_type AS parent_q_type,
                                                                                                        def.key AS qid,
                                                                                                        def.value->>'question_type' AS q_type,
                                                                                                                    (def.value->>'question') AS question
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
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   ORDER BY response_id,
            id DESC),
                                                                                       fr AS
  (SELECT form_submit_id,
          form_id,
          sno,
          submit_Date AT TIME ZONE 'Asia/Kolkata' AS submitted_At,
                                   user_id,
                                   response_id,
                                   question_id AS parent_qid,
                                   question_id AS qid,
                                   question_type,
                                   response,
                                   1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                sno,
                submitted_At,
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
             sno,
             submit_Date AT TIME ZONE 'Asia/Kolkata' AS submitted_At,
                                      user_id,
                                      response_id,
                                      question_id,
                                      question_type,
                                      base.value,
                                      base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
                                                                                     base AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.parent_question,
          fd.question,
          fd.q_type,
          rn,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Kolkata', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature') THEN fr.response ->> 'name'
              ELSE NULL
          END AS response,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS section_response,
          form_name,
          fd.form_knid,
          fr.response_id AS form_response_knid
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
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
            12
   ORDER BY 1,
            2,
            3,
            6),
                                                                                     metadata AS
  (SELECT form_response_knid,
          sno AS "Audit No",
          to_timestamp(((max(CASE
                                 WHEN section_response IS NOT NULL THEN section_response ->> 'sentAt'
                                 ELSE NULL
                             END))::bigint)/1000) AT TIME ZONE 'Asia/Kolkata' AS "Audited At",
                                                               max(CASE
                                                                       WHEN section_response IS NOT NULL THEN section_response -> 'sender' ->> 'userName'
                                                                       ELSE NULL
                                                                   END) AS "Auditor",
                                                               max(CASE
                                                                       WHEN question = 'PO Number' THEN response
                                                                       ELSE NULL
                                                                   END) AS "PO Number",
                                                               max(CASE
                                                                       WHEN question = 'Commodity' THEN response
                                                                       ELSE NULL
                                                                   END) AS "Commodity",
                                                               max(CASE
                                                                       WHEN question ='Date of Packaing (Calender Option)' THEN response
                                                                       ELSE NULL
                                                                   END) AS "Date of Packaging",
                                                               max(CASE
                                                                       WHEN question = 'Use By Date (Calender Option)' THEN response
                                                                       ELSE NULL
                                                                   END) AS "Use By Date",
                                                               max(CASE
                                                                       WHEN question = 'Lot No.' THEN response
                                                                       ELSE NULL
                                                                   END) AS "Lot No.",
                                                               max(CASE
                                                                       WHEN question LIKE 'Dispatch Location%' THEN response
                                                                       ELSE NULL
                                                                   END) AS "Dispatch Location",
                                                               max(CASE
                                                                       WHEN question ILIKE 'Total QTY as per PO' THEN response
                                                                       ELSE NULL
                                                                   END) AS "Total QTY as per PO",
                                                               max(CASE
                                                                       WHEN question ILIKE 'Total QTY. produced' THEN response
                                                                       ELSE NULL
                                                                   END) AS "Total QTY produced"
   FROM base
   GROUP BY 1,
            2)
SELECT metadata.form_response_knid,
       metadata."Audit No",
       metadata."Audited At",
       metadata."Auditor",
       metadata."PO Number",
       metadata."Commodity",
       to_date(metadata."Date of Packaging", 'YYYY-MM-DD') AS "Date of Packaging",
       to_Date(metadata."Use By Date", 'YYYY-MM-DD') AS "Use By Date",
       metadata."Lot No.",
       metadata."Dispatch Location",
       metadata."Total QTY as per PO",
       metadata."Total QTY produced",
       count(CASE
                 WHEN question = 'Score'
                      AND response != 'N.A.' THEN response
                 ELSE NULL
             END) AS "Total Attributes Checked",
       count(CASE
                 WHEN question = 'Score'
                      AND response = '1' THEN response
                 ELSE NULL
             END) AS "Total Attributes Passed",
       count(CASE
                 WHEN question = 'Score'
                      AND response = '0' THEN response
                 ELSE NULL
             END) AS "Total Attributes Failed",
       count(CASE
                 WHEN question = 'Score'
                      AND response != 'N.A.'
                      AND left(question, 1) = '*' THEN response
                 ELSE NULL
             END) AS "Critical Attributes Checked",
       count(CASE
                 WHEN question = 'Score'
                      AND response = '1'
                      AND left(question, 1) = '*' THEN response
                 ELSE NULL
             END) AS "Critical Attributes Passed",
       count(CASE
                 WHEN question = 'Score'
                      AND response = '0'
                      AND left(question, 1) = '*' THEN response
                 ELSE NULL
             END) AS "Critical Attributes Failed"
FROM metadata
LEFT JOIN base ON metadata.form_response_knid = base.form_response_knid
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
         12
ORDER BY 2 DESC,
         1,
         4,
         5
```

---

## Zepto DH Pulses Attributes Data_Zepto DH Pulses.sql

**Tables referenced:** base, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, metadata, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions

**Columns needing snake_case conversion:**

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `submittedByUserName` -> `submitted_by_user_name` (alias: `submitted_by_user_name AS "submittedByUserName"`)


**Original Query:**

```sql
-- Data Source: Zepto DH Pulses Attributes Data
-- Dashboard: Zepto DH Pulses
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:59:27
-- ============================================================

WITH /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id IN ('-NrKM5y9AZQQvjwXz8f1')), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT nugget_id AS form_knid,
                                                                  form_name,
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
                                                                  question AS parent_question,
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
                                                                                                                       form_name,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question AS parent_question,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
                                                                                       qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT nugget_id AS form_knid,
                                                                                                        form_name,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question AS parent_question,
                                                                                                        question_type AS parent_q_type,
                                                                                                        def.key AS qid,
                                                                                                        def.value->>'question_type' AS q_type,
                                                                                                                    (def.value->>'question') AS question
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
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   ORDER BY response_id,
            id DESC),
                                                                                       fr AS
  (SELECT form_submit_id,
          sno,
          response_id,
          question_id AS parent_qid,
          question_id AS qid,
          response,
          1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                sno,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             sno,
             response_id,
             question_id,
             base.value,
             base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res), base as (
SELECT fr.sno,
       fd.section_no,
       fd.q_no,
       fd.parent_question,
       fd.question,
	   fd.q_type,
       rn,
       CASE
           WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
           WHEN fd.q_type IN ('dropdown',
                              'multiple_choice',
                              'checkboxes') THEN fr.response -> 'selected'->>0
           WHEN fd.q_type IN ('date',
                              'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Dubai', 'YYYY-MM-DD HH24:MI:SS')
           WHEN fd.q_type IN ('long_text_field',
                              'single_text_field',
                              'qr_code') THEN fr.response->>0
           WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
           WHEN fd.q_type IN ('signature') THEN fr.response ->> 'name'
           ELSE NULL
       END AS response,
       CASE
           WHEN fd.q_type = 'section' THEN fr.response
           ELSE NULL
       END AS section_response,
       form_name,
       fd.form_knid,
       fr.response_id AS form_response_knid
FROM final_definition fd
JOIN fr ON fr.qid = fd.qid
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
         11,12
		 
ORDER BY 1,
         2,
         3,
         6), metadata as (
		 
		 select form_response_knid, sno as "Audit No", to_timestamp(((max(Case when section_response is not null then section_response ->> 'sentAt' else null end))::bigint)/1000) at time zone 'Asia/Kolkata' as "Audited At",
		 max(Case when section_response is not null then section_response ->> 'submittedByUserName' else null end) as "Auditor",
		 max(case when question = 'PO Number' then response else null end) as "PO Number",
		 max(case when question = 'Item Name' then response else null end) as "Item Name",
		    max(case when question ='Date of Packaging' then response else null end) as "Date of Packaging",
		    max(case when question = 'Use By Date' then response else null end) as "Use By Date",
		    max(case when question = 'Lot No.' then response else null end) as "Lot No.",
		    max(case when question = 'Dispatch Location' then response else null end) as "Dispatch Location",
		    max(case when question = 'Total QTY as per PO' then response else null end) as "Total QTY as per PO",
		    max(case when question = 'Total QTY produced' then response else null end) as "Total QTY produced"
		  
		 from base
		 group by 1, 2)
		 select metadata.form_response_knid, metadata."Audit No", 
		 /*metadata."Audited At", metadata."Auditor", */
		 metadata."PO Number", metadata."Item Name", 
		 /*metadata."Date of Packaging", metadata."Use By Date", metadata."Lot No.", metadata."Dispatch Location", metadata."Total QTY as per PO", metadata."Total QTY produced",*/
		 base.question, base.response, base.q_type
		 from metadata
		 left join base on metadata.form_response_knid = base.form_response_knid
		 where base.parent_question = 'Item Name'
		 order by 2 desc, 1, 4, 5
```

---

## Zepto L and D Productivity_Zepto - L and D Productivity dashboard.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Zepto L and D Productivity
-- Dashboard: Zepto - L and D Productivity dashboard
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:54:22
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Zds-indus'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike ('%Daily Training Update-DH L&D%')
     AND organization = 'Zds-indus'
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
        where submit_date >= '2025-09-07'
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
          1 AS rn,
          location
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
                rn,
                location
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
             base.ordinality AS rn,
             location
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id
      JOIN td ON fs.organization = td.organization,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
   /*location_questions as (
select distinct on (nugget_id) nugget_id, question_id from question_definitions qd 
where nugget_id in (select form_knid from forms)
and question_type = 'location'
order by nugget_id, section_id, sqno
),
location_response as (
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
          fd.qid,
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
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          ud.first_name as name
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   join user_details ud on fr.user_id = ud.uuid
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
            14,15,16
   ORDER BY 1,
            2,
            3)
            select sno,submit_date,
            MAX(CASE WHEN question ILIKE '%Select Your Name%' THEN response END) AS "Select Your Name",
MAX(CASE WHEN question ILIKE '%City Name%' THEN response END) AS "City Name",
MAX(CASE WHEN question ILIKE '%Delivery Hub Name%' THEN response END) AS "Delivery Hub Name",
MAX(CASE WHEN question ILIKE '%Select Zone%' THEN response END) AS "Select Zone",
MAX(CASE WHEN question ILIKE '%Date of Visit%' THEN response END) AS "Date of Visit",
MAX(CASE WHEN question ILIKE '%Your Attendance for the Day%' THEN response END) AS "Your Attendance for the Day",
MAX(CASE WHEN question ILIKE '%Time Spent on New Hire Induction Including LBD Sessions (In Hours)%' 
         THEN response::numeric END) AS "Time Spent on New Hire Induction Including LBD Sessions In Hours",
MAX(CASE WHEN q_no = 80000 AND question ILIKE '%Select Mode%' THEN response END) AS "Select Mode 1",
MAX(CASE WHEN q_no = 90000 AND question ILIKE '%Audience Covered%' THEN response::numeric END) AS "Audience Covered 1",
MAX(CASE WHEN question ILIKE '%Time Spent on New Product & Process Training (In Hours)%' THEN response::numeric END) AS "Time Spent on New Product & Process Training In Hours",
MAX(CASE WHEN q_no = 110000 AND question ILIKE '%Select Mode%' THEN response END) AS "Select Mode 2",
MAX(CASE WHEN q_no = 120000 AND question ILIKE '%Audience Covered%' THEN response::numeric END) AS "Audience Covered 2",
MAX(CASE WHEN question ILIKE '%New Product/Process Training Topic%' THEN response END) AS "New Product/Process Training Topic",
MAX(CASE WHEN question ILIKE '%Time Spent on Refresher Training (In Hours)%' THEN response::numeric END) AS "Time Spent on Refresher Training In Hours",
MAX(CASE WHEN q_no = 150000 AND question ILIKE '%Select Mode%' THEN response END) AS "Select Mode 3",
MAX(CASE WHEN q_no = 160000 AND question ILIKE '%Audience Covered%' THEN response::numeric END) AS "Audience Covered 3",
MAX(CASE WHEN question ILIKE '%Refresher Training Topic%' THEN response END) AS "Refresher Training Topic",
MAX(CASE WHEN question ILIKE '%Time Spent on Special Focused Training (In Hours)%' THEN response::numeric END) AS "Time Spent on Special Focused Training In Hours",
MAX(CASE WHEN q_no = 190000 AND question ILIKE '%Select Mode%' THEN response END) AS "Select Mode 4",
MAX(CASE WHEN q_no = 200000 AND question ILIKE '%Audience Covered%' THEN response::numeric END) AS "Audience Covered 4",
MAX(CASE WHEN question ILIKE '%Special Project Training Topic%' THEN response END) AS "Special Project Training Topic",
MAX(CASE WHEN question ILIKE '%Time Spent on LMS Follow Up (In Hours)%' THEN response::numeric END) AS "Time Spent on LMS Follow Up In Hours",
MAX(CASE WHEN question ILIKE '%Name of the Courses (Mention Exact Name as per Know LMS)%' THEN response END) AS "Name of the Courses Mention Exact Name as per Know LMS",
MAX(CASE WHEN question ILIKE '%Time Spent on MIS Update/Know App Daily Update%' THEN response::numeric END) AS "Time Spent on MIS Update/Know App Daily Update",
MAX(CASE WHEN question ILIKE '%Time Spent on Training Meets/Team Meetings/Review Meets (In Hours)%' THEN response::numeric END) AS "Time Spent on Training Meets/Team Meetings/Review Meets In Hours",
MAX(CASE WHEN question ILIKE '%Time Spent on Content Creation (PPT/Video/Voice over/Script review etc) In Hours%' THEN response::numeric END) AS "Time Spent on Content Creation PPT/Video/Voice over/Script review etc In Hours",
MAX(CASE WHEN question ILIKE '%Time Spent on Any Other Activity Not Listed Above ( In Hours)%' THEN response::numeric END) AS "Time Spent on Any Other Activity Not Listed Above  In Hours",
MAX(CASE WHEN question ILIKE '%Mention the Activity Name%' THEN response END) AS "Mention the Activity Name",
MAX(CASE WHEN question ILIKE '%Total Productive Time for the Day (In Hours)%' THEN response::numeric END) AS "Total Productive Time for the Day In Hours"
            from raw
            group by 1,2
```

---

## Zepto Maintenance Issue Ticket Daily Report_Zepto Ticket Daily Report.sql

**Tables referenced:** issue_ticketing_form_data

**Original Query:**

```sql
-- Data Source: Zepto Maintenance Issue Ticket Daily Report
-- Dashboard: Zepto Ticket Daily Report
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:57:40
-- ============================================================

select * from issue_ticketing_form_data
where "Raised At" > date_trunc('Month', current_timestamp - interval '6 months')
order by "Raised At" desc
```

---

## Zepto Maintenance Issue Ticketing_Zepto Ticket Management Old.sql

**Tables referenced:** issue_ticketing_form_data

**Original Query:**

```sql
-- Data Source: Zepto Maintenance Issue Ticketing
-- Dashboard: Zepto Ticket Management Old
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:56:44
-- ============================================================

select * from issue_ticketing_form_data
where "Raised At" between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp
order by "Raised At" desc
```

---

## Zepto Maintenance Issue Ticketing_Zepto Ticket Management.sql

**Tables referenced:** issue_ticketing_form_data

**Original Query:**

```sql
-- Data Source: Zepto Maintenance Issue Ticketing
-- Dashboard: Zepto Ticket Management
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:56:44
-- ============================================================

select * from issue_ticketing_form_data
where "Raised At" between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp
order by "Raised At" desc
```

---

## Zepto Pending HK Tickets_Zepto Pending HK Tickets.sql

**Tables referenced:** LATERAL, RAW, final_definition, form_responses, form_submissions, forms, fr, fs, issue_ticketing_form_data, latest_section, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, tickets

**Columns needing snake_case conversion:**

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `userName` -> `user_name` (alias: `user_name AS "userName"`)


**Original Query:**

```sql
-- Data Source: Zepto Pending HK Tickets
-- Dashboard: Zepto Pending HK Tickets
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:56:08
-- ============================================================

WITH forms AS
  (SELECT n.organization,
          n.id AS form_knid,
          n.title AS form_name
   FROM nuggets n
   WHERE n.title::text ~~* 'FM - Zepto Ticketing Management%'::text
     AND n.classification_type::text = 'form'::text ),
     qd_non_table_non_logic AS
  (SELECT forms.organization,
          qd.nugget_id AS form_knid,
          forms.form_name,
          CASE
              WHEN qd.section_id::text = 'section'::text THEN 1
              ELSE replace(qd.section_id::text, 'section-'::text, ''::text)::integer
          END AS section_no,
          CASE
              WHEN qd.question_type::text = 'section'::text THEN 0
              ELSE qd.sqno::integer * 10000
          END AS q_no,
          qd.section_id,
          qd.question_id AS parent_qid,
          qd.question AS parent_question,
          qd.question_type AS parent_q_type,
          qd.question_id AS qid,
          qd.question_type AS q_type,
          qd.question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid::text = qd.nugget_id::text
   WHERE qd.question_type::text <> 'table'::text ),
     qdntwl_prework AS
  (SELECT forms.organization,
          forms.form_knid,
          forms.form_name,
          qd.nugget_id,
          qd.question_id,
          qd.question,
          qd.question_type,
          qd.sqno,
          qd.definition,
          qd.created_at,
          qd.section_id,
          jsonb_array_elements(qd.definition -> 'logic'::text) -> 'questions'::text AS q
   FROM forms
   JOIN question_definitions qd ON qd.nugget_id::text = forms.form_knid::text
   WHERE (qd.definition -> 'logic'::text) IS NOT NULL ),
     qd_non_table_with_logic AS
  (SELECT qd.organization,
          qd.nugget_id AS form_knid,
          qd.form_name,
          CASE
              WHEN qd.section_id::text = 'section'::text THEN 1
              ELSE replace(qd.section_id::text, 'section-'::text, ''::text)::integer
          END AS section_no,
          qd.sqno::integer * 10000 + ((def.value ->> 'order'::text)::integer) AS q_no,
          qd.section_id,
          qd.question_id AS parent_qid,
          qd.question AS parent_question,
          qd.question_type AS parent_q_type,
          def.key AS qid,
          def.value ->> 'question_type'::text AS q_type,
                        def.value ->> 'question'::text AS question
   FROM qdntwl_prework qd
   CROSS JOIN LATERAL jsonb_each(qd.q) def(KEY, value)
   WHERE (qd.definition ->> 'logic'::text) IS NOT NULL ),
     qd_table AS
  (SELECT forms.organization,
          qd.nugget_id AS form_knid,
          forms.form_name,
          CASE
              WHEN qd.section_id::text = 'section'::text THEN 1
              ELSE replace(qd.section_id::text, 'section-'::text, ''::text)::integer
          END AS section_no,
          qd.sqno::integer * 10000 + ((def.value ->> 'order'::text)::integer) AS q_no,
          qd.section_id,
          qd.question_id AS parent_qid,
          qd.question AS parent_question,
          qd.question_type AS parent_q_type,
          def.key AS qid,
          def.value ->> 'question_type'::text AS q_type,
                        def.value ->> 'question'::text AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid::text = qd.nugget_id::text
   CROSS JOIN LATERAL jsonb_each(qd.definition -> 'questions'::text) def(KEY, value)
   WHERE qd.question_type::text = 'table'::text ),
     final_definition AS
  (SELECT qd_non_table_non_logic.organization,
          qd_non_table_non_logic.form_knid,
          qd_non_table_non_logic.form_name,
          qd_non_table_non_logic.section_no,
          qd_non_table_non_logic.q_no,
          qd_non_table_non_logic.section_id,
          qd_non_table_non_logic.parent_qid,
          qd_non_table_non_logic.parent_question,
          qd_non_table_non_logic.parent_q_type,
          qd_non_table_non_logic.qid,
          qd_non_table_non_logic.q_type,
          qd_non_table_non_logic.question
   FROM qd_non_table_non_logic
   UNION SELECT qd_non_table_with_logic.organization,
                qd_non_table_with_logic.form_knid,
                qd_non_table_with_logic.form_name,
                qd_non_table_with_logic.section_no,
                qd_non_table_with_logic.q_no,
                qd_non_table_with_logic.section_id,
                qd_non_table_with_logic.parent_qid,
                qd_non_table_with_logic.parent_question,
                qd_non_table_with_logic.parent_q_type,
                qd_non_table_with_logic.qid,
                qd_non_table_with_logic.q_type,
                qd_non_table_with_logic.question
   FROM qd_non_table_with_logic
   UNION SELECT qd_table.organization,
                qd_table.form_knid,
                qd_table.form_name,
                qd_table.section_no,
                qd_table.q_no,
                qd_table.section_id,
                qd_table.parent_qid,
                qd_table.parent_question,
                qd_table.parent_q_type,
                qd_table.qid,
                qd_table.q_type,
                qd_table.question
   FROM qd_table
   ORDER BY 1,
            2,
            3,
            5 DESC, 7 DESC),
     fs AS
  (SELECT DISTINCT ON (form_submissions.response_id) forms.organization,
                      forms.form_knid,
                      forms.form_name,
                      form_submissions.id,
                      form_submissions.organization,
                      form_submissions.form_id,
                      form_submissions.user_id,
                      form_submissions.submit_date,
                      form_submissions.sno,
                      form_submissions.response_id,
                      form_submissions.location,
                      form_submissions.in_progress,
                      form_submissions.location_id,
                      form_submissions.is_edited,
                      form_submissions.parent_nugget_id,
                      form_submissions.started_at,
                      form_submissions.approx_distance_in_km
   FROM forms
   JOIN form_submissions ON forms.form_knid::text = form_submissions.form_id::text
   WHERE form_submissions.submit_date AT TIME ZONE 'Asia/Kolkata' >= CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '1 day'
   ORDER BY form_submissions.response_id,
            form_submissions.id DESC),
     fr AS
  (SELECT fr.form_submit_id,
          fs.form_id,
          fs.location,
          fs.sno,
          (fs.submit_date AT TIME ZONE 'Asia/Kolkata'::text) AS submitted_at,
          fs.user_id,
          fs.response_id,
          fr.question_id AS parent_qid,
          fr.question_id AS qid,
          fr.response,
          1 AS rn
   FROM form_responses fr
   JOIN fs fs(organization, form_knid, form_name, id, organization_1, form_id, user_id, submit_date, sno, response_id, LOCATION, in_progress, location_id, is_edited, parent_nugget_id, started_at, approx_distance_in_km) ON fs.id = fr.form_submit_id
   WHERE fr.question_type::text <> ALL (ARRAY['table'::character varying::text,
                                              'nested'::character varying::text])
   UNION SELECT base1.form_submit_id,
                base1.form_id,
                base1.location,
                base1.sno,
                base1.submitted_at,
                base1.user_id,
                base1.response_id,
                base1.question_id AS parent_qid,
                res.key AS qid,
                res.value AS response,
                base1.rn
   FROM
     (SELECT fr.form_submit_id,
             fs.form_id,
             fs.location,
             fs.sno,
             (fs.submit_date AT TIME ZONE 'Asia/Kolkata'::text) AS submitted_at,
             fs.user_id,
             fs.response_id,
             fr.question_id,
             base.value,
             base.ordinality AS rn
      FROM form_responses fr
      JOIN fs fs(organization, form_knid, form_name, id, organization_1, form_id, user_id, submit_date, sno, response_id, LOCATION, in_progress, location_id, is_edited, parent_nugget_id, started_at, approx_distance_in_km) ON fs.id = fr.form_submit_id,
                                                                                                                                                                                                                                 LATERAL jsonb_array_elements(fr.response) WITH
      ORDINALITY base(value,
                      ORDINALITY)
      WHERE fr.question_type::text = 'table'::text) base1
   CROSS JOIN LATERAL jsonb_each(base1.value) res(KEY, value)),
     RAW AS
  (SELECT fd.organization,
          fr.location,
          fd.form_name,
          fr.submitted_at,
          fr.sno AS ticket_id,
          fd.section_no,
          fd.q_no,
          fd.parent_question,
          fd.question,
          fr.rn,
          CASE
              WHEN fd.q_type::text = 'section'::text THEN fr.response ->> 'status'::text
              WHEN fd.q_type::text = 'sub_division'::text THEN fr.response ->> 'name'::text
              WHEN fd.q_type::text = ANY (ARRAY['dropdown'::character varying::text,
                                                'multiple_choice'::character varying::text,
                                                'checkboxes'::character varying::text]) THEN (fr.response -> 'selected'::text) ->> 0
              WHEN fd.q_type::text = ANY (ARRAY['date'::character varying::text,
                                                'datetime'::character varying::text]) THEN to_char((to_timestamp((fr.response::bigint / 1000)::double precision) AT TIME ZONE 'Asia/Kolkata'::text), 'YYYY-MM-DD HH24:MI:SS'::text)
              WHEN fd.q_type::text = ANY (ARRAY['long_text_field'::character varying::text,
                                                'single_text_field'::character varying::text,
                                                'qr_code'::character varying::text,
                                                'formula'::character varying::text]) THEN fr.response ->> 0
              WHEN fd.q_type::text = 'upload_mixed'::text THEN (fr.response -> 0) ->> 'response'::text
              WHEN fd.q_type::text = ANY (ARRAY['signature'::character varying::text,
                                                'location'::character varying::text]) THEN fr.response ->> 'name'::text
              ELSE NULL::text
          END AS response,
          CASE
              WHEN fd.q_type::text = 'section'::text THEN fr.response
              ELSE NULL::jsonb
          END AS section_response,
          fr.user_id,
          fd.form_knid,
          fr.response_id AS form_response_knid
   FROM final_definition fd
   JOIN fr ON fr.qid::text = fd.qid::text
   AND fd.form_knid::text = fr.form_id::text
   GROUP BY fd.organization,
            fr.location,
            fd.form_name,
            fr.submitted_at,
            fr.sno,
            fd.section_no,
            fd.q_no,
            fd.parent_question,
            fd.question,
            fr.rn, (CASE
                        WHEN fd.q_type::text = 'section'::text THEN fr.response ->> 'status'::text
                        WHEN fd.q_type::text = 'sub_division'::text THEN fr.response ->> 'name'::text
                        WHEN fd.q_type::text = ANY (ARRAY['dropdown'::character varying::text,
                                                          'multiple_choice'::character varying::text,
                                                          'checkboxes'::character varying::text]) THEN (fr.response -> 'selected'::text) ->> 0
                        WHEN fd.q_type::text = ANY (ARRAY['date'::character varying::text,
                                                          'datetime'::character varying::text]) THEN to_char((to_timestamp((fr.response::bigint / 1000)::double precision) AT TIME ZONE 'Asia/Kolkata'::text), 'YYYY-MM-DD HH24:MI:SS'::text)
                        WHEN fd.q_type::text = ANY (ARRAY['long_text_field'::character varying::text,
                                                          'single_text_field'::character varying::text,
                                                          'qr_code'::character varying::text,
                                                          'formula'::character varying::text]) THEN fr.response ->> 0
                        WHEN fd.q_type::text = 'upload_mixed'::text THEN (fr.response -> 0) ->> 'response'::text
                        WHEN fd.q_type::text = ANY (ARRAY['signature'::character varying::text,
                                                          'location'::character varying::text]) THEN fr.response ->> 'name'::text
                        ELSE NULL::text
                    END), (CASE
                               WHEN fd.q_type::text = 'section'::text THEN fr.response
                               ELSE NULL::jsonb
                           END), fr.user_id,
                                 fd.form_knid,
                                 fr.response_id), latest_section AS
  (SELECT base.form_response_knid,
          base.section_no,
          base.section_response
   FROM
     (SELECT raw_1.form_response_knid,
             raw_1.section_no,
             raw_1.section_response,
             row_number() OVER (PARTITION BY raw_1.form_response_knid
                                ORDER BY raw_1.section_no DESC) AS rn
      FROM RAW raw_1
      WHERE raw_1.q_no = 0
        AND raw_1.section_response IS NOT NULL) base
   WHERE base.rn = 1 ),
                                                  tickets AS
  (SELECT raw.ticket_id AS "Ticket ID",
          max(CASE
                  WHEN raw.section_no = 1
                       AND raw.q_no = 0 THEN (to_timestamp((((raw.section_response ->> 'sentAt'::text)::bigint) / 1000)::double precision) AT TIME ZONE 'Asia/Kolkata'::text)
                  ELSE NULL::TIMESTAMP WITHOUT TIME ZONE
              END) AS "Raised At",
          max(CASE
                  WHEN raw.section_no = 5
                       AND raw.q_no = 0
                       AND (raw.response = ANY (ARRAY['submitted'::text, 'sent'::text, 'approved'::text])) THEN '5 - Acknowledged & Closed'::text
                  WHEN raw.section_no = 4
                       AND raw.q_no = 0
                       AND (raw.response = ANY (ARRAY['submitted'::text, 'sent'::text, 'approved'::text])) THEN '4 - Action Completed'::text
                  WHEN raw.section_no = 3
                       AND raw.q_no = 0
                       AND (raw.response = ANY (ARRAY['submitted'::text, 'sent'::text, 'approved'::text])) THEN '3 - Action Pending'::text
                  WHEN raw.section_no = 3
                       AND raw.q_no = 0
                       AND raw.response = 'rejected'::text THEN '2.5 - Cost Rejected'::text
                  WHEN raw.section_no = 2
                       AND raw.q_no = 0
                       AND (raw.response = ANY (ARRAY['submitted'::text, 'sent'::text, 'approved'::text])) THEN '2 - Quotation Submitted. Approval Pending'::text
                  WHEN raw.section_no = 1
                       AND raw.q_no = 0
                       AND (raw.response = ANY (ARRAY['submitted'::text, 'sent'::text, 'approved'::text])) THEN '1 - First Response Pending'::text
                  ELSE '0 - Pending'::text
              END) AS "Status",
          (((latest_section.section_response -> 'receiver'::text) ->> 'userName'::text) || ', ID: '::text) || ((latest_section.section_response -> 'receiver'::text) ->> 'identifier'::text) AS "Pending with",
          max(CASE
                  WHEN raw.section_no = 1
                       AND raw.question::text = 'Please enter your name'::text THEN raw.response
                  ELSE NULL::text
              END) AS "Raised By",
          max(CASE
                  WHEN raw.section_no = 1
                       AND raw.question::text = 'Please enter you phone number'::text THEN raw.response
                  ELSE NULL::text
              END) AS "Raised By (Ph)",
          max(CASE
                  WHEN raw.section_no = 1
                       AND raw.question::text = 'Facility Type'::text THEN raw.response
                  ELSE NULL::text
              END) AS "Facility Type",
          max(CASE
                  WHEN raw.section_no = 1
                       AND raw.question::text = 'City Name'::text THEN raw.response
                  ELSE NULL::text
              END) AS "City",
          max(CASE
                  WHEN raw.section_no = 1
                       AND (raw.question::text = ANY (ARRAY['DH Name'::character varying::text, 'Facility Name'::character varying::text])) THEN raw.response
                  ELSE NULL::text
              END) AS "DH Name",
          max(CASE
                  WHEN raw.section_no = 1
                       AND raw.question::text = 'Requirement Category'::text THEN raw.response
                  ELSE NULL::text
              END) AS "Category",
          max(CASE
                  WHEN raw.section_no = 1
                       AND raw.question::text = 'Sub Category'::text THEN raw.response
                  ELSE NULL::text
              END) AS "Sub Category",
          max(CASE
                  WHEN raw.section_no = 1
                       AND raw.question::text = 'Describe issue in detail'::text THEN raw.response
                  ELSE NULL::text
              END) AS "Details"
   FROM RAW
   LEFT JOIN latest_section ON raw.form_response_knid::text = latest_section.form_response_knid::text
   GROUP BY raw.ticket_id, ((((latest_section.section_response -> 'receiver'::text) ->> 'userName'::text) || ', ID: '::text) || ((latest_section.section_response -> 'receiver'::text) ->> 'identifier'::text))
   UNION SELECT "Ticket ID",
                "Raised At",
                "Status",
                "Pending with",
                "Raised By",
                "Raised By (Ph)",
                "Facility Type",
                "City",
                "DH Name",
                "Category",
                "Sub Category",
                "Details"
   FROM issue_ticketing_form_data
   WHERE "Category" IN ('Garbage Pickup Required',
                        'Housekeeping')
     AND "Raised At" < CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '1 day')
SELECT *
FROM tickets
WHERE "Category" IN ('Garbage Pickup Required',
                     'Housekeeping')
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
         12
ORDER BY 1,
         3 DESC,
         2
```

---

## Zepto Scorm Dashboard_Scorm Course Report.sql

**Tables referenced:** analytics.nuggets_user_share_requests, c, courses, scorm_data, scorm_progress, shares, suspend_data.progress, u, user_details

**Columns needing snake_case conversion:**

- `isCompleted` -> `is_completed` (alias: `is_completed AS "isCompleted"`)


**Original Query:**

```sql
-- Data Source: Zepto Scorm Dashboard
-- Dashboard: Scorm Course Report
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:52:21
-- ============================================================

WITH scorm_data AS
  (SELECT parent_id AS course_id,
          user_id, -- Status based on suspend_data.progress.isCompleted
 CASE
     WHEN (suspend_data::jsonb -> 'progress' ->> 'isCompleted')::BOOLEAN = TRUE THEN 'Completed'
     ELSE 'In Progress'
 END AS status, -- Progress % from suspend_data.progress.percentage (handle empty strings)
 ROUND(NULLIF(suspend_data::jsonb -> 'progress' ->> 'percentage', '')::NUMERIC, 2) AS progress_pct, -- Score % (raw score / max score) (handle empty strings)
 ROUND((NULLIF(progress::jsonb -> 'score' ->> 'raw', '')::NUMERIC / NULLIF(NULLIF(progress::jsonb -> 'score' ->> 'max', '')::NUMERIC, 0)) * 100, 2) AS score_pct, -- Completion timestamp
 CASE
     WHEN (suspend_data::jsonb -> 'progress' ->> 'isCompleted')::BOOLEAN = TRUE THEN updated_at AT TIME ZONE 'Asia/Kolkata'
     ELSE NULL
 END AS completed_at
   FROM scorm_progress
   WHERE parent_id = 'iYM1ho5UQcVvhNfS3ZNZNQ' ),
     shares AS
  (SELECT nugget_id,
          user_id,
          max(completed_at) AT TIME ZONE 'Asia/Kolkata' AS shared_at
   FROM analytics.nuggets_user_share_requests nusr
   WHERE nugget_id = 'iYM1ho5UQcVvhNfS3ZNZNQ'
   and completed_at AT TIME ZONE 'Asia/Kolkata'  between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
   GROUP BY 1,
            2),
     c AS
  (SELECT name,
          id AS course_id
   FROM courses
   WHERE id = 'iYM1ho5UQcVvhNfS3ZNZNQ' ),
     u AS
  (SELECT s.user_id,
          ud.first_name || ' ' || ud.last_name AS "Employee Name",
          ud.identifier AS "Employee ID",
          ud.division AS "Division",
          ud.sub_Division AS "Sub Division",
          ud.job_location AS "Location",
          ud.department AS "Department",
          ud.designation AS "Designation"
   FROM user_details ud
   JOIN shares s ON ud.uuid = s.user_id
   WHERE ud.email IS NULL
     OR ud.email NOT ILIKE '%knownuggets.com' )
SELECT
    s.user_id AS "User KNID",
    s.nugget_id AS "Course KNID",
    c.name AS "Course Name",

    COALESCE(u."Employee Name", '-') AS "Employee Name",
    COALESCE(u."Employee ID", '-') AS "Employee ID",
    COALESCE(u."Division", '-') AS "Division",
    COALESCE(u."Sub Division", '-') AS "Sub Division",
    COALESCE(u."Location", '-') AS "Location",
    COALESCE(u."Department", '-') AS "Department",
    COALESCE(u."Designation", '-') AS "Designation",

    s.shared_at AS "Enrolled At",

    CASE
        WHEN sd.status IS NOT NULL THEN sd.status
        ELSE 'Not Started'
    END AS "Completion Status",

    COALESCE(sd.completed_at::TEXT, '-') AS "Completed At",
    sd.progress_pct AS "Progress %",
    sd.score_pct AS "Score %"
FROM shares s
JOIN c ON s.nugget_id = c.course_id
JOIN u ON s.user_id = u.user_id
LEFT OUTER JOIN scorm_data sd ON s.nugget_id = sd.course_id
AND s.user_id = sd.user_id
ORDER BY 12,
         11,
         6,
         7,
         8,
         4
```

---

## Zepto ZBM MBR_QMS MBR.sql

**Tables referenced:** audit_date, current_timestamp, lm, zepto_qms_checkpoint_master_sheet_table

**Original Query:**

```sql
-- Data Source: Zepto ZBM MBR
-- Dashboard: QMS MBR
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:57:54
-- ============================================================

with lm as (select 'CHN_MADABK_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_TNAGAR_P01R1CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_NANGLR_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_NNDBKM_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_PRMBUR_P01R1CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_AMBTUR_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_PLKRNI_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_KELBKM_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_ADYAR_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_PERBKM_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_VNDLUR_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_KKNAGR_P01R1CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_MEDAVA_P01R1CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'BLR_INDNGR_P01R1CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_JPNGR_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_JYANGR_P01R1CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_BNSKRI_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_HEBBAL_P01R1CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_WHTFLD_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_BRKFLD_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_HENNUR_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_JAKKUR_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_SRJPUR_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_BDPLYT_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'DEL_KLKAJI_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_EOKLSH_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_VKSPUR_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_PSHMVR_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_PTMPUR_P01R1CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_KRLBGH_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_WZRPUR_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_VSNTKJ_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_JNKPRI_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'NOD_SEC117_P01R0CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'NOD_SEC63_P01R0CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_ARDCTY_P01R0CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_SEC66_P01R0CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'PUN_KHARDI_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'PUN_KRGPRK_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'PUN_BANER_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'PUN_KTHRUD_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'PUN_PMLSDG_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'BLR_RRNGR_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_BNRGTA_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_MCOLYT_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_BSNPUR_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_KLNNGR_P01R1CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_SNGSDR_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'MUM_AND(W)_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_AND(W)_N02R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_BANDRA_N02R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_BHNDUP_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_BOR(W)_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_CHMBUR_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_GHTKPR_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_KALYAN_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_KND(W)_P01R1CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_WAGHBL_N02R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_LOWPRL_P01R1FF' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_MAHIM_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_MALAD_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_MAROL_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_MAROL_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_MIRARD_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_BYNPAD_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_NALSPR_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'GZB_VSHALI_P01R0CC' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_SHKNGR_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_KRTNGR_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'GZB_INDPRM_P01R0CC' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select 'BLR_YLHNKA_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_SVJNGR_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_VIJNGR_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'MUM_VIRAR_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'DEL_MDLTWN_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_RHON15_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_NWFRCL_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'GZB_GAURCT_P01R0CC' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select 'GZB_RAJNGR_P01R0CC' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select 'GZB_RAJEXT_P01R0CC' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select 'NOD_SEC142_P01R0CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'KOL_NWTOWN_P01R0CC' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'KOL_PHLBGN_P01R0CC' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'PUN_AUNDH_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'KOL_JDVPUR_P01R0CC' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'HYD_SNKPRI_P01R1CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_TRNAKA_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_MHDPTM_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_RCPURM_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_ECIL_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_BEGMPT_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_MSHBAD_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_SCHTRA_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_UPPAL_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_KOTHPT_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_MOSAPT_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_BWNPLY_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_MIYPUR_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_VKDNGR_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_MADHAP_P01R1CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_GACBOW_P01R1CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_KNDPUR_N01R0FF' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_KUKTPL_P01R1CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_MOSAPT_N01R0FF' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_RMTPUR_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_JUBHIL_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_KNDPUR_P01R1CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_MADHAP_N01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_DMAGDA_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_HMYTNG_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_BCHPLY_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'NOD_SEC46_P01R0CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'CHN_TMBRAM_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_NAVLUR_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_MLPORE_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_GRUGBK_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_MUDCHR_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_MOGPAR_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_OTTERI_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'BLR_RCHMND_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_CVRNGR_P01R1CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_RGVLYT_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_KTHNUR_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'MUM_BELAPR_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_BHNDUP_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'DEL_MHVNCV_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'BLR_GUNJUR_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_YSHPUR_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_JLHALI_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'DEL_RHON03_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'BLR_BLNDUR_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'NOD_SEC73_P01R0CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_RKPURM_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_DWARKA_N01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_MYUVHR_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_ANDVHR_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_IPEXTN_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'MUM_BKC_P01R1CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_BORVLI_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_PAREL_N01R0FF' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_DMB(W)_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_GHTKPR_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'BLR_HSRLYT_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'GGN_ARDCTY_N01R0CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'PUN_NIBMRD_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'PUN_MGRPTA_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'PUN_HDPSAR_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'PUN_RAVET_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'MUM_GRG(E)_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'NOD_GAURCT_N01R0FF' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'MUM_AND(E)_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'GGN_SEC69_N01R0FF' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_SEC27_N01R0FF' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_ARDCTY_N02R0FF' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_SEC39_N02R0FF' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_UDYHVR_N01R0FF' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'BLR_NRYNPR_P01R0FF' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_SRJPUR_N01R0FF' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_KNMGLA_P01R0FF' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'CHN_ECR_P01R0FF' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'BLR_BTMLYT_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_WHTFLD_N01R0FF' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'CHN_GRUGBK_N01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'GGN_SEC82_P01R0FF' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_SEC104_P01R0FF' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'MUM_KOPKHA_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'GGN_SEC66_N01R0FF' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_SEC39_P01R1CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'CHN_ANANGR_P01R1FF' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'DEL_PSHMVR_N01R0FF' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_SEC12_P01R1FF' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'HYD_SCNDBD_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'NOD_SEC117_N01R0CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'NOD_SEC93_P01R0FF' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'CHN_PAMMAL_N01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_THORIP_P01R1FF' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'MUM_KOTARI_P01R1CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'CHN_SHOLIN_N01R0FF' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'BLR_HENNUR_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'HYD_NLGADL_P01R1CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_NZMPET_N01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'MUM_CHMBUR_N01R0FF' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_LOWPRL_N01R0FF' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'KOL_BARNGR_P01R0FF' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'CHN_MADABK_N01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'MUM_WAGHBL_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'NOD_JLVVHR_P01R0CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'BLR_MRTHAL_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'NOD_SEC73_N01R0CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'PUN_BVDHAN_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'CHN_VLCHRY_N01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'HYD_MNKOND_N01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_CHMPPT_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_MNKOND_P01R1CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_KOTHPT_N01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'PUN_BANER_N01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'NOD_BISRKH_P01R0CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'KOL_PRKSTR_P01R0FF' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'KOL_SHBPUR_P01R0CC' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'NOD_OMCRON_P01R0CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'BLR_HSRLYT_N02R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'NOD_SEC135_P01R0FF' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_VSNTKJ_N01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_MLVNGR_N01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'MUM_MALAD_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'GZB_INDPRM_N01R0FF' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select 'GZB_VSHALI_N01R0FF' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select 'HYD_BRMGDA_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'PUN_WGHOLI_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'BLR_SNHALI_P01R1CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_BMSNDR_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_BRKFLD_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_MCOLYT_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'DEL_DWARKA_N02R0FF' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'GZB_RAJEXT_N01R0CC' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_HYTPUR_P01R0CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_PLMVHR_P01R0CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'PUN_KHRADI_N01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'PUN_VIMNGR_P01R1CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'NOD_SECPI1_P01R0CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'KOL_NZIBAD_P01R0CC' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'KOL_MOTNGR_P01R0CC' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'MUM_MIRARD_P01R1CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'BLR_BNRGTA_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_BLNDUR_N02R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_JPNGR_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_CVRNGR_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'FBD_SEC21_P01R0CC' as store_id, 'FARIDABAD' as city, 'Sagar Upadhyay' as zbm
union select 'PUN_PMLSDG_N01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'CHN_SHOLIN_P01R1CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'GGN_SEC27_N02R0FF' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'PUN_DHNORI_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'GGN_SEC37_P01R0CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'BLR_KRMGLA_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'KOL_MNKTLA_P01R0CC' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'KOL_DUMDUM_P01R0CC' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'CHN_VLCHRY_P01R1CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'MUM_MUMCEN_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'DEL_NEBSAR_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'MUM_NERUL_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'CHN_KKNAGR_N01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_KELBKM_N01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'MUM_PANVEL_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_POWAI_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_BANDRA_P01R1CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_VIK(E)_P01R0FF' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_WAGHBL_P01R1CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_WAGHLE_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_WAGHLE_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_POWAI_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'BLR_SRJPUR_N02R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_GUNJUR_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'KOL_UNICTY_P01R0CC' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'CHN_TNAGAR_N01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'HYD_KNDPUR_N02R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'BLR_BDPLYT_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_BDGCRS_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_RGVLYT_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_BTMLYT_N02R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'GZB_GAURCT_N02R0CC' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select 'GZB_CRORPB_P01R0CC' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select 'FBD_SEC16_P01R0CC' as store_id, 'FARIDABAD' as city, 'Sagar Upadhyay' as zbm
union select 'FBD_GRNFLD_P01R0CC' as store_id, 'FARIDABAD' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_JSLVHR_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_CHTRPR_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'NOD_SEC142_N01R0CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'NOD_SKIPUR_P01R0CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_KRTNGR_N01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'BLR_BNRGTA_N02R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_SNGSDR_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'CHN_NUNGAM_P01R1CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'NOD_SEC117_N02R0CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'NOD_CHI5_P01R0CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'NOD_SEC46_N01R0CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'MUM_VASHI_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'CHN_ADYAR_N01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_MEDAVA_N01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'DEL_WZRPUR_N01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'HYD_ATAPUR_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'PUN_NANDED_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'BLR_ELCCTY_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_KLNNGR_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_VIJNGR_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_RMURTY_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_BSNPUR_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'MUM_VLEPRL_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_WADALA_P01R0FF' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'ZEP-MUM-DRY-004' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'ZEP-MUM-DRY-005' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'PUN_HNJPH1_P01R1CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'BLR_BLNDUR_P01R1CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'PUN_AMBGON_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'MUM_PAREL_P01R2CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'CHN_PAMMAL_P01R1CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'BLR_JAKKUR_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_NIKOHM_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'DEL_SNTNGR_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'CHN_GRUGBK_N02R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'BLR_RMURTY_P01R1CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'NOD_SEC46_N02R0CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'BLR_HSRLYT_P01R1CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_BLNDUR_N03R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'GGN_UDYHVR_P01R1CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'NOD_SEC10_P01R1CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'CHN_MOGPAR_N01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'KOL_RJARHT_P01R0FF' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'BLR_BTMLYT_P01R1CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_MLSWRM_P01R1CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_MRTHAL_P01R1CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'DEL_RJRGRN_P01R1CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'PUN_KHRADI_N02R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'NOD_GAURCT_N03R0FF' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'PUN_RAVET_N01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'BLR_WHTFLD_N02R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_BNSKRI_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_PEENYA_P01R1CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_ELCCTY_P01R1CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'FBD_SEC86_P01R0CC' as store_id, 'FARIDABAD' as city, 'Sagar Upadhyay' as zbm
union select 'KOL_LKTOWN_P01R0FF' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'DEL_DWARKA_P01R1CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'HYD_BNJHIL_P01R1CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_NZMPET_P01R1CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'MUM_AND(W)_P01R2CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'HYD_CHDNGR_P01R1CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'KOL_BLYGNJ_P01R0FF' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'GGN_SEC27_P01R1CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_SEC69_P01R1CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'PUN_BANER_N02R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'HYD_KOTHPT_N02R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_ALWAL_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'BLR_BSNPUR_N02R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_MCOLYT_N02R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_MRTHAL_N02R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'CHN_NANGLR_N01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'PUN_BHKRAI_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'NOD_SEC73_N02R0FF' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'PUN_SNHGAD_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'KOL_HRDVPR_P01R0FF' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'KOL_KMLGCH_P01R0FF' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'HYD_MIYPUR_N01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'KOL_BHWPOR_P01R1CC' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'CHN_TNHB_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_VANGRM_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'DEL_KRLBGM_P01R1CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'MUM_BKC_N01R1CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_KND(E)_P01R1CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'DEL_UTMNGR_P01R1CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'BLR_RGVLYT_N02R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'HYD_MNKOND_N02R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'DEL_UTMNGR_N01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_MLVNGR_P01R1CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_EOKLSH_N01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'HYD_KOMPLY_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_DULPLY_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'PUN_HNJPH3_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'MUM_VASHI_N02R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_MALAD_N02R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'DEL_NGLOEX_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'MUM_VASHI_P01R1CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'DEL_PTMPUR_N01R0FF' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'CHN_PERBKM_N01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_PAMMAL_N02R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'LKO_MAHNGR_P01R0FF' as store_id, 'LUCKNOW' as city, 'Sagar Upadhyay' as zbm
union select 'LKO_ELDECO_P01R0FF' as store_id, 'LUCKNOW' as city, 'Sagar Upadhyay' as zbm
union select 'LKO_SRDNGR_P01R0CC' as store_id, 'LUCKNOW' as city, 'Sagar Upadhyay' as zbm
union select 'SAS_SHVLIK_P01R0CC' as store_id, 'SAS Nagar' as city, 'Sagar Upadhyay' as zbm
union select 'SAS_PERMCL_P01R0CC' as store_id, 'SAS Nagar' as city, 'Sagar Upadhyay' as zbm
union select 'MUM_PLVAP2_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_BHYNDR_P01R1CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'NAS_RANNGR_P01R0CC' as store_id, 'Nashik' as city, 'Anurag Doshi' as zbm
union select 'JPR_JGTPRA_P01R0CC' as store_id, 'JAIPUR' as city, 'Sagar Upadhyay' as zbm
union select 'JAI_SRJNGR_P01R0FF' as store_id, 'JAIPUR' as city, 'Sagar Upadhyay' as zbm
union select 'BLR_SVJNGR_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'CHN_GVRTNG_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'GZB_HARSON_P01R0CC' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select 'GZB_SHMPRK_P01R0CC' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select 'CHN_MUDCHR_N01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'AHM_TRAGAD_P01R0CC' as store_id, 'Ahmedabad' as city, 'Anurag Doshi' as zbm
union select 'AHM_GOTA_P01R0CC' as store_id, 'Ahmedabad' as city, 'Anurag Doshi' as zbm
union select 'AHM_GNDNGR_P01R0FF' as store_id, 'Ahmedabad' as city, 'Anurag Doshi' as zbm
union select 'AHM_NIKOL_P01R0CC' as store_id, 'Ahmedabad' as city, 'Anurag Doshi' as zbm
union select 'FBD_NIT_P01R0CC' as store_id, 'FARIDABAD' as city, 'Sagar Upadhyay' as zbm
union select 'SAS_SUNENC_P01R0CC' as store_id, 'SAS Nagar' as city, 'Sagar Upadhyay' as zbm
union select 'JPR_ADRNGR_P01R0CC' as store_id, 'JAIPUR' as city, 'Sagar Upadhyay' as zbm
union select 'KOL_PRKSTR_N01R0CC' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'BLR_BAGLUR_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_JPNGR_N02R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_SRJPUR_N03R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'NAS_GPTNGR_P01R0CC' as store_id, 'Nashik' as city, 'Anurag Doshi' as zbm
union select 'HYD_SCNDBD_N01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_MADHAP_N02R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'LKO_GOLFCT_P01R0FF' as store_id, 'LUCKNOW' as city, 'Sagar Upadhyay' as zbm
union select 'LKO_GUDMBA_P01R0CC' as store_id, 'LUCKNOW' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_STHEXT_N01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'NOD_SEC149_P01R0CC' as store_id, 'NOIDA' as city, 'Sagar Upadhyay' as zbm
union select 'BLR_MAGADI_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_RRNGR_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_BTMLYT_N03R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_CVRNGR_N02R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_KNKNGR_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_NRYNPR_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'AHM_NVRGPR_P01R0FF' as store_id, 'Ahmedabad' as city, 'Anurag Doshi' as zbm
union select 'AHM_VRJVHR_P01R0FF' as store_id, 'Ahmedabad' as city, 'Anurag Doshi' as zbm
union select 'PUN_WARJE_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'PUN_RAVET_N02R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'PUN_TNGNGR_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'MUM_KLYANE_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_KRL(W)_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'DEL_MDLTWN_N01R0FF' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_JNKPRI_N01R0FF' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_KLKAJI_N01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'HYD_ECIL_N01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'DEL_NJFGRH_P01R0FF' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'CHN_MADABK_N02R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'NAS_CIDCO_P01R0CC' as store_id, 'Nashik' as city, 'Anurag Doshi' as zbm
union select 'AHM_NEWRNP_P01R0FF' as store_id, 'Ahmedabad' as city, 'Anurag Doshi' as zbm
union select 'AHM_SBOPAL_P01R0FF' as store_id, 'Ahmedabad' as city, 'Anurag Doshi' as zbm
union select 'AHM_SHNTGM_P01R0FF' as store_id, 'Ahmedabad' as city, 'Anurag Doshi' as zbm
union select 'JPR_BNIPAK_P01R0FF' as store_id, 'JAIPUR' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_SEC112_P01R0CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'HYD_MHDPTM_N01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_BOLARM_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_MOSAPT_N03R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'GGN_GWLPRI_P01R0CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_DLSGRD_P01R1CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_DWARKA_N04R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'LKO_ALIGNJ_P01R0CC' as store_id, 'LUCKNOW' as city, 'Sagar Upadhyay' as zbm
union select 'LKO_VKSKND_P01R0CC' as store_id, 'LUCKNOW' as city, 'Sagar Upadhyay' as zbm
union select 'HYD_MADHAP_N03R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'BLR_YLHNKA_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_KLNNGR_N02R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'HYD_KUKTPL_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_BWNPLY_N01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'PUN_UNDRI_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'PUN_MOSHI_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'PUN_HNJPH2_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'PUN_GAHNJE_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'CHN_KKNAGR_N02R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_GRUGBK_N03R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'MUM_PANVEL_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'GGN_SEC4_P01R0FF' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_SEC39_N04R0FF' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'MUM_AND(E)_N02R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_KND(E)_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'CHD_SEC26_P01R0CC' as store_id, 'Chandigarh' as city, 'Sagar Upadhyay' as zbm
union select 'JAI_NRMNGR_P01R0FF' as store_id, 'JAIPUR' as city, 'Sagar Upadhyay' as zbm
union select 'FBD_SEC37_P01R0FF' as store_id, 'FARIDABAD' as city, 'Sagar Upadhyay' as zbm
union select 'FBD_CHRMWD_P01R0FF' as store_id, 'FARIDABAD' as city, 'Sagar Upadhyay' as zbm
union select 'GZB_INDPRM_N02R0FF' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select 'PNK_BDNPR_P01R0CC' as store_id, 'PANCHKULA' as city, 'Sagar Upadhyay' as zbm
union select 'GZB_INDPRM_N03R0FF' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select 'GZB_MDBNBP_P01R0CC' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select 'GZB_RAJEXT_N02R0CC' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_RHON23_P01R0FF' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_DWARKA_N03R0FF' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'BLR_SNRLTY_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_MLSWRM_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_HSRLYT_N04R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_YSHPUR_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_VDYPRA_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_JAKKUR_N02R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'MUM_MAROL_N02R0FF' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_NERUL_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'LKO_HZRTGJ_P01R0CC' as store_id, 'LUCKNOW' as city, 'Sagar Upadhyay' as zbm
union select 'LKO_JNKPRM_P01R0CC' as store_id, 'LUCKNOW' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_ANDVHR_N01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_SEC12_N01R0CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'HYD_VKDNGR_N01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_SNKPRI_N01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_BEGMPT_N01R0FF' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_MOSAPT_N02R0FF' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_HMYTNG_N01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_UPPAL_N01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_KNDPUR_N04R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'BLR_VIJNGR_N02R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_MRTHAL_N03R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_SATVAE_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_PEENYA_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'AHM_MOTERA_P01R0FF' as store_id, 'Ahmedabad' as city, 'Anurag Doshi' as zbm
union select 'CHN_MLPORE_N02R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'KOC_VLTHOL_P01R0CC' as store_id, 'KOCHI' as city, 'Akash Tiwary' as zbm
union select 'KOC_PLRTHY_P01R0CC' as store_id, 'KOCHI' as city, 'Akash Tiwary' as zbm
union select 'MUM_PAREL_N02R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_POWAI_N02R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'GGN_SEC39_P01R1FF' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'MUM_KALWA_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_BDLPRE_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_DMB(W)_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_KOTARI_N01R1CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_MUMCEN_N02R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_ULSNGR_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_ULWE_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'DEL_VKSPUR_N01R0FF' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_SNTVLG_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'JAI_CDACTY_P01R0FF' as store_id, 'JAIPUR' as city, 'Sagar Upadhyay' as zbm
union select 'JAI_PTRKGT_P01R0FF' as store_id, 'JAIPUR' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_RJRGRN_N01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'COI_PELMDU_P01R0CC' as store_id, 'COIMBATORE' as city, 'Akash Tiwary' as zbm
union select 'COI_RCECRS_P01R0CC' as store_id, 'COIMBATORE' as city, 'Akash Tiwary' as zbm
union select 'KOL_BEHALA_P01R1CC' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'BLR-DRY-MH-NELAMANGALA' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR-Cold-MH-NELAMANGALA' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'GZB_INDPRM_N04R0CC' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select '   HYD_NAMPLY_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_DULPLY_SS1R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_MADHAP_SS1R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_BEGMPT_SS1R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_MOSAPT_SS1R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_BWNPLY_SS1R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'BLR_SNHALI_N01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_SVJNGR_SS1R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_JPNGR_SS1R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_CVRNGR_SS1R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'HYD_CHTLMT_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'AHM_THLTEJ_P01R0FF' as store_id, 'Ahmedabad' as city, 'Anurag Doshi' as zbm
union select 'KOC_KAKNAD_P01R0FF' as store_id, 'KOCHI' as city, 'Akash Tiwary' as zbm
union select 'HYD_BCHPLY_N01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'KOL_JOKA_P01R01FF' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'BLR_JLHALI_N01P0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'MUM_MLD(E)_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_COLABA_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'HYD_BCHPLY_N02R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'KOC_INFPRK_P01R0CC' as store_id, 'KOCHI' as city, 'Akash Tiwary' as zbm
union select 'HYD_NZMPET_N02R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'HYD_MNKOND_N03R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'LKO_INDNGR_P01R0FF' as store_id, 'LUCKNOW' as city, 'Sagar Upadhyay' as zbm
union select 'PUN_DHNORI_N01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'PUN_SPLCTY_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'GGN_SEC39_N03R0FF' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'BLR_HENNUR_N02R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_WHTFLD_N04R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'CHN_STLPKM_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'CHN_ANANGR_N01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'PUN_PASHAN_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'KOL_RICJNI_P01R0CC' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'KOL_TANGRA_N01R0FF' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'PUN_KHRADI_N03R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'CHN_VNDLUR_N01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'BLR_SNGSDR_N02R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_KENGRI_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_BRKFLD_N02R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_KGLURD_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'GGN_SEC10A_P01R0CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_SEC79_P01R0CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_ARDCTY_N04R0CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_SEC66_N01R0FF' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_ARDCTY_N03R0FF' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_PLMVHR_N01R0FF' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'BLR_NHRNGR_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'RAJ_MAVDI_P01R0CC' as store_id, 'Rajkot' as city, 'Anurag Doshi' as zbm
union select 'HYD_SNGTWS_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'COI_SNGNLR_P01R0CC' as store_id, 'COIMBATORE' as city, 'Akash Tiwary' as zbm
union select 'COI_SAIBAB_P01R0CC' as store_id, 'COIMBATORE' as city, 'Akash Tiwary' as zbm
union select 'LKO_MNSENC_P01R0CC' as store_id, 'LUCKNOW' as city, 'Sagar Upadhyay' as zbm
union select 'HYD_TRNAKA_N01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'KNU_AWSVKS_P01R0CC' as store_id, 'KANPUR' as city, 'Sagar Upadhyay' as zbm
union select 'LKO_IIM_P01R0CC' as store_id, 'LUCKNOW' as city, 'Sagar Upadhyay' as zbm
union select 'HYD_KOTHPT_N03R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'JAI_TNKPTK_P01R0FF' as store_id, 'JAIPUR' as city, 'Sagar Upadhyay' as zbm
union select 'JAI_KRSNGR_P01R0CC' as store_id, 'JAIPUR' as city, 'Sagar Upadhyay' as zbm
union select 'CHN-DRY MH' as store_id, 'CHENNAI' as city, 'Karthik Ragunath' as zbm
union select 'AHM_VASTRL_P01R0CC' as store_id, 'Ahmedabad' as city, 'Anurag Doshi' as zbm
union select 'CHN-SS-MH-THIRUVALLUR' as store_id, 'CHENNAI' as city, 'Karthik Ragunath' as zbm
union select 'BLR_CHNDPR_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_DVNHLI_P01R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'BLR_RGVLYT_N03R0CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'HYD_TELPUR_P01R0CC' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'BLR_CHKPET_P01R1CC' as store_id, 'BENGALURU' as city, 'Akash Tiwary' as zbm
union select 'PUN_BANER_N03R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'PUN_PMLSDG_N02R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'CHN_AMBTUR_N01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'DEL_KRTNGR_N02R0FF' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_RHON15_N01R0FF' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'SON_KUNDLI_P01R0CC' as store_id, 'SONIPAT' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_MHVNCV_N01R0FF' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_SHADRA_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_RHON21_P01R0FF' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_DWARKA_N05R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_KRTNGR_N03R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'SAS_GLCOPR_P01R0CC' as store_id, 'SAS Nagar' as city, 'Sagar Upadhyay' as zbm
union select 'SON_TDICTY_P01R0CC' as store_id, 'SONIPAT' as city, 'Sagar Upadhyay' as zbm
union select 'AHM_MAKRBA_P01R0CC' as store_id, 'Ahmedabad' as city, 'Anurag Doshi' as zbm
union select 'SUR_BHRTNA_P01R0CC' as store_id, 'Surat' as city, 'Anurag Doshi' as zbm
union select 'KOL_DMDCTY_P01R0FF' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'KOL_SNTPUR_P01R0CC' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'BLR-MYLAPURA MH' as store_id, 'BENGALURU' as city, 'Ajay DS' as zbm
union select 'FBD_NIT2_P01R0CC' as store_id, 'FARIDABAD' as city, 'Sagar Upadhyay' as zbm
union select 'FBD_SEC79_P01R0CC' as store_id, 'FARIDABAD' as city, 'Sagar Upadhyay' as zbm
union select 'FBD_SNIMOH_P01R0CC' as store_id, 'FARIDABAD' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_DRHERA_P01R0CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'GZB_RAJNGR_N01R0CC' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select 'MUM_BANDRA_N03R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_BHNDUP_N02R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_FORT_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_KHRGHR_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_KND(W)_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_MUMCEN_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'MUM_VLEPRL_N01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'GZB_PTPVHR_P01R0CC' as store_id, 'GHAZIABAD' as city, 'Sagar Upadhyay' as zbm
union select '' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'MUM_AMBNTH_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'HYD_MSHBAD_N01R0FF' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select '' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'CHN_KKNAGR_N03R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'COI_RJRGRN_N01R0CC' as store_id, 'COIMBATORE' as city, 'Akash Tiwary' as zbm
union select 'PUN_PMLGAU_P01R0CC' as store_id, 'PUNE' as city, 'Anurag Doshi' as zbm
union select 'NAS_JGTPML_P01R0CC' as store_id, 'Nashik' as city, 'Anurag Doshi' as zbm
union select 'SAS_FRDENC_P01R0CC' as store_id, 'SAS NAGAR' as city, 'Sagar Upadhyay' as zbm
union select 'CHN_CHRMPT_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'KOC_FRDSHP_P01R0CC' as store_id, 'KOCHI' as city, 'Akash Tiwary' as zbm
union select 'NAS_INDNGR_P01R0CC' as store_id, 'Nashik' as city, 'Anurag Doshi' as zbm
union select 'SUR_JHGPRA_P01R0CC' as store_id, 'Surat' as city, 'Anurag Doshi' as zbm
union select 'SUR_MJRAGT_P01R0CC' as store_id, 'Surat' as city, 'Anurag Doshi' as zbm
union select 'LKO_KRSNGR_P01R0FF' as store_id, 'Lucknow' as city, 'Sagar Upadhyay' as zbm
union select 'KOL_ACRPLS_P01R0CC' as store_id, 'Kolkata' as city, 'Avijit Roy' as zbm
union select 'GGN_SEC77_P01R0CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_SEC12_N02R0CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'GGN_SEC95_P01R0CC' as store_id, 'GURUGRAM' as city, 'Sagar Upadhyay' as zbm
union select 'MUM_PLVCTY_P01R0CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'TRZ_KKNGR_P01R0CC' as store_id, 'TIRUCHIRAPPALLI' as city, '' as zbm
union select 'HYD_GACBOW_N01R0FF' as store_id, 'HYDERABAD' as city, 'Srinivas Reddy' as zbm
union select 'BWD_TTRPUR_P01R0CC' as store_id, 'BHIWADI' as city, 'Sagar Upadhyay' as zbm
union select 'MUM_KHRGHR_P01R1CC' as store_id, 'MUMBAI' as city, 'Anurag Doshi' as zbm
union select 'KOL_BLYGNJ_SS1R0CC' as store_id, 'Kolkata' as city, '' as zbm
union select 'CHN_MDRWC_P01R0CC' as store_id, 'CHENNAI' as city, 'Srinivas Reddy' as zbm
union select 'DEL_DLSGRD_N01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm
union select 'DEL_RJPKHD_P01R0CC' as store_id, 'DELHI' as city, 'Sagar Upadhyay' as zbm)

SELECT lm.zbm as "ZBM", initcap(lm.city) AS "City ID",
       upper(cms.store_id) AS "DH",
       audit_type AS "Audit Type",
       CASE
           WHEN audit_main_theme ILIKE '%Process Audit%' THEN 'Process Audit'
           WHEN audit_main_theme ILIKE '%Beat Ops%' THEN 'Beat Ops'
           WHEN audit_main_theme ILIKE '%FSSAI%' THEN 'Compliance'
           WHEN audit_main_theme ILIKE '%GHP%' THEN 'GHP'
           WHEN audit_main_theme ILIKE '%Material Handling%' THEN 'Material Handling'
           ELSE audit_main_theme
       END AS "Audit",
	   	   audit_month as "Month",
       audit_date::TIMESTAMP AS "Date",
       auditor_name AS "Auditor",
       audit_submission_number AS "Report No",
       theme AS "Theme",
       CHECKPOINT AS "Checkpoint",
                     RESULT AS "Result",
                               CASE
                                   WHEN RESULT = 'NC'
                                        AND (total_follow_up_tasks = 0
                                             OR total_follow_up_tasks IS NULL) THEN 'Unassigned'
                                   WHEN RESULT = 'NC'
                                        AND total_follow_up_tasks > 0
                                        AND (total_closed_follow_up_tasks < total_follow_up_tasks
                                             OR total_closed_follow_up_tasks IS NULL) THEN 'Open'
                                   WHEN RESULT = 'NC'
                                        AND total_follow_up_tasks > 0
                                        AND total_closed_follow_up_tasks >= total_follow_up_tasks THEN 'Closed'
                                   ELSE NULL
                               END AS "NC Status",
							   case when result = 'NC' AND total_follow_up_tasks > 0
                                        AND (total_closed_follow_up_tasks < total_follow_up_tasks
                                             OR total_closed_follow_up_tasks IS NULL) and (extract(epoch from current_timestamp) - extract(epoch from audit_date::timestamp at time zone 'Asia/Kolkata'))/86400 <= 2 then '0 - 2 Days'
                               when result = 'NC' AND total_follow_up_tasks > 0
                                        AND (total_closed_follow_up_tasks < total_follow_up_tasks
                                             OR total_closed_follow_up_tasks IS NULL) and (extract(epoch from current_timestamp) - extract(epoch from audit_date::timestamp at time zone 'Asia/Kolkata'))/86400 between 2 and 7 then '3 - 7 Days'
							   when result = 'NC' AND total_follow_up_tasks > 0
                                        AND (total_closed_follow_up_tasks < total_follow_up_tasks
                                             OR total_closed_follow_up_tasks IS NULL) and (extract(epoch from current_timestamp) - extract(epoch from audit_date::timestamp at time zone 'Asia/Kolkata'))/86400 between 7 and 15 then '8 - 15 Days'
							   when result = 'NC' AND total_follow_up_tasks > 0
                                        AND (total_closed_follow_up_tasks < total_follow_up_tasks
                                             OR total_closed_follow_up_tasks IS NULL) and (extract(epoch from current_timestamp) - extract(epoch from audit_date::timestamp at time zone 'Asia/Kolkata'))/86400 >= 15 then '> 15 Days'
							   else NULL end as "Aging",
                               CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE result_score::numeric
                               END AS "Actual Score",
                               CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE max_score::numeric
                               END AS "Max Score",
                               audit_submission_knid AS "Report KNID",
                               checkpoint_knid AS "Checkpoint KNID"
FROM zepto_qms_checkpoint_master_sheet_table cms
left outer join lm on upper(cms.store_id) = upper(lm.store_id)
WHERE audit_type ILIKE '%DH Audits%'
  AND (audit_main_theme ILIKE '%Process Audit%'
       OR audit_main_theme ILIKE '%Beat Ops%'
       OR audit_main_theme ILIKE '%FSSAI%'
       OR audit_main_theme ILIKE '%GHP%'
       OR audit_main_theme ILIKE '%Material Handling%')
  AND audit_date::TIMESTAMP BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP
ORDER BY 1,
         2,
         3,
         4,
         5,
		 7,
         10,
         11
```

---

## zeptoLearn1-copy_1755514262_Zepto Cafe Learn.sql

**Tables referenced:** user_details, zepto_learn

**Original Query:**

```sql
-- Data Source: zeptoLearn1-copy_1755514262
-- Dashboard: Zepto Cafe Learn
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:54:39
-- ============================================================

SELECT 
  zl.*, 
  ud.first_name || ' ' || ud.last_name AS emp_name,
  ud.phone_number,
CASE 
    WHEN course_status <> 'Completed' 
    THEN EXTRACT(EPOCH FROM (NOW() - shared_at)) / 86400
    ELSE NULL
END AS days_difference
FROM zepto_learn zl
LEFT JOIN user_details ud 
  ON zl.user_knid = ud.uuid
WHERE zl.organization = @{{:OrganizationParameter}}
  AND zl.shared_at BETWEEN @{{:Date Range.START}}::timestamp 
                      AND @{{:Date Range.END}}::timestamp + interval '1 day'
  AND zl.course_name ILIKE '%Cafe%'
  AND ud.is_active = 'true'
  AND ud.job_location NOT IN ('KNOW', 'All')
  AND ud.job_location NOT ILIKE 'Head Office%'
group by 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
```

---

## zeptoLearn1_Zepto Learn.sql

**Tables referenced:** ROLES, lm, locations, lr, role_holders, user_details, zepto_learn

**Original Query:**

```sql
-- Data Source: zeptoLearn1
-- Dashboard: Zepto Learn
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:54:16
-- ============================================================

  with lr AS
  (SELECT l.id,
          l.location_name AS store_name,
          r.name AS ROLE,
          ud.uuid AS holder_id,
          ud.first_name || ' ' || ud.last_name AS holder
   FROM locations l
   LEFT JOIN role_holders rh ON l.id = rh.location_id
   AND rh.is_active = 'true'
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('DH/MH Trainer')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = 'true'
   WHERE l.organization = 'Zds-indus'
     AND l.is_active = 'true' ),
     lm AS
  (SELECT lr.id AS store_id,
          lr.store_name,
          MAX(CASE
                  WHEN ROLE = 'DH/MH Trainer' THEN holder
              END) AS "Trainer"
   FROM lr
   GROUP BY 1,
            2)
        SELECT 
  zl.*, 
  ud.first_name || ' ' || ud.last_name AS emp_name,
  ud.phone_number,
CASE 
    WHEN course_status <> 'Completed' 
    THEN EXTRACT(EPOCH FROM (NOW() - shared_at)) / 86400
    ELSE NULL
END AS days_difference,
lm."Trainer"
FROM zepto_learn zl
LEFT JOIN user_details ud 
  ON zl.user_knid = ud.uuid
  left JOIN lm on zl.location = lm.store_id
WHERE zl.organization = @{{:OrganizationParameter}}
  AND zl.shared_at BETWEEN @{{:Date Range.START}}::timestamp 
                      AND @{{:Date Range.END}}::timestamp + interval '1 day'
  AND zl.course_name NOT ILIKE '%Cafe%'
  AND ud.is_active = 'true'
group by 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,22
```

---

## zepto_ss_gemba_audit_Zepto SS Gemba.sql

**Tables referenced:** audit_date, base, lm, location_acl, locations, lr, role_holders, roles, user_details, user_groups, zepto_qms_checkpoint_master_sheet_table

**Original Query:**

```sql
-- Data Source: zepto_ss_gemba_audit
-- Dashboard: Zepto SS Gemba
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:55:52
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'Zds-indus'
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
               AND ug1.is_active = TRUE))),
			     lr AS (
  SELECT l.id,
        location_name AS store_name,
         r.name AS ROLE,
         ud.uuid AS holder_id,
         ud.first_name || ' ' || ud.last_name AS holder
  FROM location_acl acl
   LEFT OUTER JOIN locations l ON acl.job_location = L.location_name
  LEFT JOIN role_holders rh ON l.id = rh.location_id AND rh.is_active = 'true'
  LEFT JOIN roles r ON r.id = rh.role_id AND r.name IN ('CLM')
  LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid AND ud.is_active = 'true'
  WHERE l.organization = 'Zds-indus' AND l.is_active = 'true'
),
lm AS (
  SELECT lr.id AS store_id,
         MAX(CASE WHEN ROLE = 'CLM' THEN holder END) AS "CLM"
  FROM lr
  GROUP BY 1
),
     base AS
  (SELECT organization_id,
   "CLM",
          CASE
              WHEN result_score = '' THEN NULL
              ELSE result_score::numeric
          END AS result_score,
          CASE
              WHEN max_score = '' THEN NULL
              ELSE max_score::numeric
          END AS max_score,
          cms.store_id,
   audit_type,
          audit_main_theme,
          theme,
          audit_date,
          audit_submission_number,
          audit_submission_knid,
          auditor_name,
          checkpoint_knid,
          CHECKPOINT,
          RESULT,
          criticality,
          --is_critical_question_failed,
          auditor_observations,
          total_follow_up_tasks,
          total_closed_follow_up_tasks,
          CASE
              WHEN result_score = '' THEN 'Not checked'
              WHEN result_score::numeric < max_score::numeric THEN 'Failed'
              ELSE 'Passed'
          END AS status,
                              row_number() OVER (PARTITION BY cms.store_id,
                                       audit_main_theme,
                                       theme, checkpoint_knid,
                                       extract('Year'
                  FROM audit_date)
                          ORDER BY audit_date) AS "Audit No in Year"
   FROM zepto_qms_checkpoint_master_sheet_table cms
   join location_acl on cms.store_id = location_acl.job_location
  LEFT OUTER JOIN lm on cms.store_id = lm.store_id
   WHERE organization_id = 'Zds-indus'
  and audit_main_theme in ('SS | Gemba Walk')
  and audit_date between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval ' 1 day')
SELECT organization_id AS "Org",
       base.store_id AS "Location",
	   "CLM",
	   audit_type as "Type",
       audit_main_theme AS "Audit",
       audit_date AS "Audit Date",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
       auditor_name AS "Auditor",
	   theme as "Theme",
       checkpoint_knid as "Checkpoint KNID",
	   checkpoint as "Checkpoint",
	   result as "Result",
	   status as "Checkpoint Status",
	   auditor_observations as "Auditor Notes",
	   result_score as "Actual Score",
	   max_score as "Max Score",
	   criticality as "Criticality",
       total_follow_up_tasks AS "Total Follow Ups",
       total_closed_follow_up_tasks AS "Total Closed Follow Ups",
       "Audit No in Year"
FROM base
group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,20,21
ORDER BY 1,
         2,
         4
```

---

## zepto_ss_gemba_audit_summary_Zepto SS Gemba.sql

**Tables referenced:** audit_date, base, location_acl, user_details, user_groups, zepto_qms_checkpoint_master_sheet_table

**Original Query:**

```sql
-- Data Source: zepto_ss_gemba_audit_summary
-- Dashboard: Zepto SS Gemba
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:56:31
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'Zds-indus'
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
               AND ug1.is_active = TRUE))),
     base AS
  (SELECT organization_id,
          CASE
              WHEN result_score = '' THEN NULL
              ELSE result_score::numeric
          END AS result_score,
          CASE
              WHEN max_score = '' THEN NULL
              ELSE max_score::numeric
          END AS max_score,
          store_id,
   audit_type,
          audit_main_theme,
          theme,
          audit_date,
          audit_submission_number,
          audit_submission_knid,
          auditor_name,
          checkpoint_knid,
          CHECKPOINT,
          RESULT,
          criticality,
          --is_critical_question_failed,
          auditor_observations,
          total_follow_up_tasks,
          total_closed_follow_up_tasks,
          CASE
              WHEN result_score = '' THEN 'Not checked'
              WHEN result_score::numeric < max_score::numeric THEN 'Failed'
              ELSE 'Passed'
          END AS status,
                              row_number() OVER (PARTITION BY store_id,
                                       audit_main_theme,
                                       theme, checkpoint_knid,
                                       extract('Year'
                  FROM audit_date)
                          ORDER BY audit_date) AS "Audit No in Year"
   FROM zepto_qms_checkpoint_master_sheet_table cms
   join location_acl on cms.store_id = location_acl.job_location
   WHERE organization_id = 'Zds-indus'
   and audit_main_theme in ( 'SS | Gemba Walk')
  and audit_date between @{{:zepto_ss_gemba_audit.Date Range.START}}::timestamp and @{{:zepto_ss_gemba_audit.Date Range.END}}::timestamp + interval ' 1 day'
  )
SELECT organization_id AS "Org",
       store_id AS "Location",
	   audit_type as "Type",
       audit_main_theme AS "Audit",
       audit_date AS "Audit Date",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
       auditor_name AS "Auditor",
       sum(result_score) as "Actual Score",
	   sum(max_score) as "Max Score",
	   sum(result_score)/sum(max_score) AS "Audit Score",
       count(CASE
                 WHEN criticality = 'Critical' and result_score < max_score and result_score is not null THEN checkpoint_knid
                 ELSE NULL
             END) AS "Critical Failed Count",
       sum(total_follow_up_tasks) AS "Total Follow Ups",
       sum(total_closed_follow_up_tasks) AS "Total Closed Follow Ups",
       "Audit No in Year"
FROM location_acl acl
LEFT OUTER JOIN base ON acl.job_location = base.store_id
group by 1, 2, 3, 4, 5, 6, 7, 8, 15
ORDER BY 1,
         2,
         3, 5
```

---

## zepto_ss_gemba_audit_tasks_Zepto SS Gemba.sql

**Tables referenced:** analytics_requests, assignees, locations, role_holders, t, tasks, user_details, user_groups, zepto_qms_checkpoint_master_sheet_table

**Columns needing snake_case conversion:**

- `auditDetails` -> `audit_details` (alias: `audit_details AS "auditDetails"`)

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `formDetails` -> `form_details` (alias: `form_details AS "formDetails"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `plannedStartDate` -> `planned_start_date` (alias: `planned_start_date AS "plannedStartDate"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `resolvedPayload` -> `resolved_payload` (alias: `resolved_payload AS "resolvedPayload"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)


**Original Query:**

```sql
-- Data Source: zepto_ss_gemba_audit_tasks
-- Dashboard: Zepto SS Gemba
-- Category: Zepto DH
-- Extracted: 2026-01-29 16:56:28
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
      UNION SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = TRUE
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store_id
      FROM user_details
      WHERE organization = 'Zds-indus'
        AND is_active = 'true'
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
                  AND ug1.is_active = TRUE))) l),
				  t AS
  (SELECT t.id AS "Task KNID",
          t.ext_id AS "Task ID",
          t.title AS "Task",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Completed'
              WHEN t.status ILIKE 'notStarted' THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened') THEN 'In Progress'
          END AS "Status",
          coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') AS "Audit",
                                      coalesce(t.details->'auditDetails'->>'formId', t.details->'formDetails'->>'formId') AS "Audit KNID",
                                                                  coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') AS "Audit Report KNID",
                                                                                              coalesce(t.details->'auditDetails'->>'sno', t.details->'formDetails'->>'sno') AS "Audit Report No",
                                                                                                                          initcap(t.details->>'authorName') AS "Assigned By",
                                                                                                                          author,
                                                                                                                          to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AT TIME ZONE 'Asia/Dubai' AS "Planned Start",
                                                                                                                                                                                                   initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                                                                                                                                   initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                                                                                                                                   initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                                                                                                                                   to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Dubai' AS "Assigned At",
                                                                                                                                                                                                                                                to_timestamp(t.deadline/1000) AT TIME ZONE 'Asia/Dubai' AS "Deadline",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) AT TIME ZONE 'Asia/Dubai'
                                                                                                                                                                                                                                                                                           END AS "Started At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) AT TIME ZONE 'Asia/Dubai'
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Completed At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) AT TIME ZONE 'Asia/Dubai'
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Reopened At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Overdue Task Count",
   																																																																							CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP AND cms.criticality = 'Critical' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Critical Overdue Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'notStarted' 
   																																																																											or t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                     OR t.status ILIKE 'reopened' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Open Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN (t.status ILIKE 'notStarted' 
   																																																																											or t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                     OR t.status ILIKE 'reopened') 
																																																																									 and cms.criticality = 'Critical' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Critical Open Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Completed Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND completed_at <= deadline THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "On Time Completed Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Reopened Task Count",
                                                                                                                                                                                                                                                                                           t.details->>'comment' AS "Completion Comment",
                                                                                                                                                                                                                                                                                                       t.details->'resolvedPayload'->'images'->0->>'url' AS "Completion Image",
                                                                                                                                                                                                                                                                                                                                                   coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) AS checkpoint_knid,
                                                                                                                                                                                                                                                                                                                                                                               cms.auditor_observations AS "Auditor Comment",
   cms.store_id as "Store",
   cms.theme as "Theme",
   cms.auditor_name as "Auditor",
   cms.audit_type as "Audit Type",
   cms.audit_date as "Audited At",
   cms.checkpoint as "Checkpoint",
   cms.criticality as "Criticality",
   tu.division,
   tu.sub_division
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   JOIN zepto_qms_checkpoint_master_sheet_table cms ON coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) = cms.checkpoint_knid
   AND coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') = cms.audit_submission_knid
   LEFT OUTER JOIN user_details tu on cms.store_id = tu.job_location
   WHERE t.is_deleted = 'false'
     and cms.audit_main_theme = 'SS | Gemba Walk'
     AND cms.audit_date BETWEEN @{{:zepto_ss_gemba_audit.Date Range.START}}::timestamp AND @{{:zepto_ss_gemba_audit.Date Range.END}}::timestamp + interval '1 day'
     AND t.organization = 'Zds-indus'
  GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 ,17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37,38,39),
                            assignees AS
  (SELECT DISTINCT ON (t."Task KNID") t."Task KNID",
                      ud.first_name||' '||ud.last_name AS assignee,
                      ud.department
   FROM t
   JOIN analytics_requests ar ON t."Task KNID" = ar.nugget_id
   JOIN user_details ud ON ar.user_id = ud.uuid
   WHERE ar.event_id = 1
     AND ud.uuid != t.author
   ORDER BY 1,
            ar.updated_at)
SELECT t.*,
	   assignees.assignee AS "Assigneee",
       assignees.department AS "Assignee Department"
FROM t
LEFT OUTER JOIN assignees ON t."Task KNID" = assignees."Task KNID"
```

---
