# Quick Start Guide

Get the Kubernetes YAML Explainer up and running in 5 minutes!

## Prerequisites

- **Docker** (20.10+) and **Docker Compose** (2.0+)

That's it! No other dependencies needed.

## Installation & Startup

### 1. Get the Code

```bash
# Clone or download the repository
cd kubernetes-yaml-explainer
```

### 2. Start the Application

```bash
# Start with Docker Compose
docker-compose up -d

# Check if it's running
docker-compose ps
```

Expected output:
```
NAME                IMAGE                              STATUS
app                 kubernetes-yaml-explainer-app      Up (healthy)
```

### 3. Access the Application

Open your browser to: **http://localhost:8080**

You should see the Kubernetes YAML Explainer interface with a modern glossy design!

## First Steps

### Try an Example

1. Click **"New YAML"** in the toolbar
2. Select **"Deployment"**
3. Fill in:
   - Name: `nginx-test`
   - Image: `nginx:latest`
   - Replicas: `3`
   - Port: `80`
4. Click **"Generate YAML"**
5. Click **"Explain"** to see the explanation
6. Switch between **Summary**, **Field Details**, and **Validation** tabs

### Upload Your Own YAML

1. Click **"Upload"** and select a `.yaml` file
2. Or paste YAML directly into the editor
3. Click **"Validate"** to check for errors
4. Click **"Explain"** for detailed explanations

### Enable AI Explanations (Optional)

1. Click the **⚙️ Settings** icon
2. Go to **"LLM Configuration"**
3. Click **"Add New LLM Connection"**
4. Configure your LLM provider:

   **For OpenAI:**
   ```
   Provider Name: OpenAI
   API Endpoint: https://api.openai.com/v1/chat/completions
   API Key: sk-your-api-key-here
   Model Name: gpt-3.5-turbo
   ```

   **For Local Ollama:**
   ```
   Provider Name: Ollama Local
   API Endpoint: http://host.docker.internal:11434/api/chat
   API Key: (leave empty)
   Model Name: llama2
   ```

5. Click **"Test Connection"**
6. Click **"Save"**
7. Now the **"Explain with AI"** button will be available!

## Stopping the Application

```bash
# Stop the container
docker-compose down

# Stop and remove all data (including database)
docker-compose down -v
```

## Restarting

```bash
# Restart after stopping
docker-compose up -d

# Rebuild after code changes
docker-compose up --build -d
```

## Troubleshooting

### Can't access http://localhost:8080

**Check if the container is running:**
```bash
docker-compose ps
```

**View logs:**
```bash
docker-compose logs -f
```

**Try a different port:**
Edit `docker-compose.yml` and change:
```yaml
ports:
  - "8081:8080"  # Changed from 8080:8080
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

### Database errors

**Reset the database:**
```bash
docker-compose down -v  # Removes volumes
docker-compose up -d
```

### LLM connection fails

**For OpenAI:**
- Verify your API key is correct
- Check you have credits/quota remaining
- Ensure the endpoint URL is exact: `https://api.openai.com/v1/chat/completions`

**For Local Ollama:**
- Ensure Ollama is running on your host machine
- Use `http://host.docker.internal:11434/api/chat` (not `localhost`)
- Check Ollama is accessible: `curl http://localhost:11434/api/tags`

### Theme or settings not persisting

This is expected if you use `docker-compose down -v` which removes volumes.
Use `docker-compose down` (without `-v`) to preserve data.

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out [Architecture Documentation](docs/architecture.md)
- Review [API Documentation](docs/api.md)
- Try the example manifests in the `k8s/` directory

## Common Use Cases

### Learning Kubernetes

1. Generate a resource using the wizard
2. Read the explanations to understand each field
3. Modify the YAML and see how explanations update
4. Try different resource types

### Validating Production Manifests

1. Upload your production YAML
2. Check the **Validation** tab for issues
3. Fix any errors or warnings
4. Export the corrected YAML

### Documentation

1. Upload a complex manifest
2. Use **"Explain with AI"** for natural language summary
3. Review field-by-field explanations
4. Share explanations with your team

## Getting Help

- Check logs: `docker-compose logs -f`
- View API docs: http://localhost:8080/docs
- Review issues in the repository

---

**Enjoy using Kubernetes YAML Explainer!** 🚀

*Crafted with ♡ by RoarinPenguin*
