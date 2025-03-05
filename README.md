# FastAPI Application for AKS

This is a simple FastAPI application that can be deployed to Azure Kubernetes Service (AKS) using GitHub Actions.

## Prerequisites

- Azure CLI installed
- Docker installed
- kubectl installed
- Terraform installed (for infrastructure management)
- GitHub repository connected to Azure (for GitHub Actions)

## Project Structure

```
.
├── app.py                 # FastAPI application
├── requirements.txt       # Python dependencies
├── Dockerfile             # For containerizing the application
├── k8s/                   # Kubernetes manifests
│   ├── deployment.yaml    # Deployment configuration
│   └── service.yaml       # Service configuration
├── .github/workflows/     # GitHub Actions workflows
│   └── deploy-to-aks.yml  # Deployment workflow
├── infra/                 # Terraform infrastructure code
└── README.md              # This file
```

## Local Development

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Access the API at http://localhost:8000
   - API documentation is available at http://localhost:8000/docs

## Infrastructure Setup

1. Deploy the infrastructure using Terraform:
   ```
   cd infra
   terraform init
   terraform apply
   ```

   This will create:
   - Azure Kubernetes Service (AKS) cluster
   - Azure Container Registry (ACR) with admin access enabled
   - Resource group for all resources

2. After deployment, note the following outputs for GitHub Actions setup:
   - `acr_name`: The name of your Azure Container Registry
   - `acr_login_server`: The login server URL for your ACR
   - `kubernetes_cluster_name`: The name of your AKS cluster
   - `resource_group_name`: The resource group containing your resources

## GitHub Actions Setup

1. In the Azure Portal, set up a service principal for GitHub Actions:
   ```
   az ad sp create-for-rbac --name "github-actions-sp" --role contributor \
     --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
     --sdk-auth
   ```

2. Add the following secrets to your GitHub repository:
   - `AZURE_CREDENTIALS`: The JSON output from the service principal creation
   - `ACR_LOGIN_SERVER`: The ACR login server URL (from Terraform output)
   - `ACR_USERNAME`: The ACR admin username (from Azure Portal)
   - `ACR_PASSWORD`: The ACR admin password (from Azure Portal)
   - `AKS_RESOURCE_GROUP`: The resource group name (from Terraform output)
   - `AKS_CLUSTER_NAME`: The AKS cluster name (from Terraform output)

3. Push your code to the main branch or manually trigger the workflow to deploy the application.

## API Endpoints

- `GET /`: Returns a welcome message
- `GET /health`: Health check endpoint
- `GET /info`: Returns information about the application

## Scaling

The application is configured to run with 2 replicas by default. You can scale it by modifying the `replicas` field in `k8s/deployment.yaml` or by using the kubectl command:

```
kubectl scale deployment fastapi-app --replicas=3
``` 

## IoT Monitoring Platform with Distributed Data Collection
That's an excellent idea! Adding a distributed data collection component would make your IoT monitoring platform more robust and scalable. Let's enhance the architecture and outline how you could build this system:

┌────────────────┐   ┌─────────────────┐   ┌────────────────────┐
│  IoT Devices   │──▶│ Edge Collectors │──▶│ Ingestion Service  │
└────────────────┘   └─────────────────┘   └────────────────────┘
                                                     │
┌────────────────┐   ┌─────────────────┐             ▼
│ ML Service     │◀──│ Rules Engine    │◀───┌────────────────────┐
│ (Anomaly       │   │ Service         │    │ Telemetry Service  │
│  Detection)    │──▶│                 │───▶│ (Data Processing)  │
└────────────────┘   └─────────────────┘    └────────────────────┘
        │                    │                       │
        │                    ▼                       │
        │           ┌─────────────────┐              │
        └──────────▶│ Notification    │◀─────────────┘
                    │ Service         │
                    └─────────────────┘
                            │
┌────────────────┐          ▼          ┌────────────────────┐
│ Device         │◀───┌─────────────────┐───▶│ Dashboard Service │
│ Registry       │    │ API Gateway     │    │ (Visualization)   │
│ Service        │───▶│ (Your FastAPI)  │◀───└────────────────────┘
└────────────────┘    └─────────────────┘
                             ▲
                             │
                      ┌─────────────────┐
                      │ User Service    │
                      │ (Auth & Access) │
                      └─────────────────┘


Implementation Approach
To implement this system with a microservices architecture:

1. Start with the API Gateway: Enhance your FastAPI app to route requests to the appropriate services.

2. Build the Edge Collector: Create a lightweight Python client that:
- Runs on edge devices (Raspberry Pi, industrial gateways, etc.)
- Collects data from local sensors
- Buffers data locally during connectivity issues
- Securely sends data to your ingestion service

3. Develop Core Services:
- Device Registry Service: Stores device metadata, configuration
- Ingestion Service: Receives and validates incoming data
- Telemetry Service: Processes and stores sensor data
- Rules Engine: Evaluates conditions on incoming data
- Notification Service: Sends alerts via email, SMS, webhooks


4. Add Analytics Components:
- ML Service: Processes telemetry data for anomaly detection
- Dashboard Service: Provides visualization endpoints


Technologies to Consider
- Message Queue: Kafka or RabbitMQ for data streaming between services
- Time-Series Database: InfluxDB or TimescaleDB for telemetry data
- Fast Storage: Redis for caching and real-time data
- Visualization: React dashboard with D3.js or Grafana
- WebSockets: For real-time updates to the dashboard
- Service Mesh: Istio for service-to-service communication

Deployment Strategy
- Deploy individual microservices to your existing AKS cluster
- Use Kubernetes StatefulSets for stateful services
- Implement horizontal pod autoscaling based on traffic
- Set up persistent volumes for databases
- Use ConfigMaps and Secrets for service configuration

