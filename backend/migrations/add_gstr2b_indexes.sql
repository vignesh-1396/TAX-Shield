-- CORRECTED: Add indexes to gstr_2b_data table for optimized queries
-- Run this via Supabase SQL Editor

-- Index on (user_id, return_period) for fast filtering
CREATE INDEX IF NOT EXISTS idx_gstr2b_user_period 
ON itc_gaurd.gstr_2b_data(user_id, return_period);

-- Index on gstin_supplier for join operations (CORRECTED COLUMN NAME)
CREATE INDEX IF NOT EXISTS idx_gstr2b_gstin_supplier 
ON itc_gaurd.gstr_2b_data(gstin_supplier);

-- Composite index for common query pattern (CORRECTED COLUMN NAME)
CREATE INDEX IF NOT EXISTS idx_gstr2b_lookup 
ON itc_gaurd.gstr_2b_data(user_id, return_period, gstin_supplier);

-- Verify indexes were created
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'itc_gaurd' 
  AND tablename = 'gstr_2b_data'
ORDER BY indexname;
