ML-Ops CI/CD Engine

An automated machine learning CI/CD pipeline that triggers model training and evaluation whenever relevant Git changes are detected. The engine trains or fine-tunes models, evaluates performance using precision-focused metrics, saves improved model checkpoints, and provides a live dashboard for monitoring pipeline execution.

Project Structure
backend/    FastAPI application, webhook listener, and ML pipeline
frontend/   React, TypeScript, and Tailwind CSS dashboard

Features
Git-triggered model training through GitHub and GitLab webhooks.
Automatic detection of changes to data/ and src/models/.
Configurable model training and fine-tuning.
Model evaluation using precision, recall, and F1-score.
Performance-based model checkpointing.
Live dashboard for monitoring pipeline runs.
YAML-based model and training configuration.
SQLite support for development and PostgreSQL support for production.
Sample webhook payloads and synthetic data for testing.
Prerequisites
Python 3.10+
Node.js 18+
npm
Git

PyTorch and Hugging Face Transformers are required for the corresponding ML workloads. These libraries can be resource-intensive, so install them in an environment with suitable CPU or GPU resources.

The API and dashboard can operate without the full ML dependencies when the active code paths do not require them.

Installation and Setup
1. Clone the Repository
git clone <YOUR_REPOSITORY_URL>
cd ML-Ops-CI-CD-Engine


Replace <YOUR_REPOSITORY_URL> with your repository URL.

2. Run the Backend

Navigate to the backend directory and create a virtual environment:

cd backend
python3 -m venv .venv


Activate the environment.

Linux/macOS:

source .venv/bin/activate


Windows PowerShell:

.venv\Scripts\Activate.ps1


Install dependencies:

pip install -r requirements.txt


Start the FastAPI server:

uvicorn app.main:app --reload --port 8000


The backend will be available at:

API: http://localhost:8000
API documentation: http://localhost:8000/docs

On the first launch, the application creates an SQLite database named mlops.db and seeds sample pipeline runs for the dashboard.

3. Run the Frontend

Open a new terminal and navigate to the frontend directory:

cd frontend
npm install
npm run dev


The dashboard will be available at:

http://localhost:5173

Keep both the backend and frontend servers running during development.

Trigger a Pipeline Run

You can test the pipeline using the provided sample Git webhook payload.

Run the following command from the project root:

curl -X POST http://localhost:8000/api/webhooks/git \
  -H "Content-Type: application/json" \
  -d @backend/mock_data/sample_git_payload.json


The sample payload includes a commit that modifies data/transactions_q3.csv. Because this file matches a watched path, the webhook should trigger a pipeline run.

The expected workflow is:

The backend receives the Git webhook.
The engine checks whether the commit modifies a watched path.
A pipeline run is queued.
The model is trained or fine-tuned.
The model is evaluated against the configured criteria.
The engine decides whether to save a new checkpoint.
The dashboard displays the run status.

Open http://localhost:5173 to monitor the pipeline.

Integrate with GitHub or GitLab

To trigger the pipeline from a real repository:

Deploy the backend to a publicly accessible server.
Configure a push webhook in your GitHub or GitLab repository settings.
Set the webhook URL to https://<YOUR_BACKEND_HOST>/api/webhooks/git.
Configure the webhook to send push events.
Ensure the watched paths and config.yaml are configured correctly.
Push a commit that modifies a watched file.
Monitor the pipeline from the dashboard.

For production deployments, configure HTTPS, webhook signature verification, authentication, and appropriate access controls.

Configuration

The engine supports a config.yaml file at the root of the watched repository. This file controls the model source, training parameters, and evaluation criteria.

See backend/mock_data/config.yaml for the reference configuration.

Example:

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

