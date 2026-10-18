# ScholarPulse — Backend API Specification & Frontend Wiring Guide

> **Document Version:** 1.0.0  
> **Backend Architecture:** Modular Monolith (FastAPI + SQLAlchemy 2.0 + SQLite/PostgreSQL + scikit-learn + mlxtend)  
> **Server Base URL:** `http://localhost:8000`  
> **API Version Prefix:** `/api/v1`  
> **OpenAPI Schema:** `http://localhost:8000/openapi.json`  
> **Interactive Swagger UI:** `http://localhost:8000/docs`  
> **Interactive ReDoc:** `http://localhost:8000/redoc`

This specification is the exact contract between the ScholarPulse backend and the React/TypeScript frontend. Feed this document to your frontend agent or ChatGPT to wire up all components, state hooks, and API client adapters.

---

## 1. Global Network & Protocol Standards

### 1.1 HTTP Headers
- **`Content-Type: application/json`** — Required on all `POST` requests.
- **`X-User-ID: <uuid>`** — Optional header specifying the active user ID for personal library bookmarking. If omitted, the backend automatically defaults to the deterministic demo user ID: `00000000-0000-0000-0000-000000000001`.
- **`X-Request-ID: <string>`** — Tracing ID returned in all response headers for debugging and correlation.

### 1.2 CORS Origins
Configured by default to allow browser requests from:
- `http://localhost:3000`
- `http://localhost:5173`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

### 1.3 Uniform Error Response Envelope
All error responses (`400`, `404`, `409`, `422`, `500`) return a unified JSON envelope:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Paper with ID 'e9b2512f-9dfb-402c-a2b1-591a5e1e1234' was not found.",
    "details": null,
    "request_id": "8a7c2930-cf22-4809-91a5-8e27c1f10abc"
  }
}
```

Standard Error Codes:
- `VALIDATION_ERROR` (HTTP 400 or 422) — Missing required parameter, invalid bounds, or `year_min > year_max`.
- `NOT_FOUND` (HTTP 404) — Entity (paper, cluster, or saved bookmark) not found.
- `CONFLICT` (HTTP 409) — Entity already exists (e.g. paper already bookmarked).
- `INTERNAL_ERROR` (HTTP 500) — Server error. Internal stack traces and secrets are strictly stripped.

---

## 2. API Endpoints by Screen

---

### SCREEN 1: Search & Discovery (`/search`)

#### `GET /api/v1/search`
Executes ranked information retrieval search across paper titles and abstracts.

**Query Parameters:**
| Parameter | Type | Required | Default | Allowed Values / Bounds | Description |
|---|---|:---:|:---:|---|---|
| `query` | `string` | **Yes** | — | `1 <= len <= 500` | Search text or Boolean expression |
| `method` | `string` | No | `"bm25"` | `"bm25"`, `"tfidf"`, `"language_model"`, `"boolean"` | IR ranking algorithm to execute |
| `page` | `integer`| No | `1` | `>= 1` | 1-indexed page number |
| `page_size` | `integer`| No | `20` | `1 <= page_size <= 100` | Number of results per page |
| `year_min` | `integer`| No | `null` | `1900 <= year <= 2100` | Minimum publication year |
| `year_max` | `integer`| No | `null` | `1900 <= year <= 2100` | Maximum publication year |
| `category` | `string` | No | `null` | Any category name | Category filter (case-insensitive) |

**Sample Response (`200 OK`):**
```json
{
  "query": "transformer attention mechanism",
  "method": "bm25",
  "total_hits": 14,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "doc_id": "10.1145/3397271.3401075",
      "score": 4.8219,
      "rank": 1,
      "method": "bm25",
      "term_scores": {
        "transform": 2.4109,
        "attent": 2.411
      },
      "metadata": {
        "title": "Attention Is All You Need",
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
        "publication_year": 2017,
        "categories": ["Natural Language Processing", "Machine Learning"],
        "keywords": ["transformer", "attention mechanism", "deep learning"],
        "authors": [
          {"name": "Ashish Vaswani", "order": 1},
          {"name": "Noam Shazeer", "order": 2}
        ],
        "doi": "10.1145/3397271.3401075",
        "source_name": "ACM Digital Library"
      },
      "snippet": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
      "highlighted_snippet": "The dominant sequence transduction models are based on <mark>transformer</mark> and <mark>attention</mark> mechanisms..."
    }
  ]
}
```

**Frontend Implementation Checklist:**
- Render `highlighted_snippet` using `dangerouslySetInnerHTML={{ __html: item.highlighted_snippet }}`.
- Style `<mark>` tags with subtle background (e.g. `background-color: #EAF2FF; color: #246BFD; font-weight: 600; padding: 0 2px; border-radius: 2px;`).
- Provide an algorithm switcher in the UI: `BM25 (Default)`, `TF-IDF (Cosine)`, `Language Model (Dirichlet)`, `Boolean Search`.
- If `total_hits === 0`, display a clean empty state with recommendations to adjust keywords.

