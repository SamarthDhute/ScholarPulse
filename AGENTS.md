# AGENTS.md — ScholarPulse Project Instructions

> **Project:** ScholarPulse — Intelligent Research Discovery and Knowledge Mining Platform  
> **Primary implementation agent:** Antigravity  
> **Current delivery priority:** Complete and verify the backend before beginning frontend implementation.

These instructions are the project-wide source of truth for AI coding agents working in this repository. Follow them for every task unless the user explicitly approves a change.

---

## 1. Required Response Style

- Start **every user-facing response** with: **“Samarth bhau,”**
- Keep responses friendly, direct, and practical. Explain technical decisions in clear language.
- Before editing, briefly state the intended scope and files/areas likely to change.
- After editing, report what changed, what tests/commands were run, their actual results, and any remaining issues.
- Never claim a test passed, a feature works, or a command ran unless it actually did.
- Ask before making a major architectural change or silently dropping a requirement. Do not ask questions for decisions already specified here.
- At the end of each phase, report outcomes and wait for explicit confirmation before starting the next phase. Never run `git commit` or `git push` without asking for and receiving explicit permission.

## 2. Product Vision

ScholarPulse helps students and researchers discover, search, compare, and explore academic research papers. It is a genuine Information Retrieval (IR) and Data Science (DS) project—not merely a chatbot or a generic AI dashboard.

The application should demonstrate academic concepts in working software:

- Document ingestion, validation, normalization, and deduplication.
- Dictionary and inverted-index construction.
- Boolean retrieval and ranked retrieval.
- TF-IDF with cosine similarity, BM25, and a query-likelihood language model.
- Search filters, pagination, and explainable ranking information where feasible.
- Text classification, clustering, association-rule mining, and research analytics.
- Content-based related-paper recommendations.
- Retrieval/classification/clustering evaluation with clearly documented metrics.
- Public research metadata ingestion with source attribution and responsible source usage.

Do not invent research results, metrics, citations, paper metadata, or claims about algorithm superiority.

## 3. Hard Scope and Delivery Rules

1. **Backend first.** Do not begin production frontend implementation until the backend acceptance gates in Section 12 have passed and the user approves moving on.
2. Build a **modular monolith**, not microservices.
3. The core application must run locally with a sample/local dataset and **without external API keys**.
4. External data providers such as OpenAlex and Crossref are optional ingestion adapters, not hard dependencies for startup, search, or tests.
5. Keep IR algorithms implemented and testable in our own code. Do not replace the learning objectives with Elasticsearch or another black-box search service.
6. Build in small, reviewable phases. Do not generate or rewrite the entire repository in one unverified pass.
7. Preserve existing working code. Inspect the repository before editing; do not overwrite files or remove features without understanding their purpose.
8. Do not add infrastructure such as Kubernetes, Redis, Celery, or microservices unless a demonstrated requirement and explicit approval justify it.
9. Keep documentation synchronized with actual implementation. Label planned, partial, simulated, and completed features accurately.
10. **Phase progression confirmation:** After completing any phase (e.g., B0, B1, etc.), stop and report what was implemented, files changed, commands/tests run, and exact results. **Always wait for explicit user confirmation before starting the next phase.** Never proceed to the next phase autonomously.
11. **Git commit and push permission:** Never run `git commit` or `git push` without asking and receiving explicit permission from the user. Always present the proposed commit message and changed files, and wait for explicit confirmation.

## 4. Environment-Driven Configuration and Secret Handling

**All environment-specific and deployment-specific settings must be environment-driven.** Do not hardcode secrets, credentials, machine-specific paths, hostnames, ports, API tokens, database URLs, CORS origins, or environment-specific URLs in application code.

### 4.1 The agent must not directly access secrets

- Never open, read, print, summarize, copy, or expose the contents of `.env`, `.env.*` secret files, shell environment dumps, credential stores, or secret-bearing deployment files.
- Do not run commands such as `cat .env`, `type .env`, `printenv`, `env`, or equivalent commands that dump secrets.
- Do not inspect secret values indirectly through debug output, process dumps, logs, screenshots, generated reports, or test failures.
- Treat actual credentials as opaque. If configuration needs to be checked, inspect only variable **names**, schemas, presence/absence, and validation outcomes without revealing values.
- Application code may read environment variables through the approved configuration layer described below. This does **not** authorize the coding agent to read or reveal the actual secret values.
- If a task appears to require viewing a secret, stop and ask the user to perform the secret-specific action themselves. Continue using placeholders and variable names where possible.

### 4.2 Approved configuration pattern

