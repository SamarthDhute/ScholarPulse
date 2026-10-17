# ScholarPulse --- Software Requirements Specification (SRS)

  -----------------------------------------------------------------------
  Document Field                      Details
  ----------------------------------- -----------------------------------
  Product                             ScholarPulse

  Document                            Software Requirements Specification
                                      (SRS)

  Version                             1.0

  Status                              Proposed baseline for review

  Related document                    ScholarPulse PRD v1.1

  Development strategy                Backend-first; frontend begins
                                      after backend acceptance gates are
                                      met

  Architecture                        Modular monolith

  Primary objective                   Specify technical requirements,
                                      data model, interfaces, API
                                      contracts, quality requirements and
                                      backend delivery sequence.
  -----------------------------------------------------------------------

## 1. Purpose and Scope

  -----------------------------------------------------------------------
  ID                      Area                    Specification
  ----------------------- ----------------------- -----------------------
  SRS-001                 Purpose                 Define the system's
                                                  technical behavior,
                                                  modules, data
                                                  structures, APIs,
                                                  validation, testing and
                                                  delivery gates for
                                                  ScholarPulse.

  SRS-002                 Product scope           Academic research-paper
                                                  discovery, ranked
                                                  retrieval, paper
                                                  metadata,
                                                  classification,
                                                  clustering, keyword
                                                  association mining,
                                                  analytics, evaluation
                                                  and related-paper
                                                  recommendations.

  SRS-003                 Primary users           Students, researchers,
                                                  faculty/evaluators and
                                                  authorized
                                                  administrators.

  SRS-004                 Scope boundary          Version 1 is an
                                                  academic project with a
                                                  production-oriented
                                                  foundation, not an
                                                  enterprise-scale search
                                                  service.

  SRS-005                 Backend-first           Complete and validate
                          constraint              backend modules and
                                                  contracts before
                                                  implementing the
                                                  production frontend.

  SRS-006                 Source integrity        Store available source
                                                  attribution and never
                                                  fabricate unavailable
                                                  metadata or claim that
                                                  relevance indicates
                                                  scientific correctness.
  -----------------------------------------------------------------------

## 2. System Context and Architecture

  ------------------------------------------------------------------------------
  Component               Responsibility                 Depends on
  ----------------------- ------------------------------ -----------------------
  API layer               Request validation, response   Application services
                          schemas,                       
                          authentication/authorization   
                          where required, status codes   
                          and API versioning.            

  Research service        Paper lookup, metadata,        Repository/data access
                          filters and source references. 

  Ingestion service       Import approved public         Source adapters,
                          metadata, validate records,    repository,
                          deduplicate, report run        preprocessing
                          outcomes.                      

  Preprocessing module    Normalize text and metadata;   Ingestion service
                          preserve raw/source values     
                          where useful.                  

  Retrieval module        Boolean retrieval, inverted    Clean corpus and index
                          index, TF-IDF, BM25,           artifacts
                          query-likelihood ranking and   
                          passage retrieval.             

  Data Science module     Classification, clustering,    Clean corpus and model
                          association mining and trend   artifacts
                          analysis.                      

  Recommendation module   Content-based related-paper    Paper features and
                          ranking.                       retrieval utilities

  Evaluation module       Search and model metrics over  Retrieval and Data
                          documented datasets.           Science outputs

  Analytics module        Return aggregate statistics    Repository and analysis
                          for dashboard consumption.     outputs

  Identity/library module User identity, saved papers    User repository
                          and access rules.              

  PostgreSQL              Persistent research metadata,  Database migrations
                          users, saved papers, ingestion 
                          records and evaluation         
                          records.                       

  Artifact storage        Versioned                      Indexing and
                          index/vectorizer/model outputs model-building jobs
                          and evaluation artifacts.      
  ------------------------------------------------------------------------------

### 2.1 Architectural rules

  -----------------------------------------------------------------------
  ID                      Rule                    Reason
  ----------------------- ----------------------- -----------------------
  AR-01                   Use a modular monolith  Keeps solo development
                          for Version 1; modules  and local deployment
                          communicate through     manageable.
                          explicit Python service 
                          interfaces.             

  AR-02                   API route handlers must Makes behavior testable
                          remain thin; business   and reusable.
                          rules belong in         
                          services.               

  AR-03                   PostgreSQL is the       Avoids conflicting
                          source of truth for     copies of core
                          persistent structured   metadata.
                          records.                

  AR-04                   Indexes and trained     Prevents stale or
                          models are derived      unrecoverable derived
                          artifacts and must be   data.
                          rebuildable from        
                          versioned inputs.       

  AR-05                   Search requests must    Keeps search behavior
                          not retrain models or   predictable and
                          rebuild the full index  responsive.
                          synchronously.          

  AR-06                   Keep raw/source         Preserves provenance
                          metadata separate from  and supports
                          normalized searchable   reprocessing.
                          fields where practical. 

  AR-07                   Frontend development    Honors the
                          starts only after the   backend-first project
                          backend acceptance      plan.
                          gates in Section 14     
                          pass.                   
  -----------------------------------------------------------------------

