# Intelligent Cloud Operations Agent - GCP Implementation

> **A production-ready, modular AI agent leveraging LangChain, Hugging Face Transformers, and Google Cloud Platform services - deployed entirely within GCP's free tier.**

## 🚀 Overview

This project demonstrates enterprise-grade cloud engineering by implementing an intelligent AI agent that seamlessly integrates with Google Cloud Platform's ecosystem. The system combines advanced Natural Language Processing capabilities with real-time cloud operations monitoring, task management, and infrastructure querying.

**Key Achievement**: Zero-cost deployment utilizing GCP's free tier while maintaining production-quality architecture and functionality.

## 🏗️ Architecture 

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   User Layer    │    │   Agent Core     │    │   GCP Services      │
├─────────────────┤    ├──────────────────┤    ├─────────────────────┤
│ • Gradio Web UI │◄──►│ • LangChain      │◄──►│ • Firestore (NoSQL) │
│ • FastAPI REST  │    │   ReAct Agent    │    │ • Cloud Logging     │
│ • Swagger Docs  │    │ • Hugging Face   │    │ • BigQuery          │
└─────────────────┘    │   Transformers   │    │ • Cloud Monitoring  │
                       │ • Smart Routing  │    │ • Cloud Functions   │
                       └──────────────────┘    │ • Cloud Storage     │
                                               └─────────────────────┘
```

## ✨ Core Features

### 🤖 AI Capabilities
- **Multi-Agent Architecture**: Three specialized agents handling different domains
  - **Base Agent**: General knowledge, calculations, Wikipedia queries
  - **GCP Task Agent**: Firestore CRUD operations, Cloud Functions triggers
  - **DevOps Query Agent**: Live log analysis, BigQuery queries, metrics monitoring
- **Self-Hosted LLM**: `google/flan-t5-base` via Hugging Face Transformers
- **Intelligent Routing**: Automatic agent selection based on query context
- **Memory Management**: Conversation history and context preservation

### ☁️ GCP Integrations
- **Firestore**: Real-time task management with NoSQL database operations
- **Cloud Logging**: Live operational log querying and analysis
- **BigQuery**: On-demand SQL queries for data analytics
- **Cloud Monitoring**: Real-time infrastructure health and performance metrics
- **Cloud Functions**: Serverless workflow automation triggers
- **Cloud Storage**: Terraform state file parsing for Infrastructure as Code awareness

### 🛠️ Infrastructure & DevOps
- **Compute Engine**: Full-stack deployment on `e2-micro` instances
- **IAM & Security**: Proper service account configuration and permissions
- **VPC & Networking**: Firewall rules and network security
- **Cost Optimization**: Engineered to stay within free tier limits
- **Modular Design**: Easily extensible architecture for additional services

## 🚦 Quick Start

### Prerequisites
- Google Cloud Platform account with billing enabled
- Basic knowledge of GCP Console and CLI tools
- Python 3.8+ development environment

### 1. Infrastructure Setup

#### Deploy Compute Engine VM
```bash
# Create VM instance (stays within free tier)
gcloud compute instances create ai-agent-vm \
    --machine-type=e2-micro \
    --boot-disk-size=30GB \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --zone=us-central1-a \
    --tags=http-server,https-server

# Configure firewall rules
gcloud compute firewall-rules create allow-agent-port \
    --allow tcp:7860 \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server
```

#### Initialize Firestore Database
```bash
# Create Firestore database
gcloud firestore databases create --region=us-central1
```

### 2. Application Deployment

#### SSH into VM and Setup Environment
```bash
# Connect to your VM
gcloud compute ssh ai-agent-vm --zone=us-central1-a

# Update system and install dependencies
sudo apt update && sudo apt install -y python3-pip git
git clone <your-repository-url>
cd intelligent-cloud-operations-agent

# Install Python dependencies
pip3 install -r requirements.txt
```

#### Configure Authentication
```bash
# Authenticate with GCP (creates application default credentials)
gcloud auth application-default login

# Set your project ID
export GCP_PROJECT=$(gcloud config get-value project)
```

### 3. Deploy Cloud Function

Create the task management Cloud Function:

```bash
# Deploy the HTTP trigger function
gcloud functions deploy agent-task-trigger \
    --runtime=python310 \
    --trigger-http \
    --allow-unauthenticated \
    --region=us-central1 \
    --entry-point=handle_request \
    --memory=256MB \
    --source=./cloud-function
