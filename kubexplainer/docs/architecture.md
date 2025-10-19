# Architecture Documentation

## System Overview

The Kubernetes YAML Explainer is built as a modern web application with a clear separation between frontend and backend components.

```
┌─────────────────────────────────────────────────────────┐
│                    User's Browser                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │           React Single Page Application           │  │
│  │                                                   │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────┐ │  │
│  │  │   Monaco    │  │  Settings    │  │ Wizard  │ │  │
│  │  │   Editor    │  │    Modal     │  │  Modal  │ │  │
│  │  └─────────────┘  └──────────────┘  └─────────┘ │  │
│  │                                                   │  │
│  │              API Service Layer                    │  │
│  └───────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/REST (axios)
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  FastAPI Backend                        │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │              API Routes Layer                      │ │
│  │  ┌──────────────┐      ┌──────────────┐          │ │
│  │  │ YAML Routes  │      │Settings Routes│          │ │
│  │  └──────────────┘      └──────────────┘          │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │            Services Layer                          │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │ │
│  │  │  YAML    │ │Explainer │ │   LLM    │          │ │
│  │  │ Service  │ │  Engine  │ │ Service  │          │ │
│  │  └──────────┘ └──────────┘ └──────────┘          │ │
│  │  ┌──────────┐                                     │ │
│  │  │  Crypto  │                                     │ │
│  │  │ Service  │                                     │ │
│  │  └──────────┘                                     │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │           Data Layer                               │ │
│  │  ┌──────────────┐      ┌──────────────┐          │ │
│  │  │ SQLAlchemy   │      │   Models     │          │ │
│  │  │   (Async)    │      │  & Schemas   │          │ │
│  │  └──────────────┘      └──────────────┘          │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐           ┌────────▼────────┐
│  SQLite DB     │           │  External LLM   │
│  (Persistent)  │           │  API (Optional) │
│                │           │                 │
│ • Settings     │           │ • OpenAI        │
│ • LLM Configs  │           │ • Anthropic     │
│ • Recent Files │           │ • Ollama        │
└────────────────┘           └─────────────────┘
```

## Component Details

### Frontend (React)

**Technology Stack:**
- React 18
- Monaco Editor for YAML editing
- Axios for API communication
- Lucide React for icons
- Custom CSS with glassmorphism

**Key Components:**

1. **App.js**
   - Main application container
   - State management for YAML content, explanations, validation
   - Theme management
   - Integration with API services

2. **SettingsModal.js**
   - LLM configuration UI
   - API key management (input only, not displayed)
   - Connection testing
   - CRUD operations for LLM configs

3. **WizardModal.js**
   - Multi-step form for YAML generation
   - Resource type selection
   - Configuration forms for each resource type
   - YAML generation trigger

4. **API Service (api.js)**
   - Centralized API client
   - Axios instance with base configuration
   - Type-safe request functions

### Backend (FastAPI)

**Technology Stack:**
- FastAPI (async web framework)
- SQLAlchemy (async ORM)
- Pydantic (data validation)
- ruamel.yaml (YAML parsing)
- cryptography (encryption)
- httpx (HTTP client for LLM APIs)

**Architecture Layers:**

1. **Routes Layer** (`app/routes/`)
   - HTTP endpoint definitions
   - Request/response validation
   - Error handling
   - Route grouping by functionality

2. **Services Layer** (`app/services/`)
   - Business logic implementation
   - Stateless service classes
   - Reusable across routes

3. **Data Layer** (`app/models.py`, `app/database.py`)
   - SQLAlchemy models
   - Database session management
   - Async database operations

**Key Services:**

1. **YAMLService**
   - Parse YAML using safe loader
   - Extract Kubernetes resources
   - Validate structure and required fields
   - Check for deprecated API versions
   - Generate YAML from templates

2. **K8sExplainer**
   - Rule-based explanation engine
   - 80+ field explanations
   - Resource type descriptions
   - Field path matching with array support
   - Summary generation

3. **LLMService**
   - Multi-provider LLM support
   - OpenAI-compatible API client
   - Anthropic Claude client
   - Generic endpoint support
   - Connection testing
   - Context building for explanations

4. **CryptoService**
   - AES-256 encryption
   - PBKDF2 key derivation
   - API key encryption/decryption

### Database Schema

**UserSettings**
```
id: Integer (PK)
key: String (unique)
value: Text
created_at: DateTime
updated_at: DateTime
```

**LLMConnection**
```
id: Integer (PK)
name: String (unique)
endpoint: String
api_key_encrypted: Text
model_name: String (nullable)
custom_headers: Text (JSON)
is_active: Boolean
created_at: DateTime
updated_at: DateTime
```

**RecentFile**
```
id: Integer (PK)
filename: String
content: Text
explanation: Text (nullable)
created_at: DateTime
```

## Data Flow

### Explain YAML Flow

