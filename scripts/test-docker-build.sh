#!/bin/bash
# Test Docker builds for all services

set -e  # Exit on error

echo "🐳 Testing EcoCycle Docker Builds"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to build Docker image
build_image() {
    local service=$1
    local image_name="ecocycle-${service}:test"
    
    echo -e "${YELLOW}Building Docker image for $service...${NC}"
    
    if docker build -t "$image_name" "./$service-service"; then
        echo -e "${GREEN}✅ $image_name built successfully${NC}"
        
        # Show image size
        size=$(docker images "$image_name" --format "{{.Size}}")
        echo -e "   Image size: $size"
        return 0
    else
        echo -e "${RED}❌ $image_name build failed${NC}"
        return 1
    fi
}

# Build all images
FAILED=0

build_image "marketplace" || FAILED=1
echo ""
build_image "users" || FAILED=1
echo ""
build_image "transactions" || FAILED=1
echo ""

# Summary
echo "=================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All Docker images built successfully!${NC}"
    echo ""
    echo "Built images:"
    docker images | grep "ecocycle.*test"
    exit 0
else
    echo -e "${RED}❌ Some Docker builds failed${NC}"
    exit 1
fi

