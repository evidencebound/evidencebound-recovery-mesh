# Judge video capture

The workflow `.github/workflows/judge-video-capture.yml` performs a one-shot protected browser capture of the live judge flow for submission editing. It obtains the existing judge key through the bounded deployer identity, masks it before use, never writes it into screenshots or artifacts, and uploads only sanitized screenshots plus a non-secret capture receipt.

This workflow does not modify the Recovery Mesh runtime, Cloud Run revision, Gemini/ADK configuration, judge API, or trust semantics.
