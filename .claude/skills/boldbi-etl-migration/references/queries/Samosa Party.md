# Samosa Party

> Auto-generated on 2026-03-04 08:13

**Total queries:** 9

---

## AM Visits Report Deviation_AM Visits and Shift Management Report.sql

**Tables referenced:** all_questions, allowed_locations, deviation_summary, form_ids, form_responses, form_submissions, last, nuggets, organizations, qd_logic, qd_logic_base, qd_logic_expanded, qd_main, question_definitions, question_options, recent_submissions, responses_parsed, responses_with_scores, td

**Original Query:**

```sql
-- Data Source: AM Visits Report Deviation
-- Dashboard: AM Visits and Shift Management Report
-- Category: Samosa Party
-- Extracted: 2026-01-29 16:52:30
-- ============================================================

WITH td AS (
    SELECT 
        COALESCE(o.tzoffset, 0) as tzoffset,
        interval '1 min' * COALESCE(o.tzoffset, 0) AS diff
    FROM organizations o
    WHERE o.id IN (
        SELECT organization FROM nuggets 
        WHERE title ILIKE 'AM Store Visit Checklist%' 
        AND title NOT ILIKE '%shift%' 
        LIMIT 1
    )
),
form_ids AS (
    SELECT id AS nugget_id
    FROM nuggets
    WHERE title ILIKE 'AM Store Visit Checklist%'
    AND title NOT ILIKE '%shift%'
),
allowed_locations AS (
    SELECT unnest(ARRAY[
        'Airport Road',
        'Alpha 2 Greater Noida',
        'Ameerpet',
        'Ananth Nagar',
        'Aparna Mall',
        'AS Rao Nagar',
        'Bagmane',
        'Bagmane (CV Raman Nagar)',
        'Banashankari',
        'Bannerghatta',
        'Begur',
        'Bellandur',
        'BLR - CK - Manyta Tech Park',
        'BLR - CK - Panathur',
        'BLR - DN - Airport T-1',
        'BLR - DN - Ayyappa Nagar',
        'BLR - DN - Bagalur',
        'BLR - DN - Budigere',
        'BLR - DN - Channapatna',
        'BLR - DN - Ecoworld',
        'BLR - DN - Galleria Mall',
        'BLR - DN - Haralur',
        'BLR - DN - Kaggadasapura',
        'BLR - DN - Kengeri',
        'BLR - DN - Park Square Mall (ITPL)',
        'CBD',
        'Chandapura',
        'Channasandra',
        'Crossing Republic',
        'Dasarahalli',
        'Defence Colony',
        'Dilshad Garden',
        'Dilshukh Nagar',
        'Dommasandra',
        'Dwarka',
        'East Patel Nagar',
        'Eco Space',
        'EGL',
        'Electronic City',
        'Faridabad SEC16',
        'Gaur City- Noida Extension',
        'Hennur',
        'HSR Layout',
        'HSR Layout Sector 3',
        'Hyd - CK - Padmarao Nagar',
        'HYD - DN - Sun City',
        'Indiranagar 12B',
        'Indirapuram',
        'Jeevan Bhima Nagar',
        'JP Nagar',
        'Kalyan Nagar',
        'Kanakapura Dine-In',
        'Kanakpura Road',
        'Kondapur',
        'Koramangala',
        'Kukatpally',
        'Laxmi Nagar',
        'Madhapur',
        'Mahadevpura',
        'Malviya Nagar',
        'Manikonda',
        'Marathalli',
        'Mehdipatnam',
        'Murgeshpalya',
        'Nagarbhavi',
        'NCR - DN - Advant Tech Park',
        'NCR - DN - Sector 120 Central Market',
        'NCR - DN - Star Tower',
        'NCR - DN- Janakpuri',
        'NCR - DN- Shalimar Bag',
        'New BEL Rd',
        'Nexus Koramangala',
        'Nexus Shantiniketan',
        'Old Madras Road',
        'Pragathi Nagar',
        'Raj Nagar',
        'Rajaji Nagar',
        'Rohini',
        'Royasandra',
        'RR Nagar',
        'RT Nagar',
        'Sahakar Nagar',
        'Sarita Vihar',
        'Sarjapur',
        'Sector 4 Gurgaon',
        'Sector 56',
        'Sector 90',
        'Sector- 4 Noida',
        'Singasandra',
        'Sohna Road',
        'Sushant Lok',
        'TC Palya',
        'TechnoStar (AECS)',
        'Udyog Vihar, Phase V',
        'Uttam Nagar',
        'Varthur',
        'Vasant Kunj',
        'Whitefield',
        'NCR - CK - Palam Vihar',
        'NCR - CK - Sector 65',
        'TN - CK - Karapakkam',
        'BLR - DN - Neo Town',
        'NCR - DN - Pacific Mall(Dwarka 21)'
    ]) AS location_name
),
-- Get main questions with options
qd_main AS (
    SELECT 
        question_id AS qid,
        question,
        question_type,
        definition
    FROM question_definitions
    WHERE nugget_id IN (SELECT nugget_id FROM form_ids)
    AND question_type IN ('audit', 'multiple_choice', 'dropdown')
    AND definition->'options' IS NOT NULL
),
-- Get logic questions
qd_logic_base AS (
    SELECT 
        nugget_id,
        definition
    FROM question_definitions
    WHERE nugget_id IN (SELECT nugget_id FROM form_ids)
    AND definition -> 'logic' IS NOT NULL
),
qd_logic_expanded AS (
    SELECT 
        logic_element
    FROM qd_logic_base,
    LATERAL jsonb_array_elements(definition -> 'logic') AS logic_element
),
qd_logic AS (
    SELECT 
        qe.key AS qid,
        qe.value->>'question' AS question,
        qe.value->>'question_type' AS question_type,
        qe.value AS definition
    FROM qd_logic_expanded qle,
    LATERAL jsonb_each(qle.logic_element -> 'questions') AS qe
    WHERE qe.value->>'question_type' IN ('audit', 'multiple_choice', 'dropdown')
    AND qe.value->'options' IS NOT NULL
),
-- Combine all questions
all_questions AS (
    SELECT * FROM qd_main
    UNION
    SELECT * FROM qd_logic
),
-- Extract options with SCORE values
question_options AS (
    SELECT 
        aq.qid,
        aq.question,
        opt.value->>'value' AS option_value,
        COALESCE((opt.value->>'score')::numeric, 0) AS score
    FROM all_questions aq,
    LATERAL jsonb_array_elements(aq.definition->'options') AS opt
),
-- Get submissions from last 60 days
recent_submissions AS (
    SELECT DISTINCT ON (fs.response_id)
        fs.id AS submission_id,
        fs.response_id,
        fs.submit_date + td.diff AS submit_date,
        fs.location
    FROM form_submissions fs
    CROSS JOIN td
    WHERE fs.form_id IN (SELECT nugget_id FROM form_ids)
    AND fs.submit_date >= CURRENT_DATE - INTERVAL '60 days'
    AND fs.location IN (SELECT location_name FROM allowed_locations)
    ORDER BY fs.response_id, fs.id DESC
),
-- Get responses (NO question_type filter here!)
responses_parsed AS (
    SELECT 
        rs.response_id,
        rs.location,
        fr.question_id AS qid,
        fr.response -> 'selected' ->> 0 AS response_value
    FROM recent_submissions rs
    JOIN form_responses fr ON fr.form_submit_id = rs.submission_id
    WHERE fr.question_id IN (SELECT qid FROM all_questions)  -- Only audit questions
    AND fr.response -> 'selected' ->> 0 IS NOT NULL  -- Has a selected value
),
-- Match responses with their scores
responses_with_scores AS (
    SELECT 
        rp.response_id,
        rp.location,
        rp.qid,
        qo.question,
        rp.response_value,
        COALESCE(qo.score, 0) AS score_earned,
        CASE 
            WHEN COALESCE(qo.score, 0) = 0 THEN 1
            ELSE 0
        END AS is_deviation
    FROM responses_parsed rp
    INNER JOIN question_options qo 
        ON qo.qid = rp.qid 
        AND qo.option_value = rp.response_value
),
-- Calculate deviation summary
deviation_summary AS (
    SELECT 
        question AS checkpoint,
        COUNT(DISTINCT location) AS total_stores_checked,
        SUM(is_deviation) AS total_deviations,
        COUNT(DISTINCT CASE WHEN is_deviation = 1 THEN location END) AS stores_with_deviation,
        ROUND(
            (COUNT(DISTINCT CASE WHEN is_deviation = 1 THEN location END)::NUMERIC / 
             NULLIF(COUNT(DISTINCT location), 0)) * 100, 
            1
        ) AS deviation_percentage,
        STRING_AGG(DISTINCT 
            CASE WHEN is_deviation = 1 THEN response_value END, 
            ', '
        ) AS deviation_answers
    FROM responses_with_scores
    GROUP BY question
    HAVING COUNT(DISTINCT location) >= 3
)
-- Final output: Top 10 deviations
SELECT 
    ROW_NUMBER() OVER (ORDER BY deviation_percentage DESC, total_deviations DESC) AS rank,
    checkpoint,
    deviation_percentage,
    stores_with_deviation AS stores_missed,
    total_stores_checked,
    total_deviations AS points_lost,
    deviation_answers AS wrong_answer
FROM deviation_summary
WHERE deviation_percentage > 0
ORDER BY deviation_percentage DESC, total_deviations DESC
```

---

## AM Visits Report_AM Visits and Shift Management Report.sql

**Tables referenced:** allowed_locations, form_ids, form_responses, form_submissions, inside, jsonb_each, nuggets, organizations, outside, qd_logic, qd_logic_raw, qd_main, question_definitions, responses_parsed, s.submit_date, submissions, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: AM Visits Report
-- Dashboard: AM Visits and Shift Management Report
-- Category: Samosa Party
-- Extracted: 2026-01-29 16:52:31
-- ============================================================

