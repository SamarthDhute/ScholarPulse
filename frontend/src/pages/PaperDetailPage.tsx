import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  ArrowLeft,
  Calendar,
  Bookmark,
  Check,
  ExternalLink,
  Sparkles,
  Tag,
  ChevronRight,
  User,
} from "lucide-react";
import { apiClient } from "../services/apiClient";
import type { PaperDetail, RelatedPaperItem } from "../types/api";
import { Skeleton } from "../components/common/LoadingSkeleton";
import { ErrorPanel } from "../components/common/ErrorPanel";
import { Badge } from "../components/common/Badge";

export const PaperDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const [paper, setPaper] = useState<PaperDetail | null>(null);
  const [relatedPapers, setRelatedPapers] = useState<RelatedPaperItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [relatedLoading, setRelatedLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const [isSaved, setIsSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (id) {
      loadPaperData(id);
    }
  }, [id]);

  const loadPaperData = async (paperId: string) => {
    setLoading(true);
    setError(null);
    try {
      const paperData = await apiClient.getPaper(paperId);
      setPaper(paperData);

      // Check bookmark status
      apiClient.getSavedPapers().then((res) => {
        setIsSaved(res.items.some((i) => i.paper_id === paperData.id));
      }).catch(() => {});

      // Load content-based related recommendations
      setRelatedLoading(true);
      apiClient
        .getRelatedPapers(paperId, 5)
        .then(setRelatedPapers)
        .catch(() => setRelatedPapers([]))
        .finally(() => setRelatedLoading(false));
    } catch (err: any) {
      setError(err);
      setPaper(null);
    } finally {
      setLoading(false);
    }
  };

  const handleBookmarkToggle = async () => {
    if (!paper) return;
    setSaving(true);
    try {
      if (isSaved) {
        await apiClient.removeSavedPaper(paper.id);
        setIsSaved(false);
      } else {
        await apiClient.savePaper({ paper_id: paper.id, notes: `Saved from paper detail page` });
        setIsSaved(true);
      }
    } catch (err) {
      console.error("Failed to toggle bookmark", err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Breadcrumb Navigation */}
      <div className="flex items-center gap-2 text-xs text-secondary-text">
        <Link to="/papers" className="hover:text-primary-text flex items-center gap-1 font-medium">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Directory
        </Link>
        <span>/</span>
        <span className="truncate max-w-sm text-primary-text">{paper?.title || "Paper Details"}</span>
      </div>

      {error && (
        <ErrorPanel
          error={error}
          title="Could not retrieve paper details"
          onRetry={() => id && loadPaperData(id)}
        />
      )}

      {loading ? (
        <div className="bg-surface rounded-md border border-border p-8 space-y-4">
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-4 w-1/3" />
          <div className="space-y-2 pt-4">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
          </div>
        </div>
      ) : paper ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
          {/* Main Paper Content (2 cols) */}
          <article className="lg:col-span-2 bg-surface rounded-md border border-border p-6 shadow-sm space-y-6">
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2">
                {paper.categories.map((c) => (
                  <Badge key={c.id} variant="blue">
                    {c.name}
                  </Badge>
                ))}
                {paper.publication_year && (
                  <Badge variant="muted">
                    <Calendar className="w-3 h-3 mr-1" />
                    {paper.publication_year}
                  </Badge>
                )}
              </div>

              <h1 className="text-xl sm:text-2xl font-bold text-primary-text leading-snug">
                {paper.title}
              </h1>

              {/* Authors List */}
              <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-secondary-text pt-1">
                <span className="font-semibold text-primary-text flex items-center gap-1">
                  <User className="w-3.5 h-3.5" /> Authors:
                </span>
                {paper.authors.length > 0 ? (
                  paper.authors.map((a, i) => (
                    <span key={a.id} className="text-primary-text font-medium">
                      {a.display_name}
                      {i < paper.authors.length - 1 ? "," : ""}
                    </span>
                  ))
                ) : (
                  <span>Unspecified</span>
                )}
              </div>
            </div>

            {/* Abstract */}
            <div className="space-y-2 border-t border-border pt-4">
              <h2 className="text-sm font-bold uppercase tracking-wider text-secondary-text">
                Abstract
              </h2>
              <p className="text-sm text-primary-text leading-relaxed whitespace-pre-line font-normal">
                {paper.abstract || "No abstract recorded in corpus."}
              </p>
            </div>

            {/* Keywords */}
            {paper.keywords.length > 0 && (
              <div className="space-y-2 border-t border-border pt-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-secondary-text flex items-center gap-1.5">
                  <Tag className="w-3.5 h-3.5" />
                  Keywords & Index Terms
                </h3>
                <div className="flex flex-wrap gap-1.5">
                  {paper.keywords.map((kw) => (
                    <Link
                      key={kw.id}
                      to={`/papers?keyword=${encodeURIComponent(kw.display_term)}`}
                      className="text-xs px-2.5 py-1 rounded-md bg-surface-muted hover:bg-blue-pale text-secondary-text hover:text-blue-primary transition-colors border border-border"
                    >
                      #{kw.display_term}
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {/* Canonical Metadata Table */}
            <div className="border-t border-border pt-4 space-y-2 text-xs">
              <h3 className="font-bold text-primary-text uppercase tracking-wider">
                Bibliographic Provenance
              </h3>
              <div className="bg-surface-muted/50 rounded border border-border p-3 space-y-2 font-mono">
                <div className="flex justify-between">
                  <span className="text-secondary-text">Canonical UUID:</span>
                  <span className="text-primary-text font-semibold select-all">{paper.id}</span>
                </div>
                {paper.doi && (
                  <div className="flex justify-between">
                    <span className="text-secondary-text">Digital Object Identifier (DOI):</span>
                    <a
                      href={`https://doi.org/${paper.doi}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-primary hover:underline flex items-center gap-1"
                    >
                      {paper.doi} <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                )}
                {paper.source_name && (
                  <div className="flex justify-between">
                    <span className="text-secondary-text">Source Repository:</span>
                    <span className="text-primary-text">{paper.source_name}</span>
                  </div>
                )}
                {paper.source_url && (
                  <div className="flex justify-between">
                    <span className="text-secondary-text">Source URL:</span>
                    <a
                      href={paper.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-primary hover:underline truncate max-w-xs"
                    >
                      {paper.source_url}
                    </a>
                  </div>
                )}
              </div>
            </div>
          </article>

          {/* Right Action & Related Sidebar (1 col) */}
          <aside className="space-y-6">
            {/* Action Card */}
            <div className="bg-surface rounded-md border border-border p-4 shadow-sm space-y-3">
              <button
                type="button"
                onClick={handleBookmarkToggle}
                disabled={saving}
                className={`w-full py-2.5 px-4 rounded-md text-sm font-semibold flex items-center justify-center gap-2 transition-all shadow-sm ${
                  isSaved
                    ? "bg-status-success-bg text-status-success border border-status-success/30"
                    : "bg-blue-primary text-white hover:bg-blue-hover"
                }`}
              >
                {isSaved ? <Check className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
                <span>{isSaved ? "Saved in My Library" : "Bookmark to Library"}</span>
              </button>

              <div className="pt-2 border-t border-border flex items-center justify-between text-xs text-secondary-text">
                <Link
                  to={`/recommendations/${paper.id}`}
                  className="text-blue-primary hover:underline font-medium flex items-center gap-1"
                >
                  View Related Models <ChevronRight className="w-3 h-3" />
                </Link>
              </div>
            </div>

            {/* Related Papers Card */}
            <div className="bg-surface rounded-md border border-border p-4 shadow-sm space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-primary-text flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-blue-primary" />
                Content-Based Related Papers
              </h3>
              <p className="text-[11px] text-secondary-text">
                Derived via TF-IDF cosine similarity over keywords and abstract text.
              </p>

              <div className="space-y-2.5 pt-1">
                {relatedLoading ? (
                  Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="p-2.5 bg-surface-muted rounded space-y-1">
                      <Skeleton className="h-4 w-3/4" />
                      <Skeleton className="h-3 w-1/2" />
                    </div>
                  ))
                ) : relatedPapers.length > 0 ? (
                  relatedPapers.map((rel) => (
                    <Link
                      key={rel.paper_id}
                      to={`/papers/${rel.paper_id}`}
                      className="block p-2.5 rounded bg-surface-muted hover:bg-blue-pale/70 transition-all border border-border/80 group space-y-1"
                    >
                      <div className="font-semibold text-xs text-primary-text group-hover:text-blue-primary leading-snug line-clamp-2">
                        {rel.title}
                      </div>
                      <div className="flex items-center justify-between text-[10px] text-secondary-text pt-0.5">
                        <span className="font-mono text-blue-primary font-medium">
                          Similarity: {(rel.similarity_score * 100).toFixed(1)}%
                        </span>
                        {rel.publication_year && <span>{rel.publication_year}</span>}
                      </div>
                    </Link>
                  ))
                ) : (
                  <div className="text-xs text-secondary-text p-2">
                    No related papers computed for this item.
                  </div>
                )}
              </div>
            </div>
          </aside>
        </div>
      ) : null}
    </div>
  );
};
