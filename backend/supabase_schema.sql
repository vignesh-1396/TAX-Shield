-- Users table (extends Supabase auth.users)
-- Note: auth.users.id is UUID type in this Supabase instance
-- Schema: itc_gaurd (lowercase)

CREATE TABLE itc_gaurd.search_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users NOT NULL,
  query TEXT NOT NULL,
  filters JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE itc_gaurd.users (
  id UUID REFERENCES auth.users PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  company_name TEXT,
  phone TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User profiles (settings)
CREATE TABLE itc_gaurd.user_profiles (
  user_id UUID REFERENCES itc_gaurd.users PRIMARY KEY,
  default_amount DECIMAL(10,2) DEFAULT 10000,
  date_format TEXT DEFAULT 'DD/MM/YYYY',
  currency_format TEXT DEFAULT 'INR',
  auto_download BOOLEAN DEFAULT false,
  email_alerts BOOLEAN DEFAULT true,
  weekly_summary BOOLEAN DEFAULT true,
  risk_threshold INTEGER DEFAULT 70,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Subscriptions
CREATE TABLE itc_gaurd.subscriptions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES itc_gaurd.users NOT NULL,
  plan TEXT NOT NULL CHECK (plan IN ('trial', 'pro', 'enterprise')),
  billing_cycle TEXT CHECK (billing_cycle IN ('monthly', 'annual')),
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired')),
  trial_ends_at TIMESTAMPTZ,
  current_period_start TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,
  checks_used INTEGER DEFAULT 0,
  checks_limit INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Invoices
CREATE TABLE itc_gaurd.invoices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES itc_gaurd.users NOT NULL,
  subscription_id UUID REFERENCES itc_gaurd.subscriptions,
  invoice_number TEXT UNIQUE NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'failed')),
  plan TEXT NOT NULL,
  billing_date TIMESTAMPTZ DEFAULT NOW(),
  payment_method TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Compliance check history
CREATE TABLE itc_gaurd.compliance_checks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES itc_gaurd.users NOT NULL,
  gstin TEXT NOT NULL,
  vendor_name TEXT,
  amount DECIMAL(15,2),
  decision TEXT NOT NULL CHECK (decision IN ('APPROVED', 'REJECTED', 'REVIEW')),
  risk_score INTEGER,
  reasons JSONB,
  gsp_data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for compliance checks
CREATE INDEX idx_user_checks ON itc_gaurd.compliance_checks(user_id, created_at DESC);
CREATE INDEX idx_gstin ON itc_gaurd.compliance_checks(gstin);
CREATE INDEX idx_decision ON itc_gaurd.compliance_checks(decision);

-- Batch jobs
CREATE TABLE itc_gaurd.batch_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES itc_gaurd.users NOT NULL,
  job_id TEXT UNIQUE NOT NULL,
  filename TEXT NOT NULL,
  total_records INTEGER NOT NULL,
  processed_records INTEGER DEFAULT 0,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  results JSONB,
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Vendors
CREATE TABLE itc_gaurd.vendors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES itc_gaurd.users NOT NULL,
  gstin TEXT NOT NULL,
  legal_name TEXT,
  trade_name TEXT,
  status TEXT,
  registration_date DATE,
  last_checked_at TIMESTAMPTZ,
  risk_level TEXT CHECK (risk_level IN ('low', 'medium', 'high')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, gstin)
);

-- Filing history
CREATE TABLE itc_gaurd.filing_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  vendor_id UUID REFERENCES itc_gaurd.vendors NOT NULL,
  return_type TEXT NOT NULL,
  tax_period TEXT NOT NULL,
  filing_date DATE,
  status TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit trail
CREATE TABLE itc_gaurd.audit_trail (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES itc_gaurd.users NOT NULL,
  action TEXT NOT NULL,
  resource_type TEXT,
  resource_id UUID,
  details JSONB,
  ip_address TEXT,
  user_agent TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_user_audit ON itc_gaurd.audit_trail(user_id, created_at DESC);

-- RLS Policies (Row Level Security)
ALTER TABLE itc_gaurd.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE itc_gaurd.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE itc_gaurd.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE itc_gaurd.invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE itc_gaurd.compliance_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE itc_gaurd.batch_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE itc_gaurd.vendors ENABLE ROW LEVEL SECURITY;
ALTER TABLE itc_gaurd.filing_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE itc_gaurd.audit_trail ENABLE ROW LEVEL SECURITY;
ALTER TABLE itc_gaurd.search_history ENABLE ROW LEVEL SECURITY;

-- Create policy manual for now (allow all for authenticated users matching ID)
CREATE POLICY "Users can view own profile" ON itc_gaurd.users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON itc_gaurd.users FOR UPDATE USING (auth.uid() = id);

-- Trigger to create user profile on signup
CREATE OR REPLACE FUNCTION itc_gaurd.handle_new_user() 
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO itc_gaurd.users (id, email)
  VALUES (new.id, new.email);
  
  INSERT INTO itc_gaurd.user_profiles (user_id)
  VALUES (new.id);
  
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE itc_gaurd.handle_new_user();