WITH td AS (
    SELECT 
        COALESCE(o.tzoffset, 0) as tzoffset,
        interval '1 min' * COALESCE(o.tzoffset, 0) AS diff
    FROM organizations o
    WHERE o.id IN (
        SELECT organization FROM nuggets 
        WHERE title ILIKE 'AM Store Visit Checklist%' 
        AND title NOT ILIKE '%shift%' 
        LIMIT 1
    )
),
form_ids AS (
    SELECT id AS nugget_id
    FROM nuggets
    WHERE title ILIKE 'AM Store Visit Checklist%'
    AND title NOT ILIKE '%shift%'
),
allowed_locations AS (
    SELECT unnest(ARRAY[
        'Airport Road',
        'Alpha 2 Greater Noida',
        'Ameerpet',
        'Ananth Nagar',
        'Aparna Mall',
        'AS Rao Nagar',
        'Bagmane',
        'Bagmane (CV Raman Nagar)',
        'Banashankari',
        'Bannerghatta',
        'Begur',
        'Bellandur',
        'BLR - CK - Manyta Tech Park',
        'BLR - CK - Panathur',
        'BLR - DN - Airport T-1',
        'BLR - DN - Ayyappa Nagar',
        'BLR - DN - Bagalur',
        'BLR - DN - Budigere',
        'BLR - DN - Channapatna',
        'BLR - DN - Ecoworld',
        'BLR - DN - Galleria Mall',
        'BLR - DN - Haralur',
        'BLR - DN - Kaggadasapura',
        'BLR - DN - Kengeri',
        'BLR - DN - Park Square Mall (ITPL)',
        'CBD',
        'Chandapura',
        'Channasandra',
        'Crossing Republic',
        'Dasarahalli',
        'Defence Colony',
        'Dilshad Garden',
        'Dilshukh Nagar',
        'Dommasandra',
        'Dwarka',
        'East Patel Nagar',
        'Eco Space',
        'EGL',
        'Electronic City',
        'Faridabad SEC16',
        'Gaur City- Noida Extension',
        'Hennur',
        'HSR Layout',
        'HSR Layout Sector 3',
        'Hyd - CK - Padmarao Nagar',
        'HYD - DN - Sun City',
        'Indiranagar 12B',
        'Indirapuram',
        'Jeevan Bhima Nagar',
        'JP Nagar',
        'Kalyan Nagar',
        'Kanakapura Dine-In',
        'Kanakpura Road',
        'Kondapur',
        'Koramangala',
        'Kukatpally',
        'Laxmi Nagar',
        'Madhapur',
        'Mahadevpura',
        'Malviya Nagar',
        'Manikonda',
        'Marathalli',
        'Mehdipatnam',
        'Murgeshpalya',
        'Nagarbhavi',
        'NCR - DN - Advant Tech Park',
        'NCR - DN - Sector 120 Central Market',
        'NCR - DN - Star Tower',
        'NCR - DN- Janakpuri',
        'NCR - DN- Shalimar Bag',
        'New BEL Rd',
        'Nexus Koramangala',
        'Nexus Shantiniketan',
        'Old Madras Road',
        'Pragathi Nagar',
        'Raj Nagar',
        'Rajaji Nagar',
        'Rohini',
        'Royasandra',
        'RR Nagar',
        'RT Nagar',
        'Sahakar Nagar',
        'Sarita Vihar',
        'Sarjapur',
        'Sector 4 Gurgaon',
        'Sector 56',
        'Sector 90',
        'Sector- 4 Noida',
        'Singasandra',
        'Sohna Road',
        'Sushant Lok',
        'TC Palya',
        'TechnoStar (AECS)',
        'Udyog Vihar, Phase V',
        'Uttam Nagar',
        'Varthur',
        'Vasant Kunj',
        'Whitefield',
        'NCR - CK - Palam Vihar',
        'NCR - CK - Sector 65',
        'TN - CK - Karapakkam',
        'BLR - DN - Neo Town',
        'NCR - DN - Pacific Mall(Dwarka 21)'
    ]) AS location_name
),
qd_main AS (
    SELECT 
        question_id AS qid,
        question_type,
        question AS question_text,
        sqno::integer AS sort_order
    FROM question_definitions
    WHERE nugget_id IN (SELECT nugget_id FROM form_ids)
    AND question_type NOT IN ('table', 'section')
),
qd_logic_raw AS (
    SELECT 
        sqno,
        jsonb_array_elements(definition -> 'logic') -> 'questions' as q
    FROM question_definitions
    WHERE nugget_id IN (SELECT nugget_id FROM form_ids)
    AND definition -> 'logic' IS NOT NULL
),
qd_logic AS (
    SELECT 
        def.key AS qid,
        def.value->>'question_type' AS question_type,
        NULL AS question_text,
        sqno::integer * 10000 + (def.value->>'order')::integer AS sort_order
    FROM qd_logic_raw
    CROSS JOIN jsonb_each(q) def
),
all_questions AS (
    SELECT * FROM qd_main
    UNION
    SELECT * FROM qd_logic
),
submissions AS (
    SELECT DISTINCT ON (fs.location)
        fs.id AS submission_id,
        fs.response_id,
        fs.sno,
        fs.submit_date + td.diff AS submit_date,
        fs.user_id,
        fs.location,
        fs.organization
    FROM form_submissions fs
    CROSS JOIN td
    WHERE fs.form_id IN (SELECT nugget_id FROM form_ids)
    AND fs.location IN (SELECT location_name FROM allowed_locations)
    ORDER BY fs.location, fs.submit_date DESC, fs.id DESC
),
responses_parsed AS (
    SELECT 
        fr.form_submit_id AS submission_id,
        fr.question_id AS qid,
        qd.question AS question_text,
        CASE
            WHEN fr.question_type IN ('dropdown', 'multiple_choice', 'linear_scale', 'audit') 
                THEN fr.response -> 'selected' ->> 0
            WHEN fr.question_type IN ('checkboxes') 
                THEN array_to_string(ARRAY(
                    SELECT jsonb_array_elements_text(fr.response->'selected')
                    UNION 
                    SELECT CASE WHEN fr.response->>'otherText' IS NOT NULL 
                        THEN fr.response->>'otherText' END
                ), ', ')
            WHEN fr.question_type IN ('date', 'datetime') 
                THEN to_char(to_timestamp((fr.response::text::bigint)/1000), 'YYYY-MM-DD HH24:MI:SS')
            WHEN fr.question_type IN ('long_text_field', 'single_text_field', 'qr_code', 'formula') 
                THEN fr.response ->> 0
            WHEN fr.question_type IN ('upload_file', 'upload_image', 'upload_video', 'upload_mixed') 
                THEN COALESCE((fr.response)->0->>'response', fr.response::text)
            WHEN fr.question_type IN ('location', 'signature', 'division', 'sub_division') 
                THEN fr.response ->> 'name'
            WHEN fr.question_type = 'user'
                THEN fr.response::text
            ELSE fr.response::text
        END AS response_value
    FROM form_responses fr
    JOIN form_submissions fs ON fr.form_submit_id = fs.id
    LEFT JOIN question_definitions qd ON fr.question_id = qd.question_id AND fs.form_id = qd.nugget_id
    WHERE fr.form_submit_id IN (SELECT submission_id FROM submissions)
    AND fr.question_type NOT IN ('section', 'nested')
)
SELECT 
    s.response_id,
    s.sno AS submission_number,
    s.submit_date,
    s.location AS store_location,
    s.organization,
    ud.identifier AS employee_id,
    CONCAT(ud.first_name, ' ', ud.last_name) AS employee_name,
    ud.first_name,
    ud.last_name,
    ud.phone_number,
    ud.email,
    ud.department,
    ud.designation,
    ud.job_type,
    ud.job_location,
    ud.division,
    ud.sub_division,
    (CURRENT_DATE - s.submit_date::date)::INTEGER AS days_since_submission,
    TO_CHAR(s.submit_date, 'YYYY-MM') AS submission_month,
    TO_CHAR(s.submit_date, 'YYYY-Week-WW') AS submission_week,
    EXTRACT(YEAR FROM s.submit_date) AS submission_year,
    EXTRACT(QUARTER FROM s.submit_date) AS submission_quarter,

    MAX(CASE WHEN pr.question_text ILIKE 'All food stock shortage value below 1000%' THEN pr.response_value END) AS all_food_stock_shortage_value_below_1000,
    MAX(CASE WHEN pr.question_text ILIKE 'Physical closing is done on Agave cloud app%' THEN pr.response_value END) AS physical_closing_is_done_on_agave_cloud_app_for_yesterday_la,
    MAX(CASE WHEN pr.question_text ILIKE 'Write the name of the Hustlers present during the Audit%' THEN pr.response_value END) AS write_the_name_of_the_hustlers_present_during_the_audit,
    MAX(CASE WHEN pr.question_text ILIKE 'Overall Maintenance & Cleaning is there in the Store%' THEN pr.response_value END) AS overall_maintenance_cleaning_is_there_in_the_store,
    MAX(CASE WHEN pr.question_text ILIKE 'All "open foods" kept wrapped%' THEN pr.response_value END) AS all_open_foods_kept_wrapped_eg_sugar_chilli_powder_etc,
    MAX(CASE WHEN pr.question_text ILIKE 'Internet working with good condition%' THEN pr.response_value END) AS internet_working_with_good_condition,
    MAX(CASE WHEN pr.question_text ILIKE 'Fingernails must be kept clean%' THEN pr.response_value END) AS fingernails_must_be_kept_clean_well_clipped_filed_and_shaped,
    MAX(CASE WHEN pr.question_text ILIKE 'Trade license renewed and pasted%' THEN pr.response_value END) AS trade_license_renewed_and_pasted_in_a_visible_place,
    MAX(CASE WHEN pr.question_text ILIKE 'Whether the details of short receipt%' THEN pr.response_value END) AS whether_the_details_of_short_receipt_excess_receipts_damage_,
    MAX(CASE WHEN pr.question_text ILIKE 'Audit Info%' THEN pr.response_value END) AS audit_info,
    MAX(CASE WHEN pr.question_text ILIKE 'Google review/ Customer feedback improved%' THEN pr.response_value END) AS google_review_customer_feedback_improved_from_last_month_to_,
    MAX(CASE WHEN pr.question_text ILIKE 'Opening cash available at the cash counter%' THEN pr.response_value END) AS opening_cash_available_at_the_cash_counter,
    MAX(CASE WHEN pr.question_text ILIKE 'Outlet furniture and fittings cleaned%' THEN pr.response_value END) AS outlet_furniture_and_fittings_cleaned_and_sanitized,
    MAX(CASE WHEN pr.question_text ILIKE 'Audit Guidelines%' THEN pr.response_value END) AS audit_guidelines,
    MAX(CASE WHEN pr.question_text ILIKE 'Tab, Laptop, billing machine, Television working%' THEN pr.response_value END) AS tab_laptop_billing_machine_television_working_in_good_condit,
    MAX(CASE WHEN pr.question_text ILIKE 'Grooming%' THEN pr.response_value END) AS grooming,
    MAX(CASE WHEN pr.question_text ILIKE 'Are all employees wearing a complete uniform%' THEN pr.response_value END) AS are_all_employees_wearing_a_complete_uniform_t_shirt_belt_bl,
    MAX(CASE WHEN pr.question_text ILIKE 'Outlet Opening checklist is being followed%' THEN pr.response_value END) AS outlet_opening_checklist_is_being_followed,
    MAX(CASE WHEN pr.question_text ILIKE 'Store Name%' THEN pr.response_value END) AS store_name,
    MAX(CASE WHEN pr.question_text ILIKE 'All packing material stock shortage%' THEN pr.response_value END) AS all_packing_material_stock_shortage_is_under_rs_1000,
    MAX(CASE WHEN pr.question_text ILIKE 'Tea machine/Boiler and induction stove%' THEN pr.response_value END) AS tea_machineboiler_and_induction_stove_and_stationinduction_s,
    MAX(CASE WHEN pr.question_text ILIKE 'Store location showing correct in google map%' THEN pr.response_value END) AS store_location_showing_correct_in_google_map,
    MAX(CASE WHEN pr.question_text ILIKE 'Daily attendance marking in GreytHR%' THEN pr.response_value END) AS daily_attendance_marking_in_greythr,
    MAX(CASE WHEN pr.question_text ILIKE 'Electricity Bill Reading till date updated%' THEN pr.response_value END) AS electricity_bill_reading_till_date_updated,
    MAX(CASE WHEN pr.question_text ILIKE 'Are there any Food Items kept near the chemical%' THEN pr.response_value END) AS are_there_any_food_items_kept_near_the_chemical_area,
    MAX(CASE WHEN pr.question_text ILIKE 'Store having a weight machine%' THEN pr.response_value END) AS store_having_a_weight_machine,
    MAX(CASE WHEN pr.question_text ILIKE 'Daily Cash report is being sent to Finance%' THEN pr.response_value END) AS daily_cash_report_is_being_sent_to_finance,
    MAX(CASE WHEN pr.question_text ILIKE 'Last month cash matching to the system%' THEN pr.response_value END) AS last_month_cash_matching_to_the_system,
    MAX(CASE WHEN pr.question_text ILIKE 'Outlet Closing checklist is being followed%' THEN pr.response_value END) AS outlet_closing_checklist_is_being_followed,
    MAX(CASE WHEN pr.question_text ILIKE 'Any Expired product found%' THEN pr.response_value END) AS any_expired_product_found,
    MAX(CASE WHEN pr.question_text ILIKE 'Samosa Frying Machine from outside%' THEN pr.response_value END) AS samosa_frying_machine_from_outside_as_well_as_heating_coil_e,
    MAX(CASE WHEN pr.question_text ILIKE 'Daily Store Process%' THEN pr.response_value END) AS daily_store_process,
    MAX(CASE WHEN pr.question_text ILIKE 'Shops & Establishment license, FSSAI License%' THEN pr.response_value END) AS shops_establishment_license_fssai_license_and_music_license_,
    MAX(CASE WHEN pr.question_text ILIKE 'Write the Store rating on Swiggy%' THEN pr.response_value END) AS write_the_store_rating_on_swiggy_zomato,
    MAX(CASE WHEN pr.question_text ILIKE 'Audited Location%' THEN pr.response_value END) AS audited_location,
    MAX(CASE WHEN pr.question_text ILIKE 'Is the Internet used in the right way%' THEN pr.response_value END) AS is_the_internet_used_in_the_right_way,
    MAX(CASE WHEN pr.question_text ILIKE 'Clean shave daily%' THEN pr.response_value END) AS clean_shave_daily_using_a_sharp_razor,
    MAX(CASE WHEN pr.question_text ILIKE 'Store having a baloon blower machine%' THEN pr.response_value END) AS store_having_a_baloon_blower_machine,
    MAX(CASE WHEN pr.question_text ILIKE 'Date of Visit%' THEN pr.response_value END) AS date_of_visit,
    MAX(CASE WHEN pr.question_text ILIKE 'Store operation timing mentioned correctly%' THEN pr.response_value END) AS store_operation_timing_mentioned_correctly_in_google,
    MAX(CASE WHEN pr.question_text ILIKE 'Whether all the menu products available%' THEN pr.response_value END) AS whether_all_the_menu_products_available_in_store,
    MAX(CASE WHEN pr.question_text ILIKE 'CCTV working and covering%' THEN pr.response_value END) AS cctv_working_and_covering_the_inside_outlet_whole_area,
    MAX(CASE WHEN pr.question_text ILIKE 'Cleaning and Ambiance%' THEN pr.response_value END) AS cleaning_and_ambiance,
    MAX(CASE WHEN pr.question_text ILIKE 'Hustler was wearing head cap%' THEN pr.response_value END) AS hustler_was_wearing_head_cap_while_working_and_during_the_fo,
    MAX(CASE WHEN pr.question_text ILIKE 'Is the store having the access of recipe training%' THEN pr.response_value END) AS is_the_store_having_the_access_of_recipe_training_manual_in_,
    MAX(CASE WHEN pr.question_text ILIKE 'Waste disposed oil is kept properly%' THEN pr.response_value END) AS waste_disposed_oil_is_kept_properly_and_whether_it_is_being_,
    MAX(CASE WHEN pr.question_text ILIKE 'All chest freezers are kept clean%' THEN pr.response_value END) AS all_chest_freezers_are_kept_clean_at_the_top_and_from_the_in,
    MAX(CASE WHEN pr.question_text ILIKE 'Whether Petty cash policy has been followed%' THEN pr.response_value END) AS whether_petty_cash_policy_has_been_followed_and_also_check_i,
    MAX(CASE WHEN pr.question_text ILIKE 'Open Tickets in KNOW App%' THEN pr.response_value END) AS open_tickets_in_know_app,
    MAX(CASE WHEN pr.question_text ILIKE 'Hustlers coughing, sneezing or cold%' THEN pr.response_value END) AS hustlers_coughing_sneezing_or_cold_etc,
    MAX(CASE WHEN pr.question_text ILIKE 'Housekeeping material should be kept%' THEN pr.response_value END) AS housekeeping_material_should_be_kept_in_an_invisible_place_o,
    MAX(CASE WHEN pr.question_text ILIKE 'Whether inventory items%Packing materials%' THEN pr.response_value END) AS whether_inventory_itemspacking_materials_are_stored_at_their,
    MAX(CASE WHEN pr.question_text ILIKE 'The dustbin is clean from inside%' THEN pr.response_value END) AS the_dustbin_is_clean_from_inside_and_outside_remove_the_garb,
    MAX(CASE WHEN pr.question_text ILIKE 'If the store is facing any other issue%' THEN pr.response_value END) AS if_the_store_is_facing_any_other_issue_please_raise_ticket_i,
    MAX(CASE WHEN pr.question_text ILIKE 'Whether the expired products are discarded%' THEN pr.response_value END) AS whether_the_expired_products_are_discarded_properly_and_the_,
    MAX(CASE WHEN pr.question_text ILIKE 'EDC Machine details%' THEN pr.response_value END) AS edc_machine_details,
    MAX(CASE WHEN pr.question_text ILIKE 'Food Storage%' THEN pr.response_value END) AS food_storage,
    MAX(CASE WHEN pr.question_text ILIKE 'The rice cooker is clean%' THEN pr.response_value END) AS the_rice_cooker_is_clean_and_has_the_water_strainer_in_place,
    MAX(CASE WHEN pr.question_text ILIKE 'Maintenance & Cleaning%' THEN pr.response_value END) AS maintenance_cleaning,
    MAX(CASE WHEN pr.question_text ILIKE 'Freezer Temperature%' THEN pr.response_value END) AS freezer_temperature_18_c_to_24_c_and_maintained,
    MAX(CASE WHEN pr.question_text ILIKE 'Whether process with respect to Inter Store Transfer%' THEN pr.response_value END) AS whether_process_with_respect_to_inter_store_transfer_has_bee,
    MAX(CASE WHEN pr.question_text ILIKE 'Deployment chart made and followed%' THEN pr.response_value END) AS deployment_chart_made_and_followed_for_dinein_store_not_requ,
    MAX(CASE WHEN pr.question_text ILIKE 'If any Hustler is wearing fancy%' THEN pr.response_value END) AS if_any_hustler_is_wearing_fancy_wild_and_fashionable_hairsty,
    MAX(CASE WHEN pr.question_text ILIKE 'All GN pans are clean%' THEN pr.response_value END) AS all_gn_pans_are_clean_with_no_build_up,
    MAX(CASE WHEN pr.question_text ILIKE 'If any Hustler using chewing gum%' THEN pr.response_value END) AS if_any_hustler_using_chewing_gum_paan_masala_or_similar_subs,
    MAX(CASE WHEN pr.question_text ILIKE 'Are there any discontinued product%' THEN pr.response_value END) AS are_there_any_discontinued_product_raw_material_kept_in_the_,
    MAX(CASE WHEN pr.question_text ILIKE 'Chiller Temperature%' THEN pr.response_value END) AS chiller_temperature_0_c_to_5_c_maintained,
    MAX(CASE WHEN pr.question_text ILIKE 'Check any 10 products and attach%' THEN pr.response_value END) AS check_any_10_products_and_attach_a_picture_of_excel_sheet_ha,
    MAX(CASE WHEN pr.question_text ILIKE 'Inventory Management%' THEN pr.response_value END) AS inventory_management,
    MAX(CASE WHEN pr.question_text ILIKE 'The entire floor is clean%' THEN pr.response_value END) AS the_entire_floor_is_clean_including_the_area_under_the_washs,
    MAX(CASE WHEN pr.question_text = 'IT' THEN pr.response_value END) AS it,
    MAX(CASE WHEN pr.question_text ILIKE 'Sensitive Raw Material are handled%' THEN pr.response_value END) AS sensitive_raw_material_are_handled_stored_properly_eg_minera,
    MAX(CASE WHEN pr.question_text = 'Finance' THEN pr.response_value END) AS finance,
    MAX(CASE WHEN pr.question_text ILIKE 'All refrigeration, freezer, cold juice machine%' THEN pr.response_value END) AS all_refrigeration_freezer_cold_juice_machine_heat_display_co,
    MAX(CASE WHEN pr.question_text = 'HR' THEN pr.response_value END) AS hr,
    MAX(CASE WHEN pr.question_text ILIKE 'The vertical freezer top section%' THEN pr.response_value END) AS the_vertical_freezer_top_section_condenser_fan_grill_is_clea,
    MAX(CASE WHEN pr.question_text ILIKE 'Whether all sink areas%' THEN pr.response_value END) AS whether_all_sink_areas_kitchen_dishwashers_and_surrounding_a,
    MAX(CASE WHEN pr.question_text = 'Others' THEN pr.response_value END) AS others,
    MAX(CASE WHEN pr.question_text ILIKE 'Stock, Packing Material & Asset Maintenance%' THEN pr.response_value END) AS stock_packing_material_asset_maintenance,
    MAX(CASE WHEN pr.question_text ILIKE 'Whether yesterday''s garbage discarded%' THEN pr.response_value END) AS whether_yesterdays_garbage_discarded_and_the_dustbins_are_cl,
    MAX(CASE WHEN pr.question_text ILIKE 'All small tools/equipment are available%' THEN pr.response_value END) AS all_small_toolsequipment_are_available_and_working_poha_time,
    MAX(CASE WHEN pr.question_text ILIKE 'Hustler presented in Audit%' THEN pr.response_value END) AS hustler_presented_in_audit,
    MAX(CASE WHEN pr.question_text ILIKE 'Induction and new joiner assessment%' THEN pr.response_value END) AS induction_and_new_joiner_assessment_test_completed_for_all_n,
    MAX(CASE WHEN pr.question_text ILIKE 'Lux level to be recorded%' THEN pr.response_value END) AS lux_level_to_be_recorded_during_audit_at_all_working_station,
    MAX(CASE WHEN pr.question_text ILIKE 'Pest control activity is done%' THEN pr.response_value END) AS pest_control_activity_is_done_as_per_the_schedule_from_the_a,
    MAX(CASE WHEN pr.question_text ILIKE 'There are no pest droppigs%' THEN pr.response_value END) AS there_are_no_pest_droppigs_or_cockroaches_or_pest_infestatio,
    MAX(CASE WHEN pr.question_text ILIKE 'Explain the importance of keeping the open materials%' THEN pr.response_value END) AS explain_the_importance_of_keeping_the_open_materials_wrapped,
    MAX(CASE WHEN pr.question_text ILIKE 'Remarks%' THEN pr.response_value END) AS remarks
