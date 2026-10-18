import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  Search,
  BookOpen,
  Layers,
  BarChart3,
  Bookmark,
  Sliders,
  ShieldAlert,
  Award,
  Menu,
  X,
  Compass,
} from "lucide-react";

interface NavItem {
  label: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
}

const NAV_ITEMS: NavItem[] = [
  { label: "Discover", path: "/", icon: Compass },
  { label: "Search", path: "/search", icon: Search },
  { label: "Papers", path: "/papers", icon: BookOpen },
  { label: "Topics", path: "/topics", icon: Layers },
  { label: "Analytics", path: "/analytics", icon: BarChart3 },
  { label: "Evaluation", path: "/evaluation", icon: Award },
  { label: "DS Tools", path: "/analysis", icon: Sliders },
  { label: "My Library", path: "/library", icon: Bookmark },
  { label: "Admin", path: "/admin/ingestion", icon: ShieldAlert },
];

export const Navbar: React.FC = () => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path: string) => {
    if (path === "/") {
      return location.pathname === "/";
    }
    return location.pathname.startsWith(path);
  };

  return (
    <header className="sticky top-0 z-50 bg-surface border-b border-border shadow-sm">
      <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-md bg-blue-pale flex items-center justify-center text-blue-primary group-hover:bg-blue-primary group-hover:text-white transition-colors duration-200">
            <BookOpen className="w-5 h-5 stroke-[2.2]" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-lg text-primary-text tracking-tight flex items-center gap-1.5">
              ScholarPulse
              <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded bg-blue-pale text-blue-primary tracking-normal">
                Academic
              </span>
            </span>
            <span className="text-[11px] text-secondary-text hidden sm:inline -mt-0.5">
              Information Retrieval & Data Science
            </span>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden lg:flex items-center gap-1" aria-label="Main Navigation">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                  active
                    ? "text-blue-primary bg-blue-pale font-semibold"
                    : "text-secondary-text hover:text-primary-text hover:bg-surface-muted"
                }`}
              >
                <Icon className={`w-4 h-4 ${active ? "text-blue-primary" : "text-secondary-text"}`} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Right Section: Demo Environment Info & Mobile Menu Toggle */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-md bg-surface-muted border border-border text-xs text-secondary-text">
            <span className="w-2 h-2 rounded-full bg-status-success animate-pulse" />
            <span>Local Core Mode</span>
          </div>

          {/* Mobile hamburger button */}
          <button
            type="button"
            className="lg:hidden p-2 rounded-md text-secondary-text hover:text-primary-text hover:bg-surface-muted border border-border"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-b border-border bg-surface px-4 pt-2 pb-4 space-y-1 shadow-md">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-2.5 px-3 py-2 text-sm font-medium rounded-md ${
                  active
                    ? "text-blue-primary bg-blue-pale font-semibold"
                    : "text-secondary-text hover:text-primary-text hover:bg-surface-muted"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>
      )}
    </header>
  );
};
