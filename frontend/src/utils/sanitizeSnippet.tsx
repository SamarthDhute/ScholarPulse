import React from "react";

/**
 * Safely parses snippet text containing `<mark>` highlight tags without
 * using `dangerouslySetInnerHTML`.
 *
 * Any script tags, event handlers, or unallowed HTML elements are treated as plain text
 * and safely escaped by React's standard text node rendering.
 *
 * @param snippet Raw string snippet from backend API (may contain `<mark>term</mark>`)
 * @returns ReactNode array of safe strings and `<mark>` React elements.
 */
export function renderSafeSnippet(snippet: string | undefined | null): React.ReactNode {
  if (!snippet) {
    return null;
  }

  // Regex matches balanced <mark>...</mark> blocks non-greedily
  const markRegex = /(<mark>[\s\S]*?<\/mark>)/gi;
  const parts = snippet.split(markRegex);

  return parts.map((part, index) => {
    const isMarkTag = part.toLowerCase().startsWith("<mark>") && part.toLowerCase().endsWith("</mark>");

    if (isMarkTag) {
      // Extract the inner content inside <mark>...</mark>
      const innerText = part.slice(6, -7);
      return (
        <mark
          key={`mark-${index}`}
          className="bg-blue-pale text-blue-primary font-semibold px-0.5 rounded-sm"
        >
          {innerText}
        </mark>
      );
    }

    // Standard plain text is safely handled by React JSX (escapes <script>, etc.)
    return <React.Fragment key={`text-${index}`}>{part}</React.Fragment>;
  });
}
