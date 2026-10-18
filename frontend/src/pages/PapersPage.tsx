import React, { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { BookOpen, Filter, RotateCcw, ChevronRight, User, Tag, Calendar } from "lucide-react";
import { apiClient } from "../services/apiClient";
import type { PaperListResponse, PaperBrief, CategoryItem } from "../types/api";
import { PaperCardSkeleton } from "../components/common/LoadingSkeleton";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorPanel } from "../components/common/ErrorPanel";
import { Badge } from "../components/common/Badge";

export const PapersPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const initialPage = parseInt(searchParams.get("page") || "1", 10);
  const initialCategory = searchParams.get("category") || "";
  const initialAuthor = searchParams.get("author") || "";
  const initialKeyword = searchParams.get("keyword") || "";
  const initialYearFrom = searchParams.get("year_from") ? parseInt(searchParams.get("year_from")!, 10) : undefined;
  const initialYearTo = searchParams.get("year_to") ? parseInt(searchParams.get("year_to")!, 10) : undefined;

  const [page, setPage] = useState(initialPage);
  const [category, setCategory] = useState(initialCategory);
  const [author, setAuthor] = useState(initialAuthor);
  const [keyword, setKeyword] = useState(initialKeyword);
  const [yearFrom, setYearFrom] = useState<number | undefined>(initialYearFrom);
  const [yearTo, setYearTo] = useState<number | undefined>(initialYearTo);

  const [papersResponse, setPapersResponse] = useState<PaperListResponse | null>(null);
  const [categories, setCategories] = useState<CategoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Fetch categories
  useEffect(() => {
    apiClient.getCategories().then(setCategories).catch(() => {});
  }, []);

  // Sync state with URL params
  useEffect(() => {
    const p = parseInt(searchParams.get("page") || "1", 10);
    const cat = searchParams.get("category") || "";
    const auth = searchParams.get("author") || "";
    const kw = searchParams.get("keyword") || "";
    const yFrom = searchParams.get("year_from") ? parseInt(searchParams.get("year_from")!, 10) : undefined;
    const yTo = searchParams.get("year_to") ? parseInt(searchParams.get("year_to")!, 10) : undefined;

    setPage(p);
    setCategory(cat);
    setAuthor(auth);
    setKeyword(kw);
    setYearFrom(yFrom);
    setYearTo(yTo);

    loadPapers(p, cat, auth, kw, yFrom, yTo);
  }, [searchParams]);

  const loadPapers = async (
    p: number,
    cat?: string,
    auth?: string,
    kw?: string,
    yFrom?: number,
    yTo?: number
  ) => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.listPapers({
        page: p,
        page_size: 20,
        category: cat || undefined,
        author: auth || undefined,
        keyword: kw || undefined,
        year_from: yFrom,
        year_to: yTo,
      });
      setPapersResponse(res);
    } catch (err: any) {
      setError(err);
      setPapersResponse(null);
    } finally {
      setLoading(false);
    }
  };

  const updateFilters = (updates: Record<string, any>) => {
    const next = new URLSearchParams(searchParams);
    for (const [k, v] of Object.entries(updates)) {
      if (v !== undefined && v !== null && v !== "") {
        next.set(k, String(v));
      } else {
        next.delete(k);
      }
    }
    setSearchParams(next);
  };

  const handleReset = () => {
    setCategory("");
    setAuthor("");
    setKeyword("");
    setYearFrom(undefined);
    setYearTo(undefined);
    setSearchParams(new URLSearchParams());
  };

  const totalPages = papersResponse
    ? Math.ceil(papersResponse.total / papersResponse.page_size)
    : 1;

  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold text-primary-text flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-blue-primary" />
            Research Papers Directory
          </h1>
          <p className="text-xs text-secondary-text">
            Browse the canonical paper repository with multifaceted metadata filters.
          </p>
        </div>
        {papersResponse && (
          <div className="text-xs font-mono text-secondary-text bg-surface px-3 py-1 rounded border border-border">
            Total records: <strong className="text-primary-text">{papersResponse.total}</strong>
          </div>
        )}
      </div>

      {error && <ErrorPanel error={error} onRetry={() => loadPapers(page, category, author, keyword, yearFrom, yearTo)} />}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
        {/* Left Filter Sidebar */}
        <aside className="bg-surface rounded-md border border-border p-4 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-primary-text flex items-center gap-1.5">
              <Filter className="w-3.5 h-3.5 text-blue-primary" />
              Filters
            </h3>
            <button
              type="button"
              onClick={handleReset}
              className="text-xs text-secondary-text hover:text-status-error flex items-center gap-1"
            >
              <RotateCcw className="w-3 h-3" /> Reset
            </button>
          </div>

          {/* Author Filter */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-primary-text flex items-center gap-1">
              <User className="w-3 h-3 text-secondary-text" />
              Author Name
            </label>
            <input
              type="text"
              placeholder="e.g. Vaswani"
              value={author}
              onChange={(e) => {
                setAuthor(e.target.value);
                updateFilters({ author: e.target.value, page: 1 });
              }}
              className="w-full text-xs p-2 rounded border border-border bg-surface-muted text-primary-text focus:outline-none focus:ring-1 focus:ring-blue-primary"
            />
          </div>

          {/* Keyword Filter */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-primary-text flex items-center gap-1">
              <Tag className="w-3 h-3 text-secondary-text" />
              Keyword Term
            </label>
            <input
              type="text"
              placeholder="e.g. attention"
              value={keyword}
              onChange={(e) => {
                setKeyword(e.target.value);
                updateFilters({ keyword: e.target.value, page: 1 });
              }}
              className="w-full text-xs p-2 rounded border border-border bg-surface-muted text-primary-text focus:outline-none focus:ring-1 focus:ring-blue-primary"
            />
          </div>

          {/* Year Range Filter (year_from, year_to) */}
          <div className="space-y-1.5 pt-2 border-t border-border">
            <label className="text-xs font-semibold text-primary-text flex items-center gap-1">
              <Calendar className="w-3 h-3 text-secondary-text" />
              Year Span
            </label>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="number"
                placeholder="From"
                value={yearFrom || ""}
                onChange={(e) => {
                  const val = e.target.value ? parseInt(e.target.value, 10) : undefined;
                  setYearFrom(val);
                  updateFilters({ year_from: val, page: 1 });
                }}
                className="w-full text-xs p-2 rounded border border-border bg-surface-muted text-primary-text focus:outline-none focus:ring-1 focus:ring-blue-primary"
              />
              <input
                type="number"
                placeholder="To"
                value={yearTo || ""}
                onChange={(e) => {
                  const val = e.target.value ? parseInt(e.target.value, 10) : undefined;
                  setYearTo(val);
                  updateFilters({ year_to: val, page: 1 });
                }}
                className="w-full text-xs p-2 rounded border border-border bg-surface-muted text-primary-text focus:outline-none focus:ring-1 focus:ring-blue-primary"
              />
            </div>
          </div>

          {/* Categories */}
          <div className="space-y-1.5 pt-2 border-t border-border">
            <label className="text-xs font-semibold text-primary-text block">
              Categories
            </label>
            <div className="space-y-1 max-h-48 overflow-y-auto pr-1">
              <button
                type="button"
                onClick={() => updateFilters({ category: undefined, page: 1 })}
                className={`w-full text-left px-2 py-1.5 rounded text-xs transition-colors flex items-center justify-between ${
                  !category
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
                  onClick={() => updateFilters({ category: c.name, page: 1 })}
                  className={`w-full text-left px-2 py-1.5 rounded text-xs transition-colors flex items-center justify-between ${
                    category === c.name
                      ? "bg-blue-pale text-blue-primary font-semibold"
                      : "text-secondary-text hover:bg-surface-muted"
                  }`}
                >
                  <span className="truncate">{c.name}</span>
                  <span className="text-[10px] font-mono">{c.paper_count}</span>
                </button>
              ))}
            </div>
          </div>
        </aside>

        {/* Papers List */}
        <section className="lg:col-span-3 space-y-4">
          {loading ? (
            Array.from({ length: 4 }).map((_, i) => <PaperCardSkeleton key={i} />)
          ) : papersResponse && papersResponse.items.length > 0 ? (
            <div className="space-y-3">
              {papersResponse.items.map((paper: PaperBrief) => (
                <article
                  key={paper.id}
                  className="bg-surface rounded-md border border-border p-5 hover:border-blue-primary/40 transition-all shadow-sm space-y-2.5"
                >
                  <div className="flex items-start justify-between gap-3">
                    <Link
                      to={`/papers/${paper.id}`}
                      className="font-bold text-base text-primary-text hover:text-blue-primary transition-colors leading-snug"
                    >
                      {paper.title}
                    </Link>
                    {paper.publication_year && (
                      <span className="text-xs font-mono text-secondary-text bg-surface-muted px-2 py-0.5 rounded border border-border shrink-0">
                        {paper.publication_year}
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-secondary-text line-clamp-3 leading-relaxed">
                    {paper.abstract || "Abstract not provided for this record."}
                  </p>

                  <div className="text-xs text-secondary-text flex flex-wrap items-center gap-1">
                    <span className="font-medium text-primary-text">Authors:</span>
                    <span>{paper.authors.length > 0 ? paper.authors.join(", ") : "Unknown"}</span>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-border text-xs">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      {paper.categories.map((c) => (
                        <Badge key={c} variant="blue">
                          {c}
                        </Badge>
                      ))}
                      {paper.keywords.slice(0, 3).map((kw) => (
                        <Badge key={kw} variant="muted">
                          #{kw}
                        </Badge>
                      ))}
                    </div>

                    <Link
                      to={`/papers/${paper.id}`}
                      className="inline-flex items-center gap-1 px-3 py-1 rounded text-xs font-semibold bg-blue-pale text-blue-primary hover:bg-blue-primary hover:text-white transition-colors"
                    >
                      Inspect <ChevronRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </article>
              ))}

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between bg-surface p-3 rounded-md border border-border text-xs">
                  <button
                    type="button"
                    disabled={page <= 1}
                    onClick={() => updateFilters({ page: page - 1 })}
                    className="px-3 py-1.5 rounded border border-border bg-surface hover:bg-surface-muted disabled:opacity-40 font-medium"
                  >
                    Previous
                  </button>
                  <span className="text-secondary-text">
                    Page <strong className="text-primary-text">{page}</strong> of{" "}
                    <strong>{totalPages}</strong>
                  </span>
                  <button
                    type="button"
                    disabled={page >= totalPages}
                    onClick={() => updateFilters({ page: page + 1 })}
                    className="px-3 py-1.5 rounded border border-border bg-surface hover:bg-surface-muted disabled:opacity-40 font-medium"
                  >
                    Next
                  </button>
                </div>
              )}
            </div>
          ) : (
            <EmptyState
              title="No papers match the selected criteria"
              description="Try relaxing your author, keyword, or year span filters."
              actionLabel="Clear Filters"
              onAction={handleReset}
            />
          )}
        </section>
      </div>
    </div>
  );
};
