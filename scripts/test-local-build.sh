#!/bin/bash
# Test local Maven builds for all services

set -e  # Exit on error

echo "🧪 Testing EcoCycle Local Builds"
echo "================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test a service
test_service() {
    local service=$1
    echo -e "${YELLOW}Testing $service...${NC}"
    cd "$service"
    
    if mvn clean verify -DskipTests; then
        echo -e "${GREEN}✅ $service build successful${NC}"
        cd ..
        return 0
    else
        echo -e "${RED}❌ $service build failed${NC}"
        cd ..
        return 1
    fi
}

# Test all services
FAILED=0

test_service "marketplace-service" || FAILED=1
echo ""
test_service "users-service" || FAILED=1
echo ""
test_service "transactions-service" || FAILED=1
echo ""

# Summary
echo "================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All services built successfully!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some services failed to build${NC}"
    exit 1
fi

