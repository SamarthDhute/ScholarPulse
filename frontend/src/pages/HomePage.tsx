import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Search, BookOpen, Layers, BarChart3, ArrowRight, Sparkles } from "lucide-react";
import { apiClient } from "../services/apiClient";
import type { OverviewSummary, PaperBrief, CategoryItem } from "../types/api";
import { Skeleton, PaperCardSkeleton } from "../components/common/LoadingSkeleton";
import { ErrorPanel } from "../components/common/ErrorPanel";
import { Badge } from "../components/common/Badge";

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [overview, setOverview] = useState<OverviewSummary | null>(null);
  const [recentPapers, setRecentPapers] = useState<PaperBrief[]>([]);
  const [categories, setCategories] = useState<CategoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const SUGGESTED_QUERIES = [
    "transformer attention mechanism",
    "information retrieval bm25",
    "vector space model tf-idf",
    "deep learning neural networks",
  ];

  const loadHomeData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [overviewData, papersData, categoriesData] = await Promise.all([
        apiClient.getAnalyticsOverview(),
        apiClient.listPapers({ page: 1, page_size: 5 }),
        apiClient.getCategories(),
      ]);
      setOverview(overviewData);
      setRecentPapers(papersData.items);
      setCategories(categoriesData);
    } catch (err: any) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHomeData();
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?query=${encodeURIComponent(searchQuery.trim())}&method=bm25`);
    }
  };

  return (
    <div className="space-y-10 py-4">
      {/* Hero Section */}
      <section className="text-center max-w-3xl mx-auto space-y-4 pt-6 pb-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-pale text-blue-primary text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Academic Information Retrieval & Knowledge Mining</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-extrabold text-primary-text tracking-tight leading-tight">
          Discover, Analyze & Compare Scientific Research
        </h1>
        <p className="text-base text-secondary-text max-w-2xl mx-auto">
          Built with probabilistic IR (Okapi BM25, TF-IDF, Language Models) and machine learning
          analytics over verified academic paper collections.
        </p>

        {/* Hero Search Box */}
        <form onSubmit={handleSearchSubmit} className="pt-2 max-w-2xl mx-auto">
          <div className="relative flex items-center shadow-md rounded-md overflow-hidden border border-border focus-within:ring-2 focus-within:ring-blue-primary/40 bg-surface">
            <div className="pl-4 text-secondary-text">
              <Search className="w-5 h-5" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by keywords, abstract text, or research topic..."
              className="w-full py-3.5 pl-3 pr-28 text-sm text-primary-text bg-transparent focus:outline-none"
            />
            <button
              type="submit"
              className="absolute right-1.5 px-4 py-2 bg-blue-primary hover:bg-blue-hover text-white text-sm font-semibold rounded transition-colors shadow-sm"
            >
              Search
            </button>
          </div>

          {/* Query Suggestion Chips */}
          <div className="flex flex-wrap items-center justify-center gap-2 pt-3 text-xs text-secondary-text">
            <span className="font-medium">Try:</span>
            {SUGGESTED_QUERIES.map((q) => (
              <button
                key={q}
                type="button"
                onClick={() => {
                  setSearchQuery(q);
                  navigate(`/search?query=${encodeURIComponent(q)}&method=bm25`);
                }}
                className="px-2.5 py-1 rounded-full bg-surface border border-border hover:bg-blue-pale hover:text-blue-primary hover:border-blue-primary/30 transition-colors text-primary-text font-normal"
              >
                {q}
              </button>
            ))}
          </div>
        </form>
      </section>

      {error && <ErrorPanel error={error} onRetry={loadHomeData} />}

      {/* KPI Stats Section */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-surface p-5 rounded-md border border-border space-y-2">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-8 w-16" />
            </div>
          ))
        ) : overview ? (
          <>
            <div className="bg-surface p-5 rounded-md border border-border shadow-sm">
              <span className="text-xs font-medium text-secondary-text uppercase tracking-wider">
                Indexed Papers
              </span>
              <div className="text-2xl sm:text-3xl font-bold text-primary-text mt-1">
                {overview.total_papers.toLocaleString()}
              </div>
              <span className="text-[11px] text-secondary-text">Across verified datasets</span>
            </div>
            <div className="bg-surface p-5 rounded-md border border-border shadow-sm">
              <span className="text-xs font-medium text-secondary-text uppercase tracking-wider">
                Unique Authors
              </span>
              <div className="text-2xl sm:text-3xl font-bold text-primary-text mt-1">
                {overview.total_authors.toLocaleString()}
              </div>
              <span className="text-[11px] text-secondary-text">
                Avg {overview.avg_authors_per_paper} per paper
              </span>
            </div>
            <div className="bg-surface p-5 rounded-md border border-border shadow-sm">
              <span className="text-xs font-medium text-secondary-text uppercase tracking-wider">
                Taxonomy Categories
              </span>
              <div className="text-2xl sm:text-3xl font-bold text-primary-text mt-1">
                {overview.total_categories}
              </div>
              <span className="text-[11px] text-secondary-text">Subject classifications</span>
            </div>
            <div className="bg-surface p-5 rounded-md border border-border shadow-sm">
              <span className="text-xs font-medium text-secondary-text uppercase tracking-wider">
                Publication Span
              </span>
              <div className="text-2xl sm:text-3xl font-bold text-primary-text mt-1">
                {overview.year_min && overview.year_max
                  ? `${overview.year_min} – ${overview.year_max}`
                  : "Corpus Range"}
              </div>
              <span className="text-[11px] text-secondary-text">Historical to contemporary</span>
            </div>
          </>
        ) : null}
      </section>

      {/* Two Column Layout: Recent Papers & Popular Categories */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Papers Feed (2 Cols) */}
        <section className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <div>
              <h2 className="text-lg font-bold text-primary-text flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-blue-primary" />
                Featured Research Papers
              </h2>
              <p className="text-xs text-secondary-text">Canonical metadata from local dataset</p>
            </div>
            <Link
              to="/papers"
              className="text-xs font-semibold text-blue-primary hover:text-blue-hover flex items-center gap-1"
            >
              View directory <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-3">
            {loading ? (
              Array.from({ length: 3 }).map((_, i) => <PaperCardSkeleton key={i} />)
            ) : recentPapers.length > 0 ? (
              recentPapers.map((paper) => (
                <div
                  key={paper.id}
                  className="bg-surface p-4 rounded-md border border-border hover:border-blue-primary/40 transition-all shadow-sm space-y-2"
                >
                  <div className="flex items-start justify-between gap-3">
                    <Link
                      to={`/papers/${paper.id}`}
                      className="font-semibold text-sm sm:text-base text-primary-text hover:text-blue-primary transition-colors leading-snug"
                    >
                      {paper.title}
                    </Link>
                    {paper.publication_year && (
                      <span className="text-xs font-mono text-secondary-text bg-surface-muted px-2 py-0.5 rounded border border-border shrink-0">
                        {paper.publication_year}
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-secondary-text line-clamp-2 leading-relaxed">
                    {paper.abstract || "No abstract available for this record."}
                  </p>

                  <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs">
                    <div className="text-secondary-text truncate max-w-sm">
                      {paper.authors.length > 0
                        ? paper.authors.slice(0, 3).join(", ") +
                          (paper.authors.length > 3 ? " et al." : "")
                        : "Unknown authors"}
                    </div>
                    <div className="flex items-center gap-1.5 flex-wrap">
                      {paper.categories.slice(0, 2).map((cat) => (
                        <Badge key={cat} variant="blue">
                          {cat}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-6 bg-surface rounded-md border border-border text-center text-sm text-secondary-text">
                No papers found in corpus.
              </div>
            )}
          </div>
        </section>

        {/* Right Sidebar: Topics & Quick Navigation (1 Col) */}
        <section className="space-y-6">
          {/* Research Categories */}
          <div className="bg-surface rounded-md border border-border p-5 shadow-sm space-y-3">
            <h3 className="font-bold text-sm text-primary-text flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-primary" />
              Active Research Fields
            </h3>
            <p className="text-xs text-secondary-text">
              Classified categories with indexed paper volumes.
            </p>
            <div className="space-y-1.5 pt-1">
              {loading ? (
                Array.from({ length: 4 }).map((_, i) => (
                  <Skeleton key={i} className="h-7 w-full" />
                ))
              ) : categories.length > 0 ? (
                categories.map((cat) => (
                  <Link
                    key={cat.id}
                    to={`/papers?category=${encodeURIComponent(cat.name)}`}
                    className="flex items-center justify-between p-2 rounded hover:bg-blue-pale text-xs text-primary-text transition-colors group"
                  >
                    <span className="font-medium group-hover:text-blue-primary truncate">
                      {cat.name}
                    </span>
                    <span className="text-[11px] font-mono text-secondary-text bg-surface-muted px-1.5 py-0.5 rounded border border-border shrink-0 ml-2">
                      {cat.paper_count} papers
                    </span>
                  </Link>
                ))
              ) : (
                <div className="text-xs text-secondary-text">No categories loaded.</div>
              )}
            </div>
          </div>

          {/* Quick IR & DS Jump Cards */}
          <div className="bg-blue-pale/50 border border-blue-primary/20 rounded-md p-5 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-blue-primary flex items-center gap-1.5">
              <BarChart3 className="w-4 h-4" />
              Knowledge Mining Engines
            </h4>
            <div className="space-y-2 text-xs">
              <Link
                to="/topics"
                className="block p-2.5 rounded bg-surface border border-border hover:border-blue-primary text-primary-text font-medium transition-all shadow-sm"
              >
                🔬 K-Means & Hierarchical Clustering
              </Link>
              <Link
                to="/analytics"
                className="block p-2.5 rounded bg-surface border border-border hover:border-blue-primary text-primary-text font-medium transition-all shadow-sm"
              >
                📈 Publication Trends & Co-authorship
              </Link>
              <Link
                to="/evaluation"
                className="block p-2.5 rounded bg-surface border border-border hover:border-blue-primary text-primary-text font-medium transition-all shadow-sm"
              >
                📊 IR Algorithm Benchmarking (MAP & NDCG)
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};
