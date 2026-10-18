# ScholarPulse Brand Kit
**Version:** 1.0  
**Purpose:** Shared visual and interaction system for all ScholarPulse frontend screens.  
**Product character:** Scholarly, editorial, precise, data-focused, accessible, and calm.  
**Theme:** Light only for the current prototype.

## 1. Brand principles

- Research-first: make query, paper metadata, filters, and evidence more prominent than decoration.
- Calm density: support data-heavy workflows without clutter or oversized hero-only layouts.
- Trustworthy: show provenance, publication year, DOI/source where available, and distinguish sample data from live data.
- Consistent: reuse tokens and components across Home, Search, Paper Details, Directory, Topic Exploration, Analytics, Recommendations, Library, Evaluation, Admin, Login, and Register.
- Accessible: keyboard support, visible focus, adequate contrast, semantic controls, reduced motion, and labels that do not depend on color alone.

## 2. Color tokens

These are the primary ScholarPulse tokens from the backend specification's design directives.

| Token | CSS custom property | Value | Usage |
|---|---|---|---|
| Page background | `--bg-page` | `#F5F8FC` | Main app canvas |
| Surface | `--bg-surface` | `#FFFFFF` | Cards, panels, inputs |
| Primary text | `--text-primary` | `#14233B` | Headings and core content |
| Secondary text | `--text-secondary` | `#5F6F85` | Metadata, helper text |
| Border | `--border-color` | `#DCE5EF` | Dividers, card/input outlines |
| Primary blue | `--primary-blue` | `#246BFD` | Primary actions, links, selected states |
| Pale blue | `--pale-blue` | `#EAF2FF` | Tags, badges, highlighted query terms |
| Success | `--status-success` | `#16856B` | Verified/success states |
| Warning | `--status-warning` | `#C98222` | Moderate scores, unverified labels |
| Error | `--status-error` | `#C2414B` | Errors, low-confidence status |

### Suggested derived tokens
These are implementation recommendations, not additional values explicitly stated in the backend contract.

| Token | Value | Usage |
|---|---|---|
| `--surface-muted` | `#F8FAFD` | Subtle inset panels |
| `--blue-hover` | `#1D5CE0` | Primary button hover |
| `--blue-active` | `#174BB8` | Pressed primary button |
| `--focus-ring` | `rgba(36, 107, 253, 0.28)` | Keyboard focus halo |
| `--overlay` | `rgba(20, 35, 59, 0.42)` | Modal backdrop |
| `--status-success-bg` | `#E8F6F1` | Success badge background |
| `--status-warning-bg` | `#FFF4E3` | Warning badge background |
| `--status-error-bg` | `#FDECEE` | Error badge background |

Use semantic tokens rather than hard-coded colors in components. Keep contrast accessible and never communicate status through color alone.

## 3. Typography

Suggested default font stack:
```css
font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
  "Segoe UI", sans-serif;
```

| Token | Value | Usage |
|---|---|---|
| `--font-size-xs` | `0.75rem` / 12px | Dense metadata, chart ticks (avoid for essential text) |
| `--font-size-sm` | `0.875rem` / 14px | Metadata, labels, controls |
| `--font-size-md` | `1rem` / 16px | Body text and inputs |
| `--font-size-lg` | `1.125rem` / 18px | Card titles, section labels |
| `--font-size-xl` | `1.5rem` / 24px | Page section headings |
| `--font-size-2xl` | `2rem` / 32px | Main page headings |
| `--font-size-display` | `clamp(2.25rem, 4vw, 3.5rem)` | Home hero heading only |
| `--line-height-tight` | `1.2` | Large headings |
| `--line-height-normal` | `1.5` | Body copy |
| `--line-height-relaxed` | `1.65` | Long abstracts and explanatory text |
| `--font-weight-normal` | `400` | Body text |
| `--font-weight-medium` | `500` | Labels and navigation |
| `--font-weight-semibold` | `600` | Cards and section headings |
| `--font-weight-bold` | `700` | Page headings |

Avoid ultra-light text and all-caps UI labels except small, intentional eyebrow labels.

## 4. Spacing, sizing, and layout

Use a 4px base spacing unit.

| Token | Value |
|---|---:|
| `--space-1` | 4px |
| `--space-2` | 8px |
| `--space-3` | 12px |
| `--space-4` | 16px |
| `--space-5` | 20px |
| `--space-6` | 24px |
| `--space-8` | 32px |
| `--space-10` | 40px |
| `--space-12` | 48px |
| `--space-16` | 64px |
| `--content-max-width` | 1440px |
| `--sidebar-width` | 248px |
| `--topbar-height` | 64px |
| `--control-height` | 40px |
| `--control-height-compact` | 32px |