- Use `pydantic-settings` and a centralized settings module, e.g. `backend/app/core/config.py`.
- Application modules must consume typed settings through dependency injection or the central settings object; do not call `os.getenv()` throughout the codebase.
- Provide `.env.example` containing **placeholder values only** and comments explaining each variable. Never place real secrets in it.
- Keep real `.env` files out of Git. Add suitable `.env` patterns to `.gitignore`.
- Validate required configuration at startup with clear, non-secret error messages.
- Use separate configuration for local development, tests, and deployment. Tests must not depend on a developer's real `.env`.
- Do not put secrets in frontend code, `VITE_*` variables, browser bundles, client-visible logs, API responses, or committed files. Any `VITE_*` variable must be considered public.
- Use safe defaults only for non-sensitive local development settings. Production secrets must be explicitly supplied through the deployment environment or secret manager.
- Avoid logging database URLs, authorization headers, passwords, API keys, tokens, or full secret-bearing settings objects.
- External provider integrations must be disabled or gracefully unavailable when optional credentials/configuration are absent. Never prevent the local demo from starting because an optional provider key is missing.

### 4.3 Suggested variables

Add or adjust this list to match the actual implementation; do not assume every variable is required.

| Variable | Purpose | Secret? |
|---|---|---|
| `APP_ENV` | development/test/production mode | No |
| `APP_NAME` | Application display/service name | No |
| `API_V1_PREFIX` | API version prefix | No |
| `HOST` / `PORT` | Local server bind settings | No |
| `DATABASE_URL` | PostgreSQL connection string | **Yes; may contain credentials** |
| `CORS_ORIGINS` | Allowed browser origins | No |
| `LOG_LEVEL` | Logging verbosity | No |
| `SECRET_KEY` | Signing/session security, if implemented | **Yes** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access-token lifetime, if auth is implemented | No |
| `OPENALEX_API_KEY` | Optional OpenAlex credential if used | **Yes** |
| `CROSSREF_MAILTO` | Optional polite-identification contact | Potentially personal; keep configurable |
| `DATASET_PATH` | Local dataset location | No |
| `ARTIFACTS_PATH` | Generated index/model artifact location | No |
| `RATE_LIMIT_*` | Optional rate-limit settings if implemented | No |

Do not add fake provider keys. Do not require `SECRET_KEY` until the relevant security feature needs it; use a secure production validation policy when it is introduced.

## 5. Approved Technology Stack

Use the following unless the repository already contains a justified, working equivalent or the user approves a change.

### Backend (current priority)

- Python 3.12+
- FastAPI
- Pydantic v2 and `pydantic-settings`
- PostgreSQL
- SQLAlchemy 2.x
- Alembic migrations
- Pandas and NumPy
- scikit-learn for classification, clustering, and standard evaluation utilities
- `mlxtend` for Apriori/association-rule support where appropriate
- pytest and HTTPX/FastAPI TestClient
- Docker Compose for reproducible local services

For text processing, choose **one** of NLTK or spaCy after a small evaluation. Avoid installing both without a concrete need.

### Frontend (later, only after backend approval)

- React
- TypeScript
- Vite
- Tailwind CSS
- Recharts for data visualizations
- Vitest and React Testing Library; Playwright for important end-to-end flows

Do not add packages merely for fashion or duplicate functionality between libraries.

## 6. Architecture and Repository Practices

Prefer clear boundaries:

- `api`: HTTP routes, request/response schemas, dependency wiring.
- `core`: configuration, logging, errors, security.
- `db`: database session, base metadata, migrations.
- `models`: SQLAlchemy persistence models.
- `schemas`: Pydantic request/response models.
- `repositories`: database access and persistence queries.
- `services`: application/business logic.
- `ingestion`: provider adapters, validation, normalization, deduplication.
- `preprocessing`: text normalization and tokenization.
- `retrieval`: tokenizer, dictionary, inverted index, Boolean retrieval, TF-IDF, BM25, language model, passage retrieval.
- `data_science`: classification, clustering, association rules, trend analysis.
- `recommendations`: related-paper/content-based recommendation logic.
- `evaluation`: retrieval and model evaluation.
- `tests`: unit, integration, contract, and fixtures.
- `scripts`: repeatable maintenance/import/evaluation commands.
- `docs`: PRD, SRS, API contracts, setup, and evaluation methodology.

Adapt the exact folder layout to the repository after inspecting it. Do not create duplicate modules simply to match this outline.

### Database and migrations

- Use Alembic migrations for schema changes; do not rely on `create_all()` as the production migration strategy.
- Keep the database as the source of truth for canonical paper metadata.
- Treat search indexes, trained models, and evaluation outputs as derived/rebuildable artifacts with version and provenance information.
- Use UUIDs or a consistently justified identifier strategy.
- Enforce uniqueness and foreign-key constraints where appropriate; deduplicate papers using normalized DOI and provider identifiers when available.
- Store source attribution and source URLs for imported metadata.
- Keep timestamps timezone-aware where relevant.
- Avoid destructive migrations without explicit review and a safe migration plan.

