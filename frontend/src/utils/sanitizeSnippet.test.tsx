import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { renderSafeSnippet } from "./sanitizeSnippet";

describe("renderSafeSnippet", () => {
  it("renders null for empty or undefined snippet", () => {
    expect(renderSafeSnippet(null)).toBeNull();
    expect(renderSafeSnippet(undefined)).toBeNull();
    expect(renderSafeSnippet("")).toBeNull();
  });

  it("safely highlights valid <mark> tags", () => {
    const snippet = "The <mark>transformer</mark> model and <mark>attention</mark> mechanism.";
    const { container } = render(<div>{renderSafeSnippet(snippet)}</div>);

    const markElements = container.querySelectorAll("mark");
    expect(markElements.length).toBe(2);
    expect(markElements[0].textContent).toBe("transformer");
    expect(markElements[1].textContent).toBe("attention");
  });

  it("neutralizes malicious script tags and does not execute or inject them as DOM elements", () => {
    const maliciousSnippet =
      "Safe text <script>alert('xss')</script> <mark>valid query</mark> <img src=x onerror=alert(1) />";
    const { container } = render(<div>{renderSafeSnippet(maliciousSnippet)}</div>);

    // No script or img elements should be rendered into the DOM
    expect(container.querySelectorAll("script").length).toBe(0);
    expect(container.querySelectorAll("img").length).toBe(0);

    // The <mark> element should still be parsed safely
    const marks = container.querySelectorAll("mark");
    expect(marks.length).toBe(1);
    expect(marks[0].textContent).toBe("valid query");

    // The script text is safely escaped as literal text
    expect(container.textContent).toContain("<script>alert('xss')</script>");
  });
});
