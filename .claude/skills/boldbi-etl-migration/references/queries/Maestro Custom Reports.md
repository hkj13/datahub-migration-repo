# Maestro Custom Reports

> Auto-generated on 2026-03-04 08:13

**Total queries:** 3

---

## PRP Opening Checklist_PRP Opening Checklist.sql

**Tables referenced:** RAW, _fs, current_date, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: PRP Opening Checklist
-- Dashboard: PRP Opening Checklist
-- Category: Maestro Custom Reports
-- Extracted: 2026-01-29 16:52:32
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'maestropizza-ksa-cartwheel'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ILIKE ('PRP Opening Checklist%')
     AND organization = 'maestropizza-ksa-cartwheel'
     AND is_deleted = FALSE
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
   WHERE submit_date >= current_date
                     - extract(dow from current_date)::int
                     - 7
   ORDER BY response_id,
            id DESC),
     fs AS
  (SELECT *
   FROM _fs
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
          LOCATION
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
                LOCATION
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
             LOCATION
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id
      JOIN td ON fs.organization = td.organization,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res), /*location_questions as (
select distinct on (nugget_id) nugget_id, question_id from question_definitions qd
where nugget_id in (select form_knid from forms)
and question_type = 'location'
order by nugget_id, section_id, sqno
),
location_response as (
select form_submit_id, (response ->> 'name')::text location_name from form_responses fr
where question_id in (select question_id from location_questions)
and form_submit_id in (select id from fs)
),*/ RAW AS
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
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          fr.user_id,
          ud.first_name AS "UserName"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN user_details ud ON fr.user_id = ud.uuid
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
            15,
            16,
            17
   ORDER BY 1,
            2,
            3) 
SELECT sno AS "Sno",
       submit_date AS "Submit Date",
       "UserName" AS "Form Submitted By",
       MAX(CASE WHEN parent_question = 'Store Location' THEN response END) AS "Store Location",
MAX(CASE WHEN parent_question = 'What is the Current Temperature?' and q_type = 'single_text_field' THEN response END) AS "What is the Current Temperature?",
MAX(CASE WHEN parent_question = 'What is the Current Temperature?' and q_type = 'upload_file' THEN response END) AS "What is the Current Temperature? Image",
MAX(CASE WHEN parent_question = 'Are all tools (Scissors, Knife, Spoon, Sealing Clips, SS dispenser for Double Cheddar) placed in the SS container?' and q_type = 'multiple_choice' THEN response END) AS "Are all tools (Scissors, Knife, Spoon, Sealing Clips, SS dispenser for Double Cheddar) placed in the SS container?",
MAX(CASE WHEN parent_question = 'Are all tools (Scissors, Knife, Spoon, Sealing Clips, SS dispenser for Double Cheddar) placed in the SS container?' and q_type = 'upload_file' THEN response END) AS "Are all tools (Scissors, Knife, Spoon, Sealing Clips, SS dispenser for Double Cheddar) placed in the SS container? Image",
MAX(CASE WHEN parent_question = 'Sanitizer solution available in labeled spray bottles at make table, cut table, and customer area?' and q_type = 'multiple_choice' THEN response END) AS "Sanitizer solution available in labeled spray bottles at make table, cut table, and customer area?",
MAX(CASE WHEN parent_question = 'Sanitizer solution available in labeled spray bottles at make table, cut table, and customer area?' and q_type = 'upload_file' THEN response END) AS "Sanitizer solution available in labeled spray bottles at make table, cut table, and customer area? Image",
MAX(CASE WHEN parent_question = 'Do we have MAD Pizza and Pinzatta (sandwich) items thawed and ready?' and q_type = 'multiple_choice' THEN response END) AS "Do we have MAD Pizza and Pinzatta (sandwich) items thawed and ready?",
MAX(CASE WHEN parent_question = 'Do we have MAD Pizza and Pinzatta (sandwich) items thawed and ready?' and q_type = 'upload_file' THEN response END) AS "Do we have MAD Pizza and Pinzatta (sandwich) items thawed and ready? Image",
MAX(CASE WHEN parent_question = 'Are all closed-bag Sauces, Vegetable toppings, Meat items, and Appetizers available under the cabinet?' and q_type = 'multiple_choice' THEN response END) AS "Are all closed-bag Sauces, Vegetable toppings, Meat items, and Appetizers available under the cabinet?",
MAX(CASE WHEN parent_question = 'Are all closed-bag Sauces, Vegetable toppings, Meat items, and Appetizers available under the cabinet?' and q_type = 'upload_file' THEN response END) AS "Are all closed-bag Sauces, Vegetable toppings, Meat items, and Appetizers available under the cabinet? Image",
MAX(CASE WHEN parent_question = 'Are the Scoopers available for each topping (¼ scoops for Tomato, Chicken, Buffalo, Seasoned Chicken, Peri Peri Chicken and ½ scoop for Mozzarella)?' and q_type = 'multiple_choice' THEN response END) AS "Are the Scoopers available for each topping (¼ scoops for Tomato, Chicken, Buffalo, Seasoned Chicken, Peri Peri Chicken and ½ scoop for Mozzarella)?",
MAX(CASE WHEN parent_question = 'Are the Scoopers available for each topping (¼ scoops for Tomato, Chicken, Buffalo, Seasoned Chicken, Peri Peri Chicken and ½ scoop for Mozzarella)?'  and q_type = 'upload_file' THEN response END) AS "Are the Scoopers available for each topping (¼ scoops for Tomato, Chicken, Buffalo, Seasoned Chicken, Peri Peri Chicken and ½ scoop for Mozzarella)? Image",

