<div align="center">
<a href="https://github.com/Nilesh1735/OMNICREW-AI">
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:EC4730,100:B33A24&height=120&section=header" width="100%" />
</a>
</div>

# OMNICREW AI - Autonomous Web Extraction & Enrichment

<div align="center">
<p>An enterprise-grade, autonomous B2B lead generation platform that leverages a multi-agent AI crew to scrape, structure, and enrich web data without API usage caps. Built with a microservices architecture optimized for cost, scale, and real-time observability.</p>

<img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
<img src="https://img.shields.io/badge/React_19-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
<img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis" />
<img src="https://img.shields.io/badge/Snov.io-EC4730?style=for-the-badge&logo=mailgun&logoColor=white" alt="Snov.io" />

</div>

<br>

<div align="center">
<a href="https://github.com/Nilesh1735/OMNICREW-AI">
<img src="https://github-readme-stats.vercel.app/api/pin/?username=Nilesh1735&repo=OMNICREW-AI&theme=highcontrast&title_color=EC4730&icon_color=EC4730&border_color=EC4730" alt="OMNICREW-AI" />
</a>
</div>

## Overview

OMNICREW AI is not just a scraper; it is a closed-loop multi-agent system designed for B2B lead generation. The Researcher agent navigates the web, the Extraction Analyst formats the data into strict JSON schemas, and the backend enriches the data using the Snov.io API to find verified emails. 

Instead of relying on a single LLM provider, OMNICREW uses a 3-tier resilient routing pipeline (DeepSeek → Mistral AI → Google Gemini) to ensure high availability. To optimize for production scale and cost, the backend utilizes FastAPI BackgroundTasks for asynchronous processing, Upstash Redis for zero-token LLM caching, and strict JWT user isolation to ensure multi-tenant data security.

## Tech Stack

<div align="center">

<table>
<tr>
<td><b>Layer</b></td>
<td><b>Technology</b></td>
</tr>
<tr>
<td>AI / GenAI</td>
<td>CrewAI, LangChain, DeepSeek (V3), Mistral AI, Google Gemini, Snov.io API</td>
</tr>
<tr>
<td>Backend</td>
<td>FastAPI, Pydantic, WebSockets, BackgroundTasks</td>
</tr>
<tr>
<td>Frontend</td>
<td>React 19, Vite, TypeScript, Framer Motion</td>
</tr>
<tr>
<td>Data Layer</td>
<td>MySQL (Aiven), Upstash Redis</td>
</tr>
<tr>
<td>DevOps & Cloud</td>
<td>Docker, AWS S3, Render, Vercel</td>
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
<img src="https://skillicons.dev/icons?i=mysql" alt="MySQL" />
<img src="https://skillicons.dev/icons?i=git" alt="Git" />
<img src="https://skillicons.dev/icons?i=github" alt="GitHub" />

</div>

## Enterprise Architecture Upgrades

This repository includes production-grade, enterprise-level architectural implementations:

1. **B2B Email Enrichment (Snov.io API):** Features a custom CrewAI `BaseTool` that authenticates with Snov.io via OAuth 2.0 to autonomously find and verify B2B emails based on scraped names and company domains.
2. **JWT User Data Isolation:** Implements strict multi-tenant security. The backend decodes the JWT on every request to extract the `user_id`, ensuring Account A can never query or view Account B's leads and task history.
3. **Zero-Token Redis Caching:** Implements an MD5-hashed Upstash Redis cache for LLM responses. If a user submits a duplicate query, the system returns the cached result instantly, costing 0 API tokens.
4. **Asynchronous BackgroundTasks:** Decouples heavy AI processing from the FastAPI web server using native `BackgroundTasks`, preventing UI timeouts when multiple users initiate scraping tasks.
5. **Real-Time WebSocket Telemetry:** Streams live agent reasoning logs and pipeline status updates directly to the React frontend via WebSockets, giving stakeholders full observability into the AI's thought process.
6. **Resilient LLM Routing:** Architected a 3-tier LLM fallback pipeline (DeepSeek → Mistral AI → Gemini). If the primary provider fails or rate-limits, the pipeline automatically catches the exception and reroutes to the next provider, ensuring 99.9% task completion.
7. **AWS S3 Archival:** Automatically archives the raw JSON output of every successful task to an S3 bucket for audit and compliance purposes.