---

### SCREEN 2: Research Papers Directory & Details (`/papers`)

#### `GET /api/v1/papers`
Paginated directory of papers with multifaceted filtering.

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|---|---|:---:|:---:|---|
| `page` | `integer` | No | `1` | 1-indexed page |
| `page_size` | `integer` | No | `20` | Items per page (max 100) |
| `year_from` | `integer` | No | `null` | Minimum publication year |
| `year_to` | `integer` | No | `null` | Maximum publication year |
| `author` | `string` | No | `null` | Author display name filter |
| `category` | `string` | No | `null` | Category name filter |
| `keyword` | `string` | No | `null` | Keyword filter |

**Sample Response (`200 OK`):**
```json
{
  "total": 25,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": "e9b2512f-9dfb-402c-a2b1-591a5e1e1234",
      "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
      "abstract": "We introduce a new language representation model called BERT...",
      "publication_year": 2018,
      "doi": "10.18653/v1/N19-1423",
      "source_name": "ACL Anthology",
      "source_url": "https://doi.org/10.18653/v1/N19-1423",
      "authors": ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
      "categories": ["Natural Language Processing", "Machine Learning"],
      "keywords": ["bert", "language representation", "deep learning"]
    }
  ]
}
```

---

#### `GET /api/v1/papers/{id}`
Returns full canonical metadata for a single paper.

**Path Parameters:**
- `id` (`uuid`): Paper UUID identifier.

**Sample Response (`200 OK`):**
```json
{
  "id": "e9b2512f-9dfb-402c-a2b1-591a5e1e1234",
  "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
  "abstract": "We introduce a new language representation model called BERT...",
  "publication_year": 2018,
  "doi": "10.18653/v1/N19-1423",
  "source_name": "ACL Anthology",
  "source_url": "https://doi.org/10.18653/v1/N19-1423",
  "external_id": "corpus_002",
  "document_type": "journal_article",
  "language": "en",
  "raw_metadata": {},
  "authors": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "display_name": "Jacob Devlin",
      "author_order": 1
    }
  ],
  "keywords": [
    {
      "id": "b1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "display_term": "BERT"
    }
  ],
  "categories": [
    {
      "id": "c1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "name": "Natural Language Processing",
      "label_source": "verified",
      "confidence": 1.0
    }
  ],
  "created_at": "2026-10-17T12:00:00Z",
  "updated_at": "2026-10-17T12:00:00Z"
}
```

---

#### `GET /api/v1/papers/{id}/related`
Content-based recommendation engine (FR-019) returning top similar papers based on TF-IDF cosine similarity, **guaranteed to exclude the seed paper**.

**Path Parameters:**
- `id` (`uuid`): Paper UUID.

