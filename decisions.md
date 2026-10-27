# Decision Log

Record each decision once made. Newest first. Do not edit past entries; supersede them with a new entry.

## Template

### D-NNN: Title
- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Superseded by D-NNN
- **Context:** What prompted the decision.
- **Options considered:** Brief list.
- **Decision:** What was chosen.
- **Rationale:** Why.
- **Consequences:** Trade-offs, follow-ups.

---

## Open questions

- Modelling method for enrolment forecast (undecided; validate extraction first).

## Decisions

### D-002: Missing values are never imputed
- **Date:** 2026-10-27
- **Status:** Accepted
- **Decision:** Missing values stay blank/N/A in extracted data.
- **Rationale:** Avoids introducing unsourced values into the forecast inputs.

### D-001: uv as the sole package manager
- **Date:** 2026-10-27
- **Status:** Accepted
- **Decision:** Use uv only; no pip.
- **Rationale:** Single reproducible workflow.
