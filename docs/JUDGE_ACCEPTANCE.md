# Judge acceptance gate

Final submission remains blocked until one exact production run proves all items below with real receipts.

- public GitHub repository contains the hackathon code, disclosure, README, reproducible tests, and current CI;
- Google ADK dependency installs and the ADK agent catalog constructs successfully;
- Gemini 3.5+ is invoked with real Google credentials and no deterministic fallback;
- Cloud Run deploy is live and the `/healthz` execution provider is `google_adk_vertex`;
- fresh production baseline creates four live ADK agent receipts;
- controlled `stale_evidence` fault invalidates `history_snapshot`;
- exact blast radius blocks `publish_action` and preserves Scout;
- autonomous recovery reruns only Statistician, Skeptic, and Orchestrator;
- recomputed checkpoints are deterministically re-verified;
- `publish_action` resumes only after dependency trust passes;
- benchmark receipt compares actual full restart and selective recovery paths;
- Flight Recorder production UI shows the causal sequence without fabricated state;
- architecture diagram matches the deployed design;
- <=4-minute public video shows the same live path and visible Google Cloud proof;
- Devpost fields, repo, hosted URL, architecture file, video, and stack claims all match the accepted production state.
