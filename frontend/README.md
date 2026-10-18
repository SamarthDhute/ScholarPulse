# ScholarPulse — Frontend Web Application

> **Design Aesthetic:** Light theme, scholarly editorial design system (`#F5F8FC` backdrop, `#FFFFFF` surfaces, `#14233B` navy text, `#246BFD` academic blue accents).  
> **Architecture:** React 19 + TypeScript + Vite + Tailwind CSS + React Router v7 + Recharts + Lucide Icons.  
> **API Contracts:** 100% aligned with [`BACKEND_SPECIFICATION.md`](../docs/BACKEND_SPECIFICATION.md).

---

## 1. Quick Start

### Prerequisites
- Node.js v20+ (tested on Node v24.19.0)
- ScholarPulse Backend running on `http://localhost:8000`

### Setup and Running
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Configure environment (defaults to http://localhost:8000)
cp .env.example .env

# 3. Install dependencies
npm install

# 4. Start local development server
npm run dev
```

The web application will be accessible at: `http://localhost:5173`.

---

## 2. Testing and Production Build

```bash
# Run Vitest test suite
npm run test

# Run TypeScript compilation and Vite production bundle
npm run build
```

---

## 3. Screen & Route Inventory

| Route | View Component | Backend Contract Endpoints |
|---|---|---|
| `/` | `HomePage` | `GET /api/v1/analytics/overview`, `GET /api/v1/papers`, `GET /api/v1/categories` |
| `/search` | `SearchPage` | `GET /api/v1/search`, `GET /api/v1/keywords` (autocomplete), `GET /api/v1/categories`, `POST/DELETE /api/v1/library/papers` |
| `/papers` | `PapersPage` | `GET /api/v1/papers` (faceted filters: `author`, `category`, `keyword`, `year_from`, `year_to`) |
| `/papers/:id` | `PaperDetailPage` | `GET /api/v1/papers/{id}`, `GET /api/v1/papers/{id}/related`, `POST/DELETE /api/v1/library/papers` |
| `/topics` | `TopicsPage` | `GET /api/v1/analysis/clusters` (K-Means & Hierarchical), `GET /api/v1/categories` |
| `/topics/clusters/:clusterId` | `ClusterDetailPage` | `GET /api/v1/analysis/clusters/{cluster_id}/papers` |
| `/analytics` | `AnalyticsPage` | `GET /api/v1/analytics/overview`, `trends`, `categories`, `keywords`, `collaboration-network` |
| `/recommendations/:paperId` | `RecommendationsPage` | `GET /api/v1/papers/{id}/related` |
| `/library` | `LibraryPage` | `GET /api/v1/library/papers`, `DELETE /api/v1/library/papers/{paper_id}` |
| `/evaluation` | `EvaluationPage` | `GET /api/v1/evaluation/retrieval` (Cranfield MAP, MRR, NDCG@K) |
| `/analysis` | `AnalysisPage` | `POST /api/v1/analysis/classify`, `GET /api/v1/analysis/association-rules` (Apriori) |
| `/admin/ingestion` | `AdminPage` | `POST /api/v1/admin/ingest`, `GET /api/v1/admin/ingest/status` |
| `/login` & `/register` | `LoginPage` / `RegisterPage` | Open research mode transparency notices (no fake client-side auth) |

---

## 4. Key Engineering Implementations

- **Safe HTML Snippet Parsing:** `src/utils/sanitizeSnippet.tsx` safely renders highlighted `<mark>` tags from the backend without `dangerouslySetInnerHTML`, preventing script injection and XSS vulnerabilities.
- **Strict Parameter Separation:** Search queries use `year_min` & `year_max`, while the Papers Directory uses `year_from` & `year_to`, strictly conforming to the backend parameter validation schemas.
- **Zero Fabricated Content:** Every paper, abstract, metric, cluster label, and evaluation score is fetched directly from the backend API.