MAX(CASE WHEN parent_question = 'Is the PRP for Potato Wedges completed?' and q_type = 'multiple_choice' THEN response END) AS "Is the PRP for Potato Wedges completed?",
MAX(CASE WHEN parent_question = 'Is the PRP for Potato Wedges completed?' and q_type = 'upload_file' THEN response END) AS "Is the PRP for Potato Wedges completed? Image",

MAX(CASE WHEN parent_question = 'Are these 4 items stored in an airtight container? Pinzatta tomato sauce, Alfredo sauce, Chipotle Chicken Mix (250g Chicken topping + 75g chipotle sauce), and Pesto Chicken Mix (250g Chicken topping + 100g pesto sauce for Pinzatta sandwiches)' and q_type = 'multiple_choice' THEN response END) AS "Are these 4 items stored in an airtight container? Pinzatta tomato sauce, Alfredo sauce, Chipotle Chicken Mix (250g Chicken topping + 75g chipotle sauce), and Pesto Chicken Mix (250g Chicken topping + 100g pesto sauce for Pinzatta sandwiches)",
MAX(CASE WHEN parent_question = 'Are these 4 items stored in an airtight container? Pinzatta tomato sauce, Alfredo sauce, Chipotle Chicken Mix (250g Chicken topping + 75g chipotle sauce), and Pesto Chicken Mix (250g Chicken topping + 100g pesto sauce for Pinzatta sandwiches)'  and q_type = 'upload_file' THEN response END) AS "Are these 4 items stored in an airtight container? Pinzatta tomato sauce, Alfredo sauce, Chipotle Chicken Mix (250g Chicken topping + 75g chipotle sauce), and Pesto Chicken Mix (250g Chicken topping + 100g pesto sauce for Pinzatta sandwiches) Image",

MAX(CASE WHEN parent_question = 'Do we have Pinzatta screens / Small & Medium pans ready to prepare Appetizers?' and q_type = 'multiple_choice' THEN response END) AS "Do we have Pinzatta screens / Small & Medium pans ready to prepare Appetizers?",
MAX(CASE WHEN parent_question = 'Do we have Pinzatta screens / Small & Medium pans ready to prepare Appetizers?' and q_type = 'upload_file' THEN response END) AS "Do we have Pinzatta screens / Small & Medium pans ready to prepare Appetizers? Image",

