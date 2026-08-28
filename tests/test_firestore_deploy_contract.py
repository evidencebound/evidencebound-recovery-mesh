from pathlib import Path


def test_firestore_bootstrap_is_idempotent_and_least_privilege() -> None:
    script = Path("scripts/gcp-firestore-bootstrap.sh")
    assert script.exists(), "Firestore production bootstrap must exist"
    text = script.read_text(encoding="utf-8")

    assert "firestore.googleapis.com" in text
    assert "gcloud firestore databases describe" in text
    assert "'(default)'" in text or '"(default)"' in text
    assert "gcloud firestore databases create" in text
    assert "--edition=standard" in text
    assert "--type=firestore-native" in text
    assert "roles/datastore.user" in text
    assert "recovery-mesh-runtime@" in text
    assert "FIRESTORE_DATABASE=READY" in text
    assert "FIRESTORE_RUNTIME_IAM=READY" in text


def test_cloud_run_deploy_bootstraps_and_enables_firestore_mode() -> None:
    deploy = Path("scripts/deploy-cloud-run.sh").read_text(encoding="utf-8")

    assert "gcp-firestore-bootstrap.sh" in deploy
    assert "RECOVERY_MESH_PERSISTENCE_MODE=firestore" in deploy


def test_owner_bootstrap_provisions_firestore_without_broadening_ci_deployer() -> None:
    owner = Path("scripts/gcp-owner-bootstrap.sh").read_text(encoding="utf-8")
    deploy_wif = Path("scripts/gcp-bootstrap-deploy-wif.sh").read_text(encoding="utf-8")

    assert "firestore.googleapis.com" in owner
    assert "RECOVERY_MESH_FIRESTORE_BOOTSTRAP_MODE=provision" in owner
    assert "gcp-firestore-bootstrap.sh" in owner
    assert "roles/datastore.viewer" in owner
    assert "roles/datastore.viewer" in deploy_wif
    assert "roles/datastore.owner" not in deploy_wif
    assert "roles/resourcemanager.projectIamAdmin" not in deploy_wif


def test_ci_validates_firestore_bootstrap_shell_and_durable_javascript() -> None:
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "scripts/gcp-firestore-bootstrap.sh" in workflow
    assert "node --check static/durable.js" in workflow
