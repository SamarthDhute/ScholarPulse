import React, { useState, useEffect } from "react";
import { Sliders, Sparkles, Network } from "lucide-react";
import { apiClient } from "../services/apiClient";
import type {
  ClassifyResponse,
  AssociationRulesResponse,
  AssociationRuleItem,
} from "../types/api";
import { TableSkeleton } from "../components/common/LoadingSkeleton";
import { ErrorPanel } from "../components/common/ErrorPanel";

export const AnalysisPage: React.FC = () => {
  // Classification state
  const [inputText, setInputText] = useState(
    "Deep convolutional and recurrent neural network architectures for natural language processing and machine translation."
  );
  const [topK, setTopK] = useState(3);
  const [classifyResult, setClassifyResult] = useState<ClassifyResponse | null>(null);
  const [classifying, setClassifying] = useState(false);
  const [classifyError, setClassifyError] = useState<Error | null>(null);

  // Association rules state
  const [minSupport, setMinSupport] = useState(0.04);
  const [minConfidence, setMinConfidence] = useState(0.3);
  const [minLift, setMinLift] = useState(1.0);
  const [rulesResponse, setRulesResponse] = useState<AssociationRulesResponse | null>(null);
  const [rulesLoading, setRulesLoading] = useState(true);
  const [rulesError, setRulesError] = useState<Error | null>(null);

  const handleClassify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    setClassifying(true);
    setClassifyError(null);
    try {
      const res = await apiClient.classifyText({ text: inputText.trim(), top_k: topK });
      setClassifyResult(res);
    } catch (err: any) {
      setClassifyError(err);
      setClassifyResult(null);
    } finally {
      setClassifying(false);
    }
  };

  const loadRules = async () => {
    setRulesLoading(true);
    setRulesError(null);
    try {
      const res = await apiClient.getAssociationRules({
        min_support: minSupport,
        min_confidence: minConfidence,
        min_lift: minLift,
        page: 1,
        page_size: 20,
      });
      setRulesResponse(res);
    } catch (err: any) {
      setRulesError(err);
      setRulesResponse(null);
    } finally {
      setRulesLoading(false);
    }
  };

  useEffect(() => {
    loadRules();
  }, []);

  return (
    <div className="space-y-10 max-w-5xl mx-auto">
      {/* Header */}
      <div className="border-b border-border pb-4">
        <h1 className="text-2xl font-bold text-primary-text flex items-center gap-2">
          <Sliders className="w-6 h-6 text-blue-primary" />
          Data Science Analytics & Inference
        </h1>
        <p className="text-xs text-secondary-text">
          Interactive machine learning tools: Multiclass Text Classification & Association Rule Mining.
        </p>
      </div>

      {/* Section 1: Text Classifier */}
      <section className="bg-surface rounded-md border border-border p-6 shadow-sm space-y-4">
        <div>
          <h2 className="text-base font-bold text-primary-text flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-blue-primary" />
            Machine Learning Paper Category Classifier
          </h2>
          <p className="text-xs text-secondary-text">
            Enter an abstract or paper title to predict discipline categories using the trained scikit-learn classifier.
          </p>
        </div>

        {classifyError && <ErrorPanel error={classifyError} />}

        <form onSubmit={handleClassify} className="space-y-3">
          <textarea
            rows={3}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Paste research abstract or technical passage..."
            className="w-full text-xs p-3 rounded-md border border-border bg-surface-muted text-primary-text focus:outline-none focus:ring-1 focus:ring-blue-primary leading-relaxed"
          />

          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2 text-xs">
              <span className="text-secondary-text">Top predictions:</span>
              <select
                value={topK}
                onChange={(e) => setTopK(parseInt(e.target.value, 10))}
                className="bg-surface-muted border border-border rounded px-2 py-1 text-xs text-primary-text"
              >
                <option value={1}>1</option>
                <option value={3}>3</option>
                <option value={5}>5</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={classifying || !inputText.trim()}
              className="px-4 py-2 bg-blue-primary hover:bg-blue-hover text-white text-xs font-semibold rounded transition-colors shadow-sm disabled:opacity-50"
            >
              {classifying ? "Classifying..." : "Run Classifier"}
            </button>
          </div>
        </form>

        {classifyResult && (
          <div className="p-4 rounded-md bg-surface-muted border border-border space-y-3 pt-3">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-primary-text">Predicted Categories:</span>
              <span className="font-mono text-[11px] text-secondary-text">
                Model: {classifyResult.model_version}
              </span>
            </div>

            <div className="space-y-2">
              {classifyResult.predicted_categories.map((pred) => (
                <div key={pred.name} className="space-y-1">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-primary-text">{pred.name}</span>
                    <span className="font-mono text-blue-primary">
                      {(pred.score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full h-1.5 bg-border rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-primary rounded-full transition-all"
                      style={{ width: `${Math.min(100, Math.max(2, pred.score * 100))}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* Section 2: Apriori Association Rules */}
      <section className="bg-surface rounded-md border border-border p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border pb-3">
          <div>
            <h2 className="text-base font-bold text-primary-text flex items-center gap-2">
              <Network className="w-4 h-4 text-blue-primary" />
              Keyword Association Rules (Apriori Algorithm)
            </h2>
            <p className="text-xs text-secondary-text">
              Discovers strong co-occurrence patterns among keyword index terms across the research corpus.
            </p>
          </div>
          {rulesResponse && (
            <span className="text-xs font-mono bg-blue-pale text-blue-primary px-2.5 py-1 rounded font-semibold self-start sm:self-auto">
              {rulesResponse.total_rules} rules mined
            </span>
          )}
        </div>

        {/* Threshold Adjustment Controls */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 bg-surface-muted p-3.5 rounded border border-border text-xs">
          <div>
            <span className="text-secondary-text block mb-1">Min Support:</span>
            <input
              type="number"
              step="0.01"
              min="0.01"
              max="1.0"
              value={minSupport}
              onChange={(e) => setMinSupport(parseFloat(e.target.value) || 0.04)}
              className="w-full p-1.5 bg-surface border border-border rounded text-primary-text font-mono"
            />
          </div>
          <div>
            <span className="text-secondary-text block mb-1">Min Confidence:</span>
            <input
              type="number"
              step="0.05"
              min="0.1"
              max="1.0"
              value={minConfidence}
              onChange={(e) => setMinConfidence(parseFloat(e.target.value) || 0.3)}
              className="w-full p-1.5 bg-surface border border-border rounded text-primary-text font-mono"
            />
          </div>
          <div>
            <span className="text-secondary-text block mb-1">Min Lift:</span>
            <input
              type="number"
              step="0.1"
              min="0.5"
              max="10.0"
              value={minLift}
              onChange={(e) => setMinLift(parseFloat(e.target.value) || 1.0)}
              className="w-full p-1.5 bg-surface border border-border rounded text-primary-text font-mono"
            />
          </div>
          <div className="flex items-end">
            <button
              type="button"
              onClick={loadRules}
              className="w-full py-1.5 px-3 bg-blue-primary hover:bg-blue-hover text-white rounded font-medium transition-colors"
            >
              Mine Rules
            </button>
          </div>
        </div>

        {rulesError && <ErrorPanel error={rulesError} onRetry={loadRules} />}

        {/* Rules Table */}
        {rulesLoading ? (
          <TableSkeleton rows={4} />
        ) : rulesResponse && rulesResponse.rules.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-surface-muted border-b border-border text-secondary-text font-semibold uppercase">
                  <th className="py-2.5 px-3">Antecedent (If)</th>
                  <th className="py-2.5 px-3">Consequent (Then)</th>
                  <th className="py-2.5 px-3 text-right">Support</th>
                  <th className="py-2.5 px-3 text-right">Confidence</th>
                  <th className="py-2.5 px-3 text-right">Lift</th>
                  <th className="py-2.5 px-3 text-right">Conviction</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {rulesResponse.rules.map((rule: AssociationRuleItem, idx) => (
                  <tr key={idx} className="hover:bg-blue-pale/30 transition-colors font-mono">
                    <td className="py-2.5 px-3 font-sans text-primary-text font-medium">
                      {rule.antecedents.join(", ")}
                    </td>
                    <td className="py-2.5 px-3 font-sans text-blue-primary font-medium">
                      {rule.consequents.join(", ")}
                    </td>
                    <td className="py-2.5 px-3 text-right text-secondary-text">
                      {rule.support.toFixed(3)}
                    </td>
                    <td className="py-2.5 px-3 text-right text-primary-text font-semibold">
                      {(rule.confidence * 100).toFixed(1)}%
                    </td>
                    <td className="py-2.5 px-3 text-right font-bold text-status-success">
                      {rule.lift.toFixed(2)}x
                    </td>
                    <td className="py-2.5 px-3 text-right text-secondary-text">
                      {rule.conviction ? rule.conviction.toFixed(2) : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-secondary-text">
            No association rules satisfied the support and confidence constraints.
          </div>
        )}
      </section>
    </div>
  );
};
