# Judge acceptance gate

Final submission remains blocked until one exact production run proves all applicable items below with real receipts.

- public GitHub repository contains the hackathon code, disclosure, README, reproducible tests, and current green CI;
- Google ADK dependency installs and the ADK agent catalog constructs successfully;
- each live specialist agent is generation-bounded (`temperature=0`, `max_output_tokens=256`) and the configured model is Gemini 3.5+;
- Gemini 3.5+ is invoked with real Google credentials and no deterministic fallback;
- isolated Google Cloud project ID/number/label match the documented hackathon target;
- billing is enabled before bootstrap mutates APIs/IAM;
- Secret Manager contains the dedicated pinned judge secret version and the secret value is absent from source/log receipts;
- public UI/health remains reachable while unauthenticated `POST /api/runs` returns `401` before model execution;
- Cloud Run deploy is live and the `/healthz` execution provider is `google_adk_vertex` with protected judge access enabled;
- Cloud Run revision uses the dedicated runtime service account and bounded process-local live-call guard;
- fresh protected production baseline creates four live ADK agent receipts;
- controlled `stale_evidence` fault invalidates `history_snapshot`;
- exact blast radius blocks `publish_action` and preserves Scout;
- autonomous recovery reruns only Statistician, Skeptic, and Orchestrator;
- recomputed checkpoints are deterministically re-verified;
- `publish_action` resumes only after dependency trust passes;
- duplicate side effects remain suppressed, including concurrent duplicate commits in the process-local ledger test;
- benchmark receipt compares actual full restart and selective recovery paths;
- Flight Recorder production UI shows the six-step causal sequence without fabricated state;
- non-mutating Google Cloud proof receipt identifies the same project, service URL, revision, runtime identity, health provider, and recent request metadata;
- Workload Identity Federation, if claimed, is observed with the exact GitHub repository/owner/`main` restriction and no service-account key;
- architecture diagram matches the deployed design and does not add unverified enterprise services;
- <=4-minute public video shows the same live path and visible Google Cloud proof without exposing the private judge key;
- Devpost fields, repo, hosted URL, architecture file, video, private testing instructions, and stack claims all match the accepted production state.

A deterministic/local PASS, synthetic scale receipt, source-level Secret Manager/WIF configuration, or skipped live integration test cannot substitute for the production evidence above.
