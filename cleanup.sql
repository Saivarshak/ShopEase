
-- 1. Remove all Accessories products completely from the database
DELETE FROM store_product 
WHERE product_name LIKE '%Accessories%' 
   OR category_id IN (SELECT category_id FROM categories WHERE category_name LIKE '%Accessories%')
   OR subcategory_id IN (SELECT subcategory_id FROM subcategories WHERE subcategory_name LIKE '%Accessories%')
   OR fashion_category_id IN (SELECT fashion_category_id FROM fashion_categories WHERE name LIKE '%Accessories%');

-- 2. Delete all existing Accessories product records (already covered by above but ensuring)
-- No specific product record table other than store_product found in list.

-- 3. Delete Accessories categories/subcategories if they are not needed for the cards.
-- However, the prompt says "Keep only the category cards: Men -> Accessories, Women -> Accessories, Kids -> Accessories"
-- These cards are likely in men_categories, women_categories, kids_categories tables.
-- Let's check those tables.
