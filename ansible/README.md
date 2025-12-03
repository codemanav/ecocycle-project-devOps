# Ansible Automation for EcoCycle

This directory contains Ansible playbooks and roles for automated deployment of the EcoCycle application.

## 📁 Structure

```
ansible/
├── ansible.cfg                 # Ansible configuration
├── inventory/                  # Environment inventories
│   ├── staging.ini            # Staging environment
│   └── production.ini         # Production environment
├── playbooks/                  # Deployment playbooks
│   ├── deploy_staging.yml     # Deploy to staging
│   ├── deploy_production.yml  # Deploy to production
│   └── rollback.yml           # Rollback deployment
└── roles/                      # Ansible roles
    ├── common/                # VM setup and configuration
    ├── deploy/                # Application deployment
    └── healthcheck/           # Health verification
```

## 🚀 Quick Start

### Prerequisites

1. **Install Ansible** (on your local machine):
```bash
pip3 install ansible
```

2. **Setup SSH Access** to VM:
```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "mdshah5@ncsu.edu"

# Copy key to VM
ssh-copy-id mdshah5@152.7.176.20

# Test connection
ssh mdshah5@152.7.176.20
```

3. **Configure Secrets**:
```bash
# Create vault file for sensitive data
ansible-vault create inventory/vault.yml

# Add these variables:
vault_db_password: your-secure-db-password
vault_github_token: your-github-personal-access-token
```

## 📝 Usage

### Deploy to Staging

```bash
cd ansible

# Full deployment (setup + deploy + health check)
ansible-playbook playbooks/deploy_staging.yml

# With vault password
ansible-playbook playbooks/deploy_staging.yml --ask-vault-pass

# Specific image tag
ansible-playbook playbooks/deploy_staging.yml -e "image_tag=v1.0.0"

# Skip setup (if VM already configured)
ansible-playbook playbooks/deploy_staging.yml --skip-tags setup

# Only health check
ansible-playbook playbooks/deploy_staging.yml --tags healthcheck
```

### Deploy to Production

```bash
# Full production deployment
ansible-playbook playbooks/deploy_production.yml --ask-vault-pass

# Skip manual confirmation (for CI/CD)
ansible-playbook playbooks/deploy_production.yml -e "manual_approval=false"

# Specific image tag
ansible-playbook playbooks/deploy_production.yml -e "image_tag=v1.0.0"
```

### Rollback Deployment

```bash
# Rollback staging
ansible-playbook playbooks/rollback.yml -e "target_env=staging"

# Rollback production
ansible-playbook playbooks/rollback.yml -e "target_env=production"
```

### Test Connection

```bash
# Test staging connection
ansible staging -m ping

# Test production connection
ansible production -m ping

# Check all hosts
ansible all -m ping
```

### Dry Run (Check Mode)

```bash
# See what would change without making changes
ansible-playbook playbooks/deploy_staging.yml --check

# With diff output
ansible-playbook playbooks/deploy_staging.yml --check --diff
```

## 🔐 Security

### Using Ansible Vault

```bash
# Create encrypted vault
ansible-vault create inventory/vault.yml

# Edit vault
ansible-vault edit inventory/vault.yml

# View vault
ansible-vault view inventory/vault.yml

# Encrypt existing file
ansible-vault encrypt inventory/staging.ini

# Decrypt file
ansible-vault decrypt inventory/staging.ini
```

### Required Secrets

Add these to `inventory/vault.yml`:

```yaml
vault_db_password: your-secure-password
vault_github_token: ghp_xxxxxxxxxxxxxxxxxxxx
```

## 📊 Roles

### Common Role
- Updates system packages
- Installs Docker and Docker Compose
- Configures firewall
- Creates application directories
- Sets up logging

**Tags:** `setup`, `common`

### Deploy Role
- Pulls latest Docker images
- Deploys application using docker-compose
- Manages service lifecycle
- Cleans up old images

**Tags:** `deploy`