## 7. Core Product and Data Rules

- Core search must work against local/sample data when offline.
- External ingestion adapters must be isolated, configurable, and independently testable.
- Respect provider terms, rate limits, attribution, copyright, and robots.txt where crawling is used. Prefer official APIs and permitted metadata sources.
- Do not scrape login-protected content or bypass access controls.
- Metadata availability does not imply permission to download or redistribute a full-text paper.
- Preserve original/source metadata where useful; make normalization reproducible.
- Search and analytics should return useful empty states instead of errors when the corpus has no matching records.
- Ranking method must be explicit in the API contract. Use BM25 as the default ranker unless the SRS or user-approved decision says otherwise.
- Keep retrieval evaluation data and relevance judgments separate from the corpus used to tune an algorithm where feasible.
- Report metrics such as Precision@K, Recall@K, MAP, and NDCG@K only when the evaluation procedure and relevance labels support them.
- Classification should report suitable metrics, such as precision, recall, F1, and confusion matrix, not accuracy alone.
- Clustering quality metrics must be applied only where mathematically appropriate; explain limitations for small or unsuitable datasets.
- Apriori association rules must expose their support, confidence, and lift thresholds/values.
- Content-based recommendations can use paper text/keywords. Do not claim collaborative filtering is meaningful until enough genuine interaction data exists.
- Make sample/demo data clearly identifiable as sample data.

## 8. API and Error-Handling Rules

- Version APIs under `/api/v1` unless the existing SRS specifies another prefix.
- Use Pydantic schemas for validation; do not expose raw ORM objects directly.
- Keep request/response shapes stable and document them in FastAPI OpenAPI output.
- Use consistent pagination and filter semantics.
- Return suitable HTTP status codes and predictable error bodies, with a request/correlation ID when practical.
- Do not return stack traces, internal file paths, SQL text, secret values, or raw provider exceptions to clients.
- Validate inputs and cap unreasonable query lengths, page sizes, and computationally expensive requests.
- Keep admin-only actions protected by authorization if authentication/roles are implemented. Do not treat hiding a frontend button as authorization.
- Never leave placeholder endpoints that return fabricated successful results while appearing production-ready. Mark stubs explicitly or implement and test them.

## 9. Security and Privacy

- Follow least privilege for database accounts and admin operations.
- Use parameterized ORM/database queries; never construct SQL from untrusted strings.
- Validate and normalize user input at API boundaries.
- If authentication is implemented, hash passwords with an established password-hashing library; never store plaintext passwords.
- Enforce per-user authorization for saved papers, private data, and account operations.
- Keep secrets out of source control, frontend bundles, fixtures, screenshots, generated documentation, and logs.
- Avoid collecting personal data that is not required by the product.
- Add rate limiting or resource guards where public endpoints or expensive analysis need them.
- Never disable TLS/certificate validation as a routine workaround.

## 10. Testing and Code Quality

Every implementation phase must include appropriate tests.

- Unit-test tokenization, normalization, Boolean operators, inverted-index behavior, TF-IDF/cosine, BM25, query-likelihood ranking, deduplication, classification, clustering, association rules, and evaluation calculations.
- Integration-test database repositories, migrations, API filters, pagination, validation, error responses, and authorization boundaries.
- Use deterministic fixtures and fixed random seeds for reproducible ML tests.
- Test empty corpora, no-results queries, malformed inputs, duplicate records, missing optional provider configuration, and unavailable external services.
- Mock external APIs in tests. Standard test runs must not require internet access or real API keys.
- Use temporary/test databases and isolated test settings; never run destructive tests against a user's development or production database.
- Run relevant formatting, linting, type checks, migrations, and tests before calling a phase complete. Use only tools that are installed or add them with justification.
- Fix root causes instead of weakening assertions or skipping tests to get a green run.
- Do not mark a task complete if tests could not run; state the blocker accurately.

## 11. Frontend Design Direction (Future Phase)

The frontend must look like a carefully designed academic research product, **not a generic AI SaaS template**. Use a light theme and the following direction.

### Visual identity

- Quiet, editorial, scholarly, precise, and data-focused.
- White/off-white surfaces, pale cool-gray backgrounds, dark navy/slate typography, and restrained blue accents.
- Suggested starting palette (centralize as design tokens and adjust consistently):
  - Page background: `#F5F8FC`
  - Main surface: `#FFFFFF`
  - Primary text: `#14233B`
  - Secondary text: `#5F6F85`
  - Borders: `#DCE5EF`
  - Primary blue: `#246BFD`
  - Pale blue: `#EAF2FF`
  - Success: `#16856B`
  - Warning: `#C98222`
  - Error: `#C2414B`