FROM submissions s
LEFT JOIN responses_parsed pr ON pr.submission_id = s.submission_id
LEFT JOIN user_details ud ON s.user_id = ud.uuid
GROUP BY 
    s.response_id, s.sno, s.submit_date, s.location, s.organization,
    ud.identifier, ud.first_name, ud.last_name, ud.phone_number, ud.email,
    ud.department, ud.designation, ud.job_type, ud.job_location, ud.division, ud.sub_division
ORDER BY s.submit_date DESC
```

---

## Routine Compliance Samosa Party Report_Routine Compliance - Report.sql

**Tables referenced:** form_compliance_v2, location_acl, organizations, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Routine Compliance Samosa Party Report
-- Dashboard: Routine Compliance - Report
-- Category: Samosa Party
-- Extracted: 2026-01-29 16:53:05
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
		"QueryTable 1"."Date Mod" AS "Date Mod"
FROM( SELECT
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
		"QueryTable 1"."Date Mod" AS "Date Mod"
FROM(WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'sampar-cartwheel'
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
                  WHERE ug2.user_id = @{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = 'sampar-cartwheel')
select fc.*, to_char("Date", 'YYYY-MM-DD') as "Date Mod"
from form_compliance_v2 fc
join location_acl on fc."Location" = location_acl.job_location
where fc."Organization" ='sampar-cartwheel'
	 and fc."Reminded At" >= date_trunc('week', CURRENT_DATE)
order by 1, 5, 2 desc, 6 desc, 4)"QueryTable 1")"QueryTable 1"
```