MAX(CASE WHEN parent_question = 'Are Burrata Cheese, Mushroom, Jalapeno, Black Olives, and Cheddar Cheese available under the make table?' and q_type = 'multiple_choice' THEN response END) AS "Are Burrata Cheese, Mushroom, Jalapeno, Black Olives, and Cheddar Cheese available under the make table?",
MAX(CASE WHEN parent_question = 'Are Burrata Cheese, Mushroom, Jalapeno, Black Olives, and Cheddar Cheese available under the make table?' and q_type = 'upload_file' THEN response END) AS "Are Burrata Cheese, Mushroom, Jalapeno, Black Olives, and Cheddar Cheese available under the make table? Image",

MAX(CASE WHEN parent_question = 'Do we have enough Sliced Kickers ready?' and q_type = 'multiple_choice' THEN response END) AS "Do we have enough Sliced Kickers ready?",
MAX(CASE WHEN parent_question = 'Do we have enough Sliced Kickers ready?' and q_type = 'upload_file' THEN response END) AS "Do we have enough Sliced Kickers ready? Image",

MAX(CASE WHEN parent_question = 'Is Garlic Bread Butter available on the shelf above the making table?' and q_type = 'multiple_choice' THEN response END) AS "Is Garlic Bread Butter available on the shelf above the making table?",
MAX(CASE WHEN parent_question = 'Is Garlic Bread Butter available on the shelf above the making table?' and q_type = 'upload_file' THEN response END) AS "Is Garlic Bread Butter available on the shelf above the making table? Image",

MAX(CASE WHEN parent_question = 'Are all items in stock, or is anything out of stock?' and q_type = 'multiple_choice' THEN response END) AS "Are all items in stock, or is anything out of stock?",
MAX(CASE WHEN parent_question = 'Are all items in stock, or is anything out of stock?' and q_type = 'upload_file' THEN response END) AS "Are all items in stock, or is anything out of stock? Image",

MAX(CASE WHEN parent_question = 'Note down the temperature of the Standing Chiller' and q_type = 'single_text_field' THEN response END) AS "Note down the temperature of the Standing Chiller",
MAX(CASE WHEN parent_question = 'Note down the temperature of the Standing Chiller' and q_type = 'upload_file' THEN response END) AS "Note down the temperature of the Standing Chiller Image",

MAX(CASE WHEN parent_question = 'Are Classic, Detroit, Pan, and Cheesy Crusts available in the Standing Chiller?' and q_type = 'multiple_choice' THEN response END) AS "Are Classic, Detroit, Pan, and Cheesy Crusts available in the Standing Chiller?",
MAX(CASE WHEN parent_question = 'Are Classic, Detroit, Pan, and Cheesy Crusts available in the Standing Chiller?' and q_type = 'upload_file' THEN response END) AS "Are Classic, Detroit, Pan, and Cheesy Crusts available in the Standing Chiller? Image",

MAX(CASE WHEN parent_question = 'Are the Dough Monitoring Sheet and Thawing Sheet updated?' and q_type = 'multiple_choice' THEN response END) AS "Are the Dough Monitoring Sheet and Thawing Sheet updated?",
MAX(CASE WHEN parent_question = 'Are the Dough Monitoring Sheet and Thawing Sheet updated?' and q_type = 'upload_file' THEN response END) AS "Are the Dough Monitoring Sheet and Thawing Sheet updated? Image",

MAX(CASE WHEN parent_question = 'No Wrong / duplicate labels on food items' and q_type = 'multiple_choice' THEN response END) AS "No Wrong / duplicate labels on food items",
MAX(CASE WHEN parent_question = 'No Wrong / duplicate labels on food items' and q_type = 'upload_file' THEN response END) AS "No Wrong / duplicate labels on food items Image",

