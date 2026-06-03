# Veo3 Lead Gen Video Pipeline

An event-driven backend service that converts incoming sales leads into personalised marketing videos — fully automated, end-to-end.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HTTP Layer (FastAPI)                         │
│                                                                     │
│  POST /webhook/lead  ──► validate (Pydantic)                        │
│                          persist PipelineJob (status: queued)       │
│                          enqueue Celery task                        │
│                          return { job_id, status }                  │
│                                                                     │
│  GET  /jobs/{id}     ──► return job status + artefacts              │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ Celery task
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Worker Layer (Celery + Redis)                   │
│                                                                     │
│  1. claude_service   → generate 4-scene script (claude-sonnet-4-6)  │
│  2. veo_service      → submit clip (Vertex AI Veo3) × 4 scenes      │
│                        poll every 20s until done                    │
│  3. ffmpeg_service   → download clips from GCS                      │
│                        stitch with xfade → upload final.mp4         │
│  4. publish_service  → LinkedIn / Instagram / Meta Ads              │
│  5. notify_service   → Slack Block Kit notification                 │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
              ┌─────────────────┼──────────────────┐
              ▼                 ▼                   ▼
        PostgreSQL           Redis              Google Cloud
        (job state)       (Celery broker)      Storage (clips
                                               + final video)
```

**Status flow:** `queued` → `running` → `stitching` → `publishing` → `completed` | `failed`

---

## Prerequisites

- Python 3.10+
- PostgreSQL running locally (DB: `leadgen-db`, user: `devuser`, pass: `devpass`)
- Redis running locally on port 6379
- FFmpeg installed (`brew install ffmpeg` on macOS)
- A GCP project with Vertex AI Veo 3 access (see below)
- A GCS bucket for video storage
- A GCP service account JSON key file
- API tokens for LinkedIn, Meta (Instagram + Ads), and Slack

---

## Local Setup

### 1. Clone and enter the backend directory

```bash
git clone <repo-url>
cd backend
```

### 2. Install dependencies

```bash
make install
```

Creates a `.venv` virtualenv and installs all packages from `requirements.txt`.

### 3. Configure environment

```bash
make env
```

Copies `.env.example` → `.env` (skipped if `.env` already exists). Open `.env` and fill in your API keys — DB credentials are pre-filled for the local Postgres instance.

### 4. Place your GCP service account key

```bash
cp /path/to/your/service_account.json ./service_account.json
```

The service account needs these IAM roles:
- `roles/aiplatform.user` — Vertex AI (Veo3 calls)
- `roles/storage.objectAdmin` — GCS read/write
- `roles/iam.serviceAccountTokenCreator` — signed URL generation

### 5. Run database migrations

```bash
make migrate
```

### 6. Start the API server (terminal 1)

```bash
make api
```

FastAPI starts on [http://localhost:8000](http://localhost:8000).

### 7. Start the Celery worker (terminal 2)

```bash
make worker
```

### 8. Verify the service is running

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

---

## All Make Commands

```
make install          Create venv and install dependencies
make env              Copy .env.example → .env (skip if .env exists)
make api              Start FastAPI dev server on :8000 (with --reload)
make worker           Start Celery worker (concurrency=2)
make migrate          Run all pending Alembic migrations
make migrate-down     Roll back the last migration
make migrate-create   Create a new migration  (NAME=your_migration_name)
make test             Run full pytest suite
make test-file        Run one test file       (FILE=tests/test_webhook.py)
make lint             Run ruff linter
make format           Auto-format with ruff
```

---

## Triggering a Pipeline Run

```bash
curl -X POST http://localhost:8000/webhook/lead \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "company": "TechCorp",
    "industry": "SaaS",
    "pain_point": "slow customer onboarding",
    "funnel_stage": "awareness",
    "target_channel": ["linkedin", "instagram"]
  }'
```

Response:
```json
{"job_id": "550e8400-e29b-41d4-a716-446655440000", "status": "queued"}
```

### Check job status

```bash
curl http://localhost:8000/jobs/550e8400-e29b-41d4-a716-446655440000
```

Response fields: `job_id`, `status`, `script`, `clips`, `final_video_url`, `error_message`, `created_at`, `completed_at`.

### API docs

| URL | Interface |
|---|---|
| [http://localhost:8000/docs](http://localhost:8000/docs) | Swagger UI (interactive) |
| [http://localhost:8000/redoc](http://localhost:8000/redoc) | ReDoc (read-only) |
| [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json) | Raw OpenAPI 3.1.0 spec |

---

## Running Tests

```bash
make test

# Single file
make test-file FILE=tests/test_webhook.py

