/**
 * ScholarPulse Centralized HTTP API Client.
 *
 * Implements strict error envelope handling, X-User-ID, X-Request-ID,
 * request parameter serialization, and typed endpoints.
 */

import { API_BASE_URL, DEFAULT_USER_ID } from "../config/env";
import type {
  ApiError,
  ApiErrorEnvelope,
  SearchQueryParams,
  SearchResponse,
  PaperListQueryParams,
  PaperListResponse,
  PaperDetail,
  RelatedPaperItem,
  CategoryItem,
  KeywordItem,
  ClassifyPayload,
  ClassifyResponse,
  ClustersResponse,
  ClusterMembersResponse,
  AssociationRulesResponse,
  OverviewSummary,
  TrendItem,
  CategoryShare,
  KeywordShare,
  CollaborationNetwork,
  EvaluationResponse,
  SavedLibraryResponse,
  SavePaperPayload,
  SavedPaperItem,
  IngestPayload,
  IngestRunResponse,
  IngestionStatusResponse,
} from "../types/api";

export class ScholarPulseApiError extends Error {
  public code: string;
  public details?: Record<string, any> | null;
  public requestId?: string;
  public status: number;

  constructor(status: number, errorData: ApiError) {
    super(errorData.message || `HTTP ${status} Request Failed`);
    this.name = "ScholarPulseApiError";
    this.status = status;
    this.code = errorData.code || "UNKNOWN_ERROR";
    this.details = errorData.details;
    this.requestId = errorData.request_id;
  }
}

/**
 * Builds clean query string omitting null, undefined, or empty string values.
 */
export function buildQueryString(params: Record<string, any>): string {
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.append(key, String(value));
    }
  }
  const str = searchParams.toString();
  return str ? `?${str}` : "";
}

interface RequestOptions {
  method?: "GET" | "POST" | "DELETE" | "PUT";
  body?: any;
  userId?: string;
  signal?: AbortSignal;
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers: Record<string, string> = {
    Accept: "application/json",
  };

  if (options.body) {
    headers["Content-Type"] = "application/json";
  }

  // Include X-User-ID for library actions or when specified
  const effectiveUserId = options.userId || DEFAULT_USER_ID;
  if (effectiveUserId) {
    headers["X-User-ID"] = effectiveUserId;
  }

  try {
    const response = await fetch(url, {
      method: options.method || "GET",
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
      signal: options.signal,
    });

    const requestId = response.headers.get("x-request-id") || undefined;

    if (!response.ok) {
      let errorData: ApiError = {
        code: `HTTP_${response.status}`,
        message: `Request failed with status ${response.status}`,
        request_id: requestId,
      };

      try {
        const json = await response.json();
        if (json && json.error) {
          const envelope = json as ApiErrorEnvelope;
          errorData = {
            ...envelope.error,
            request_id: envelope.error.request_id || requestId,
          };
        } else if (json && json.detail) {
          // Standard FastAPI 422 validation structure
          errorData = {
            code: "VALIDATION_ERROR",
            message: Array.isArray(json.detail)
              ? json.detail.map((d: any) => `${d.loc?.join(".")}: ${d.msg}`).join("; ")
              : String(json.detail),
            request_id: requestId,
          };
        }
      } catch {
        // Response was not JSON
      }

      throw new ScholarPulseApiError(response.status, errorData);
    }

    if (response.status === 204) {
      return {} as T;
    }

    return (await response.json()) as T;
  } catch (err: any) {
    if (err instanceof ScholarPulseApiError) {
      throw err;
    }
    if (err.name === "AbortError") {
      throw err;
    }
    // Network failure or unexpected browser exception
    throw new ScholarPulseApiError(0, {
      code: "NETWORK_ERROR",
      message: err.message || "Failed to communicate with ScholarPulse backend.",
    });
  }
}

// =========================================================================
// Authoritative API Endpoints
// =========================================================================

