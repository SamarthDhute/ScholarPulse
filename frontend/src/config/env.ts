/**
 * Environment configuration for ScholarPulse frontend.
 * Purely public variables only — zero secrets.
 */

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Normalize baseUrl to ensure no trailing slash
const cleanBaseUrl = rawBaseUrl.replace(/\/+$/, "");

// Ensure API base has /api/v1 prefix without duplication
export const API_BASE_URL = cleanBaseUrl.endsWith("/api/v1")
  ? cleanBaseUrl
  : `${cleanBaseUrl}/api/v1`;

export const DEFAULT_USER_ID =
  import.meta.env.VITE_DEFAULT_USER_ID || "00000000-0000-0000-0000-000000000001";

export const APP_CONFIG = {
  appName: "ScholarPulse",
  version: "1.0.0",
  apiBaseUrl: API_BASE_URL,
  defaultUserId: DEFAULT_USER_ID,
  defaultPageSize: 20,
  maxPageSize: 100,
} as const;
