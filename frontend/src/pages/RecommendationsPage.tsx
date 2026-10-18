import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Sparkles, ArrowLeft, ChevronRight, Tag } from "lucide-react";
import { apiClient } from "../services/apiClient";
import type { RelatedPaperItem, PaperDetail } from "../types/api";
import { PaperCardSkeleton } from "../components/common/LoadingSkeleton";
import { ErrorPanel } from "../components/common/ErrorPanel";
import { Badge } from "../components/common/Badge";

export const RecommendationsPage: React.FC = () => {
  const { paperId } = useParams<{ paperId: string }>();

  const [topN, setTopN] = useState<number>(10);
  const [seedPaper, setSeedPaper] = useState<PaperDetail | null>(null);
  const [relatedPapers, setRelatedPapers] = useState<RelatedPaperItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchRecommendations = async (id: string, n: number) => {
    setLoading(true);
    setError(null);
    try {
      const [seed, related] = await Promise.all([
        apiClient.getPaper(id),
        apiClient.getRelatedPapers(id, n),
      ]);
      setSeedPaper(seed);
      setRelatedPapers(related);
    } catch (err: any) {
      setError(err);
      setRelatedPapers([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (paperId) {
      fetchRecommendations(paperId, topN);
    }
  }, [paperId, topN]);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-secondary-text">
        <Link to="/papers" className="hover:text-primary-text flex items-center gap-1 font-medium">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Directory
        </Link>
        <span>/</span>
        <span className="text-primary-text font-semibold">Recommendations Engine</span>
      </div>

      {/* Seed Paper Header Card */}
      <div className="bg-surface rounded-md border border-border p-6 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-blue-primary">
            Seed Reference Paper
          </span>
          <div className="flex items-center gap-2 text-xs">
            <span className="text-secondary-text">Top N:</span>
            <select
              value={topN}
              onChange={(e) => setTopN(parseInt(e.target.value, 10))}
              className="bg-surface-muted border border-border rounded px-2 py-1 text-xs text-primary-text focus:outline-none"
            >
              <option value={5}>Top 5</option>
              <option value={10}>Top 10</option>
              <option value={20}>Top 20</option>
            </select>
          </div>
        </div>

        {seedPaper && (
          <div className="space-y-1">
            <h1 className="text-xl font-bold text-primary-text">{seedPaper.title}</h1>
            <p className="text-xs text-secondary-text line-clamp-2">{seedPaper.abstract}</p>
          </div>
        )}
      </div>

      {error && (
        <ErrorPanel
          error={error}
          title="Could not load recommendations"
          onRetry={() => paperId && fetchRecommendations(paperId, topN)}
        />
      )}

      {/* Recommendations List */}
      <section className="space-y-3">
        <h2 className="text-sm font-bold uppercase tracking-wider text-primary-text flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-blue-primary" />
          Recommended Literature by Content Similarity
        </h2>

        {loading ? (
          Array.from({ length: 4 }).map((_, i) => <PaperCardSkeleton key={i} />)
        ) : relatedPapers.length > 0 ? (
          relatedPapers.map((paper) => (
            <div
              key={paper.paper_id}
              className="bg-surface rounded-md border border-border p-5 shadow-sm hover:border-blue-primary/40 transition-all space-y-3"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <Link
                    to={`/papers/${paper.paper_id}`}
                    className="font-bold text-base text-primary-text hover:text-blue-primary transition-colors leading-snug"
                  >
                    {paper.title}
                  </Link>
                  <div className="flex items-center gap-2 text-xs text-secondary-text mt-1">
                    {paper.category && <Badge variant="blue">{paper.category}</Badge>}
                    {paper.publication_year && (
                      <span className="font-mono">Year: {paper.publication_year}</span>
                    )}
                  </div>
                </div>

                <div className="text-right shrink-0">
                  <span className="text-xs font-mono font-bold px-2 py-1 rounded bg-blue-pale text-blue-primary">
                    {(paper.similarity_score * 100).toFixed(1)}% Match
                  </span>
                </div>
              </div>

              {/* Shared Keywords */}
              {paper.shared_keywords.length > 0 && (
                <div className="flex items-center gap-1.5 flex-wrap text-xs pt-1">
                  <span className="text-secondary-text font-medium flex items-center gap-1">
                    <Tag className="w-3 h-3" /> Shared Terms:
                  </span>
                  {paper.shared_keywords.map((kw) => (
                    <span
                      key={kw}
                      className="px-2 py-0.5 rounded bg-surface-muted border border-border text-[11px] text-primary-text"
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              )}

              <div className="flex justify-end pt-2 border-t border-border">
                <Link
                  to={`/papers/${paper.paper_id}`}
                  className="inline-flex items-center gap-1 text-xs font-semibold px-3 py-1 rounded bg-blue-pale text-blue-primary hover:bg-blue-primary hover:text-white transition-colors"
                >
                  Inspect Paper <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))
        ) : (
          <div className="bg-surface rounded-md border border-border p-8 text-center text-sm text-secondary-text">
            No related papers met the similarity threshold.
          </div>
        )}
      </section>
    </div>
  );
};
