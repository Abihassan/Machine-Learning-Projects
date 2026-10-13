ML-Ops CI/CD Engine

Automated machine learning training, evaluation, and model versioning triggered by Git commits.

The ML-Ops CI/CD Engine automates the machine learning lifecycle by connecting Git-based workflows with model training, evaluation, checkpointing, and a live monitoring dashboard.

When a commit modifies files in watched directories such as data/ or src/models/, the engine detects the change, triggers a training or fine-tuning pipeline, evaluates the model with a precision-focused evaluation strategy, and saves a new checkpoint only when the model meets the configured performance criteria.

✨ Features
Git-triggered automation — Trigger ML pipelines through GitHub or GitLab push webhooks.
Automated model training — Train or fine-tune models when relevant data or model code changes.
Precision-focused evaluation — Evaluate models using precision, recall, and F1-score.
Performance-based checkpointing — Save a model only when it improves on the current best and satisfies the configured precision threshold.
Live dashboard — Monitor pipeline execution and run statuses through a React-based interface.
Configurable training — Customize model architecture, training parameters, and evaluation thresholds using YAML.
Flexible database support — Use SQLite for local development or PostgreSQL for production deployments.
Demo-ready setup — Explore the pipeline using sample webhook payloads and synthetic data without requiring a real Git repository.
🏗️ Architecture
GitHub / GitLab
       |
       | Push Webhook
       v
 FastAPI Backend
       |
       v
 Change Detection
       |
       | Watched paths modified?
       v
 Pipeline Orchestrator
       |
       +----> Model Loading
       |
       +----> Training / Fine-tuning
       |
       +----> Model Evaluation
       |
       +----> Best Model Checkpointing
       |
       v
 Database (SQLite / PostgreSQL)
       |
       v
 React Dashboard

Project Structure
ML-Ops-CI-CD-Engine/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── ml/
│   │       ├── model_manager.py
│   │       ├── training.py
│   │       ├── evaluation.py
│   │       └── pipeline_orchestrator.py
│   ├── mock_data/
│   │   ├── sample_git_payload.json
│   │   ├── config.yaml
│   │   └── ...
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
└── README.md

backend/ — FastAPI application, Git webhook handling, ML pipeline orchestration, and database integration.
frontend/ — React, TypeScript, and Tailwind CSS dashboard.
backend/mock_data/ — Sample webhook payloads, configuration, and synthetic data for local testing.
🛠️ Tech Stack
Component	Technology
Backend API	Python, FastAPI
ML Framework	PyTorch
Pretrained Models	Hugging Face Transformers
Frontend	React, TypeScript
Styling	Tailwind CSS
Database	SQLite / PostgreSQL
Development Server	Uvicorn
Configuration	YAML
Integration	GitHub / GitLab webhooks
🚀 Getting Started
Prerequisites

Install the following before running the project:

Python 3.10 or later
Node.js 18 or later
npm
Git

Optional: GPU-compatible PyTorch and the required ML dependencies for running actual model training workloads.

1. Clone the Repository
git clone <YOUR_REPOSITORY_URL>
cd ML-Ops-CI-CD-Engine


Replace <YOUR_REPOSITORY_URL> with your repository's clone URL.

2. Start the Backend

Navigate to the backend directory and create a virtual environment:

cd backend

python3 -m venv .venv


Activate the environment.

Linux / macOS:

source .venv/bin/activate


Windows PowerShell:

.venv\Scripts\Activate.ps1


Install the backend dependencies:

pip install -r requirements.txt


Start the FastAPI development server:

uvicorn app.main:app --reload --port 8000


The backend will be available at:

API base URL: http://localhost:8000
Interactive API documentation: http://localhost:8000/docs

On its first launch, the application creates an SQLite database named mlops.db and seeds sample pipeline runs so the dashboard has data to display.

Note: PyTorch and Hugging Face Transformers can require substantial disk space, memory, and compute resources. Install and configure the appropriate dependencies for your environment if you intend to execute real training workloads. API and dashboard functionality can be used without the full ML stack, provided the relevant imports are not required by the running code path.
3. Start the Frontend