**Query Parameters:**
- `top_n` (`integer`, default: `5`, range `1-50`): Max recommendations to return.

**Sample Response (`200 OK`):**
```json
[
  {
    "paper_id": "10.1145/3397271.3401075",
    "title": "Attention Is All You Need",
    "similarity_score": 0.4821,
    "shared_keywords": ["transformer", "deep learning"],
    "category": "Natural Language Processing",
    "publication_year": 2017
  }
]
```

---

### SCREEN 3: Taxonomy & Autocomplete

#### `GET /api/v1/categories`
Returns all academic categories with paper counts, sorted alphabetically.

**Sample Response (`200 OK`):**
```json
[
  {
    "id": "c1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Computer Vision",
    "description": "Visual representation learning, object detection, and CNNs.",
    "paper_count": 6
  },
  {
    "id": "c2b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Natural Language Processing",
    "description": "Computational linguistics, transformers, and language models.",
    "paper_count": 9
  }
]
```

#### `GET /api/v1/keywords`
Keyword vocabulary search for live search-bar autocomplete.

**Query Parameters:**
- `prefix` (`string`, optional): Prefix to search (e.g. `"att"`).
- `limit` (`integer`, default: `20`, range `1-100`): Max keywords to return.

**Sample Response (`200 OK`):**
```json
[
  {
    "id": "k1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "display_term": "Attention Mechanism",
    "normalized_term": "attention mechanism",
    "paper_count": 4
  }
]
```

---

### SCREEN 4: Data Science Analysis (`/analysis`)

#### `POST /api/v1/analysis/classify`
Supervised text categorization into research subjects.

**Request Body (`application/json`):**
*Option A: Classify raw text snippet:*
```json
{
  "text": "Deep residual neural networks with skip connections for high-accuracy image recognition on ImageNet.",
  "top_k": 3
}
```
*Option B: Classify an existing paper by ID:*
```json
{
  "paper_id": "e9b2512f-9dfb-402c-a2b1-591a5e1e1234",
  "top_k": 3
}
```

**Sample Response (`200 OK`):**
```json
{
  "paper_id": null,
  "predicted_categories": [
    {
      "name": "Computer Vision",
      "score": 0.8412
    },
    {
      "name": "Machine Learning",
      "score": 0.1254
    },
    {
      "name": "Natural Language Processing",
      "score": 0.0334
    }
  ],
  "model_version": "multinomial_nb-v1"
}
```

---

#### `GET /api/v1/analysis/clusters`
Unsupervised document clustering with explainable semantic topic labels and representative centroid papers.

**Query Parameters:**
- `method` (`string`, default: `"kmeans"`): `"kmeans"` or `"hierarchical"`.
- `n_clusters` (`integer`, default: `4`, range `2-10`): Target number of clusters.

**Sample Response (`200 OK`):**
```json
{
  "model_version": "clustering-v1",
  "method": "kmeans",
  "n_clusters": 3,
  "total_documents": 25,
  "silhouette_score": 0.0842,
  "inertia": 18.421,
  "clusters": [
    {
      "cluster_id": 0,
      "label": "transformer / attention / language",
      "size": 9,
      "top_terms": [
        {"term": "transformer", "weight": 0.4215},
        {"term": "attention", "weight": 0.3812},
        {"term": "language", "weight": 0.2981}
      ],
      "representative_papers": [
        {
          "paper_id": "10.1145/3397271.3401075",
          "title": "Attention Is All You Need",
          "similarity_to_centroid": 0.8921,
          "category": "Natural Language Processing"
        }
      ],
      "paper_ids": ["10.1145/3397271.3401075", "10.18653/v1/N19-1423"]
    }
  ]
}
```

---

#### `GET /api/v1/analysis/clusters/{cluster_id}/papers`
Member papers of a selected cluster.

**Path Parameters:**
- `cluster_id` (`integer`): ID of the cluster.

