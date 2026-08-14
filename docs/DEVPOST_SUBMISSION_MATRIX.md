# Devpost Submission Matrix — All Things Agentic Hackathon 2026

Canonical project: **EvidenceBound Recovery Mesh**  
Category: **Fortified Enterprise Fleet**  
Project start date: **08-14-26**  
Devpost project: `evidencebound-recovery-mesh`  
Submission draft ID: `1136853`

> Rule: do not fill a field as implemented/used until the corresponding runtime gate is verified.

## Required submission fields

| Field ID | Devpost field | Intended answer | Current evidence status |
|---:|---|---|---|
| 28083 | Submitter Type | `Individuals` | READY |
| 28084 | Submitter country of residence | `Ukraine` | READY |
| 28085 | Which Category are you submitting to? | `Fortified Enterprise Fleet` | READY |
| 28086 | Organization name | `N/A — individual submission` | READY |
| 28087 | What date did you start this project? | `08-14-26` | READY; git history begins in submission period |
| 28141 | URL to public/private code repo | `https://github.com/moneyparking/evidencebound-recovery-mesh` | READY; public repository created |
| 28089 | Reproducible Testing instructions in README? | `Yes` | READY; remote CI verified on public `main` |
| 28088 | Hosted project URL | **PENDING** | Cloud Run not yet deployed |
| 28090 | Testing instructions | **PENDING FINAL URL** | draft below |
| 28091 | Which Google SDK did you use? | `Agent Development Kit (ADK)` | source + remote ADK construction gate verified; live invocation still pending |
| 28142 | Which Google Cloud Service(s) did you use? | `Cloud Run` | **DO NOT SUBMIT YET**; deployment pending |
| 28092 | Architecture diagram | **PENDING FILE** | required upload |
| 28143 | Which Google AI Models did you use? | `Gemini 3.5 Flash` | configured in source; **DO NOT SUBMIT YET** until live invocation receipt |
| 28106 | Bonus content link | optional / pending | not started |
| 28107 | Bonus social link | optional / pending | not started |

## Remote CI evidence

Public `main` commit `b5c1568f208ad4f7e435a9497f34a7e5696ae4cd` passed GitHub Actions run `31791061902` on 2026-08-14:

- `google-adk==2.7.0` and Google Cloud dependencies installed from the declared package;
- Ruff: PASS;
- strict mypy: PASS (`13 source files`);
- pytest: **28 passed, 1 skipped**;
- ADK catalog construction test: PASS with installed Google ADK;
- branch-aware coverage: **91.91%** (required >=90%);
- Python compile gate: PASS;
- committed-secret regex gate: PASS;
- Docker image build: PASS.

The one skipped test is the opt-in live Google integration test. A skipped live test is not a Gemini/Vertex PASS.

## Draft private testing instructions

1. Open the hosted Flight Recorder URL.
2. Run the normal verified workflow.
3. Inject the visibly labeled `stale_evidence` controlled fault.
4. Confirm the final action changes to `BLOCKED` before recomputation.
5. Inspect the exact blast radius and the reusable checkpoints.
6. Trigger autonomous recovery; do not choose rerun agents manually.
7. Confirm only affected agent checkpoints rerun, unaffected checkpoints remain reused, and the final action resumes only after deterministic re-verification.
8. Run the 100-agent synthetic scale probe from the repository to inspect the deterministic fleet-scale receipt; it is not a claim of 100 Gemini calls.

## Required deliverables

- [x] Project name and tagline
- [x] Devpost project draft created
- [x] Category locked: Fortified Enterprise Fleet
- [x] New-project / pre-existing-work disclosure in repository
- [x] Local deterministic Trust Graph / recovery core
- [x] Controlled trust-break scenarios
- [x] Fail-closed action gate and idempotency tests
- [x] 100 synthetic agent-checkpoint scale probe
- [x] Reproducible local README instructions
- [x] Public GitHub repository URL
- [x] Remote GitHub CI / ADK construction / container build
- [ ] Live Gemini 3.5+ invocation via Google ADK
- [ ] Google Cloud Cloud Run deployment
- [ ] Hosted judge URL
- [ ] Architecture diagram upload
- [ ] <=4 minute public YouTube/Vimeo demo with visible Google Cloud proof
- [ ] Final Devpost submission

## Google Cloud credits

Official hackathon path: existing Google Cloud account may request **$150 Google Cloud credits**.
The request is an external Google Form rather than a Devpost submission field.

Current state: **REQUESTED — APPROVAL PENDING**.

Evidence: the credits form was submitted on 2026-08-14 and the connected Gmail account received the Google Forms response receipt. Do not claim credits approved or redeemed until a later official approval/code message is observed.

Official deadline from the current rules: **August 28, 2026 at 12:00 PM PT, or while supplies last**. Review may take up to **72 business hours** and credits are not guaranteed.

## Stop condition before final submission

Do not call Devpost `submit_project` until all required claims are backed by current evidence, especially:

- public repo exists and is judge-accessible;
- README reproduces the submitted system;
- live ADK + Gemini execution is observed;
- Cloud Run deployment is observed;
- architecture diagram is attached;
- required demo video is public and <=4 minutes;
- project description, code, video, diagram, and testing instructions describe the same working system.