```

### 4. Launch the Application

```bash
# Start the AI agent system
python3 app.py
```

Access the application:
- **Web Interface**: `http://[VM_EXTERNAL_IP]:7860`
- **API Documentation**: `http://[VM_EXTERNAL_IP]:7860/docs`

## 📖 Usage Examples

### General Knowledge Queries
```
User: "What is machine learning according to Wikipedia?"
Agent: [Uses Base Agent with Wikipedia tool]
```

### GCP Task Management
```
User: "Add a task: Optimize database queries for the user service"
Agent: [Routes to GCP Task Agent, creates Firestore document]

User: "Show me all pending tasks"
Agent: [Retrieves and displays tasks from Firestore]
```

### DevOps Operations
```
User: 'Query logs with filter "severity=ERROR AND timestamp>="2024-01-01""'
Agent: [Uses DevOps Agent to query Cloud Logging API]

User: "Show CPU utilization for all compute instances"
Agent: [Queries Cloud Monitoring metrics API]
```

### Infrastructure Analysis
```
User: "List all compute instances from terraform state in bucket my-tf-state"
Agent: [Parses Terraform state files from Cloud Storage]
```

## 🔧 Configuration

### Environment Variables
```bash
# Required for local development
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
export GCP_PROJECT="your-project-id"

# Optional: Custom model configurations
export HF_MODEL_NAME="google/flan-t5-base"
export MAX_TOKENS=512
```

### Agent Configuration
Each agent can be customized in their respective files:
- `agents/base_llm_agent.py`: General-purpose tools and capabilities
- `agents/gcp_task_agent.py`: Firestore and Cloud Functions integration
- `agents/devops_query_agent.py`: GCP monitoring and logging tools

## 💰 Cost Management

### Free Tier Utilization
- **Compute Engine**: `e2-micro` instance (744 hours/month free)
- **Firestore**: 50,000 document reads/writes per day
- **Cloud Functions**: 2 million invocations per month
- **Cloud Logging**: 50GB ingestion per month
- **BigQuery**: 1TB queries per month
- **Cloud Storage**: 5GB storage

### Monitoring Costs
```bash
# Check current usage
gcloud billing budgets list
gcloud logging metrics list
```

## 🔒 Security Considerations

### Production Deployment Checklist
- [ ] Restrict Cloud Function access with IAM policies
- [ ] Update Firestore security rules beyond development mode
- [ ] Implement API authentication and rate limiting
- [ ] Configure VPC with private subnets
- [ ] Enable audit logging for compliance
- [ ] Set up monitoring alerts for unusual activity

### Service Account Permissions
```bash
# Minimal required roles
roles/datastore.user          # Firestore access
roles/logging.viewer           # Cloud Logging read access
roles/bigquery.user           # BigQuery query execution
roles/monitoring.viewer        # Cloud Monitoring access
roles/storage.objectViewer     # GCS read access for Terraform states
```

## 🧪 Testing

### Unit Tests
```bash
# Run agent tests
python -m pytest tests/test_agents.py -v

# Test GCP integrations
python -m pytest tests/test_gcp_helpers.py -v
```

### Integration Testing
```bash
# Test full workflow
curl -X POST "http://localhost:7860/invoke_agent" \
     -H "Content-Type: application/json" \
     -d '{"query": "Add task: Test deployment pipeline"}'
```

## 🚀 Future Enhancements

### Planned Features
- [ ] **Multi-Model Support**: Integration with Vertex AI and other LLM providers
- [ ] **Advanced Monitoring**: Custom dashboards and alerting rules
- [ ] **Workflow Automation**: Complex multi-step task orchestration
- [ ] **Data Pipeline Integration**: Cloud Dataflow and Pub/Sub connectivity
- [ ] **Security Scanning**: Automated vulnerability assessment tools
- [ ] **Kubernetes Integration**: GKE cluster management capabilities
- [ ] **CI/CD Pipeline**: GitHub Actions integration for automated deployments

### Scalability Improvements
- [ ] Horizontal scaling with load balancers
- [ ] Database connection pooling
- [ ] Caching layer with Cloud Memorystore
- [ ] Asynchronous task processing with Cloud Tasks

## 📚 Technical Documentation

### Agent Architecture
The system implements a modular agent architecture where each agent specializes in specific domains:

1. **Agent Selection**: Smart routing based on keyword analysis
2. **Tool Integration**: Each agent has access to relevant GCP APIs
3. **Memory Management**: Conversation context preservation
4. **Error Handling**: Graceful degradation and user feedback
