import React, { useEffect, useState } from "react";
import {
  BarChart3,
  TrendingUp,
  PieChart as PieIcon,
  Tag,
  Users,
  RotateCcw,
} from "lucide-react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { apiClient } from "../services/apiClient";
import type {
  OverviewSummary,
  TrendItem,
  CategoryShare,
  KeywordShare,
  CollaborationNetwork,
} from "../types/api";
import { Skeleton } from "../components/common/LoadingSkeleton";
import { ErrorPanel } from "../components/common/ErrorPanel";

export const AnalyticsPage: React.FC = () => {
  const [yearMin, setYearMin] = useState<number | undefined>(undefined);
  const [yearMax, setYearMax] = useState<number | undefined>(undefined);

  const [overview, setOverview] = useState<OverviewSummary | null>(null);
  const [trends, setTrends] = useState<TrendItem[]>([]);
  const [categories, setCategories] = useState<CategoryShare[]>([]);
  const [keywords, setKeywords] = useState<KeywordShare[]>([]);
  const [collaboration, setCollaboration] = useState<CollaborationNetwork | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Scholarly color palette for charts
  const CHART_COLORS = [
    "#246BFD",
    "#16856B",
    "#C98222",
    "#7C3AED",
    "#0284C7",
    "#E11D48",
    "#059669",
    "#D97706",
  ];

  const loadAnalytics = async (yMin?: number, yMax?: number) => {
    setLoading(true);
    setError(null);
    try {
      const [ov, tr, cat, kw, col] = await Promise.all([
        apiClient.getAnalyticsOverview(yMin, yMax),
        apiClient.getAnalyticsTrends(yMin, yMax),
        apiClient.getAnalyticsCategories(yMin, yMax),
        apiClient.getAnalyticsKeywords(yMin, yMax, 10),
        apiClient.getCollaborationNetwork(1, 10),
      ]);
      setOverview(ov);
      setTrends(tr);
      setCategories(cat);
      setKeywords(kw);
      setCollaboration(col);
    } catch (err: any) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics(yearMin, yearMax);
  }, []);

  const handleFilterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadAnalytics(yearMin, yearMax);
  };

  const handleReset = () => {
    setYearMin(undefined);
    setYearMax(undefined);
    loadAnalytics(undefined, undefined);
  };

  return (
    <div className="space-y-8">
      {/* Header & Filter Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-5">
        <div>
          <h1 className="text-2xl font-bold text-primary-text flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-blue-primary" />
            Research Corpus Analytics
          </h1>
          <p className="text-xs text-secondary-text">
            Quantitative analysis of publication growth, taxonomy share, and co-authorship networks.
          </p>
        </div>

        <form onSubmit={handleFilterSubmit} className="flex items-center gap-2 bg-surface p-2 rounded-md border border-border shadow-sm flex-wrap text-xs">
          <span className="font-semibold text-secondary-text">Year Window:</span>
          <input
            type="number"
            placeholder="Min"
            value={yearMin || ""}
            onChange={(e) => setYearMin(e.target.value ? parseInt(e.target.value, 10) : undefined)}
            className="w-16 p-1.5 rounded border border-border bg-surface-muted text-center text-primary-text"
          />
          <span className="text-secondary-text">–</span>
          <input
            type="number"
            placeholder="Max"
            value={yearMax || ""}
            onChange={(e) => setYearMax(e.target.value ? parseInt(e.target.value, 10) : undefined)}
            className="w-16 p-1.5 rounded border border-border bg-surface-muted text-center text-primary-text"
          />
          <button
            type="submit"
            className="px-3 py-1.5 bg-blue-primary text-white rounded font-medium hover:bg-blue-hover transition-colors"
          >
            Apply
          </button>
          {(yearMin || yearMax) && (
            <button
              type="button"
              onClick={handleReset}
              className="p-1.5 text-secondary-text hover:text-status-error"
              title="Reset Filters"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          )}
        </form>
      </div>

      {error && <ErrorPanel error={error} onRetry={() => loadAnalytics(yearMin, yearMax)} />}

      {/* KPI Stats */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-surface p-5 rounded-md border border-border space-y-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-8 w-16" />
            </div>
          ))
        ) : overview ? (
          <>
            <div className="bg-surface p-5 rounded-md border border-border shadow-sm">
              <span className="text-xs font-medium text-secondary-text uppercase tracking-wider">
                Total Papers
              </span>
              <div className="text-2xl font-bold text-primary-text mt-1">
                {overview.total_papers.toLocaleString()}
              </div>
            </div>
            <div className="bg-surface p-5 rounded-md border border-border shadow-sm">
              <span className="text-xs font-medium text-secondary-text uppercase tracking-wider">
                Total Authors
              </span>
              <div className="text-2xl font-bold text-primary-text mt-1">
                {overview.total_authors.toLocaleString()}
              </div>
            </div>
            <div className="bg-surface p-5 rounded-md border border-border shadow-sm">
              <span className="text-xs font-medium text-secondary-text uppercase tracking-wider">
                Index Term Vocabulary
              </span>
              <div className="text-2xl font-bold text-primary-text mt-1">
                {overview.total_keywords.toLocaleString()}
              </div>
            </div>
            <div className="bg-surface p-5 rounded-md border border-border shadow-sm">
              <span className="text-xs font-medium text-secondary-text uppercase tracking-wider">
                Avg Authors / Paper
              </span>
              <div className="text-2xl font-bold text-blue-primary mt-1 font-mono">
                {overview.avg_authors_per_paper}
              </div>
            </div>
          </>
        ) : null}
      </section>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Chart 1: Publication Trends (Area Chart) */}
        <div className="bg-surface rounded-md border border-border p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-2.5">
            <div>
              <h3 className="font-bold text-sm text-primary-text flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-blue-primary" />
                Chronological Publication Growth
              </h3>
              <p className="text-[11px] text-secondary-text">Annual volume and cumulative research papers</p>
            </div>
          </div>

          <div className="h-72 w-full pt-2">
            {loading ? (
              <Skeleton className="h-full w-full" />
            ) : trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#DCE5EF" vertical={false} />
                  <XAxis dataKey="year" tick={{ fontSize: 11, fill: "#5F6F85" }} />
                  <YAxis tick={{ fontSize: 11, fill: "#5F6F85" }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#FFFFFF",
                      borderColor: "#DCE5EF",
                      borderRadius: "6px",
                      fontSize: "12px",
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                  <Area
                    type="monotone"
                    dataKey="count"
                    name="Annual Papers"
                    stroke="#246BFD"
                    fill="#EAF2FF"
                    strokeWidth={2}
                  />
                  <Area
                    type="monotone"
                    dataKey="cumulative_count"
                    name="Cumulative Total"
                    stroke="#16856B"
                    fill="#E8F6F1"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-secondary-text">
                No publication trend records available.
              </div>
            )}
          </div>
        </div>

        {/* Chart 2: Category Distribution (Pie Chart) */}
        <div className="bg-surface rounded-md border border-border p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-2.5">
            <div>
              <h3 className="font-bold text-sm text-primary-text flex items-center gap-2">
                <PieIcon className="w-4 h-4 text-blue-primary" />
                Subject Category Distribution
              </h3>
              <p className="text-[11px] text-secondary-text">Percentage share of classified research disciplines</p>
            </div>
          </div>

          <div className="h-72 w-full pt-2">
            {loading ? (
              <Skeleton className="h-full w-full" />
            ) : categories.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categories}
                    dataKey="count"
                    nameKey="category"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    innerRadius={45}
                    paddingAngle={3}
                  >
                    {categories.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#FFFFFF",
                      borderColor: "#DCE5EF",
                      borderRadius: "6px",
                      fontSize: "12px",
                    }}
                    formatter={(value: any, name: any, props: any) => [
                      `${value} papers (${props.payload.percentage_share}%)`,
                      name,
                    ]}
                  />
                  <Legend wrapperStyle={{ fontSize: "11px" }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-secondary-text">
                No category data available.
              </div>
            )}
          </div>
        </div>

        {/* Chart 3: Top Indexing Keywords (Bar Chart) */}
        <div className="bg-surface rounded-md border border-border p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-2.5">
            <div>
              <h3 className="font-bold text-sm text-primary-text flex items-center gap-2">
                <Tag className="w-4 h-4 text-blue-primary" />
                Top Indexing Keywords
              </h3>
              <p className="text-[11px] text-secondary-text">Frequency of prominent vocabulary terms</p>
            </div>
          </div>

          <div className="h-72 w-full pt-2">
            {loading ? (
              <Skeleton className="h-full w-full" />
            ) : keywords.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={keywords} layout="vertical" margin={{ top: 5, right: 20, left: 40, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#DCE5EF" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 11, fill: "#5F6F85" }} />
                  <YAxis
                    dataKey="keyword"
                    type="category"
                    tick={{ fontSize: 10, fill: "#14233B" }}
                    width={90}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#FFFFFF",
                      borderColor: "#DCE5EF",
                      borderRadius: "6px",
                      fontSize: "12px",
                    }}
                  />
                  <Bar dataKey="count" name="Papers" fill="#246BFD" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-secondary-text">
                No keyword data available.
              </div>
            )}
          </div>
        </div>

        {/* Collaboration Network Leaderboard */}
        <div className="bg-surface rounded-md border border-border p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-2.5">
            <div>
              <h3 className="font-bold text-sm text-primary-text flex items-center gap-2">
                <Users className="w-4 h-4 text-blue-primary" />
                Co-Authorship Collaboration Network
              </h3>
              <p className="text-[11px] text-secondary-text">
                Top joint research partnerships ({collaboration?.total_edges || 0} co-authorship edges)
              </p>
            </div>
          </div>

          <div className="space-y-2 pt-1 max-h-72 overflow-y-auto pr-1">
            {loading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))
            ) : collaboration && collaboration.top_collaborators.length > 0 ? (
              collaboration.top_collaborators.map((pair, index) => (
                <div
                  key={index}
                  className="p-3 bg-surface-muted rounded border border-border flex items-center justify-between text-xs"
                >
                  <div className="font-medium text-primary-text truncate max-w-xs">
                    {pair.author_a} &amp; {pair.author_b}
                  </div>
                  <span className="font-mono bg-blue-pale text-blue-primary px-2 py-0.5 rounded font-semibold text-[11px] shrink-0 ml-2">
                    {pair.collaborations} joint {pair.collaborations === 1 ? "paper" : "papers"}
                  </span>
                </div>
              ))
            ) : (
              <div className="p-6 text-center text-xs text-secondary-text">
                No co-authorship relationships found.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
