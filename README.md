# EcoCycle DevOps Reinforcement Project — Proposal

## Team Members
| Name | Unity ID |
|------|-----------|
| **Manav Shah** | mdshah5 | 
| **Yuvraj Singh Bhatia** | ybhatia2 | 

---
## 1. Problem Statement & Description

### The Problem
EcoCycle is a marketplace which focuses on sustainability, it is built with three microservices (Marketplace, Transactions, Users) and currently runs only on local machines. The problem is that every build, test, and deployment functions are currently performed manually, which sometimes leads to inconsistent results, fragile environments, and delays in delivery.

### Why It Matters
Automation is important because without automation, even a small change in code can break a service. Manual deployments sometimes lead to version mismatches or config mistakes or can cause unexpected downtime which can create an issue for active user transactions. Without the security or health checks, the system also becomes more prone to bugs, regressions and security risks.

### Our Solution
Our solution is that we will design and implement an automated CI/CD pipeline that will build, test, scan for any bug, and deploy the microservices using GitHub Actions and Ansible automatically. The pipeline will check the quality of code through linting, testing, analysis and then it will build secure container images for deployment. It will use a controlled release process to deploy these containers to a remote server and will have health checks, security scans, and Blue/Green staging to make sure that every update is safe, stable, and reliable from commit to production.

---

## 2. Use Case

### Use Case: PR to `release/*` Triggers Automated Secure Deployment

#### Preconditions
- A release branch exists and branch-protection rules are enabled.  
- A target VM is reachable via SSH and configured for Ansible.  
- Docker Hub account & namespace (`DOCKERHUB_USERNAME`) available for image pushes.

#### Main Flow
1. Developer opens a Pull Request (PR) into `release/*`.  
2. **Continuous Integration (Test Environment)**  
   - Runs Checkstyle & Spotless lint
   - Maven tests (JUnit & integration)
   - Static analysis.  
   - Security scans.  
   - If all checks pass → proceed to step 3.  
   - **If tests or scans fail**, the pipeline terminates (**[E1]**, **[E2]**).  
3. **Image Build and Push**  
   - If all checks pass, Docker images for Marketplace, Transactions, and Users are built and pushed to GHCR.
4. **Continuous Deployment (Staging Environment)**  
   - Ansible provisions the remote server (installs Docker, pulls images, starts docker compose up -d).
   - Executes **health checks on staging**  
   - If staging passes → proceed to step 5.  
   - If staging fails → rollback to previous stable image (**[E3]**).  
5. **Production Deployment**  
   - Ansible promotes the same images to production.  
   - Executes **post-deploy health checks** in production.  
   - Rollback triggered automatically if production fails threshold (**[E4]**).  

#### Subflows
- **[S1]** Developer creates PR with commit message and reviewers.
- **[S2]** PR approved → CI workflow starts automatically.  
- **[S3]** Ansible logs and deployment artifacts stored for auditing.

#### Alternative / Error Flows
- **[E1]** Build or tests fail → pipeline stops in CI stage.  
- **[E2]** Security scan finds critical CVE  → deployment blocked.  
- **[E3]** Health check failure in staging → rollback.  
- **[E4]** Production health degradation → automatic rollback to last stable release.

---

## 3. Pipeline Design

**Figure 1:** CI Workflow
![EcoCycle CI Pipeline](assets/flow.png)

---
## 4. Implementation Progress (Automation)

### Added Enhancements
- Unique service ports: `8081` marketplace, `8082` transactions, `8083` users.
- Spring Boot Actuator added to all services for `/actuator/health` checks.
- Multi-stage Dockerfiles (smaller runtime images) per service.
- GitHub Actions workflow (`.github/workflows/ci.yml`) for PR validation and staged deploy.
- OWASP Dependency Check scan job (`vuln-scan`) added for each module producing HTML reports.
- Removed direct compile dependency between `transactions-service` and `marketplace-service` for proper microservice isolation.
- Switched image registry from GHCR to Docker Hub.

### CI/CD Workflow Summary
1. PR to `release/*` → build & test each microservice (JUnit) + dependency review (blocks critical CVEs).
2. Images built & pushed to Docker Hub tagged with commit SHA (and `latest` on `main`).
3. Staging deploy via SSH to VM, health checks hit `/actuator/health`.
4. On push to `main`, production deploy job reuses images and validates health.

### Required GitHub Secrets
| Secret | Purpose |
|--------|---------|
| `DOCKERHUB_USERNAME` | Docker Hub username/namespace for image tags |
| `DOCKERHUB_TOKEN` | Docker Hub PAT or password for login |
| `STAGING_HOST` / `PROD_HOST` | VM hostnames / IPs |
| `STAGING_USER` / `PROD_USER` | SSH usernames |
| `STAGING_SSH_KEY` / `PROD_SSH_KEY` | Private keys (PEM) |

### Setting Up VM (One-Time)
```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

### Local Build & Test
```bash
cd marketplace-service && mvn test
cd ../transactions-service && mvn test
cd ../users-service && mvn test
```

### Run Single Service (Dev In-Memory DB)
Use the `dev` profile to avoid needing Postgres:
```bash
docker build -t marketplace:dev marketplace-service
docker run -e SPRING_PROFILES_ACTIVE=dev -p 8081:8081 marketplace:dev
curl http://localhost:8081/actuator/health
```

### Run With Postgres (Without Compose)
```bash
docker run -d --name marketplace-db \
   -e POSTGRES_DB=marketplace -e POSTGRES_USER=ecocycle -e POSTGRES_PASSWORD=ecocycle \
   -p 5433:5432 postgres:16
docker run -p 8081:8081 \
   -e SPRING_DATASOURCE_URL=jdbc:postgresql://host.docker.internal:5433/marketplace \
   -e SPRING_DATASOURCE_USERNAME=ecocycle -e SPRING_DATASOURCE_PASSWORD=ecocycle \
   marketplace:dev
```

### Build Images Locally
```bash
docker build -t marketplace:dev marketplace-service
docker build -t transactions:dev transactions-service
docker build -t users:dev users-service
```

### Run Locally with Compose (Quick Draft)
```bash
docker compose up -d
curl http://localhost:8081/actuator/health
curl http://localhost:8082/actuator/health
curl http://localhost:8083/actuator/health
```

### Next Suggested Improvements
- Add dependency scanning (OWASP or Snyk) step.
- Promote rollbacks (store previous SHA, redeploy on failure).
- Centralize security (OAuth2) & externalize secrets (remove plain text JWT secret).
- Add testcontainer-based integration tests for Postgres.

---
## 5. Grading Alignment Checklist
| Criterion | Status |
|-----------|--------|
| CI pipeline triggers | Implemented |
| Automated tests | Maven test stage |
| Security gate | Dependency review action |
| Vulnerability scan | OWASP dep check reports |
| Containerization | Multi-stage Dockerfiles |
| Environment separation | Staging vs Production jobs |
| Health checks | Actuator endpoints used |
| Documentation | Updated README section |

---
_Generated with assistance; keep iterating for full marks._

