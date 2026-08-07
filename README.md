TO DO:
- HTTPS
- elastic IP
- pre-signed URL
- Lambda 
- Secrets Manager
- Fargate

AWS architecture:
ElastiCache
RDS
EKS: 2 EC2 nodes
ALB
S3

EKS notes:
Kubernetes cluster
├── Control plane
│   ├── API server: entry point for Kubernetes commands
│   ├── Scheduler: choose which node should run each new pod
│   ├── Controller manager: continuously reconciles desired and actual state
│   └── etcd: stores cluster configuration and state, i.e. it is the control plane’s persistent key-value database
└── Worker nodes: a physical or virtual machine providing CPU, memory and networking
    ├── kubelet: agent running on the worker node
    ├── container runtime
    └── Pods
kubectl = Kubernetes API
locally: worker nodes are specific Docker containers that are generated automatically with 'kind create cluster'
Services: ClusterIP
Load Balancer Controller: translates Kubernetes intent into AWS load-balancer configuration

Deployment
└── ReplicaSet
    └── Pod
        └── FastAPI container


Helm: package manager for kubernetes

ECR notes:
Amazon ECR Registry: user_id.dkr.ecr.aws_region.amazonaws.com

$AwsRegion = "eu-west-2"
$AwsAccountId = aws sts get-caller-identity `
  --profile learning `
  --query Account `
  --output text
$EcrRegistry = "$AwsAccountId.dkr.ecr.$AwsRegion.amazonaws.com"
$EcrRepository = "$EcrRegistry/auth-fastapi"
$ImageTag = git rev-parse --short HEAD
docker build -t "${EcrRepository}:${ImageTag}" .

aws ecr get-login-password `
  --region $AwsRegion `
  --profile learning |
docker login `
  --username AWS `
  --password-stdin $EcrRegistry

docker push "${EcrRepository}:${ImageTag}"

EC2:
$env:AWS_PROFILE = "learning"
$env:AWS_REGION = "eu-west-2"

Terraform notes
- terraform, provider
- resource <Resource-Type> <local-name>
- data
- outputs
- (terraform fmt)
- terraform init
- (terraform validate)
- terraform plan
- **terraform apply**

Amazon Virtual Private Cloud notes
- VPC
  → defines the private network and address range
- Subnets
  → divide that network by address range and availability zone
- Route tables
  → decide **where** traffic goes
- Internet Gateway / NAT Gateway
  → provide different forms of internet connectivity
- Security groups
  → stateful inbound/outbound allow-only rules attached to a resource
- NACL
  → stateless inbound/outbound rules attached to a subnet

IAM notes
- root user
- IAM user
- IAM role
  - trust policy - every role has 1
  - permission policy
- IAM policy
- ARN

Docker notes:
- docker run --rm -it    for a temporary container
- Image — immutable packaged blueprint for a runnable environment.
- Container — one running instance of an image.
- Dockerfile — recipe used to produce an image.
- Layer/cache — why dependency installation should be before copying frequently changed application code.
- Volume — persistent data mounted into a container.
- Network — how containers in the same Compose app address each other by service name.
- Environment variables/secrets — configuration injected at runtime, not baked into an image.
- Compose - describes which containers should run together