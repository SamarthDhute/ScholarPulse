# ScholarPulse — Repository Memory & Architecture Guide

> **Project:** ScholarPulse — Intelligent Research Discovery and Knowledge Mining Platform  
> **Repository:** `https://github.com/SamarthDhute/ScholarPulse.git`  
> **Last Updated:** October 17, 2026 (Post-Phase B4 completion)

This document serves as the persistent memory and technical reference for developers and AI agents working on ScholarPulse. It captures architectural decisions, data models, algorithm specifications, environment setup, and operational gotchas.

---

## 1. Project Philosophy & Core Invariants

1. **Backend First:** No production frontend code is written until backend acceptance gates (Phases B0 through B8) are passed and approved.
2. **Transparent Information Retrieval:** Core IR algorithms (Inverted Index, Boolean Shunting-Yard parser, TF-IDF Cosine Similarity, Okapi BM25, Query-Likelihood Language Model) are implemented in project-owned Python code. Black-box search services (Elasticsearch, Solr, Algolia) are prohibited to preserve educational and algorithmic transparency.
3. **BM25 as Default Ranker:** Okapi BM25 ($k_1=1.5, b=0.75$) is the default ranking engine across all search interfaces unless specifically overridden by the client.
4. **Environment-Driven Configuration & Zero-Secret Leakage:**
   - Managed via `pydantic-settings` in `backend/app/core/config.py`.
   - `.env` files are never dumped, logged, or checked into Git.
   - Offline local demo starts without external API keys.
5. **Modular Monolith Architecture:** Separation of concerns across `api`, `core`, `db`, `models`, `repositories`, `preprocessing`, `retrieval`, `data_science`, `evaluation`, and `services`.
6. **Strict Phase Gate & Git Protocol:**
   - Every user-facing AI response begins with **“Samarth bhau,”**.
   - No phase advancement occurs without explicit user confirmation.
   - No `git commit` or `git push` is executed without prior user permission.

---

## 2. System Architecture & Directory Layout

```text
ScholarPulse/
├── AGENTS.md                  # Project constitution & agent rules
├── README.md                  # Project overview & local setup
├── REPO_MEMORY.md             # Persistent architectural memory (this file)
├── progress.md                # Phase-by-phase completion status
├── technicaldebt.md           # Tracked tech debt, warnings, and future improvements
├── .env.example               # Safe environment variable template
├── .gitignore                 # Secrets, cache, and virtualenv exclusions
│
├── datasets/
│   ├── raw/
│   │   └── sample_papers.json # 25-paper curated academic corpus
│   └── eval/
│       └── relevance_judgments.json # Ground-truth query-paper relevance grades
│
├── docs/
│   ├── ScholarPulse_PRD_v1_1.md # Product Requirements Document v1.1
│   └── ScholarPulse_SRS_v1.md   # Software Requirements Specification v1.0
│
├── artifacts/                 # Serialized indexes, models, and evaluation outputs
│   └── indexes/
│
├── backend/
│   ├── pyproject.toml         # Python package dependencies & tool settings
│   ├── alembic.ini            # Database migration configuration
│   ├── migrations/            # Alembic schema versions
│   │   └── versions/
│   │       └── 001_initial_schema.py # 13 canonical tables
│   ├── app/
│   │   ├── core/              # Config (pydantic-settings), logging, errors
│   │   ├── db/                # Base declarative model & session makers
│   │   ├── models/            # SQLAlchemy 2.0 ORM entities
│   │   ├── repositories/      # Database CRUD and relational queries
│   │   ├── preprocessing/     # Text normalization, tokenization, Porter stemming
│   │   ├── ingestion/         # Adapters, validation, deduplication, importer
│   │   ├── retrieval/         # InvertedIndex, Boolean, TF-IDF, BM25, LanguageModel, Passage
│   │   ├── evaluation/        # RetrievalEvaluator (MAP, NDCG@K, P@K, Recall@K, MRR)
│   │   ├── data_science/      # (Phase B5) Classifier, Clustering, Apriori, Analytics
│   │   ├── api/               # (Phase B6) FastAPI endpoints & route routers
│   │   ├── schemas/           # Pydantic v2 request/response schemas
│   │   ├── services/          # High-level domain service coordinators
│   │   └── main.py            # FastAPI application factory
│   └── tests/
│       ├── fixtures/          # Deterministic test corpora (toy_corpus.py)
│       ├── unit/              # Focused unit tests
│       └── integration/       # Database, search, and evaluation integration tests
```

---

## 3. Database Schema (13 Entities)

Defined using SQLAlchemy 2.0 declarative mapping in `backend/app/models/`:

