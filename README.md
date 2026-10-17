# ScholarPulse — Intelligent Research Discovery and Knowledge Mining Platform

ScholarPulse is an academic Information Retrieval (IR) and Data Science (DS) platform designed to help students, researchers, and evaluators discover, search, compare, and analyze academic research papers.

Unlike generic chatbot wrappers, ScholarPulse demonstrates genuine information retrieval and data science algorithms in transparent, explainable software:
- **Custom IR Suite:** Inverted Index, Boolean retrieval, TF-IDF cosine similarity, Okapi BM25 (default ranker), Query-Likelihood Language Model, and Passage Retrieval.
- **Data Science Suite:** Text categorization (Naive Bayes & SVM), K-Means & Hierarchical Clustering, Apriori Association Rule Mining (support, confidence, lift), and bibliometric trend analytics.
- **Repeatable Evaluation:** Objective IR evaluation framework measuring Precision@K, Recall@K, MAP, and NDCG@K on judged query sets.

---

## Architecture & Project Structure

The project is structured as a **Modular Monolith** under a strict backend-first delivery strategy:

```text
ScholarPulse/
├── backend/
│   ├── pyproject.toml         # Dependencies and project metadata
│   ├── requirements.txt       # Frozen dependencies
│   ├── alembic.ini            # Alembic database migrations config
│   ├── migrations/            # Migration versions and environment
│   ├── app/
│   │   ├── main.py            # FastAPI application entrypoint
│   │   ├── api/v1/            # API route controllers and endpoints
│   │   ├── core/              # Centralized pydantic-settings, logging, errors
│   │   ├── db/                # Database engine, session, DeclarativeBase
│   │   ├── models/            # SQLAlchemy 2.0 ORM persistence models
│   │   ├── schemas/           # Pydantic v2 request/response schemas
│   │   ├── repositories/      # Database query abstractions
│   │   ├── services/          # Application business logic
│   │   ├── ingestion/         # Ingestion pipeline, validation, deduplication
│   │   ├── preprocessing/     # Text normalization, tokenization, stemming
│   │   ├── retrieval/         # Custom Inverted Index, Boolean, BM25, TF-IDF
│   │   ├── data_science/      # Classifier, Clustering, Apriori, Trends
│   │   ├── recommendations/   # Content-based paper recommendation
│   │   └── evaluation/        # IR evaluation runner (MAP, NDCG@K, etc.)
│   └── tests/                 # Unit, integration, and contract tests
├── datasets/                  # Raw and processed local research datasets
├── artifacts/                 # Versioned index, model, and evaluation artifacts
├── scripts/                   # Repeatable management and seed CLI commands
├── docs/                      # PRD, SRS, and architecture documentation
├── .env.example               # Environment variables template (no secrets)
└── .gitignore                 # Excludes .env, virtualenvs, caches, artifacts
```

---

## Getting Started (Local Development)

### Prerequisites
- Python 3.12+ (or Python 3.11+)
- `uv` (recommended) or standard `venv + pip`
- PostgreSQL 15+ (optional for Phase B0 tests; SQLite in-memory/fallback supported for isolated unit tests)

### 1. Environment Setup

Copy `.env.example` to create your local `.env`:
```bash
cp .env.example .env
```
*(Note: Never commit your actual `.env` file to Git.)*

### 2. Virtual Environment & Dependencies

Using `uv` (fastest):
```bash
uv venv backend/.venv --python 3.12
# On Windows:
backend\.venv\Scripts\activate
# Install dependencies:
uv pip install -r backend/requirements.txt
```

Or using standard `venv`:
```bash
python -m venv backend/.venv
backend\Scripts\activate
pip install -r backend/requirements.txt
```

### 3. Running the Backend Server

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Verify service health:
```bash
curl http://localhost:8000/api/v1/health
```
Response:
```json
{
  "status": "ok",
  "service": "scholarpulse-api",
  "version": "1.0.0"
}
```

### 4. Running Automated Tests

```bash
pytest backend/tests/ -v
```

---

## License & Attribution
ScholarPulse is developed for academic evaluation in Information Retrieval and Data Science.
