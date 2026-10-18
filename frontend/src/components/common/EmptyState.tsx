import React from "react";
import { SearchX, FileQuestion, FolderOpen } from "lucide-react";

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: "search" | "file" | "folder";
  actionLabel?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = "No research papers found",
  description = "Try adjusting your query, relaxing filters, or selecting a different retrieval algorithm.",
  icon = "search",
  actionLabel,
  onAction,
}) => {
  const IconComponent = icon === "search" ? SearchX : icon === "file" ? FileQuestion : FolderOpen;

  return (
    <div className="bg-surface rounded-md border border-border p-8 text-center max-w-lg mx-auto my-6 shadow-sm">
      <div className="w-12 h-12 rounded-full bg-surface-muted border border-border flex items-center justify-center mx-auto text-secondary-text mb-3">
        <IconComponent className="w-6 h-6 stroke-[1.5]" />
      </div>
      <h3 className="text-base font-semibold text-primary-text mb-1">{title}</h3>
      <p className="text-sm text-secondary-text mb-4 leading-relaxed">{description}</p>
      {actionLabel && onAction && (
        <button
          type="button"
          onClick={onAction}
          className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md bg-blue-pale text-blue-primary hover:bg-blue-primary hover:text-white transition-colors"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
};
