# GCP Firebase Package

This package contains shared infrastructure-facing code and configurations for Google Cloud Platform and Firebase integration.

## Structure

```
packages/gcp_firebase/
├── api_gateway/
│   └── openapi-gateway.yaml    # API Gateway configuration with Firebase JWT
├── firestore_rules/
│   └── firestore.rules         # Multi-tenant Firestore security rules
├── storage_rules/
│   └── storage.rules           # Tenant-prefixed Cloud Storage rules
├── terraform/
│   ├── main.tf                 # Main Terraform configuration
│   ├── variables.tf            # Terraform variables
│   └── outputs.tf              # Terraform outputs
└── README.md                   # This file
```

## Components

### API Gateway
- **openapi-gateway.yaml**: Configures Google Cloud API Gateway with Firebase JWT authentication
- Handles routing to the FastAPI backend
- Validates Firebase ID tokens

### Firestore Rules
- **firestore.rules**: Security rules for multi-tenant Firestore access
- Ensures tenant isolation
- Validates user permissions based on custom claims

### Storage Rules
- **storage.rules**: Security rules for Cloud Storage buckets
- Implements tenant-prefixed access patterns
- Validates file upload/download permissions

### Terraform
Infrastructure as Code for:
- Cloud Run services
- Pub/Sub topics and subscriptions
- Storage buckets
- Secret Manager secrets
- IAM roles and bindings
- API Gateway configuration

## Usage

### Deploy Infrastructure
```bash
cd packages/gcp_firebase/terraform
terraform init
terraform plan
terraform apply
```

### Deploy Firestore Rules
```bash
firebase deploy --only firestore:rules
```

### Deploy Storage Rules
```bash
firebase deploy --only storage
```

### Deploy API Gateway
```bash
gcloud api-gateway api-configs create CONFIG_ID \
  --api=API_ID \
  --openapi-spec=api_gateway/openapi-gateway.yaml
```

## Configuration

### Environment Variables
- `GCP_PROJECT_ID`: Google Cloud Project ID
- `FIREBASE_PROJECT_ID`: Firebase Project ID (usually same as GCP_PROJECT_ID)
- `REGION`: Deployment region (e.g., us-central1)

### Firebase Configuration
Ensure Firebase is properly configured with:
- Authentication enabled
- Firestore database created
- Cloud Storage bucket created
- Custom claims configured for multi-tenancy

## Multi-Tenancy

This package implements a multi-tenant architecture where:
- Each tenant has isolated data in Firestore
- Storage files are prefixed with tenant ID
- API Gateway validates tenant access via Firebase custom claims
- Pub/Sub messages include tenant context

## Security

- All resources implement least-privilege access
- Firebase custom claims control tenant access
- API Gateway validates all requests
- Firestore and Storage rules enforce data isolation
