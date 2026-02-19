"""
Database Migration: Add Performance Indexes
Optimizes query performance for compliance checks, batch jobs, and vendors
"""

-- ============================================
-- COMPLIANCE CHECKS INDEXES
-- ============================================

-- Index for user's compliance check history (most common query)
CREATE INDEX IF NOT EXISTS idx_compliance_user_created 
ON itc_gaurd.compliance_checks(user_id, created_at DESC);

-- Index for GSTIN lookups with timestamp
CREATE INDEX IF NOT EXISTS idx_compliance_gstin_created 
ON itc_gaurd.compliance_checks(gstin, created_at DESC);

-- Index for filtering by decision type
CREATE INDEX IF NOT EXISTS idx_compliance_decision_created 
ON itc_gaurd.compliance_checks(decision, created_at DESC);

-- Composite index for user + decision filtering
CREATE INDEX IF NOT EXISTS idx_compliance_user_decision 
ON itc_gaurd.compliance_checks(user_id, decision, created_at DESC);

-- ============================================
-- BATCH JOBS INDEXES
-- ============================================

-- Index for user's batch jobs with status filtering
CREATE INDEX IF NOT EXISTS idx_batch_user_status 
ON itc_gaurd.batch_jobs(user_id, status, created_at DESC);

-- Index for job status monitoring
CREATE INDEX IF NOT EXISTS idx_batch_status_created 
ON itc_gaurd.batch_jobs(status, created_at DESC);

-- ============================================
-- BATCH ITEMS INDEXES
-- ============================================

-- Index for batch items by batch_id and status
CREATE INDEX IF NOT EXISTS idx_batch_items_batch_status 
ON itc_gaurd.batch_items(batch_id, status);

-- Index for batch items by GSTIN
CREATE INDEX IF NOT EXISTS idx_batch_items_gstin 
ON itc_gaurd.batch_items(gstin);

-- ============================================
-- VENDORS INDEXES
-- ============================================

-- Index for GSTIN lookups (primary lookup key)
CREATE INDEX IF NOT EXISTS idx_vendors_gstin 
ON itc_gaurd.vendors(gstin);

-- Index for finding vendors needing refresh
CREATE INDEX IF NOT EXISTS idx_vendors_last_checked 
ON itc_gaurd.vendors(last_checked_at);

-- Index for user's vendors
CREATE INDEX IF NOT EXISTS idx_vendors_user_gstin 
ON itc_gaurd.vendors(user_id, gstin);

-- Index for risk level filtering
CREATE INDEX IF NOT EXISTS idx_vendors_risk_level 
ON itc_gaurd.vendors(risk_level, last_checked_at DESC);

-- ============================================
-- SEARCH HISTORY INDEXES
-- ============================================

-- Index for user's search history
CREATE INDEX IF NOT EXISTS idx_search_user_created 
ON itc_gaurd.search_history(user_id, created_at DESC);

-- ============================================
-- AUDIT TRAIL INDEXES
-- ============================================

-- Index for user's audit trail (already exists in schema but ensuring)
CREATE INDEX IF NOT EXISTS idx_audit_user_created 
ON itc_gaurd.audit_trail(user_id, created_at DESC);

-- Index for resource tracking
CREATE INDEX IF NOT EXISTS idx_audit_resource 
ON itc_gaurd.audit_trail(resource_type, resource_id, created_at DESC);

-- ============================================
-- PERFORMANCE ANALYSIS
-- ============================================

-- Run ANALYZE to update statistics after creating indexes
ANALYZE itc_gaurd.compliance_checks;
ANALYZE itc_gaurd.batch_jobs;
ANALYZE itc_gaurd.batch_items;
ANALYZE itc_gaurd.vendors;
ANALYZE itc_gaurd.search_history;
ANALYZE itc_gaurd.audit_trail;
