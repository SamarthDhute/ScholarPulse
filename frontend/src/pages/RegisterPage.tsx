import React from "react";
import { Link } from "react-router-dom";
import { UserPlus, Info, ArrowLeft } from "lucide-react";

export const RegisterPage: React.FC = () => {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center max-w-md mx-auto px-4">
      <div className="w-full bg-surface rounded-md border border-border p-6 shadow-sm space-y-4 text-center">
        <div className="w-12 h-12 rounded-full bg-blue-pale text-blue-primary flex items-center justify-center mx-auto">
          <UserPlus className="w-6 h-6" />
        </div>

        <h1 className="text-xl font-bold text-primary-text">Create Account</h1>

        <div className="p-4 bg-surface-muted border border-border rounded text-xs text-secondary-text text-left space-y-2 leading-relaxed">
          <div className="flex items-center gap-1.5 font-semibold text-primary-text">
            <Info className="w-4 h-4 text-blue-primary" />
            Backend Contract Status: Open Research Mode
          </div>
          <p>
            Registration is currently not required. The ScholarPulse v1.0 platform provides access to all Information Retrieval algorithms, Data Science tools, clustering, and research analytics out-of-the-box.
          </p>
          <p>
            Personal libraries operate using deterministic session identifiers. User management contracts will be introduced in an upcoming release.
          </p>
        </div>

        <div className="pt-2">
          <Link
            to="/"
            className="inline-flex items-center justify-center gap-2 w-full py-2.5 px-4 bg-blue-primary hover:bg-blue-hover text-white text-xs font-semibold rounded transition-colors shadow-sm"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Return to Discovery
          </Link>
        </div>
      </div>
    </div>
  );
};
