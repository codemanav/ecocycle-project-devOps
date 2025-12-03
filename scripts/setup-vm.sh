#!/bin/bash
# Setup script for VM - Run this ON THE VM

echo "🖥️  Setting up EcoCycle VM Environment"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run as root${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y
echo -e "${GREEN}✅ System updated${NC}"
echo ""

echo -e "${YELLOW}Step 2: Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    sudo apt install -y docker.io docker-compose
    sudo systemctl start docker
    sudo systemctl enable docker
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo -e "${GREEN}✅ Docker already installed${NC}"
fi
echo ""

echo -e "${YELLOW}Step 3: Adding user to docker group...${NC}"
sudo usermod -aG docker $USER
echo -e "${GREEN}✅ User added to docker group${NC}"
echo -e "${YELLOW}⚠️  You need to logout and login again for this to take effect${NC}"
echo ""

echo -e "${YELLOW}Step 4: Installing Python and Ansible...${NC}"
if ! command -v ansible &> /dev/null; then
    sudo apt install -y python3 python3-pip
    pip3 install ansible
    echo -e "${GREEN}✅ Python and Ansible installed${NC}"
else
    echo -e "${GREEN}✅ Ansible already installed${NC}"
fi
echo ""

echo -e "${YELLOW}Step 5: Installing additional tools...${NC}"
sudo apt install -y git curl wget htop vim
echo -e "${GREEN}✅ Additional tools installed${NC}"
echo ""

echo -e "${YELLOW}Step 6: Creating project directory...${NC}"
mkdir -p ~/ecocycle-project
cd ~/ecocycle-project
echo -e "${GREEN}✅ Project directory created at ~/ecocycle-project${NC}"
echo ""

echo -e "${YELLOW}Step 7: Creating environment file template...${NC}"
cat > .env << 'EOF'
# Database Configuration
DB_USERNAME=ecocycle
DB_PASSWORD=change-this-password

# JWT Configuration
JWT_SECRET=change-this-jwt-secret

# GitHub Configuration
GITHUB_REPOSITORY_OWNER=mdshah5
IMAGE_TAG=latest
EOF
chmod 600 .env
echo -e "${GREEN}✅ Environment file created (.env)${NC}"
echo -e "${YELLOW}⚠️  Please edit .env and update passwords!${NC}"
echo ""

echo -e "${YELLOW}Step 8: Creating backup directories...${NC}"
mkdir -p ~/ecocycle-project/backups/{marketplace,transactions,users}
echo -e "${GREEN}✅ Backup directories created${NC}"
echo ""

echo "======================================"
echo -e "${GREEN}✅ VM Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Logout and login again (for docker group)"
echo "2. Edit ~/ecocycle-project/.env with secure passwords"
echo "3. Setup GitHub Container Registry login:"
echo "   echo 'YOUR_PAT' | docker login ghcr.io -u mdshah5 --password-stdin"
echo "4. Test docker: docker run hello-world"
echo ""
echo "Installed versions:"
docker --version 2>/dev/null || echo "Docker: Not accessible yet (logout required)"
docker-compose --version 2>/dev/null || echo "Docker Compose: Not accessible yet (logout required)"
ansible --version 2>/dev/null | head -1 || echo "Ansible: Not found"
python3 --version


#!/bin/bash
# Setup script for VM - Run this ON THE VM

echo "🖥️  Setting up EcoCycle VM Environment"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run as root${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y
echo -e "${GREEN}✅ System updated${NC}"
echo ""

echo -e "${YELLOW}Step 2: Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    sudo apt install -y docker.io docker-compose
    sudo systemctl start docker
    sudo systemctl enable docker
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo -e "${GREEN}✅ Docker already installed${NC}"
fi
echo ""

echo -e "${YELLOW}Step 3: Adding user to docker group...${NC}"
sudo usermod -aG docker $USER
echo -e "${GREEN}✅ User added to docker group${NC}"
echo -e "${YELLOW}⚠️  You need to logout and login again for this to take effect${NC}"
echo ""

echo -e "${YELLOW}Step 4: Installing Python and Ansible...${NC}"
if ! command -v ansible &> /dev/null; then
    sudo apt install -y python3 python3-pip
    pip3 install ansible
    echo -e "${GREEN}✅ Python and Ansible installed${NC}"
else
    echo -e "${GREEN}✅ Ansible already installed${NC}"
fi
echo ""

echo -e "${YELLOW}Step 5: Installing additional tools...${NC}"
sudo apt install -y git curl wget htop vim
echo -e "${GREEN}✅ Additional tools installed${NC}"
echo ""

echo -e "${YELLOW}Step 6: Creating project directory...${NC}"
mkdir -p ~/ecocycle-project
cd ~/ecocycle-project
echo -e "${GREEN}✅ Project directory created at ~/ecocycle-project${NC}"
echo ""

echo -e "${YELLOW}Step 7: Creating environment file template...${NC}"
cat > .env << 'EOF'
# Database Configuration
DB_USERNAME=ecocycle
DB_PASSWORD=change-this-password

# JWT Configuration
JWT_SECRET=change-this-jwt-secret

# GitHub Configuration
GITHUB_REPOSITORY_OWNER=mdshah5
IMAGE_TAG=latest
EOF
chmod 600 .env
echo -e "${GREEN}✅ Environment file created (.env)${NC}"
echo -e "${YELLOW}⚠️  Please edit .env and update passwords!${NC}"
echo ""

echo -e "${YELLOW}Step 8: Creating backup directories...${NC}"
mkdir -p ~/ecocycle-project/backups/{marketplace,transactions,users}
echo -e "${GREEN}✅ Backup directories created${NC}"
echo ""

echo "======================================"
echo -e "${GREEN}✅ VM Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Logout and login again (for docker group)"
echo "2. Edit ~/ecocycle-project/.env with secure passwords"
echo "3. Setup GitHub Container Registry login:"
echo "   echo 'YOUR_PAT' | docker login ghcr.io -u mdshah5 --password-stdin"
echo "4. Test docker: docker run hello-world"
echo ""
echo "Installed versions:"
docker --version 2>/dev/null || echo "Docker: Not accessible yet (logout required)"
docker-compose --version 2>/dev/null || echo "Docker Compose: Not accessible yet (logout required)"
ansible --version 2>/dev/null | head -1 || echo "Ansible: Not found"
python3 --version