- Check contrast and accessibility; do not use color as the only status indicator.
- Use consistent spacing, typography hierarchy, border radius, and restrained shadows. Avoid excessive gradients, glassmorphism, neon glows, giant rounded cards, random decorative blobs, and overused AI sparkle motifs.
- Use real, meaningful paper metadata and charts; do not fill the UI with fabricated metrics presented as live data.
- Charts must have clear titles, units, labels, accessible legends, and empty/loading/error states.

### Information architecture

Plan the responsive web experience around:

1. Home / Discover
2. Search Results with ranker selection and filters
3. Paper Details with abstract, metadata, references/related papers where data exists
4. Topic Exploration / Clustering
5. Research Analytics
6. My Library / Saved Papers
7. Authentication screens if included in the approved scope
8. Admin / Ingestion and Evaluation screens when needed

Use a consistent top navigation and clear active states. Search is a core workflow, not an ornamental hero section. Prioritize readable result titles, authors, publication venue/year, snippets, ranking score/method, and useful filters. Make the layout responsive across desktop, tablet, and mobile. Support keyboard navigation, focus states, reduced motion, semantic HTML, and accessible forms.

Do not begin frontend implementation before backend acceptance and explicit user approval.

## 12. Backend-First Implementation Plan and Acceptance Gates

Work in this order. Verify each phase before starting the next.

### B0 — Foundation

- Inspect the repository and current files before editing.
- Establish backend package/configuration, centralized settings, safe logging, error conventions, database session setup, health endpoint, `.env.example`, `.gitignore`, and README setup instructions.
- Add a small automated test for health and settings validation.
- Confirm the app starts without optional external API credentials.

### B1 — Database

- Implement SQLAlchemy models and Alembic migrations.
- Add repositories and database integration tests.
- Verify a clean database can be migrated from scratch.

### B2 — Ingestion and preprocessing

- Implement a deterministic local sample-data import.
- Add validation, normalization, author/keyword relations, source attribution, and deduplication.
- Add optional provider adapters behind configuration and mock their network calls in tests.

### B3 — Retrieval core

- Implement the dictionary/inverted index, Boolean retrieval, TF-IDF/cosine, BM25, filters, and deterministic ranking behavior.
- Add focused unit tests and small hand-checkable fixtures.

### B4 — Language model and search evaluation

- Implement query-likelihood ranking and passage retrieval if supported by the corpus.
- Add relevance judgments and repeatable Precision@K, Recall@K, MAP, and NDCG@K evaluation.
- Document limitations and how to reproduce results.

### B5 — Data Science

- Implement classification and its evaluation.
- Implement K-means and hierarchical clustering, with meaningful cluster labels/representative papers.
- Implement association-rule mining with support/confidence/lift.
- Implement publication/category/keyword analytics with tests.

### B6 — API surface

- Implement search, paper details/listing, categories/keywords, related papers, analytics, analysis, evaluation, ingestion/admin, and approved library/auth functionality.
- Keep OpenAPI documentation and response schemas synchronized with behavior.

### B7 — Hardening

- Test invalid inputs, empty data, duplicate ingestion, authorization, configuration failures, and missing optional provider keys.
- Check logs for accidental secret leakage.
- Review migrations, performance on the agreed demo corpus, error responses, and documentation.

### B8 — Backend freeze

Do not start frontend work until all applicable items are verified:

- A new developer can configure the project using `.env.example` without exposing secrets.
- Database setup and migrations work from a clean state.
- The local demo dataset can be loaded repeatably without external credentials.
- Search/ranking/filtering/pagination and paper details work through documented APIs.
- IR algorithms have meaningful automated tests.
- DS modules return tested outputs and evaluation information.
- Admin/auth/library features included in the agreed scope are protected and tested.
- OpenAPI contracts, setup instructions, sample requests/responses, and known limitations are documented.
- No known critical data-loss, cross-user access, secret-leakage, or index-corruption issue remains.
- The user has reviewed the backend status and approved moving to frontend.

## 13. Change Management

Before any substantial change:

1. Inspect relevant files and tests.
2. Identify the applicable SRS/PRD requirement.
3. State the planned change and potential impact.
4. Prefer the smallest coherent change.
5. Add or update tests and documentation.
6. Run the relevant checks and report exact results.

Do not silently change database contracts, endpoint names, default ranker, dependency versions, project scope, or data-provider strategy. If a specification is ambiguous, propose a low-risk default and ask only when the decision materially affects architecture, security, data integrity, or user-visible behavior.

## 14. Definition of Done

A task is done only when:

- The requested behavior is implemented rather than merely described.
- Code follows the architecture and security rules above.
- Relevant tests are added or updated and actually run, or any blocker is explicitly reported.
- Configuration remains environment-driven and no secrets are exposed.
- Documentation reflects actual behavior.
- No unrelated destructive changes or unrequested frontend work were introduced.
- The final response begins with **“Samarth bhau,”** and accurately summarizes files changed, checks run, results, and remaining work.
