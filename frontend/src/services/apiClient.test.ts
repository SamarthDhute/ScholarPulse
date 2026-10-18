import { describe, it, expect } from "vitest";
import { buildQueryString, ScholarPulseApiError } from "./apiClient";

describe("apiClient utilities", () => {
  describe("buildQueryString", () => {
    it("returns empty string when no params provided or all are undefined/null/empty", () => {
      expect(buildQueryString({})).toBe("");
      expect(buildQueryString({ query: "", category: null, page: undefined })).toBe("");
    });

    it("serializes valid parameters into URL query string", () => {
      const qs = buildQueryString({
        query: "transformer attention",
        method: "bm25",
        page: 1,
        year_min: 2017,
        year_max: 2024,
      });

      expect(qs).toBe("?query=transformer+attention&method=bm25&page=1&year_min=2017&year_max=2024");
    });

    it("omits empty string and null parameters cleanly", () => {
      const qs = buildQueryString({
        query: "neural",
        category: null,
        author: undefined,
        page: 2,
      });

      expect(qs).toBe("?query=neural&page=2");
    });
  });

  describe("ScholarPulseApiError", () => {
    it("constructs error object with code, message, and requestId", () => {
      const err = new ScholarPulseApiError(404, {
        code: "NOT_FOUND",
        message: "Paper not found",
        request_id: "req-12345",
      });

      expect(err.status).toBe(404);
      expect(err.code).toBe("NOT_FOUND");
      expect(err.message).toBe("Paper not found");
      expect(err.requestId).toBe("req-12345");
      expect(err.name).toBe("ScholarPulseApiError");
    });
  });
});
