import React, { useEffect, useState, useRef } from "react";
import { useSearchParams, Link } from "react-router-dom";
import {
  Search,
  SlidersHorizontal,
  Bookmark,
  Check,
  RotateCcw,
  ChevronRight,
  TrendingUp,
} from "lucide-react";
import { apiClient } from "../services/apiClient";
import type { SearchResponse, SearchResultItem, IRMethod, CategoryItem, KeywordItem } from "../types/api";
import { renderSafeSnippet } from "../utils/sanitizeSnippet";
import { PaperCardSkeleton } from "../components/common/LoadingSkeleton";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorPanel } from "../components/common/ErrorPanel";
import { Badge } from "../components/common/Badge";

export const SearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  // Read URL query params
  const initialQuery = searchParams.get("query") || "";
  const initialMethod = (searchParams.get("method") as IRMethod) || "bm25";
  const initialPage = parseInt(searchParams.get("page") || "1", 10);
  const initialYearMin = searchParams.get("year_min") ? parseInt(searchParams.get("year_min")!, 10) : undefined;
  const initialYearMax = searchParams.get("year_max") ? parseInt(searchParams.get("year_max")!, 10) : undefined;
  const initialCategory = searchParams.get("category") || undefined;

  // Local state
  const [queryInput, setQueryInput] = useState(initialQuery);
  const [activeMethod, setActiveMethod] = useState<IRMethod>(initialMethod);
  const [currentPage, setCurrentPage] = useState<number>(initialPage);
  const [yearMin, setYearMin] = useState<number | undefined>(initialYearMin);
  const [yearMax, setYearMax] = useState<number | undefined>(initialYearMax);
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>(initialCategory);

  // Autocomplete state
  const [keywordSuggestions, setKeywordSuggestions] = useState<KeywordItem[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Search API response state
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);
  const [categories, setCategories] = useState<CategoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Saved bookmark tracking
  const [savedPaperIds, setSavedPaperIds] = useState<Set<string>>(new Set());
  const [savingId, setSavingId] = useState<string | null>(null);

  // Available IR Methods
  const IR_METHODS: { id: IRMethod; label: string; desc: string }[] = [
    { id: "bm25", label: "BM25 (Default)", desc: "Probabilistic ranker with length normalization" },
    { id: "tfidf", label: "TF-IDF", desc: "Vector Space Model with Cosine Similarity" },
    { id: "language_model", label: "Language Model", desc: "Query Likelihood with Dirichlet smoothing" },
    { id: "boolean", label: "Boolean", desc: "Exact Boolean logic (AND, OR, NOT)" },
  ];

  // Fetch categories on mount
  useEffect(() => {
    apiClient.getCategories().then(setCategories).catch(() => {});
    // Also fetch currently saved papers to display bookmark state
    apiClient.getSavedPapers().then((res) => {
      setSavedPaperIds(new Set(res.items.map((i) => i.paper_id)));
    }).catch(() => {});
  }, []);

  // Sync state with URL params
  useEffect(() => {
    const q = searchParams.get("query") || "";
    const m = (searchParams.get("method") as IRMethod) || "bm25";
    const p = parseInt(searchParams.get("page") || "1", 10);
    const yMin = searchParams.get("year_min") ? parseInt(searchParams.get("year_min")!, 10) : undefined;
    const yMax = searchParams.get("year_max") ? parseInt(searchParams.get("year_max")!, 10) : undefined;
    const cat = searchParams.get("category") || undefined;

    setQueryInput(q);
    setActiveMethod(m);
    setCurrentPage(p);
    setYearMin(yMin);
    setYearMax(yMax);
    setSelectedCategory(cat);

    if (q.trim()) {
      executeSearch(q, m, p, yMin, yMax, cat);
    } else {
      setSearchResponse(null);
    }
  }, [searchParams]);

  // Autocomplete fetch on query typing
  useEffect(() => {
    if (queryInput.trim().length >= 2) {
      const controller = new AbortController();
      apiClient
        .getKeywords(queryInput.trim(), 6, controller.signal)
        .then((items) => {
          setKeywordSuggestions(items);
        })
        .catch(() => {});
      return () => controller.abort();
    } else {
      setKeywordSuggestions([]);
    }
  }, [queryInput]);

  const executeSearch = async (
    q: string,
    method: IRMethod,
    page: number,
    yMin?: number,
    yMax?: number,
    cat?: string
  ) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.searchPapers({
        query: q,
        method,
        page,
        page_size: 20,
        year_min: yMin,
        year_max: yMax,
        category: cat,
      });
      setSearchResponse(response);
    } catch (err: any) {
      setError(err);
      setSearchResponse(null);
    } finally {
      setLoading(false);
    }
  };

  const updateSearchUrl = (updates: Partial<{
    query: string;
    method: IRMethod;
    page: number;
    year_min?: number;
    year_max?: number;
    category?: string;
  }>) => {
    const nextParams = new URLSearchParams(searchParams);

    const q = updates.query !== undefined ? updates.query : queryInput;
    const m = updates.method !== undefined ? updates.method : activeMethod;
    const p = updates.page !== undefined ? updates.page : 1;
    const yMin = updates.year_min !== undefined ? updates.year_min : yearMin;
    const yMax = updates.year_max !== undefined ? updates.year_max : yearMax;
    const cat = updates.category !== undefined ? updates.category : selectedCategory;

    if (q) nextParams.set("query", q);
    else nextParams.delete("query");

    if (m) nextParams.set("method", m);
    if (p > 1) nextParams.set("page", String(p));
    else nextParams.delete("page");

    if (yMin) nextParams.set("year_min", String(yMin));
    else nextParams.delete("year_min");

    if (yMax) nextParams.set("year_max", String(yMax));
    else nextParams.delete("year_max");

    if (cat) nextParams.set("category", cat);
    else nextParams.delete("category");

    setSearchParams(nextParams);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowSuggestions(false);
    if (queryInput.trim()) {
      updateSearchUrl({ query: queryInput.trim(), page: 1 });
    }
  };

  const handleResetFilters = () => {
    setYearMin(undefined);
    setYearMax(undefined);
    setSelectedCategory(undefined);
    setActiveMethod("bm25");
    updateSearchUrl({
      method: "bm25",
      year_min: undefined,
      year_max: undefined,
      category: undefined,
      page: 1,
    });
  };

  const handleBookmarkToggle = async (paperId: string) => {
    if (savedPaperIds.has(paperId)) {
      // Remove
      setSavingId(paperId);
      try {
        await apiClient.removeSavedPaper(paperId);
        setSavedPaperIds((prev) => {
          const next = new Set(prev);
          next.delete(paperId);
          return next;
        });
      } catch (err) {
        console.error("Failed to remove bookmark", err);
      } finally {
        setSavingId(null);
      }
    } else {
      // Save
      setSavingId(paperId);
      try {
        await apiClient.savePaper({ paper_id: paperId, notes: `Bookmarked from search for "${queryInput}"` });
        setSavedPaperIds((prev) => new Set(prev).add(paperId));
      } catch (err) {
        console.error("Failed to save paper", err);
      } finally {
        setSavingId(null);
      }
    }
  };

  const totalPages = searchResponse
    ? Math.ceil(searchResponse.total_hits / searchResponse.page_size)
    : 1;

  return (
    <div className="space-y-6">
      {/* Search Bar & Method Switcher Header */}
      <div className="bg-surface rounded-md border border-border p-4 shadow-sm space-y-3">
        <form onSubmit={handleSearchSubmit} className="relative">
          <div className="flex items-center rounded-md border border-border focus-within:ring-2 focus-within:ring-blue-primary/30 bg-surface overflow-hidden">
            <div className="pl-3.5 text-secondary-text">
              <Search className="w-5 h-5" />
            </div>
            <input
              ref={searchInputRef}
              type="text"
              value={queryInput}
              onChange={(e) => {
                setQueryInput(e.target.value);
                setShowSuggestions(true);
              }}
              onFocus={() => setShowSuggestions(true)}
              placeholder="Search research papers by topic, title, or Boolean query (e.g. 'transformer AND attention')..."
              className="w-full py-2.5 px-3 text-sm text-primary-text bg-transparent focus:outline-none"
            />
            <button
              type="submit"
              className="px-5 py-2.5 bg-blue-primary hover:bg-blue-hover text-white text-sm font-semibold transition-colors shrink-0"
            >
              Search
            </button>
          </div>

          {/* Keyword Autocomplete Popup */}
          {showSuggestions && keywordSuggestions.length > 0 && (
            <div className="absolute left-0 right-0 top-full mt-1 bg-surface border border-border rounded-md shadow-lg z-50 overflow-hidden divide-y divide-border">
              {keywordSuggestions.map((kw) => (
                <button
                  key={kw.id}
                  type="button"
                  onClick={() => {
                    setQueryInput(kw.display_term);
                    setShowSuggestions(false);
                    updateSearchUrl({ query: kw.display_term, page: 1 });
                  }}
                  className="w-full text-left px-4 py-2 text-xs text-primary-text hover:bg-blue-pale flex items-center justify-between"
                >
                  <span className="font-medium">{kw.display_term}</span>
                  <span className="text-[11px] text-secondary-text font-mono">
                    {kw.paper_count} papers
                  </span>
                </button>
              ))}
            </div>
          )}
        </form>

        {/* Algorithm Pills */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-border">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-xs font-semibold text-secondary-text mr-1">IR Ranker:</span>
            {IR_METHODS.map((m) => (
              <button
                key={m.id}
                type="button"
                onClick={() => {
                  setActiveMethod(m.id);
                  updateSearchUrl({ method: m.id, page: 1 });
                }}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors border ${
                  activeMethod === m.id
                    ? "bg-blue-primary text-white border-blue-primary shadow-sm"
                    : "bg-surface-muted text-secondary-text border-border hover:bg-blue-pale hover:text-blue-primary"
                }`}
                title={m.desc}
              >
                {m.label}
              </button>
            ))}
          </div>

          {searchResponse && (
            <div className="text-xs text-secondary-text font-mono">
              Hits: <strong className="text-primary-text">{searchResponse.total_hits}</strong> papers
            </div>
          )}
        </div>
      </div>

      {error && <ErrorPanel error={error} onRetry={() => executeSearch(queryInput, activeMethod, currentPage, yearMin, yearMax, selectedCategory)} />}

      {/* 3-Column Search Layout (Reference B Aligned) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Facet Filters (3 cols) */}
        <aside className="lg:col-span-3 space-y-5 bg-surface rounded-md border border-border p-4 shadow-sm">
          <div className="flex items-center justify-between border-b border-border pb-2.5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-primary-text flex items-center gap-1.5">
              <SlidersHorizontal className="w-3.5 h-3.5 text-blue-primary" />
              Search Filters
            </h3>
            {(yearMin || yearMax || selectedCategory || activeMethod !== "bm25") && (
              <button
                type="button"
                onClick={handleResetFilters}
                className="text-xs text-secondary-text hover:text-status-error flex items-center gap-1 transition-colors"
              >
                <RotateCcw className="w-3 h-3" /> Reset
              </button>
            )}
          </div>

          {/* Year Range Filter */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-primary-text block">
              Publication Year
            </label>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-[10px] text-secondary-text">From</span>
                <input
                  type="number"
                  placeholder="Min"
                  value={yearMin || ""}
                  onChange={(e) => {
                    const val = e.target.value ? parseInt(e.target.value, 10) : undefined;
                    setYearMin(val);
                    updateSearchUrl({ year_min: val, page: 1 });
                  }}
                  className="w-full text-xs p-2 rounded border border-border bg-surface-muted text-primary-text focus:outline-none focus:ring-1 focus:ring-blue-primary"
                />
              </div>
              <div>
                <span className="text-[10px] text-secondary-text">To</span>
                <input
                  type="number"
                  placeholder="Max"
                  value={yearMax || ""}
                  onChange={(e) => {
                    const val = e.target.value ? parseInt(e.target.value, 10) : undefined;
                    setYearMax(val);
                    updateSearchUrl({ year_max: val, page: 1 });
                  }}
                  className="w-full text-xs p-2 rounded border border-border bg-surface-muted text-primary-text focus:outline-none focus:ring-1 focus:ring-blue-primary"
                />
              </div>
            </div>
          </div>

          {/* Category Filter */}
          <div className="space-y-2 pt-2 border-t border-border">
            <label className="text-xs font-semibold text-primary-text block">
              Categories
            </label>
            <div className="space-y-1 max-h-56 overflow-y-auto pr-1">
              <button
                type="button"
                onClick={() => {
                  setSelectedCategory(undefined);
                  updateSearchUrl({ category: undefined, page: 1 });
                }}
                className={`w-full text-left px-2 py-1.5 rounded text-xs transition-colors flex items-center justify-between ${
                  !selectedCategory
                    ? "bg-blue-pale text-blue-primary font-semibold"
                    : "text-secondary-text hover:bg-surface-muted"
                }`}
              >
                <span>All Categories</span>
              </button>

              {categories.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => {
                    const next = selectedCategory === c.name ? undefined : c.name;
                    setSelectedCategory(next);
                    updateSearchUrl({ category: next, page: 1 });
                  }}
                  className={`w-full text-left px-2 py-1.5 rounded text-xs transition-colors flex items-center justify-between ${
                    selectedCategory === c.name
                      ? "bg-blue-pale text-blue-primary font-semibold"
                      : "text-secondary-text hover:bg-surface-muted"
                  }`}
                >
                  <span className="truncate">{c.name}</span>
                  <span className="text-[10px] font-mono opacity-80">{c.paper_count}</span>
                </button>
              ))}
            </div>
          </div>
        </aside>

        {/* Middle Column: Ranked Search Results List (6 cols) */}
        <section className="lg:col-span-6 space-y-4">
          {loading ? (
            Array.from({ length: 4 }).map((_, i) => <PaperCardSkeleton key={i} />)
          ) : searchResponse && searchResponse.results.length > 0 ? (
            <div className="space-y-3">
              {searchResponse.results.map((item: SearchResultItem) => {
                const isSaved = savedPaperIds.has(item.doc_id);
                const isSaving = savingId === item.doc_id;

                return (
                  <article
                    key={item.doc_id}
                    className="bg-surface rounded-md border border-border p-5 hover:border-blue-primary/40 transition-all shadow-sm space-y-3"
                  >
                    {/* Header: Rank, Title, Score Badge */}
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start gap-2.5">
                        <span className="w-6 h-6 rounded-full bg-blue-pale text-blue-primary text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                          #{item.rank}
                        </span>
                        <div>
                          <Link
                            to={`/papers/${encodeURIComponent(item.doc_id)}`}
                            className="font-bold text-base text-primary-text hover:text-blue-primary transition-colors leading-snug"
                          >
                            {item.metadata.title}
                          </Link>

                          {/* Authors & Publication Year Metadata */}
                          <div className="text-xs text-secondary-text mt-1 flex flex-wrap items-center gap-1.5">
                            {item.metadata.authors && item.metadata.authors.length > 0 && (
                              <span>
                                {item.metadata.authors.map((a) => a.name).join(", ")}
                              </span>
                            )}
                            {item.metadata.publication_year && (
                              <>
                                <span>•</span>
                                <span className="font-mono">{item.metadata.publication_year}</span>
                              </>
                            )}
                            {item.metadata.source_name && (
                              <>
                                <span>•</span>
                                <span className="italic">{item.metadata.source_name}</span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Score Badge */}
                      <div className="text-right shrink-0">
                        <Badge variant="blue" className="font-mono">
                          Score: {item.score.toFixed(3)}
                        </Badge>
                      </div>
                    </div>

                    {/* Highlighted Passage Snippet with safe <mark> tags */}
                    <div className="text-xs text-secondary-text leading-relaxed bg-surface-muted/60 p-3 rounded border border-border">
                      {item.highlighted_snippet ? (
                        renderSafeSnippet(item.highlighted_snippet)
                      ) : (
                        item.snippet || item.metadata.abstract
                      )}
                    </div>

                    {/* Explainable Term Scores Breakdown */}
                    {item.term_scores && Object.keys(item.term_scores).length > 0 && (
                      <div className="flex items-center gap-1.5 flex-wrap text-[11px] text-secondary-text pt-1">
                        <span className="font-medium text-primary-text">Term weights:</span>
                        {Object.entries(item.term_scores).map(([term, weight]) => (
                          <span
                            key={term}
                            className="bg-surface px-1.5 py-0.5 rounded border border-border font-mono text-[10px]"
                          >
                            {term}: {weight.toFixed(2)}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Bottom Action Footer */}
                    <div className="flex items-center justify-between pt-2 border-t border-border text-xs">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        {item.metadata.categories?.map((cat) => (
                          <Badge key={cat} variant="blue">
                            {cat}
                          </Badge>
                        ))}
                        {item.metadata.doi && (
                          <span className="text-[10px] text-secondary-text font-mono truncate max-w-[140px]">
                            DOI: {item.metadata.doi}
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => handleBookmarkToggle(item.doc_id)}
                          disabled={isSaving}
                          className={`inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium border transition-colors ${
                            isSaved
                              ? "bg-status-success-bg text-status-success border-status-success/30"
                              : "bg-surface hover:bg-surface-muted text-secondary-text border-border"
                          }`}
                        >
                          {isSaved ? <Check className="w-3.5 h-3.5" /> : <Bookmark className="w-3.5 h-3.5" />}
                          <span>{isSaved ? "Saved" : "Save"}</span>
                        </button>

                        <Link
                          to={`/papers/${encodeURIComponent(item.doc_id)}`}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-semibold bg-blue-pale text-blue-primary hover:bg-blue-primary hover:text-white transition-colors"
                        >
                          Details <ChevronRight className="w-3.5 h-3.5" />
                        </Link>
                      </div>
                    </div>
                  </article>
                );
              })}

              {/* Pagination Bar */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between bg-surface p-3 rounded-md border border-border text-xs">
                  <button
                    type="button"
                    disabled={currentPage <= 1}
                    onClick={() => updateSearchUrl({ page: currentPage - 1 })}
                    className="px-3 py-1.5 rounded border border-border bg-surface hover:bg-surface-muted disabled:opacity-40 disabled:cursor-not-allowed font-medium"
                  >
                    Previous
                  </button>
                  <span className="text-secondary-text">
                    Page <strong className="text-primary-text">{currentPage}</strong> of{" "}
                    <strong>{totalPages}</strong>
                  </span>
                  <button
                    type="button"
                    disabled={currentPage >= totalPages}
                    onClick={() => updateSearchUrl({ page: currentPage + 1 })}
                    className="px-3 py-1.5 rounded border border-border bg-surface hover:bg-surface-muted disabled:opacity-40 disabled:cursor-not-allowed font-medium"
                  >
                    Next
                  </button>
                </div>
              )}
            </div>
          ) : queryInput.trim() ? (
            <EmptyState
              title={`No papers matching "${queryInput}"`}
              description="No documents matched your criteria. Try broader keywords, check spelling, or change ranking algorithm."
              onAction={handleResetFilters}
              actionLabel="Reset Filters"
            />
          ) : (
            <div className="bg-surface rounded-md border border-border p-10 text-center text-secondary-text text-sm">
              Enter a search query above to explore research papers.
            </div>
          )}
        </section>

        {/* Right Column: "Results Insights" (Reference B Aligned, 3 cols) */}
        <aside className="lg:col-span-3 space-y-4">
          <div className="bg-surface rounded-md border border-border p-4 shadow-sm space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-primary-text flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5 text-blue-primary" />
              Search Context Insights
            </h4>
            <p className="text-xs text-secondary-text">
              Active retrieval model: <strong className="text-primary-text uppercase">{activeMethod}</strong>
            </p>

            <div className="p-3 bg-surface-muted rounded text-xs space-y-2 border border-border">
              <div className="flex justify-between">
                <span className="text-secondary-text">Scored Documents:</span>
                <span className="font-semibold">{searchResponse?.total_hits || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-secondary-text">Active Filter:</span>
                <span className="font-semibold truncate max-w-[120px]">
                  {selectedCategory || "All Topics"}
                </span>
              </div>
              {yearMin || yearMax ? (
                <div className="flex justify-between">
                  <span className="text-secondary-text">Year Window:</span>
                  <span className="font-semibold">
                    {yearMin || "–"} to {yearMax || "–"}
                  </span>
                </div>
              ) : null}
            </div>

            <div className="pt-2 border-t border-border space-y-2">
              <span className="text-xs font-semibold text-primary-text block">
                Related Topics & Exploration
              </span>
              <div className="flex flex-wrap gap-1.5">
                {categories.slice(0, 5).map((cat) => (
                  <button
                    key={cat.id}
                    type="button"
                    onClick={() => {
                      setSelectedCategory(cat.name);
                      updateSearchUrl({ category: cat.name, page: 1 });
                    }}
                    className="text-[11px] px-2 py-0.5 rounded bg-surface border border-border hover:bg-blue-pale hover:text-blue-primary transition-colors text-secondary-text"
                  >
                    #{cat.name}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
};
