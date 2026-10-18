import React from "react";
import { Link } from "react-router-dom";

export const Footer: React.FC = () => {
  return (
    <footer className="mt-auto border-t border-border bg-surface text-secondary-text text-xs py-8">
      <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-4 text-center sm:text-left">
          <span className="font-semibold text-primary-text">ScholarPulse v1.0</span>
          <span className="hidden sm:inline text-border">•</span>
          <span>Information Retrieval & Data Science Academic Platform</span>
          <span className="hidden sm:inline text-border">•</span>
          <span>Light Theme Editorial Design</span>
        </div>

        <div className="flex items-center gap-6">
          <Link to="/evaluation" className="hover:text-primary-text transition-colors">
            IR Benchmarking
          </Link>
          <Link to="/analysis" className="hover:text-primary-text transition-colors">
            Data Science
          </Link>
          <Link to="/admin/ingestion" className="hover:text-primary-text transition-colors">
            Admin Ingestion
          </Link>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-blue-primary transition-colors font-medium text-blue-primary"
          >
            Swagger API Docs ↗
          </a>
        </div>
      </div>
    </footer>
  );
};
