import React from "react";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "blue" | "success" | "warning" | "error" | "muted";
  className?: string;
  onClick?: () => void;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "blue",
  className = "",
  onClick,
}) => {
  const variantStyles = {
    blue: "bg-blue-pale text-blue-primary border-blue-primary/20",
    success: "bg-status-success-bg text-status-success border-status-success/20",
    warning: "bg-status-warning-bg text-status-warning border-status-warning/20",
    error: "bg-status-error-bg text-status-error border-status-error/20",
    muted: "bg-surface-muted text-secondary-text border-border",
  };

  const clickableStyles = onClick
    ? "cursor-pointer hover:opacity-85 active:scale-95 transition-all"
    : "";

  return (
    <span
      onClick={onClick}
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium border ${variantStyles[variant]} ${clickableStyles} ${className}`}
    >
      {children}
    </span>
  );
};
