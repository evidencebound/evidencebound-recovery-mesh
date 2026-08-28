const durableState = { provider: 'unknown', durable: false };

function setDurableText(selector, text, tone='neutral') {
  const node = qs(selector);
  if (!node) return;
  node.textContent = text;
  node.className = `durable-value ${tone}`;
}

async function loadPersistenceHealth() {
  try {
    const response = await fetch('/health');
    if (!response.ok) throw new Error(`health ${response.status}`);
    const health = await response.json();
    const persistence = health.persistence || {};
    durableState.provider = persistence.provider || 'unknown';
    durableState.durable = Boolean(persistence.durable);
    setDurableText(
      '#persistenceProvider',
      durableState.durable ? durableState.provider.toUpperCase() : `${durableState.provider.toUpperCase()} · EPHEMERAL`,
      durableState.durable ? 'ok' : 'neutral'
    );
  } catch (error) {
    console.error('persistence health failed', error);
    setDurableText('#persistenceProvider', 'UNAVAILABLE', 'warn');
  }
}

async function renderDurableProof(run) {
  if (!run?.run_id) return;
  setDurableText('#persistedState', 'VERIFYING…', 'neutral');
  setDurableText(
    '#actionReceiptState',
    run.active_blast_radius ? 'ACTION BLOCKED · CHECKING RECEIPT' : 'CHECKING RECEIPT',
    run.active_blast_radius ? 'blocked' : 'neutral'
  );
  setDurableText('#rehydrationState', 'VERIFYING TRUST BINDINGS…', 'neutral');

  try {
    const durable = await request(`/api/durable-runs/${run.run_id}`);
    const snapshot = durable.snapshot || {};
    const receipt = durable.action_receipt || null;
    const rehydration = durable.rehydration || {};

    setDurableText(
      '#persistedState',
      snapshot.run_id === run.run_id ? 'PERSISTED · SAME RUN_ID' : 'PERSISTENCE MISMATCH',
      snapshot.run_id === run.run_id ? 'ok' : 'warn'
    );

    if (run.active_blast_radius && !receipt) {
      setDurableText('#actionReceiptState', 'ACTION BLOCKED · NO RECEIPT', 'blocked');
    } else if (receipt) {
      const suffix = receipt.duplicate_suppressed ? ' · DUPLICATE SUPPRESSED' : '';
      setDurableText('#actionReceiptState', `RECEIPT COMMITTED${suffix}`, 'ok');
    } else {
      setDurableText('#actionReceiptState', 'NO ACTION RECEIPT', 'neutral');
    }

    if (rehydration.trusted) {
      setDurableText('#rehydrationState', 'REHYDRATED · TRUST VALIDATED', 'ok');
    } else {
      const count = Array.isArray(rehydration.failures) ? rehydration.failures.length : 0;
      setDurableText('#rehydrationState', `FAIL-CLOSED · ${count} TRUST FAILURE${count === 1 ? '' : 'S'}`, 'warn');
    }
  } catch (error) {
    if (state.accessRequired && !judgeKey()) {
      setDurableText('#persistedState', 'LOCKED · JUDGE KEY REQUIRED', 'neutral');
      setDurableText('#actionReceiptState', 'LOCKED', 'neutral');
      setDurableText('#rehydrationState', 'LOCKED', 'neutral');
      return;
    }
    console.error('durable proof readback failed', error);
    setDurableText('#persistedState', 'READBACK FAILED', 'warn');
    setDurableText('#actionReceiptState', 'UNVERIFIED', 'warn');
    setDurableText('#rehydrationState', 'UNVERIFIED', 'warn');
  }
}

const renderWithoutDurableProof = render;
render = function renderWithDurableProof(run) {
  renderWithoutDurableProof(run);
  void renderDurableProof(run);
};

void loadPersistenceHealth();
