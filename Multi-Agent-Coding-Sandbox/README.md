🤖 Multi-Agent Coding Sandbox

«From a natural-language prompt to a generated, tested full-stack application — entirely offline.»

Multi-Agent Coding Sandbox is a local-first AI software development system that uses CrewAI, Ollama, and Docker to coordinate four specialized AI agents. Together, they plan, generate, and test a full-stack application from a single natural-language instruction.

The system divides software development responsibilities across a Product Manager, Frontend Developer, Backend Developer, and DevOps/QA agent. Generated code is tested inside isolated, ephemeral Docker containers rather than executed directly on the host machine.

✨ Key Features

- 🤝 Multi-agent collaboration — Four specialized agents coordinate through CrewAI.
- 🧠 Local LLM inference — Uses Ollama-hosted models instead of proprietary AI APIs.
- 📝 Natural-language development — Describe an application in a single prompt.
- 🎨 Frontend generation — Dedicated agent for frontend implementation.
- ⚙️ Backend generation — Dedicated agent for backend implementation.
- 🧪 Automated QA — A DevOps/QA agent evaluates generated components and produces a report.
- 🔧 Automatic correction pass — Failed QA checks can trigger one corrective pass per component, configurable with "--max-fix-passes".
- 🐳 Docker sandboxing — Generated code runs in temporary containers.
- 🔒 Resource limits — Containers are CPU- and memory-capped.
- 🌐 Network isolation — Containers have networking disabled by default.
- 📂 Organized output — Generated frontend, backend, and QA report are saved to a predictable output directory.

---

🏗️ Architecture

The system separates application planning, implementation, and validation across four specialized agents.

                 Natural-Language Prompt
                           │
                           ▼
              ┌────────────────────────┐
              │   Product Manager          │
              │ Requirements & Planning.   │
              └────────────┬───────────┘
                             │
                 ┌─────────┴─────────┐
                 ▼                   ▼
       ┌─────────────────┐ ┌─────────────────┐
       │ Frontend Dev       │ │ Backend Dev     │
       │ UI Generation      │ │ API Generation  │
       └────────┬────────┘ └────────┬────────┘
                 │                   │
                └─────────┬─────────┘
                          ▼
              ┌────────────────────────┐
              │      DevOps / QA       │
              │ Docker-Sandbox Testing │
              └────────────┬───────────┘
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
          ┌─────────────┐     ┌─────────────┐
          │ QA Passed   │     │ QA Failed   │
          └──────┬──────┘     └──────┬──────┘
                 │                   │
                 │                   ▼
                 │            Corrective Pass
                 │                   │
                 └─────────┬─────────┘
                           ▼
                  Generated Artifacts
                           │
                           ▼
                  ./output/ Directory

This diagram illustrates the intended high-level workflow; exact task dependencies are determined by the implementation.

---

🧑‍💻 The Four Agents

Agent| Responsibility
Product Manager| Organizes the requested application into requirements and a development plan.
Frontend Developer| Generates the frontend implementation.
Backend Developer| Generates the backend implementation.
DevOps / QA| Tests generated components in Docker sandboxes and produces a QA report.

Each agent has a defined role within the development workflow, helping separate responsibilities instead of relying on a single model to perform every task.

---

🛠️ Technology Stack

Technology| Purpose
Python 3.10+| Main application runtime
CrewAI| Agent orchestration
Ollama| Local language-model inference
Llama 3.1 8B| General-purpose local model option
CodeQwen 7B| Code-generation model option
Mistral 7B| Additional local model option
Docker| Isolated execution and testing
"llm_config.py"| Model and endpoint configuration
"sandbox_manager.py"| Docker sandbox management

The available models can be changed to suit the models installed locally.

---

⚙️ Prerequisites

Before running the project, install the following:

- Python 3.10 or later
- Docker Desktop or a working local Docker daemon
- Ollama
- The required Python dependencies

1. Start Ollama

Start the Ollama service:

ollama serve

Pull the models used by the default configuration:

ollama pull llama3.1:8b
ollama pull codeqwen:7b
ollama pull mistral:7b

Make sure the model names match the configuration used by the application.

2. Verify Docker

Ensure Docker is installed and running before executing the application.

The sandbox manager uses Docker containers to run generated code in an isolated environment.

---

🚀 Installation

1. Clone the Repository

git clone <repository-url>
cd <repository-directory>

Replace the placeholders with your actual repository URL and directory name.

2. Create a Virtual Environment

python -m venv .venv

Activate it using the command for your operating system.

Linux / macOS

source .venv/bin/activate

Windows PowerShell

.venv\Scripts\Activate.ps1

3. Install Dependencies

pip install -r requirements.txt

---

▶️ Run the Application

Provide a natural-language description of the application you want to generate.

python main.py "Build a full-stack to-do app with a React frontend and FastAPI backend"

The multi-agent workflow processes the prompt and generates the application components.

Example Prompts

