# API Documentation

## Base URL

```
http://localhost:8080/api/v1
```

## Endpoints

### YAML Operations

#### Parse YAML

Parse YAML content into structured Kubernetes resources.

**Endpoint:** `POST /parse`

**Request Body:**
```json
{
  "content": "apiVersion: v1\nkind: Pod\n..."
}
```

**Response:**
```json
{
  "success": true,
  "resources": [
    {
      "kind": "Pod",
      "api_version": "v1",
      "name": "my-pod",
      "namespace": "default",
      "content": { ... }
    }
  ],
  "error": null
}
```

#### Validate YAML

Validate YAML against Kubernetes schemas.

**Endpoint:** `POST /validate`

**Request Body:**
```json
{
  "content": "apiVersion: apps/v1\nkind: Deployment\n..."
}
```

**Response:**
```json
{
  "success": true,
  "valid": true,
  "issues": [
    {
      "severity": "warning",
      "path": "apiVersion",
      "message": "API version 'apps/v1beta1' is deprecated",
      "suggestion": "Use 'apps/v1' instead"
    }
  ],
  "error": null
}
```

#### Explain YAML

Generate explanations for YAML fields.

**Endpoint:** `POST /explain`

**Request Body:**
```json
{
  "content": "apiVersion: v1\nkind: Service\n...",
  "use_llm": false
}
```

**Response:**
```json
{
  "success": true,
  "resources": [ ... ],
  "explanations": [
    {
      "path": "spec.replicas",
      "value": 3,
      "explanation": "Defines the desired number of pod replicas...",
      "source": "rule-based"
    }
  ],
  "summary": "This manifest contains a Service...",
  "llm_used": false,
  "error": null
}
```

#### Generate YAML

Generate YAML manifest using wizard.

**Endpoint:** `POST /generate`

**Request Body:**
```json
{
  "resource_type": "deployment",
  "config": {
    "name": "my-app",
    "image": "nginx:latest",
    "replicas": 3,
    "port": 80
  }
}
```

**Response:**
```json
{
  "success": true,
  "yaml": "apiVersion: apps/v1\nkind: Deployment\n..."
}
```

### Settings Operations

#### Get All Settings

**Endpoint:** `GET /settings`

**Response:**
```json
{
  "theme": "dark",
  "default_llm": "openai"
}
```

#### Get Single Setting

**Endpoint:** `GET /settings/{key}`

**Response:**
```json
{
  "key": "theme",
  "value": "dark"
}
```

#### Update Setting

**Endpoint:** `PUT /settings`

**Request Body:**
```json
{
  "key": "theme",
  "value": "dark"
}
```

### LLM Configuration

#### Get All LLM Configs

**Endpoint:** `GET /llm/config`

**Response:**
```json
[
  {
    "id": 1,
    "name": "OpenAI",
    "endpoint": "https://api.openai.com/v1/chat/completions",
    "model_name": "gpt-3.5-turbo",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Create LLM Config

**Endpoint:** `POST /llm/config`

**Request Body:**
```json
{
  "name": "OpenAI",
  "endpoint": "https://api.openai.com/v1/chat/completions",
  "api_key": "sk-...",
  "model_name": "gpt-3.5-turbo",
  "is_active": true
}
```

#### Delete LLM Config

**Endpoint:** `DELETE /llm/config/{config_id}`

#### Activate LLM Config

**Endpoint:** `POST /llm/config/{config_id}/activate`

#### Test LLM Connection

**Endpoint:** `POST /llm/test`

**Request Body:**
```json
{
  "endpoint": "https://api.openai.com/v1/chat/completions",
  "api_key": "sk-...",
  "model_name": "gpt-3.5-turbo"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connection successful"
}
```

## Error Responses

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

HTTP Status Codes:
- `200` - Success
- `400` - Bad Request (validation error)
- `404` - Not Found
- `500` - Internal Server Error
