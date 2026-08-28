# Video V2 Proof Package

Status: **LOCAL ASSEMBLY VERIFIED / PUBLICATION PENDING**

This document records the final Proof-of-Action V2 evidence package assembled on 2026-08-28. It does not claim a public YouTube/Vimeo publication until a public URL is created and read back.

## Final master

- Duration: `75.080 s`
- Resolution: `1920x1080`
- Frame rate: `25 fps`
- Upload master: H.264 MP4
- Evidence master: VP8 WebM
- Audio: none
- English SRT supplied separately
- Final frame count: `1877`

SHA-256:

```text
MP4  82ea4a9b7164c6ea50a3792114ff3c9e9337af3d4d5df4363b61d2e49cb17c66
WebM aa55e91c86cdd81cedadd1789fc0f6f1a07fcc851f07da82abbb034064a64200
```

## Continuous Proof of Action

The centerpiece is the complete source segment `video-v2-live-segment.webm`:

```text
duration:      24.080 s
frames:        602
position:      20.000 .. 44.080 in the assembled master
capture run:   run-06fdaf68fdff
source SHA256: c18a372f211a3f50006256f2fc41ba5b5e3a84dd1409ca450c344d9ab38025c5
```

Compliance checks:

```text
internal cuts:          NONE
internal overlays:      NONE
speed changes:          NONE
decoded frame equality: PASS — 602 / 602 source frames match the joined WebM
```

The source artifact ZIP was preserved before expiry and independently matched its GitHub artifact digest:

```text
sha256:de20f3595ab1da1eae43cdcbca842290dc238d98908c754a3df68866acf440db
```

## Capture-run receipt

The live capture run is kept separate from the newer production acceptance receipt:

```text
run:                run-06fdaf68fdff
provider:           google_adk_vertex
model:              gemini-3.5-flash
full restart:       4 model calls / 1744 input tokens
selective recovery: 3 model calls / 1366 input tokens
saved in this run:  1 model call / 378 input tokens
unaffected work:    Scout REUSED
final state:        VERIFIED
```

These are per-run controlled measurements, not general savings claims.

## Current production acceptance proof

Separate evidence cards use the current production receipt from workflow `32817763402`:

```text
revision:           evidencebound-recovery-mesh-00006-tc4
run:                run-6d1427ccb2ca
provider/model:     google_adk_vertex / gemini-3.5-flash
live agents:        4
trust break:        publish_action BLOCKED
reuse:              Scout REUSED
repair set:         3 rerun / 1 reused
model calls:        4 -> 3
input tokens:       1739 -> 1388
final action:       VERIFIED
unauth POST:        401
```

The Google Cloud proof card also shows the canonical `.run.app` service URL and states that its data comes from the authenticated `gcloud` + live `/health` acceptance receipt. It is **not** represented as a Google Cloud Console screenshot.

## Google Agent Registry proof

Production control-plane receipt from workflow `31871557186`:

```text
AGENT_REGISTRY=PASS operation=created location=global transport=rest-v1 discovery=service-registry-resource
AGENT_REGISTRY_SERVICE=projects/evidencebound-rm-c977c1/locations/global/services/recovery-mesh-fleet
AGENT_REGISTRY_AGENT=projects/457699623691/locations/global/agents/agentregistry-00000000-0000-0000-a7f5-b9837959f789
AGENT_REGISTRY_INTERFACE=https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app
AGENT_REGISTRY_DISCOVERY=PASS
```

This is an observed production registration receipt. It is not described as a fresh 2026-08-28 registration and does not grant Registry authority over deterministic Recovery Mesh trust decisions.

## Publication gate

Do not replace the Devpost V1 URL until all three conditions are true:

1. V2 MP4 is publicly available on YouTube or Vimeo;
2. the public URL resolves without owner authentication;
3. Devpost readback shows that exact V2 URL.

Until then, the existing public V1 remains the submission video of record.