python main.py "Build a full-stack to-do app with a React frontend and FastAPI backend"

python main.py "Create a task management application with a web frontend and REST API"

python main.py "Generate a simple full-stack application with a user interface and backend API"

These are example prompts; the output depends on the models, agent instructions, and project requirements.

---

📂 Generated Output

Generated files are written to the "output/" directory.

output/
├── frontend/
├── backend/
└── qa_report.md

Output| Description
"output/frontend/"| Generated frontend application files
"output/backend/"| Generated backend application files
"output/qa_report.md"| QA findings and test results

The generated application is kept separate from the orchestration code, making it easier to inspect the results.

---

🧪 Automated QA & Correction

The DevOps/QA agent evaluates generated components inside Docker sandboxes.

If a QA check fails, the system can trigger an automatic corrective pass for the affected component.

The number of permitted correction passes is configurable using:

--max-fix-passes

For example, to allow two corrective passes:

python main.py "Build a full-stack to-do app" --max-fix-passes 2

The exact result depends on the project's QA implementation and the generated code. Always review the resulting report and source files before using a generated application.

---

🔒 Docker Sandbox & Security

Executing AI-generated code directly on the host can introduce unnecessary risk. This project uses Docker sandboxes to isolate generated-code execution.

Sandbox Protections

- Ephemeral containers — Containers are force-removed after each run.
- Network isolation — Networking is disabled by default.
- Resource limits — CPU and memory usage are capped.
- Host separation — Generated code runs inside containers rather than directly on the host.

Sandbox management is handled by:

sandbox_manager.py

Network Configuration

Network access can be enabled when the generated application requires external dependency installation, such as downloading packages from PyPI.

The configuration described by the project is:

SandboxManager(network_enabled=True)

Network access should remain disabled unless it is needed.

«Security note: Docker isolation is a useful defense-in-depth measure, not a complete security guarantee. Review generated code and Docker configuration, and avoid exposing sensitive host resources or credentials to generated workloads.»

---

🧠 Local Model Configuration

Model and endpoint settings are managed in:

llm_config.py

The configuration reads model and endpoint values from environment variables.

Example

Linux / macOS

export OLLAMA_BASE_URL=http://localhost:11434
export BACKEND_MODEL=ollama/codeqwen:7b

Windows PowerShell

$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:BACKEND_MODEL = "ollama/codeqwen:7b"

The project is designed to use local models. According to the supplied configuration, proprietary API keys are neither used nor read, and configuration rejects model names beginning with "gpt-" or "claude-".

For reliable offline operation, download all required model weights and dependencies before disconnecting from the internet. Actual offline behavior also depends on the dependencies and configuration used by the application.

---

🔄 End-to-End Workflow

1. Receive a natural-language prompt
                 ↓
2. Plan requirements with the Product Manager
                 ↓
3. Generate frontend and backend components
                 ↓
4. Prepare generated code for sandbox testing
                 ↓
5. Execute tests in isolated Docker containers
                 ↓
6. Generate a QA report
                 ↓
7. Apply corrective passes when needed
                 ↓
8. Save generated artifacts to ./output/

This workflow combines local AI inference with a structured agent-based development process and isolated testing.

---

🛠️ Configuration Reference

Setting| Purpose
"OLLAMA_BASE_URL"| Ollama endpoint
"BACKEND_MODEL"| Backend model identifier
"--max-fix-passes"| Maximum permitted corrective passes

Additional model settings are managed in "llm_config.py". Refer to the source code and "requirements.txt" for the complete configuration and dependency details.

---

📌 Current Scope

Based on the supplied project description, the system includes:

- Four specialized CrewAI agents
- Local Ollama model configuration
- Natural-language application prompts
- Frontend and backend code generation
- Docker-based sandbox testing
- Resource-limited, network-isolated containers by default
- QA report generation
- Configurable automatic correction passes
- Organized generated output

The project is a code-generation and testing workflow. Generated applications should be reviewed and validated before deployment.

---

🗺️ Potential Future Improvements

Possible extensions include:

- [ ] Richer QA summaries and failure categorization
- [ ] More detailed test reports
- [ ] Configurable agent roles and task definitions
- [ ] Additional local model profiles
- [ ] Improved handling of failed generation steps
- [ ] More comprehensive generated-application validation
- [ ] Clearer progress reporting for long-running workflows
- [ ] Reproducible sandbox test configurations

These are potential enhancements, not claims about existing functionality.

---

🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Implement your changes.
4. Test the changes locally.
5. Update the documentation where needed.
6. Submit a pull request with a clear description.

When contributing to sandbox or execution code, prioritize isolation, resource limits, and safe handling of generated artifacts.

---

📄 License

Add the license appropriate for your project before distributing it publicly.

---

<div align="center">🧠 Describe It. Generate It. Test It.

Multi-Agent Coding Sandbox

Local LLMs · CrewAI · Docker · Automated QA

</div>
