import React from "react";
import { Link } from "react-router-dom";
import { Lock, Info, ArrowLeft } from "lucide-react";

export const LoginPage: React.FC = () => {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center max-w-md mx-auto px-4">
      <div className="w-full bg-surface rounded-md border border-border p-6 shadow-sm space-y-4 text-center">
        <div className="w-12 h-12 rounded-full bg-blue-pale text-blue-primary flex items-center justify-center mx-auto">
          <Lock className="w-6 h-6" />
        </div>

        <h1 className="text-xl font-bold text-primary-text">ScholarPulse Authentication</h1>

        <div className="p-4 bg-surface-muted border border-border rounded text-xs text-secondary-text text-left space-y-2 leading-relaxed">
          <div className="flex items-center gap-1.5 font-semibold text-primary-text">
            <Info className="w-4 h-4 text-blue-primary" />
            Backend Contract Status: Open Research Mode
          </div>
          <p>
            The ScholarPulse v1.0 backend specification operates in an open academic research mode.
            Database actions and saved libraries utilize deterministic or header-driven session identifiers (e.g.{" "}
            <code className="text-primary-text font-mono">X-User-ID</code>) without requiring password-based login.
          </p>
          <p>
            Password authentication and user registration endpoints are not yet defined in the backend API contract.
            In accordance with project integrity rules, fake client-side logins are strictly disallowed.
          </p>
        </div>

        <div className="pt-2">
          <Link
            to="/"
            className="inline-flex items-center justify-center gap-2 w-full py-2.5 px-4 bg-blue-primary hover:bg-blue-hover text-white text-xs font-semibold rounded transition-colors shadow-sm"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Continue to Search & Discovery
          </Link>
        </div>
      </div>
    </div>
  );
};
