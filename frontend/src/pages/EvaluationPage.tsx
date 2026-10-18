import React, { useEffect, useState } from "react";
import { Award, Info } from "lucide-react";
import { apiClient } from "../services/apiClient";
import type { EvaluationResponse, EvaluationReportItem } from "../types/api";
import { TableSkeleton } from "../components/common/LoadingSkeleton";
import { ErrorPanel } from "../components/common/ErrorPanel";

export const EvaluationPage: React.FC = () => {
  const [evalData, setEvalData] = useState<EvaluationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const loadEvaluation = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getRetrievalEvaluation();
      setEvalData(data);
    } catch (err: any) {
      setError(err);
      setEvalData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvaluation();
  }, []);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold text-primary-text flex items-center gap-2">
            <Award className="w-6 h-6 text-blue-primary" />
            Information Retrieval Benchmarking & Evaluation
          </h1>
          <p className="text-xs text-secondary-text">
            Standard Cranfield-style IR evaluation using pre-annotated relevance judgments.
          </p>
        </div>
        {evalData && (
          <div className="text-xs font-mono text-secondary-text bg-surface px-3 py-1 rounded border border-border">
            Dataset: <strong className="text-primary-text">{evalData.dataset_version}</strong> •{" "}
            Queries: <strong className="text-primary-text">{evalData.query_count}</strong>
          </div>
        )}
      </div>

      {/* Methodology Explainer */}
      <div className="bg-surface rounded-md border border-border p-4 shadow-sm text-xs text-secondary-text space-y-1.5 leading-relaxed">
        <div className="font-semibold text-primary-text flex items-center gap-1.5">
          <Info className="w-4 h-4 text-blue-primary" />
          Rigorous Evaluation Methodology
        </div>
        <p>
          Metrics are computed deterministically against test queries with ground-truth binary relevance
          judgments. All metric values displayed below originate directly from the backend evaluation engine.
        </p>
      </div>

      {error && <ErrorPanel error={error} onRetry={loadEvaluation} />}

      {/* Main Benchmark Comparison Table */}
      <section className="bg-surface rounded-md border border-border shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-border">
          <h2 className="text-sm font-bold uppercase tracking-wider text-primary-text">
            Algorithm Performance Comparison
          </h2>
        </div>

        {loading ? (
          <div className="p-4">
            <TableSkeleton rows={4} />
          </div>
        ) : evalData && evalData.reports.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-surface-muted border-b border-border text-secondary-text font-semibold uppercase tracking-wider">
                  <th className="py-3 px-4">IR Model</th>
                  <th className="py-3 px-3 text-right">Queries</th>
                  <th className="py-3 px-3 text-right">MAP</th>
                  <th className="py-3 px-3 text-right">MRR</th>
                  <th className="py-3 px-3 text-right">P@5</th>
                  <th className="py-3 px-3 text-right">P@10</th>
                  <th className="py-3 px-3 text-right">R@10</th>
                  <th className="py-3 px-4 text-right">NDCG@10</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border font-mono">
                {evalData.reports.map((report: EvaluationReportItem) => (
                  <tr key={report.ranker_name} className="hover:bg-blue-pale/30 transition-colors">
                    <td className="py-3.5 px-4 font-sans font-bold text-primary-text">
                      {report.ranker_name.toUpperCase()}
                    </td>
                    <td className="py-3.5 px-3 text-right text-secondary-text">
                      {report.num_queries}
                    </td>
                    <td className="py-3.5 px-3 text-right font-bold text-blue-primary">
                      {report.mean_average_precision.toFixed(4)}
                    </td>
                    <td className="py-3.5 px-3 text-right text-primary-text">
                      {report.mean_reciprocal_rank.toFixed(4)}
                    </td>
                    <td className="py-3.5 px-3 text-right text-secondary-text">
                      {report.precision_at_k["5"] !== undefined ? report.precision_at_k["5"].toFixed(4) : "—"}
                    </td>
                    <td className="py-3.5 px-3 text-right text-secondary-text">
                      {report.precision_at_k["10"] !== undefined ? report.precision_at_k["10"].toFixed(4) : "—"}
                    </td>
                    <td className="py-3.5 px-3 text-right text-secondary-text">
                      {report.recall_at_k["10"] !== undefined ? report.recall_at_k["10"].toFixed(4) : "—"}
                    </td>
                    <td className="py-3.5 px-4 text-right font-semibold text-status-success">
                      {report.ndcg_at_k["10"] !== undefined ? report.ndcg_at_k["10"].toFixed(4) : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-secondary-text">
            No evaluation benchmarks available. Run backend evaluation suite or ingest ground truth.
          </div>
        )}
      </section>

      {/* Metric Definitions Card */}
      <section className="bg-surface rounded-md border border-border p-5 shadow-sm space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-primary-text">
          Metric Definitions & Interpretations
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-secondary-text leading-relaxed">
          <div className="p-3 rounded bg-surface-muted border border-border space-y-1">
            <strong className="text-primary-text">Mean Average Precision (MAP):</strong>
            <p>
              Computes the mean of the average precision across all test queries, giving higher credit
              when relevant papers appear near top ranks.
            </p>
          </div>
          <div className="p-3 rounded bg-surface-muted border border-border space-y-1">
            <strong className="text-primary-text">Mean Reciprocal Rank (MRR):</strong>
            <p>
              Measures the reciprocal rank of the first relevant document retrieved across evaluation queries.
            </p>
          </div>
          <div className="p-3 rounded bg-surface-muted border border-border space-y-1">
            <strong className="text-primary-text">Precision@K & Recall@K:</strong>
            <p>
              Proportion of retrieved documents that are relevant at cutoff K, and proportion of total
              relevant documents successfully retrieved.
            </p>
          </div>
          <div className="p-3 rounded bg-surface-muted border border-border space-y-1">
            <strong className="text-primary-text">Normalized Discounted Cumulative Gain (NDCG@K):</strong>
            <p>
              Evaluates ranking quality accounting for the graded position of relevant items with logarithmic discounting.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};
