# matters/ — portfolio data

This folder holds the portfolio. Two layers:

- **`_log.yaml`** — the ledger. One row per matter. Parseable by skills. Source of truth for rollups.
- **`[slug]/`** — per-matter detail. Narrative and history. Where humans read and edit.

## Layout

```
matters/
├── _log.yaml                  # ledger (all matters, including closed)
├── _README.md                 # this file
└── [matter-slug]/
    ├── matter.md              # narrative intake + theory + posture
    └── history.md             # append-only event log
```

## Slug conventions

Lowercase, hyphens, year at the end. Examples:
- `acme-v-us-2026`
- `ftc-inquiry-2026`
- `employment-smith-2026`

Year makes the slug stable even if a similar matter arises later. The folder name matches the slug exactly.

## Who writes what

| File | Written by | Edit directly? |
|---|---|---|
| `_log.yaml` | `litigation-legal:matter-intake`, `litigation-legal:matter-update`, `litigation-legal:matter-close` | Yes, but reflect the change in the matter's `history.md` |
| `matter.md` | `litigation-legal:matter-intake` at intake; appended by `litigation-legal:matter-close` | Yes, for evolving theory / posture notes |
| `history.md` | `litigation-legal:matter-intake` seeds; `litigation-legal:matter-update` and `litigation-legal:matter-close` append | Append-only in practice — treat past entries as record |

## Closed matters

Stay here. Don't delete. `litigation-legal:portfolio-status` filters them from active rollups by default; `litigation-legal:portfolio-status --all` includes them. Closed matters are the training set for portfolio judgment.

## Corrections

If a past history entry was wrong, don't edit it. Append a new entry that references and corrects it. The record of the correction is as important as the correction itself.
