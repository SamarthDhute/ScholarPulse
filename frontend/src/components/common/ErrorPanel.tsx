import React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { ScholarPulseApiError } from "../../services/apiClient";

interface ErrorPanelProps {
  error: Error | ScholarPulseApiError | string | null;
  onRetry?: () => void;
  title?: string;
}

export const ErrorPanel: React.FC<ErrorPanelProps> = ({
  error,
  onRetry,
  title = "Failed to load data from backend",
}) => {
  if (!error) return null;

  const isApiError = error instanceof ScholarPulseApiError;
  const message = typeof error === "string" ? error : error.message;
  const code = isApiError ? error.code : "CLIENT_ERROR";
  const requestId = isApiError ? error.requestId : undefined;

  return (
    <div className="bg-status-error-bg/60 border border-status-error/30 rounded-md p-5 text-primary-text my-4 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="p-1.5 rounded-full bg-status-error-bg text-status-error shrink-0 mt-0.5">
          <AlertTriangle className="w-5 h-5 stroke-[2]" />
        </div>
        <div className="flex-1 space-y-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className="text-sm font-semibold text-status-error">{title}</h4>
            <span className="text-[11px] font-mono px-1.5 py-0.5 bg-surface border border-status-error/30 text-status-error rounded">
              {code}
            </span>
          </div>
          <p className="text-sm text-secondary-text leading-relaxed">{message}</p>
          {requestId && (
            <p className="text-xs text-secondary-text font-mono pt-1">
              Trace Request ID: <span className="text-primary-text">{requestId}</span>
            </p>
          )}

          {onRetry && (
            <div className="pt-2">
              <button
                type="button"
                onClick={onRetry}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md bg-surface border border-border text-primary-text hover:bg-surface-muted transition-colors shadow-sm"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Retry Request
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