1. User pastes YAML in Monaco Editor
2. User clicks "Explain" or "Explain with AI"
3. Frontend sends POST to `/api/v1/explain` with content and use_llm flag
4. Backend:
   a. YAMLService parses YAML into documents
   b. Extracts Kubernetes resources
   c. K8sExplainer walks resource tree, generates field explanations
   d. If use_llm=true:
      - Queries database for active LLM config
      - Decrypts API key
      - Sends context to LLM
      - Combines LLM response with rule-based explanations
   e. Returns combined explanations
5. Frontend displays in three tabs:
   - Summary (high-level overview)
   - Details (field-by-field)
   - Validation (errors/warnings)

### LLM Configuration Flow

1. User opens Settings modal
2. Frontend loads existing configs from `/api/v1/llm/config`
3. User fills in new LLM connection form
4. User clicks "Test Connection"
5. Backend:
   a. LLMService sends minimal test request to endpoint
   b. Returns success/failure status
6. User clicks "Save"
7. Backend:
   a. CryptoService encrypts API key
   b. Stores in database
   c. If is_active=true, deactivates other configs
8. Frontend reloads configs, closes modal

## Security Model

### API Key Protection

1. **Input**: API key entered in plaintext in UI
2. **Transmission**: Sent over HTTPS to backend
3. **Storage**: 
   - Master key derived from ENCRYPTION_KEY env var
   - PBKDF2 with 100,000 iterations
   - Encrypted with AES-256 via Fernet
   - Stored as base64 string in database
4. **Usage**:
   - Decrypted on-demand when needed
   - Never returned to frontend
   - Only used for LLM API calls

### YAML Parsing Security

- Uses `ruamel.yaml` safe loader
- No code execution or object construction
- No eval() or unsafe deserialization
- Input size limits (handled by FastAPI)

### CORS Protection

- Configurable allowed origins
- Default: Allow all in development
- Production: Should specify exact origins

## Deployment Architecture

### Docker Deployment

```
┌─────────────────────────────────────────┐
│          Docker Container               │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │     Uvicorn ASGI Server           │ │
│  │     (Port 8080)                   │ │
│  │                                   │ │
│  │  ┌─────────────────────────────┐ │ │
│  │  │   FastAPI App               │ │ │
│  │  │                             │ │ │
│  │  │   Serves:                   │ │ │
│  │  │   • API endpoints           │ │ │
│  │  │   • Static frontend build   │ │ │
│  │  └─────────────────────────────┘ │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │     Persistent Volume             │ │
│  │     /app/data/                    │ │
│  │                                   │ │
│  │     • app.db (SQLite)             │ │
│  │     • User settings               │ │
│  │     • LLM configurations          │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
         ↑
         │ Volume Mount
         │
    Docker Volume (app-data)
```

### Multi-Stage Build

1. **Stage 1: Frontend Build**
   - Node.js 18 Alpine image
   - Install dependencies
   - Build React app
   - Output: `/app/frontend/build/`

2. **Stage 2: Backend + Frontend**
   - Python 3.11 Slim image
   - Install Python dependencies
   - Copy backend code
   - Copy frontend build from Stage 1
   - Expose port 8080
   - Run uvicorn server

### Scaling Considerations

**Current Architecture:**
- Single container deployment
- SQLite for simplicity
- In-memory session state

**For Production Scale:**
- Switch to PostgreSQL for shared state
- Deploy multiple backend replicas
- Add Redis for session storage
- Use external load balancer
- Separate frontend to CDN

## Extension Points

### Adding New Resource Types

1. Add explanation entries to `FIELD_EXPLANATIONS` in `explainer.py`
2. Add resource description to `RESOURCE_DESCRIPTIONS`
3. Add validation logic in `YAMLService._validate_*()` methods
4. Add generation template in `YAMLService._generate_*()` methods
5. Update wizard UI with new resource type option

### Adding New LLM Providers

LLMService supports any OpenAI-compatible API. For custom protocols:

1. Add provider-specific test method in `LLMService._test_*())`
2. Add provider-specific explain method in `LLMService._explain_*()`
3. Provider detection can be based on endpoint URL pattern

### Custom Validation Rules

1. Add validation function in `YAMLService`
2. Call from `validate_structure()` method
3. Return issues in standard format:
   ```python
   {
       "severity": "error|warning|info",
       "path": "field.path",
       "message": "Issue description",
       "suggestion": "How to fix"
   }
   ```

## Performance Characteristics

- **YAML Parsing**: O(n) where n is YAML size
- **Explanation Generation**: O(m) where m is number of fields
- **LLM Calls**: Network-bound, 1-5 seconds typical
- **Database Operations**: Sub-millisecond for SQLite
- **Frontend Rendering**: Optimized for 1000+ field explanations

## Browser Compatibility

- Chrome/Edge: 90+
- Firefox: 88+
- Safari: 14+
- Mobile browsers: iOS Safari 14+, Chrome Android 90+