---

## Routine Compliance Samosa Party_Routine Compliance.sql

**Tables referenced:** acl, am, am_groups, form_compliance_v2, location_acl, organizations, store_map, stores, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Routine Compliance Samosa Party
-- Dashboard: Routine Compliance
-- Category: Samosa Party
-- Extracted: 2026-01-29 16:53:04
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
		"QueryTable 1"."Area Manager" AS "Area Manager"
FROM( SELECT
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
		"QueryTable 1"."Area Manager" AS "Area Manager"
FROM(WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'sampar-cartwheel'
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'All',
                              'HO')
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
     td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'sampar-cartwheel'),
     stores AS
  (SELECT *
   FROM user_details
   WHERE designation = 'Store'
     AND organization = 'sampar-cartwheel'),
     am AS
  (SELECT *
   FROM user_details
   WHERE designation = 'Area Manager'
   and is_active = true
     AND organization = 'sampar-cartwheel'),
     am_groups AS
  (SELECT am.*,
          group_id
   FROM user_groups ug
   JOIN am ON ug.user_id = am.uuid
   AND ug.has_access = 'true'),
     acl AS
  (SELECT stores.first_name AS store,
          stores.division AS region,
          stores.sub_division AS city,
          am_groups.uuid AS am_knid
   FROM stores
   LEFT OUTER JOIN user_groups ug ON stores.uuid = ug.user_id
   AND ug.is_active = 'true'
   LEFT OUTER JOIN am_groups ON ug.group_id = am_groups.group_id),
     store_map AS
  (SELECT acl.store,
          acl.region,
          acl.city,
          acl.am_knid,
          am.first_name||' '||am.last_name AS am_name,
          am.identifier AS am_identifier
   FROM acl
   LEFT OUTER JOIN user_details am ON acl.am_knid = am.uuid
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6
   HAVING am_knid IS NOT NULL
   ORDER BY 2,
            3,
            4,
            1)
SELECT fc.*,
                   sm.am_name||' - '||sm.am_identifier AS "Area Manager"
                  
FROM form_compliance_v2 fc
left outer JOIN location_acl ON fc."Location" = location_acl.job_location
left outer JOIN store_map sm ON fc."Location" = sm.store
WHERE fc."Organization" = 'sampar-cartwheel'
and fc."Reminded At" between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
ORDER BY 1, 5, 2 desc, 6 desc, 4)"QueryTable 1")"QueryTable 1"
```

---

## Samosa Party Course Report_Learn.sql

**Tables referenced:** analytics.nugget_analytics_raw, analytics.nuggets_user_share_requests, cards, cards_consumed, final_quiz_cards, final_scores, latest_attempt, latest_course_received, latest_course_shares, latest_received, latest_share_ids, organizations, progress, public.courses, public.learning_journey_courses, public.lesson_cards, public.lessons, quiz.quiz_responses, quiz_status, td, user_acl, user_details, user_groups

**Columns needing snake_case conversion:**

- `latestAttempt` -> `latest_attempt` (alias: `latest_attempt AS "latestAttempt"`)

- `passMark` -> `pass_mark` (alias: `pass_mark AS "passMark"`)

- `qCount` -> `q_count` (alias: `q_count AS "qCount"`)


**Original Query:**

```sql
-- Data Source: Samosa Party Course Report
-- Dashboard: Learn
-- Category: Samosa Party
-- Extracted: 2026-01-29 16:57:03
-- ============================================================

WITH user_acl AS
  (SELECT ud.organization,
          ud.uuid,
          ud.first_name||' '||ud.last_name AS emp_name,
          ud.identifier AS emp_id,
          ud.division,
          ud.sub_division,
          ud.job_location,
          ud.department,
          ud.designation,
          ud.job_type
   FROM user_details ud
   WHERE organization = @{{:OrganizationParameter}}
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
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
               AND ug1.is_active = TRUE))
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10),
     td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = @{{:OrganizationParameter}}),
     latest_share_ids AS
  (SELECT DISTINCT ON (nugget_id,
                       user_id) nugget_id,
                      share_id,
                      user_id,
                      created_at AS sent_at
   FROM analytics.nuggets_user_share_requests nusr
   JOIN user_acl ud ON nusr.user_id = ud.uuid
   WHERE created_at BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP + interval '1 day'
   ORDER BY 1,
            3,
            created_at DESC),
     latest_course_shares AS
  (SELECT lsi.user_id,
          lsi.nugget_id AS course_id,
          lsi.share_id,
          lsi.sent_at,
          1 AS seq
   FROM latest_share_ids lsi
   JOIN public.courses c ON lsi.nugget_id = c.id
   WHERE c.organization = @{{:OrganizationParameter}}
   UNION ALL SELECT lsi.user_id,
                    ljc.course_id,
                    lsi.share_id,
                    lsi.sent_at,
                    (seq::int)+1 AS seq
   FROM latest_share_ids lsi
   JOIN public.learning_journey_courses ljc ON lsi.nugget_id = ljc.learning_journey_id
   JOIN public.courses c ON ljc.course_id = c.id),
     latest_received AS
  (SELECT ra.user_id,
          ra.nugget_id,
          ra.share_id,
          ra.created_at AS received_at
   FROM analytics.nugget_analytics_raw ra
   JOIN latest_share_ids lsi ON ra.user_id = lsi.user_id
   AND ra.nugget_id = lsi.nugget_id
   AND ra.share_id = lsi.share_id
   WHERE ra.event_id NOT IN (1,
                             7)),
     latest_course_received AS
  (SELECT lr.user_id,
          lr.nugget_id AS course_id,
          lr.share_id,
          min(lr.received_at) AS received_at
   FROM latest_received lr
   JOIN public.courses c ON lr.nugget_id = c.id
   WHERE c.organization = @{{:OrganizationParameter}}
   GROUP BY 1,
            2,
            3
   UNION ALL SELECT lr.user_id,
                    ljc.course_id,
                    lr.share_id,
                    min(lr.received_at) AS received_at
   FROM latest_received lr
   JOIN public.learning_journey_courses ljc ON lr.nugget_id = ljc.learning_journey_id
   JOIN public.courses c ON ljc.course_id = c.id
   WHERE c.organization = @{{:OrganizationParameter}}
   GROUP BY 1,
            2,
            3),
     cards AS
  (SELECT l.course_id,
          lc.id AS card_id
   FROM public.lesson_cards lc
   JOIN public.lessons l ON l.id = lc.lesson_id
   JOIN public.courses c ON l.course_id = c.id
   WHERE c.organization = @{{:OrganizationParameter}}
   GROUP BY 1,
            2),
     cards_consumed AS
  (SELECT ra.user_id,
          lcs.seq,
          ra.course_id,
          ra.share_id,
          lc.card_id,
          ra.lang,
          min(ra.created_at) AS consumed_at
   FROM analytics.nugget_analytics_raw ra
   JOIN latest_course_shares lcs ON ra.user_id = lcs.user_id
   AND ra.course_id = lcs.course_id
   AND ra.share_id = lcs.share_id
   JOIN cards lc ON lc.course_id = ra.course_id
   AND lc.card_id = ra.nugget_id
   WHERE ra.event_id = 3
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6
   ORDER BY 1,
            2,
            3,
            4,
            5),
     progress AS
  (SELECT cc.user_id,
          cc.course_id,
          cc.share_id,
          count(distinct(cc.card_id)) AS consumed_count
   FROM cards_consumed cc
   GROUP BY 1,
            2,
            3),
     final_quiz_cards AS
  (SELECT DISTINCT ON (c.id) c.id AS course_id,
                      lc.id AS quizcard_id,
                      jsonb_array_length(lc.payload -> 'questions') AS qCount,
                      (lc.settings->>'passMark')::numeric AS pass_mark
   FROM public.lesson_cards lc
   JOIN public.lessons l ON lc.lesson_id = l.id
   JOIN public.courses c ON l.course_id = c.id
   WHERE c.organization = @{{:OrganizationParameter}}
     AND lc.type = 'quiz'
   ORDER BY c.id,
            l.seq DESC, lc.seq DESC),
     latest_attempt AS
  (SELECT qr.user_id,
          qr.course_id,
          qr.share_id,
          qr.card_id,
          qr.question_id,
          max(attempt) AS latestAttempt
   FROM quiz.quiz_responses qr
   JOIN latest_course_shares lcs ON qr.user_id = lcs.user_id
   AND qr.course_id = lcs.course_id
   AND qr.share_id = lcs.share_id
   JOIN final_quiz_cards qc ON qr.course_id = qc.course_id
   AND qr.card_id = qc.quizcard_id
   GROUP BY 1,
            2,
            3,
            4,
            5),
     final_scores AS
  (SELECT la.user_id,
          la.course_id,
          la.share_id,
          qc.quizcard_id,
          qc.pass_mark,
          qc.qcount,
          count(distinct(CASE
                             WHEN qr.is_correct = TRUE THEN qr.question_id
                             ELSE NULL
                         END))::numeric AS correct_count
   FROM latest_attempt la
   JOIN quiz.quiz_responses qr ON la.user_id = qr.user_id
   AND la.course_id = qr.course_id
   AND la.share_id = qr.share_id
   AND la.card_id = qr.card_id
   AND la.question_id = qr.question_id
   AND la.latestAttempt = qr.attempt
   JOIN final_quiz_cards qc ON qr.course_id = qc.course_id
   AND qr.card_id = qc.quizcard_id
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6),
     quiz_status AS
  (SELECT fs.user_id,
          fs.course_id,
          fs.share_id,
          count(distinct(quizcard_id)) AS no_of_quizzes,
          count(distinct(CASE
                             WHEN correct_count >= pass_mark THEN quizcard_id
                             ELSE NULL
                         END)) AS passed_quizzes,
          sum(correct_count) *100 / sum(qcount) AS score_in_pct
   FROM final_scores fs
   GROUP BY 1,
            2,
            3)
