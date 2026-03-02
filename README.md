# Tiresias - AI-Powered Audio Description System

Tiresias provides accurate, timely, and non-intrusive audio descriptions for videos, enabling visually impaired individuals to experience visual media with dignity and independence.

## Core Principles

1. **ZERO dialogue interruption** - Absolute priority
2. **Surgical timing precision** - Descriptions only in natural pauses
3. **Narrative intelligence** - Focus on story-critical visuals
4. **Full keyboard accessibility** - Every feature keyboard-operable
5. **Screen reader excellence** - WCAG AAA compliance

## Architecture

- **Backend**: FastAPI (Python 3.11+) - `tiresias-api/`
- **Frontend**: Next.js 15 (React 19) - `tiresias-dashboard/`
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL
- **AI Models**: Gemini 2.0 Flash (default), Claude, GPT-4

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 14+
- Redis 7+
- FFmpeg

### Backend

```bash
cd tiresias-api
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
cp .env.example .env  # Edit with your API keys
alembic upgrade head
uvicorn src.main:app --reload
```

### Frontend

```bash
cd tiresias-dashboard
pnpm install
cp .env.local.example .env.local
pnpm dev
```

### Docker (All Services)

```bash
cp .env.example .env  # Edit with your API keys
docker compose up -d
```

Access:
- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/api/docs

## Key Features

- Multi-LLM support (Gemini, Claude, GPT-4)
- Multi-platform video input (YouTube, Vimeo, Dailymotion, file upload)
- 4+ voice options (Male/Female x US/UK accents)
- Real-time processing with progress updates
- Community feedback and alternative descriptions
- Professional review system
- Full keyboard navigation and screen reader support

## License

All rights reserved.
