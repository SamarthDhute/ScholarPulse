# ScholarPulse — Technical Debt & Architectural Refinement Tracker

> **Project:** ScholarPulse  
> **Last Updated:** October 17, 2026

This document tracks known deprecation warnings, design trade-offs, potential scaling bottlenecks, and planned future refinements across the ScholarPulse codebase.

---

## 1. Active Technical Debt & Deprecation Warnings

### 1.1 Starlette / FastAPI TestClient Deprecation
- **Warning:** `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.`
- **Location:** `fastapi/testclient.py` invoked during integration API tests.
- **Severity:** Low (non-breaking deprecation notice).
- **Status:** Monitored.
- **Resolution Plan:** Keep standard `TestClient` while Starlette stabilizes `httpx` integration, or transition to direct `httpx.AsyncClient` with `ASGITransport` in Phase B7 (Hardening).

### 1.2 Windows SQLite Engine File Lock in Migration Tests
- **Issue:** On Windows OS, SQLite files cannot be deleted if a SQLAlchemy connection pool holds an active file handle (WinError 32).
- **Severity:** Medium (can cause test suite crashes if not disposed).
- **Status:** Mitigated.
- **Resolution Applied:** Integration tests explicitly call `engine.dispose()` before `os.remove(db_path)` in test teardown.

---

## 2. Design Trade-Offs & Scaling Considerations

### 2.1 Inverted Index Memory Architecture
- **Current Design:** The `InvertedIndex` stores term postings in Python dictionaries (`Dict[str, Dict[str, int]]`) with JSON artifact persistence.
- **Trade-off:**
  - *Pros:* Blazing fast retrieval ($O(\text{postings})$ in memory), pure Python transparency, zero external C-dependencies, effortless serialization.
  - *Limitation:* For multi-gigabyte corpora (>500,000 papers), memory footprint grows with vocabulary size and postings list lengths.
- **Future Scaling Path:** Introduce disk-backed postings with variable-byte or PForDelta integer compression when scaling beyond 100,000 papers.

### 2.2 Corpus Size for Data Science Evaluation (Phase B5)
- **Current Design:** Curated 25-paper academic corpus across 4 computer science categories (Information Retrieval, NLP, Machine Learning, Database Systems).
- **Trade-off:** Ideal for reproducible unit testing, fast CI runs (<15 seconds), and deterministic ranking checks. However, small sample counts per class require stratified splitting and careful evaluation documentation (avoiding over-claiming statistical significance).
- **Future Scaling Path:** Support dynamic synthetic expansion or secondary 500-paper evaluation corpus for advanced benchmarking in Phase B7.

### 2.3 External Ingestion Adapters (OpenAlex, Crossref)
- **Current Design:** Provider adapters in `backend/app/ingestion/adapters/` are designed with strict network boundaries; offline demo does not require keys.
- **Trade-off:** Real API rate limits (e.g. OpenAlex 100k requests/day, Crossref polite pool) must be respected when live ingestion is triggered.
- **Future Scaling Path:** Add exponential backoff, circuit-breaker retry policies, and disk caching of external raw responses before bulk import.

---

## 3. Security & Quality Checklist for Upcoming Phases

- [x] **No Secret Leakage:** Centralized `pydantic-settings`, opaque credentials, zero hardcoded tokens.
- [x] **Pure Python IR:** Complete algorithmic transparency without Elasticsearch/Lucene black-boxes.
- [x] **Timezone-Aware Timestamps:** UTC timestamps utilized across database models.
- [ ] **Password Hashing (Phase B6):** Use Argon2 or Bcrypt for `users.password_hash`.
- [ ] **API Input Validation & Rate Limiting (Phase B7):** Cap query lengths, page sizes, and expensive analytical clustering runs.
- [ ] **Frontend Boundary Guard (Phase B8):** Enforce backend freeze before starting frontend implementation.
