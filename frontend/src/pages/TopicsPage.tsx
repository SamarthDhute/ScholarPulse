import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Layers, ChevronRight } from "lucide-react";
import { apiClient } from "../services/apiClient";
import type { ClustersResponse, ClusterSummary } from "../types/api";
import { Skeleton } from "../components/common/LoadingSkeleton";
import { ErrorPanel } from "../components/common/ErrorPanel";

export const TopicsPage: React.FC = () => {
  const [method, setMethod] = useState<"kmeans" | "hierarchical">("kmeans");
  const [nClusters, setNClusters] = useState<number>(4);
  const [clustersResponse, setClustersResponse] = useState<ClustersResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchClusters = async (m: "kmeans" | "hierarchical", k: number) => {
    setLoading(true);
    setError(null);
    try {
      const clusterData = await apiClient.getClusters(m, k);
      setClustersResponse(clusterData);
    } catch (err: any) {
      setError(err);
      setClustersResponse(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClusters(method, nClusters);
  }, []);

  const handleApply = (e: React.FormEvent) => {
    e.preventDefault();
    fetchClusters(method, nClusters);
  };

  return (
    <div className="space-y-8">
      {/* Page Title & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-5">
        <div>
          <h1 className="text-2xl font-bold text-primary-text flex items-center gap-2">
            <Layers className="w-6 h-6 text-blue-primary" />
            Topic Modeling & Corpus Clustering
          </h1>
          <p className="text-xs text-secondary-text">
            Unsupervised machine learning partitions academic literature into semantic topic clusters.
          </p>
        </div>

        {/* Algorithm & Cluster Slider Form */}
        <form onSubmit={handleApply} className="flex items-center gap-3 bg-surface p-2 rounded-md border border-border shadow-sm flex-wrap">
          <div className="flex items-center gap-1.5 text-xs">
            <span className="font-semibold text-secondary-text">Method:</span>
            <select
              value={method}
              onChange={(e) => setMethod(e.target.value as "kmeans" | "hierarchical")}
              className="text-xs bg-surface-muted border border-border rounded px-2 py-1 text-primary-text focus:outline-none"
            >
              <option value="kmeans">K-Means</option>
              <option value="hierarchical">Agglomerative Hierarchical</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5 text-xs">
            <span className="font-semibold text-secondary-text">Clusters (k):</span>
            <input
              type="number"
              min={2}
              max={10}
              value={nClusters}
              onChange={(e) => setNClusters(parseInt(e.target.value, 10) || 4)}
              className="w-14 text-xs bg-surface-muted border border-border rounded px-2 py-1 text-primary-text text-center focus:outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="px-3 py-1 bg-blue-primary hover:bg-blue-hover text-white text-xs font-semibold rounded transition-colors shadow-sm disabled:opacity-50"
          >
            Compute
          </button>
        </form>
      </div>

      {error && <ErrorPanel error={error} onRetry={() => fetchClusters(method, nClusters)} />}

      {/* Cluster Evaluation KPI Bar */}
      {clustersResponse && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-surface p-4 rounded-md border border-border shadow-sm">
            <span className="text-[11px] font-medium text-secondary-text uppercase tracking-wider">
              Clustered Documents
            </span>
            <div className="text-2xl font-bold text-primary-text mt-0.5">
              {clustersResponse.total_documents}
            </div>
          </div>
          <div className="bg-surface p-4 rounded-md border border-border shadow-sm">
            <span className="text-[11px] font-medium text-secondary-text uppercase tracking-wider">
              Silhouette Score
            </span>
            <div className="text-2xl font-bold text-blue-primary font-mono mt-0.5">
              {clustersResponse.silhouette_score.toFixed(3)}
            </div>
            <span className="text-[10px] text-secondary-text">Cohesion & separation</span>
          </div>
          <div className="bg-surface p-4 rounded-md border border-border shadow-sm">
            <span className="text-[11px] font-medium text-secondary-text uppercase tracking-wider">
              Algorithm Applied
            </span>
            <div className="text-2xl font-bold text-primary-text capitalize mt-0.5">
              {clustersResponse.method}
            </div>
            <span className="text-[10px] text-secondary-text">TF-IDF feature vectors</span>
          </div>
          <div className="bg-surface p-4 rounded-md border border-border shadow-sm">
            <span className="text-[11px] font-medium text-secondary-text uppercase tracking-wider">
              Active Model Version
            </span>
            <div className="text-sm font-mono font-semibold text-primary-text mt-2 truncate">
              {clustersResponse.model_version}
            </div>
          </div>
        </div>
      )}

      {/* Clusters Grid */}
      <section className="space-y-4">
        <h2 className="text-base font-bold text-primary-text">
          Identified Topic Clusters ({clustersResponse?.clusters.length || 0})
        </h2>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="bg-surface p-5 rounded-md border border-border space-y-3">
                <Skeleton className="h-6 w-1/2" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-20 w-full" />
              </div>
            ))}
          </div>
        ) : clustersResponse && clustersResponse.clusters.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {clustersResponse.clusters.map((c: ClusterSummary) => (
              <div
                key={c.cluster_id}
                className="bg-surface rounded-md border border-border p-5 shadow-sm hover:border-blue-primary/40 transition-all space-y-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-blue-primary">
                      Cluster {c.cluster_id}
                    </span>
                    <h3 className="font-bold text-base text-primary-text leading-snug">
                      {c.label}
                    </h3>
                  </div>
                  <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-blue-pale text-blue-primary shrink-0">
                    {c.size} papers
                  </span>
                </div>

                {/* Top Discriminative Terms */}
                <div className="space-y-1.5">
                  <span className="text-[11px] font-semibold text-secondary-text uppercase tracking-wider block">
                    Salient Keywords
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {c.top_terms.map((t) => (
                      <span
                        key={t.term}
                        className="text-xs px-2 py-0.5 rounded bg-surface-muted border border-border text-primary-text font-mono"
                        title={`Weight: ${t.weight.toFixed(3)}`}
                      >
                        {t.term}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Representative Centroid Papers */}
                {c.representative_papers.length > 0 && (
                  <div className="space-y-1.5 pt-2 border-t border-border">
                    <span className="text-[11px] font-semibold text-secondary-text uppercase tracking-wider block">
                      Representative Papers (Centroid Nearest)
                    </span>
                    <div className="space-y-1.5">
                      {c.representative_papers.map((p) => (
                        <div
                          key={p.paper_id}
                          className="text-xs p-2 rounded bg-surface-muted/60 flex items-center justify-between gap-2"
                        >
                          <span className="font-medium text-primary-text truncate max-w-xs">
                            {p.title}
                          </span>
                          <span className="text-[10px] font-mono text-secondary-text shrink-0">
                            Dist: {p.similarity_to_centroid.toFixed(3)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Action Link to Inspect Cluster Member Papers */}
                <div className="pt-2 border-t border-border flex justify-end">
                  <Link
                    to={`/topics/clusters/${c.cluster_id}`}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-blue-primary hover:text-blue-hover"
                  >
                    Browse all {c.size} member papers <ChevronRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-surface p-8 rounded-md border border-border text-center text-sm text-secondary-text">
            No clusters computed. Click Compute above to run the algorithm.
          </div>
        )}
      </section>
    </div>
  );
};