1. **`Paper` (`papers`):** Canonical paper metadata (`id` [UUID], `title`, `abstract`, `publication_year`, `doi`, `source_name`, `source_url`, `external_id`, `normalized_text`, timestamps).
2. **`Author` (`authors`):** Author names, normalized names, ORCID, affiliations.
3. **`PaperAuthor` (`paper_authors`):** Many-to-many join with `author_order`.
4. **`Keyword` (`keywords`):** Cleaned keyword strings.
5. **`PaperKeyword` (`paper_keywords`):** Many-to-many join with `origin` (`author` vs `extracted`).
6. **`Category` (`categories`):** Academic subjects (IR, NLP, ML, Databases, Security).
7. **`PaperCategory` (`paper_categories`):** Join with `label_source` (`verified` vs `predicted`) and confidence score.
8. **`User` (`users`):** Account credentials (Argon2/Bcrypt hash placeholder), roles (`user`, `admin`).
9. **`SavedPaper` (`saved_papers`):** User library bookmarks and private notes.
10. **`IngestionRun` (`ingestion_runs`):** Tracking import batches, status, counts, errors.
11. **`RelevanceJudgment` (`relevance_judgments`):** Ground-truth query-paper pairs with graded relevance (0, 1, 2).
12. **`EvaluationRun` (`evaluation_runs`):** IR and DS evaluation executions.
13. **`EvaluationMetric` (`evaluation_metrics`):** Metric values (MAP, NDCG@K, Precision@K, F1) linked to runs.

---

## 4. Implemented Information Retrieval Algorithms

### 4.1 Inverted Index (`InvertedIndex`)
- Postings mapping: `term -> {doc_id: term_frequency}`.
- Tracks document length $|d|$ and average document length $avgdl$.
- Serializes and deserializes to JSON (`artifacts/indexes/inverted_index.json`).

### 4.2 Boolean Retrieval (`BooleanRetrievalEngine`)
- **Shunting-Yard Algorithm:** Converts infix boolean queries with parentheses to postfix (Reverse Polish Notation).
- **Precedence:** `NOT` (3) > `AND` (2) > `OR` (1).
- Supports explicit operators, nested parentheses, and implicit AND between adjacent terms.
- Evaluates over postings sets using intersection, union, and set difference.

### 4.3 Vector Space Model (`TFIDFRetrievalEngine`)
- Sublinear TF scaling: $tf(t, d) = 1 + \ln(count)$ if $count > 0$ else $0$.
- Smoothed IDF: $idf(t) = \ln\left(\frac{N + 1}{df(t) + 1}\right) + 1.0$.
- Precomputed Euclidean document norms $\|d\| = \sqrt{\sum w(t, d)^2}$.
- Cosine similarity: $\text{CosineSim}(q, d) = \frac{\sum w(t, q) \cdot w(t, d)}{\|q\| \cdot \|d\|} \in [0, 1]$.
- Provides explainable term-level score breakdowns.

### 4.4 Okapi BM25 (`BM25RetrievalEngine`) — Default Ranker
- Robertson-Spärck Jones IDF: $\text{RSJ-IDF}(t) = \ln\left(\frac{N - df(t) + 0.5}{df(t) + 0.5} + 1.0\right)$.
- Scoring formula:
  $$\text{Score}(q, d) = \sum_{t \in q} \text{RSJ-IDF}(t) \cdot \frac{tf(t, d) \cdot (k_1 + 1)}{tf(t, d) + k_1 \cdot \left(1 - b + b \cdot \frac{|d|}{avgdl}\right)}$$
- Parameters: $k_1 = 1.5$ (term frequency saturation), $b = 0.75$ (document length normalization).
- Returns total score and explainable dictionary of term contributions.

### 4.5 Query-Likelihood Language Model (`LanguageModelRetrievalEngine`)
- Unigram statistical language model ranking documents by log query likelihood:
  $$\ln P(q | M_d) = \sum_{t \in q} \ln P(t | M_d)$$
- **Dirichlet Smoothing:** $P(t | M_d) = \frac{count(t, d) + \mu P(t | C)}{|d| + \mu}$ (default $\mu = 1000.0$).
- **Jelinek-Mercer Smoothing:** $P(t | M_d) = (1 - \lambda) P_{ml}(t | d) + \lambda P(t | C)$ (default $\lambda = 0.1$).
- Background collection probability: $P(t | C) = \frac{cf(t)}{|C|}$.

### 4.6 Passage Retrieval (`PassageRetrievalEngine`)
- Splits paper abstract into sentences.
- Scores passages based on query term coverage, frequency, and length penalties.
- Injects HTML `<mark>term</mark>` tags for clean frontend search card previews.

### 4.7 Search Service Orchestrator (`SearchService`)
- Unified interface for `bm25`, `tfidf`, `language_model`, and `boolean`.
- Metadata filtering: `year_min`, `year_max`, and `category`.
- Deterministic 1-indexed pagination (`page`, `page_size`, `total_hits`).
- Complete artifact serialization (`inverted_index.json`, `index_metadata.json`, `document_texts.json`).