MAX(CASE WHEN parent_question = 'Enter the current Walk-in Chiller temperature.' and q_type = 'single_text_field' THEN response END) AS "Enter the current Walk-in Chiller temperature.",
MAX(CASE WHEN parent_question = 'Enter the current Walk-in Chiller temperature.' and q_type = 'upload_file' THEN response END) AS "Enter the current Walk-in Chiller temperature. Image",
MAX(CASE WHEN parent_question = 'Enter the Walk-in Freezer temperature' and q_type = 'single_text_field' THEN response END) AS "Enter the Walk-in Freezer temperature",
MAX(CASE WHEN parent_question = 'Enter the Walk-in Freezer temperature' and q_type = 'upload_file' THEN response END) AS "Enter the Walk-in Freezer temperature Image",
MAX(CASE WHEN parent_question = 'Note the Mozzarella Cheese temperature' and q_type = 'single_text_field' THEN response END) AS "Note the Mozzarella Cheese temperature",
MAX(CASE WHEN parent_question = 'Note the Mozzarella Cheese temperature' and q_type = 'upload_file' THEN response END) AS "Note the Mozzarella Cheese temperature Image",
MAX(CASE WHEN parent_question = 'Enter the temperature of any Meat items (Chicken/Beef)' and q_type = 'single_text_field' THEN response END) AS "Enter the temperature of any Meat items (Chicken/Beef)",
MAX(CASE WHEN parent_question = 'Enter the temperature of any Meat items (Chicken/Beef)' and q_type = 'upload_file' THEN response END) AS "Enter the temperature of any Meat items (Chicken/Beef) Image",
MAX(CASE WHEN parent_question = 'Record the temperature at the top of the Pizza Warmer' and q_type = 'single_text_field' THEN response END) AS "Record the temperature at the top of the Pizza Warmer",
MAX(CASE WHEN parent_question = 'Record the temperature at the top of the Pizza Warmer' and q_type = 'upload_file' THEN response END) AS "Record the temperature at the top of the Pizza Warmer Image",
MAX(CASE WHEN parent_question = 'Check and only record the display temperature of Pizza Oven' and q_type = 'single_text_field' THEN response END) AS "Check and only record the display temperature of Pizza Oven",
MAX(CASE WHEN parent_question = 'Check and only record the display temperature of Pizza Oven' and q_type = 'upload_file' THEN response END) AS "Check and only record the display temperature of Pizza Oven Image",
MAX(CASE WHEN parent_question = 'Have the Proofer’s temperature and humidity been checked?' and q_type = 'multiple_choice' THEN response END) AS "Have the Proofer’s temperature and humidity been checked?",
MAX(CASE WHEN parent_question = 'Have the Proofer’s temperature and humidity been checked?' and q_type = 'upload_file' THEN response END) AS "Have the Proofer’s temperature and humidity been checked? Image",

MAX(CASE WHEN parent_question = 'Calibrated thermometer' THEN response END) AS "Calibrated thermometer",

MAX(CASE WHEN parent_question = 'Calibration' and q_type = 'multiple_choice' THEN response END) AS "Calibration",
MAX(CASE WHEN parent_question = 'Calibration' and question = 'Done By:' THEN response END) AS "Calibration Done by",
MAX(CASE WHEN parent_question = 'Calibration' and q_type = 'upload_file' THEN response END) AS "Calibration Image",
MAX(CASE WHEN parent_question = 'Do we have all types of Pizza Boxes, Side Dish Boxes, Sandwich Boxes, and Inliners (Maestro, Pinzatta, MAD) available?' and q_type = 'multiple_choice' THEN response END) AS "Do we have all types of Pizza Boxes, Side Dish Boxes, Sandwich Boxes, and Inliners (Maestro, Pinzatta, MAD) available?",
MAX(CASE WHEN parent_question = 'Do we have all types of Pizza Boxes, Side Dish Boxes, Sandwich Boxes, and Inliners (Maestro, Pinzatta, MAD) available?' and q_type = 'upload_file' THEN response END) AS "Do we have all types of Pizza Boxes, Side Dish Boxes, Sandwich Boxes, and Inliners (Maestro, Pinzatta, MAD) available? Image",