## 3. Technology Stack

  -----------------------------------------------------------------------------------
  Layer              Selected technology Use in ScholarPulse    Decision notes
  ------------------ ------------------- ---------------------- ---------------------
  Language           Python 3.12+ (pin a API and IR/Data        Keep the runtime
                     supported minor     Science backend.       version consistent
                     version in project                         across development
                     configuration)                             and deployment.

  API framework      FastAPI             REST API, dependency   Use versioned
                                         handling and OpenAPI   `/api/v1` routes.
                                         docs.                  

  Request/response   Pydantic v2         Validate inputs and    Reject invalid query
  validation                             response schemas.      parameters and
                                                                malformed payloads.

  Database           PostgreSQL          Research metadata and  Relational source of
                                         user/application       truth.
                                         records.               

  ORM                SQLAlchemy 2.x      Database persistence   Use explicit
                                         and queries.           relationships and
                                                                transactions.

  Migrations         Alembic             Versioned schema       Schema changes must
                                         changes.               be reviewed and
                                                                migration-tested.

  Data processing    Pandas, NumPy       Cleaning, aggregation  Avoid loading
                                         and numerical work.    unnecessarily large
                                                                corpora into memory.

  ML and evaluation  scikit-learn        TF-IDF features, Naive Separate
                                         Bayes, SVM, K-means,   training/evaluation
                                         hierarchical           data where
                                         clustering and         applicable.
                                         metrics.               

  Association mining mlxtend             Apriori, frequent      Report support,
                                         itemsets and           confidence and lift.
                                         association rules.     

  Language           NLTK or spaCy       Tokenization and       Preserve original
  processing         (choose one after a optional linguistic    text; preprocessing
                     short preprocessing normalization.         must be consistent
                     spike)                                     between indexing and
                                                                queries.

  Retrieval          Project-owned       Inverted index,        Required algorithms
  algorithms         Python modules      Boolean operations,    must be independently
                                         BM25 and               explainable and
                                         query-likelihood       testable.
                                         scoring.               

  HTTP client        HTTPX               External metadata API  Set timeouts and
                                         calls and API tests.   handle rate limits.

  Testing            pytest              Unit and integration   Test algorithm edge
                                         tests.                 cases and API
                                                                behavior.

  API integration    FastAPI TestClient  API contract and       Tests should not
  testing            / HTTPX             status-code tests.     depend on live
                                                                third-party services.

  Configuration      pydantic-settings   Environment-based      Secrets must not be
                                         configuration.         committed.

  Logging            Python standard     Diagnostics and        Do not log passwords,
                     logging with        ingestion/evaluation   tokens or unnecessary
                     structured fields   outcomes.              personal data.

  Packaging          Docker Compose      Repeatable local       Keep setup
                                         backend and database   instructions
                                         setup.                 reproducible.

  Frontend (later    React, TypeScript,  Web interface and      Do not begin
  phase)             Vite, Tailwind CSS, charts.                production frontend
                     Recharts                                   until backend gates
                                                                pass.

  Version control    Git                 Source control and     Use small commits and
                                         reviewable changes.    keep generated
                                                                datasets/artifacts
                                                                out of Git when large
                                                                or restricted.
  -----------------------------------------------------------------------------------

## 4. Functional Requirements

  ---------------------------------------------------------------------------------
  ID                Requirement       Expected behavior         Priority
  ----------------- ----------------- ------------------------- -------------------
  FR-001            Research records  Create, retrieve, update  Must
                                      and list research-paper   
                                      metadata.                 

  FR-002            Provenance        Preserve source name,     Must
                                      source URL and available  
                                      DOI/external identifier.  

  FR-003            Data validation   Validate required fields  Must
                                      and normalize optional    
                                      metadata.                 

  FR-004            Deduplication     Detect likely duplicates  Must
                                      using stable identifiers  
                                      and fallback metadata     
                                      matching; uncertain       
                                      matches must not be       
                                      silently merged.          

  FR-005            Ingestion runs    Track start/end status,   Must
                                      counts, failures and      
                                      source for each import    
                                      run.                      

  FR-006            Preprocessing     Produce consistent        Must
                                      searchable text from      
                                      title, abstract and       
                                      keywords while preserving 
                                      display text.             

  FR-007            Inverted index    Build a term dictionary   Must
                                      and posting lists mapping 
                                      terms to document IDs.    

  FR-008            Boolean retrieval Support documented AND,   Must
                                      OR and NOT behavior.      

  FR-009            Ranked retrieval  Support TF-IDF/cosine and Must
                                      BM25 ranking over the     
                                      same candidate corpus.    

  FR-010            Query likelihood  Provide a smoothed        Must for
                                      query-likelihood ranking  syllabus-complete
                                      mode as an IR Unit IV     release
                                      capability.               

  FR-011            Passage retrieval Return relevant abstract  Should
                                      sentence/passage snippets 
                                      when available.           

  FR-012            Filters and       Filter by year, author,   Must
                    pagination        category and keyword      
                                      where data exists;        
                                      paginate results.         

  FR-013            Classification    Train/evaluate a baseline Must
                                      text classifier and       
                                      expose predicted          
                                      categories with           
                                      prediction status.        

  FR-014            Clustering        Produce inspectable       Must
                                      K-means groups and        
                                      support a                 
                                      hierarchical-clustering   
                                      comparison.               

  FR-015            Association       Produce frequent keyword  Must
                    mining            itemsets and rules with   
                                      support, confidence and   
                                      lift.                     

  FR-016            Trend analytics   Return publication counts Must
                                      and category/keyword      
                                      aggregates by supported   
                                      time range.               

  FR-017            Search evaluation Calculate Precision@K,    Must
                                      Recall@K, MAP and NDCG@K  
                                      from a judged query set.  

  FR-018            Model evaluation  Report classification     Must
                                      metrics and suitable      
                                      clustering quality        
                                      indicators.               

  FR-019            Related papers    Rank papers by content    Should
                                      similarity and exclude    
                                      the selected paper        
                                      itself.                   

  FR-020            Saved library     Authenticated users can   Should
                                      save, list and remove     
                                      saved papers.             

  FR-021            Health endpoint   Expose service health and Must
                                      dependency readiness      
                                      without leaking secrets.  

  FR-022            Error responses   Return consistent, safe   Must
                                      error objects and         
                                      appropriate HTTP status   
                                      codes.                    

  FR-023            Authorization     Restrict admin operations Must if
                                      and ensure users can only account/library
                                      access their own saved    features are
                                      library.                  enabled

  FR-024            Data update       Expose ingestion status   Should
                    status            and basic collection      
                                      health to authorized      
                                      administrators.           
  ---------------------------------------------------------------------------------

