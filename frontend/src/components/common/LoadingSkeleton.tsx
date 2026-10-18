import React from "react";

interface SkeletonProps {
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = "" }) => (
  <div className={`animate-pulse bg-slate-200/70 rounded-md ${className}`} />
);

export const PaperCardSkeleton: React.FC = () => (
  <div className="bg-surface p-5 rounded-md border border-border space-y-3 shadow-sm">
    <div className="flex items-center justify-between">
      <Skeleton className="h-4 w-28" />
      <Skeleton className="h-4 w-16" />
    </div>
    <Skeleton className="h-6 w-3/4" />
    <Skeleton className="h-4 w-1/2" />
    <div className="space-y-1.5 pt-1">
      <Skeleton className="h-3.5 w-full" />
      <Skeleton className="h-3.5 w-5/6" />
    </div>
    <div className="flex gap-2 pt-2">
      <Skeleton className="h-5 w-20 rounded" />
      <Skeleton className="h-5 w-24 rounded" />
    </div>
  </div>
);

export const TableSkeleton: React.FC<{ rows?: number }> = ({ rows = 5 }) => (
  <div className="bg-surface rounded-md border border-border p-4 space-y-3">
    <Skeleton className="h-6 w-48" />
    <div className="space-y-2 pt-2">
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-10 w-full" />
      ))}
    </div>
  </div>
);