MAX(CASE WHEN parent_question = 'Are Piano Boxes prepared with 3 inliners and a dip sauce holder?' and q_type = 'multiple_choice' THEN response END) AS "Are Piano Boxes prepared with 3 inliners and a dip sauce holder?",
MAX(CASE WHEN parent_question = 'Are Piano Boxes prepared with 3 inliners and a dip sauce holder?' and q_type = 'upload_file' THEN response END) AS "Are Piano Boxes prepared with 3 inliners and a dip sauce holder? Image",

MAX(CASE WHEN parent_question = 'Are all sauces in swirl bottles available?' and q_type = 'multiple_choice' THEN response END) AS "Are all sauces in swirl bottles available?",
MAX(CASE WHEN parent_question = 'Are all sauces in swirl bottles available?' and q_type = 'upload_file' THEN response END) AS "Are all sauces in swirl bottles available? Image",

MAX(CASE WHEN parent_question = 'Are the Louisiana and BBQ sauce bottles placed with caps in the Counter Top Chiller?' and q_type = 'multiple_choice' THEN response END) AS "Are the Louisiana and BBQ sauce bottles placed with caps in the Counter Top Chiller?",
MAX(CASE WHEN parent_question = 'Are the Louisiana and BBQ sauce bottles placed with caps in the Counter Top Chiller?' and q_type = 'upload_file'  THEN response END) AS "Are the Louisiana and BBQ sauce bottles placed with caps in the Counter Top Chiller? Image",

MAX(CASE WHEN parent_question = 'Is Sugar mix ready and are Crushed Nachos available (only Crushed Nachos for EI Taco Pizza orders)?' and q_type = 'multiple_choice' THEN response END) AS "Is Sugar mix ready and are Crushed Nachos available (only Crushed Nachos for EI Taco Pizza orders)?",
MAX(CASE WHEN parent_question = 'Is Sugar mix ready and are Crushed Nachos available (only Crushed Nachos for EI Taco Pizza orders)?' and q_type = 'upload_file' THEN response END) AS "Is Sugar mix ready and are Crushed Nachos available (only Crushed Nachos for EI Taco Pizza orders)? Image",

MAX(CASE WHEN parent_question = 'Does the Counter Top Chiller have fresh Basil Leaves and Rocca Leaves (needed for Pinzatta sandwiches)?' and q_type = 'multiple_choice' THEN response END) AS "Does the Counter Top Chiller have fresh Basil Leaves and Rocca Leaves (needed for Pinzatta sandwiches)?",
MAX(CASE WHEN parent_question = 'Does the Counter Top Chiller have fresh Basil Leaves and Rocca Leaves (needed for Pinzatta sandwiches)?' and q_type = 'upload_file' THEN response END) AS "Does the Counter Top Chiller have fresh Basil Leaves and Rocca Leaves (needed for Pinzatta sandwiches)?",

MAX(CASE WHEN parent_question = 'Have all items been checked for expiry dates and are they correct?' and q_type = 'multiple_choice' THEN response END) AS "Have all items been checked for expiry dates and are they correct?",
MAX(CASE WHEN parent_question = 'Have all items been checked for expiry dates and are they correct?' and q_type = 'upload_file' THEN response END) AS "Have all items been checked for expiry dates and are they correct? Image",

MAX(CASE WHEN parent_question = 'Is the Fatura Highlighter available and working properly?' and q_type = 'multiple_choice' THEN response END) AS "Is the Fatura Highlighter available and working properly?",
MAX(CASE WHEN parent_question = 'Is the Fatura Highlighter available and working properly?' and q_type = 'upload_file' THEN response END) AS "Is the Fatura Highlighter available and working properly? Image",

MAX(CASE WHEN parent_question = 'Are Sealing Stickers and Bags ready for Maestro, Pinzatta, and MAD Pizza?' and q_type = 'multiple_choice' THEN response END) AS "Are Sealing Stickers and Bags ready for Maestro, Pinzatta, and MAD Pizza?",
MAX(CASE WHEN parent_question = 'Are Sealing Stickers and Bags ready for Maestro, Pinzatta, and MAD Pizza?' and q_type = 'upload_file' THEN response END) AS "Are Sealing Stickers and Bags ready for Maestro, Pinzatta, and MAD Pizza? Image",

