import React from "react";
import { Link } from "react-router-dom";
import { FileQuestion, ArrowLeft } from "lucide-react";

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-4">
      <div className="w-16 h-16 rounded-full bg-blue-pale text-blue-primary flex items-center justify-center mb-4">
        <FileQuestion className="w-8 h-8" />
      </div>
      <h1 className="text-3xl font-bold text-primary-text mb-2">404 — Page Not Found</h1>
      <p className="text-secondary-text max-w-md mb-6 text-sm">
        The academic route you requested does not exist or has been relocated.
      </p>
      <Link
        to="/"
        className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-blue-primary text-white font-medium text-sm hover:bg-blue-hover transition-colors shadow-sm"
      >
        <ArrowLeft className="w-4 h-4" />
        Return to Discover
      </Link>
    </div>
  );
};
