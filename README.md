TO DO:
- EKS
- HTTPS
- elastic IP
- pre-signed URL
- Lambda 
- Secrets Manager

EKS:
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


Deployment
└── ReplicaSet
    └── Pod
        └── FastAPI container


Helm

The most common design is one application container per Pod.
EKS:


Fargate:
- CloudWatch for logs
- task definition
- Secrets Manager
- 

ECR notes:
- Amazon ECR Registry: 123456789012.dkr.ecr.eu-west-2.amazonaws.com
      - user id
      - region
- Repository: 
- Image tag:
- Repository policy: 
- Authorization token: aws login
- IAM permission
- steps:
  - 1. create repository
  - 2. give EC2 IAM policy: /AmazonEC2ContainerRegistryPullOnly
  - 3. build image with tag (registry/repository)
  - 4. (give user access to push to ECR)
  - 5. Authenticate Docker with ECR
  - 6. push image
  - 7. pull and restart container
(no need for image build instructions in docker compose)
$AwsRegion = "eu-west-2"
$AwsAccountId = aws sts get-caller-identity `
  --profile learning `
  --query Account `
  --output text
$EcrRegistry = "$AwsAccountId.dkr.ecr.$AwsRegion.amazonaws.com"
$EcrRepository = "$EcrRegistry/auth-fastapi"
$ImageTag = git rev-parse --short HEAD


Log Docker into ECR locally
aws ecr get-login-password `
  --region $AwsRegion `
  --profile learning |
docker login `
  --username AWS `
  --password-stdin $EcrRegistry




$env:AWS_PROFILE = "learning"
$env:AWS_REGION = "eu-west-2"



ECS notes:
- cluster
- task definition
- task
- service




- An ECS-compatible EC2 machine is called a container instance



Kubernetes notes:
- Control plane
- Worker nodes (EC2/Fargate)
- 



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
  - trust policy
  - permission policy
- IAM policy
- ARN

ALB notes:
- 

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