## 5. Non-Functional Requirements

  ---------------------------------------------------------------------------------
  ID                Quality                   Requirement         Verification
  ----------------- ------------------------- ------------------- -----------------
  NFR-001           Correctness               Search, filters and Automated unit
                                              metrics must        tests.
                                              produce             
                                              deterministic       
                                              results for fixed   
                                              inputs and fixed    
                                              artifacts.          

  NFR-002           Reliability               Expected            Integration tests
                                              external-source     with mocked
                                              failures must be    failures.
                                              recorded and must   
                                              not corrupt already 
                                              committed records.  

  NFR-003           Security                  Validate all        Security
                                              inputs; store       checklist and
                                              passwords only as   tests.
                                              secure hashes if    
                                              password            
                                              authentication is   
                                              implemented; never  
                                              commit secrets.     

  NFR-004           Authorization             User-owned records  Cross-user access
                                              must be isolated by tests.
                                              authenticated user  
                                              identity.           

  NFR-005           Maintainability           Separate API,       Code review and
                                              service, domain,    module tests.
                                              repository,         
                                              retrieval and Data  
                                              Science             
                                              responsibilities.   

  NFR-006           Reproducibility           Record dataset      Re-run evaluation
                                              version, query-set  and compare
                                              version,            outputs.
                                              model/index version 
                                              and relevant        
                                              evaluation          
                                              settings.           

  NFR-007           Observability             Log request IDs,    Log review and
                                              ingestion outcomes  error-path tests.
                                              and job failures    
                                              without sensitive   
                                              payloads.           

  NFR-008           Performance               Establish baseline  Repeatable local
                                              response-time       load test.
                                              targets after the   
                                              initial corpus is   
                                              fixed; avoid        
                                              unsupported speed   
                                              claims.             

  NFR-009           Data integrity            Use constraints and Migration and
                                              transactions for    repository tests.
                                              core metadata and   
                                              user-owned records. 

  NFR-010           Accessibility/readiness   API errors and      API contract
                                              validation messages tests.
                                              should be clear     
                                              enough for a        
                                              frontend to display 
                                              usefully.           

  NFR-011           Compatibility             Public API          Contract tests.
                                              responses must      
                                              follow documented   
                                              schemas; breaking   
                                              changes require an  
                                              API version or      
                                              explicit migration. 

  NFR-012           Responsible sourcing      Use public data     Source review
                                              sources only under  checklist.
                                              permitted terms;    
                                              respect rate limits 
                                              and access          
                                              restrictions.       
  ---------------------------------------------------------------------------------

## 6. Database Design

### 6.1 Entity summary

  -----------------------------------------------------------------------
  Entity                  Purpose                 Key relationships
  ----------------------- ----------------------- -----------------------
  papers                  Canonical               Many-to-many with
                          research-paper          authors and keywords;
                          metadata.               optional category.

  authors                 Normalized author names Many-to-many with
                          and available           papers.
                          identifiers.            

  paper_authors           Connect papers to       Paper + author.
                          authors and preserve    
                          author order.           

  keywords                Normalized keyword      Many-to-many with
                          vocabulary.             papers.

  paper_keywords          Connect papers to       Paper + keyword.
                          keywords.               

  categories              Research categories     One category may be
                          used for browsing and   assigned to many
                          labels.                 papers; predicted
                                                  labels may be stored
                                                  separately if needed.

  ingestion_runs          Records source imports  One run can
                          and outcomes.           create/update many
                                                  papers.

  saved_papers            User's saved library.   User + paper, unique
                                                  pair.

  users                   User account and role   One user has many saved
                          information, if account papers.
                          features are enabled.   

  relevance_judgments     Human-assigned          Query set/query and
                          relevance labels for    paper.
                          query-paper pairs.      

  evaluation_runs         Metadata and summary    May reference a dataset
                          metrics for             or evaluation set
                          search/model            version.
                          evaluation.             

  evaluation_metrics      Individual named metric Belongs to an
                          values for an           evaluation run.
                          evaluation run.         
  -----------------------------------------------------------------------

### 6.2 Table: papers

  --------------------------------------------------------------------------
  Column                  Suggested type          Rules / meaning
  ----------------------- ----------------------- --------------------------
  id                      UUID                    Primary key, generated
                                                  internally.

  title                   TEXT                    Required display title;
                                                  reject blank values.

  abstract                TEXT, nullable          Available abstract;
                                                  absence is allowed.

  publication_year        SMALLINT, nullable      Validate plausible range
                                                  without assuming every
                                                  source has a year.

  doi                     VARCHAR, nullable       Normalize when available;
                                                  unique when non-null after
                                                  normalization.

  source_name             VARCHAR                 Source provider or dataset
                                                  name.

  source_url              TEXT, nullable          Original record URL when
                                                  available.

  external_id             VARCHAR, nullable       Identifier assigned by
                                                  source.

  document_type           VARCHAR, nullable       Paper, preprint,
                                                  conference record, etc.,
                                                  when known.

  language                VARCHAR, nullable       Language code when known.

  raw_metadata            JSONB, nullable         Selected source metadata
                                                  retained for
                                                  provenance/reprocessing.

  normalized_text         TEXT, nullable          Derived searchable text;
                                                  rebuildable from canonical
                                                  fields.

  created_at              TIMESTAMPTZ             Creation timestamp.

  updated_at              TIMESTAMPTZ             Last update timestamp.
  --------------------------------------------------------------------------