Open a second terminal and navigate to the frontend directory:

cd frontend

npm install
npm run dev


The dashboard will be available at:

http://localhost:5173

Keep both the backend and frontend servers running while testing the application.

⚡ Trigger a Pipeline Run

You can test the complete webhook workflow without connecting a real Git repository.

From the project root, run:

curl -X POST http://localhost:8000/api/webhooks/git \
  -H "Content-Type: application/json" \
  -d @backend/mock_data/sample_git_payload.json


The sample payload includes a commit that modifies:

data/transactions_q3.csv


Because this file matches a watched path, the backend should enqueue a pipeline run.

Expected Workflow
Git Push
   |
   v
Webhook Received
   |
   v
Watched Changes Detected
   |
   v
Run Queued
   |
   v
Model Training
   |
   v
Model Evaluation
   |
   v
Checkpoint Decision
   |
   v
Run Completed


Open the dashboard at http://localhost:5173 to monitor the run and inspect its status.

A successful run should progress through states such as Queued → Running → Success, depending on the pipeline's execution and error-handling behavior.

🔗 Integrate with GitHub or GitLab

To trigger the pipeline from a real repository:

Deploy the backend to an endpoint accessible by your Git hosting provider.
Configure a push webhook in your repository settings.
Set the webhook URL to:
   https://<YOUR_BACKEND_HOST>/api/webhooks/git

Configure the webhook to send push events.
Ensure the repository's watched paths and config.yaml are configured correctly.
Push a commit that modifies a watched file.
Open the dashboard to monitor the resulting pipeline run.

Production note: Configure webhook signature verification, authentication, HTTPS, and appropriate access controls before exposing the endpoint publicly.

⚙️ Configuration

The pipeline can be configured using a config.yaml file at the root of the repository being watched.

See backend/mock_data/config.yaml for the project's reference configuration.

Example Configuration
model:
  source: local
  architecture: CustomCNN
  hf_model_id: distilbert-base-uncased

training:
  epochs: 5
  batch_size: 32
  learning_rate: 0.001
  val_split: 0.2

evaluation:
  precision_threshold: 0.85

Configuration Reference
Parameter	Description
model.source	Model source: local or huggingface.
model.architecture	Name of the local model architecture to load.
model.hf_model_id	Hugging Face model identifier when using a pretrained model.
training.epochs	Number of training epochs.
training.batch_size	Number of samples processed per batch.
training.learning_rate	Optimizer learning rate.
training.val_split	Fraction of the dataset reserved for validation.
evaluation.precision_threshold	Minimum precision required for a checkpoint to be accepted.

The configuration values shown above are examples. Ensure that the selected architecture, dataset, tokenizer, and training parameters are compatible with your actual ML task.

🧠 Machine Learning Pipeline

The ML components are organized into focused modules.

Model Management

File: backend/app/ml/model_manager.py

Responsible for resolving the model configuration and loading the appropriate model.

Supports local PyTorch model architectures.
Supports Hugging Face pretrained models and tokenizers.
Uses the configured model source and architecture settings.
Model Training

File: backend/app/ml/training.py

Handles the model training loop and associated training configuration, including epochs, batch size, and learning rate.

The project includes a minimal tabular demo to help demonstrate the pipeline. Replace or extend its data-loading logic, preprocessing, and model forward pass to support your production dataset and architecture.

Model Evaluation

File: backend/app/ml/evaluation.py

Evaluates model performance using classification metrics, including:

Precision — The proportion of positive predictions that are correct.
Recall — The proportion of actual positive cases that are correctly identified.
F1-score — The harmonic mean of precision and recall.

The configured precision threshold determines the minimum precision required for a model checkpoint to be considered.

Pipeline Orchestration

File: backend/app/ml/pipeline_orchestrator.py

Coordinates the pipeline from model loading through training and evaluation to the final checkpoint decision.

