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
| 28088 | Hosted project URL | **PENDING** | isolated GCP project exists; billing/live deployment pending |
| 28090 | Testing instructions | **PENDING FINAL URL + PRIVATE KEY** | draft below; private judge key must be retrieved only after successful bootstrap |
| 28091 | Which Google SDK did you use? | `Agent Development Kit (ADK)` | source + remote ADK construction gate verified; live invocation still pending |
| 28142 | Which Google Cloud Service(s) did you use? | `Cloud Run` | **DO NOT SUBMIT YET**; deployment pending |
| 28092 | Architecture diagram | **PENDING FILE** | canonical source exists in `docs/ARCHITECTURE.md`; final upload must match deployed state |
| 28143 | Which Google AI Models did you use? | `Gemini 3.5 Flash` | configured in source; **DO NOT SUBMIT YET** until live invocation receipt |
| 28106 | Bonus content link | optional / pending | not started |
| 28107 | Bonus social link | optional / pending | not started |

## Latest remote CI evidence

Public `main` commit `1221650385716392336175b59295732867d0be79` passed GitHub Actions run `31802835412`, job `94774629648`, on 2026-08-14. GitHub reports the job `completed / success` and every recorded step completed successfully.

Verified receipts from that run:

- `google-adk==2.7.0` and declared Google Cloud dependencies installed;
- Ruff: PASS;
- strict mypy: PASS (`13 source files`);
- pytest: **34 passed, 1 skipped, 2 warnings**;
- ADK catalog construction test: PASS with installed Google ADK;
- branch-aware coverage: **92.55%** (required >=90%);
- Python compile gate: PASS;
- shell syntax validation for bootstrap/preflight/deploy/smoke/proof-receipt scripts: PASS;
- Flight Recorder JavaScript syntax gate (`node --check`): PASS;
- deterministic synthetic fleet-scale receipt gate: **PASS — 100 agent checkpoints / 14 affected / 86 reused / 1 blocked action**;
- committed-secret regex gate: PASS;
- Docker image build: PASS.

The one skipped test is the opt-in live Google integration test. A skipped live test is not a Gemini/Vertex PASS.

Additional source/regression hardening on current `main` includes:

- protected run/read/mutation APIs using `X-Recovery-Mesh-Judge-Key`;
- live mode fails closed with `503` if the server-side judge secret is absent;
- missing/incorrect client key fails `401` before model execution;
- process-local live model-call budget with pre-provider reservation and fail-closed exhaustion;
- first-bootstrap Secret Manager path for `recovery-mesh-judge-key:1` without printing/committing the value;
- protected production smoke requirement proving unauthenticated run creation returns `401`;
- keyless GitHub Workload Identity Federation deployment design restricted to exact repository ID/owner/`main`;
- non-mutating Google Cloud proof-receipt script.

These are source/test claims only until the Google Cloud bootstrap creates the real secret, WIF provider, Cloud Run revision, and live receipts.

## Google Cloud deployment evidence boundary

Isolated hackathon target created on 2026-08-14:

- Project ID: `evidencebound-rm-c977c1`
- Project number: `457699623691`
- Project name: `EvidenceBound Recovery Mesh`
- Label: `hackathon=all-things-agentic-2026`
- Lifecycle observed: `ACTIVE`

The prior project `vocal-lightning-7dmzd` received a deletion request and was observed as `DELETE_REQUESTED`; it is not a Recovery Mesh deployment target.

Bootstrap now fails closed before API/IAM mutation unless the exact project ID, project number, hackathon label, ACTIVE lifecycle, and enabled billing all match. Billing has not yet been verified enabled, so live Google, Secret Manager runtime state, WIF runtime state, and Cloud Run fields remain pending.

The first bootstrap is designed to create:

- separate `recovery-mesh-runtime` and `recovery-mesh-build` service identities;
- Secret Manager secret `recovery-mesh-judge-key:1`, generated once without printing the value;
- a public judge UI/health endpoint with protected run/read/mutation APIs;
- a bounded live model-call guard (`64` reservations/process by default; explicitly not a billing cap);
- a keyless `recovery-mesh-deployer` + Workload Identity Federation provider restricted to repo ID `1334014784`, owner `moneyparking`, ref `refs/heads/main`.

A manual keyless GitHub Actions deployment workflow is committed at `.github/workflows/deploy-cloud-run.yml`. It can be used only after the owner bootstrap creates the real bounded deployer identity and WIF provider.

## Draft private testing instructions

1. Open the hosted Flight Recorder URL.
2. Enter the private judge access key supplied in this Devpost judge-only field. Do not place this key in public project text/video/screenshots.
3. Start the normal verified workflow. Confirm the execution provider/model shown by the hosted runtime.
4. Inject the visibly labeled `stale_evidence` controlled fault.
5. Confirm the final action changes to `BLOCKED` before recomputation.
6. Inspect the exact blast radius and reusable checkpoints. The proof strip must show `TRUST BREAK → BLAST RADIUS → ACTION BLOCKED → SAFE WORK REUSED` from the same runtime state.
7. Trigger autonomous recovery; do not choose rerun agents manually.
8. Confirm only affected agent checkpoints rerun, unaffected checkpoints remain reused, and the final action resumes only after deterministic re-verification. The proof strip must finish `BRANCH RECOMPUTED → VERIFIED RECOVERY`.
9. Run the repository's 100-agent synthetic scale probe to inspect the deterministic fleet-scale receipt; it is explicitly not a claim of 100 Gemini calls.

The private key itself remains **PENDING** until the live bootstrap creates `recovery-mesh-judge-key:1`. Retrieve it locally from Secret Manager and paste it only into Devpost's private testing-credentials/instructions field; never paste it into chat or GitHub.

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
- [x] Remote GitHub CI / ADK construction / shell / JS / scale receipt / container build
- [x] Protected judge API regression tests
- [x] Process-local live model-call guard regression tests
- [x] Canonical architecture source (`docs/ARCHITECTURE.md`)
- [x] Fortified threat model (`docs/THREAT_MODEL.md`)
- [x] Isolated hackathon GCP project created
- [x] Secret Manager / protected-smoke bootstrap path implemented
- [x] Keyless post-bootstrap deployment workflow prepared
- [x] Non-mutating Google Cloud proof-receipt script prepared
- [x] Flight Recorder six-step judge proof strip wired to runtime state
- [ ] Billing enabled on isolated hackathon project
- [ ] Secret Manager judge key created in real GCP project
- [ ] Live Gemini 3.5+ invocation via Google ADK
- [ ] Google Cloud Cloud Run deployment
- [ ] Protected production smoke PASS (`401` unauthenticated + live recovery)
- [ ] Hosted judge URL
- [ ] Architecture diagram image/file upload
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
- protected judge flow is observed in production;
- architecture diagram is attached;
- required demo video is public and <=4 minutes;
- project description, code, video, diagram, and testing instructions describe the same working system.