MAX(CASE WHEN parent_question = 'Are Wet Tissues (for MAD Wings) and Kids Toys (for Maestro) available?' and q_type = 'multiple_choice' THEN response END) AS "Are Wet Tissues (for MAD Wings) and Kids Toys (for Maestro) available?",
MAX(CASE WHEN parent_question = 'Are Wet Tissues (for MAD Wings) and Kids Toys (for Maestro) available?' and q_type = 'upload_file' THEN response END) AS "Are Wet Tissues (for MAD Wings) and Kids Toys (for Maestro) available? Image",

MAX(CASE WHEN parent_question = 'Is sufficient Cash Change available at the cashier counter?' and q_type = 'multiple_choice' THEN response END) AS "Is sufficient Cash Change available at the cashier counter?",
MAX(CASE WHEN parent_question = 'Is sufficient Cash Change available at the cashier counter?' and q_type = 'upload_file' THEN response END) AS "Is sufficient Cash Change available at the cashier counter?",

MAX(CASE WHEN parent_question = 'Are the Span Machines fully charged and in working condition?' and q_type = 'multiple_choice' THEN response END) AS "Are the Span Machines fully charged and in working condition?",
MAX(CASE WHEN parent_question = 'Are the Delivery Bags clean and connected to Vollrath / CookTek chargers?' and q_type = 'multiple_choice'  THEN response END) AS "Are the Delivery Bags clean and connected to Vollrath / CookTek chargers? ",
MAX(CASE WHEN parent_question = 'Are the Delivery Bags clean and connected to Vollrath / CookTek chargers?' and q_type = 'upload_file' THEN response END) AS "Are the Delivery Bags clean and connected to Vollrath / CookTek chargers? Image",

MAX(CASE WHEN parent_question = 'Note the Visi Cooler (Beverage Can Cooler) temperature' and q_type = 'single_text_field' THEN response END) AS "Note the Visi Cooler (Beverage Can Cooler) temperature",
MAX(CASE WHEN parent_question = 'Note the Visi Cooler (Beverage Can Cooler) temperature' and q_type = 'upload_file' THEN response END) AS "Note the Visi Cooler (Beverage Can Cooler) temperature Image",
MAX(CASE WHEN parent_question = 'Do we have all Drinks filled and available in the cooler?' and q_type = 'multiple_choice' THEN response END) AS "Do we have all Drinks filled and available in the cooler?",
MAX(CASE WHEN parent_question = 'Do we have all Drinks filled and available in the cooler?' and q_type = 'upload_file' THEN response END) AS "Do we have all Drinks filled and available in the cooler? Image",

MAX(CASE WHEN parent_question = 'Are all Sauce Dips stocked and available?' and q_type = 'multiple_choice' THEN response END) AS "Are all Sauce Dips stocked and available?",
MAX(CASE WHEN parent_question = 'Are all Sauce Dips stocked and available?' and q_type = 'upload_file' THEN response END) AS "Are all Sauce Dips stocked and available? Image",

MAX(CASE WHEN parent_question = 'Are Rocca Boxes for Maestro and Pinzatta ready with the correct expiry date?' and q_type = 'multiple_choice' THEN response END) AS "Are Rocca Boxes for Maestro and Pinzatta ready with the correct expiry date?",
MAX(CASE WHEN parent_question = 'Are Rocca Boxes for Maestro and Pinzatta ready with the correct expiry date?' and q_type = 'upload_file' THEN response END) AS "Are Rocca Boxes for Maestro and Pinzatta ready with the correct expiry date? Image",

