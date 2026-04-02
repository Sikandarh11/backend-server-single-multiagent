# Agentic ML Experiment Assistant — Backend

> **Frontend repository:** [Sikandarh11/agentic-ml-experiment-assistant](https://github.com/Sikandarh11/agentic-ml-experiment-assistant)  
> **Live demo:** [agentic-ml-experiment-assistant.vercel.app](https://agentic-ml-experiment-assistant.vercel.app/)

---

A **FastAPI** backend that powers a conversational AI assistant capable of running in two distinct modes:

| Mode | Description |
|------|-------------|
| **Single-agent** | A focused Weather Agent that fetches real-time weather data and can send weather-report emails |
| **Multi-agent** | A Triage Agent that intelligently routes conversations to specialist agents (Sales or Refunds) |

The core orchestration engine (`Swarm`) is a lightweight, custom implementation inspired by OpenAI's Swarm pattern — agents can hand off control to each other mid-conversation and invoke real tools like weather lookups and SMTP email delivery.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Local Development](#local-development)
- [Docker](#docker)
- [Deployment (Vercel)](#deployment-vercel)
- [API Reference](#api-reference)
- [Agent Definitions](#agent-definitions)
- [CLI Examples](#cli-examples)

---

## Features

- ⚡ **Real-time weather** via OpenWeatherMap API (current temperature, feels-like, humidity, conditions)
- 📧 **Real email delivery** via SMTP (configurable — works with Gmail, SendGrid, etc.)
- 🤖 **Single-agent mode** — one-shot Weather Agent handles weather queries and emails
- 🔀 **Multi-agent mode** — Triage → Sales / Refunds agents with automatic hand-offs
- 🔧 **Tool-calling** — agents invoke Python functions directly; results feed back into the conversation
- 🌐 **CORS-ready** — configurable allowed origins via `CORS_ORIGINS` env var
- 🐳 **Docker** support for Hugging Face Spaces or any container platform
- ▲ **Vercel** serverless deployment via `api/index.py` shim

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                  │
│         agentic-ml-experiment-assistant.vercel.app       │
└────────────────────────┬────────────────────────────────┘
                         │ POST /chat  {mode, messages}
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI  (main.py)                      │
│                                                         │
│  mode="single"  ──►  Weather Agent                      │
│                           │                             │
│                    ┌──────┴──────┐                      │
│                    │             │                      │
│               get_weather   send_email                  │
│             (OpenWeatherMap)  (SMTP)                    │
│                                                         │
│  mode="multi"   ──►  Triage Agent                       │
│                      │         │                        │
│               Sales Agent   Refunds Agent               │
│                             │         │                 │
│                      process_refund  apply_discount     │
└─────────────────────────────────────────────────────────┘
                         │
                    Swarm Engine
              (agent.py — orchestrates
               tool calls & hand-offs)
```

---

## Project Structure

```
.
├── main.py                  # FastAPI app, /health & /chat endpoints
├── agent.py                 # Swarm engine, Agent/Response/Result models
├── agents.py                # All agent definitions (weather, triage, sales, refunds)
├── schemas.py               # Pydantic request/response schemas
├── weather.py               # get_weather() — OpenWeatherMap integration
├── email_tools.py           # send_email() — SMTP integration
├── single_agent_example.py  # CLI demo: single Weather Agent
├── multi_agent_example.py   # CLI demo: multi-agent (triage/sales/refunds)
├── api/
│   └── index.py             # Vercel serverless entry-point (re-exports app)
├── Dockerfile               # Container image (Python 3.11-slim, port 7860)
├── vercel.json              # Vercel build & routing config
└── requirements.txt         # Python dependencies
```

---

## Prerequisites

- Python **3.11+**
- An **OpenAI API key** (`gpt-4o` is the default model)
- An **OpenWeatherMap API key** (free tier is sufficient)
- SMTP credentials for email delivery (e.g. Gmail App Password, SendGrid)

---

## Environment Variables

Create a `.env` file in the project root (never commit this file):

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Weather
OPENWEATHER_API_KEY=your_openweathermap_key

# SMTP email delivery
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=you@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=you@gmail.com
SMTP_USE_TLS=true          # true = STARTTLS (port 587), false = SSL (port 465)

# CORS (comma-separated list; defaults to localhost dev ports if omitted)
CORS_ORIGINS=https://agentic-ml-experiment-assistant.vercel.app,http://localhost:5173
```

> **Gmail tip:** Enable 2-FA on your Google account and generate an [App Password](https://myaccount.google.com/apppasswords) to use as `SMTP_PASSWORD`.

---

## Local Development

```bash
# 1. Clone the repo
git clone https://github.com/Sikandarh11/backend-server-single-multiagent.git
cd backend-server-single-multiagent

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your .env file (see Environment Variables above)

# 5. Start the development server
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## Docker

The image is designed for **Hugging Face Spaces** (port 7860) but works anywhere.

```bash
# Build
docker build -t agent-backend .

# Run
docker run -p 7860:7860 --env-file .env agent-backend
```

The server listens on `0.0.0.0:7860` inside the container.

---

## Deployment (Vercel)

The `vercel.json` routes all traffic through `api/index.py`, which simply re-exports the FastAPI `app` object from `main.py`.

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

Set each variable from the [Environment Variables](#environment-variables) section in your Vercel project dashboard under **Settings → Environment Variables**.

---

## API Reference

### `GET /health`

Health check — returns `{"ok": true}` when the server is running.

---

### `POST /chat`

Run a conversation turn through the agent system.

**Request body**

```jsonc
{
  "mode": "single",          // "single" (Weather Agent) | "multi" (Triage system)
  "messages": [
    { "role": "user", "content": "What's the weather in Tokyo?" }
  ],
  "max_turns": 6             // optional, default 6 — caps agentic loop iterations
}
```

**Response body**

```jsonc
{
  "activeAgent": "Weather Agent",
  "messages": [
    {
      "role": "tool",
      "content": "{\"location\": \"Tokyo, JP\", \"temperature_c\": 18.4, ...}",
      "sender": "Weather Agent",
      "tool_name": "get_weather",
      "tool_call_id": "call_abc123"
    },
    {
      "role": "assistant",
      "content": "The current temperature in Tokyo is 18.4 °C with clear skies.",
      "sender": "Weather Agent"
    }
  ]
}
```

**Example — send a weather report by email**

```jsonc
// POST /chat
{
  "mode": "single",
  "messages": [
    {
      "role": "user",
      "content": "Send the weather in London to alice@example.com"
    }
  ]
}
```

**Example — multi-agent refund flow**

```jsonc
// POST /chat
{
  "mode": "multi",
  "messages": [
    { "role": "user", "content": "I want to return item_42, it was too expensive." }
  ]
}
```

---

## Agent Definitions

### Single-agent mode — `Weather Agent`

| Property | Value |
|----------|-------|
| Model | `gpt-4o` |
| Tools | `get_weather`, `send_email`, `send_weather_report_email` |
| Behaviour | Fetches current weather for any city; can compose and send a formatted weather-report email via SMTP |

### Multi-agent mode

| Agent | Tools / Transfers | Behaviour |
|-------|------------------|-----------|
| **Triage Agent** | `transfer_to_sales`, `transfer_to_refunds` | Entry point — routes every message to the correct specialist; never answers directly |
| **Sales Agent** | `transfer_back_to_triage` | Enthusiastically sells bees 🐝; hands back off-topic queries to Triage |
| **Refunds Agent** | `process_refund`, `apply_discount`, `transfer_back_to_triage` | Handles returns; offers a discount before processing a full refund |

---

## CLI Examples

Two standalone scripts let you test agents from the terminal without the HTTP layer.

**Single agent (Weather)**

```bash
python single_agent_example.py
# Ask me how is the weather today in Brussels?
# User: What's the weather in Paris?
```

**Multi-agent (Triage / Sales / Refunds)**

```bash
python multi_agent_example.py
# User: I want a refund for item_99, it was too expensive.
```
