# Prize Audit Documentation Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove stale judge-facing documentation after the final production acceptance without changing runtime behavior or expanding claims.

**Architecture:** Documentation-only cleanup. Canonical current facts remain README, final preflight, public Devpost submission, Cloud Run receipts, Agent Registry receipts, and final video receipt. Historical planning/runbook documents are either updated to current state or clearly marked historical so judges cannot mistake obsolete pending gates for the current submission.

**Tech Stack:** Markdown, GitHub Actions CI.

**Spec:** Final prize audit performed against current All Things Agentic rules and repository state on 2026-08-22.

## Global Constraints

- Do not modify application/runtime code, Cloud Run configuration, Gemini/ADK behavior, IAM, secrets, or Devpost runtime fields.
- Do not add unverified Google services or persistence claims.
- Keep durable multi-week context, Firestore, BigQuery export, Agent Runtime, Memory Bank, and Model Armor as explicit non-claims.
- Current health endpoint is `/health`, never `/healthz`.
- Current production revision is `evidencebound-recovery-mesh-00005-82k`.
- Current final public video is `https://youtu.be/AExuVCC-m7o`.
- Current submission type is `Team of individuals`; invited teammate acceptance remains owner-visible until confirmed.

---

### Task 1: Update current submission matrix

**Files:**
- Modify: `docs/DEVPOST_SUBMISSION_MATRIX.md`

- [ ] Replace obsolete draft/pending statuses with verified final submission state.
- [ ] Preserve explicit non-claims and team-roster caveat.
- [ ] Record current hosted URL, video, Agent Registry, and production receipts.

### Task 2: Update production deployment and acceptance docs

**Files:**
- Modify: `docs/GCP_DEPLOYMENT_TARGET.md`
- Modify: `docs/JUDGE_ACCEPTANCE.md`
- Modify: `docs/THREAT_MODEL.md`

- [ ] Replace obsolete billing/deployment-pending language with verified production state.
- [ ] Replace every stale `/healthz` reference with `/health`.
- [ ] Keep Secret Manager, WIF, fail-closed API, bounded model-call guard, and current limitations accurate.

### Task 3: Mark historical operational documents clearly

**Files:**
- Modify: `docs/FORTIFIED_TRACK_PLAN.md`
- Modify: `docs/OWNER_RETURN_RUNBOOK.md`

- [ ] Add a prominent historical-status banner and current-state pointer.
- [ ] Update completed Gate B / Agent Registry status.
- [ ] Preserve Gate C durable-state limitation as not implemented.
- [ ] Remove language that could imply the live submission is still blocked.

### Task 4: Verify documentation consistency

- [ ] Confirm no current judge-facing document claims production is pending.
- [ ] Confirm no stale `/healthz` remains in active docs.
- [ ] Confirm current URLs, revision, model, ADK version, Agent Registry receipt, video URL, and non-claims match README/preflight.
- [ ] Open a PR and run the repository CI.
- [ ] Merge only after CI succeeds.
