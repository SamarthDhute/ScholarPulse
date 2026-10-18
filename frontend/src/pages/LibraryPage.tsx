import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bookmark, Trash2, Info } from "lucide-react";
import { apiClient } from "../services/apiClient";
import type { SavedPaperItem } from "../types/api";
import { PaperCardSkeleton } from "../components/common/LoadingSkeleton";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorPanel } from "../components/common/ErrorPanel";

export const LibraryPage: React.FC = () => {
  const [savedPapers, setSavedPapers] = useState<SavedPaperItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const loadSavedPapers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.getSavedPapers();
      setSavedPapers(res.items);
    } catch (err: any) {
      setError(err);
      setSavedPapers([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSavedPapers();
  }, []);

  const handleRemove = async (paperId: string) => {
    setDeletingId(paperId);
    try {
      await apiClient.removeSavedPaper(paperId);
      setSavedPapers((prev) => prev.filter((p) => p.paper_id !== paperId));
    } catch (err: any) {
      setError(err);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold text-primary-text flex items-center gap-2">
            <Bookmark className="w-6 h-6 text-blue-primary" />
            My Saved Research Library
          </h1>
          <p className="text-xs text-secondary-text">
            Personal reading list and bookmarks stored via the backend library service.
          </p>
        </div>
        <div className="text-xs font-mono text-secondary-text bg-surface px-3 py-1 rounded border border-border">
          Saved count: <strong className="text-primary-text">{savedPapers.length}</strong>
        </div>
      </div>

      {/* Contract Notice Banner */}
      <div className="p-3.5 bg-blue-pale/50 border border-blue-primary/20 rounded-md flex items-start gap-2.5 text-xs text-secondary-text">
        <Info className="w-4 h-4 text-blue-primary shrink-0 mt-0.5" />
        <div>
          <strong className="text-primary-text">Contract Transparency:</strong> In ScholarPulse v1.0, the backend provides personal bookmark persistence with optional research notes. Named custom collections and query search history are not supported by the backend specification and are not fabricated.
        </div>
      </div>

      {error && <ErrorPanel error={error} onRetry={loadSavedPapers} />}

      {/* Saved Papers List */}
      <div className="space-y-3">
        {loading ? (
          Array.from({ length: 3 }).map((_, i) => <PaperCardSkeleton key={i} />)
        ) : savedPapers.length > 0 ? (
          savedPapers.map((item) => (
            <div
              key={item.id}
              className="bg-surface rounded-md border border-border p-5 shadow-sm hover:border-blue-primary/40 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            >
              <div className="space-y-1.5 flex-1">
                <Link
                  to={`/papers/${encodeURIComponent(item.paper_id)}`}
                  className="font-bold text-base text-primary-text hover:text-blue-primary transition-colors leading-snug"
                >
                  {item.title}
                </Link>

                <div className="flex flex-wrap items-center gap-2 text-xs text-secondary-text">
                  {item.publication_year && (
                    <span className="font-mono">Year: {item.publication_year}</span>
                  )}
                  {item.doi && (
                    <span className="font-mono text-[11px] truncate max-w-xs">
                      DOI: {item.doi}
                    </span>
                  )}
                  <span>•</span>
                  <span>
                    Saved on {new Date(item.saved_at).toLocaleDateString()}
                  </span>
                </div>

                {item.notes && (
                  <p className="text-xs text-secondary-text bg-surface-muted p-2 rounded border border-border italic">
                    "{item.notes}"
                  </p>
                )}
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <Link
                  to={`/papers/${encodeURIComponent(item.paper_id)}`}
                  className="px-3 py-1.5 text-xs font-semibold rounded bg-blue-pale text-blue-primary hover:bg-blue-primary hover:text-white transition-colors"
                >
                  Open Paper
                </Link>
                <button
                  type="button"
                  onClick={() => handleRemove(item.paper_id)}
                  disabled={deletingId === item.paper_id}
                  className="p-1.5 text-secondary-text hover:text-status-error hover:bg-status-error-bg rounded border border-border transition-colors disabled:opacity-50"
                  title="Remove from saved library"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        ) : (
          <EmptyState
            title="Your library is currently empty"
            description="Bookmark papers during search or while browsing the directory to save them here."
            actionLabel="Discover Research Papers"
            onAction={() => (window.location.href = "/search")}
          />
        )}
      </div>
    </div>
  );
};
