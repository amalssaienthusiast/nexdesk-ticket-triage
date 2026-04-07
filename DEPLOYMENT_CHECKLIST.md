# NexDesk Deployment Checklist

Complete checklist for deploying NexDesk to HuggingFace Spaces for the OpenEnv Competition.

## Pre-Deployment Checklist

### 1. Required Files

Ensure all these files exist in your project root:

```
nexdesk-ticket-triage/
├── Dockerfile              # Container configuration
├── pyproject.toml          # Package metadata
├── requirements.txt        # Python dependencies
├── openenv.yaml            # Environment manifest
├── README.md               # Documentation
├── SETUP.md                # Setup guide
├── inference.py            # Baseline script
├── models.py               # Pydantic models
├── client.py               # Python client
├── validate_deployment.py  # Validation script
└── server/
    ├── __init__.py         # Package exports
    ├── app.py              # FastAPI server
    ├── environment.py      # Core environment logic
    ├── graders.py          # Scoring functions
    ├── metrics.py          # Business metrics
    └── tickets.py          # Ticket dataset
```

### 2. File Validation

Run the validation script:

```bash
python validate_deployment.py
```

Expected output:
```
============================================================
Validation Summary
============================================================
  files           PASS
  syntax          PASS
  imports         PASS
  yaml            PASS
  graders         PASS
  docker          PASS
  server          PASS
  reset           PASS
  step            PASS

Total: 9/9 checks passed

All checks passed! Ready for deployment.
```

### 3. Docker Build Test

```bash
# Build the image
docker build -t nexdesk .

# Run the container
docker run -d -p 7860:7860 --name nexdesk-test nexdesk

# Test health endpoint
curl http://localhost:7860/health

# Expected response:
{"status":"healthy","env":"nexdesk-ticket-triage","version":"1.1.0",...}

# Stop and remove test container
docker stop nexdesk-test && docker rm nexdesk-test
```

### 4. Local Server Test

```bash
# Start server locally
uvicorn server.app:app --host 0.0.0.0 --port 7860

# Test all endpoints in another terminal

# Health check
curl http://localhost:7860/health

# List tasks
curl http://localhost:7860/tasks

# Reset environment
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "ticket_classify"}'

# Take a step (replace SESSION_ID with actual value)
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "priority": "high",
    "category": "network",
    "confidence": 0.85
  }'

# Get metrics
curl http://localhost:7860/metrics

# Get ROI projection
curl "http://localhost:7860/metrics/roi?monthly_volume=1000"
```

### 5. Inference Script Test

```bash
# Set environment variables
export HF_TOKEN="your-huggingface-token"
export ENV_BASE_URL="http://localhost:7860"
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"

# Run inference
python inference.py

# Expected output format:
[START] task=ticket_classify env=nexdesk-ticket-triage model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action={"priority":"high","category":"network","confidence":0.85} reward=0.85 done=true error=null
[END] success=true steps=1 score=0.85 rewards=0.85

...

==================================================
SUMMARY
==================================================
  ticket_classify: 0.85 [PASS]
  ticket_route: 0.78 [PASS]
  ticket_resolve: 0.65 [PASS]
  crisis_surge: 0.60 [PASS]

Total: 2.88 / 4
Average: 0.72
Success rate: 4/4
```

## HuggingFace Spaces Deployment

### 1. Create HuggingFace Account

If you don't have one:
1. Go to https://huggingface.co/join
2. Sign up with email or GitHub
3. Verify your email

### 2. Create Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in:
   - **Owner**: Your username
   - **Space Name**: `nexdesk-ticket-triage`
   - **License**: MIT
   - **Space SDK**: Docker
   - **Space Hardware**: CPU (free tier)
4. Click "Create Space"

### 3. Upload Files

Option 1: Using Git
```bash
# Clone the space
git clone https://huggingface.co/spaces/YOUR_USERNAME/nexdesk-ticket-triage
cd nexdesk-ticket-triage

# Copy your files
cp -r /path/to/your/nexdesk/* .

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

Option 2: Using HuggingFace CLI
```bash
# Install huggingface_hub
pip install huggingface_hub

