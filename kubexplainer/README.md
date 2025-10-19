# 🚀 Kubernetes YAML Explainer

<div align="center">

![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)

**Understand your Kubernetes manifests with AI-powered and rule-based explanations**

[Features](#-features) • [Quick Start](#-quick-start) • [Usage](#-usage) • [Configuration](#-configuration) • [API Docs](#-api-documentation)

</div>

---

## 📖 Overview

**Kubernetes YAML Explainer** is a self-contained, Dockerized web application that helps you understand Kubernetes and k3s YAML manifests. It validates manifests against known schemas and explains their structure and meaning in clear English.

The application works **entirely offline** using an internal rule-based engine, but also supports optional integration with remote LLM backends (OpenAI, Anthropic Claude, local Ollama, etc.) for richer natural-language explanations.

### ✨ Key Highlights

- 🔍 **Parse & Validate** - Parse multi-document YAML and validate against Kubernetes schemas
- 📚 **Rule-Based Explanations** - 80+ built-in explanations for common Kubernetes fields
- 🤖 **Optional AI Integration** - Connect to OpenAI, Claude, or local LLMs for enhanced explanations
- 🎨 **Modern Glossy UI** - Beautiful glassmorphism design with light/dark themes
- 🔒 **Secure & Private** - All API keys encrypted, works offline, no telemetry
- 🐳 **Fully Dockerized** - One-command deployment with persistent storage
- 🛠️ **YAML Wizard** - Generate common resources (Deployment, Service, Ingress, ConfigMap)

---

## 🎯 Features

### Core Functionality

- **YAML Upload & Parsing**
  - Upload `.yaml` or `.yml` files or paste content directly
  - Multi-document YAML support (separated by `---`)
  - Identifies and structures each Kubernetes resource

- **Schema Validation**
  - Validates required fields and structure
  - Detects deprecated API versions
  - Provides actionable suggestions for fixes
  - Highlights errors, warnings, and informational issues

- **Rule-Based Explanation Engine (Offline)**
  - Maps 80+ field paths to human-readable explanations
  - Covers Deployments, Services, Pods, Ingresses, ConfigMaps, and more
  - Explains purpose, behavior, and cluster impact
  - Works completely offline without external dependencies

- **LLM Integration (Optional)**
  - Configure OpenAI, Anthropic Claude, or custom endpoints
  - API keys encrypted with AES-256 and persisted
  - Test connections before saving
  - Enhanced natural-language summaries
  - Multiple LLM configurations supported

- **YAML Wizard**
  - Guided creation for common resources
  - Step-by-step forms with validation
  - Generates production-ready YAML
  - Supports: Deployment, Service, Ingress, ConfigMap

- **Modern UI**
  - Glossy glassmorphism design
  - Light/Dark theme with smooth transitions
  - Monaco Editor with syntax highlighting
  - Responsive layout for desktop and mobile
  - Keyboard shortcuts and accessibility

---

## 🚀 Quick Start

### Prerequisites

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **OR** Node.js 18+ and Python 3.11+ for local development

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd kubernetes-yaml-explainer
   ```

2. **Start the application**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   
   Open your browser to: **http://localhost:8080**

That's it! The app is now running with persistent storage.

### Local Development

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend runs at: http://localhost:8000

#### Frontend

```bash
cd frontend
npm install
npm start
```

Frontend runs at: http://localhost:3000 (proxied to backend)

---

## 📝 Usage

### 1. Upload or Paste YAML

- Click **Upload** to select a `.yaml` file from your computer
- Or paste YAML content directly into the Monaco Editor
- Or use the **New YAML** wizard to generate manifests

### 2. Validate Your Manifest

- Click **Validate** to check for errors and warnings
- Review issues in the **Validation** tab
- Each issue includes the field path, message, and suggestion

### 3. Explain the Manifest

- Click **Explain** for rule-based explanations (works offline)
- Click **Explain with AI** for LLM-enhanced summaries (requires LLM setup)
- View results in three tabs:
  - **Summary** - High-level overview of all resources
  - **Field Details** - Field-by-field explanations
  - **Validation** - Errors, warnings, and suggestions

### 4. Export Your Work

- Click **Export** to download the YAML file
- Modified content in the editor is automatically saved to the download

---

## ⚙️ Configuration

### LLM Integration

1. Click the **Settings** icon (⚙️) in the top-right corner
2. Navigate to **LLM Configuration**
3. Click **Add New LLM Connection**
4. Fill in the details:
   - **Provider Name**: e.g., "OpenAI", "Anthropic", "Local Ollama"
   - **API Endpoint**: Full URL including path
     - OpenAI: `https://api.openai.com/v1/chat/completions`
     - Anthropic: `https://api.anthropic.com/v1/messages`
     - Ollama: `http://localhost:11434/api/chat`
   - **API Key**: Your authentication key
   - **Model Name**: e.g., `gpt-3.5-turbo`, `claude-3-sonnet-20240229`
5. Click **Test Connection** to verify
6. Click **Save** to persist (encrypted)

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Server Port
PORT=8080

# Database (SQLite by default)
DATABASE_URL=sqlite+aiosqlite:///./data/app.db

# Encryption Key (CHANGE THIS!)
ENCRYPTION_KEY=your-secure-random-key-here

# Optional: PostgreSQL
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/k8s_explainer
```

**⚠️ Security Note**: Always change the `ENCRYPTION_KEY` in production!

### Theme Preferences

- Click the **Sun/Moon** icon to toggle between light and dark themes
- Your preference is saved automatically

---

## 🏗️ Architecture

```
┌─────────────────┐
│   React SPA     │  ← Glossy UI with Monaco Editor
│  (Frontend)     │
└────────┬────────┘
         │ HTTP/REST
┌────────▼────────┐
│   FastAPI       │  ← YAML parsing, validation, explanations
│   (Backend)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────────┐
│ SQLite│ │ Optional  │
│  DB   │ │ LLM API   │
└───────┘ └───────────┘
```

### Components

- **Frontend**: React with Monaco Editor, Lucide icons, custom CSS
- **Backend**: FastAPI with async SQLAlchemy, ruamel.yaml parser
- **Database**: SQLite (default) or PostgreSQL for settings and LLM configs
- **Encryption**: AES-256 via cryptography library
- **LLM Support**: OpenAI, Anthropic, Ollama, and OpenAI-compatible APIs

---

## 📚 API Documentation

Once running, access interactive API docs:

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/parse` | POST | Parse YAML into structured resources |
| `/api/v1/validate` | POST | Validate manifest against schemas |
| `/api/v1/explain` | POST | Generate explanations (rule-based + optional LLM) |
| `/api/v1/generate` | POST | Generate YAML via wizard |
| `/api/v1/settings` | GET/PUT | User settings (theme, preferences) |
| `/api/v1/llm/config` | GET/POST/DELETE | Manage LLM connections |
| `/api/v1/llm/test` | POST | Test LLM connection |

### Example: Explain YAML

```bash
curl -X POST http://localhost:8080/api/v1/explain \
  -H "Content-Type: application/json" \
  -d '{
    "content": "apiVersion: v1\nkind: Pod\nmetadata:\n  name: nginx\nspec:\n  containers:\n  - name: nginx\n    image: nginx:latest",
    "use_llm": false
  }'
```

---

## 🗂️ Project Structure

```
kubernetes-yaml-explainer/
├── backend/
│   ├── app/
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── database.py        # Database configuration
│   │   ├── routes/            # API endpoints
│   │   │   ├── yaml_routes.py
│   │   │   └── settings_routes.py
│   │   └── services/          # Business logic
│   │       ├── yaml_service.py       # YAML parsing & validation
│   │       ├── explainer.py          # Rule-based explanations
│   │       ├── llm_service.py        # LLM integration
│   │       └── crypto_service.py     # Encryption
│   ├── main.py                # FastAPI app entry point
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── SettingsModal.js
│   │   │   └── WizardModal.js
│   │   ├── services/
│   │   │   └── api.js         # API client
│   │   ├── styles/
│   │   │   └── App.css        # Glassmorphism styles
│   │   ├── App.js             # Main app component
│   │   └── index.js           # React entry point
│   └── package.json           # Node dependencies
├── docker/
│   └── Dockerfile             # Multi-stage Docker build
├── k8s/                       # Example YAML files
├── docs/                      # Additional documentation
├── docker-compose.yml         # Docker Compose config
├── .env.example               # Environment template
└── README.md                  # This file
```

---

## 🧪 Example Manifests

Try these example manifests located in the `k8s/` directory:

- `example-deployment.yaml` - Nginx deployment with resource limits and probes
- `example-service.yaml` - LoadBalancer service
- `example-ingress.yaml` - Ingress with TLS

---

## 🔒 Security

- **API Key Encryption**: All LLM API keys are encrypted using AES-256 with PBKDF2 key derivation
- **Master Key**: Set `ENCRYPTION_KEY` environment variable (default is insecure)
- **CORS Protection**: Configurable allowed origins
- **Safe YAML Parsing**: Uses `ruamel.yaml` safe loader (no code execution)
- **No Telemetry**: Zero external requests unless LLM is explicitly configured
- **Rate Limiting**: (Coming soon) Protect LLM endpoints from abuse

---

## 🛠️ Troubleshooting

### Application won't start

```bash
# Check Docker logs
docker-compose logs -f

# Rebuild containers
docker-compose up --build
```

### Database errors

```bash
# Remove and recreate database
docker-compose down -v
docker-compose up
```

### LLM connection fails

- Verify endpoint URL is correct (include full path)
- Check API key is valid
- Ensure network connectivity to LLM provider
- Review backend logs for detailed error messages

### Frontend can't reach backend

- Ensure backend is running on port 8000 (dev) or 8080 (prod)
- Check CORS configuration in `backend/main.py`
- Verify proxy setting in `frontend/package.json`

---

## 🚧 Future Enhancements

- [ ] AI-assisted YAML generation ("create a Deployment for nginx with 3 replicas")
- [ ] Policy scanning integration (OPA, Kyverno)
- [ ] Diff/compare mode for multiple YAMLs
- [ ] Helm chart support
- [ ] Kustomize overlay explanations
- [ ] Export explanations as Markdown/PDF
- [ ] Offline Kubernetes API reference cache
- [ ] Multi-language support
- [ ] Browser extension
- [ ] VS Code extension

---

## 📄 License

This project is provided as-is for educational and practical use.

---

## 🙏 Acknowledgments

- **Kubernetes** community for comprehensive API documentation
- **Monaco Editor** for the excellent code editor
- **FastAPI** for the elegant Python web framework
- **React** for the powerful UI library

---

## 👤 Author

**Crafted with ♡ by RoarinPenguin**

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

<div align="center">

**⭐ If you find this project useful, please consider giving it a star! ⭐**

</div>
