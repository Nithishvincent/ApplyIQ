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
```bash
npm install
```

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
```bash
npm run db:generate
npm run db:migrate
```

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