SELECT ud.organization,
       c.name as course_name,
       ud.emp_name,
       ud.emp_id,
       ud.division,
       ud.sub_division,
       ud.job_location AS LOCATION,
       ud.department,
       ud.designation,
       ud.job_type,
       lcs.sent_at + td.diff AS shared_at,
       max(cc.consumed_at + td.diff) AS completed_at,
       CASE
           WHEN (c.total_cards > 0
                 AND p.consumed_count = c.total_cards) THEN 'Completed'
           WHEN c.total_cards > 0
                AND p.consumed_count > 0
                AND p.consumed_count < c.total_cards THEN 'In Progress'
           WHEN c.total_cards > 0
                AND (p.consumed_count = 0
                     OR p.consumed_count IS NULL) THEN 'Not Started'
           ELSE NULL
       END AS course_status,
      CASE
           WHEN (c.total_cards > 0
                 AND p.consumed_count = c.total_cards)
                AND s.no_of_quizzes = 0 THEN 'NA'
           WHEN (c.total_cards > 0
                 AND p.consumed_count = c.total_cards)
                AND s.no_of_quizzes > 0
                AND s.passed_quizzes >= s.no_of_quizzes THEN 'Pass'
           WHEN (c.total_cards > 0
                 AND p.consumed_count = c.total_cards)
                AND s.no_of_quizzes > 0
                AND s.passed_quizzes < s.no_of_quizzes THEN 'Fail'
           ELSE NULL
       END AS quiz_status,
       s.score_in_pct,
       lcs.course_id AS course_knid,
       ud.uuid AS user_knid,
	   to_char(lcs.sent_at + td.diff, 'YYYY-MM-DD') as shared_date,
	   to_char(lcs.sent_at + td.diff, 'HH24::MI') as shared_time,
	   to_char(max(cc.consumed_at + td.diff), 'YYYY-MM-DD') as consumed_date,
	   to_char(max(cc.consumed_at + td.diff), 'HH24:MI') as consumed_time
	   
	   /*,
       (p.consumed_count::numeric) / (c.total_cards::numeric) AS completion_pct,
       upper(cc.lang) AS LANGUAGE*/
FROM user_acl ud
JOIN latest_course_shares lcs ON lcs.user_id = ud.uuid
LEFT OUTER JOIN latest_course_received lcr ON lcs.user_id = lcr.user_id
AND lcs.course_id = lcr.course_id
AND lcs.share_id = lcr.share_id
LEFT OUTER JOIN progress p ON lcs.user_id = p.user_id
AND lcs.course_id = p.course_id
AND lcs.share_id = p.share_id
LEFT OUTER JOIN cards_consumed cc ON lcs.user_id = cc.user_id
AND lcs.course_id = cc.course_id
AND lcs.share_id = cc.share_id
LEFT OUTER JOIN quiz_status s ON lcs.user_id = s.user_id
AND lcs.course_id = s.course_id
AND lcs.share_id = s.share_id
LEFT OUTER JOIN public.courses c ON lcs.course_id = c.id
LEFT OUTER JOIN td ON ud.organization = td.organization
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
         13,
         14,
         15,
         16,
         17, 18, 19
ORDER BY 1,
         2,
         13,
         5,
         6,
         7,
         3
```

---

## Samosa Party Travel Reimbursement_Travel Reimbursement.sql

**Tables referenced:** RAW, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, results, user_details

**Columns needing snake_case conversion:**

- `endDate` -> `end_date` (alias: `end_date AS "endDate"`)

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `startDate` -> `start_date` (alias: `start_date AS "startDate"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)

- `userName` -> `user_name` (alias: `user_name AS "userName"`)


**Original Query:**

```sql
-- Data Source: Samosa Party Travel Reimbursement
-- Dashboard: Travel Reimbursement
-- Category: Samosa Party
-- Extracted: 2026-01-29 16:53:23
-- ============================================================

WITH forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ILIKE 'Travel Reimbursement Form%'),
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
     fs AS
  (SELECT DISTINCT ON (response_id) form_submissions.*,
                      form_name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   where form_submissions.submit_date at time zone 'Asia/Kolkata' between @{{:startDate}}::timestamp and @{{:endDate}}::timestamp  +interval '1 day'
   ORDER BY response_id,
            id DESC),
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
   JOIN fs ON fs.id = fr.form_submit_id
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
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
     RAW AS
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
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Kolkata', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('user') THEN fr.response::text
              WHEN fd.q_type IN ('upload_mixed',
                                 'upload_image',
                                 'upload_video',
								'upload_file') THEN (fr.response)->0->>'response'
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
          fr.submit_date AS submit_date,
          user_id
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
            12,
            13
   ORDER BY 1,
            2,
            3),
results as (
	SELECT response_id AS "Submission KNID",
       sno AS "Submission No",
       r.user_id,
       max(CASE
               WHEN question = 'Fill at start of travel' THEN (to_timestamp((section_response->>'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Kolkata')::date
               ELSE NULL
           END) AS "Date",
       max(CASE
               WHEN question = 'Name' THEN (response::json)->'selected'->0->>'userName'
               ELSE NULL
           END) AS "Name",
       max(CASE
               WHEN question = 'Name' THEN (response::json)->'selected'->0->>'identifier'
               ELSE NULL
           END) AS "Employee ID",
       max(CASE
               WHEN question = 'Name' THEN (response::json)->'selected'->0->>'department'
               ELSE NULL
           END) AS "Department",
       max(CASE
               WHEN question = 'Name' THEN (response::json)->'selected'->0->>'designation'
               ELSE NULL
           END) AS "Designation",
       max(CASE
               WHEN question = 'Name' THEN (response::json)->'selected'->0->>'location'
               ELSE NULL
           END) AS "Location",
       max(CASE
               WHEN question = 'Mode of travel' THEN response
               ELSE NULL
           END) AS "Mode of Travel",
       max(CASE
               WHEN question = 'Fill at start of travel' THEN to_timestamp((section_response->>'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Kolkata'
               ELSE NULL
           END) AS "Travel Start Time",
       max(CASE
               WHEN question = 'Fill on reaching your location' THEN to_timestamp((section_response->>'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Kolkata'
               ELSE NULL
           END) AS "Travel End Time",
       max(CASE
               WHEN question = 'Fill at start of travel' THEN 'https://www.google.com/maps/place/'||(section_response->'location'->>'lat')||','||(section_response->'location'->>'lng')
               ELSE NULL
           END) AS "Travel Start Lat/Long",
       max(CASE
               WHEN question = 'Fill on reaching your location' THEN 'https://www.google.com/maps/place/'||(section_response->'location'->>'lat')||','||(section_response->'location'->>'lng')
               ELSE NULL
           END) AS "Travel End Lat/Long",
		   'https://www.google.com/maps/dir/?api=1&origin='||(max(CASE
               WHEN question = 'Fill at start of travel' THEN (section_response->'location'->>'lat')||','||(section_response->'location'->>'lng')
               ELSE NULL
           END))||'&destination='||max(CASE
               WHEN question = 'Fill on reaching your location' THEN (section_response->'location'->>'lat')||','||(section_response->'location'->>'lng')
               ELSE NULL
           END) as "Distance Measure URL",
       max(CASE
               WHEN question = 'Fill at start of travel' THEN section_response->'location'->>'address'
               ELSE NULL
           END) AS "Travel Start Address",
       max(CASE
               WHEN question = 'Fill on reaching your location' THEN section_response->'location'->>'address'
               ELSE NULL
           END) AS "Travel End Address",
       max(CASE
               WHEN question = 'Any travel charges/ receipts' THEN response
               ELSE NULL
           END) AS "Travel Charges",
  max(CASE
               WHEN question = 'Invoice Image' THEN response
               ELSE NULL
           END) AS "Invoice",
       max(CASE
               WHEN question = 'Fill at start of travel' THEN (section_response->>'sentAt')::bigint 
               ELSE NULL
           END) AS "Submission Epoch",
       max(CASE
               WHEN question = 'Fill at start of travel' THEN section_response->'sender'->>'userId'
               ELSE NULL
           END) AS "Sender KNID"
FROM RAW r
GROUP BY 1,
         2,
         3
)
select r."Submission KNID",
r."Submission No",
r."Date",
coalesce(r."Name", ud.first_name ||' ' || ud.last_name) "Name",
coalesce(r."Employee ID", ud.identifier) "Employee ID",
coalesce(r."Department", ud.department) "Department",
coalesce(r."Designation", ud.designation) "Designation",
coalesce(r."Location", ud.job_location) "Location",
r."Mode of Travel",
r."Travel Start Time",
r."Travel End Time",
r."Travel Start Lat/Long",
r."Travel End Lat/Long",
r."Distance Measure URL",
r."Travel Start Address",
r."Travel End Address",
r."Travel Charges",
r."Invoice",
r."Submission Epoch",
r."Sender KNID"
from results r
join user_details ud 
on r.user_id = ud.uuid
ORDER BY 3 DESC,
         2
```

---

## Shift Management Report_AM Visits and Shift Management Report.sql

**Tables referenced:** allowed_locations, form_ids, form_responses, form_submissions, jsonb_each, nuggets, organizations, qd_logic, qd_logic_raw, qd_main, question_definitions, responses_parsed, s.submit_date, submissions, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Shift Management Report
-- Dashboard: AM Visits and Shift Management Report
-- Category: Samosa Party
-- Extracted: 2026-01-29 16:52:30
-- ============================================================

