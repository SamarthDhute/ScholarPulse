import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, ChevronRight } from "lucide-react";
import { apiClient } from "../services/apiClient";
import type { ClusterMembersResponse, ClusterMemberItem } from "../types/api";
import { PaperCardSkeleton } from "../components/common/LoadingSkeleton";
import { ErrorPanel } from "../components/common/ErrorPanel";
import { Badge } from "../components/common/Badge";

export const ClusterDetailPage: React.FC = () => {
  const { clusterId } = useParams<{ clusterId: string }>();
  const [page, setPage] = useState(1);
  const [data, setData] = useState<ClusterMembersResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const parsedId = clusterId ? parseInt(clusterId, 10) : 0;

  const loadClusterPapers = async (cId: number, p: number) => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.getClusterPapers(cId, p, 20);
      setData(res);
    } catch (err: any) {
      setError(err);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadClusterPapers(parsedId, page);
  }, [parsedId, page]);

  const totalPages = data ? Math.ceil(data.total / data.page_size) : 1;

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-secondary-text">
        <Link to="/topics" className="hover:text-primary-text flex items-center gap-1 font-medium">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Topic Modeling
        </Link>
        <span>/</span>
        <span className="text-primary-text font-semibold">Cluster {parsedId}</span>
      </div>

      {/* Header */}
      <div className="bg-surface rounded-md border border-border p-6 shadow-sm space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-blue-primary">
            Cluster {parsedId}
          </span>
          {data && (
            <span className="text-xs font-mono bg-blue-pale text-blue-primary px-2.5 py-0.5 rounded font-semibold">
              {data.total} member documents
            </span>
          )}
        </div>
        <h1 className="text-xl font-bold text-primary-text">
          {data?.label || `Topic Cluster #${parsedId}`}
        </h1>
        <p className="text-xs text-secondary-text">
          Full listing of research papers assigned to this cluster by the unsupervised partition algorithm.
        </p>
      </div>

      {error && (
        <ErrorPanel
          error={error}
          title="Could not load cluster members"
          onRetry={() => loadClusterPapers(parsedId, page)}
        />
      )}

      {/* Papers List */}
      <div className="space-y-3">
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => <PaperCardSkeleton key={i} />)
        ) : data && data.papers.length > 0 ? (
          <>
            {data.papers.map((p: ClusterMemberItem) => (
              <div
                key={p.paper_id}
                className="bg-surface rounded-md border border-border p-4 shadow-sm hover:border-blue-primary/40 transition-all flex items-center justify-between gap-4"
              >
                <div className="space-y-1">
                  <div className="font-semibold text-sm text-primary-text">
                    {p.title}
                  </div>
                  <div className="flex items-center gap-2 text-xs text-secondary-text">
                    {p.category && <Badge variant="blue">{p.category}</Badge>}
                    {p.publication_year && (
                      <span className="font-mono text-secondary-text">
                        Year: {p.publication_year}
                      </span>
                    )}
                    <span className="font-mono text-[10px] text-secondary-text truncate max-w-xs">
                      ID: {p.paper_id}
                    </span>
                  </div>
                </div>

                <Link
                  to={`/papers/${encodeURIComponent(p.paper_id)}`}
                  className="inline-flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded bg-blue-pale text-blue-primary hover:bg-blue-primary hover:text-white transition-colors shrink-0"
                >
                  View Paper <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            ))}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between bg-surface p-3 rounded-md border border-border text-xs">
                <button
                  type="button"
                  disabled={page <= 1}
                  onClick={() => setPage((prev) => Math.max(1, prev - 1))}
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
                  onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
                  className="px-3 py-1.5 rounded border border-border bg-surface hover:bg-surface-muted disabled:opacity-40 font-medium"
                >
                  Next
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="p-8 bg-surface rounded-md border border-border text-center text-sm text-secondary-text">
            No papers found in this cluster.
          </div>
        )}
      </div>
    </div>
  );
};
