# FRP v3.2.0 Release Notes

## Release Identity

| Field | Value |
|---|---|
| Version | `FRP v3.2.0` |
| Milestone | `M30 — Reproducibility, Qualification, and Archival Release Closure` |
| Source boundary | `ff3dd434da5dcbd9e8fa62444f658ed4c495b540` |
| Qualification status | `PASS` |

## Closure Surface

FRP v3.2.0 closes the M17 through M30 progression with:

- `13` completed milestone evidence records;
- `124` indexed schema definitions including M30 schemas;
- `109` immutable M18 through M29 canonical artifacts;
- `40` indexed workflow definitions including the M30 workflow;
- `20` qualification-manifest records;
- complete SHA-256 digest inventory;
- deterministic clean-environment reproduction;
- deterministic archival release-package construction and verification;
- current-state repository alignment;
- preserved historical release records.

## Immutable Processor Boundary

Balanced ternary core:

`-1/0/1`

Active neutral state:

`0`

Temporal scheduler modes:

`1/7` and `7/1`

Separate service scheduler mode:

`free`

## Observatory Boundary

The existing `FRP-Trace-Observatory` scaffold remains a separate downstream
repository. FRP publishes immutable bytes through the one-way read-only
boundary. M30 introduces no downstream source dependency or writeback path.