### 4.8 Evaluation Harness (`RetrievalEvaluator`)
- Standardized academic IR evaluation against `datasets/eval/relevance_judgments.json`.
- Implements Precision@K, Recall@K, MAP, MRR, DCG@K, and NDCG@K.
- Automated multi-ranker benchmarking (`compare_rankers`).

---

## 5. Implemented Data Science & Recommendation Modules

### 5.1 Supervised Text Classification (`PaperClassifier`)
- Supervised classification across research taxonomies (Information Retrieval, Machine Learning, NLP, Data Mining, Systems).
- Supports Multinomial Naive Bayes, Logistic Regression (`lbfgs` solver), and Linear SVC.
- Strict featurization ordering: split before fitting TF-IDF to guarantee zero feature leakage.
- Metrics reported: Accuracy, Precision (macro), Recall (macro), Macro/Weighted F1-score, class-level metrics, and Confusion Matrix.
- Model comparison suite (`compare_models`) evaluating models on identical splits.
- Artifact serialization with `joblib` and metadata JSON.

### 5.2 Document Clustering & Topic Modeling (`PaperClustering`)
- Unsupervised semantic topic grouping via K-Means and Hierarchical/Agglomerative Clustering.
- Cosine-metric TF-IDF feature space.
- Evaluation metrics: Silhouette Score and Inertia.
- Automated optimal cluster count ($k$) search across candidate values.
- Explainable semantic topic labels generated from top centroid feature weights.
- Representative paper discovery based on cosine proximity to cluster centroids.

### 5.3 Association Rule Mining (`KeywordAssociationMiner`)
- Apriori algorithm powered by `mlxtend` over keyword transaction sets.
- Strict validation: $\text{min\_support} \in (0, 1]$, $\text{min\_confidence} \in (0, 1]$, $\text{min\_lift} \ge 0.0$.
- Calculates Support, Confidence, Lift, Leverage, and Conviction.
- Directional rule search by antecedent term.
- Bounded pagination conforming to SRS 8.8.

### 5.4 Bibliometric & Research Analytics (`ResearchAnalyticsService`)
- Chronological publication volume and year-over-year growth percentage.
- Category distribution and percentage market share.
- Recurring keyword frequencies and distributions.
- Author productivity ranking and co-authorship collaboration network graph (nodes, edges, weights, top collaborating pairs).
- Bounded time-range filtering (`year_min`, `year_max`).

### 5.5 Content-Based Related-Paper Recommendations (`ContentBasedRecommender`)
- Pairwise cosine similarity matrix over unified paper representations (title + abstract + keywords).
- Strict exclusion of the query seed paper itself per FR-019.
- Explainable shared keywords between seed paper and recommended candidates.
- Fast top-$N$ recommendation with minimum similarity threshold.

---

## 6. Key Engineering Insights & Gotchas

1. **Windows SQLite File Locking in Tests:**
   When testing file-based SQLite databases (e.g. Alembic migrations), `engine.dispose()` must be called before calling `os.remove(db_path)` to avoid Windows OS Error 32 sharing violations.
2. **Alembic Path Separator:**
   In `backend/alembic.ini`, using `%(here)s/migrations` with `path_separator = os` ensures migration discovery works uniformly across Windows and Linux.
3. **Unicode Dash Normalization:**
   Academic titles and abstracts frequently contain Unicode en-dashes (`–`) and em-dashes (`—`). Converting them to spaces before stripping non-ASCII characters prevents concatenated terms (e.g., `Natural—Language` -> `natural language`).
4. **Non-Negative BM25 IDF:**
   Using the smoothed RSJ-IDF variant $\ln\left(\frac{N - df + 0.5}{df + 0.5} + 1.0\right)$ guarantees strictly positive IDF even when a term appears in more than half the collection documents.
5. **Language Model Underflow:**
   Direct multiplication of unigram probabilities causes arithmetic underflow for long queries. Summing log probabilities ($\ln P(t|M_d)$) guarantees numerical stability.
6. **Logistic Regression Multiclass Solver:**
   In scikit-learn $\ge$ 1.5, `solver='lbfgs'` natively handles multinomial multiclass classification without deprecation warnings.
7. **Safe Stratification for Small Corpora:**
   Stratified train/test splitting requires the test partition size to be at least equal to the number of classes. Conditional stratification guards against `ValueError` when running evaluations on small custom test sets.

---

## 7. Development & Testing Commands

All backend dependencies are managed in `backend/.venv` (Python 3.12.14).

```powershell
# Activate environment
backend\.venv\Scripts\Activate.ps1

# Run full test suite (116 tests)
backend\.venv\Scripts\python.exe -m pytest backend/tests/ -v

# Run Alembic migrations
cd backend
..\backend\.venv\Scripts\python.exe -m alembic upgrade head

# Start local FastAPI server
..\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```
