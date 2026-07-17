<div align="center">
<a href="https://github.com/Nilesh1735/OmniCrew-AI">
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:7dd3fc,100:0ea5e9&height=120&section=header" width="100%" />
</a>
</div>

# OmniCrew AI - Autonomous Web Extraction

<div align="center">
<p>An enterprise-grade, autonomous data extraction platform that leverages a multi-agent AI crew to navigate, scrape, and structure web data without API usage caps. Built with a microservices architecture optimized for cost, scale, and real-time observability.</p>

<img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
<img src="https://img.shields.io/badge/React_19-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
<img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis" />
<img src="https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white" alt="Celery" />

</div>

<br>

<div align="center">
<a href="https://github.com/Nilesh1735/OmniCrew-AI">
<img src="https://github-readme-stats.vercel.app/api/pin/?username=Nilesh1735&repo=OmniCrew-AI&theme=nord&title_color=7dd3fc&icon_color=7dd3fc&border_color=7dd3fc" alt="OmniCrew-AI" />
</a>
</div>

## Overview

OmniCrew AI is not just a scraper; it is a closed-loop multi-agent system. The Researcher agent navigates the web, the Extraction Analyst formats the data into strict JSON schemas, and the Manager validates the output. 

Instead of relying on a single LLM provider, OmniCrew uses a resilient routing pipeline (Mistral AI to OpenAI to Local Ollama) to ensure high availability. To optimize for production scale and cost, the backend utilizes Celery and Redis for asynchronous task queues, Redis LLM caching to bypass duplicate API calls (saving tokens), and semantic deduplication to maintain clean database records.

## Tech Stack

<div align="center">

<table>
<tr>
<td><b>Layer</b></td>
<td><b>Technology</b></td>
</tr>
<tr>
<td>AI / GenAI</td>
<td>CrewAI, LangChain, Mistral AI, OpenAI, Ollama</td>
</tr>
<tr>
<td>Backend</td>
<td>FastAPI, Celery, Uvicorn, Pydantic</td>
</tr>
<tr>
<td>Frontend</td>
<td>React 19, Vite, TypeScript, Framer Motion, ReactFlow</td>
</tr>
<tr>
<td>Data Layer</td>
<td>PostgreSQL, MySQL, Redis</td>
</tr>
<tr>
<td>DevOps & Cloud</td>
<td>Docker, Docker Compose, AWS S3, Render, Vercel</td>
</tr>
</table>

<br>

<img src="https://skillicons.dev/icons?i=python" alt="Python" />
<img src="https://skillicons.dev/icons?i=fastapi" alt="FastAPI" />
<img src="https://skillicons.dev/icons?i=react" alt="React" />
<img src="https://skillicons.dev/icons?i=redis" alt="Redis" />
<img src="https://skillicons.dev/icons?i=docker" alt="Docker" />
<img src="https://skillicons.dev/icons?i=aws" alt="AWS" />
<br><br>
<img src="https://skillicons.dev/icons?i=typescript" alt="TypeScript" />
<img src="https://skillicons.dev/icons?i=postgres" alt="PostgreSQL" />
<img src="https://skillicons.dev/icons?i=mysql" alt="MySQL" />
<img src="https://skillicons.dev/icons?i=git" alt="Git" />
<img src="https://skillicons.dev/icons?i=github" alt="GitHub" />

</div>

## Enterprise Architecture Upgrades

This repository includes production-grade, enterprise-level architectural implementations:

1. **Multi-Agent CrewAI Orchestration:** Utilizes a sequential pipeline where a Web Researcher gathers data and an Extraction Analyst strictly formats it into Pydantic schemas.
2. **Intelligent LLM Routing & Fallbacks:** Dynamically routes requests through Mistral AI, OpenAI, and Local Ollama. If a provider fails or rate-limits, the pipeline automatically reroutes without dropping the task.
3. **Zero-Token Redis Caching:** Implements an MD5-hashed Redis cache for LLM responses. If a user submits a duplicate query, the system returns the cached result in under 1 second, costing 0 API tokens.
4. **Asynchronous Task Queues (Celery):** Decouples heavy AI processing from the FastAPI web server using Celery workers and Redis, preventing UI timeouts when multiple users initiate scraping tasks.
5. **Semantic Deduplication:** Computes an MD5 hash of the extracted entity name and data payload. Uses INSERT IGNORE in MySQL to prevent duplicate records from polluting the database.
6. **Real-Time Telemetry (Redis Pub/Sub):** Streams live agent reasoning logs and pipeline status updates directly to the React frontend via WebSockets.
7. **AWS S3 Archival:** Automatically archives the raw JSON output of every successful task to an S3 bucket for audit and compliance purposes.