### Healthcheck Role
- Verifies all services are healthy
- Checks container status
- Monitors resource usage
- Logs health check results

**Tags:** `healthcheck`, `verify`

## 🎯 Variables

### Common Variables (in inventory files)

```ini
env_name=staging                    # Environment name
deploy_user=mdshah5                 # Deploy user
app_dir=/home/mdshah5/ecocycle-project  # App directory
image_tag=latest                    # Docker image tag
db_username=ecocycle                # Database username
marketplace_port=8081               # Marketplace port
users_port=8083                     # Users port
transactions_port=8082              # Transactions port
```

### Override Variables

```bash
# Override image tag
ansible-playbook playbooks/deploy_staging.yml -e "image_tag=v1.2.3"

# Override multiple variables
ansible-playbook playbooks/deploy_staging.yml \
  -e "image_tag=v1.2.3" \
  -e "db_username=custom_user"
```

## 🧪 Testing

### Test Playbook Syntax

```bash
# Check syntax
ansible-playbook playbooks/deploy_staging.yml --syntax-check

# List tasks
ansible-playbook playbooks/deploy_staging.yml --list-tasks

# List tags
ansible-playbook playbooks/deploy_staging.yml --list-tags
```

### Test Specific Tasks

```bash
# Run only setup tasks
ansible-playbook playbooks/deploy_staging.yml --tags setup

# Run only deployment
ansible-playbook playbooks/deploy_staging.yml --tags deploy

# Run only health checks
ansible-playbook playbooks/deploy_staging.yml --tags healthcheck
```

## 🔍 Troubleshooting

### Connection Issues

```bash
# Test SSH connection
ssh -v mdshah5@152.7.176.20

# Test Ansible connection
ansible staging -m ping -vvv

# Check inventory
ansible-inventory --list
```

### Deployment Failures

```bash
# Run with verbose output
ansible-playbook playbooks/deploy_staging.yml -vvv

# Check logs on VM
ssh mdshah5@152.7.176.20
cd ~/ecocycle-project
docker-compose logs

# Check health manually
curl http://152.7.176.20:8081/actuator/health
```

### Permission Issues

```bash
# Ensure user is in docker group
ssh mdshah5@152.7.176.20
groups  # Should show 'docker'

# If not, logout and login again
exit
ssh mdshah5@152.7.176.20
```

## 📈 Best Practices

1. **Always test in staging first**
```bash
ansible-playbook playbooks/deploy_staging.yml
# Verify everything works
ansible-playbook playbooks/deploy_production.yml
```

2. **Use specific image tags in production**
```bash
ansible-playbook playbooks/deploy_production.yml -e "image_tag=v1.0.0"
```

3. **Keep vault file secure**
```bash
# Never commit unencrypted secrets
ansible-vault encrypt inventory/vault.yml
```

4. **Test rollback procedure**
```bash
# Practice rollback in staging
ansible-playbook playbooks/rollback.yml -e "target_env=staging"
```

5. **Monitor deployments**
```bash
# Check health after deployment
ansible-playbook playbooks/deploy_staging.yml --tags healthcheck
```

## 🚀 CI/CD Integration

### GitHub Actions Example

```yaml
- name: Deploy to Staging
  run: |
    cd ansible
    ansible-playbook playbooks/deploy_staging.yml \
      -e "image_tag=${{ github.sha }}" \
      -e "github_token=${{ secrets.GITHUB_TOKEN }}" \
      --vault-password-file <(echo "${{ secrets.ANSIBLE_VAULT_PASSWORD }}")
```

## 📞 Support

For issues or questions:
1. Check logs: `~/ecocycle-project/logs/`
2. Check container status: `docker-compose ps`
3. Check health endpoints: `curl http://localhost:8081/actuator/health`

---

**Last Updated:** November 18, 2024
**Team:** Manav Shah (mdshah5) & Yuvraj Singh Bhatia (ybhatia2)

