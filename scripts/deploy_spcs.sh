#!/bin/bash
# ============================================================================
# Trade Compliance - SPCS Deployment Script
# ============================================================================

set -e

# Configuration
SNOWFLAKE_ACCOUNT="${SNOWFLAKE_ACCOUNT:-your_account}"
SNOWFLAKE_USER="${SNOWFLAKE_USER:-your_user}"
DATABASE="TRADE_COMPLIANCE_DB"
SCHEMA="SPCS"
REPO="COMPLIANCE_REPO"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Trade Compliance SPCS Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Get repository URL
echo -e "\n${YELLOW}Getting repository URL...${NC}"
REPO_URL=$(snow sql -c my_snowflake -q "SHOW IMAGE REPOSITORIES IN SCHEMA ${DATABASE}.${SCHEMA};" --format json | jq -r '.[0].repository_url')
echo "Repository URL: $REPO_URL"

# Docker login to Snowflake
echo -e "\n${YELLOW}Logging into Snowflake container registry...${NC}"
snow spcs image-registry login

# Build and push backend
echo -e "\n${YELLOW}Building backend image...${NC}"
cd copilot/backend
docker build -t ${REPO_URL}/backend:latest .
echo -e "\n${YELLOW}Pushing backend image...${NC}"
docker push ${REPO_URL}/backend:latest
cd ../..

# Build and push frontend
echo -e "\n${YELLOW}Building frontend image...${NC}"
cd copilot/frontend
docker build -t ${REPO_URL}/frontend:latest .
echo -e "\n${YELLOW}Pushing frontend image...${NC}"
docker push ${REPO_URL}/frontend:latest
cd ../..

# Deploy services
echo -e "\n${YELLOW}Deploying SPCS services...${NC}"

# Create backend service
snow sql -c my_snowflake -q "
CREATE SERVICE IF NOT EXISTS ${DATABASE}.${SCHEMA}.COMPLIANCE_BACKEND
    IN COMPUTE POOL COMPLIANCE_POOL
    FROM SPECIFICATION \$\$
    spec:
      containers:
      - name: backend
        image: ${REPO_URL}/backend:latest
        env:
          TC_DATABASE: ${DATABASE}
          TC_WAREHOUSE: COMPLIANCE_COMPUTE_WH
        resources:
          requests:
            cpu: '0.5'
            memory: '1Gi'
          limits:
            cpu: '2'
            memory: '4Gi'
      endpoints:
      - name: api
        port: 8000
        public: true
    \$\$
    MIN_INSTANCES = 1
    MAX_INSTANCES = 3;
"

# Create frontend service
snow sql -c my_snowflake -q "
CREATE SERVICE IF NOT EXISTS ${DATABASE}.${SCHEMA}.COMPLIANCE_FRONTEND
    IN COMPUTE POOL COMPLIANCE_POOL
    FROM SPECIFICATION \$\$
    spec:
      containers:
      - name: frontend
        image: ${REPO_URL}/frontend:latest
        env:
          VITE_API_URL: /api
        resources:
          requests:
            cpu: '0.25'
            memory: '512Mi'
          limits:
            cpu: '1'
            memory: '2Gi'
      endpoints:
      - name: web
        port: 80
        public: true
    \$\$
    MIN_INSTANCES = 1
    MAX_INSTANCES = 2;
"

# Get service URLs
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${YELLOW}Service Status:${NC}"
snow sql -c my_snowflake -q "SHOW SERVICES IN SCHEMA ${DATABASE}.${SCHEMA};"

echo -e "\n${YELLOW}To get service URLs, run:${NC}"
echo "snow sql -c my_snowflake -q \"CALL SYSTEM\$GET_SERVICE_STATUS('${DATABASE}.${SCHEMA}.COMPLIANCE_BACKEND');\""
echo "snow sql -c my_snowflake -q \"CALL SYSTEM\$GET_SERVICE_STATUS('${DATABASE}.${SCHEMA}.COMPLIANCE_FRONTEND');\""