**Query Parameters:**
- `page` (`integer`, default: `1`)
- `page_size` (`integer`, default: `20`)

**Sample Response (`200 OK`):**
```json
{
  "cluster_id": 0,
  "label": "transformer / attention / language",
  "total": 9,
  "page": 1,
  "page_size": 20,
  "papers": [
    {
      "paper_id": "10.1145/3397271.3401075",
      "title": "Attention Is All You Need",
      "category": "Natural Language Processing",
      "publication_year": 2017
    }
  ]
}
```

---

#### `GET /api/v1/analysis/association-rules`
Apriori association-rule mining over keyword co-occurrences.

**Query Parameters:**
- `min_support` (`float`, default: `0.04`, range `0.0 < x <= 1.0`)
- `min_confidence` (`float`, default: `0.3`, range `0.0 < x <= 1.0`)
- `min_lift` (`float`, default: `1.0`, range `>= 0.0`)
- `page` (`integer`, default: `1`)
- `page_size` (`integer`, default: `20`)

**Sample Response (`200 OK`):**
```json
{
  "page": 1,
  "page_size": 20,
  "total_rules": 8,
  "total_pages": 1,
  "min_support": 0.04,
  "min_confidence": 0.3,
  "min_lift": 1.0,
  "model_version": "apriori-v1",
  "rules": [
    {
      "antecedents": ["transformer"],
      "consequents": ["attention mechanism"],
      "support": 0.16,
      "confidence": 0.8,
      "lift": 3.25,
      "leverage": 0.1108,
      "conviction": 3.77
    }
  ]
}
```

---

### SCREEN 5: Bibliometric Research Analytics (`/analytics`)

#### `GET /api/v1/analytics/overview`
Corpus aggregate statistics.
**Query Parameters:** `year_min` (`integer`), `year_max` (`integer`).

**Sample Response (`200 OK`):**
```json
{
  "total_papers": 25,
  "total_authors": 68,
  "total_categories": 5,
  "total_keywords": 92,
  "year_min": 1967,
  "year_max": 2024,
  "avg_authors_per_paper": 2.72
}
```

#### `GET /api/v1/analytics/trends`
Chronological publication volume and YoY growth % (ideal for Recharts `AreaChart` or `BarChart`).
**Query Parameters:** `year_min` (`integer`), `year_max` (`integer`).

**Sample Response (`200 OK`):**
```json
[
  {
    "year": 2017,
    "count": 4,
    "cumulative_count": 18,
    "growth_percentage": 33.33
  },
  {
    "year": 2018,
    "count": 5,
    "cumulative_count": 23,
    "growth_percentage": 25.0
  }
]
```

#### `GET /api/v1/analytics/categories`
Subject category market share distribution (ideal for Recharts `PieChart`).
**Query Parameters:** `year_min` (`integer`), `year_max` (`integer`).

**Sample Response (`200 OK`):**
```json
[
  {
    "category": "Natural Language Processing",
    "count": 9,
    "percentage_share": 36.0
  },
  {
    "category": "Computer Vision",
    "count": 6,
    "percentage_share": 24.0
  }
]
```

#### `GET /api/v1/analytics/keywords`
Top recurring keywords.
**Query Parameters:** `top_n` (`integer`, default: 20), `year_min`, `year_max`.

**Sample Response (`200 OK`):**
```json
[
  {
    "keyword": "deep learning",
    "count": 12,
    "percentage_share": 13.04
  },
  {
    "keyword": "neural network",
    "count": 9,
    "percentage_share": 9.78
  }
]
```

#### `GET /api/v1/analytics/collaboration-network`
Co-authorship collaboration network graph.
**Query Parameters:** `min_collaborations` (`integer`, default: 1), `year_min`, `year_max`.