Layout rules:
- Desktop: persistent top navigation; optional left filter/sidebar where it helps the task.
- Tablet: compress navigation and filters; allow filter panels to collapse.
- Mobile: single-column content, filter drawer, full-width search input, horizontally scrollable chips only when necessary.
- Search results should prioritize readable title, authors, year/source, snippet, rank/score, tags, and actions.
- Analytics should reflow charts into a single column on small screens.
- Keep page content aligned to a consistent max-width; avoid unnecessarily wide line lengths for abstracts.

## 5. Borders, radii, and elevation

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | `6px` | Small tags and compact controls |
| `--radius-md` | `10px` | Inputs, buttons, standard cards |
| `--radius-lg` | `14px` | Main panels |
| `--radius-xl` | `20px` | Rare hero containers |
| `--border-width` | `1px` | Standard outline |
| `--shadow-sm` | `0 1px 2px rgba(20, 35, 59, 0.04)` | Default cards |
| `--shadow-md` | `0 6px 18px rgba(20, 35, 59, 0.07)` | Menus and elevated panels |
| `--shadow-focus` | `0 0 0 3px rgba(36, 107, 253, 0.20)` | Focus outline support |

Use borders for structure; shadows should be subtle. Avoid heavy glassmorphism, neon glow, excessive gradients, and giant rounded-card layouts.

## 6. Components and interaction states

### Buttons
- Primary: blue background, white text; one primary action per main panel where practical.
- Secondary: white surface, border, primary/navy text.
- Tertiary/quiet: transparent surface with text/icon.
- Destructive: error semantic token and explicit confirmation for destructive bulk actions.
- All interactive controls require hover, active, disabled, and visible keyboard-focus states.

### Inputs and search
- Standard control height: 40px.
- Search accepts Enter to submit and shows a clear button when a query exists.
- Autocomplete uses `GET /api/v1/keywords?prefix=...&limit=...`.
- Search method options must exactly match the API contract:
  - `bm25` — BM25 (Default)
  - `tfidf` — TF-IDF (Cosine)
  - `language_model` — Language Model (Dirichlet)
  - `boolean` — Boolean Search
- Search request parameters must use `query`, `method`, `page`, `page_size`, `year_min`, `year_max`, and `category` as specified. Do not send `q` or `ranker`.

### Chips, badges, and score labels
- Pale blue for topical tags and query highlights.
- Success/warning/error colors for semantic status only.
- Similarity/relevance scores must be labelled with their actual metric and method; do not imply a score is a probability unless the API defines it that way.
- Highlighted snippets from the API must be sanitized before HTML rendering; never inject untrusted HTML without sanitization.

### Cards and data tables
- Paper cards display only available metadata; gracefully omit missing optional fields.
- Avoid invented citation counts, paper counts, or relevance scores.
- Tables need clear headers, alignment, pagination status, and mobile fallback.
- Charts require titles, axes/units where relevant, legends, tooltips, and empty/loading/error states.

### Feedback states
- Loading: skeletons or restrained spinner; prevent duplicate submission.
- Empty: explain no results and suggest a relevant action.
- Error: concise user-facing message, request ID when useful, retry where safe.
- Success: concise confirmation for save/remove/ingestion actions.
- Never show stack traces, secrets, or raw provider exceptions.

## 7. Screen-to-contract alignment

| Screen | Contract endpoints | Important behavior |
|---|---|---|
| Home / Discover | `/api/v1/search`, `/api/v1/papers`, `/api/v1/categories`, `/api/v1/keywords`, `/api/v1/analytics/overview`, `/api/v1/analytics/trends` | Search and featured content must come from API; mark demo content clearly |
| Search Results | `/api/v1/search`, `/api/v1/keywords` | `query` + `method`; page/page_size; year_min/year_max; category; no-results state |
| Paper Details | `/api/v1/papers/{id}`, `/api/v1/papers/{id}/related` | Details require canonical UUID; search result `doc_id` may be DOI-like, so resolve/map to UUID before navigation |
| Papers Directory | `/api/v1/papers`, `/api/v1/categories`, `/api/v1/keywords` | Directory uses year_from/year_to, unlike search's year_min/year_max |
| Topic Exploration | `/api/v1/categories`, `/api/v1/analysis/clusters`, `/api/v1/analysis/association-rules` | Method `kmeans` or `hierarchical`; cluster count 2–10; association thresholds validated |
| Cluster Details | `/api/v1/analysis/clusters/{cluster_id}/papers` | `cluster_id` is integer; paginated paper list |
| Research Analytics | `/api/v1/analytics/overview`, `/trends`, `/categories`, `/keywords`, `/collaboration-network` | Charts and KPI cards use actual response values |
| Recommendations | `/api/v1/papers/{id}/related` | Excludes seed paper; top_n 1–50 |
| My Library | `/api/v1/library/papers` GET/POST and `/api/v1/library/papers/{paper_id}` DELETE | Optional `X-User-ID`; duplicate save can return 409; collections/history are not in current contract |
| Retrieval Evaluation | `/api/v1/evaluation/retrieval` | Only retrieval benchmarking is specified |
| Data Science Analysis | `/api/v1/analysis/classify`, `/api/v1/analysis/clusters`, `/api/v1/analysis/association-rules` | Use exact request and response types |
| Admin / Ingestion | `/api/v1/admin/ingest`, `/api/v1/admin/ingest/status` | Show run status/counts/errors; secure admin access must be defined server-side |
| Login / Register | No authentication endpoints in current contract | Treat as design-only until an auth contract is added; do not fake successful login |