## System Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│               React 19 + Vite + Framer Motion (Vercel)         │ │
│  • Real-time LogViewer • Pipeline Graph • Expandable Data Grid │ │
└───────────────────────────────────┬─────────────────────────────┘
                                    ↓ (REST / WebSocket)
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Async)                       │
│ ┌────────────────────┐ ┌────────────────────┐ ┌──────────────┐ │
│ │ Security (SSRF)    │ │ JWT Auth & Isolate │ │ Rate Limiter │ │
│ └────────────────────┘ └────────────────────┘ └──────────────┘ │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Spawns BackgroundTask & Streams Logs via WebSockets         │ │
└───────────────────────────────────┬─────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Background Task                       │
│ ┌─────────┐    ┌──────────┐    ┌─────────┐    ┌──────────┐     │
│ │ Research│ -> │ Analyze  │ -> │ Enrich  │ -> │ Save/Achv│     │
│ └─────────┘    └──────────┘    └─────────┘    └──────────┘     │
└───────────────────────────────────┬─────────────────────────────┘
          ↓                 ↓                 ↓                 ↓
┌─────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  LLM Fallback   │ │ Snov.io API  │ │ MySQL (Aiven)│ │  AWS S3      │
│  1. DeepSeek    │ │ (Email Finder│ │ (Leads/Tasks)│ │  (Archival)  │
│  2. Mistral AI  │ └──────────────┘ └──────────────┘ └──────────────┘
│  3. Gemini      │
└─────────────────┘
```

## Project Structure

```text
OMNICREW-AI/
├── backend/                     # Python FastAPI Backend
│   ├── agents/                  # Autonomous AI agent logic
│   │   ├── crew.py              # CrewAI state machine & LLM routing
│   │   └── tools.py             # Web Scraper & Snov.io Email Finder Tool
│   ├── api/                     # REST API & WebSocket endpoints
│   │   ├── main.py              # FastAPI app initialization & CORS
│   │   ├── routes.py            # Task queueing, JWT Isolation & History
│   │   ├── auth.py              # Bcrypt Signup & JWT Login
│   │   └── websockets.py        # Redis Pub/Sub WebSocket streaming
│   ├── db/                      # Database connectors
│   │   └── mysql_client.py      # MySQL (Leads/Tasks) & Deduplication
│   ├── security/                # AppSec layers
│   │   ├── ssrf_blocker.py      # Server-Side Request Forgery protection
│   │   └── validators.py        # URL input validation
│   ├── tasks.py                 # BackgroundTask definition
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
│   └── mysql/init.sql           # MySQL schema (Leads, Tasks, Data Hash)
├── .env.example                 # Environment variable template
├── docker-compose.yml           # Docker orchestration (MySQL, Redis, API, Worker)
└── README.md                    # This file
```

## Getting Started

### Prerequisites
- **Docker & Docker Compose** (Recommended for local development)
- **API Keys:** DeepSeek (Primary), Mistral AI (Secondary), Google Gemini (Tertiary), Snov.io (for Email Enrichment)

### Installation & Local Deployment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Nilesh1735/OMNICREW-AI.git
   cd OMNICREW-AI
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   # AI Providers
   DEEPSEEK_API_KEY=your_deepseek_key_here
   MISTRAL_API_KEY=your_mistral_key_here
   GOOGLE_API_KEY=your_google_gemini_key_here

   # B2B Enrichment
   SNOV_CLIENT_ID=your_snov_client_id
   SNOV_CLIENT_SECRET=your_snov_client_secret

   # Databases
   MYSQL_HOST=...
   MYSQL_USER=...
   MYSQL_PASSWORD=...
   MYSQL_DB=...
   REDIS_URL=redis://localhost:6379/0

   # Security
   JWT_SECRET=your_super_secret_jwt_key
   ```

3. **Start the Microservices Stack:**
   ```bash
   docker-compose up --build
   ```

4. **Access the Application:**
   Open your browser and navigate to `http://localhost:3001`. Create an account, log in, and initiate an autonomous task!

## Free Tier Cloud Deployment

To deploy this application for $0.00, the architecture is split across free cloud providers:

1. **Frontend (Vercel):** Deploy the `frontend/` directory. Set `VITE_API_URL` to your Render backend URL.
2. **Backend (Render):** Deploy the `backend/` directory as a Web Service. Use `uvicorn api.main:app --host 0.0.0.0 --port $PORT` as the start command.
3. **Databases:** Use free tiers from Aiven (MySQL) and Upstash (Redis).

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
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:EC4730,100:B33A24&height=120&section=footer" width="100%" />
</a>
</div>
```