### 6.3 Supporting tables

  -------------------------------------------------------------------------------------------
  Table                               Columns and constraints
  ----------------------------------- -------------------------------------------------------
  authors                             `id UUID PK`, `display_name TEXT NOT NULL`,
                                      `normalized_name TEXT NOT NULL`,
                                      `external_id TEXT NULL`, `created_at TIMESTAMPTZ`;
                                      index normalized name.

  paper_authors                       `paper_id UUID FK`, `author_id UUID FK`,
                                      `author_order INT NOT NULL`; composite PK
                                      `(paper_id, author_id)`; unique
                                      `(paper_id, author_order)`.

  keywords                            `id UUID PK`, `display_term TEXT NOT NULL`,
                                      `normalized_term TEXT NOT NULL UNIQUE`,
                                      `created_at TIMESTAMPTZ`.

  paper_keywords                      `paper_id UUID FK`, `keyword_id UUID FK`,
                                      `origin VARCHAR NOT NULL` (source/manual/extracted);
                                      composite PK `(paper_id, keyword_id, origin)` or an
                                      agreed unique pair if multiple origins are not needed.

  categories                          `id UUID PK`, `name VARCHAR NOT NULL UNIQUE`,
                                      `description TEXT NULL`.

  paper_categories                    `paper_id UUID FK`, `category_id UUID FK`,
                                      `label_source VARCHAR NOT NULL` (verified/predicted),
                                      `confidence REAL NULL`, `model_version VARCHAR NULL`;
                                      primary key includes paper, category and label source
                                      as appropriate.

  users                               `id UUID PK`,
                                      `email CITEXT or normalized VARCHAR UNIQUE NOT NULL`,
                                      `password_hash TEXT NOT NULL` if password login is
                                      used, `role VARCHAR NOT NULL`,
                                      `is_active BOOLEAN NOT NULL`, `created_at TIMESTAMPTZ`,
                                      `updated_at TIMESTAMPTZ`.

  saved_papers                        `user_id UUID FK`, `paper_id UUID FK`,
                                      `created_at TIMESTAMPTZ`; composite PK
                                      `(user_id, paper_id)`.

  ingestion_runs                      `id UUID PK`, `source_name VARCHAR NOT NULL`,
                                      `status VARCHAR NOT NULL`, `started_at TIMESTAMPTZ`,
                                      `finished_at TIMESTAMPTZ NULL`, `records_seen INT`,
                                      `records_created INT`, `records_updated INT`,
                                      `records_skipped INT`, `error_count INT`,
                                      `summary JSONB NULL`.

  relevance_judgments                 `id UUID PK`, `query_id VARCHAR NOT NULL`,
                                      `paper_id UUID FK`,
                                      `relevance_grade SMALLINT NOT NULL`,
                                      `judge_id VARCHAR NULL`,
                                      `dataset_version VARCHAR NOT NULL`; unique
                                      `(query_id, paper_id, dataset_version)`.

  evaluation_runs                     `id UUID PK`, `evaluation_type VARCHAR NOT NULL`,
                                      `dataset_version VARCHAR NOT NULL`,
                                      `query_set_version VARCHAR NULL`,
                                      `model_or_ranker VARCHAR NOT NULL`,
                                      `parameters JSONB NULL`, `started_at TIMESTAMPTZ`,
                                      `finished_at TIMESTAMPTZ NULL`,
                                      `status VARCHAR NOT NULL`.

  evaluation_metrics                  `id UUID PK`, `evaluation_run_id UUID FK`,
                                      `metric_name VARCHAR NOT NULL`, `cutoff_k INT NULL`,
                                      `metric_value DOUBLE PRECISION NOT NULL`,
                                      `details JSONB NULL`.
  -------------------------------------------------------------------------------------------

### 6.4 Data model rules

  -----------------------------------------------------------------------
  ID                                  Rule
  ----------------------------------- -----------------------------------
  DB-01                               Use UUID primary keys for internal
                                      entities.

  DB-02                               Enforce foreign keys and
                                      appropriate unique constraints in
                                      PostgreSQL.

  DB-03                               Normalize DOI and source
                                      identifiers before uniqueness
                                      checks.

  DB-04                               Do not require abstract, DOI,
                                      author or year when legitimate
                                      source records may omit them.

  DB-05                               Preserve paper display text;
                                      normalized/searchable text is
                                      derived data.

  DB-06                               Deletion behavior must be explicit;
                                      avoid cascading user or paper
                                      deletion unexpectedly.

  DB-07                               Model/index artifacts must record
                                      corpus version and creation
                                      settings outside or alongside the
                                      artifact.

  DB-08                               Use migrations for all schema
                                      changes; do not rely on automatic
                                      table creation in production.
  -----------------------------------------------------------------------

## 7. API Conventions

  ----------------------------------------------------------------------------------------------------------------
  Item                                Contract
  ----------------------------------- ----------------------------------------------------------------------------
  Base path                           `/api/v1`

  Data format                         JSON for request and response bodies unless an endpoint explicitly returns a
                                      file.

  Identifiers                         UUID strings for internal IDs.

  Pagination                          `page` starts at 1; `page_size` defaults to 20 and has a documented maximum
                                      (initial proposal: 100).

  Sorting                             Only documented sort fields and directions are accepted.

  Validation                          Invalid parameters return HTTP 422 with field-level detail.

  Authentication                      Bearer access token for protected routes if account features are enabled.

  Timestamps                          ISO 8601 timestamps with timezone.

  Error envelope                      `{"error":{"code":"...","message":"...","details":{},"request_id":"..."}}`

  Success envelope                    Use stable endpoint-specific response schemas; include pagination metadata
                                      for lists.

  Versioning                          Breaking response changes require a versioned API path or explicit migration
                                      plan.

  Documentation                       OpenAPI schema must be generated from the API and checked as part of backend
                                      acceptance.
  ----------------------------------------------------------------------------------------------------------------

## 8. API Contracts

### 8.1 Health and readiness

  ------------------------------------------------------------------------------------------------------
  Field                               Contract
  ----------------------------------- ------------------------------------------------------------------
  Method and path                     `GET /api/v1/health`

  Purpose                             Return service health without exposing secrets.

  Auth                                Public, minimal response.

  Success                             `200 OK`

  Example response                    `{"status":"ok","service":"scholarpulse-api","version":"1.0.0"}`

  Failure behavior                    Readiness checks may use a separate protected/internal endpoint if
                                      they expose dependency details.

  Why                                 Supports deployment checks and troubleshooting.
  ------------------------------------------------------------------------------------------------------