**Sample Response (`200 OK`):**
```json
{
  "total_nodes": 68,
  "total_edges": 84,
  "nodes": [
    {
      "id": "Ashish Vaswani",
      "name": "Ashish Vaswani",
      "paper_count": 2
    }
  ],
  "edges": [
    {
      "source": "Ashish Vaswani",
      "target": "Noam Shazeer",
      "weight": 1,
      "paper_titles": ["Attention Is All You Need"]
    }
  ],
  "top_collaborators": [
    {
      "author_a": "Ashish Vaswani",
      "author_b": "Noam Shazeer",
      "collaborations": 1
    }
  ]
}
```

---

### SCREEN 6: Information Retrieval Evaluation (`/evaluation`)

#### `GET /api/v1/evaluation/retrieval`
Objective multi-ranker benchmarking report comparing BM25, TF-IDF, and Language Model against ground-truth judgments.

**Sample Response (`200 OK`):**
```json
{
  "dataset_version": "relevance-v1",
  "query_count": 5,
  "reports": [
    {
      "ranker_name": "bm25",
      "num_queries": 5,
      "mean_average_precision": 0.8124,
      "mean_reciprocal_rank": 0.9500,
      "precision_at_k": {
        "5": 0.6400,
        "10": 0.4200
      },
      "recall_at_k": {
        "5": 0.8500,
        "10": 1.0000
      },
      "ndcg_at_k": {
        "5": 0.8654,
        "10": 0.8841
      }
    },
    {
      "ranker_name": "tfidf",
      "num_queries": 5,
      "mean_average_precision": 0.7241,
      "mean_reciprocal_rank": 0.8667,
      "precision_at_k": {"5": 0.5600, "10": 0.3800},
      "recall_at_k": {"5": 0.7667, "10": 0.9200},
      "ndcg_at_k": {"5": 0.7812, "10": 0.8015}
    },
    {
      "ranker_name": "language_model",
      "num_queries": 5,
      "mean_average_precision": 0.7652,
      "mean_reciprocal_rank": 0.9000,
      "precision_at_k": {"5": 0.6000, "10": 0.4000},
      "recall_at_k": {"5": 0.8000, "10": 0.9600},
      "ndcg_at_k": {"5": 0.8245, "10": 0.8490}
    }
  ]
}
```

---

### SCREEN 7: Saved Papers Library (`/library`)

#### `GET /api/v1/library/papers`
List all research papers saved by the user (accepts optional `X-User-ID` header).

**Sample Response (`200 OK`):**
```json
{
  "total": 1,
  "items": [
    {
      "id": "e9b2512f-9dfb-402c-a2b1-591a5e1e1234",
      "paper_id": "e9b2512f-9dfb-402c-a2b1-591a5e1e1234",
      "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
      "notes": "Must read for literature review",
      "saved_at": "2026-10-17T12:30:00Z",
      "publication_year": 2018,
      "doi": "10.18653/v1/N19-1423"
    }
  ]
}
```

#### `POST /api/v1/library/papers`
Bookmark a research paper.

**Request Body (`application/json`):**
```json
{
  "paper_id": "e9b2512f-9dfb-402c-a2b1-591a5e1e1234",
  "notes": "Key paper on transformers"
}
```
**Response (`201 Created`):** Returns the newly saved item. Returns `409 Conflict` if the paper is already saved.

#### `DELETE /api/v1/library/papers/{paper_id}`
Removes a saved paper from the library.
**Response (`200 OK`):**
```json
{
  "status": "success",
  "message": "Paper removed from library."
}
```

---

### SCREEN 8: Administration & Ingestion (`/admin`)

#### `POST /api/v1/admin/ingest`
Triggers offline sample dataset ingestion.

**Request Body (`application/json`):**
```json
{
  "filepath": "datasets/raw/sample_papers.json",
  "source_name": "local_sample"
}
```
**Response (`200 OK`):**
```json
{
  "run_id": "d1e2f3a4-b5c6-7890-1234-56789abcdef0",
  "status": "completed",
  "total_processed": 25,
  "created_count": 25,
  "updated_count": 0,
  "skipped_count": 0,
  "error_count": 0
}
```