WITH td AS (
    SELECT 
        COALESCE(o.tzoffset, 0) as tzoffset,
        interval '1 min' * COALESCE(o.tzoffset, 0) AS diff
    FROM organizations o
    WHERE o.id IN (
        SELECT organization FROM nuggets 
        WHERE title ILIKE 'Shift Management Evaluation Form%' 
        LIMIT 1
    )
),
form_ids AS (
    SELECT id AS nugget_id
    FROM nuggets
    WHERE title ILIKE 'Shift Management Evaluation Form%'
),
allowed_locations AS (
    SELECT unnest(ARRAY[
        'Airport Road',
        'Alpha 2 Greater Noida',
        'Ameerpet',
        'Ananth Nagar',
        'Aparna Mall',
        'AS Rao Nagar',
        'Bagmane',
        'Bagmane (CV Raman Nagar)',
        'Banashankari',
        'Bannerghatta',
        'Begur',
        'Bellandur',
        'BLR - CK - Manyta Tech Park',
        'BLR - CK - Panathur',
        'BLR - DN - Airport T-1',
        'BLR - DN - Ayyappa Nagar',
        'BLR - DN - Bagalur',
        'BLR - DN - Budigere',
        'BLR - DN - Channapatna',
        'BLR - DN - Ecoworld',
        'BLR - DN - Galleria Mall',
        'BLR - DN - Haralur',
        'BLR - DN - Kaggadasapura',
        'BLR - DN - Kengeri',
        'BLR - DN - Park Square Mall (ITPL)',
        'CBD',
        'Chandapura',
        'Channasandra',
        'Crossing Republic',
        'Dasarahalli',
        'Defence Colony',
        'Dilshad Garden',
        'Dilshukh Nagar',
        'Dommasandra',
        'Dwarka',
        'East Patel Nagar',
        'Eco Space',
        'EGL',
        'Electronic City',
        'Faridabad SEC16',
        'Gaur City- Noida Extension',
        'Hennur',
        'HSR Layout',
        'HSR Layout Sector 3',
        'Hyd - CK - Padmarao Nagar',
        'HYD - DN - Sun City',
        'Indiranagar 12B',
        'Indirapuram',
        'Jeevan Bhima Nagar',
        'JP Nagar',
        'Kalyan Nagar',
        'Kanakapura Dine-In',
        'Kanakpura Road',
        'Kondapur',
        'Koramangala',
        'Kukatpally',
        'Laxmi Nagar',
        'Madhapur',
        'Mahadevpura',
        'Malviya Nagar',
        'Manikonda',
        'Marathalli',
        'Mehdipatnam',
        'Murgeshpalya',
        'Nagarbhavi',
        'NCR - DN - Advant Tech Park',
        'NCR - DN - Sector 120 Central Market',
        'NCR - DN - Star Tower',
        'NCR - DN- Janakpuri',
        'NCR - DN- Shalimar Bag',
        'New BEL Rd',
        'Nexus Koramangala',
        'Nexus Shantiniketan',
        'Old Madras Road',
        'Pragathi Nagar',
        'Raj Nagar',
        'Rajaji Nagar',
        'Rohini',
        'Royasandra',
        'RR Nagar',
        'RT Nagar',
        'Sahakar Nagar',
        'Sarita Vihar',
        'Sarjapur',
        'Sector 4 Gurgaon',
        'Sector 56',
        'Sector 90',
        'Sector- 4 Noida',
        'Singasandra',
        'Sohna Road',
        'Sushant Lok',
        'TC Palya',
        'TechnoStar (AECS)',
        'Udyog Vihar, Phase V',
        'Uttam Nagar',
        'Varthur',
        'Vasant Kunj',
        'Whitefield',
        'NCR - CK - Palam Vihar',
        'NCR - CK - Sector 65',
        'TN - CK - Karapakkam',
        'BLR - DN - Neo Town',
        'NCR - DN - Pacific Mall(Dwarka 21)'
    ]) AS location_name
),
qd_main AS (
    SELECT 
        question_id AS qid,
        question_type,
        question AS question_text,
        sqno::integer AS sort_order
    FROM question_definitions
    WHERE nugget_id IN (SELECT nugget_id FROM form_ids)
    AND question_type NOT IN ('table', 'section')
),
qd_logic_raw AS (
    SELECT 
        sqno,
        jsonb_array_elements(definition -> 'logic') -> 'questions' as q
    FROM question_definitions
    WHERE nugget_id IN (SELECT nugget_id FROM form_ids)
    AND definition -> 'logic' IS NOT NULL
),
qd_logic AS (
    SELECT 
        def.key AS qid,
        def.value->>'question_type' AS question_type,
        NULL AS question_text,
        sqno::integer * 10000 + (def.value->>'order')::integer AS sort_order
    FROM qd_logic_raw
    CROSS JOIN jsonb_each(q) def
),
all_questions AS (
    SELECT * FROM qd_main
    UNION
    SELECT * FROM qd_logic
),
submissions AS (
    SELECT DISTINCT ON (fs.location)
        fs.id AS submission_id,
        fs.response_id,
        fs.sno,
        fs.submit_date + td.diff AS submit_date,
        fs.user_id,
        fs.location,
        fs.organization
    FROM form_submissions fs
    CROSS JOIN td
    WHERE fs.form_id IN (SELECT nugget_id FROM form_ids)
    AND fs.location IN (SELECT location_name FROM allowed_locations)
    ORDER BY fs.location, fs.submit_date DESC, fs.id DESC
),
responses_parsed AS (
    SELECT 
        fr.form_submit_id AS submission_id,
        fr.question_id AS qid,
        qd.question AS question_text,
        CASE
            WHEN fr.question_type IN ('dropdown', 'multiple_choice', 'linear_scale', 'audit') 
                THEN fr.response -> 'selected' ->> 0
            WHEN fr.question_type IN ('checkboxes') 
                THEN array_to_string(ARRAY(
                    SELECT jsonb_array_elements_text(fr.response->'selected')
                    UNION 
                    SELECT CASE WHEN fr.response->>'otherText' IS NOT NULL 
                        THEN fr.response->>'otherText' END
                ), ', ')
            WHEN fr.question_type IN ('date', 'datetime') 
                THEN to_char(to_timestamp((fr.response::text::bigint)/1000), 'YYYY-MM-DD HH24:MI:SS')
            WHEN fr.question_type IN ('long_text_field', 'single_text_field', 'qr_code', 'formula') 
                THEN fr.response ->> 0
            WHEN fr.question_type IN ('upload_file', 'upload_image', 'upload_video', 'upload_mixed') 
                THEN COALESCE((fr.response)->0->>'response', fr.response::text)
            WHEN fr.question_type IN ('location', 'signature', 'division', 'sub_division') 
                THEN fr.response ->> 'name'
            WHEN fr.question_type = 'user'
                THEN fr.response::text
            ELSE fr.response::text
        END AS response_value
    FROM form_responses fr
    JOIN form_submissions fs ON fr.form_submit_id = fs.id
    LEFT JOIN question_definitions qd ON fr.question_id = qd.question_id AND fs.form_id = qd.nugget_id
    WHERE fr.form_submit_id IN (SELECT submission_id FROM submissions)
    AND fr.question_type NOT IN ('section', 'nested')
)
SELECT 
    s.response_id,
    s.sno AS submission_number,
    s.submit_date,
    s.location AS store_location,
    s.organization,
    ud.identifier AS employee_id,
    CONCAT(ud.first_name, ' ', ud.last_name) AS employee_name,
    ud.first_name,
    ud.last_name,
    ud.phone_number,
    ud.email,
    ud.department,
    ud.designation,
    ud.job_type,
    ud.job_location,
    ud.division,
    ud.sub_division,
    (CURRENT_DATE - s.submit_date::date)::INTEGER AS days_since_submission,
    TO_CHAR(s.submit_date, 'YYYY-MM') AS submission_month,
    TO_CHAR(s.submit_date, 'YYYY-Week-WW') AS submission_week,
    EXTRACT(YEAR FROM s.submit_date) AS submission_year,
    EXTRACT(QUARTER FROM s.submit_date) AS submission_quarter,

    MAX(CASE WHEN pr.question_text ILIKE 'Sale planning activity happening%lookwalker%' THEN pr.response_value END) AS sale_planning_activity_happening_lookwalker_npi_bulk_order_c,
    MAX(CASE WHEN pr.question_text ILIKE 'Team is aware about their MTD/last weekly variance%' THEN pr.response_value END) AS team_is_aware_about_their_mtdlast_weekly_variance_and_top_5_,
    MAX(CASE WHEN pr.question_text ILIKE 'In case of dinein store, check the safe cash sheet%' THEN pr.response_value END) AS in_case_of_dinein_store_check_the_safe_cash_sheet_should_not,
    MAX(CASE WHEN pr.question_text ILIKE 'Store has the required broom, mop, queeze%' THEN pr.response_value END) AS store_has_the_required_broom_mop_queeze_caddy_and_cleaning_s,
    MAX(CASE WHEN pr.question_text ILIKE 'Please comment about the positive things observed%' THEN pr.response_value END) AS please_comment_about_the_positive_things_observed_during_the,
    MAX(CASE WHEN pr.question_text ILIKE 'Everyone has GreytHR/ZingHR login access%' THEN pr.response_value END) AS everyone_has_greythrzinghr_login_access,
    MAX(CASE WHEN pr.question_text ILIKE 'Audit Info%' THEN pr.response_value END) AS audit_info,
    MAX(CASE WHEN pr.question_text ILIKE 'Area Manager Shift Evaluation Form%' THEN pr.response_value END) AS area_manager_shift_evaluation_form,
    MAX(CASE WHEN pr.question_text ILIKE 'Dinein%Any co-webs are seen%' THEN pr.response_value END) AS dinein_any_cowebs_are_seen_in_the_customer_area_inside_and_o,
    MAX(CASE WHEN pr.question_text ILIKE 'Is the team aware about their ratings on Swiggy%' THEN pr.response_value END) AS is_the_team_aware_about_their_ratings_on_swiggy_zomato_and_g,
    MAX(CASE WHEN pr.question_text ILIKE 'Oil quality is OK/usable in all the fryers%' THEN pr.response_value END) AS oil_quality_is_okusable_in_all_the_fryers_and_all_fryers_are,
    MAX(CASE WHEN pr.question_text ILIKE 'Audited Location%' THEN pr.response_value END) AS audited_location,
    MAX(CASE WHEN pr.question_text ILIKE 'Please mention in hand quantity of oil%' THEN pr.response_value END) AS please_mention_in_hand_quantity_of_oil_both_fresh_and_used,
    MAX(CASE WHEN pr.question_text = 'Cleanliness' THEN pr.response_value END) AS cleanliness,
    MAX(CASE WHEN pr.question_text ILIKE 'Team is aware about their monthly target%' THEN pr.response_value END) AS team_is_aware_about_their_monthly_target_and_the_current_run,
    MAX(CASE WHEN pr.question_text ILIKE 'Please comment about the opportunity areas%' THEN pr.response_value END) AS please_comment_about_the_opportunity_areas_and_action_items,
    MAX(CASE WHEN pr.question_text ILIKE 'Any pest sighting or pest infestation%' THEN pr.response_value END) AS any_pest_sighting_or_pest_infestation_observed,
    MAX(CASE WHEN pr.question_text ILIKE 'Store has all the small tools%Peg Measure%' THEN pr.response_value END) AS store_has_all_the_small_tools_peg_measure_balloon_blower_ric,
    MAX(CASE WHEN pr.question_text ILIKE 'Standard hiring poster with QR code%' THEN pr.response_value END) AS standard_hiring_poster_with_qr_code_is_being_put_up,
    MAX(CASE WHEN pr.question_text ILIKE 'Everyone has KNOW app login access%' THEN pr.response_value END) AS everyone_has_know_app_login_access,
    MAX(CASE WHEN pr.question_text ILIKE 'Everyone has courses completed in KNOW%' THEN pr.response_value END) AS everyone_has_courses_completed_in_know_and_not_having_more_t,
    MAX(CASE WHEN pr.question_text = 'Equipment' THEN pr.response_value END) AS equipment,
    MAX(CASE WHEN pr.question_text ILIKE 'EDC machine is working properly%' THEN pr.response_value END) AS edc_machine_is_working_properly,
    MAX(CASE WHEN pr.question_text ILIKE 'Dinein%Main outside signage is clean%' THEN pr.response_value END) AS dinein_main_outside_signage_is_clean,
    MAX(CASE WHEN pr.question_text ILIKE 'Oil change was done at the right frequency%' THEN pr.response_value END) AS oil_change_was_done_at_the_right_frequency_weekly_and_biweek,
    MAX(CASE WHEN pr.question_text ILIKE 'LSM marketing collaterals condition%' THEN pr.response_value END) AS lsm_marketing_collaterals_condition_is_good_to_use,
    MAX(CASE WHEN pr.question_text ILIKE 'Pictures of opportunity areas%' THEN pr.response_value END) AS pictures_of_opportunity_areas_and_action_items,
    MAX(CASE WHEN pr.question_text = 'HR' THEN pr.response_value END) AS hr,
    MAX(CASE WHEN pr.question_text ILIKE 'All not working equipment or any other IT/Infra%' THEN pr.response_value END) AS all_not_working_equipment_or_any_other_itinfra_pending_work_,
    MAX(CASE WHEN pr.question_text ILIKE 'Washroom is clean for staff/customers%' THEN pr.response_value END) AS washroom_is_clean_for_staffcustomers_and_has_the_required_su,
    MAX(CASE WHEN pr.question_text ILIKE 'All employees are in 100% uniform%' THEN pr.response_value END) AS all_employees_are_in_100_uniform_with_shoes_cap_and_name_bad,
    MAX(CASE WHEN pr.question_text ILIKE 'Dinein%DMB working and updated%' THEN pr.response_value END) AS dinein_dmb_working_and_updated_with_all_new_products_and_all,
    MAX(CASE WHEN pr.question_text ILIKE 'Catch someone doing something right%' THEN pr.response_value END) AS catch_someone_doing_something_right_and_appreciate_if_feasib,
    MAX(CASE WHEN pr.question_text = 'Training' THEN pr.response_value END) AS training,
    MAX(CASE WHEN pr.question_text ILIKE 'Samosa Party App QR code available%' THEN pr.response_value END) AS samosa_party_app_qr_code_available_and_crispy_points_are_bei,
    MAX(CASE WHEN pr.question_text ILIKE 'Dinein%All tables, chairs and floors are clean%' THEN pr.response_value END) AS dinein_all_tables_chairs_and_floors_are_clean,
    MAX(CASE WHEN pr.question_text ILIKE 'For Dinein stores, the steel table number%' THEN pr.response_value END) AS for_dinein_stores_the_steel_table_number_is_used_for_all_ord,
    MAX(CASE WHEN pr.question_text = 'Inventory' THEN pr.response_value END) AS inventory,
    MAX(CASE WHEN pr.question_text ILIKE 'Daily briefing call is happening%' THEN pr.response_value END) AS daily_briefing_call_is_happening_with_their_respective_ams_a,
    MAX(CASE WHEN pr.question_text ILIKE 'Adequate change available in the till%' THEN pr.response_value END) AS adequate_change_available_in_the_till_for_customers,
    MAX(CASE WHEN pr.question_text ILIKE 'FIFO is followed for all items%' THEN pr.response_value END) AS fifo_is_followed_for_all_items,
    MAX(CASE WHEN pr.question_text ILIKE 'Dinein%All customers are greeted%' THEN pr.response_value END) AS dinein_all_customers_are_greeted_at_the_counter,
    MAX(CASE WHEN pr.question_text = 'Process' THEN pr.response_value END) AS process,
    MAX(CASE WHEN pr.question_text ILIKE 'General cleanliness level is OK%' THEN pr.response_value END) AS general_cleanliness_level_is_ok_for_the_store,
    MAX(CASE WHEN pr.question_text ILIKE 'No expired item is found%' THEN pr.response_value END) AS no_expired_item_is_found_inside_the_store,
    MAX(CASE WHEN pr.question_text ILIKE 'Store is using the Suma Bac solution%' THEN pr.response_value END) AS store_is_using_the_suma_bac_solution_10ml_in_1_lit_for_table,
    MAX(CASE WHEN pr.question_text ILIKE 'Dinein%Suggestive selling and upselling%' THEN pr.response_value END) AS dinein_suggestive_selling_and_upselling_is_happening,
    MAX(CASE WHEN pr.question_text = 'Sales' THEN pr.response_value END) AS sales,
    MAX(CASE WHEN pr.question_text ILIKE 'Team is having all hierarchy number%' THEN pr.response_value END) AS team_is_having_all_hierarchy_number_for_issues_escalation_hr,
    MAX(CASE WHEN pr.question_text ILIKE 'Overall Comments%' THEN pr.response_value END) AS overall_comments,
    MAX(CASE WHEN pr.question_text ILIKE 'Sufficient PRP is done%' THEN pr.response_value END) AS sufficient_prp_is_done_and_service_is_moving_smoothly
