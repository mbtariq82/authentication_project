TO DO:
- tanstack query
- IAM
- HTTPS
- elastic IP
- RDS
- elastic Cache
- Application Load Balancer
- pre-signed URL
- EKS
- Lambda 
- modules
- Secrets Manager

Cloud architecture:
- react: S3
- fastapi server + postgres + redis: EC2

Terraform notes
- terraform, provider
- resource <Resource-Type> <local-name>
- data
- outputs
(terraform fmt)
terraform init
(terraform validate)
terraform plan
**terraform apply**

Amazon Virtual Private Cloud notes
Example:
    VPC: 10.0.0.0/16
    ├── Subnet A: 10.0.1.0/24
    │   |── EC2: 10.0.1.20
    |   └── NAT Gateway
    │
    └── Subnet B: 10.0.2.0/24
        └── RDS: 10.0.2.30
    Route tables:
        Subnet A: 
            Destination      Target
            10.0.1.0/24  ->  local
            0.0.0.0/0    ->  Internet Gateway    
        Subnet B:
            Destination      Target
            10.0.2.0/24      local
            0.0.0.0/0        Nat Gateway
VPC
  → defines the private network and address range
Subnets
  → divide that network by address range and availability zone
Route tables
  → decide where traffic goes
Internet Gateway / NAT Gateway
  → provide different forms of internet connectivity
Security groups
  → stateful inbound/outbound allow-only rules attached to a resource
NACL
  → stateless inbound/outbound rules attached to a subnet

IAM notes
- IAM user
- IAM role
- root user
- IAM policy
- ARN


Docker notes:
- Image — immutable packaged blueprint for a runnable environment.
- Container — one running instance of an image.
- Dockerfile — recipe used to produce an image.
- Layer/cache — why dependency installation should be before copying frequently changed application code.
- Volume — persistent data mounted into a container.
- Network — how containers in the same Compose app address each other by service name.
- Environment variables/secrets — configuration injected at runtime, not baked into an image.