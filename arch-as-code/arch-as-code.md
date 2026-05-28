# Arch-as-Code — Context Summary

## Overview

Strategic-planning workspace for an Architecture-as-Code (AAC) ecosystem at DTCC, the financial-market SIFMU. Markdown-only repo. Outputs are a refined planning brief and a strategic plan that DTCC stakeholders use to scope and fund the AAC program.

## Current State

Two deliverables live on `main`:

- `Arch as Code Plan.md` — refined planning brief (~135 lines).
- `Architecture as Code - Strategic Plan.md` — synthesized strategic plan (~900 lines), 13 sections + 5 appendices.

Decisions baked in: hybrid operating model; Structurizr DSL + Mermaid + PlantUML rendering; Backstage *out of AAC scope* (joint EA + Engineering workstream); 4 Phase-0 bootstrap + 10 Phase-1 MCPs + 8 Phase-1 skills; ADRs in SharePoint Word/PDF (not Confluence); ~$39M 3-yr TCO; Equity C&S pilot Jun–Nov 2026; second-wave = ITP. Phasing anchored to May 2026 kickoff (Phase 0 May 2026 → Phase 3 Sep 2027–Aug 2028).

**The user leads the DA function.** The arch-as-code workspace now hosts both AAC strategic-planning deliverables *and* adjacent workstreams the user runs as DA function lead (training plan, workforce transition, team assessment). Head of architecture is the user's boss/peer who tasks the assessment work.

**Three open PRs:**

- **PR #5 — `da-team-assessment` branch (current focus, late May 2026).** Plan for a confidential assessment of the 14-person DA team, requested by the head of architecture. Primary use: individual performance input. Secondary objective: distinguish true individual signal from program/structural issues showing up as performance complaints. Three tracks — stakeholder survey (breadth), DA self-survey (self vs. external gap + working-conditions read), work-product review + interviews (depth). Plan includes full draft instruments for both surveys, anonymity model (anonymous-to-respondent, named-DAs), coverage routing, a per-development-area meta-attribution question (Q8) that is the key mechanism for separating individual from structural, fielding timeline targeting an interim read on Wed June 3, and an analysis approach that outputs a recommended-intervention table split by individual vs. program-level owners.
- **PR #4 — `training-plan` branch.** Leadership-ready ITA Training Plan covering the five offsite initiatives (AAC, Frontline Engineering Consolidation, Backstage, Technology Radar, Governance) in three formats: full plan markdown, Word (pandoc-generated), and a 10-slide briefing PowerPoint. Y1 budget ~$80k steady-state, ~$50–55k 2026 actuals (revised down from $100k after applying DTCC's AWS Enterprise customer benefits to the Backstage training line). Three decisions requested at leadership review: budget approval, initiative-led ownership endorsement (with Phase 1 exit checkpoint for a central training PM), and time-allocation policy.
- **PR #3 — `workforce-transition-docs` branch.** Three solution-architect transition documents extending Strategic Plan R9 — one-pager, Phase 0 charter (deliverables, RACI, role skeletons, FAQ), and a Q&A doc capturing the leader's ten questions with plan-grounded answers. Awaiting leader / AAC Platform Lead / HR / Backstage workstream-lead review.

**New strategic thread (May 2026):** **Frontline Engineering** — converging the Domain Architecture and Service Architecture teams into one role organized around the modernization-project lifecycle in partnership with application development. The user is preparing a presentation to the broader architecture community. Recommended framing: *Master Builder Returns* (elevation), *Stereo Vision* (convergence = depth), *Pilot in the Cockpit* (full-lifecycle partnership), grounded in Team Topologies / platform engineering / shift-along. Closely related to the PR #3 workforce-transition docs (same change, architecture-community angle). Deck not yet built.

## Next Steps

**DA team assessment (this week):**
1. Review PR #5 and lock the seven open decisions in §10 (survey tool, distribution list, manager role bucket, pre-brief list, invitation voice, domain list, DA-name format).
2. Fri May 29 — pre-brief 3–5 domain leaders; send DA self-survey to the 14 DAs Friday afternoon.
3. Mon Jun 1 — launch stakeholder survey. Reminder Tue AM, soft cutoff Tue EOD.
4. Wed Jun 3 PM — deliver interim read to head of architecture (per-DA pages, team aggregate, individual-vs-structural split, recommended-intervention table).
5. Jun 4–12 — surveys stay open for late responses; interviews continue; updated read end of week 2.

**Other open threads:**
6. Build the Frontline Engineering deck (speaker notes or pandoc starter `.pptx` offered, neither done).
7. ITA leadership review of PR #4 — three decisions: budget approval, initiative-led ownership endorsement, time-allocation policy.
8. Apply DTCC branding to the PR #4 briefing PPT in PowerPoint manually.
9. AWS account team confirmation of Enterprise benefits assumption for the ~$5k Backstage training reserve.
10. Land PR #3 (workforce-transition docs) after pending reviews complete.
11. After PRs land, start **Pass 2** — Reference Architecture and How-To Guide using locked decisions as inputs. Major outstanding AAC deliverable per project CLAUDE.md.
12. Coursera-by-role curation pending org catalog access — candidate list in Appendix A of `Training Plan.md`.