FROM submissions s
LEFT JOIN responses_parsed pr ON pr.submission_id = s.submission_id
LEFT JOIN user_details ud ON s.user_id = ud.uuid
GROUP BY 
    s.response_id, s.sno, s.submit_date, s.location, s.organization,
    ud.identifier, ud.first_name, ud.last_name, ud.phone_number, ud.email,
    ud.department, ud.designation, ud.job_type, ud.job_location, ud.division, ud.sub_division
ORDER BY s.submit_date DESC
```

---

## Shifts Management Report Deviation_AM Visits and Shift Management Report.sql

**Tables referenced:** all_questions, allowed_locations, deviation_summary, form_ids, form_responses, form_submissions, last, nuggets, organizations, qd_logic, qd_logic_base, qd_logic_expanded, qd_main, question_definitions, question_options, recent_submissions, responses_parsed, responses_with_scores, td

**Original Query:**

```sql
-- Data Source: Shifts Management Report Deviation
-- Dashboard: AM Visits and Shift Management Report
-- Category: Samosa Party
-- Extracted: 2026-01-29 16:52:29
-- ============================================================

WITH td AS (
    SELECT 
        COALESCE(o.tzoffset, 0) as tzoffset,
        interval '1 min' * COALESCE(o.tzoffset, 0) AS diff
    FROM organizations o
    WHERE o.id IN (
        SELECT organization FROM nuggets 
        WHERE title ILIKE 'Shift Management Evaluation Form%' 
        LIMIT 1
    )
),
form_ids AS (
    SELECT id AS nugget_id
    FROM nuggets
    WHERE title ILIKE 'Shift Management Evaluation Form%'
),
allowed_locations AS (
    SELECT unnest(ARRAY[
        'Airport Road',
        'Alpha 2 Greater Noida',
        'Ameerpet',
        'Ananth Nagar',
        'Aparna Mall',
        'AS Rao Nagar',
        'Bagmane',
        'Bagmane (CV Raman Nagar)',
        'Banashankari',
        'Bannerghatta',
        'Begur',
        'Bellandur',
        'BLR - CK - Manyta Tech Park',
        'BLR - CK - Panathur',
        'BLR - DN - Airport T-1',
        'BLR - DN - Ayyappa Nagar',
        'BLR - DN - Bagalur',
        'BLR - DN - Budigere',
        'BLR - DN - Channapatna',
        'BLR - DN - Ecoworld',
        'BLR - DN - Galleria Mall',
        'BLR - DN - Haralur',
        'BLR - DN - Kaggadasapura',
        'BLR - DN - Kengeri',
        'BLR - DN - Park Square Mall (ITPL)',
        'CBD',
        'Chandapura',
        'Channasandra',
        'Crossing Republic',
        'Dasarahalli',
        'Defence Colony',
        'Dilshad Garden',
        'Dilshukh Nagar',
        'Dommasandra',
        'Dwarka',
        'East Patel Nagar',
        'Eco Space',
        'EGL',
        'Electronic City',
        'Faridabad SEC16',
        'Gaur City- Noida Extension',
        'Hennur',
        'HSR Layout',
        'HSR Layout Sector 3',
        'Hyd - CK - Padmarao Nagar',
        'HYD - DN - Sun City',
        'Indiranagar 12B',
        'Indirapuram',
        'Jeevan Bhima Nagar',
        'JP Nagar',
        'Kalyan Nagar',
        'Kanakapura Dine-In',
        'Kanakpura Road',
        'Kondapur',
        'Koramangala',
        'Kukatpally',
        'Laxmi Nagar',
        'Madhapur',
        'Mahadevpura',
        'Malviya Nagar',
        'Manikonda',
        'Marathalli',
        'Mehdipatnam',
        'Murgeshpalya',
        'Nagarbhavi',
        'NCR - DN - Advant Tech Park',
        'NCR - DN - Sector 120 Central Market',
        'NCR - DN - Star Tower',
        'NCR - DN- Janakpuri',
        'NCR - DN- Shalimar Bag',
        'New BEL Rd',
        'Nexus Koramangala',
        'Nexus Shantiniketan',
        'Old Madras Road',
        'Pragathi Nagar',
        'Raj Nagar',
        'Rajaji Nagar',
        'Rohini',
        'Royasandra',
        'RR Nagar',
        'RT Nagar',
        'Sahakar Nagar',
        'Sarita Vihar',
        'Sarjapur',
        'Sector 4 Gurgaon',
        'Sector 56',
        'Sector 90',
        'Sector- 4 Noida',
        'Singasandra',
        'Sohna Road',
        'Sushant Lok',
        'TC Palya',
        'TechnoStar (AECS)',
        'Udyog Vihar, Phase V',
        'Uttam Nagar',
        'Varthur',
        'Vasant Kunj',
        'Whitefield',
        'NCR - CK - Palam Vihar',
        'NCR - CK - Sector 65',
        'TN - CK - Karapakkam',
        'BLR - DN - Neo Town',
        'NCR - DN - Pacific Mall(Dwarka 21)'
    ]) AS location_name
),
-- Get main questions with options
qd_main AS (
    SELECT 
        question_id AS qid,
        question,
        question_type,
        definition
    FROM question_definitions
    WHERE nugget_id IN (SELECT nugget_id FROM form_ids)
    AND question_type IN ('audit', 'multiple_choice', 'dropdown')
    AND definition->'options' IS NOT NULL
),
-- Get logic questions
qd_logic_base AS (
    SELECT 
        nugget_id,
        definition
    FROM question_definitions
    WHERE nugget_id IN (SELECT nugget_id FROM form_ids)
    AND definition -> 'logic' IS NOT NULL
),
qd_logic_expanded AS (
    SELECT 
        logic_element
    FROM qd_logic_base,
    LATERAL jsonb_array_elements(definition -> 'logic') AS logic_element
),
qd_logic AS (
    SELECT 
        qe.key AS qid,
        qe.value->>'question' AS question,
        qe.value->>'question_type' AS question_type,
        qe.value AS definition
    FROM qd_logic_expanded qle,
    LATERAL jsonb_each(qle.logic_element -> 'questions') AS qe
    WHERE qe.value->>'question_type' IN ('audit', 'multiple_choice', 'dropdown')
    AND qe.value->'options' IS NOT NULL
),
-- Combine all questions
all_questions AS (
    SELECT * FROM qd_main
    UNION
    SELECT * FROM qd_logic
),
-- Extract options with SCORE values
question_options AS (
    SELECT 
        aq.qid,
        aq.question,
        opt.value->>'value' AS option_value,
        COALESCE((opt.value->>'score')::numeric, 0) AS score
    FROM all_questions aq,
    LATERAL jsonb_array_elements(aq.definition->'options') AS opt
),
-- Get submissions from last 60 days
recent_submissions AS (
    SELECT DISTINCT ON (fs.response_id)
        fs.id AS submission_id,
        fs.response_id,
        fs.submit_date + td.diff AS submit_date,
        fs.location
    FROM form_submissions fs
    CROSS JOIN td
    WHERE fs.form_id IN (SELECT nugget_id FROM form_ids)
    AND fs.submit_date >= CURRENT_DATE - INTERVAL '60 days'
    AND fs.location IN (SELECT location_name FROM allowed_locations)
    ORDER BY fs.response_id, fs.id DESC
),
-- Get responses
responses_parsed AS (
    SELECT 
        rs.response_id,
        rs.location,
        fr.question_id AS qid,
        fr.response -> 'selected' ->> 0 AS response_value
    FROM recent_submissions rs
    JOIN form_responses fr ON fr.form_submit_id = rs.submission_id
    WHERE fr.question_id IN (SELECT qid FROM all_questions)
    AND fr.response -> 'selected' ->> 0 IS NOT NULL
),
-- Match responses with their scores
responses_with_scores AS (
    SELECT 
        rp.response_id,
        rp.location,
        rp.qid,
        qo.question,
        rp.response_value,
        COALESCE(qo.score, 0) AS score_earned,
        CASE 
            WHEN COALESCE(qo.score, 0) = 0 THEN 1
            ELSE 0
        END AS is_deviation
    FROM responses_parsed rp
    INNER JOIN question_options qo 
        ON qo.qid = rp.qid 
        AND qo.option_value = rp.response_value
),
-- Calculate deviation summary
deviation_summary AS (
    SELECT 
        question AS checkpoint,
        COUNT(DISTINCT location) AS total_stores_checked,
        SUM(is_deviation) AS total_deviations,
        COUNT(DISTINCT CASE WHEN is_deviation = 1 THEN location END) AS stores_with_deviation,
        ROUND(
            (COUNT(DISTINCT CASE WHEN is_deviation = 1 THEN location END)::NUMERIC / 
             NULLIF(COUNT(DISTINCT location), 0)) * 100, 
            1
        ) AS deviation_percentage,
        STRING_AGG(DISTINCT 
            CASE WHEN is_deviation = 1 THEN response_value END, 
            ', '
        ) AS deviation_answers
    FROM responses_with_scores
    GROUP BY question
    HAVING COUNT(DISTINCT location) >= 3
)
-- Final output
SELECT 
    ROW_NUMBER() OVER (ORDER BY deviation_percentage DESC, total_deviations DESC) AS rank,
    checkpoint,
    deviation_percentage,
    stores_with_deviation AS stores_missed,
    total_stores_checked,
    total_deviations AS points_lost,
    deviation_answers AS wrong_answer