## System Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│               React 19 + Vite + Framer Motion (Port 3001)      │ │
│  • Real-time LogViewer • Pipeline Graph • Expandable Data Grid │ │
└───────────────────────────────────┬─────────────────────────────┘
                                    ↓ (REST / WebSocket)
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Async)                       │
│ ┌────────────────────┐ ┌────────────────────┐ ┌──────────────┐ │
│ │ Security (SSRF)    │ │ Rate Limiter       │ │ Pydantic     │ │
│ └────────────────────┘ └────────────────────┘ └──────────────┘ │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Pushes Task to Celery Queue & Streams Logs via Redis Pub/Sub│ │
└───────────────────────────────────┬─────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Celery Worker (Background)                    │
│ ┌─────────┐    ┌──────────┐    ┌─────────┐    ┌──────────┐     │
│ │ Research│ -> │ Analyze  │ -> │ Validate│ -> │ Save/Achv│     │
│ └─────────┘    └──────────┘    └─────────┘    └──────────┘     │
└───────────────────────────────────┬─────────────────────────────┘
          ↓                 ↓                 ↓                 ↓
┌─────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  LLM Fallback   │ │ Redis Cache  │ │ MySQL/Postgres│ │  AWS S3      │
│  1. Mistral     │ │ (Zero Token) │ │ (Dual DBs)   │ │  (Archival)  │
│  2. OpenAI      │ └──────────────┘ └──────────────┘ └──────────────┘
│  3. Ollama      │
└─────────────────┘
```

## Project Structure

```text
autobrowse-ai/ (OmniCrew AI)
├── backend/                     # Python FastAPI & Celery Backend
│   ├── agents/                  # Autonomous AI agent logic
│   │   ├── crew.py              # CrewAI state machine, LLM routing & Caching
│   │   └── tools.py             # Playwright/Requests web scraper tool
│   ├── api/                     # REST API & WebSocket endpoints
│   │   ├── main.py              # FastAPI app initialization & CORS
│   │   ├── routes.py            # Task queueing & History endpoints
│   │   ├── auth.py              # PostgreSQL JWT Authentication
│   │   └── websockets.py        # Redis Pub/Sub WebSocket streaming
│   ├── db/                      # Database connectors
│   │   ├── mysql_client.py      # MySQL (Leads/Tasks) & Deduplication
│   │   └── postgres_client.py   # PostgreSQL (Users/Auth)
│   ├── security/                # AppSec layers
│   │   ├── ssrf_blocker.py      # Server-Side Request Forgery protection
│   │   └── validators.py        # URL input validation
│   ├── tasks.py                 # Celery background task definition
│   ├── celery_worker.py         # Celery app initialization
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile               # Backend container build
├── frontend/                    # React 19 + Vite + TypeScript Frontend
│   ├── src/                     # React source code
│   │   ├── App.tsx              # Main dashboard & 80/20 layout logic
│   │   ├── components/          # AuthScreen, LeadTable, PipelineGraph
│   │   └── hooks/               # useLeads, useWebSocket
│   ├── Dockerfile               # Frontend Nginx container build
│   └── package.json             # Node dependencies
├── init/                        # Database initialization scripts
│   ├── mysql/init.sql           # MySQL schema (Leads, Tasks, Data Hash)
│   └── postgres/init.sql        # PostgreSQL schema (Users, Sessions)
├── .env.example                 # Environment variable template
├── docker-compose.yml           # Docker orchestration (MySQL, Postgres, Redis, API, Worker)
└── README.md                    # This file
```

## Getting Started

### Prerequisites
- **Docker & Docker Compose** (Recommended for local development)
- **API Keys:** Mistral AI (Primary), OpenAI (Secondary)

### Installation & Local Deployment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Nilesh1735/OmniCrew-AI.git
   cd OmniCrew-AI
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   # AI Providers
   MISTRAL_API_KEY=your_mistral_key_here
   OPENAI_API_KEY=your_openai_key_here

   # LLMOps (Optional)
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_langsmith_key
   LANGCHAIN_PROJECT=omnicrew-ai-prod

   # AWS S3 (Optional)
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   AWS_STORAGE_BUCKET_NAME=your_bucket
   ```

3. **Start the Microservices Stack:**
   ```bash
   docker-compose up --build
   ```
   *(This spins up MySQL, PostgreSQL, Redis, the FastAPI Backend, the Celery Worker, and the React Frontend).*

4. **Access the Application:**
   Open your browser and navigate to `http://localhost:3001`. Create an account, log in, and initiate an autonomous task!

## Free Tier Cloud Deployment

To deploy this application for $0.00, the architecture is split across free cloud providers:

1. **Frontend (Vercel):** Deploy the `frontend/` directory. Set `VITE_API_URL` to your Render backend URL.
2. **Backend (Render):** Deploy the `backend/` directory as a Web Service. Use `uvicorn api.main:app --host 0.0.0.0 --port $PORT` as the start command.
3. **Databases:** Use free tiers from Supabase (PostgreSQL), Aiven (MySQL), and Upstash (Redis).

*(Note: For the free Render tier, Celery is disabled. The backend uses FastAPI's native BackgroundTasks to process the crew asynchronously).*

## Connect With Me

<div align="center">
<a href="https://www.linkedin.com/in/nilesh-raj-nr1735/">
<img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" />
</a>
<a href="mailto:nileshraj1735@gmail.com">
<img src="https://img.shields.io/badge/Email-Contact-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email" />
</a>
</div>

<br>

<div align="center">
<a href="https://github.com/Nilesh1735">
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:7dd3fc,100:0ea5e9&height=120&section=footer" width="100%" />
</a>
</div>