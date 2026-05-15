# Arch-as-Code — Context Summary

## Overview

Strategic-planning workspace for an Architecture-as-Code (AAC) ecosystem at DTCC, the financial-market SIFMU. Markdown-only repo. Outputs are a refined planning brief and a strategic plan that DTCC stakeholders use to scope and fund the AAC program.

## Current State

Two deliverables live on `main`:

- `Arch as Code Plan.md` — refined planning brief (~135 lines).
- `Architecture as Code - Strategic Plan.md` — synthesized strategic plan (~900 lines), 13 sections + 5 appendices.

Decisions baked in: hybrid operating model; Structurizr DSL + Mermaid + PlantUML rendering; Backstage *out of AAC scope* (joint EA + Engineering workstream); 4 Phase-0 bootstrap + 10 Phase-1 MCPs + 8 Phase-1 skills; ADRs in SharePoint Word/PDF (not Confluence); ~$39M 3-yr TCO; Equity C&S pilot Jun–Nov 2026; second-wave = ITP. Phasing anchored to May 2026 kickoff (Phase 0 May 2026 → Phase 3 Sep 2027–Aug 2028).

**Two open PRs awaiting leadership review:**

- **PR #4 — `training-plan` branch (current focus, May 2026).** Leadership-ready ITA Training Plan covering the five offsite initiatives (AAC, Frontline Engineering Consolidation, Backstage, Technology Radar, Governance) in three formats: full plan markdown, Word (pandoc-generated), and a 10-slide briefing PowerPoint. Y1 budget ~$80k steady-state, ~$50–55k 2026 actuals (revised down from $100k after applying DTCC's AWS Enterprise customer benefits to the Backstage training line). Working planning input (`Training Plan.md`) with sources matrix and Coursera candidate appendix retained alongside the deliverables. Three decisions requested at leadership review: budget approval, initiative-led ownership endorsement (with Phase 1 exit checkpoint for a central training PM), and time-allocation policy.
- **PR #3 — `workforce-transition-docs` branch.** Three solution-architect transition documents extending Strategic Plan R9 — one-pager, Phase 0 charter (deliverables, RACI, role skeletons, FAQ), and a Q&A doc capturing the leader's ten questions with plan-grounded answers. Awaiting leader / AAC Platform Lead / HR / Backstage workstream-lead review from the prior session.

## Next Steps

1. ITA leadership review of PR #4 — three decisions: budget approval (~$80k steady-state, $50–55k 2026 actuals), initiative-led ownership endorsement, and time-allocation policy for live training vs. self-directed.
2. Apply DTCC branding to the briefing PPT in PowerPoint manually (pandoc output is plain theme; user opted for manual branding over python-pptx automation).
3. AWS account team confirmation of Enterprise benefits assumption for the ~$5k Backstage training reserve.
4. Land PR #3 (workforce-transition docs) after pending reviews complete.
5. After PRs land, start **Pass 2** — Reference Architecture and How-To Guide using locked decisions as inputs. Major outstanding deliverable per project CLAUDE.md.
6. Coursera-by-role curation pending org catalog access — candidate list in Appendix A of `Training Plan.md`.