### Contract gaps to preserve visibly
The current specification does not define endpoints for full-text PDF retrieval, citation export, named library collections, search history, password-based login/register, password reset, or classification/clustering evaluation reports. Keep those controls hidden, disabled with an explanation, or explicitly labelled as not yet available until a backend contract exists.

## 8. CSS token starter

```css
:root {
  color-scheme: light;

  --bg-page: #F5F8FC;
  --bg-surface: #FFFFFF;
  --surface-muted: #F8FAFD;

  --text-primary: #14233B;
  --text-secondary: #5F6F85;
  --border-color: #DCE5EF;

  --primary-blue: #246BFD;
  --blue-hover: #1D5CE0;
  --blue-active: #174BB8;
  --pale-blue: #EAF2FF;
  --focus-ring: rgba(36, 107, 253, 0.28);

  --status-success: #16856B;
  --status-warning: #C98222;
  --status-error: #C2414B;
  --status-success-bg: #E8F6F1;
  --status-warning-bg: #FFF4E3;
  --status-error-bg: #FDECEE;

  --font-family: Inter, ui-sans-serif, system-ui, -apple-system,
    BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-md: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.5rem;
  --font-size-2xl: 2rem;
  --line-height-tight: 1.2;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.65;

  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;

  --control-height: 40px;
  --control-height-compact: 32px;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-xl: 20px;
  --border-width: 1px;
  --shadow-sm: 0 1px 2px rgba(20, 35, 59, 0.04);
  --shadow-md: 0 6px 18px rgba(20, 35, 59, 0.07);
  --shadow-focus: 0 0 0 3px rgba(36, 107, 253, 0.20);

  --content-max-width: 1440px;
  --sidebar-width: 248px;
  --topbar-height: 64px;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: var(--font-family);
  background: var(--bg-page);
  color: var(--text-primary);
  line-height: var(--line-height-normal);
}

:focus-visible {
  outline: 2px solid var(--primary-blue);
  outline-offset: 2px;
  box-shadow: var(--shadow-focus);
}

::selection {
  background: var(--pale-blue);
  color: var(--text-primary);
}
```

## 9. Iconography and imagery

- Use one consistent outline icon set (e.g. Lucide) and consistent stroke weight.
- Use the ScholarPulse mark with a simple scholarly/book/chart motif; do not use random unrelated logos.
- Avoid decorative stock imagery as a substitute for research data.
- Use paper/topic thumbnails only when they improve scanning; data tables and charts should remain the primary visual language.

## 10. Motion

- Use short, purposeful transitions (approximately 120–180ms) for hover/focus and small panel changes.
- Avoid animated chart movement that impairs reading.
- Respect `prefers-reduced-motion: reduce`.
- Do not make essential content depend on animation.

## 11. Acceptance checklist

- [ ] All colors and sizes come from tokens, not arbitrary one-off values.
- [ ] All screens use the same navigation, typography, controls, and spacing scale.
- [ ] Search request names and method enum match the backend contract exactly.
- [ ] Paper detail navigation uses a canonical UUID, not an ambiguous DOI-like `doc_id`.
- [ ] Search and directory year-filter names remain distinct.
- [ ] No fabricated metrics or fake successful API actions.
- [ ] Unspecified PDF, citation, collections, history, auth, and extra evaluation actions are not represented as working backend features.
- [ ] Every data view has loading, empty, error, and success states.
- [ ] Keyboard focus and reduced-motion behavior are present.
- [ ] Responsive behavior is verified at desktop, tablet, and mobile widths.
- [ ] No secrets or `.env` files are included in the brand kit.
