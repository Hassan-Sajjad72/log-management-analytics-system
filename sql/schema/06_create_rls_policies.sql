-- Row-Level Security (RLS) Setup
-- Enables per-team data isolation at the database engine level.

-- Step 1: Create a restricted role for the web application
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'web_user') THEN
    CREATE ROLE web_user WITH LOGIN PASSWORD 'web_password';
  END IF;
END
$$;

-- Step 2: Grant minimum necessary privileges
GRANT USAGE ON SCHEMA public TO web_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO web_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO web_user;

-- Step 3: Enable RLS on log tables
ALTER TABLE logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE logs_unpartitioned ENABLE ROW LEVEL SECURITY;

-- Step 4: Create team isolation policies
-- The policy checks a session variable (app.current_team) set by the application.
-- Admin or empty team sees all rows. Otherwise, only rows belonging to the team's services.
DROP POLICY IF EXISTS team_isolation_policy ON logs;
CREATE POLICY team_isolation_policy ON logs
FOR ALL
USING (
    current_setting('app.current_team', true) = 'Admin'
    OR current_setting('app.current_team', true) IS NULL
    OR current_setting('app.current_team', true) = ''
    OR service_id IN (
        SELECT service_id FROM services
        WHERE owner_team = current_setting('app.current_team', true)
    )
);

DROP POLICY IF EXISTS team_isolation_policy ON logs_unpartitioned;
CREATE POLICY team_isolation_policy ON logs_unpartitioned
FOR ALL
USING (
    current_setting('app.current_team', true) = 'Admin'
    OR current_setting('app.current_team', true) IS NULL
    OR current_setting('app.current_team', true) = ''
    OR service_id IN (
        SELECT service_id FROM services
        WHERE owner_team = current_setting('app.current_team', true)
    )
);