### 8.2 Search papers

  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Field                               Contract
  ----------------------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Method and path                     `GET /api/v1/search`

  Purpose                             Search and rank research papers.

  Query parameters                    `q` required; `ranker` = `bm25` (default), `tfidf`, `query_likelihood`, or `boolean`; optional `year_from`, `year_to`, `author`, `category`, `keyword`, `page`, `page_size`, `sort_by`, `sort_order`.

  Validation                          Reject blank `q`, invalid year ranges, unsupported rankers/sort fields and invalid pagination.

  Success                             `200 OK`

  Example request                     `/api/v1/search?q=machine%20learning&ranker=bm25&page=1&page_size=20`

  Example response                    `{"query":"machine learning","ranker":"bm25","items":[{"paper_id":"UUID","title":"Example title","abstract_snippet":"Example abstract...","publication_year":2025,"authors":["Example Author"],"categories":["AI"],"source_url":"https://example.org/paper","score":4.82}],"pagination":{"page":1,"page_size":20,"total_items":1,"total_pages":1}}`

  Errors                              `422` invalid query/filters; `500` unexpected internal failure with safe error envelope.

  Why                                 This is the primary product API and allows the same corpus to be searched with comparable retrieval approaches.
  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### 8.3 List and retrieve papers

  -----------------------------------------------------------------------
  Field                               Contract
  ----------------------------------- -----------------------------------
  List method/path                    `GET /api/v1/papers`

  Detail method/path                  `GET /api/v1/papers/{paper_id}`

  List parameters                     Optional `q`, `year_from`,
                                      `year_to`, `author`, `category`,
                                      `page`, `page_size`.

  Detail response fields              `id`, `title`, `abstract`,
                                      `publication_year`, `doi`,
                                      `authors`, `keywords`,
                                      `categories`, `source_name`,
                                      `source_url`, `created_at`,
                                      `updated_at`.

  Success                             `200 OK`

  Errors                              `404` unknown paper ID; `422`
                                      malformed filters or ID.

  Why                                 Separates collection browsing from
                                      the detailed record view.
  -----------------------------------------------------------------------

### 8.4 Related papers

  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Field                               Contract
  ----------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------
  Method/path                         `GET /api/v1/papers/{paper_id}/related`

  Parameters                          `limit` (default 10, documented maximum 50).

  Behavior                            Return papers ranked by content similarity; exclude the requested paper.

  Response                            `{"paper_id":"UUID","items":[{"paper_id":"UUID","title":"Related title","similarity_score":0.73,"source_url":"https://example.org/paper"}]}`

  Errors                              `404` paper not found; empty list if no meaningful related records exist.

  Why                                 Supports continued research exploration.
  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### 8.5 Categories and keywords

  -----------------------------------------------------------------------------------------------
  Field                               Contract
  ----------------------------------- -----------------------------------------------------------
  Categories                          `GET /api/v1/categories`

  Keywords                            `GET /api/v1/keywords?prefix=machine&page=1&page_size=20`

  Behavior                            Return available categories or matching normalized keyword
                                      terms.

  Response                            Paginated or bounded list of IDs, display labels and
                                      optional counts.

  Why                                 Supports filters and exploration without requiring users to
                                      know exact terms.
  -----------------------------------------------------------------------------------------------

### 8.6 Research analytics

  -----------------------------------------------------------------------------------------------------------------------
  Field                               Contract
  ----------------------------------- -----------------------------------------------------------------------------------
  Publication trends                  `GET /api/v1/analytics/publications?year_from=2015&year_to=2026`

  Category distribution               `GET /api/v1/analytics/categories`

  Cluster summary                     `GET /api/v1/analytics/clusters?model_version=...`

  Keyword associations                `GET /api/v1/analytics/associations?min_support=0.02&min_confidence=0.3&limit=20`

  Response principle                  Return data points, labels, units and relevant dataset/version metadata; do not
                                      return only pre-rendered chart images.

  Validation                          Bound numeric parameters and reject invalid ranges.

  Why                                 Keeps analytical results reusable by different presentation clients.
  -----------------------------------------------------------------------------------------------------------------------

### 8.7 Classification and clustering

  -----------------------------------------------------------------------------------------------------------------------------------------------
  Field                               Contract
  ----------------------------------- -----------------------------------------------------------------------------------------------------------
  Classification endpoint             `POST /api/v1/analysis/classify`

  Request                             `{"paper_id":"UUID"}` or a bounded text input with documented maximum length; do not accept both unless
                                      explicitly defined.

  Response                            `{"paper_id":"UUID","predicted_categories":[{"name":"AI","score":0.87}],"model_version":"classifier-v1"}`

  Clusters endpoint                   `GET /api/v1/analysis/clusters?model_version=...`

  Cluster detail                      `GET /api/v1/analysis/clusters/{cluster_id}/papers?page=1&page_size=20`

  Errors                              `404` unknown paper/cluster; `422` invalid request; `503` model artifact unavailable.

  Why                                 Makes model outputs inspectable and keeps prediction metadata explicit.
  -----------------------------------------------------------------------------------------------------------------------------------------------

### 8.8 Association rules

  ---------------------------------------------------------------------------------------------------------------------------------------------------
  Field                               Contract
  ----------------------------------- ---------------------------------------------------------------------------------------------------------------
  Method/path                         `GET /api/v1/analysis/association-rules?min_support=0.02&min_confidence=0.3&min_lift=1.0&page=1&page_size=20`

  Response fields                     Antecedent terms, consequent terms, support, confidence, lift and dataset/model version.

  Validation                          Require support in `(0,1]`, confidence in `(0,1]`, lift greater than or equal to zero, and bounded pagination.

  Errors                              `422` invalid thresholds; `503` if the latest association artifact is unavailable.

  Why                                 Provides transparent evidence for keyword co-occurrence patterns.
  ---------------------------------------------------------------------------------------------------------------------------------------------------

### 8.9 Search evaluation

  ---------------------------------------------------------------------------------------------------------------------------------
  Field                               Contract
  ----------------------------------- ---------------------------------------------------------------------------------------------
  Summary method/path                 `GET /api/v1/evaluation/search?query_set_version=...`

  Run method/path                     `POST /api/v1/evaluation/search-runs`

  Request                             `{"query_set_version":"v1","rankers":["tfidf","bm25","query_likelihood"],"cutoffs":[5,10]}`

  Response                            Evaluation run ID, status, dataset version, rankers and metric summaries for Precision@K,
                                      Recall@K, MAP and NDCG@K.

  Access                              Evaluation run creation restricted to authorized users/admins.

  Errors                              `422` unknown query set or unsupported ranker; `409` incompatible evaluation configuration.

  Why                                 Allows repeatable and defensible comparison of retrieval methods.
  ---------------------------------------------------------------------------------------------------------------------------------

