# ScholarPulse Brand Kit

Files:
- `ScholarPulse_Brand_Kit.md` — brand principles, design tokens, screen-to-contract guidance, interaction/accessibility rules, acceptance checklist.
- `tokens.css` — ready-to-import CSS custom properties for the light theme.
- `tokens.json` — machine-readable starter tokens.

The core color tokens follow the provided `BACKEND_SPECIFICATION.md` design directives. Typography, spacing, radius, shadows, and derived states are implementation recommendations added to make the system usable. The kit does not claim that frontend code has already been wired or tested.

Suggested use: import `tokens.css` once in the frontend global stylesheet, then use `var(--token-name)` throughout components instead of one-off values.
