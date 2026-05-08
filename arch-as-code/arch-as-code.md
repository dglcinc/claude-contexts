# Arch-as-Code — Context Summary

## Overview

Strategic-planning workspace for an Architecture-as-Code (AAC) ecosystem at DTCC, the financial-market SIFMU. Markdown-only repo. Outputs are a refined planning brief and a strategic plan that DTCC stakeholders use to scope and fund the AAC program.

## Current State

Two deliverables live on `main`:

- `Arch as Code Plan.md` — refined planning brief (~135 lines). Captures decided constraints, resolved open questions, and explicit timing constraints (90-day milestone, year-end deliverable).
- `Architecture as Code - Strategic Plan.md` — synthesized strategic plan (~900 lines). 13-section executive narrative + 5 appendices.

Decisions baked in: hybrid operating model; Structurizr DSL + Mermaid + PlantUML rendering; Backstage *out of AAC scope* (joint EA + Engineering workstream); 4 Phase-0 bootstrap + 10 Phase-1 MCPs + 8 Phase-1 skills, with maturity ladder; ADRs are in SharePoint Word/PDF (not Confluence); ~$39M 3-yr TCO; Equity C&S pilot Jun–Nov 2026; second-wave = ITP.

Phasing anchored to May 2026 kickoff: Phase 0 May 2026 → Phase 1 Jun–Nov 2026 → Phase 2 Dec 2026–Aug 2027 → Phase 3 Sep 2027–Aug 2028.

**Open work — branch `workforce-transition-docs` (PR #3):** three solution-architect transition documents extending Strategic Plan R9 — a one-pager for the architecture leader, a Phase 0 workstream charter (deliverables, RACI, role-definition skeletons, FAQ), and a Q&A doc capturing the leader's ten questions with plan-grounded answers. Awaiting leader review.

## Next Steps

1. Land PR #3 (workforce-transition docs) after leader / AAC Platform Lead / HR / Backstage workstream-lead review.
2. **Pass 2** — produce the Reference Architecture and How-To Guide using the now-locked tooling/operating-model decisions as inputs. Originally agreed as a separate downstream pass.
3. Optional re-run of `/ultraplan` against the mature brief.
4. Optional refresh of budget and risk register once DTCC's actual rate-card and Kiro enterprise pricing are confirmed.