A model is checkpointed only when both conditions are satisfied:

Its precision exceeds the current best model's precision.
Its precision meets or exceeds the configured precision_threshold.

This helps prevent a lower-performing model from replacing the best saved model.

Important: Precision alone may not be sufficient for selecting a production model. Depending on the use case, also consider recall, F1-score, class imbalance, validation methodology, and the consequences of false positives and false negatives.
🗄️ Database Configuration

The project uses SQLite by default for local development.

The database is created automatically on startup:

mlops.db


For production deployments, configure the DATABASE_URL environment variable with a PostgreSQL connection string.

Example:

export DATABASE_URL="postgresql://USER:PASSWORD@HOST:5432/DATABASE"


Replace the placeholders with your database credentials and connection details.

The application is designed to support changing the database URL without requiring unrelated application code changes. Ensure the PostgreSQL driver and connection settings are configured appropriately for your environment.

🖥️ Dashboard

The React dashboard provides a visual interface for monitoring pipeline execution.

Use it to observe pipeline runs and their statuses as webhook-triggered workflows progress.

View existing demo runs.
Monitor queued, running, and completed runs.
Follow model training and evaluation activity exposed by the backend.

Dashboard details depend on the API endpoints and fields implemented in the current project version.

🧪 Demo Data

The backend/mock_data/ directory contains sample assets for testing:

sample_git_payload.json — A mock Git push event.
config.yaml — Example model and training configuration.
Synthetic dataset files — Sample data for exercising the demo pipeline.

These assets let you explore the end-to-end workflow without connecting an external repository or supplying a production dataset.

🔧 Troubleshooting
Backend fails to start
Verify that Python 3.10 or later is installed.
Activate the backend virtual environment.
Install the dependencies from requirements.txt.
Check the terminal output for missing packages or configuration errors.
Frontend cannot connect to the backend
Confirm that the backend is running on port 8000.
Confirm that the frontend is running on port 5173.
Check the frontend API base URL and backend CORS configuration.
Webhook does not trigger a run
Verify that the request reaches /api/webhooks/git.
Check that the payload follows the expected Git webhook format.
Confirm that the commit modifies a watched path, such as data/ or src/models/.
Inspect the backend logs for validation errors or pipeline scheduling issues.
Model training fails
Verify that the required ML dependencies are installed.
Check that the selected model architecture matches the dataset and input format.
Confirm that the dataset and configuration are accessible to the pipeline.
Review the backend logs for training or evaluation errors.
A trained model is not checkpointed

Check whether the evaluated model:

Achieved precision above the current best model's precision.
Met the configured evaluation.precision_threshold.

A model that fails either condition should not replace the current best checkpoint.

🔒 Production Considerations

Before deploying the engine in a production environment, consider implementing or verifying:

Webhook signature validation and authentication.
Secure secret and environment-variable management.
Background task execution or a dedicated job queue for long-running training.
GPU resource management and training timeouts.
Dataset and model artifact versioning.
Persistent artifact storage and backup strategies.
Database migrations and production connection pooling.
Structured logging, monitoring, and failure notifications.
Automated tests for webhook handling, training, evaluation, and checkpoint selection.
Reproducible training runs with recorded dataset, configuration, and model versions.

The demo pipeline is a starting point. Production readiness depends on the actual data loaders, model implementations, job execution model, and deployment configuration.

🛣️ Future Enhancements

Potential extensions include:

Experiment tracking and run comparisons.
Model registry and artifact version management.
Configurable evaluation metrics and acceptance policies.
Distributed training and GPU scheduling.
Automated rollback to previously validated checkpoints.
CI test integration for data and model changes.
Notifications for failed runs and improved model performance.
🤝 Contributing

Contributions, bug reports, and feature suggestions are welcome.

Fork the repository.
Create a feature branch.
Make your changes and add relevant tests.
Submit a pull request describing the changes.
📄 License

Add your project's license information here. If the repository is open source, include the appropriate LICENSE file and update this section accordingly.