Configuration Parameters
Parameter	Description
model.source	Model source: local or huggingface.
model.architecture	Local PyTorch model architecture.
model.hf_model_id	Hugging Face pretrained model identifier.
training.epochs	Number of training epochs.
training.batch_size	Number of samples per batch.
training.learning_rate	Optimizer learning rate.
training.val_split	Fraction of data reserved for validation.
evaluation.precision_threshold	Minimum precision required for checkpoint acceptance.

Ensure the selected model, dataset, and training parameters are compatible with your ML task.

Machine Learning Pipeline
Model Manager

File: backend/app/ml/model_manager.py

Resolves the model configuration and loads the appropriate model. It supports local PyTorch architectures and Hugging Face pretrained models with their corresponding tokenizers.

Training

File: backend/app/ml/training.py

Implements the model training loop and manages training parameters such as epochs, batch size, and learning rate.

The project includes a minimal tabular demo. Replace or extend the demo data loaders, preprocessing logic, and model forward pass to support your production workload.

Evaluation

File: backend/app/ml/evaluation.py

Evaluates model performance using:

Precision
Recall
F1-score

These metrics help assess the model's predictive performance and suitability for the target task.

Pipeline Orchestrator

File: backend/app/ml/pipeline_orchestrator.py

Coordinates the complete pipeline, including model loading, training, evaluation, and checkpoint selection.

A model is saved as the new best checkpoint only when both conditions are met:

Its precision exceeds the current best model's precision.
Its precision meets or exceeds the configured precision_threshold.

This prevents a model from replacing the current best checkpoint unless it satisfies the configured acceptance criteria.

Database

The application uses SQLite by default and creates mlops.db automatically.

For production, configure the DATABASE_URL environment variable with a PostgreSQL connection string:

export DATABASE_URL="postgresql://USER:PASSWORD@HOST:5432/DATABASE"


Replace the placeholders with your database credentials and connection details. Ensure the required database driver is installed and the connection settings are configured correctly.

Demo Data

The backend/mock_data/ directory contains sample assets for testing the pipeline:

sample_git_payload.json — Sample Git push webhook payload.
config.yaml — Example model and training configuration.
Synthetic dataset files — Sample data for demonstrating the pipeline.

These files allow you to test the workflow without connecting a real Git repository or using a production dataset.

Troubleshooting
Backend fails to start
Verify that Python 3.10 or later is installed.
Ensure the virtual environment is activated.
Install all required dependencies.
Review the backend logs for errors.
Webhook does not trigger a pipeline
Confirm that the backend is running.
Verify the webhook endpoint and request payload.
Ensure the commit modifies a watched path, such as data/ or src/models/.
Check the backend logs for validation or scheduling errors.
Model training fails
Verify that the required ML dependencies are installed.
Check the dataset format and model configuration.
Ensure the selected architecture supports the input data.
Review the training logs for errors.
Model checkpoint is not updated

The model must outperform the current best model in precision and meet the configured precision threshold. If either condition fails, the existing best checkpoint is retained.

Production Considerations

Before deploying the engine in production, consider implementing or verifying:

Webhook authentication and signature validation.
Secure management of secrets and environment variables.
Background workers or a dedicated job queue for long-running training.
GPU resource management and execution timeouts.
Model artifact storage and versioning.
Database migrations and backup strategies.
Structured logging, monitoring, and failure notifications.
Automated tests for webhook handling, training, evaluation, and checkpoint selection.

The included pipeline is a demonstration framework. Production workloads may require custom data loaders, model implementations, execution infrastructure, and deployment configuration.

Future Enhancements
Experiment tracking and model comparison.
Model registry and artifact versioning.
Configurable evaluation metrics.
Distributed training and GPU scheduling.
Automated rollback to previous checkpoints.
Pipeline failure notifications.
Integration with automated testing and deployment workflows.
Contributing

Contributions, bug reports, and feature suggestions are welcome.

Fork the repository.
Create a feature branch.
Implement and test your changes.
Submit a pull request describing your changes.
License

Add the appropriate license information for your project and include a LICENSE file in the repository.