FROM deviation_summary
WHERE deviation_percentage > 0
ORDER BY deviation_percentage DESC, total_deviations DESC
```

---

## samosapartyattendancereport_Attendance Report - Samosa Party.sql

**Tables referenced:** base, day_wise, sa, shift_attendance, user_details

**Original Query:**

```sql
-- Data Source: samosapartyattendancereport
-- Dashboard: Attendance Report - Samosa Party
-- Category: Samosa Party
-- Extracted: 2026-01-29 16:56:32
-- ============================================================

WITH base AS (
  SELECT 
    sa."Shift ID",
    sa."UUID",
    sa."Employee Name",
    sa."Employee ID",
  sa."Home Location",
    sa."Designation",
    sa."Department",
    sa."Division",
    sa."Sub Division",
    sa."Status",
    sa."Scheduled Start Time",
    sa."Scheduled End Time",
    sa."Scheduled Break Hours",

    CASE 
      WHEN sa."Status" != 'On Leave' THEN 
        (extract(epoch FROM sa."Scheduled End Time") - extract(epoch FROM sa."Scheduled Start Time")) / 3600
      ELSE 0
    END AS "Scheduled Hours incl Break",

    CASE 
      WHEN sa."Status" != 'On Leave' THEN 
        (extract(epoch FROM sa."Scheduled End Time") - extract(epoch FROM sa."Scheduled Start Time")) / 3600 - sa."Scheduled Break Hours"
      ELSE 0
    END AS "Scheduled Hours excl Break",

    sa."Actual Clockin Time",
    sa."Actual Clockout Time",
    sa."Actual Break Hours",
    sa."Actual Work Duration",

    CASE
      WHEN sa."Actual Clockin Time" IS NOT NULL 
           AND sa."Actual Clockin Time" > sa."Scheduled Start Time" + INTERVAL '15 minutes' THEN 
        (extract(epoch FROM sa."Actual Clockin Time") - extract(epoch FROM sa."Scheduled Start Time" + INTERVAL '15 minutes')) / 60
      ELSE 0
    END AS "Late Mins",

    CASE
      WHEN sa."Actual Clockin Time" IS NOT NULL 
           AND sa."Actual Clockin Time" > sa."Scheduled Start Time" + INTERVAL '15 minutes' THEN 
        CEIL((extract(epoch FROM sa."Actual Clockin Time") - extract(epoch FROM sa."Scheduled Start Time" + INTERVAL '15 minutes')) / 3600)
      ELSE 0
    END AS "Late Hours",

    CASE
      WHEN sa."Actual Clockout Time" IS NOT NULL 
           AND sa."Actual Clockout Time" < sa."Scheduled End Time" - INTERVAL '15 minutes' THEN 
        CEIL((extract(epoch FROM sa."Scheduled End Time" - INTERVAL '15 minutes') - extract(epoch FROM sa."Actual Clockout Time")) / 3600)
      ELSE 0
    END AS "Early Clockout Hours"

  FROM shift_attendance sa
  WHERE sa.organization = 'sampar-cartwheel'
    AND sa."Scheduled Start Time" BETWEEN @{{:Date Range.START}}::TIMESTAMP 
                                      AND @{{:Date Range.END}}::TIMESTAMP + INTERVAL '1 day'
),
day_wise AS (
  SELECT 
    b."UUID",
    b."Employee Name",
    b."Employee ID",
    b."Designation",
    b."Department",
    b."Division",
  b."Home Location",
    b."Sub Division",
    TO_CHAR(b."Scheduled Start Time", 'YYYY-MM') AS "Month",
    TO_CHAR(b."Scheduled Start Time", 'DD') AS "Day",

    SUM(b."Scheduled Hours excl Break") AS "Scheduled Hours",
    SUM(b."Actual Work Duration") AS "Actual Work Hours",

    SUM(CASE
      WHEN b."Actual Work Duration" > 0
        AND b."Actual Work Duration" > b."Scheduled Hours excl Break" + (1.0/6) -- 10 mins
        AND b."Actual Clockout Time" > b."Scheduled End Time" + INTERVAL '10 minutes' THEN 
        CEIL(b."Actual Work Duration" - b."Scheduled Hours excl Break" - (1.0/6))
      ELSE 0
    END) AS "Overtime Hours",

    SUM(CASE
      WHEN b."Actual Work Duration" > 0
        AND b."Actual Work Duration" > b."Scheduled Hours excl Break" + (1.0/6)
        AND b."Actual Clockout Time" > b."Scheduled End Time" + INTERVAL '10 minutes' THEN 1
      ELSE 0
    END) AS "Overtime Count",

    SUM(CASE
      WHEN b."Actual Work Duration" > 0
        AND b."Actual Work Duration" < b."Scheduled Hours excl Break" - (1.0/6) THEN 
        CEIL(b."Scheduled Hours excl Break" - b."Actual Work Duration" - (1.0/6))
      ELSE 0
    END) AS "Undertime Hours",

    SUM(CASE
      WHEN b."Actual Work Duration" > 0
        AND b."Actual Work Duration" < b."Scheduled Hours excl Break" - (1.0/6) THEN 1
      ELSE 0
    END) AS "Undertime Count",

    COUNT(DISTINCT CASE 
      WHEN b."Status" != 'On Leave' THEN TO_CHAR(b."Scheduled Start Time", 'DD')
    END) AS "Scheduled Count",

    COUNT(DISTINCT CASE 
      WHEN b."Status" = 'Absent' THEN TO_CHAR(b."Scheduled Start Time", 'DD')
    END) AS "Absent Count",SUM(
  CASE 
    WHEN b."Actual Work Duration" >= 4.5 
         AND b."Actual Work Duration" < 9 THEN 1
    ELSE 0
  END
) AS "Half Day Count",

    SUM(b."Late Hours" + b."Early Clockout Hours") AS "Late or Early CO Hours"
  FROM base b
  GROUP BY 1,2,3,4,5,6,7,8,9,10
)
SELECT 
  dw."Month",
  dw."UUID",
  dw."Employee Name",
  dw."Employee ID",
  dw."Designation",
  dw."Department",
  dw."Division",
  dw."Home Location",
  dw."Sub Division",

  SUM(dw."Scheduled Count") AS "Scheduled Days",
  SUM(dw."Absent Count") AS "Absent Days",
  SUM(dw."Scheduled Hours") AS "Total Scheduled Hours",
  SUM(dw."Actual Work Hours") AS "Total Hours Worked",
  SUM(dw."Overtime Hours") AS "Total OT Hours",
  SUM(dw."Undertime Hours") AS "Total UT Hours",
  SUM(dw."Late or Early CO Hours") AS "Total Late or Early CO Hours",
SUM(dw."Half Day Count") AS "Half Days",
  -- Pivoted daily hours
  SUM(CASE WHEN dw."Day" = '01' THEN dw."Actual Work Hours" ELSE 0 END) AS "01",
  SUM(CASE WHEN dw."Day" = '02' THEN dw."Actual Work Hours" ELSE 0 END) AS "02",
  SUM(CASE WHEN dw."Day" = '03' THEN dw."Actual Work Hours" ELSE 0 END) AS "03",
  SUM(CASE WHEN dw."Day" = '04' THEN dw."Actual Work Hours" ELSE 0 END) AS "04",
  SUM(CASE WHEN dw."Day" = '05' THEN dw."Actual Work Hours" ELSE 0 END) AS "05",
  SUM(CASE WHEN dw."Day" = '06' THEN dw."Actual Work Hours" ELSE 0 END) AS "06",
  SUM(CASE WHEN dw."Day" = '07' THEN dw."Actual Work Hours" ELSE 0 END) AS "07",
  SUM(CASE WHEN dw."Day" = '08' THEN dw."Actual Work Hours" ELSE 0 END) AS "08",
  SUM(CASE WHEN dw."Day" = '09' THEN dw."Actual Work Hours" ELSE 0 END) AS "09",
  SUM(CASE WHEN dw."Day" = '10' THEN dw."Actual Work Hours" ELSE 0 END) AS "10",
  SUM(CASE WHEN dw."Day" = '11' THEN dw."Actual Work Hours" ELSE 0 END) AS "11",
  SUM(CASE WHEN dw."Day" = '12' THEN dw."Actual Work Hours" ELSE 0 END) AS "12",
  SUM(CASE WHEN dw."Day" = '13' THEN dw."Actual Work Hours" ELSE 0 END) AS "13",
  SUM(CASE WHEN dw."Day" = '14' THEN dw."Actual Work Hours" ELSE 0 END) AS "14",
  SUM(CASE WHEN dw."Day" = '15' THEN dw."Actual Work Hours" ELSE 0 END) AS "15",
  SUM(CASE WHEN dw."Day" = '16' THEN dw."Actual Work Hours" ELSE 0 END) AS "16",
  SUM(CASE WHEN dw."Day" = '17' THEN dw."Actual Work Hours" ELSE 0 END) AS "17",
  SUM(CASE WHEN dw."Day" = '18' THEN dw."Actual Work Hours" ELSE 0 END) AS "18",
  SUM(CASE WHEN dw."Day" = '19' THEN dw."Actual Work Hours" ELSE 0 END) AS "19",
  SUM(CASE WHEN dw."Day" = '20' THEN dw."Actual Work Hours" ELSE 0 END) AS "20",
  SUM(CASE WHEN dw."Day" = '21' THEN dw."Actual Work Hours" ELSE 0 END) AS "21",
  SUM(CASE WHEN dw."Day" = '22' THEN dw."Actual Work Hours" ELSE 0 END) AS "22",
  SUM(CASE WHEN dw."Day" = '23' THEN dw."Actual Work Hours" ELSE 0 END) AS "23",
  SUM(CASE WHEN dw."Day" = '24' THEN dw."Actual Work Hours" ELSE 0 END) AS "24",
  SUM(CASE WHEN dw."Day" = '25' THEN dw."Actual Work Hours" ELSE 0 END) AS "25",
  SUM(CASE WHEN dw."Day" = '26' THEN dw."Actual Work Hours" ELSE 0 END) AS "26",
  SUM(CASE WHEN dw."Day" = '27' THEN dw."Actual Work Hours" ELSE 0 END) AS "27",
  SUM(CASE WHEN dw."Day" = '28' THEN dw."Actual Work Hours" ELSE 0 END) AS "28",
  SUM(CASE WHEN dw."Day" = '29' THEN dw."Actual Work Hours" ELSE 0 END) AS "29",
  SUM(CASE WHEN dw."Day" = '30' THEN dw."Actual Work Hours" ELSE 0 END) AS "30",
  SUM(CASE WHEN dw."Day" = '31' THEN dw."Actual Work Hours" ELSE 0 END) AS "31"

FROM day_wise dw
LEFT JOIN user_details ud ON dw."UUID" = ud.uuid
GROUP BY 1,2,3,4,5,6,7,8,9
ORDER BY 1,2,3,4
```

---
