# NexDesk Setup Guide

Complete setup and deployment guide for the NexDesk IT Ticket Triage environment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Local Development](#local-development)
4. [Docker Deployment](#docker-deployment)
5. [Running Inference](#running-inference)
6. [API Reference](#api-reference)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Python 3.11+** (for local development)
- **Docker** (for containerized deployment)
- **API Key** for LLM inference (HuggingFace token or OpenAI-compatible API)

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Build the image
docker build -t nexdesk .

# Run the server
docker run -p 7860:7860 nexdesk

# Test the server
curl http://localhost:7860/health
```

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn server.app:app --host 0.0.0.0 --port 7860 --reload

# Test the server
curl http://localhost:7860/health
```

---

## Local Development

### Project Structure

```
nexdesk/
├── server/                 # FastAPI server
│   ├── __init__.py        # Package exports
│   ├── app.py             # FastAPI endpoints
│   ├── environment.py     # Core environment logic
│   ├── graders.py         # Scoring functions
│   ├── metrics.py         # Business metrics tracking
│   └── tickets.py         # Ticket dataset (25 tickets)
├── client.py              # Typed Python client
├── models.py              # Pydantic data models
├── inference.py           # Baseline LLM agent
├── openenv.yaml           # Environment manifest
├── Dockerfile             # Container config
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Package metadata
└── README.md              # Documentation
```

### Installing as a Package

```bash
# Install in development mode
pip install -e .

# Now you can import the client
from nexdesk import NexDeskClient

client = NexDeskClient("http://localhost:7860")
result = client.reset("ticket_classify")
```

### Running Tests

```bash
# Start the server first
uvicorn server.app:app --host 0.0.0.0 --port 7860 &

# Test all endpoints
curl http://localhost:7860/health
curl -X POST http://localhost:7860/reset -H "Content-Type: application/json" -d '{"task": "ticket_classify"}'
```

---

## Docker Deployment

### Building the Image

```bash
# Standard build
docker build -t nexdesk .

# With build args (optional)
docker build -t nexdesk:v1.1.0 .
```

### Running the Container

```bash
# Basic run
docker run -p 7860:7860 nexdesk

# Detached mode
docker run -d -p 7860:7860 --name nexdesk-server nexdesk

# With resource limits
docker run -d -p 7860:7860 --memory=512m --cpus=1 nexdesk
```

### Docker Compose (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  nexdesk:
    build: .
    ports:
      - "7860:7860"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7860/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with:

```bash
docker-compose up -d
```

---

## Running Inference

### Environment Variables

```bash
# Required for LLM calls
export HF_TOKEN="your-huggingface-token"

# Optional configuration
export API_BASE_URL="https://router.huggingface.co/v1"  # LLM endpoint
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"           # Model to use
export ENV_BASE_URL="http://localhost:7860"              # NexDesk server
```

### Running the Baseline Agent

```bash
# Ensure server is running first
uvicorn server.app:app --port 7860 &

# Run inference
python inference.py
```

### Expected Output

```
[START] task=ticket_classify env=nexdesk-ticket-triage model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action={"priority":"high","category":"network"} reward=0.85 done=true error=null
[END] success=true steps=1 score=0.85 rewards=0.85

[START] task=ticket_route env=nexdesk-ticket-triage model=Qwen/Qwen2.5-72B-Instruct
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

---

## API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/reset` | POST | Start new episode |
| `/step` | POST | Take action |
| `/state` | POST | Get session state |
| `/metrics` | GET | Business metrics |
| `/metrics/roi` | GET | ROI projections |

### Reset Endpoint

```bash
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "ticket_classify"}'
```

Response:

```json
{
  "observation": {
    "ticket_id": "TKT-001",
    "subject": "VPN not connecting after update",
    "description": "Since the latest Windows update, I cannot connect to the corporate VPN...",
    "submitter": "john.smith@company.com",
    "department": "Engineering",
    "task": "ticket_classify",
    "step": 0,
    "max_steps": 1,
    "sla_deadline_minutes": 60,
    "stress_level": 0.5
  },
  "session_id": "abc123-..."
}
```

### Step Endpoint

```bash
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc123-...",
    "priority": "high",
    "category": "network",
    "confidence": 0.85
  }'
```

Response:

```json
{
  "observation": {...},
  "reward": 0.85,
  "done": true,
  "info": {
    "step": 1,
    "total_reward": 0.85,
    "score_breakdown": {
      "priority": 0.5,
      "category": 0.5,
      "confidence_bonus": 0.05,
      "time_penalty": 0.0
    }
  }
}
```

---

## Configuration

### Task Configuration

| Task | Steps | Max Reward | SLA (min) | Difficulty |
|------|-------|------------|-----------|------------|
| `ticket_classify` | 1 | 1.0 | 60 | Easy |
| `ticket_route` | 2 | 1.0 | 30 | Medium |
| `ticket_resolve` | 3 | 1.0 | 20 | Hard |
| `crisis_surge` | 10 | 1.0* | 5 | Hard |

*Crisis surge raw max is 1.2, normalized to 1.0 in scoring.

### Scoring Breakdown

**ticket_classify (1.0 max)**
- Priority: 0.5 (exact match) / 0.25 (acceptable)
- Category: 0.5 (exact match) / 0.25 (acceptable)

**ticket_route (1.0 max)**
- Step 1 (0.85): Priority (0.25) + Category (0.25) + Team (0.35)
- Step 2 (0.15): Affected system

**ticket_resolve (1.0 max)**
- Step 1 (0.45): Priority (0.15) + Category (0.15) + Team (0.15)
- Step 2 (0.30): Affected system (0.10) + First response (0.20)
- Step 3 (0.25): Resolution steps (0.15) + SLA estimate (0.10)

**crisis_surge (1.2 max raw, normalized to 1.0)**
- Per ticket (0.12): Priority (0.03) + Category (0.03) + Team (0.04) + Bonuses

### Modifiers

- **Time Penalty**: Up to -40% for exceeding SLA
- **SLA Breach Penalty**: -5% per breach (cumulative, max -30%)
- **Confidence Bonus**: +5% for well-calibrated, -10% for overconfident

---

## Troubleshooting

### Common Issues

**Server won't start**
```bash
# Check if port is in use
lsof -i :7860

# Kill existing process
kill -9 $(lsof -t -i :7860)
```

**Docker build fails**
```bash
# Clear Docker cache
docker builder prune -f

# Rebuild
docker build --no-cache -t nexdesk .
```

**Inference returns 0.0 rewards**
- Check LLM is returning valid JSON
- Verify HF_TOKEN is set correctly
- Check server logs for errors

**ModuleNotFoundError**
```bash
# Ensure you're in the project directory
cd /path/to/nexdesk

# Reinstall dependencies
pip install -r requirements.txt
```

### Debug Mode

Enable verbose logging:

```bash
# Run server with debug
uvicorn server.app:app --port 7860 --log-level debug

# Run inference with debug
python inference.py 2>&1 | tee inference.log
```

### Health Check

```bash
# Quick health check
curl http://localhost:7860/health

# Expected response
{"status":"ok"}
```

---

## Support

For issues or questions:
- Check the [README.md](README.md) for overview
- Review [openenv.yaml](openenv.yaml) for specifications
- Open an issue on the repository

---

*NexDesk v1.1.0 - OpenEnv Competition Entry*