# Login
huggingface-cli login

# Upload files
huggingface-cli upload YOUR_USERNAME/nexdesk-ticket-triage . .
```

Option 3: Web Interface
1. Go to your space: `https://huggingface.co/spaces/YOUR_USERNAME/nexdesk-ticket-triage`
2. Click "Files" tab
3. Click "Add file" -> "Upload files"
4. Upload all your files

### 4. Configure Space

Add the `openenv` tag to your space:
1. Go to Space Settings
2. Under "Tags", add: `openenv`
3. Save changes

### 5. Verify Deployment

Wait for the build to complete (check the "Logs" tab), then test:

```bash
# Replace with your actual space URL
SPACE_URL="https://your-username-nexdesk-ticket-triage.hf.space"

# Test health
curl $SPACE_URL/health

# Test reset
curl -X POST $SPACE_URL/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "ticket_classify"}'
```

### 6. Run Inference Against Deployed Space

```bash
export ENV_BASE_URL="https://your-username-nexdesk-ticket-triage.hf.space"
export HF_TOKEN="your-huggingface-token"

python inference.py
```

## Competition Submission Checklist

### Required for Round 1

- [ ] Environment deployed to HuggingFace Spaces
- [ ] Space tagged with `openenv`
- [ ] `/health` endpoint returns 200
- [ ] `/reset` endpoint returns valid session
- [ ] `/step` endpoint processes actions correctly
- [ ] `inference.py` runs without errors
- [ ] All 4 tasks produce scores in [0.0, 1.0]
- [ ] Dockerfile builds successfully
- [ ] README.md explains the environment
- [ ] `openenv.yaml` is valid

### Validation Script

Run the official validator (if provided):
```bash
curl -fsSL https://raw.githubusercontent.com/.../validate-submission.sh | bash -s -- https://your-space.hf.space
```

Or use the provided validation:
```bash
python validate_deployment.py
```

## Troubleshooting

### Docker Build Fails

```bash
# Clear Docker cache
docker builder prune -f

# Rebuild with no cache
docker build --no-cache -t nexdesk .

# Check Dockerfile syntax
docker run --rm -i hadolint/hadolint < Dockerfile
```

### Server Won't Start

```bash
# Check if port is in use
lsof -i :7860

# Kill existing process
kill -9 $(lsof -t -i :7860)

# Check Python syntax
python -m py_compile server/app.py
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check for circular imports
python -c "import server.app"
```

### Inference Returns 0.0 Rewards

1. Check LLM is returning valid JSON
2. Verify HF_TOKEN is set correctly
3. Check server logs for errors
4. Test with a simple action manually:
   ```bash
   curl -X POST http://localhost:7860/step \
     -H "Content-Type: application/json" \
     -d '{"session_id": "...", "priority": "high", "category": "network"}'
   ```

## Performance Optimization

### For HuggingFace Spaces (2 vCPU, 8GB RAM)

1. **Optimize Dockerfile**:
   - Use slim Python image
   - Minimize layers
   - Clean up after install

2. **Server Configuration**:
   - Single worker is fine for HF Spaces
   - Use `--workers 1` in uvicorn

3. **Session Management**:
   - Sessions auto-expire after 1 hour
   - Old sessions are cleaned up automatically

## Final Check Before Submitting

```bash
# 1. Clean up any test files
rm -rf __pycache__ *.pyc .pytest_cache

# 2. Verify all files are committed
git status

# 3. Run final validation
python validate_deployment.py

# 4. Test inference one more time
python inference.py

# 5. Check output format matches requirements
grep -E "^\[START\]|^\[STEP\]|^\[END\]" inference_output.log

# 6. Verify space is live
curl https://your-username-nexdesk-ticket-triage.hf.space/health
```

## Submission

1. **Submit your HuggingFace Space URL**
2. **Include your GitHub repository** (if applicable)
3. **Document any special instructions**

Good luck!
