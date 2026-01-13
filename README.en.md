English | [日本語](README.md)

# MemoScribe - Personal Life Secretary

Personal Life Secretary is a personal web application that securely stores all information input or uploaded by the user, providing "citation-backed" answers, text generation, advice, and retrospectives using LLM and RAG (Search + Generation).

## Features

- **Citation-Backed Answers**: Generated results always display citations from referenced notes/logs/documents.
- **3-Layer Data Structure**: Raw (Original) → Digest (Structured Summary) → Memory (Search Target).
- **Privacy First**: Designed for local/self-hosting, minimizing external data transmission.
- **LLM ON/OFF Support**: Basic functions operate even without an LLM.

## Functions

- 📝 **Note Management**: Create and edit notes with Markdown support.
- 📅 **Daily Logs**: Record daily events and automatically generate digests.
- 📄 **Document Management**: Upload PDF/Text/Markdown files, extract text, and search.
- ✅ **Task Management**: Manage tasks with priorities and deadlines.
- ⚙️ **Preferences & Rules**: Set personal preferences and policies.
- 💬 **Assistant**: Provide answers based on accumulated data.
- ✍️ **Text Generation**: Compose emails, rewrite text, propose schedules.

## Tech Stack

- Python 3.12
- Django 5.x
- PostgreSQL 16 + pgvector
- Celery + Redis
- OpenAI API (or compatible API)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/MemoScribe.git
cd MemoScribe
```

### 2. Set environment variables

```bash
cp .env.example .env
# Edit .env to set API keys, etc.
```

Main settings:
- `DJANGO_SECRET_KEY`: Django secret key (Must be changed in production).
- `LLM_API_KEY`: OpenAI API key (If using LLM features).
- `PII_MASKING`: PII masking (Default: true).

### 3. Start with Docker Compose

```bash
docker compose up --build
```

### 4. Create a superuser

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. (Optional) Seed demo data

```bash
docker compose exec web python manage.py seed_demo
```

Demo user: `demo` / `demo1234`

### 6. Access in browser

http://localhost:8000

## Configuration

### Environment Variables

| Variable Name | Description | Default |
|--------|------|-----------|
| `DJANGO_SECRET_KEY` | Django secret key | - |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `POSTGRES_*` | PostgreSQL connection settings | - |
| `REDIS_URL` | Redis URL | `redis://redis:6379/0` |
| `LLM_PROVIDER` | LLM provider | `openai` |
| `LLM_API_KEY` | LLM API key | - |
| `LLM_MODEL` | LLM model name | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `SEND_NOTES` | Send notes to LLM | `true` |
| `SEND_DIGESTS` | Send digests to LLM | `true` |
| `SEND_DOCS` | Send documents to LLM | `false` |
| `SEND_RAW_LOGS` | Send raw logs to LLM | `false` |
| `PII_MASKING` | PII masking | `true` |
| `LLM_ENABLED` | Enable LLM features | `true` |

### Privacy Settings

You can control the following in the settings page (/settings/):

- Selection of data types to send to LLM
- ON/OFF for PII masking
- ON/OFF for LLM features

## Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Database migration
python manage.py migrate

# Start development server
python manage.py runserver
```

### Run Tests

```bash
# Run pytest
docker compose exec web pytest

# With coverage
docker compose exec web pytest --cov=.
```

### Code Quality

```bash
# Lint with ruff
ruff check .

# Format with black
black .
```

## Architecture

```
MemoScribe/
├── config/           # Django project settings
├── core/             # Common utilities, LLM provider
├── notes/            # Note management
├── logs/             # Daily logs, digests
├── documents/        # Document management
├── tasks/            # Task management
├── preferences/      # Preferences, rules, user settings
├── assistant/        # Chat assistant
├── retrieval/        # RAG, embeddings, search
├── audits/           # Audit logs
├── templates/        # HTML templates
├── static/           # Static files
└── tests/            # Tests
```

## RAG (Retrieval-Augmented Generation) Mechanism

1. **Indexing Targets**
   - Note content
   - Digests (Summaries, Topics, Actions)
   - Document chunks
   - Tasks
   - Preferences & Rules

2. **Search Flow**
   - User question is vectorized (embeddings).
   - Cosine similarity search via pgvector.
   - Retrieve top k results.
   - Provide to LLM as context.

3. **Citation Display**
   - Answers always display grounds (citations).
   - If grounds are insufficient, additional questions are prompted.

## License

MIT License

## Contribution

Issues and Pull Requests are welcome.
