-- ============================================================================
-- TRADE COMPLIANCE - SPCS Deployment DDL
-- Snowpark Container Services setup
-- ============================================================================

USE DATABASE TRADE_COMPLIANCE_DB;
USE SCHEMA SPCS;
USE ROLE ACCOUNTADMIN;

-- ============================================================================
-- COMPUTE POOL
-- ============================================================================
CREATE COMPUTE POOL IF NOT EXISTS COMPLIANCE_POOL
    MIN_NODES = 1
    MAX_NODES = 3
    INSTANCE_FAMILY = CPU_X64_S
    AUTO_RESUME = TRUE
    AUTO_SUSPEND_SECS = 300
    COMMENT = 'Compute pool for Trade Compliance application';

-- ============================================================================
-- IMAGE REPOSITORY
-- ============================================================================
CREATE IMAGE REPOSITORY IF NOT EXISTS COMPLIANCE_REPO
    COMMENT = 'Container images for Trade Compliance';

-- Show repository URL for pushing images
SHOW IMAGE REPOSITORIES IN SCHEMA;

-- ============================================================================
-- EXTERNAL ACCESS INTEGRATION (if needed for external APIs)
-- ============================================================================
CREATE OR REPLACE NETWORK RULE COMPLIANCE_EGRESS_RULE
    MODE = EGRESS
    TYPE = HOST_PORT
    VALUE_LIST = ('api.openai.com:443', 'api.anthropic.com:443');

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION COMPLIANCE_EXTERNAL_ACCESS
    ALLOWED_NETWORK_RULES = (COMPLIANCE_EGRESS_RULE)
    ENABLED = TRUE
    COMMENT = 'External access for LLM APIs if needed';

-- ============================================================================
-- OAUTH SECURITY INTEGRATION (for Snowflake OAuth)
-- ============================================================================
CREATE OR REPLACE SECURITY INTEGRATION COMPLIANCE_OAUTH
    TYPE = oauth
    OAUTH_CLIENT = snowservices_ingress
    ENABLED = TRUE;

-- ============================================================================
-- SERVICE SPECIFICATION STAGE
-- ============================================================================
CREATE STAGE IF NOT EXISTS SPCS.SERVICE_SPECS
    COMMENT = 'Stage for service specification YAML files';

-- ============================================================================
-- SERVICE: Backend API
-- ============================================================================
-- Note: After pushing images to repository, create service with:
/*
CREATE SERVICE COMPLIANCE_BACKEND
    IN COMPUTE POOL COMPLIANCE_POOL
    FROM SPECIFICATION $$
    spec:
      containers:
      - name: backend
        image: /trade_compliance_db/spcs/compliance_repo/backend:latest
        env:
          TC_DATABASE: TRADE_COMPLIANCE_DB
          TC_WAREHOUSE: COMPLIANCE_COMPUTE_WH
        resources:
          requests:
            cpu: "0.5"
            memory: "1Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
      endpoints:
      - name: api
        port: 8000
        public: true
    $$
    MIN_INSTANCES = 1
    MAX_INSTANCES = 3
    EXTERNAL_ACCESS_INTEGRATIONS = (COMPLIANCE_EXTERNAL_ACCESS)
    COMMENT = 'Trade Compliance Backend API';
*/

-- ============================================================================
-- SERVICE: Frontend Web App
-- ============================================================================
/*
CREATE SERVICE COMPLIANCE_FRONTEND
    IN COMPUTE POOL COMPLIANCE_POOL
    FROM SPECIFICATION $$
    spec:
      containers:
      - name: frontend
        image: /trade_compliance_db/spcs/compliance_repo/frontend:latest
        env:
          VITE_API_URL: /api
        resources:
          requests:
            cpu: "0.25"
            memory: "512Mi"
          limits:
            cpu: "1"
            memory: "2Gi"
      endpoints:
      - name: web
        port: 80
        public: true
    $$
    MIN_INSTANCES = 1
    MAX_INSTANCES = 2
    COMMENT = 'Trade Compliance Frontend';
*/

-- ============================================================================
-- GRANTS
-- ============================================================================
GRANT USAGE ON COMPUTE POOL COMPLIANCE_POOL TO ROLE ACCOUNTADMIN;
GRANT USAGE ON INTEGRATION COMPLIANCE_EXTERNAL_ACCESS TO ROLE ACCOUNTADMIN;

-- View services
SHOW SERVICES IN SCHEMA SPCS;
SHOW COMPUTE POOLS;