#### `GET /api/v1/admin/ingest/status?limit=10`
Returns ingestion history runs.
**Response (`200 OK`):**
```json
{
  "total_runs": 1,
  "runs": [
    {
      "run_id": "d1e2f3a4-b5c6-7890-1234-56789abcdef0",
      "source_name": "local_sample",
      "status": "completed",
      "total_records": 25,
      "created_count": 25,
      "updated_count": 0,
      "skipped_count": 0,
      "error_count": 0,
      "started_at": "2026-10-17T12:00:00Z",
      "finished_at": "2026-10-17T12:00:02Z"
    }
  ]
}
```

---

## 3. Ready-to-Use TypeScript Type Definitions (`src/types/api.ts`)

Copy-paste this directly into your React frontend project:

```typescript
// ==========================================
// Global Envelopes & Errors
// ==========================================

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any> | null;
  request_id?: string;
}

export interface ApiErrorEnvelope {
  error: ApiError;
}

// ==========================================
// Search & Retrieval Types
// ==========================================

export type IRMethod = "bm25" | "tfidf" | "language_model" | "boolean";

export interface SearchResultItem {
  doc_id: string;
  score: number;
  rank: number;
  method: string;
  term_scores: Record<string, number>;
  metadata: {
    title: string;
    abstract?: string;
    publication_year?: number;
    categories?: string[];
    keywords?: string[];
    authors?: Array<{ name: string; order: number }>;
    doi?: string;
    source_name?: string;
  };
  snippet?: string;
  highlighted_snippet?: string;
}

export interface SearchResponse {
  query: string;
  method: IRMethod;
  total_hits: number;
  page: number;
  page_size: number;
  results: SearchResultItem[];
}

// ==========================================
// Paper & Taxonomy Types
// ==========================================

export interface AuthorBrief {
  id: string;
  display_name: string;
  author_order: number;
}

export interface KeywordBrief {
  id: string;
  display_term: string;
}

export interface CategoryBrief {
  id: string;
  name: string;
  label_source: string;
  confidence?: number;
}

export interface PaperBrief {
  id: string;
  title: string;
  abstract?: string;
  publication_year?: number;
  doi?: string;
  source_name?: string;
  source_url?: string;
  authors: string[];
  categories: string[];
  keywords: string[];
}

export interface PaperDetail {
  id: string;
  title: string;
  abstract?: string;
  publication_year?: number;
  doi?: string;
  source_name?: string;
  source_url?: string;
  external_id?: string;
  document_type?: string;
  language?: string;
  raw_metadata?: Record<string, any>;
  authors: AuthorBrief[];
  keywords: KeywordBrief[];
  categories: CategoryBrief[];
  created_at?: string;
  updated_at?: string;
}

export interface PaperListResponse {
  total: number;
  page: number;
  page_size: number;
  items: PaperBrief[];
}

export interface RelatedPaperItem {
  paper_id: string;
  title: string;
  similarity_score: number;
  shared_keywords: string[];
  category?: string;
  publication_year?: number;
}

export interface CategoryItem {
  id: string;
  name: string;
  description?: string;
  paper_count: number;
}

export interface KeywordItem {
  id: string;
  display_term: string;
  normalized_term: string;
  paper_count: number;
}

// ==========================================
// Data Science & Analysis Types
// ==========================================

export interface PredictedCategory {
  name: string;
  score: number;
}

export interface ClassifyResponse {
  paper_id?: string;
  predicted_categories: PredictedCategory[];
  model_version: string;
}

export interface ClusterTopTerm {
  term: string;
  weight: number;
}

export interface RepresentativePaper {
  paper_id: string;
  title: string;
  similarity_to_centroid: number;
  category?: string;
}

export interface ClusterSummary {
  cluster_id: number;
  label: string;
  size: number;
  top_terms: ClusterTopTerm[];
  representative_papers: RepresentativePaper[];
  paper_ids: string[];
}

export interface ClustersResponse {
  model_version: string;
  method: "kmeans" | "hierarchical";
  n_clusters: number;
  total_documents: number;
  silhouette_score: number;
  inertia?: number;
  clusters: ClusterSummary[];
}

export interface AssociationRuleItem {
  antecedents: string[];
  consequents: string[];
  support: number;
  confidence: number;
  lift: number;
  leverage: number;
  conviction: number;
}

export interface AssociationRulesResponse {
  page: number;
  page_size: number;
  total_rules: number;
  total_pages: number;
  min_support: number;
  min_confidence: number;
  min_lift: number;
  model_version: string;
  rules: AssociationRuleItem[];
}

// ==========================================
// Analytics Types
// ==========================================

export interface OverviewSummary {
  total_papers: number;
  total_authors: number;
  total_categories: number;
  total_keywords: number;
  year_min?: number;
  year_max?: number;
  avg_authors_per_paper: number;
}

export interface TrendItem {
  year: number;
  count: number;
  cumulative_count: number;
  growth_percentage?: number;
}

export interface CategoryShare {
  category: string;
  count: number;
  percentage_share: number;
}

export interface KeywordShare {
  keyword: string;
  count: number;
  percentage_share: number;
}

export interface CollaborationNode {
  id: string;
  name: string;
  paper_count: number;
}

export interface CollaborationEdge {
  source: string;
  target: string;
  weight: number;
  paper_titles: string[];
}

export interface TopCollaboratorPair {
  author_a: string;
  author_b: string;
  collaborations: number;
}

export interface CollaborationNetwork {
  total_nodes: number;
  total_edges: number;
  nodes: CollaborationNode[];
  edges: CollaborationEdge[];
  top_collaborators: TopCollaboratorPair[];
}

// ==========================================
// Evaluation Types
// ==========================================

export interface EvaluationReportItem {
  ranker_name: string;
  num_queries: number;
  mean_average_precision: number;
  mean_reciprocal_rank: number;
  precision_at_k: Record<string, number>;
  recall_at_k: Record<string, number>;
  ndcg_at_k: Record<string, number>;
}

export interface EvaluationResponse {
  dataset_version: string;
  query_count: number;
  reports: EvaluationReportItem[];
}

// ==========================================
// Saved Library Types
// ==========================================

export interface SavedPaperItem {
  id: string;
  paper_id: string;
  title: string;
  notes?: string;
  saved_at: string;
  publication_year?: number;
  doi?: string;
}

export interface SavedLibraryResponse {
  total: number;
  items: SavedPaperItem[];
}
```

---

## 4. Academic Visual Tokens & Design Directives

The frontend must reflect a quiet, scholarly, data-dense editorial aesthetic (Light Theme). Do not style as a dark-mode neon SaaS dashboard.

```css
:root {
  /* Surfaces & Backgrounds */
  --bg-page: #F5F8FC;         /* Clean pale gray/blue backdrop */
  --bg-surface: #FFFFFF;      /* Pure white card backgrounds */
  
  /* Typography */
  --text-primary: #14233B;    /* Deep navy text for headings and titles */
  --text-secondary: #5F6F85;  /* Slate gray text for metadata and captions */
  
  /* Borders & Dividers */
  --border-color: #DCE5EF;    /* Subtle crisp border */
  
  /* Academic Accents */
  --primary-blue: #246BFD;    /* Vibrant scholarly blue for actions */
  --pale-blue: #EAF2FF;       /* Pill, badge, and mark backgrounds */
  
  /* Semantic Status */
  --status-success: #16856B;  /* High similarity, verified metadata */
  --status-warning: #C98222;  /* Moderate scores, unverified labels */
  --status-error: #C2414B;    /* Errors, low confidence */
}
```