### 8.10 Ingestion administration

  -----------------------------------------------------------------------------------------------------------
  Field                               Contract
  ----------------------------------- -----------------------------------------------------------------------
  Start run                           `POST /api/v1/admin/ingestion-runs`

  Request                             `{"source":"approved_source_name","mode":"incremental","limit":1000}`

  Get run                             `GET /api/v1/admin/ingestion-runs/{run_id}`

  List runs                           `GET /api/v1/admin/ingestion-runs?page=1&page_size=20`

  Behavior                            Only approved source adapters and supported modes may be used. Record
                                      counts, errors and timestamps.

  Access                              Admin only.

  Errors                              `401` unauthenticated; `403` not authorized; `422` invalid
                                      source/mode/limit; `409` incompatible concurrent run if concurrency is
                                      restricted.

  Why                                 Makes data refreshes traceable and manageable.
  -----------------------------------------------------------------------------------------------------------

### 8.11 Saved library and authentication

  ---------------------------------------------------------------------------------------
  Field                               Contract
  ----------------------------------- ---------------------------------------------------
  Authentication                      If enabled, `POST /api/v1/auth/register`,
                                      `POST /api/v1/auth/login`, and
                                      `POST /api/v1/auth/refresh` or a simpler documented
                                      session model.

  List saved papers                   `GET /api/v1/me/saved-papers?page=1&page_size=20`

  Save paper                          `PUT /api/v1/me/saved-papers/{paper_id}`

  Remove saved paper                  `DELETE /api/v1/me/saved-papers/{paper_id}`

  Access rule                         A user may only view or modify their own saved
                                      library.

  Errors                              `401` unauthenticated; `403` forbidden; `404` paper
                                      not found; `422` invalid input.

  Why                                 Supports personal research organization without
                                      exposing one user's saved records to another.
  ---------------------------------------------------------------------------------------

## 9. Error Handling Contract

  --------------------------------------------------------------------------------
  HTTP status       When to use          Error code example      Expected behavior
  ----------------- -------------------- ----------------------- -----------------
  400               Malformed request    `BAD_REQUEST`           Explain the issue
                    not covered by                               safely.
                    normal validation.                           

  401               Authentication is    `UNAUTHENTICATED`       Do not reveal
                    missing or invalid.                          protected data.

  403               User lacks           `FORBIDDEN`             Do not execute
                    permission.                                  the operation.

  404               Requested record or  `NOT_FOUND`             Return a stable
                    resource does not                            error shape.
                    exist.                                       

  409               Request conflicts    `CONFLICT`              Explain the
                    with current state.                          conflict without
                                                                 exposing
                                                                 internals.

  422               Input validation     `VALIDATION_ERROR`      Include
                    failed.                                      field-level
                                                                 validation
                                                                 details.

  429               Request rate limit   `RATE_LIMITED`          Include retry
                    exceeded, where rate                         guidance when
                    limiting applies.                            appropriate.

  500               Unexpected internal  `INTERNAL_ERROR`        Return safe
                    error.                                       message and
                                                                 request ID; log
                                                                 details
                                                                 server-side.

  503               Required             `SERVICE_UNAVAILABLE`   Communicate
                    model/index/source                           temporary
                    dependency is                                unavailability
                    unavailable.                                 without false
                                                                 success.
  --------------------------------------------------------------------------------

## 10. Folder Structure

