/**
 * ScholarPulse API Types — Contract Aligned with BACKEND_SPECIFICATION.md
 */

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

export interface SearchQueryParams {
  query: string;
  method?: IRMethod;
  page?: number;
  page_size?: number;
  year_min?: number;
  year_max?: number;
  category?: string;
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

export interface PaperListQueryParams {
  page?: number;
  page_size?: number;
  year_from?: number;
  year_to?: number;
  author?: string;
  category?: string;
  keyword?: string;
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

export interface ClassifyPayload {
  text?: string;
  paper_id?: string;
  top_k?: number;
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

export interface ClusterMemberItem {
  paper_id: string;
  title: string;
  category?: string;
  publication_year?: number;
}

export interface ClusterMembersResponse {
  cluster_id: number;
  label: string;
  total: number;
  page: number;
  page_size: number;
  papers: ClusterMemberItem[];
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

export interface SavePaperPayload {
  paper_id: string;
  notes?: string;
}

// ==========================================
// Admin Ingestion Types
// ==========================================

export interface IngestPayload {
  filepath: string;
  source_name: string;
}

export interface IngestRunResponse {
  run_id: string;
  status: "completed" | "failed" | "in_progress";
  total_processed: number;
  created_count: number;
  updated_count: number;
  skipped_count: number;
  error_count: number;
}

export interface IngestRunHistoryItem {
  run_id: string;
  source_name: string;
  status: string;
  total_records: number;
  created_count: number;
  updated_count: number;
  skipped_count: number;
  error_count: number;
  started_at: string;
  finished_at?: string;
}

export interface IngestionStatusResponse {
  total_runs: number;
  runs: IngestRunHistoryItem[];
}
