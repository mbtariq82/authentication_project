TO DO:
- tanstack query
- HTTPS
- elastic IP
- Lambda AWS service
- modules
- AWS: pre-signed URL, RDS, EC2 (x)
- kubernetes: EKS ()

Cloud architecture:
- react server: S3 + Cloudfront
- fastapi server: EC2
- postgres: RDS
- redis: Elastic Cache
- Application Load Balancer 
    - waits for HTTPS requests on port 443
    - listener rule
    - target group
- Route53 + HTTPS + DNS
- Secrets Manager

Terraform notes
- terraform, provider
- resource <Resource-Type> <local-name>
- 
- 
- versions.tf → what Terraform/provider versions are required
- provider.tf → how the AWS provider is configured
- vpc.tf      → what AWS resource should exist
- outputs.tf  → what resulting values should be displayed
(terraform fmt)
terraform init
(terraform validate)
terraform plan
**terraform apply**



Amazon Virtual Private Cloud
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

IAM
- IAM user
- IAM role
- root user
- IAM policy
- ARN


Docker notes:
Image — immutable packaged blueprint for a runnable environment.
Container — one running instance of an image.
Dockerfile — recipe used to produce an image.
Layer/cache — why dependency installation should be before copying frequently changed application code.
Volume — persistent data mounted into a container.
Network — how containers in the same Compose app address each other by service name.
Environment variables/secrets — configuration injected at runtime, not baked into an image.