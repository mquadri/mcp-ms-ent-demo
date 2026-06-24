# Skills UI Design Decisions

Date: 2026-05-18  
Module: TalentIQ Skills Updater UI  
Status: Draft for development-team review

## 1. Purpose

This document captures design decisions and open questions for the new Skills Updater UI stack.
It converts architecture and UX review feedback into a decision-oriented format the team can close in sprint planning.

## 2. Decision Status Legend

- Proposed: recommendation exists, team has not approved.
- Decided: approved by product/design/engineering.
- Deferred: intentionally postponed.
- Blocked: waiting on dependency.

## 3. Priority Findings (from UI review)

1. Information density is high and hierarchy is weak for fast decision-making.
2. Primary call-to-action is unclear on key screens.
3. Explainability is not explicit enough at decision points.
4. Color and tier semantics are inconsistent across screens.
5. Notification flow may cause fatigue without suppression controls.
6. Accessibility risks exist (text size, contrast, dense layout).
7. Empty, stale, conflict, and error states are not fully defined.
8. Role-based UX is not explicit enough by persona.

## 4. Design Decision Register

| ID | Topic | Decision to Make | Options | Recommended Position | Owner | Due | Status |
|---|---|---|---|---|---|---|---|
| UI-01 | Primary action path | What is the main CTA per screen? | A: Multiple equal CTAs, B: Single primary CTA + secondary actions | B | Product + Design | TBD | Proposed |
| UI-02 | Information hierarchy | How should dense content be structured? | A: Single dense page, B: Progressive disclosure with drill-down | B | Design | TBD | Proposed |
| UI-03 | Score explainability | How much evidence appears inline? | A: Score only, B: Score + top evidence + source + recency + confidence | B | Product + Design | TBD | Proposed |
| UI-04 | Tier/color semantics | How to standardize visual meaning? | A: Per-screen custom semantics, B: Shared semantic tokens and labels | B | Design System | TBD | Proposed |
| UI-05 | Notification frequency | What reminder cadence is allowed? | A: Fixed sequence, B: policy-based with suppression and snooze | B | Product | TBD | Proposed |
| UI-06 | Role-based views | Should all roles see same UI? | A: Single view for all, B: role-adaptive layouts/actions | B | Product + Security | TBD | Proposed |
| UI-07 | Conflict states | How to show data disagreements? | A: Silent precedence, B: explicit conflict banner with source comparison | B | Product + UX | TBD | Proposed |
| UI-08 | Error handling | How to surface write-back failures? | A: generic toast, B: actionable inline state + retry + audit link | B | UX + Engineering | TBD | Proposed |
| UI-09 | Accessibility baseline | What standard applies? | A: best effort, B: WCAG 2.1 AA for key workflows | B | UX + QA | TBD | Proposed |
| UI-10 | Responsive strategy | What breakpoints and behaviors? | A: desktop-first only, B: desktop + laptop + tablet tested layouts | B | Frontend | TBD | Proposed |
| UI-11 | Rejection memory UX | How to handle rejected suggestions? | A: ignore history, B: persist rejection memory and explanation | B | Product + Engineering | TBD | Proposed |
| UI-12 | Metrics visibility | Should users see policy outcomes? | A: internal only, B: expose key acceptance/rejection/freshness metrics by role | B | Product | TBD | Proposed |

## 5. Screen-Specific Questions To Close

## 5.1 New Signals and Data Sources

- What is the exact user task on this page: understand trust sources, tune policy, or approve signal usage?
- Which sources are active vs pilot vs disabled, and how is that shown?
- Is each source weighted globally, by role family, or by geography/business unit?
- What evidence drill-down is required per source entry?
- How do users see freshness and data quality per source?

## 5.2 Scoring Framework

- Are tier weights fixed or configurable by policy version?
- How are non-developer profiles scored fairly when developer signals are absent?
- How are recency decay rules explained in plain language?
- What edge-case rules are visible to users and what remains admin-only?
- Should users see final score only, or score plus component-level contributions?

## 5.3 Notifications Workflow

- What maximum number of reminders can one user receive per cycle?
- What are stop conditions and are they visible in the user UI?
- Can users snooze, delegate, or opt down notification channels?
- How are manager escalations justified and traceable?
- How are repeated rejects remembered to prevent re-spam?

## 6. UX Principles for This Module

- One primary action per screen.
- Evidence before recommendation acceptance.
- Progressive disclosure for dense technical detail.
- Consistent semantic design tokens across all pages.
- Every score/recommendation must be explainable and auditable.
- Every workflow must define empty, stale, conflict, and failure states.
- Role-aware interaction depth (employee vs manager vs approver vs admin).

## 7. Minimum State Catalog (must be designed)

- Loading
- Empty profile
- No signal available
- Stale profile
- Source conflict
- Approval pending
- Write-back success
- Write-back failed
- Suppressed notification
- Permission denied

## 8. Accessibility and Usability Acceptance Criteria

- WCAG 2.1 AA contrast on all critical text and controls.
- Keyboard-only completion for approve/reject/review flows.
- Non-color indicator for all severity/tier states.
- Readable density at standard laptop resolutions.
- Touch targets and spacing validated for tablet breakpoints.

## 9. Product Metrics (design effectiveness)

- Suggestion acceptance rate
- Suggestion rejection rate
- Median decision time per suggestion
- Notification response rate
- Stale-profile recovery rate
- Drill-down usage on explainability panel
- Write-back failure recovery rate

## 10. Meeting Checklist (fill live)

| Item | Decision | Owner | Date | Notes |
|---|---|---|---|---|
| Primary CTA per screen |  |  |  |  |
| Explainability standard |  |  |  |  |
| Weight/tier configurability |  |  |  |  |
| Notification suppression policy |  |  |  |  |
| Role-specific UI behavior |  |  |  |  |
| Conflict-state UX |  |  |  |  |
| Accessibility baseline signoff |  |  |  |  |
| MVP breakpoints |  |  |  |  |
| State catalog completion |  |  |  |  |
| Instrumentation events |  |  |  |  |

## 11. Immediate Next Actions

1. Run a 60-minute design decision workshop and close UI-01 to UI-06.
2. Create Figma variants for high-density vs progressive-disclosure layouts.
3. Define policy-config schema for scoring weights and notification cadence.
4. Produce state/error wireframes for all critical flows.
5. Add analytics event spec before implementation freeze.