MAX(CASE WHEN parent_question = 'Glass bottles or Glass items stored in lower racks?' and q_type = 'multiple_choice' THEN response END) AS "Glass bottles or Glass items stored in lower racks?",
MAX(CASE WHEN parent_question = 'Glass bottles or Glass items stored in lower racks?' and q_type = 'upload_file' THEN response END) AS "Glass bottles or Glass items stored in lower racks? Image"

FROM RAW
GROUP BY 1,
         2,
         3
```

---

## Sanitization - Critical Food Contact Surface 24 Hours Operations_Sanitization - Critical Food Contact Surface 24 Hours Operations - Moved.sql

**Tables referenced:** RAW, _fs, current_date, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Sanitization - Critical Food Contact Surface 24 Hours Operations
-- Dashboard: Sanitization - Critical Food Contact Surface 24 Hours Operations - Moved
-- Category: Maestro Custom Reports
-- Extracted: 2026-01-29 16:52:34
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'maestropizza-ksa-cartwheel'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ILIKE ('Sanitization - Critical Food Contact Surface | 24 Hours Operations%')
     AND organization = 'maestropizza-ksa-cartwheel'
     AND is_deleted = FALSE
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
  WHERE submit_date >= current_date
                     - extract(dow from current_date)::int
                     - 7
   ORDER BY response_id,
            id DESC),
     fs AS
  ( SELECT *
   FROM _fs
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
          LOCATION
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
                LOCATION
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
             LOCATION
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id
      JOIN td ON fs.organization = td.organization,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res), /*location_questions as (
select distinct on (nugget_id) nugget_id, question_id from question_definitions qd
where nugget_id in (select form_knid from forms)
and question_type = 'location'
order by nugget_id, section_id, sqno
),
location_response as (
select form_submit_id, (response ->> 'name')::text location_name from form_responses fr
where question_id in (select question_id from location_questions)
and form_submit_id in (select id from fs)
),*/ RAW AS
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
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          fr.user_id,
          ud.first_name AS "UserName"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN user_details ud ON fr.user_id = ud.uuid
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
            15,
            16,
            17
   ORDER BY 1,
            2,
            3)
SELECT sno as "Sno",
       submit_date as "Submit Date",
       "UserName" as "Form Submitted By",
       MAX(CASE
               WHEN parent_question = 'Branch' THEN response
           END) AS "Branch",
       MAX(CASE
               WHEN parent_question = 'Make table surface, cabinet door handles, lid top & handles, make table shelves' THEN response
           END) AS "Make table surface, cabinet door handles, lid top & handles, make table shelves",
       MAX(CASE
               WHEN parent_question = 'Standing chiller handles, knobs & timer' THEN response
           END) AS "Standing chiller handles, knobs & timer",
       MAX(CASE
               WHEN parent_question = 'Proofer handles, knobs & timer, inside proofer dry' THEN response
           END) AS "Proofer handles, knobs & timer, inside proofer dry",
       MAX(CASE
               WHEN parent_question = 'Walk-in cooler & freezer door handles' THEN response
           END) AS "Walk-in cooler & freezer door handles",
       MAX(CASE
               WHEN parent_question = 'Sauce Ladles, topping scoop and other small wares' THEN response
           END) AS "Sauce Ladles, topping scoop and other small wares",
       MAX(CASE
               WHEN parent_question = 'Order screens, make table, cut table' THEN response
           END) AS "Order screens, make table, cut table",
       MAX(CASE
               WHEN parent_question = 'Cut table surface, SS pizza cutter, tongs, Cutting board,Pie server, bread knife' THEN response
           END) AS "Cut table surface, SS pizza cutter, tongs, Cutting board,Pie server, bread knife",
       MAX(CASE
               WHEN parent_question = 'Sauce chiller, Pizza warmer surface & knobs' THEN response
           END) AS "Sauce chiller, Pizza warmer surface & knobs",
       MAX(CASE
               WHEN parent_question = 'Dispatch table, customer counter' THEN response
           END) AS "Dispatch table, customer counter",
       MAX(CASE
               WHEN parent_question = 'Customer self-service kiosk' THEN response
           END) AS "Customer self-service kiosk",
       MAX(CASE
               WHEN parent_question = 'Front door handle' THEN response
           END) AS "Front door handle"
FROM RAW
GROUP BY 1,
         2,
         3
```