# With coverage (activate venv first)
source .venv/bin/activate
pytest --cov=app tests/
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude |
| `GOOGLE_PROJECT_ID` | GCP project ID |
| `GOOGLE_REGION` | Vertex AI region (default: `us-central1`) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON (default: `/app/service_account.json`) |
| `GCS_BUCKET_NAME` | GCS bucket for clips and final videos |
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn OAuth 2.0 access token (expires every 60 days) |
| `LINKEDIN_AUTHOR_URN` | LinkedIn organisation URN (`urn:li:organization:XXXXX`) |
| `META_ACCESS_TOKEN` | Meta Graph API long-lived access token |
| `META_IG_USER_ID` | Instagram Business account user ID |
| `META_AD_ACCOUNT_ID` | Meta Ads account ID (`act_XXXXXXXXX`) |
| `META_CAMPAIGN_ID` | Existing Meta Ads campaign to attach creatives to |
| `META_ADSET_ID` | Existing Meta Ads adset to attach ads to |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL for notifications |
| `REDIS_URL` | Redis connection URL (default: `redis://localhost:6379/0`) |
| `DATABASE_URL` | PostgreSQL asyncpg connection URL |

---

## Getting Veo 3 API Access

Veo 3 is currently in preview on Vertex AI. To request access:

1. Visit [cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos](https://cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos)
2. Click **Request access** and fill out the form
3. Once approved, enable the **Vertex AI API** in your GCP project:
   ```bash
   gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID
   ```
4. Create a service account and download the JSON key:
   ```bash
   gcloud iam service-accounts create veo-pipeline-sa \
     --display-name="Veo Pipeline Service Account"

   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:veo-pipeline-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/aiplatform.user"

   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:veo-pipeline-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/storage.objectAdmin"

   gcloud iam service-accounts keys create service_account.json \
     --iam-account=veo-pipeline-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

---

## Platform OAuth Token Setup

### LinkedIn

1. Create a LinkedIn Developer App at [developer.linkedin.com](https://developer.linkedin.com)
2. Request the `w_member_social` and `r_basicprofile` permissions
3. Exchange OAuth 2.0 authorization code for an access token
4. LinkedIn tokens expire every **60 days** — set a calendar reminder to rotate

### Meta (Instagram + Ads)

1. Create a Meta Developer App at [developers.facebook.com](https://developers.facebook.com)
2. Add the Instagram Graph API and Marketing API products
3. Generate a long-lived user access token (valid 60 days):
   ```
   https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token
     &client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_TOKEN
   ```
4. Find your Instagram Business Account ID:
   ```bash
   curl "https://graph.facebook.com/v19.0/me/accounts?access_token=TOKEN"
   ```
5. Note your Ad Account ID from [business.facebook.com](https://business.facebook.com) → Ad Accounts

### Slack

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → Create App → From Scratch
2. Navigate to **Incoming Webhooks** → Activate → Add to a channel
3. Copy the webhook URL into `SLACK_WEBHOOK_URL`

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app + router registration
│   ├── config.py                # pydantic-settings — all env vars
│   ├── models/
│   │   ├── lead.py              # Pydantic v2 LeadPayload schema
│   │   └── job.py               # SQLAlchemy 2.0 PipelineJob ORM model
│   ├── routers/
│   │   ├── webhook.py           # POST /webhook/lead
│   │   └── jobs.py              # GET /jobs/{job_id}
│   ├── services/
│   │   ├── claude_service.py    # Script generation (Anthropic API, retry logic)
│   │   ├── veo_service.py       # Veo3 submit + poll (Vertex AI)
│   │   ├── ffmpeg_service.py    # Download → stitch → upload (GCS + FFmpeg)
│   │   ├── publish_service.py   # LinkedIn, Instagram, Meta Ads publishing
│   │   └── notify_service.py    # Slack Block Kit notifications
│   ├── tasks/
│   │   └── pipeline_task.py     # Celery task orchestrating the full flow
│   └── db/
│       ├── session.py           # SQLAlchemy async engine + session factory
│       └── migrations/          # Alembic migrations
│           └── versions/
│               └── 0001_initial.py
├── tests/
│   ├── conftest.py
│   ├── test_webhook.py
│   ├── test_claude_service.py
│   ├── test_veo_service.py
│   └── test_ffmpeg_service.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── alembic.ini
└── .env.example
```

---

## Key Design Decisions

- **Sequential Veo3 clip generation** — scenes are processed one at a time to respect Vertex AI rate limits on preview quotas. Parallelism can be enabled once production quota is confirmed.
- **Celery task timeout = 960s** — accommodates up to 4 clips × 3 min each + stitching + publishing overhead.
- **Best-effort publishing** — `PublishError` is caught per channel; a failure on LinkedIn does not block Instagram or Meta Ads.
- **Signed URLs** — 7-day expiry. Meta's servers pull the video directly from the signed URL, so it must remain accessible during the publishing window.
- **Database session in Celery** — each task run creates its own `AsyncSessionLocal()` context, avoiding cross-task session sharing.
