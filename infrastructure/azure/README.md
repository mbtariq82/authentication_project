# Azure Migration - Learning Setup

This is a **minimal, learning-focused** Terraform configuration for Azure.

## Prerequisites

- **Terraform**: >= 1.5.0 (install from https://www.terraform.io/downloads.html)
- **Azure CLI**: Latest version (install from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Azure Subscription**: Active Azure subscription with appropriate permissions
- **SSH Keys**: An SSH public key pair (`~/.ssh/id_rsa.pub`) for VM access

### Azure Authentication

Authenticate with Azure before running Terraform:

```bash
az login
az account show
```

If you have multiple subscriptions, set the active one:

```bash
az account set --subscription <SUBSCRIPTION_ID>
```

## File Structure

- **versions.tf**: Terraform version constraints and required providers
- **provider.tf**: Azure provider configuration
- **variables.tf**: Input variables with descriptions and defaults
- **resource_group.tf**: Azure Resource Group
- **vnet.tf**: Virtual Network, subnets, and public IPs
- **network_security_groups.tf**: Network Security Groups (NSGs) for firewalls
- **vm.tf**: Linux VM for FastAPI application with disk encryption
- **database.tf**: Azure Database for PostgreSQL (Flexible Server)
- **redis.tf**: Azure Cache for Redis with private endpoints
- **storage.tf**: Storage Accounts for frontend and profile images
- **container_registry.tf**: Azure Container Registry (ACR) for Docker images
- **outputs.tf**: Output values for reference

## Quick Start

### 1. Prepare Variables

Create a `terraform.tfvars` file based on the example:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your actual values:
- **admin_ip**: Your public IP address (get it from `curl https://checkip.amazonaws.com`)
- **database_username** & **database_password**: Strong credentials for PostgreSQL
- **location**: Azure region (default: uksouth)
- **environment**: Environment name (dev/staging/prod)

### 2. Initialize Terraform

```bash
terraform init
```

This downloads the Azure provider and initializes the working directory.

### 3. Validate Configuration

```bash
terraform validate
```

### 4. Plan Deployment

```bash
terraform plan -out=tfplan
```

Review the changes before applying.

### 5. Apply Configuration

```bash
terraform apply tfplan
```

This will create all Azure resources. The first deployment may take 10-15 minutes.

### 6. Get Outputs

After deployment completes:

```bash
terraform output
```

Save important outputs:
- `fastapi_public_ip`: Your application's public IP
- `postgres_fqdn`: PostgreSQL server hostname
- `redis_hostname`: Redis cache hostname
- `container_registry_login_server`: ACR login server
- `frontend_storage_primary_web_endpoint`: Frontend website URL

## Resource Mappings: AWS → Azure

| AWS | Azure | Notes |
|-----|-------|-------|
| VPC | Virtual Network | Virtual network for all resources |
| Subnet | Subnet | Public, private DB, and cache subnets |
| Security Groups | NSG | Network access control |
| EC2 (t3.micro) | Standard_B1s VM | Equivalent burstable compute |
| EIP | Static Public IP | Stable IP for VM |
| RDS PostgreSQL | PostgreSQL Flexible Server | Managed database service |
| ElastiCache Valkey | Azure Cache for Redis | In-memory cache |
| S3 (frontend) | Storage Account (Static Website) | Frontend hosting |
| S3 (profile images) | Storage Account (Private) | Private blob storage |
| ECR | Container Registry (ACR) | Private Docker registry |

## Network Architecture

```
┌─────────────────────────────────────────┐
│     Azure Virtual Network (10.0.0.0/16) │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │ Public Subnet (10.0.1.0/24)      │   │
│  │ ├─ FastAPI VM                    │   │
│  │ ├─ Public IP                     │   │
│  │ └─ ACR Private Endpoint          │   │
│  └──────────────────────────────────┘   │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │ Private DB Subnet (10.0.2.0/24)  │   │
│  │ └─ PostgreSQL Server             │   │
│  └──────────────────────────────────┘   │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │ Private Cache Subnet (10.0.3.0/24)  │
│  │ └─ Redis Cache                   │   │
│  └──────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

## Security Features

- **VM Disk Encryption**: OS disks encrypted with Azure Key Vault
- **Database Encryption**: SSL/TLS 1.2 required for PostgreSQL
- **Redis Encryption**: SSL/TLS encryption in transit, encryption at rest
- **Network Security**: NSGs restrict traffic to necessary ports/protocols
- **Storage Access**: Private storage account restricted to VNet
- **Private Endpoints**: Redis and ACR accessible only via private endpoints
- **Admin Access**: SSH access restricted to your IP address

## Environment Variables

For unattended deployments, you can set:

```bash
export ARM_SUBSCRIPTION_ID="<subscription-id>"
export ARM_TENANT_ID="<tenant-id>"
export ARM_CLIENT_ID="<client-id>"
export ARM_CLIENT_SECRET="<client-secret>"

terraform apply
```

## GitHub Actions Integration

For CI/CD deployment, see the GitHub Actions workflow configuration. You'll need to:

1. Create an Azure Service Principal:
   ```bash
   az ad sp create-for-rbac --name terraform-ci --role Contributor
   ```

2. Add credentials to GitHub Secrets:
   - `AZURE_CREDENTIALS`: Service principal JSON
   - `AZURE_SUBSCRIPTION_ID`: Subscription ID
   - `AZURE_TENANT_ID`: Tenant ID

## Cost Estimation

The default configuration uses economical resources:

| Resource | SKU | Estimated Cost |
|----------|-----|-----------------|
| VM | Standard_B1s | ~$8-15/month |
| PostgreSQL | B_Standard_B1ms | ~$25-35/month |
| Redis | Basic (250MB) | ~$15-20/month |
| Storage | Standard LRS | ~$0.50/GB |

**Total estimated**: ~$50-70/month for development.

## Troubleshooting

### Authentication Failed
```bash
az login
az account set --subscription <SUBSCRIPTION_ID>
```

### SSH Key Not Found
Create SSH keys:
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa
```

### Resource Group Already Exists
Delete and retry, or import into state:
```bash
terraform import azurerm_resource_group.main /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}
```

### Disk Encryption Issues
Ensure you have permissions to create Key Vault access policies. You may need to run:
```bash
az role assignment create --assignee <your-user-id> --role "Key Vault Administrator"
```

## Maintenance

### Regular Backups

PostgreSQL backups are configured with 7-day retention. To adjust:

```hcl
backup_retention_days = 7  # in database.tf
```

### Updates

To update resource properties:

1. Edit the relevant `.tf` file
2. Run `terraform plan` to review changes
3. Run `terraform apply` to apply changes

## Destroying Resources

To tear down all Azure resources:

```bash
terraform destroy
```

Review the plan before confirming deletion. This will:
- ✓ Delete all resources
- ✓ Remove resource group
- ✓ Clean up storage and backups

## Additional Resources

- [Azure Terraform Provider Documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest)
- [Azure Best Practices](https://docs.microsoft.com/en-us/azure/cloud-adoption-framework/ready/enterprise-scale/terraform-overview)
- [Terraform Cloud Documentation](https://www.terraform.io/cloud-docs)

## Notes

- **State Management**: Currently configured for local state. For production, use Terraform Cloud or Azure Storage Account for remote state.
- **Cost Optimization**: Monitor Azure costs and adjust resource SKUs as needed.
- **High Availability**: Current setup is single-zone. For production HA, enable multi-AZ for PostgreSQL and Redis.
- **SSL/TLS**: Configure custom domain and SSL certificates via Azure Application Gateway or CDN.

## Support

For issues or questions:
1. Check Terraform logs: `TF_LOG=DEBUG terraform apply`
2. Review Azure error messages in the console
3. Check Azure Portal for resource status
4. Consult Azure documentation links above


## Azure <--> AWS
Resource group > Access control (IAM)
EntraID

Virtual network = VPC

Blob storage    = S3
Blob container  = S3 bucket
Blob            = S3 object
Block           = a chunk used to construct a block blob.

AWS:
S3 storage classes - S3 Standard, Standard-IA, Glacier Instant Retrieval, Glacier Flexible Retrieval, and Deep Archive
Azure:
Access tiers - Hot, Cool, Cold, and Archive

## Azure only concepts
Resource group