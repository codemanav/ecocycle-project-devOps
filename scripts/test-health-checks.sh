#!/bin/bash
# Test health endpoints for all services

echo "🏥 Testing EcoCycle Health Endpoints"
echo "====================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check health
check_health() {
    local service=$1
    local port=$2
    local url="http://localhost:$port/actuator/health"
    
    echo -e "${YELLOW}Checking $service (port $port)...${NC}"
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        response=$(curl -s "$url")
        echo -e "${GREEN}✅ $service is healthy${NC}"
        echo "   Response: $response"
        return 0
    else
        echo -e "${RED}❌ $service is not responding${NC}"
        return 1
    fi
}

# Wait for services to start
echo "Waiting for services to start..."
sleep 10
echo ""

# Check all services
FAILED=0

check_health "Marketplace Service" 8081 || FAILED=1
echo ""
check_health "Transactions Service" 8082 || FAILED=1
echo ""
check_health "Users Service" 8083 || FAILED=1
echo ""

# Summary
echo "====================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All services are healthy!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some services are not healthy${NC}"
    echo "Check logs with: docker-compose logs"
    exit 1
fi


#!/bin/bash
# Test health endpoints for all services

echo "🏥 Testing EcoCycle Health Endpoints"
echo "====================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check health
check_health() {
    local service=$1
    local port=$2
    local url="http://localhost:$port/actuator/health"
    
    echo -e "${YELLOW}Checking $service (port $port)...${NC}"
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        response=$(curl -s "$url")
        echo -e "${GREEN}✅ $service is healthy${NC}"
        echo "   Response: $response"
        return 0
    else
        echo -e "${RED}❌ $service is not responding${NC}"
        return 1
    fi
}

# Wait for services to start
echo "Waiting for services to start..."
sleep 10
echo ""

# Check all services
FAILED=0

check_health "Marketplace Service" 8081 || FAILED=1
echo ""
check_health "Transactions Service" 8082 || FAILED=1
echo ""
check_health "Users Service" 8083 || FAILED=1
echo ""

# Summary
echo "====================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All services are healthy!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some services are not healthy${NC}"
    echo "Check logs with: docker-compose logs"
    exit 1
fi