---

## Sanitization - Critical Food Contact Surface_Sanitization - Critical Food Contact Surface.sql

**Tables referenced:** RAW, _fs, current_date, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Sanitization - Critical Food Contact Surface
-- Dashboard: Sanitization - Critical Food Contact Surface
-- Category: Maestro Custom Reports
-- Extracted: 2026-01-29 16:52:33
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'maestropizza-ksa-cartwheel'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ILIKE ('Sanitization - Critical Food Contact Surface%')
     AND organization = 'maestropizza-ksa-cartwheel'
     AND is_deleted = FALSE
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
   WHERE submit_date >= current_date
                     - extract(dow from current_date)::int
                     - 7
   ORDER BY response_id,
            id DESC),
     fs AS
  (SELECT *
   FROM _fs
  
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
          LOCATION
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
                LOCATION
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
             LOCATION
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id
      JOIN td ON fs.organization = td.organization,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res), /*location_questions as (
select distinct on (nugget_id) nugget_id, question_id from question_definitions qd
where nugget_id in (select form_knid from forms)
and question_type = 'location'
order by nugget_id, section_id, sqno
),
location_response as (
select form_submit_id, (response ->> 'name')::text location_name from form_responses fr
where question_id in (select question_id from location_questions)
and form_submit_id in (select id from fs)
),*/ RAW AS
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
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          fr.user_id,
          ud.first_name AS "UserName"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN user_details ud ON fr.user_id = ud.uuid
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
            15,
            16,
            17
   ORDER BY 1,
            2,
            3)
SELECT sno AS "Sno",
       submit_date AS "Submit Date",
       "UserName" AS "Form Submitted By",
       MAX(CASE
               WHEN parent_question = 'Branch' THEN response
           END) AS "Branch",
       MAX(CASE
               WHEN parent_question = 'Make table surface, cabinet door handles, lid top & handles, make table shelves' THEN response
           END) AS "Make table surface, cabinet door handles, lid top & handles, make table shelves",
       MAX(CASE
               WHEN parent_question = 'Standing chiller handles, knobs & timer' THEN response
           END) AS "Standing chiller handles, knobs & timer",
       MAX(CASE
               WHEN parent_question = 'Proofer handles, knobs & timer, inside proofer dry' THEN response
           END) AS "Proofer handles, knobs & timer, inside proofer dry",
       MAX(CASE
               WHEN parent_question = 'Walk-in cooler & freezer door handles' THEN response
           END) AS "Walk-in cooler & freezer door handles",
       MAX(CASE
               WHEN parent_question = 'Sauce Ladles, topping scoop and other small wares' THEN response
           END) AS "Sauce Ladles, topping scoop and other small wares",
       MAX(CASE
               WHEN parent_question = 'Order screens, make table, cut table' THEN response
           END) AS "Order screens, make table, cut table",
       MAX(CASE
               WHEN parent_question = 'Cut table surface, SS pizza cutter, tongs, Cutting board,Pie server, bread knife' THEN response
           END) AS "Cut table surface, SS pizza cutter, tongs, Cutting board,Pie server, bread knife",
       MAX(CASE
               WHEN parent_question = 'Sauce chiller, Pizza warmer surface & knobs' THEN response
           END) AS "Sauce chiller, Pizza warmer surface & knobs",
       MAX(CASE
               WHEN parent_question = 'Dispatch table, customer counter' THEN response
           END) AS "Dispatch table, customer counter",
       MAX(CASE
               WHEN parent_question = 'Customer self-service kiosk' THEN response
           END) AS "Customer self-service kiosk",
       MAX(CASE
               WHEN parent_question = 'Front door handle' THEN response
           END) AS "Front door handle"
FROM RAW
GROUP BY 1,
         2,
         3
```

---
