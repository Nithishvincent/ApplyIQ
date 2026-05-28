<<<<<<< HEAD
# ApplyIQ 🚀

AI-powered Job Recommendation & Auto-Apply System — monorepo.

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| [Node.js](https://nodejs.org/) | ≥ 20 | Runtime for web/worker |
| [npm](https://npmjs.com/) | ≥ 10 | Package manager |
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Latest | PostgreSQL + Redis |
| [Python](https://python.org/) | ≥ 3.11 | FastAPI microservice |

> **Windows users:** Install Docker Desktop from https://www.docker.com/products/docker-desktop/
> After install, start Docker Desktop and ensure it's running in the system tray before running `npm run docker:up`.

---

## Quick Start

### 1. Install dependencies
=======
# 🎯 ApplyIQ: AI-Powered Job Recommendation & Auto-Apply System

ApplyIQ is a premium, end-to-end job application tracking, matching, and browser-automation platform built as a modern, high-performance monorepo. It automatically aggregates job listings, matches them to candidate profiles using vector embeddings, parses resumes, generates customized cover letters, and automates form submissions using browser automation.

---

## 🏛️ System Architecture

ApplyIQ is organized as a monorepo powered by **Turborepo**, separating core responsibilities into dedicated applications and shared packages:

```
ApplyIQ/
├── apps/
│   ├── web/          # Next.js CRM Dashboard & Admin Interface (React 18, Next 14.2)
│   ├── mobile/       # React Native / Expo Mobile App (Expo 56, Zustand, Paper)
│   ├── api/          # FastAPI Python Microservice (AI/ML processing, Python 3.10+)
│   └── worker/       # Node.js TypeScript Worker (BullMQ + Playwright auto-apply)
├── packages/
│   └── db/           # Shared Database client & Prisma schemas (PostgreSQL)
├── docker-compose.yml# Production & Development container orchestrations
└── package.json      # Workspace runner configuration
```

---

## ✨ Features

*   **📄 AI Resume Parsing:** Integrates with GPT-4o to parse resumes into structured JSON schemas, extracting skills, experience levels, contact details, and locations.
*   **🔍 Semantic Vector Search & Scoring:** Uses OpenAI embeddings stored in Pinecone to compare profiles and job descriptions, providing detailed scoring across multiple dimensions (skills, experience, domain, salary, culture).
*   **🤖 Browser-Automated Auto-Apply:** A BullMQ background worker utilizing Playwright to auto-fill application forms on modern ATS platforms (Greenhouse, Lever, Ashby, Workday, SmartRecruiters).
*   **📨 Automated Gmail Syncer:** Classifies incoming email communication from recruiters using AI, updating application statuses and pipelines in real-time.
*   **📊 Unified CRM Kanban & Analytics:** Kanban pipeline tracking applications from saved to applied, screening, interview, offer, and rejection phases, complete with weekly automated insights.
*   **🚀 Mobile Experience:** A native mobile application built on React Native & Expo with push notifications (FCM & Expo notifications) for live updates.
*   **💡 Skill Gap Analyzer:** Automatically tracks missing skills in matching jobs and suggests learning resources.

---

## 🛠️ Technology Stack

### Core Workspace & Orchestration
*   **Turborepo**: High-performance build system for JavaScript and TypeScript codebases.
*   **npm Workspaces**: Manages monorepo packages and workspaces.
*   **Docker & Docker Compose**: Simplifies service orchestration (PostgreSQL, Redis, web, api, worker).

### 🖥️ Frontend (Web App)
*   **Next.js 14.2 (App Router)** & **React 18**
*   **Tailwind CSS**: Utility-first styling.
*   **Radix UI** & **Shadcn UI components**: Sleek, modern design system.
*   **TanStack React Query**: State management and caching for asynchronous API requests.
*   **Recharts**: Premium data visualizations and weekly analytical snapshots.
*   **TipTap**: Modern rich-text editor for email drafting and cover letters.

### 📱 Mobile App
*   **React Native** & **Expo (SDK 56)**
*   **Zustand**: Lightweight, fast state management.
*   **React Native Paper**: Material Design components.
*   **Victory Native**: Data visualization and analytics on mobile.

### ⚙️ Python AI Microservice (API)
*   **FastAPI**: Modern, high-performance web framework.
*   **OpenAI SDK**: Resume parsing (Structured Outputs) and vector embeddings generation (using `text-embedding-3-small`).
*   **Pinecone Client**: Vector database connection for storing and query-matching jobs/profiles.
*   **Pydantic v2**: High-performance data validation.

### 🔄 Queue & Browser Automation (Worker)
*   **Playwright & Playwright Extra**: Controls browser instances to automate job submissions.
*   **Puppeteer Extra Stealth Plugin**: Evades detection and bot mitigation on major ATS platforms.
*   **BullMQ & Ioredis**: Robust Redis-backed queue system for managing asynchronous tasks (Gmail syncs, scraper tasks, R2 uploads, auto-applies).
*   **Mammoth & PDF-Parse**: Parsers for processing `.docx` and `.pdf` resume files.

### 🗄️ Database & Storage
*   **PostgreSQL**: Core relational database.
*   **Prisma ORM**: Modern database access client, migrations, and schema definition.
*   **Cloudflare R2**: S3-compatible object storage for application attachments, screenshots, and logs.

---

## 🚀 Getting Started & Local Installation

To run ApplyIQ on your machine, follow these instructions step by step.

### 📋 Prerequisites

Ensure you have the following installed:
*   [Node.js](https://nodejs.org/) (>= 20.0.0)
*   [npm](https://www.npmjs.com/) (>= 10.0.0)
*   [Docker](https://www.docker.com/) & Docker Compose
*   [Python](https://www.python.org/) (>= 3.10)

### ⚙️ Environment Configuration

1. Copy the example environment variables file at the root directory:
   ```bash
   cp .env.example .env
   ```
2. Open the `.env` file and fill in your API credentials (OpenAI, Pinecone, NextAuth, Database, Google OAuth, Cloudflare R2, etc.).

---

## 🏃 Running the Application

### Option A: Complete Docker Deployment (Recommended)

To spin up the entire microservices stack (databases, next.js app, fastapi api, worker) instantly:

```bash
# Start all containers in detached mode
npm run docker:up

# View containers logs
npm run docker:logs

# Shut down containers
npm run docker:down
```

Once running:
*   **Web Dashboard:** `http://localhost:3000`
*   **AI Microservice API:** `http://localhost:8000`
*   **Prisma Studio (Database GUI):** `http://localhost:5555`

---

### Option B: Run Services Locally (Development Mode)

If you are developing and need hot-reloading across the Next.js app, FastAPI backend, and Node.js queue worker, follow these steps:

#### Step 1: Start PostgreSQL & Redis Infrastructure
Start the database and cache container services:
```bash
docker compose up -d postgres redis
```

#### Step 2: Install Node.js Workspace Dependencies
Install dependencies at the root directory of the monorepo:
>>>>>>> b336b801566eac2ca93c8fa3de4e801391a1179c
```bash
npm install
```

<<<<<<< HEAD
### 2. Set up environment
```bash
copy .env.example .env
```
Edit `.env` and fill in:
- `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` (from [Google Cloud Console](https://console.cloud.google.com/))
- `NEXTAUTH_SECRET` (any 32+ character random string)
- `OPENAI_API_KEY`
- `PINECONE_API_KEY`

### 3. Start the database (requires Docker)
```bash
npm run docker:up
```
This starts **PostgreSQL** on port 5432 and **Redis** on port 6379.

### 4. Generate Prisma Client & run migrations
=======
#### Step 3: Install Playwright Web Browsers
The worker application requires browser binaries to automate job applications.
```bash
npx playwright install chromium
```

#### Step 4: Run Prisma Database Migrations
Generate the Prisma Client and migrate your local PostgreSQL database schema:
>>>>>>> b336b801566eac2ca93c8fa3de4e801391a1179c
```bash
npm run db:generate
npm run db:migrate
```

<<<<<<< HEAD
### 5. Start the web app
```bash
cd apps/web && npm run dev
```
Open http://localhost:3000

### 6. Start the FastAPI service (optional — for AI features)
```bash
cd apps/api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

---

## NPM Scripts (from root)

| Script | Description |
|--------|-------------|
| `npm run dev` | Start the Next.js dev server |
| `npm run build` | Build all apps for production |
| `npm run lint` | Lint all apps |
| `npm run db:generate` | Generate the Prisma Client SDK |
| `npm run db:migrate` | Run database migrations (needs Docker running) |
| `npm run db:push` | Push schema changes without migrations (faster for dev) |
| `npm run db:studio` | Open Prisma Studio GUI at http://localhost:5555 |
| `npm run db:reset` | Reset the database (drops all data) |
| `npm run docker:up` | Start PostgreSQL + Redis |
| `npm run docker:down` | Stop all Docker services |
| `npm run docker:up:all` | Start all Docker services including web/api/worker |

---

## Project Structure

```
ApplyIQ/
├── apps/
│   ├── web/          # Next.js 14 app (main UI + API routes)
│   ├── api/          # FastAPI Python microservice (AI/ML)
│   ├── worker/       # BullMQ background worker
│   └── mobile/       # Expo React Native app
├── packages/
│   └── db/           # Prisma schema + migrations
├── docker-compose.yml
├── .env.example
└── turbo.json
```

---

## Common Issues

### ❌ `Can't reach database server at localhost:5432`
Docker is not installed or not running.
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Open Docker Desktop and wait for it to start
3. Run `npm run docker:up`

### ❌ `npm run docker:up` — command not found
Docker is not installed. See above.

### ❌ `npm run db:migrate` fails immediately
The database isn't running. Run `npm run docker:up` first, wait ~10 seconds, then retry.

### ❌ `NEXTAUTH_URL` not set / OAuth redirect loop
Ensure `.env` has:
```
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=<any-32-char-string>
```

### ❌ After Google OAuth, redirected back to login
Make sure `http://localhost:3000/api/auth/callback/google` is in your Google OAuth app's **Authorized Redirect URIs** in the [Google Cloud Console](https://console.cloud.google.com/).
=======
#### Step 5: Setup Python AI Microservice (FastAPI)
Create a Python virtual environment and install the required modules:
```bash
# Navigate to the API microservice
cd apps/api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (CMD):
.\venv\Scripts\activate.bat
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Return to root directory
cd ../..
```

#### Step 6: Launch Applications
Now, run the Turborepo dev runner from the root workspace directory. This will start the Web App, Python API, and worker queue simultaneously:
```bash
npm run dev
```

*To start the React Native / Expo Mobile App local development environment:*
```bash
# Navigate to the mobile app workspace
cd apps/mobile

# Start Expo dev server
npm run start
```
From the Expo CLI menu, you can press `a` to run the Android emulator, `i` for the iOS simulator, or `w` for the web explorer.

---

## 🛠️ Available Root Scripts

Execute these scripts from the root workspace directory:

| Script | Description |
| :--- | :--- |
| `npm run dev` | Runs the workspace project apps locally in development mode via Turborepo |
| `npm run build` | Builds all applications for production |
| `npm run lint` | Lints all applications and packages |
| `npm run db:generate` | Generates the Prisma Client SDK |
| `npm run db:migrate` | Runs database migrations with Prisma |
| `npm run db:studio` | Opens Prisma Studio GUI to view the database |
| `npm run docker:up` | Starts all Docker services (DB, Redis, Web app, API, Worker) |
| `npm run docker:down` | Stops all Docker services |

---

## 🔒 Security & Automation Guardrails

By default, the worker runs in **Dry-Run mode** to protect you from unintended job submissions.
*   Check `DRY_RUN_MODE="true"` in your `.env`. When active, Playwright will load job boards, fill fields, perform match verification, log any captcha, and stop right before clicking the final submit button.
*   Set `DRY_RUN_MODE="false"` in production when you are ready to begin automated applications.
>>>>>>> b336b801566eac2ca93c8fa3de4e801391a1179c