export const apiClient = {
  // 1. Search
  searchPapers: (params: SearchQueryParams, signal?: AbortSignal): Promise<SearchResponse> => {
    const qs = buildQueryString({
      query: params.query,
      method: params.method,
      page: params.page,
      page_size: params.page_size,
      year_min: params.year_min,
      year_max: params.year_max,
      category: params.category,
    });
    return request<SearchResponse>(`/search${qs}`, { signal });
  },

  // 2. Papers Directory
  listPapers: (params: PaperListQueryParams, signal?: AbortSignal): Promise<PaperListResponse> => {
    const qs = buildQueryString({
      page: params.page,
      page_size: params.page_size,
      year_from: params.year_from,
      year_to: params.year_to,
      author: params.author,
      category: params.category,
      keyword: params.keyword,
    });
    return request<PaperListResponse>(`/papers${qs}`, { signal });
  },

  // 3. Paper Details
  getPaper: (id: string, signal?: AbortSignal): Promise<PaperDetail> => {
    return request<PaperDetail>(`/papers/${encodeURIComponent(id)}`, { signal });
  },

  // 4. Related Papers
  getRelatedPapers: (id: string, topN: number = 5, signal?: AbortSignal): Promise<RelatedPaperItem[]> => {
    const qs = buildQueryString({ top_n: topN });
    return request<RelatedPaperItem[]>(`/papers/${encodeURIComponent(id)}/related${qs}`, { signal });
  },

  // 5. Taxonomy: Categories
  getCategories: (signal?: AbortSignal): Promise<CategoryItem[]> => {
    return request<CategoryItem[]>("/categories", { signal });
  },

  // 6. Taxonomy: Keywords Autocomplete
  getKeywords: (prefix?: string, limit: number = 10, signal?: AbortSignal): Promise<KeywordItem[]> => {
    const qs = buildQueryString({ prefix, limit });
    return request<KeywordItem[]>(`/keywords${qs}`, { signal });
  },

  // 7. Data Science: Text Classification
  classifyText: (payload: ClassifyPayload, signal?: AbortSignal): Promise<ClassifyResponse> => {
    return request<ClassifyResponse>("/analysis/classify", {
      method: "POST",
      body: payload,
      signal,
    });
  },

  // 8. Data Science: Topic Clustering
  getClusters: (
    method: "kmeans" | "hierarchical" = "kmeans",
    nClusters: number = 4,
    signal?: AbortSignal
  ): Promise<ClustersResponse> => {
    const qs = buildQueryString({ method, n_clusters: nClusters });
    return request<ClustersResponse>(`/analysis/clusters${qs}`, { signal });
  },

  // 9. Data Science: Cluster Member Papers
  getClusterPapers: (
    clusterId: number,
    page: number = 1,
    pageSize: number = 20,
    signal?: AbortSignal
  ): Promise<ClusterMembersResponse> => {
    const qs = buildQueryString({ page, page_size: pageSize });
    return request<ClusterMembersResponse>(`/analysis/clusters/${clusterId}/papers${qs}`, { signal });
  },

  // 10. Data Science: Association Rules
  getAssociationRules: (
    params: {
      min_support?: number;
      min_confidence?: number;
      min_lift?: number;
      page?: number;
      page_size?: number;
    } = {},
    signal?: AbortSignal
  ): Promise<AssociationRulesResponse> => {
    const qs = buildQueryString(params);
    return request<AssociationRulesResponse>(`/analysis/association-rules${qs}`, { signal });
  },

  // 11. Analytics: Overview
  getAnalyticsOverview: (yearMin?: number, yearMax?: number, signal?: AbortSignal): Promise<OverviewSummary> => {
    const qs = buildQueryString({ year_min: yearMin, year_max: yearMax });
    return request<OverviewSummary>(`/analytics/overview${qs}`, { signal });
  },

  // 12. Analytics: Trends
  getAnalyticsTrends: (yearMin?: number, yearMax?: number, signal?: AbortSignal): Promise<TrendItem[]> => {
    const qs = buildQueryString({ year_min: yearMin, year_max: yearMax });
    return request<TrendItem[]>(`/analytics/trends${qs}`, { signal });
  },

  // 13. Analytics: Categories Share
  getAnalyticsCategories: (yearMin?: number, yearMax?: number, signal?: AbortSignal): Promise<CategoryShare[]> => {
    const qs = buildQueryString({ year_min: yearMin, year_max: yearMax });
    return request<CategoryShare[]>(`/analytics/categories${qs}`, { signal });
  },

  // 14. Analytics: Keywords Share
  getAnalyticsKeywords: (
    yearMin?: number,
    yearMax?: number,
    topN: number = 20,
    signal?: AbortSignal
  ): Promise<KeywordShare[]> => {
    const qs = buildQueryString({ year_min: yearMin, year_max: yearMax, top_n: topN });
    return request<KeywordShare[]>(`/analytics/keywords${qs}`, { signal });
  },

  // 15. Analytics: Collaboration Network
  getCollaborationNetwork: (
    minCollaborations: number = 1,
    topN: number = 20,
    signal?: AbortSignal
  ): Promise<CollaborationNetwork> => {
    const qs = buildQueryString({ min_collaborations: minCollaborations, top_n: topN });
    return request<CollaborationNetwork>(`/analytics/collaboration-network${qs}`, { signal });
  },

  // 16. Evaluation: Retrieval Benchmark Reports
  getRetrievalEvaluation: (signal?: AbortSignal): Promise<EvaluationResponse> => {
    return request<EvaluationResponse>("/evaluation/retrieval", { signal });
  },

  // 17. Saved Library: Get User Papers
  getSavedPapers: (userId?: string, signal?: AbortSignal): Promise<SavedLibraryResponse> => {
    return request<SavedLibraryResponse>("/library/papers", { userId, signal });
  },

  // 18. Saved Library: Bookmark Paper
  savePaper: (payload: SavePaperPayload, userId?: string, signal?: AbortSignal): Promise<SavedPaperItem> => {
    return request<SavedPaperItem>("/library/papers", {
      method: "POST",
      body: payload,
      userId,
      signal,
    });
  },

  // 19. Saved Library: Remove Bookmark
  removeSavedPaper: (
    paperId: string,
    userId?: string,
    signal?: AbortSignal
  ): Promise<{ status: string; message: string }> => {
    return request<{ status: string; message: string }>(`/library/papers/${encodeURIComponent(paperId)}`, {
      method: "DELETE",
      userId,
      signal,
    });
  },

  // 20. Admin: Trigger Ingestion
  triggerIngest: (payload: IngestPayload, signal?: AbortSignal): Promise<IngestRunResponse> => {
    return request<IngestRunResponse>("/admin/ingest", {
      method: "POST",
      body: payload,
      signal,
    });
  },

  // 21. Admin: Ingestion Status History
  getIngestStatus: (limit: number = 10, signal?: AbortSignal): Promise<IngestionStatusResponse> => {
    const qs = buildQueryString({ limit });
    return request<IngestionStatusResponse>(`/admin/ingest/status${qs}`, { signal });
  },
};