``` text
scholarpulse/
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── migrations/
│   │   ├── env.py
│   │   └── versions/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py
│   │   │       └── endpoints/
│   │   │           ├── health.py
│   │   │           ├── search.py
│   │   │           ├── papers.py
│   │   │           ├── categories.py
│   │   │           ├── analytics.py
│   │   │           ├── analysis.py
│   │   │           ├── evaluation.py
│   │   │           ├── auth.py
│   │   │           ├── library.py
│   │   │           └── admin.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   ├── errors.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── session.py
│   │   │   └── base.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── ingestion/
│   │   │   ├── adapters/
│   │   │   ├── validation.py
│   │   │   └── deduplication.py
│   │   ├── preprocessing/
│   │   ├── retrieval/
│   │   │   ├── tokenizer.py
│   │   │   ├── inverted_index.py
│   │   │   ├── boolean.py
│   │   │   ├── tfidf.py
│   │   │   ├── bm25.py
│   │   │   ├── language_model.py
│   │   │   └── passage.py
│   │   ├── data_science/
│   │   │   ├── classification.py
│   │   │   ├── clustering.py
│   │   │   ├── association_rules.py
│   │   │   └── trends.py
│   │   ├── recommendations/
│   │   ├── evaluation/
│   │   └── artifacts/
│   └── tests/
│       ├── unit/
│       ├── integration/
│       ├── contract/
│       └── fixtures/
├── datasets/
│   ├── README.md
│   ├── raw/
│   └── processed/
├── artifacts/
│   ├── indexes/
│   ├── models/
│   └── evaluations/
├── docs/
│   ├── PRD.md
│   ├── SRS.md
│   └── API-CONTRACTS.md
├── scripts/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

  ------------------------------------------------------------------------
  Folder                  Responsibility           Rule
  ----------------------- ------------------------ -----------------------
  `api/`                  HTTP routes and          Keep business logic out
                          request/response         of route handlers.
                          handling.                

  `schemas/`              API request and response Public contracts are
                          validation.              explicit and stable.

  `models/`               Database entity          Persistence entities
                          definitions.             are separate from API
                                                   schemas.

  `repositories/`         Database access.         Avoid direct database
                                                   queries scattered
                                                   across endpoints.

  `services/`             Product/application use  Orchestrate
                          cases.                   repositories and domain
                                                   modules.

  `retrieval/`            Search and ranking       Keep algorithms
                          algorithms.              independently
                                                   unit-testable.

  `data_science/`         Classification,          Record model/data
                          clustering, association  versions for
                          and trend analysis.      reproducibility.

  `evaluation/`           Search/model evaluation. Evaluation must use
                                                   documented test data.

  `ingestion/`            Approved source adapters Respect source terms
                          and import validation.   and rate limits.

  `artifacts/`            Derived                  Rebuildable, versioned
                          index/model/evaluation   and excluded from Git
                          outputs.                 when large.

  `tests/`                Unit, integration and    Backend gates must pass
                          contract tests.          before frontend work
                                                   begins.
  ------------------------------------------------------------------------

## 11. Backend Testing Requirements

  ---------------------------------------------------------------------------------
  Test ID           Area                   What must be tested?  Why?
  ----------------- ---------------------- --------------------- ------------------
  T-001             Data validation        Required title,       Prevents bad
                                           optional metadata,    records entering
                                           invalid years and     the corpus.
                                           malformed             
                                           identifiers.          

  T-002             Deduplication          Exact DOI match,      Protects data
                                           source-ID match,      integrity.
                                           normalized-title      
                                           match and ambiguous   
                                           near-duplicates.      

  T-003             Inverted index         Term postings,        Confirms index
                                           missing terms,        correctness.
                                           updates and           
                                           deterministic         
                                           serialization.        

  T-004             Boolean retrieval      AND, OR, NOT,         Confirms query
                                           precedence policy and semantics.
                                           empty results.        

  T-005             Ranking                Known small corpus    Detects scoring
                                           produces expected     regressions.
                                           relative ordering for 
                                           TF-IDF and BM25       
                                           fixtures.             

  T-006             Language model         Smoothing prevents    Prevents invalid
                                           zero probability for  query-likelihood
                                           unseen terms.         scores.

  T-007             Classification         Training/evaluation   Prevents
                                           separation, expected  misleading model
                                           output schema and     evaluation.
                                           metric generation.    

  T-008             Clustering             Stable output schema, Makes clustering
                                           empty/small corpus    usable and
                                           handling and quality  testable.
                                           metric availability   
                                           where applicable.     

  T-009             Association mining     Support, confidence   Verifies the
                                           and lift match        syllabus formulas.
                                           hand-calculated       
                                           fixtures.             

  T-010             API contracts          Status codes,         Protects future
                                           response schemas,     frontend
                                           validation and        integration.
                                           pagination.           

  T-011             Authorization          User cannot access    Protects private
                                           another user's saved  data and
                                           papers; admin         operations.
                                           endpoints reject      
                                           non-admins.           

  T-012             Ingestion              Timeouts, source      Prevents
                                           errors, retries,      external-source
                                           partial failures and  failures from
                                           run summaries.        corrupting the
                                                                 system.

  T-013             Evaluation             Same versioned        Supports academic
                    reproducibility        corpus, query set and credibility.
                                           configuration produce 
                                           repeatable metrics    
                                           within defined        
                                           tolerance.            

  T-014             Health/configuration   Missing required      Improves
                                           configuration fails   operational
                                           clearly; health       readiness.
                                           response does not     
                                           leak secrets.         
  ---------------------------------------------------------------------------------

## 12. Security and Data Governance

  ------------------------------------------------------------------------
  ID                      Requirement              Why
  ----------------------- ------------------------ -----------------------
  SEC-01                  Keep secrets in          Prevents credential
                          environment              leakage.
                          configuration and        
                          provide only placeholder 
                          values in                
                          `.env.example`.          

  SEC-02                  Validate all user inputs Reduces abuse and
                          and enforce query/text   accidental resource
                          size limits.             exhaustion.

  SEC-03                  Use password hashing and Protects account
                          a documented             credentials.
                          authentication/session   
                          approach if login is     
                          enabled.                 

  SEC-04                  Enforce authorization in Prevents direct API
                          backend services, not    access to protected
                          only in the frontend.    operations.

  SEC-05                  Use parameterized        Reduces injection risk.
                          database access through  
                          the ORM or safe query    
                          mechanisms.              

  SEC-06                  Restrict administrative  Protects costly or
                          ingestion and            sensitive operations.
                          evaluation-run creation  
                          to authorized roles.     

  SEC-07                  Avoid storing full text  Respects copyright and
                          unless permitted;        source conditions.
                          preserve source          
                          attribution and access   
                          restrictions.            

  SEC-08                  Do not log passwords,    Reduces privacy and
                          access tokens or         security exposure.
                          unnecessary personal     
                          information.             

  SEC-09                  Define backup and        Protects persistent
                          restore expectations for records.
                          the database before      
                          deployment.              

  SEC-10                  Do not expose stack      Reduces information
                          traces or internal       leakage.
                          configuration in public  
                          API errors.              
  ------------------------------------------------------------------------

## 13. Backend-First Implementation Plan

  -----------------------------------------------------------------------
  Phase                   Deliverables            Exit gate --- all must
                                                  pass before moving on
  ----------------------- ----------------------- -----------------------
  B0 --- Repository and   Backend package,        Application starts from
  configuration           configuration, logging, documented
                          error format, database  instructions;
                          connection and health   configuration errors
                          route.                  are clear; health route
                                                  works.

  B1 --- Database         Initial schema,         Migrations apply on a
  foundation              migrations,             clean database;
                          repositories and        constraints and
                          paper/author/keyword    repository tests pass.
                          relationships.          

  B2 --- Ingestion and    One approved metadata   Import is repeatable;
  preprocessing           source or import file,  failures are reported;
                          validation,             duplicate fixtures
                          deduplication,          behave as expected.
                          ingestion-run tracking. 

  B3 --- Retrieval core   Tokenization policy,    Unit tests pass; API
                          inverted index, Boolean can search a fixed
                          retrieval, TF-IDF and   fixture corpus; index
                          BM25.                   can be rebuilt.

  B4 --- Retrieval        Query-likelihood model, Evaluation is
  completion and          passage snippets where  reproducible and
  evaluation              available, judged query reports documented
                          set, IR metrics.        metrics.

  B5 --- Data Science     Classification,         Models produce expected
  modules                 K-means, hierarchical   schemas; evaluation
                          comparison, Apriori     outputs and limitations
                          rules and trends.       are documented.

  B6 --- Product APIs     Paper endpoints, search OpenAPI contract is
                          filters, analytics,     reviewed; API
                          related papers, admin   integration tests pass;
                          ingestion status and    authorization tests
                          optional library/auth.  pass where applicable.

  B7 --- Backend          Logging, error          All required tests
  hardening               handling, configuration pass; known limitations
                          review, database backup are documented; clean
                          guidance and smoke/load setup is reproducible.
                          tests.                  

  B8 --- Backend          Freeze API contracts,   All mandatory backend
  acceptance              sample                  gates below pass. Only
                          requests/responses,     then start frontend
                          seed/demo data and      implementation.
                          backend README.         
  -----------------------------------------------------------------------

### 13.1 Backend acceptance gates before frontend

  -----------------------------------------------------------------------
  Gate ID                             Required condition
  ----------------------------------- -----------------------------------
  GATE-01                             Clean environment setup and
                                      database migrations work from the
                                      documented instructions.

  GATE-02                             Approved dataset can be imported,
                                      validated, deduplicated and
                                      queried.

  GATE-03                             Search APIs support documented
                                      ranking modes, filters, pagination
                                      and consistent errors.

  GATE-04                             Required IR algorithms have unit
                                      tests and a repeatable evaluation
                                      report.

  GATE-05                             Classification, clustering and
                                      association mining return
                                      documented results and evaluation
                                      outputs.

  GATE-06                             API schemas and example
                                      requests/responses are frozen for
                                      the first frontend integration.

  GATE-07                             Authentication/authorization tests
                                      pass for every enabled protected
                                      capability.

  GATE-08                             Health endpoint, logs, error
                                      handling and configuration checks
                                      work without exposing secrets.

  GATE-09                             No critical known data-loss,
                                      cross-user access or
                                      index-corruption issue remains
                                      open.

  GATE-10                             Backend README, setup instructions,
                                      sample data instructions and known
                                      limitations are complete.
  -----------------------------------------------------------------------

## 14. Definition of Done

  ---------------------------------------------------------------------------
  ID                      Deliverable             Completion condition
  ----------------------- ----------------------- ---------------------------
  DOD-01                  Feature                 Requirement is implemented
                                                  and documented.

  DOD-02                  Tests                   Relevant
                                                  unit/integration/contract
                                                  tests pass.

  DOD-03                  Data                    Data behavior and
                                                  missing-data handling are
                                                  verified.

  DOD-04                  API                     OpenAPI schema and example
                                                  response match actual
                                                  behavior.

  DOD-05                  Errors                  Expected failure cases
                                                  return documented safe
                                                  errors.

  DOD-06                  Security                Permissions and
                                                  sensitive-data handling are
                                                  tested where applicable.

  DOD-07                  Reproducibility         Model/index version and
                                                  evaluation settings are
                                                  recorded.

  DOD-08                  Documentation           Setup, behavior,
                                                  assumptions and limitations
                                                  are updated.
  ---------------------------------------------------------------------------

## 15. Open Decisions

  -----------------------------------------------------------------------
  ID                Decision          Proposed default  When to finalize
  ----------------- ----------------- ----------------- -----------------
  OD-01             Initial research  Start with one    Before ingestion
                    dataset/source    permitted public  implementation.
                                      metadata source   
                                      or a reviewed     
                                      dataset file.     

  OD-02             Corpus size       Start with a      Before
                                      manageable        performance
                                      sample; increase  targets.
                                      after memory and  
                                      evaluation        
                                      behavior is       
                                      measured.         

  OD-03             Text              Select NLTK or    During B2.
                    preprocessing     spaCy after       
                    library           comparing         
                                      requirements and  
                                      setup complexity. 

  OD-04             Authentication    Enable accounts   Before protected
                                      if saved          endpoints.
                                      library/admin     
                                      access is         
                                      included in the   
                                      first release;    
                                      otherwise keep    
                                      public discovery  
                                      and restrict      
                                      admin operations  
                                      using a           
                                      documented        
                                      mechanism.        

  OD-05             Artifact          Choose a          Before B3/B5
                    persistence       versioned format  completion.
                    format            suitable for the  
                                      selected          
                                      index/model       
                                      artifacts.        

  OD-06             Search relevance  Define after the  During B4.
                    targets           judged query set  
                                      exists.           

  OD-07             Performance       Set after corpus  During B7.
                    targets           size and local    
                                      baseline are      
                                      measured.         

  OD-08             Full crawler,     Treat as optional After B8.
                    distributed       unless core       
                    processing and    backend gates are 
                    graph ranking     complete.         
  -----------------------------------------------------------------------

## 16. PRD Traceability

  -----------------------------------------------------------------------
  PRD capability          SRS sections            Verification evidence
  ----------------------- ----------------------- -----------------------
  Research collection and 4, 6, 8.3, 8.10, 11     Repository and
  data quality                                    ingestion tests

  Search, ranking and     4, 7, 8.2, 8.3, 11      Search contract tests
  filters                                         and IR evaluation
                                                  report

  Paper details and       4, 6, 8.3               API contract tests
  source provenance                               

  Classification          4, 8.7, 11              Held-out classification
                                                  metrics

  Clustering              4, 8.7, 11              Cluster output and
                                                  quality indicators

  Association mining      4, 8.8, 11              Hand-calculated rule
                                                  fixtures

  Analytics               4, 8.6                  Aggregate API tests

  Search evaluation       4, 8.9                  Reproducible evaluation
                                                  run

  Related papers          4, 8.4                  Recommendation tests

  Saved library           4, 8.11                 Authorization and CRUD
                                                  tests

  Responsive frontend     3, 13                   Frontend phase after
                                                  backend acceptance

  Admin/data health       4, 8.10, 12             Permission and
                                                  ingestion-status tests
  -----------------------------------------------------------------------

## 17. Document Boundary

  -----------------------------------------------------------------------
  This SRS includes                   Separate implementation work will
                                      define
  ----------------------------------- -----------------------------------
  Technology stack and module         Exact pinned dependency versions
  responsibilities.                   after compatibility checks.

  Database entities, fields,          Final migration files and detailed
  relationships and constraints.      ORM code.

  API paths, parameters, schemas and  Actual route handlers and generated
  error behavior.                     OpenAPI output.

  Folder structure and backend        Detailed implementation tickets and
  phases.                             code.

  Quality, security and acceptance    Measured performance results and
  requirements.                       deployment-specific operational
                                      values.
  -----------------------------------------------------------------------

**End of SRS --- Version 1.0**
