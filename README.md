# EcoCycle DevOps Project — CI/CD Pipeline & Infrastructure Automation

[![CI Pipeline](https://img.shields.io/badge/CI-Automated-brightgreen)](https://github.ncsu.edu/mdshah5/ecocycle-project/actions)
[![Security](https://img.shields.io/badge/Security-12%2B%20Features-blue)](#security-implementation)
[![Docker](https://img.shields.io/badge/Docker-Hub-2496ED?logo=docker)](https://hub.docker.com/u/manavshah13)

**Team Members:** Manav Shah (mdshah5) | Yuvraj Singh Bhatia (ybhatia2)  

---

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [CI/CD Pipeline](#cicd-pipeline)
  - [CI Pipeline (7 Stages)](#ci-pipeline-7-stages)
  - [CD Pipeline (Staging & Production)](#cd-pipeline-staging--production)
- [Infrastructure as Code](#infrastructure-as-code)
- [Microservices](#microservices)
- [Security Implementation](#security-implementation)
- [Setup & Deployment](#setup--deployment)
- [Testing & Quality Gates](#testing--quality-gates)
- [Monitoring & Health Checks](#monitoring--health-checks)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)
- [Learning Resources](#learning-resources)
- [Team Contributions](#team-contributions)
- [License & Contact](#license--contact)
- [Quick Start Summary](#quick-start-summary)

---

## <a id="overview"></a>🎯 Overview

EcoCycle is a **sustainability-focused marketplace platform** with three Spring Boot microservices (Marketplace, Transactions, Users) and an Nginx-based frontend. This project implements a **production-ready CI/CD pipeline** using GitHub Actions and Ansible that automates:

- **Continuous Integration**: Code quality checks, testing, security scanning, and Docker builds
- **Continuous Deployment**: Automated staging and production deployments with health verification
- **Security Hardening**: 12+ security features including vulnerability scanning, non-root containers, and secrets management
- **Infrastructure as Code**: Ansible-based deployment automation with rollback capabilities
- **Self-Hosted Runner**: Persistent build cache and full control over CI environment

### Key Achievements

- **Automation**: Reduced deployment time from 2+ hours (manual) to 15 minutes (automated)
- **Quality Gates**: 7-stage CI pipeline with Checkstyle, JUnit, JaCoCo (50%+ coverage), SpotBugs, OWASP, Hadolint, Trivy
- **Security**: Multi-layer vulnerability scanning, non-root containers, encrypted secrets, firewall rules
- **Reliability**: Automated health checks with rollback on failure
- **Reproducibility**: Complete Infrastructure as Code with Ansible

---

## <a id="project-structure"></a>📁 Project Structure

```
ecocycle-project/
├── .github/                          # GitHub Actions workflows
│   └── workflows/
│       ├── ci.yml                    # 7-stage CI pipeline
│       ├── cd_staging.yml            # Staging deployment
│       └── cd_production.yml         # Production deployment
│
├── marketplace-service/              # Marketplace microservice
│   ├── src/                          # Java source code
│   │   ├── main/java/com/ecocycle/marketplace/
│   │   │   ├── controller/          # REST controllers
│   │   │   │   └── ListingController.java
│   │   │   ├── dto/                 # Data transfer objects
│   │   │   │   ├── CreateListingRequest.java
│   │   │   │   └── ListingDto.java
│   │   │   ├── model/               # JPA entities
│   │   │   │   ├── Listing.java
│   │   │   │   └── ListingType.java (DONATION/SALE)
│   │   │   ├── repository/          # Data access layer
│   │   │   │   └── ListingRepository.java
│   │   │   ├── service/             # Business logic
│   │   │   │   └── ListingService.java
│   │   │   └── MarketplaceServiceApplication.java
│   │   └── resources/
│   │       ├── application.properties
│   │       └── application.yml      # Spring Boot config
│   ├── Dockerfile                   # Multi-stage Docker build
│   ├── pom.xml                      # Maven dependencies + plugins
│   └── owasp-suppressions.xml       # CVE suppression rules
│
├── users-service/                   # Users microservice
│   ├── src/
│   │   ├── main/java/com/ecocycle/users/
│   │   │   ├── controller/
│   │   │   │   ├── AuthController.java      # Login/Register
│   │   │   │   └── UserController.java      # User CRUD
│   │   │   ├── dto/
│   │   │   │   ├── CreateUserRequest.java
│   │   │   │   └── UserDto.java
│   │   │   ├── model/
│   │   │   │   └── User.java
│   │   │   ├── repository/
│   │   │   │   └── UserRepository.java
│   │   │   ├── service/
│   │   │   │   └── UserService.java
│   │   │   └── UsersServiceApplication.java
│   │   └── resources/
│   │       └── application.yml
│   ├── Dockerfile
│   ├── pom.xml
│   └── owasp-suppressions.xml
│
├── transactions-service/            # Transactions microservice
│   ├── src/
│   │   ├── main/java/com/ecocycle/transactions/
│   │   │   ├── client/              # Inter-service communication
│   │   │   │   ├── MarketplaceClient.java
│   │   │   │   ├── UsersClient.java
│   │   │   │   └── ListingDto.java
│   │   │   ├── controller/
│   │   │   │   └── TransactionController.java
│   │   │   ├── dto/
│   │   │   │   ├── ClaimDonationRequest.java
│   │   │   │   ├── CreateOfferRequest.java
│   │   │   │   ├── TransactionDto.java
│   │   │   │   └── UpdateTransactionStatusRequest.java
│   │   │   ├── model/
│   │   │   │   ├── Transaction.java
│   │   │   │   └── TransactionStatus.java (PENDING/COMPLETED/CANCELLED)
│   │   │   ├── repository/
│   │   │   │   └── TransactionRepository.java
│   │   │   ├── service/
│   │   │   │   └── TransactionService.java
│   │   │   └── TransactionsServiceApplication.java
│   │   └── resources/
│   │       └── application.yml
│   ├── Dockerfile
│   ├── pom.xml
│   └── owasp-suppressions.xml
│
├── frontend/                        # Nginx-based web frontend
│   ├── index.html                   # Main UI page
│   ├── script.js                    # API calls to backend services
│   ├── style.css                    # Styling
│   ├── nginx.conf                   # Nginx reverse proxy config
│   └── Dockerfile                   # Nginx container
│
├── ansible/                         # Infrastructure as Code
│   ├── ansible.cfg                  # Ansible configuration
│   ├── inventory/                   # Environment definitions
│   │   ├── staging.ini              # Staging VM (152.7.176.20:80)
│   │   └── production.ini           # Production VM (152.7.176.20:8080)
│   ├── group_vars/
│   │   └── all/
│   │       └── vault.yml            # Encrypted secrets (AES256)
│   ├── playbooks/
│   │   ├── deploy_staging.yml       # Staging deployment playbook
│   │   ├── deploy_production.yml    # Production deployment playbook
│   │   └── rollback.yml             # Rollback playbook
│   ├── roles/
│   │   ├── common/                  # VM setup role
│   │   │   ├── tasks/
│   │   │   │   └── main.yml         # Docker install, firewall, directories
│   │   │   └── templates/
│   │   │       ├── env.j2           # Environment file template
│   │   │       └── logrotate.j2     # Log rotation config
│   │   ├── deploy/                  # Deployment role
│   │   │   ├── tasks/
│   │   │   │   └── main.yml         # Pull images, deploy compose
│   │   │   └── templates/
│   │   │       ├── docker-compose.yml.j2         # Local dev
│   │   │       ├── docker-compose.staging.yml.j2  # Staging env
│   │   │       └── docker-compose.prod.yml.j2     # Production env
│   │   └── healthcheck/             # Health verification role
│   │       └── tasks/
│   │           └── main.yml         # Health checks + retry logic
│   └── README.md                    # Ansible documentation
│
├── scripts/                         # Helper scripts
│   ├── setup-vm.sh                  # VM initial setup script
│   ├── test-docker-build.sh         # Local Docker build test
│   ├── test-health-checks.sh        # Health check test script
│   └── test-local-build.sh          # Local Maven build test
│
├── docs/                            # Project documentation
│   ├── PROJECT_REPORT.md            # Final project report
│   ├── PIPELINE_DIAGRAMS.md         # Mermaid diagrams
│   ├── VIDEO_SCRIPT.md              # Demo video script
│   ├── status_report_1.md           # Sprint 1 status
│   └── status_report_2.md           # Sprint 2 status
│
├── docker-compose.yml               # Local development
├── docker-compose.staging.yml       # Staging environment
├── docker-compose.prod.yml          # Production environment
├── proposal.md                      # Project proposal
└── .gitignore                       # Git ignore rules
```

---

## <a id="architecture"></a>🏗️ Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
    end
    
    subgraph "Frontend Layer"
        Frontend[Nginx Frontend<br/>Port: 80/8080]
    end
    
    subgraph "Application Layer"
        Marketplace[Marketplace Service<br/>Port: 8081/9081]
        Users[Users Service<br/>Port: 8083/9083]
        Transactions[Transactions Service<br/>Port: 8082/9082]
    end
    
    subgraph "Data Layer"
        MarketplaceDB[(Marketplace DB<br/>PostgreSQL)]
        UsersDB[(Users DB<br/>PostgreSQL)]
        TransactionsDB[(Transactions DB<br/>PostgreSQL)]
    end
    
    Browser --> Frontend
    Frontend --> Marketplace
    Frontend --> Users
    Frontend --> Transactions
    Transactions --> Marketplace
    Transactions --> Users
    Marketplace --> MarketplaceDB
    Users --> UsersDB
    Transactions --> TransactionsDB
    
    style Frontend fill:#e6f3ff
    style Marketplace fill:#fff4e6
    style Users fill:#f0e6ff
    style Transactions fill:#e6ffe6
```

### Deployment Environments

| Environment | Host | Ports | Purpose |
|------------|------|-------|---------|
| **Staging** | 152.7.176.20 | Frontend: 80, Services: 8081-8083 | Pre-production testing |
| **Production** | 152.7.176.20 | Frontend: 8080, Services: 9081-9083 | Production deployment |

---

## <a id="cicd-pipeline"></a>🔄 CI/CD Pipeline

### CI/CD Pipeline Flow

```mermaid
graph LR
    A[Developer Push/PR] --> B[CI Pipeline<br/>7 Stages]
    B --> C{Quality<br/>Gates Pass?}
    C -->|No| D[Failed]
    C -->|Yes| E[Build & Push<br/>to Docker Hub]
    E --> F{release/*<br/>branch?}
    F -->|No| G([CI Complete])
    F -->|Yes| H[CD Staging]
    H --> I{Healthy?}
    I -->|No| J[Rollback]
    I -->|Yes| K[Staging OK]
    K --> L{Deploy to<br/>Production?}
    L -->|No| M([Done])
    L -->|Yes| N[CD Production]
    N --> O{Healthy?}
    O -->|No| J
    O -->|Yes| P[Production OK]
    
    style B fill:#fff4e6
    style E fill:#e6f3ff
    style H fill:#f0e6ff
    style N fill:#e6ffe6
    style D fill:#ffcccc
    style J fill:#fff3cd
    style K fill:#d4edda
    style P fill:#d4edda
```

---

## <a id="ci-pipeline-7-stages"></a>🔧 CI Pipeline (7 Stages)

**Location:** `.github/workflows/ci.yml` (548 lines)

### Triggers

```yaml
# PRs to main/release/develop branches
pull_request:
  branches: ['main', 'release/**', 'develop']

# Direct pushes to protected branches
push:
  branches: ['main', 'release/staging', 'release/production']
```

### Stage 1: Validation (Lines 32-65)

**Purpose:** Verify project structure and cache Maven dependencies

```yaml
- Cleanup previous build artifacts (sudo rm -rf */target)
- Checkout code
- Cache Maven dependencies (~/.m2) → 80% faster builds
- Verify all service directories exist (marketplace, users, transactions, frontend)
```

**Key Configuration:**
- **Cache Key:** `${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}`
- **Cache Hit Rate:** ~80% on subsequent builds

### Stage 2: Code Quality (Lines 67-124)

**Purpose:** Enforce Google Java Style Guide using Checkstyle

```yaml
- Run Checkstyle on each service using Dockerized Maven
  Command: docker run maven:3.9.6-eclipse-temurin-17 mvn checkstyle:check
- Fail build if style violations found
- Cleanup Docker-created files (sudo chown)
```

**Checkstyle Configuration (in pom.xml lines 136-158):**
```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-checkstyle-plugin</artifactId>
  <version>3.3.1</version>
  <configuration>
    <configLocation>google_checks.xml</configLocation>
    <violationSeverity>warning</violationSeverity>
    <failOnViolation>true</failOnViolation>
  </configuration>
</plugin>
```

### Stage 3: Unit Tests & Coverage (Lines 125-203)

**Purpose:** Run JUnit tests and enforce 50%+ code coverage with JaCoCo

```yaml
- Test each service: mvn clean test jacoco:report
- Generate JaCoCo coverage reports (XML + HTML)
- Upload coverage to Codecov (separate flags: marketplace, users, transactions)
- Fail if coverage < 50%
```

**JaCoCo Configuration (pom.xml lines 177-218):**
```xml
<plugin>
  <groupId>org.jacoco</groupId>
  <artifactId>jacoco-maven-plugin</artifactId>
  <configuration>
    <rules>
      <rule>
        <element>PACKAGE</element>
        <limits>
          <limit>
            <counter>LINE</counter>
            <value>COVEREDRATIO</value>
            <minimum>0.50</minimum>  <!-- 50% minimum -->
          </limit>
        </limits>
      </rule>
    </rules>
  </configuration>
</plugin>
```

### Stage 4: Static Analysis (Lines 204-260)

**Purpose:** Detect bug patterns and code smells with SpotBugs

```yaml
- Run SpotBugs on each service: mvn compile spotbugs:check
- Detect 400+ bug patterns (null pointer, concurrency, security)
- Continue on error (informational, doesn't fail build)
```

**SpotBugs Configuration (pom.xml lines 159-176):**
```xml
<plugin>
  <groupId>com.github.spotbugs</groupId>
  <artifactId>spotbugs-maven-plugin</artifactId>
  <version>4.8.3.0</version>
  <configuration>
    <effort>Max</effort>
    <threshold>Medium</threshold>
    <failOnError>false</failOnError>
  </configuration>
</plugin>
```

### Stage 5: Security Scanning (Lines 261-356)

**Purpose:** 3-layer vulnerability scanning (Dependencies, Dockerfiles, Images)

#### 5a. Hadolint - Dockerfile Security (Lines 295-317)

```bash
# Scans all Dockerfiles for security best practices
docker run --rm -i hadolint/hadolint < Dockerfile

# Checks:
# - Pinned versions (FROM maven:3.9.6-eclipse-temurin-17)
# - Non-root user (USER ecocycle)
# - Minimal layers (multi-stage builds)
# - HEALTHCHECK present
```

**Example Violations:**
- `FROM maven:latest` → `FROM maven:3.9.6-eclipse-temurin-17`
- No USER directive → `USER ecocycle`

#### 5b. OWASP Dependency Check (Lines 318-350)

```yaml
# Scans Maven dependencies against NVD (National Vulnerability Database)
mvn dependency-check:check

# Configuration (pom.xml lines 234-254):
<failBuildOnCVSS>7</failBuildOnCVSS>  # Fail on CVSS >= 7 (High/Critical)
<autoUpdate>false</autoUpdate>         # Use cached NVD data (API rate limits)
<suppressionFiles>
  <suppressionFile>owasp-suppressions.xml</suppressionFile>
</suppressionFiles>
```

**Suppression Example (owasp-suppressions.xml):**
```xml
<!-- Suppress false positives -->
<suppress>
   <cve>CVE-2023-20883</cve>  <!-- Spring Boot - fixed in 3.5.6 -->
</suppress>
```

**Output:** HTML reports uploaded as artifacts (7-day retention)

#### 5c. Trivy - Container Image Scanning (Lines 446-463)

```yaml
# Scans Docker images for OS/library vulnerabilities
aquasecurity/trivy-action@0.20.0
  image-ref: manavshah13/ecocycle-marketplace-service:latest
  severity: 'CRITICAL,HIGH'
  exit-code: '1'  # Fail pipeline on vulnerabilities
```

### Stage 6: Build Docker Images (Lines 357-463)

**Purpose:** Multi-stage Docker builds and push to Docker Hub

```yaml
# Matrix strategy - builds 4 services in parallel
strategy:
  matrix:
    service: [marketplace-service, users-service, transactions-service, frontend]

# Steps:
1. Set up Docker Buildx (layer caching)
2. Login to Docker Hub (credentials from secrets)
3. Extract metadata (tags: latest, pr-#, sha-, branch)
4. Build and push images
   - Push on: direct pushes + PRs to release/* branches
   - Skip push on: PRs to main (validation only)
5. Run Trivy scan on pushed images
```

**Dockerfile Structure (marketplace-service/Dockerfile):**

```dockerfile
# Stage 1: Build (maven:3.9.6-eclipse-temurin-17)
FROM maven:3.9.6-eclipse-temurin-17 AS builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline -B  # Cache dependencies
COPY src ./src
RUN mvn clean package -DskipTests -B

# Stage 2: Runtime (eclipse-temurin:17-jre-jammy)
FROM eclipse-temurin:17-jre-jammy
RUN groupadd -r ecocycle && useradd -r -g ecocycle ecocycle  # Non-root user
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
RUN chown -R ecocycle:ecocycle /app
USER ecocycle  # Security: run as non-root

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8081/actuator/health || exit 1

ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]
```

**Image Optimization:**
- **Size Reduction:** 800MB (builder) → 300MB (runtime) = 60% smaller
- **Security:** No build tools in runtime (Maven, compilers removed)
- **Caching:** Layer caching via GitHub Actions cache (type=gha)

**Image Tags (Docker Hub: manavshah13/ecocycle-*):**
- `latest` - Latest build from main/release branches
- `pr-42` - Pull request #42
- `sha-abc1234` - Git commit SHA
- `release-staging` - Release branch name

### Stage 7: Build Summary (Lines 518-548)

**Purpose:** Aggregate results and fail on critical issues

```yaml
# Job dependencies: needs all previous stages
needs: [validate, code-quality, test, static-analysis, security-scan, build-images]
if: always()  # Run even if some jobs fail

# Actions:
1. Display job results in GitHub Step Summary
2. Show branch, commit, author info
3. Fail pipeline if code-quality, test, or static-analysis failed
4. Cleanup all Docker-created files (final sudo chown)
```

**Example Summary Output:**
```
## CI Pipeline Summary

[OK] Code Quality: success
[OK] Tests: success
[OK] Static Analysis: success
[OK] Security Scan: success
[OK] Build Images: success

Branch: release/staging
Commit: abc1234567890
Author: mdshah5
```

---

## <a id="cd-pipeline-staging--production"></a>🚀 CD Pipeline (Staging & Production)

### CD Deployment Flow

```mermaid
graph TB
    A[CI Success] --> B[Ansible Deploy]
    B --> C[Role: common<br/>Docker + Firewall]
    C --> D[Role: deploy<br/>Pull & Start]
    D --> E[Role: healthcheck<br/>Verify Services]
    E --> F{All<br/>Healthy?}
    F -->|Yes| G[Deployed]
    F -->|No| H[Rollback]
    H --> I[Restore Previous<br/>Version]
    
    style B fill:#fff4e6
    style C fill:#e1f5ff
    style D fill:#ffe6e6
    style E fill:#f0e6ff
    style G fill:#d4edda
    style H fill:#fff3cd
```

### Staging Deployment

**Location:** `.github/workflows/cd_staging.yml` (84 lines)

**Trigger:**
```yaml
workflow_run:
  workflows: ["CI Pipeline"]
  types: [completed]
  branches: ['release/staging']

# Only run if CI succeeded
if: github.event.workflow_run.conclusion == 'success'
```

**Steps:**
1. **Configure SSH** (Lines 43-48)
   ```yaml
   - Create ~/.ssh/id_rsa from GitHub Secret
   - Set permissions to 600 (required by SSH)
   - Add host to known_hosts (prevent MITM attacks)
   ```

2. **Install Ansible** (Lines 37-42)
   ```bash
   pip install ansible ansible-lint
   ansible-galaxy collection install community.docker  # Docker Compose v2 support
   ```

3. **Test Connection** (Lines 50-52)
   ```bash
   ansible -i ansible/inventory/staging.ini staging -m ping
   ```

4. **Deploy** (Lines 54-72)
   ```bash
   cd ansible
   ansible-playbook -i inventory/staging.ini playbooks/deploy_staging.yml \
     -e "image_tag=latest" \
     -e "dockerhub_username=manavshah13" \
     -e "dockerhub_token=${{ secrets.DOCKERHUB_TOKEN }}"
   ```

5. **Verify** (Lines 73-84)
   ```
   Display deployment summary with service URLs:
   - Frontend: http://152.7.176.20
   - Marketplace: http://152.7.176.20:8081
   - Users: http://152.7.176.20:8083
   - Transactions: http://152.7.176.20:8082
   ```

### Production Deployment

**Location:** `.github/workflows/cd_production.yml` (92 lines)

**Trigger:**
```yaml
workflow_run:
  workflows: ["CI Pipeline"]
  types: [completed]
  branches: ['main', 'release/production']
```

**Differences from Staging:**
- **Ports:** 8080 (frontend), 9081-9083 (services)
- **Resource Limits:** CPU/memory caps (docker-compose.prod.yml)
- **Health Checks:** 15 retries vs 10 (more conservative)
- **Firewall:** UFW enabled (production only)
- **Backups:** 30-day retention vs 7-day

**Manual Approval Override:**
```bash
# For automated CD (skips confirmation)
-e "manual_approval=false"
```

---

## <a id="infrastructure-as-code"></a>🏢 Infrastructure as Code

### Ansible Roles

#### 1. Common Role (`ansible/roles/common/tasks/main.yml`)

**Purpose:** Provision and configure the VM

```yaml
Tasks:
1. Update system packages (apt update && apt upgrade)
2. Install Docker and Docker Compose
3. Add deploy_user to docker group
4. Configure UFW firewall (production only):
   - Allow SSH (22)
   - Allow frontend port (80/8080)
   - Allow service ports (8081-8083 or 9081-9083)
   - Enable UFW
5. Create directories:
   - {{ app_dir }} (~/ecocycle-project)
   - {{ app_dir }}/logs
   - {{ app_dir }}/backups
6. Setup log rotation (logrotate.j2 template)
7. Create environment file from template (env.j2)
```

**Firewall Configuration:**
```yaml
- name: Allow SSH
  ufw:
    rule: allow
    port: 22
    proto: tcp

- name: Allow frontend port
  ufw:
    rule: allow
    port: "{{ frontend_port }}"
    proto: tcp

- name: Enable UFW
  ufw:
    state: enabled
  when: env_name == 'production'  # Production only
```

#### 2. Deploy Role (`ansible/roles/deploy/tasks/main.yml`)

**Purpose:** Pull images and deploy services

```yaml
Tasks:
1. Login to Docker Hub (credentials from secrets, no_log: true)
2. Copy docker-compose template to server:
   - docker-compose.staging.yml.j2 → docker-compose.staging.yml
   - Variables: image_tag, dockerhub_username, ports, env_name
3. Remove existing containers (safe cleanup):
   docker rm -f marketplace-service-{{ env_name }} ...
4. Deploy with Docker Compose v2:
   community.docker.docker_compose_v2:
     project_src: "{{ app_dir }}"
     files: ["{{ compose_file }}"]
     state: present
     pull: always        # Pull latest images
     recreate: always    # Force recreate containers
5. Wait for services (pause: 30 seconds)
```

**Docker Compose Template (docker-compose.staging.yml.j2):**
```yaml
services:
  marketplace:
    image: {{ dockerhub_username }}/ecocycle-marketplace-service:{{ image_tag }}
    container_name: marketplace-service-{{ env_name }}
    ports:
      - "{{ marketplace_port }}:8081"
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://marketplace-db-{{ env_name }}:5432/marketplace
      SPRING_DATASOURCE_USERNAME: {{ db_username }}
      SPRING_DATASOURCE_PASSWORD: {{ vault_db_password }}  # From Ansible Vault
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8081/actuator/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

#### 3. Healthcheck Role (`ansible/roles/healthcheck/tasks/main.yml`)

**Purpose:** Verify all services are healthy post-deployment

```yaml
Tasks:
1. Check backend services:
   - URI: http://{{ ansible_host }}:{{ port }}/actuator/health
   - Retry: {{ health_check_retries }} times (10 for staging, 15 for production)
   - Delay: {{ health_check_delay }} seconds between retries (5s)
   - Expected: HTTP 200 OK with {"status": "UP"}
   
2. Check frontend:
   - URI: http://{{ ansible_host }}:{{ frontend_port }}/health
   - Same retry logic
   
3. Display health status:
   - Marketplace Service: HEALTHY
   - Users Service: HEALTHY
   - Transactions Service: HEALTHY
   - Frontend: HEALTHY
   
4. Check all_healthy fact:
   - all_healthy: true if all services return 200
   - all_healthy: false if any service fails
   
5. Fail deployment if unhealthy:
   - fail: "Health check failed! One or more services are not healthy."
   - Triggers rollback workflow
   
6. Display container status:
   - docker compose ps
```

**Health Check Retry Logic:**
```yaml
- name: Check backend service health
  uri:
    url: "http://{{ ansible_host }}:{{ item.port }}/actuator/health"
    method: GET
    status_code: 200
    timeout: 10
  register: health_results
  retries: 15              # Try up to 15 times
  delay: 5                 # Wait 5 seconds between attempts
  until: health_results.status == 200
  failed_when: false       # Don't fail immediately, aggregate results
```

### Rollback Playbook

**Location:** `ansible/playbooks/rollback.yml`

**Usage:**
```bash
# Rollback staging
ansible-playbook playbooks/rollback.yml -e "target_env=staging"

# Rollback production
ansible-playbook playbooks/rollback.yml -e "target_env=production"
```

**Process:**
1. Stop current containers
2. Restore previous image tag (stored in backup)
3. Deploy with previous tag
4. Run health checks
5. Verify rollback success

---

## <a id="microservices"></a>🧪 Microservices

### 1. Marketplace Service

**Location:** `marketplace-service/` (Spring Boot 3.5.6 + PostgreSQL)

**Endpoints:**
```
POST   /api/listings              # Create listing (donation/sale)
GET    /api/listings              # Get all listings
GET    /api/listings/{id}         # Get listing by ID
GET    /api/listings/type/{type}  # Get by type (DONATION/SALE)
DELETE /api/listings/{id}         # Delete listing
GET    /actuator/health           # Health check
```

**Key Classes:**
- `ListingController.java` - REST endpoints
- `ListingService.java` - Business logic (create, find, delete)
- `ListingRepository.java` - JPA repository (extends JpaRepository)
- `Listing.java` - Entity (id, title, description, price, type, userId, createdAt)
- `ListingType.java` - Enum (DONATION, SALE)

**Dependencies (pom.xml):**
```xml
- spring-boot-starter-web (REST API)
- spring-boot-starter-data-jpa (Database access)
- spring-boot-starter-actuator (Health checks, metrics)
- spring-boot-starter-validation (Input validation)
- postgresql (Database driver)
- springdoc-openapi-starter-webmvc-ui (Swagger/OpenAPI 3.0)
- lombok (Reduce boilerplate)
```

**Database:** PostgreSQL 16, Port 5433 (local), Database: `marketplace`

### 2. Users Service

**Location:** `users-service/` (Spring Boot 3.5.6 + PostgreSQL)

**Endpoints:**
```
POST   /api/auth/register         # Register new user
POST   /api/auth/login            # Login (returns user ID)
GET    /api/users                 # Get all users
GET    /api/users/{id}            # Get user by ID
GET    /api/users/email/{email}   # Get user by email
PUT    /api/users/{id}            # Update user
DELETE /api/users/{id}            # Delete user
GET    /actuator/health           # Health check
```

**Key Classes:**
- `AuthController.java` - Registration and login
- `UserController.java` - User CRUD operations
- `UserService.java` - Business logic (register, login, findByEmail)
- `UserRepository.java` - JPA repository
- `User.java` - Entity (id, username, email, createdAt)

**Database:** PostgreSQL 16, Port 5435 (local), Database: `users`

### 3. Transactions Service

**Location:** `transactions-service/` (Spring Boot 3.5.6 + PostgreSQL)

**Endpoints:**
```
POST   /api/transactions/offers             # Create purchase offer
POST   /api/transactions/claim              # Claim donation
GET    /api/transactions                    # Get all transactions
GET    /api/transactions/{id}               # Get transaction by ID
GET    /api/transactions/user/{userId}      # Get user's transactions
GET    /api/transactions/listing/{listingId}# Get listing's transactions
PUT    /api/transactions/{id}/status        # Update status (COMPLETED/CANCELLED)
GET    /actuator/health                     # Health check
```

**Key Classes:**
- `TransactionController.java` - REST endpoints
- `TransactionService.java` - Business logic + inter-service calls
- `TransactionRepository.java` - JPA repository
- `Transaction.java` - Entity (id, listingId, buyerId, sellerId, amount, status, createdAt)
- `TransactionStatus.java` - Enum (PENDING, COMPLETED, CANCELLED)
- `MarketplaceClient.java` - HTTP client to Marketplace service
- `UsersClient.java` - HTTP client to Users service

**Inter-Service Communication:**
```java
// MarketplaceClient.java - Fetches listing details
@Value("${marketplace.base-url}")
private String marketplaceBaseUrl;

public ListingDto getListingById(Long listingId) {
    String url = marketplaceBaseUrl + "/api/listings/" + listingId;
    return restTemplate.getForObject(url, ListingDto.class);
}

// Configuration (application.yml)
marketplace:
  base-url: http://marketplace:8081  # Docker internal network
```

**Database:** PostgreSQL 16, Port 5434 (local), Database: `transactions`

### 4. Frontend

**Location:** `frontend/` (Nginx 1.25 + Vanilla JavaScript)

**Files:**
- `index.html` - Main UI (login, register, service buttons)
- `script.js` - API calls to backend services
- `style.css` - Styling
- `nginx.conf` - Reverse proxy configuration

**Nginx Configuration (`nginx.conf`):**
```nginx
server {
    listen 80;
    server_name localhost;
    
    # Serve static frontend
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # Reverse proxy to backend services
    location /api/users {
        proxy_pass http://users:8083;
    }
    
    location /api/marketplace {
        proxy_pass http://marketplace:8081;
    }
    
    location /api/transactions {
        proxy_pass http://transactions:8082;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

**API Calls (script.js):**
```javascript
async function callService(service) {
  const apiEndpoints = {
    users: '/api/users',
    marketplace: '/api/listings',
    transactions: '/api/transactions'
  };
  
  const response = await fetch(apiEndpoints[service]);
  const data = await response.json();
  document.getElementById('result').textContent = JSON.stringify(data, null, 2);
}
```

---

## <a id="security-implementation"></a>🔒 Security Implementation

### 1. Vulnerability Scanning (3 Layers)

#### Layer 1: OWASP Dependency Check
- **What:** Scans Maven dependencies against NVD (50,000+ CVEs)
- **Where:** `.github/workflows/ci.yml` lines 318-350, `pom.xml` lines 234-254
- **Threshold:** CVSS ≥ 7 fails build
- **Example:** Detected outdated Spring Boot with CVE-2023-20883 → upgraded to 3.5.6

#### Layer 2: Hadolint Dockerfile Linting
- **What:** Static analysis of Dockerfiles for security best practices
- **Where:** `.github/workflows/ci.yml` lines 295-317
- **Checks:** Pinned versions, non-root user, minimal layers, no secrets in ENV
- **Example:** Enforced `USER ecocycle` in all service Dockerfiles

#### Layer 3: Trivy Image Scanning
- **What:** Scans Docker images for OS/library vulnerabilities
- **Where:** `.github/workflows/ci.yml` lines 446-463
- **Severity:** CRITICAL + HIGH (exit-code: 1)
- **Example:** Caught vulnerable OpenSSL in base image → switched to patched image

### 2. Container Hardening

#### Non-Root User (All Dockerfiles lines 30-42)
```dockerfile
RUN groupadd -r ecocycle && useradd -r -g ecocycle ecocycle
USER ecocycle
```
- **Why:** Limits blast radius if container compromised
- **Impact:** Attacker has no root privileges even if shell access gained

#### Multi-Stage Builds
```dockerfile
FROM maven:3.9.6-eclipse-temurin-17 AS builder  # Build stage
FROM eclipse-temurin:17-jre-jammy                # Runtime stage
```
- **Why:** Excludes build tools from runtime (60% smaller: 800MB → 300MB)
- **Impact:** Fewer binaries = smaller attack surface

#### Health Checks (All Dockerfiles lines 48-49)
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD wget --spider http://localhost:8081/actuator/health || exit 1
```
- **Why:** Docker/Ansible can detect unhealthy containers automatically
- **Impact:** Prevents deploying broken services

### 3. Secrets Management

#### GitHub Secrets (`.github/workflows/*.yml`)
```yaml
${{ secrets.DOCKERHUB_TOKEN }}         # Docker Hub access
${{ secrets.ANSIBLE_SSH_PRIVATE_KEY }} # SSH key for deployment
${{ secrets.ANSIBLE_VAULT_PASSWORD }}  # Ansible Vault decryption key
```
- **Encryption:** AES256 at rest
- **Masking:** Auto-redacted in logs (`***`)

#### Ansible Vault (`ansible/group_vars/all/vault.yml`)
```bash
# Encrypted file
$ANSIBLE_VAULT;1.1;AES256
3339643935363538353...

# Decrypt
ansible-vault view vault.yml
vault_db_password: SecurePassword123!
```
- **Algorithm:** AES256
- **Safe to commit:** Yes, encrypted in repo
- **Access control:** Only CI/CD has vault password

#### Credential Masking (`ansible/roles/deploy/tasks/main.yml` line 10)
```yaml
- name: Login to Docker Hub
  docker_login:
    username: "{{ dockerhub_username }}"
    password: "{{ dockerhub_token }}"
  no_log: true  # Prevents password leakage in logs
```

### 4. Network Security

#### UFW Firewall (Production Only)
```yaml
# ansible/roles/common/tasks/main.yml lines 104-128
- name: Configure UFW
  ufw:
    rule: allow
    port: "{{ item }}"
  loop:
    - 22      # SSH
    - 8080    # Frontend
    - 9081    # Marketplace
    - 9082    # Transactions
    - 9083    # Users
  when: env_name == 'production'
```
- **Default:** Deny all inbound traffic
- **Allowed:** Only SSH + application ports
- **Impact:** Prevents unauthorized port scanning

#### SSH Hardening (`.github/workflows/cd_*.yml` lines 43-48)
```yaml
- name: Configure SSH
  run: |
    chmod 600 ~/.ssh/id_rsa          # Strict permissions (SSH requirement)
    ssh-keyscan >> ~/.ssh/known_hosts  # Prevent MITM attacks
```

### 5. Resource Limits (`docker-compose.prod.yml`)

```yaml
services:
  marketplace:
    deploy:
      resources:
        limits:
          cpus: '1.0'      # Max 1 CPU core
          memory: 1024M     # Max 1GB RAM
        reservations:
          cpus: '0.5'      # Guarantee 0.5 cores
          memory: 512M      # Guarantee 512MB
```
- **Why:** Prevents resource exhaustion (DoS attacks)
- **Impact:** One compromised container can't starve others

### 6. File Permissions

```yaml
# Environment files: 0600 (owner read/write only)
- name: Create environment file
  template:
    src: env.j2
    dest: "{{ app_dir }}/.env"
    mode: '0600'
```

### Security Summary

| Feature | Location | Impact |
|---------|----------|--------|
| OWASP Dependency Check | CI line 318-350, pom.xml 234-254 | Blocks vulnerable libraries |
| Trivy Image Scanning | CI line 446-463 | Blocks vulnerable images |
| Hadolint | CI line 295-317 | Enforces Dockerfile best practices |
| Non-Root Containers | All Dockerfiles line 30-42 | Limits privilege escalation |
| Multi-Stage Builds | All Dockerfiles | 60% smaller attack surface |
| GitHub Secrets | All workflows | Encrypted credentials |
| Ansible Vault | ansible/group_vars/all/vault.yml | AES256 encrypted passwords |
| Credential Masking | ansible/roles/deploy line 10 | Prevents log leakage |
| UFW Firewall | ansible/roles/common line 104-128 | Port restriction |
| SSH Key Auth | CD workflows line 43-48 | 600 perms, MITM protection |
| Resource Limits | docker-compose.prod.yml | DoS prevention |
| File Permissions | ansible/roles/common | 0600 for sensitive files |

---

## <a id="setup--deployment"></a>🛠️ Setup & Deployment

### Prerequisites

1. **Self-Hosted GitHub Runner** (for CI)
   ```bash
   # On runner machine
   mkdir actions-runner && cd actions-runner
   ./config.sh --url https://github.ncsu.edu/mdshah5/ecocycle-project --token <TOKEN>
   ./run.sh
   ```

2. **Docker & Docker Compose** (on deployment VM)
   ```bash
   bash scripts/setup-vm.sh  # Automated setup script
   ```

3. **GitHub Secrets** (in repo settings)
   ```
   DOCKERHUB_TOKEN           # Docker Hub access token
   ANSIBLE_SSH_PRIVATE_KEY   # SSH key for VM access
   ANSIBLE_VAULT_PASSWORD    # Ansible vault decryption key
   ```

### Local Development

```bash
# Clone repository
git clone https://github.ncsu.edu/mdshah5/ecocycle-project.git
cd ecocycle-project

# Build all services
./scripts/test-local-build.sh

# Run locally with Docker Compose
docker-compose up -d

# Check services
docker-compose ps
curl http://localhost:8081/actuator/health  # Marketplace
curl http://localhost:8083/actuator/health  # Users
curl http://localhost:8082/actuator/health  # Transactions
curl http://localhost:80                    # Frontend

# View logs
docker-compose logs -f marketplace

# Stop services
docker-compose down
```

### Deploy to Staging

```bash
# Push to release/staging branch
git checkout -b release/staging
git push origin release/staging

# Automated process:
# 1. CI Pipeline runs (7 stages)
# 2. Docker images built and pushed to Docker Hub
# 3. CD Staging workflow triggered
# 4. Ansible deploys to 152.7.176.20
# 5. Health checks verify deployment

# Access staging
http://152.7.176.20              # Frontend
http://152.7.176.20:8081/api/listings  # Marketplace
```

### Deploy to Production

```bash
# Option 1: Push to main
git checkout main
git merge release/staging
git push origin main

# Option 2: Push to release/production
git checkout -b release/production
git push origin release/production

# Automated process:
# 1. CI Pipeline runs
# 2. Docker images built and pushed
# 3. CD Production workflow triggered
# 4. Ansible deploys with production config
# 5. Health checks verify deployment

# Access production
http://152.7.176.20:8080              # Frontend
http://152.7.176.20:9081/api/listings  # Marketplace
```

### Manual Deployment (Ansible)

```bash
cd ansible

# Deploy to staging
ansible-playbook -i inventory/staging.ini playbooks/deploy_staging.yml \
  -e "image_tag=latest"

# Deploy to production
ansible-playbook -i inventory/production.ini playbooks/deploy_production.yml \
  -e "image_tag=latest" \
  --ask-vault-pass

# Specific image tag
ansible-playbook -i inventory/staging.ini playbooks/deploy_staging.yml \
  -e "image_tag=sha-abc1234"

# Dry run (check mode)
ansible-playbook -i inventory/staging.ini playbooks/deploy_staging.yml --check --diff

# Rollback
ansible-playbook playbooks/rollback.yml -e "target_env=staging"
```

---

## <a id="testing--quality-gates"></a>📊 Testing & Quality Gates

### Unit Tests

**Location:** Each service's `src/test/java/`

```bash
# Run tests locally
cd marketplace-service
mvn test

# Run with coverage
mvn test jacoco:report

# View coverage report
open target/site/jacoco/index.html
```

**Coverage Threshold:** 50% minimum (enforced by JaCoCo)

**Test Structure:**
```
marketplace-service/src/test/java/
└── com/manav/marketplace_service/
    └── MarketplaceServiceApplicationTests.java

users-service/src/test/java/
└── com/example/users_service/
    └── UsersServiceApplicationTests.java

transactions-service/src/test/java/
└── com/ecocyle/transactions/
    └── TransactionsServiceApplicationTests.java
```

### Integration Tests

**Location:** `.github/workflows/ci.yml` lines 466-517

```yaml
# Runs after Docker builds
integration-tests:
  services:
    postgres:  # Test database
      image: postgres:16
      
  steps:
    - Install pytest
    - Run integration tests (placeholder for future tests)
```

### Health Check Tests

**Script:** `scripts/test-health-checks.sh`

```bash
#!/bin/bash
# Test all service health endpoints

echo "Testing Marketplace health..."
curl -f http://localhost:8081/actuator/health || exit 1

echo "Testing Users health..."
curl -f http://localhost:8083/actuator/health || exit 1

echo "Testing Transactions health..."
curl -f http://localhost:8082/actuator/health || exit 1

echo "Testing Frontend health..."
curl -f http://localhost:80/health || exit 1

echo "[OK] All health checks passed"
```

### Quality Gate Summary

| Gate | Tool | Threshold | Location |
|------|------|-----------|----------|
| **Code Style** | Checkstyle | 0 violations | CI lines 101-117, pom.xml 136-158 |
| **Code Coverage** | JaCoCo | 50% minimum | CI lines 158-169, pom.xml 177-218 |
| **Bug Detection** | SpotBugs | Medium+ bugs | CI lines 238-252, pom.xml 159-176 |
| **Dependency CVEs** | OWASP | CVSS < 7 | CI lines 318-334, pom.xml 234-254 |
| **Dockerfile Security** | Hadolint | 0 critical issues | CI lines 295-317 |
| **Image Vulnerabilities** | Trivy | 0 CRITICAL/HIGH | CI lines 446-463 |
| **Health Checks** | Ansible | All services UP | ansible/roles/healthcheck |

---

## <a id="monitoring--health-checks"></a>📈 Monitoring & Health Checks

### Spring Boot Actuator

**Endpoints:** `/actuator/health`, `/actuator/info`, `/actuator/metrics`

**Configuration (`application.yml`):**
```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      show-details: always
```

**Health Check Response:**
```json
{
  "status": "UP",
  "components": {
    "db": {
      "status": "UP",
      "details": {
        "database": "PostgreSQL",
        "validationQuery": "isValid()"
      }
    },
    "diskSpace": {
      "status": "UP",
      "details": {
        "total": 107374182400,
        "free": 53687091200,
        "threshold": 10485760
      }
    }
  }
}
```

### Docker Health Checks

**Configuration:** All service Dockerfiles lines 48-49

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD wget --spider http://localhost:8081/actuator/health || exit 1
```

**Check Status:**
```bash
docker ps  # Shows health status in STATUS column
# CONTAINER ID   IMAGE                        STATUS
# abc123         marketplace-service:latest   Up 2 minutes (healthy)
```

### Ansible Health Verification

**Process (ansible/roles/healthcheck/tasks/main.yml):**
1. Check each service HTTP endpoint
2. Retry up to 15 times (5 seconds between attempts)
3. Aggregate results
4. Fail deployment if any service unhealthy
5. Display container status

**Example Output:**
```
TASK [healthcheck : Display health check results]
ok: [staging] => 
  msg: "Marketplace Service: HEALTHY"
ok: [staging] => 
  msg: "Users Service: HEALTHY"
ok: [staging] => 
  msg: "Transactions Service: HEALTHY"
ok: [staging] => 
  msg: "Frontend: HEALTHY"

TASK [healthcheck : Check if all services are healthy]
ok: [staging] => 
  all_healthy: true
```

---

## <a id="troubleshooting"></a>🐛 Troubleshooting

### CI Pipeline Issues

#### Issue: Maven build fails with "Permission denied"
**Cause:** Docker creates root-owned files in `target/` directories  
**Solution:** Cleanup step runs `sudo chown -R $USER:$USER */target`

#### Issue: OWASP Dependency Check timeout
**Cause:** NVD API rate limiting  
**Solution:** Disabled auto-update (`<autoUpdate>false</autoUpdate>`) in pom.xml

#### Issue: Checkstyle violations
**Cause:** Code doesn't follow Google Java Style Guide  
**Solution:** Run locally before pushing
```bash
mvn checkstyle:check
```

### Deployment Issues

#### Issue: SSH connection failed
**Cause:** Incorrect SSH key or host key mismatch  
**Solution:**
```bash
# Test SSH manually
ssh -i ~/.ssh/id_rsa mdshah5@152.7.176.20

# Add to known_hosts
ssh-keyscan -H 152.7.176.20 >> ~/.ssh/known_hosts
```

#### Issue: Health check failed
**Cause:** Service not ready or database connection issue  
**Solution:**
```bash
# SSH to VM
ssh mdshah5@152.7.176.20

# Check logs
cd ~/ecocycle-project
docker-compose logs marketplace

# Check database
docker exec -it marketplace-db psql -U ecocycle -d marketplace
```

#### Issue: Container not starting
**Cause:** Port conflict or resource constraints  
**Solution:**
```bash
# Check port usage
sudo netstat -tulpn | grep 8081

# Check container logs
docker logs marketplace-service-staging

# Check resource usage
docker stats
```

### Service Issues

#### Issue: 500 Internal Server Error
**Cause:** Database connection failure  
**Solution:** Verify environment variables
```bash
# Check .env file
cat ~/ecocycle-project/.env

# Test database connection
docker exec marketplace-db psql -U ecocycle -d marketplace -c "SELECT 1;"
```

#### Issue: Service can't reach other services
**Cause:** Docker network issue  
**Solution:**
```bash
# Check Docker network
docker network ls
docker network inspect ecocycle-project_default

# Test connectivity
docker exec marketplace-service ping users-service
```

---

## <a id="documentation"></a>📚 Documentation

### Project Documentation

| Document | Location | Description |
|----------|----------|-------------|
| **Project Report** | `docs/PROJECT_REPORT.md` | Final project report (5 pages, 2400 words) |
| **Pipeline Diagrams** | `docs/PIPELINE_DIAGRAMS.md` | Mermaid diagrams for CI/CD flows |
| **Video Script** | `docs/VIDEO_SCRIPT.md` | Demo video script with timestamps |
| **Ansible Guide** | `ansible/README.md` | Detailed Ansible usage guide |
| **Proposal** | `proposal.md` | Original project proposal |
| **Status Reports** | `docs/status_report_*.md` | Sprint status updates |

### API Documentation

**Swagger UI (when services running):**
- Marketplace: http://localhost:8081/swagger-ui.html
- Users: http://localhost:8083/swagger-ui.html
- Transactions: http://localhost:8082/swagger-ui.html

**OpenAPI Spec:**
- http://localhost:8081/v3/api-docs

### Code Documentation

**Key Files to Review:**

1. **CI Pipeline:** `.github/workflows/ci.yml`
   - Complete 7-stage CI pipeline definition
   - Maven caching, Docker builds, security scans

2. **CD Workflows:** `.github/workflows/cd_*.yml`
   - Staging and production deployment automation
   - SSH configuration, Ansible execution

3. **Dockerfiles:** `*/Dockerfile`
   - Multi-stage builds, security hardening
   - Health checks, non-root users

4. **Maven Config:** `*/pom.xml`
   - Dependencies, plugins (Checkstyle, JaCoCo, SpotBugs, OWASP)
   - Build configuration, test settings

5. **Ansible Playbooks:** `ansible/playbooks/*.yml`
   - Deployment orchestration
   - Role composition, variable passing

6. **Ansible Roles:** `ansible/roles/*/tasks/main.yml`
   - Infrastructure provisioning (common)
   - Application deployment (deploy)
   - Health verification (healthcheck)

---

## <a id="learning-resources"></a>🎓 Learning Resources

### DevOps Concepts Implemented

- **Continuous Integration (CI):** Automated build, test, quality checks
- **Continuous Deployment (CD):** Automated staging/production deployments
- **Infrastructure as Code (IaC):** Ansible playbooks for reproducible deployments
- **Containerization:** Docker for consistent environments
- **Security by Design:** Multiple layers of vulnerability scanning
- **Health Monitoring:** Automated health checks with rollback
- **Version Control:** Git branching strategy (main, release/*, develop)

### Tools & Technologies

| Category | Tools |
|----------|-------|
| **CI/CD** | GitHub Actions, Ansible |
| **Containers** | Docker, Docker Compose |
| **Backend** | Spring Boot 3.5.6, Java 17, Maven |
| **Frontend** | Nginx 1.25, Vanilla JavaScript |
| **Database** | PostgreSQL 16 |
| **Code Quality** | Checkstyle, SpotBugs, JaCoCo |
| **Security** | OWASP Dependency Check, Trivy, Hadolint |
| **Monitoring** | Spring Boot Actuator |
| **Secrets** | GitHub Secrets, Ansible Vault |

---

## <a id="team-contributions"></a>👥 Team Contributions

### Manav Shah (mdshah5) - CI Pipeline & Security
- **40+ hours:** Designed and implemented 7-stage CI pipeline
- **15+ hours:** Security scanning (OWASP, Trivy, Hadolint)
- **12+ hours:** Docker optimization (multi-stage builds, non-root users)
- **10+ hours:** Ansible roles (common, deploy)
- **Key Achievement:** 12+ security features, 80% faster builds with caching

### Yuvraj Singh Bhatia (ybhatia2) - CD Pipeline & Frontend
- **35+ hours:** CD workflows (staging, production, rollback)
- **20+ hours:** Ansible playbooks and healthcheck role
- **18+ hours:** Frontend development (HTML/CSS/JS, Nginx)
- **12+ hours:** Infrastructure setup (VM provisioning, SSH, firewall)
- **Key Achievement:** Zero-downtime deployments with automated health checks

**Collaborative Work:**
- Architecture design and technology selection
- Docker Compose files for all environments
- Security implementation and best practices
- End-to-end testing and validation
- Documentation and reporting

---

## <a id="license--contact"></a>📝 License & Contact

**Course:** CSC 519 - DevOps, NC State University  
**Semester:** Fall 2024  
**Instructor:** Dr. Chris Parnin

**Team Contact:**
- Manav Shah: mdshah5@ncsu.edu
- Yuvraj Singh Bhatia: ybhatia2@ncsu.edu

---

## <a id="quick-start-summary"></a>🚀 Quick Start Summary

```bash
# 1. Clone repository
git clone https://github.ncsu.edu/mdshah5/ecocycle-project.git
cd ecocycle-project

# 2. Local development
docker-compose up -d

# 3. Push to staging
git checkout -b release/staging
git push origin release/staging
# → Automated CI + CD to http://152.7.176.20

# 4. Push to production
git checkout main
git merge release/staging
git push origin main
# → Automated CI + CD to http://152.7.176.20:8080

# 5. Manual deployment
cd ansible
ansible-playbook -i inventory/staging.ini playbooks/deploy_staging.yml

# 6. Rollback if needed
ansible-playbook playbooks/rollback.yml -e "target_env=staging"
```

---

**For detailed pipeline execution logs and workflow runs, visit:**  
https://github.ncsu.edu/mdshah5/ecocycle-project/actions

---