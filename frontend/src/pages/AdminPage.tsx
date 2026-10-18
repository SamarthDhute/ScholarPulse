import React, { useState, useEffect } from "react";
import { ShieldAlert, Play, CheckCircle2, Info, RefreshCw } from "lucide-react";
import { apiClient } from "../services/apiClient";
import type { IngestRunHistoryItem, IngestRunResponse } from "../types/api";
import { TableSkeleton } from "../components/common/LoadingSkeleton";
import { ErrorPanel } from "../components/common/ErrorPanel";

export const AdminPage: React.FC = () => {
  const [filepath, setFilepath] = useState("datasets/raw/sample_papers.json");
  const [sourceName, setSourceName] = useState("local_sample");

  const [history, setHistory] = useState<IngestRunHistoryItem[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [historyError, setHistoryError] = useState<Error | null>(null);

  const [ingesting, setIngesting] = useState(false);
  const [ingestResult, setIngestResult] = useState<IngestRunResponse | null>(null);
  const [ingestError, setIngestError] = useState<Error | null>(null);

  const loadHistory = async () => {
    setLoadingHistory(true);
    setHistoryError(null);
    try {
      const res = await apiClient.getIngestStatus(10);
      setHistory(res.runs);
    } catch (err: any) {
      setHistoryError(err);
      setHistory([]);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    setIngesting(true);
    setIngestError(null);
    setIngestResult(null);
    try {
      const res = await apiClient.triggerIngest({
        filepath: filepath.trim(),
        source_name: sourceName.trim(),
      });
      setIngestResult(res);
      // Reload history
      loadHistory();
    } catch (err: any) {
      setIngestError(err);
    } finally {
      setIngesting(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="border-b border-border pb-4">
        <h1 className="text-2xl font-bold text-primary-text flex items-center gap-2">
          <ShieldAlert className="w-6 h-6 text-blue-primary" />
          Corpus Administration & Data Ingestion
        </h1>
        <p className="text-xs text-secondary-text">
          Trigger batch dataset ingestion, validate provenance metadata, and view past pipeline execution runs.
        </p>
      </div>

      {/* Security & Contract Transparency Banner */}
      <div className="p-4 bg-surface-muted border border-border rounded-md text-xs text-secondary-text space-y-1.5 leading-relaxed">
        <div className="font-semibold text-primary-text flex items-center gap-1.5">
          <Info className="w-4 h-4 text-secondary-text" />
          Authorization & Access Notice
        </div>
        <p>
          In accordance with the project specification, role-based admin authentication is not implemented
          in backend v1.0. This view executes directly against the open administrative API surface and does
          not fabricate false permissions.
        </p>
      </div>

      {/* Ingestion Trigger Form */}
      <section className="bg-surface rounded-md border border-border p-6 shadow-sm space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-primary-text">
          Trigger Dataset Ingestion Run
        </h2>

        {ingestError && <ErrorPanel error={ingestError} title="Ingestion Run Failed" />}

        <form onSubmit={handleIngest} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-xs font-semibold text-primary-text">
                Dataset Filepath (Server Local)
              </label>
              <input
                type="text"
                value={filepath}
                onChange={(e) => setFilepath(e.target.value)}
                required
                className="w-full text-xs p-2.5 rounded border border-border bg-surface-muted text-primary-text font-mono focus:outline-none focus:ring-1 focus:ring-blue-primary"
              />
              <span className="text-[10px] text-secondary-text block">
                Relative to backend working directory
              </span>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-primary-text">
                Source Provider Name
              </label>
              <input
                type="text"
                value={sourceName}
                onChange={(e) => setSourceName(e.target.value)}
                required
                className="w-full text-xs p-2.5 rounded border border-border bg-surface-muted text-primary-text focus:outline-none focus:ring-1 focus:ring-blue-primary"
              />
              <span className="text-[10px] text-secondary-text block">
                Provenance tag (e.g. local_sample, arxiv, openalex)
              </span>
            </div>
          </div>

          <button
            type="submit"
            disabled={ingesting}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-primary hover:bg-blue-hover text-white text-xs font-semibold rounded transition-colors shadow-sm disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5" />
            {ingesting ? "Ingesting records..." : "Execute Ingestion"}
          </button>
        </form>

        {ingestResult && (
          <div className="p-4 bg-status-success-bg border border-status-success/30 rounded-md text-xs space-y-2 mt-4">
            <div className="font-bold text-status-success flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" />
              Ingestion Run Completed Successfully
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono text-[11px] text-primary-text pt-1">
              <div>Total: {ingestResult.total_processed}</div>
              <div>Created: {ingestResult.created_count}</div>
              <div>Updated: {ingestResult.updated_count}</div>
              <div>Skipped: {ingestResult.skipped_count}</div>
            </div>
            <div className="text-[10px] text-secondary-text font-mono pt-1">
              Run ID: {ingestResult.run_id}
            </div>
          </div>
        )}
      </section>

      {/* History Table */}
      <section className="bg-surface rounded-md border border-border shadow-sm overflow-hidden space-y-2">
        <div className="p-4 border-b border-border flex items-center justify-between">
          <h2 className="text-sm font-bold uppercase tracking-wider text-primary-text">
            Ingestion Execution History
          </h2>
          <button
            type="button"
            onClick={loadHistory}
            className="p-1 text-secondary-text hover:text-primary-text"
            title="Refresh history"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>

        {historyError && <ErrorPanel error={historyError} onRetry={loadHistory} />}

        {loadingHistory ? (
          <div className="p-4">
            <TableSkeleton rows={3} />
          </div>
        ) : history.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-surface-muted border-b border-border text-secondary-text font-semibold uppercase">
                  <th className="py-2.5 px-3">Run ID</th>
                  <th className="py-2.5 px-3">Source</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 text-right">Records</th>
                  <th className="py-2.5 px-3 text-right">Created</th>
                  <th className="py-2.5 px-3 text-right">Updated</th>
                  <th className="py-2.5 px-3 text-right">Started</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border font-mono text-[11px]">
                {history.map((run) => (
                  <tr key={run.run_id} className="hover:bg-blue-pale/20 transition-colors">
                    <td className="py-2.5 px-3 text-primary-text truncate max-w-[140px]" title={run.run_id}>
                      {run.run_id.slice(0, 12)}...
                    </td>
                    <td className="py-2.5 px-3 font-sans font-medium text-primary-text">
                      {run.source_name}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="px-1.5 py-0.5 rounded text-[10px] uppercase font-bold bg-status-success-bg text-status-success">
                        {run.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right text-secondary-text">
                      {run.total_records}
                    </td>
                    <td className="py-2.5 px-3 text-right text-primary-text font-semibold">
                      {run.created_count}
                    </td>
                    <td className="py-2.5 px-3 text-right text-secondary-text">
                      {run.updated_count}
                    </td>
                    <td className="py-2.5 px-3 text-right text-secondary-text">
                      {new Date(run.started_at).toLocaleTimeString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-6 text-center text-xs text-secondary-text">
            No past ingestion runs recorded in database.
          </div>
        )}
      </section>
    </div>
  );
};
