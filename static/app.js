const state = { run: null, accessRequired: false, pendingAutorun: null };
const graphOrder = {
  fixture_snapshot: [1,1], history_snapshot: [1,2], policy_rules: [1,3],
  statistician: [2,1], scout: [2,3], skeptic: [3,2], orchestrator: [4,2], publish_action: [5,2]
};
const qs = (s) => document.querySelector(s);
const qsa = (s) => [...document.querySelectorAll(s)];
const judgeKey = () => sessionStorage.getItem('recoveryMeshJudgeKey') || '';
const AUTORUN_STAGE_HOLDS_MS = {baseline: 1800, incident: 3200, recovered: 1200};

async function holdAutorunStage(stage) {
  const delayMs = AUTORUN_STAGE_HOLDS_MS[stage] || 0;
  if (!delayMs) return;
  await new Promise(resolve => setTimeout(resolve, delayMs));
}

function updateAccessUi(status) {
  const gate = qs('#accessGate');
  const pill = qs('#accessState');
  if (!state.accessRequired) {
    gate.hidden = true;
    qs('#startRun').disabled = false;
    return;
  }
  gate.hidden = false;
  const hasKey = Boolean(judgeKey());
  qs('#startRun').disabled = !hasKey;
  pill.textContent = status || (hasKey ? 'KEY STORED' : 'LOCKED');
  pill.className = 'pill ' + (hasKey && status !== 'REJECTED' ? 'ok' : 'neutral');
}

async function request(path, opts={}) {
  const headers = {'Content-Type':'application/json'};
  const key = judgeKey();
  if (key) headers['X-Recovery-Mesh-Judge-Key'] = key;
  const r = await fetch(path, {method: opts.method || 'GET', headers});
  if (!r.ok) {
    if (r.status === 401) updateAccessUi('REJECTED');
    let detail = `${r.status}`;
    try { detail = (await r.json()).detail || detail; } catch (_) { /* keep status */ }
    throw new Error(detail);
  }
  return r.json();
}

async function loadHealth() {
  const r = await fetch('/health');
  if (!r.ok) throw new Error(`health ${r.status}`);
  const health = await r.json();
  state.accessRequired = Boolean(health.judge_access_required);
  const execution = health.execution || {};
  const provider = execution.provider || 'unknown';
  const model = execution.model ? ` · ${execution.model}` : '';
  qs('#executionProvider').textContent = `${provider}${model}`.toUpperCase();
  qs('#executionProvider').className = 'pill ' + (execution.live_google ? 'ok' : 'neutral');
  updateAccessUi();
}

function counts(run) {
  const result = {VERIFIED:0, INVALIDATED:0, RECOMPUTE:0, BLOCKED:0};
  run.checkpoints.forEach(c => result[c.status]++);
  return result;
}

function setProofStep(key, className, meta) {
  const node = qs(`[data-proof="${key}"]`);
  if (!node) return;
  node.className = `proof-step ${className}`;
  node.querySelector('.proof-meta').textContent = meta;
}

function trustBreakSource(run) {
  if (run.active_blast_radius?.invalidated_source) return run.active_blast_radius.invalidated_source;
  return run.events.find(e => e.event_type.includes('TRUST_BREAK'))?.checkpoint_id || null;
}

function reusedCheckpointIds(run) {
  const active = run.active_blast_radius?.reusable_checkpoints || [];
  if (active.length) return new Set(active);
  return new Set(
    run.events
      .filter(e => e.event_type.includes('REUSED'))
      .map(e => e.checkpoint_id)
      .filter(Boolean)
  );
}

function renderProof(run) {
  qsa('[data-proof]').forEach(node => {
    node.className = 'proof-step pending';
    node.querySelector('.proof-meta').textContent = 'waiting';
  });

  const blast = run.active_blast_radius;
  if (blast) {
    const recomputeCount = blast.recomputation_set?.length || 0;
    const reusable = blast.reusable_checkpoints || [];
    const blocked = blast.blocked_action_nodes || [];
    const reusedScout = reusable.includes('scout');

    setProofStep('trust-break', 'alert', blast.invalidated_source || 'detected');
    setProofStep('blast-radius', 'alert', `${recomputeCount} checkpoints to recompute`);
    setProofStep('action-blocked', 'blocked', blocked.length ? blocked.join(', ') : 'blocked');
    setProofStep('safe-reuse', 'complete', reusedScout ? 'Scout preserved' : `${reusable.length} reusable`);
    setProofStep('recomputed', 'pending', 'awaiting recovery');
    setProofStep('verified-recovery', 'pending', 'action remains frozen');
    return;
  }

  if (run.benchmark) {
    const breakEvent = run.events.find(e => e.event_type.includes('TRUST_BREAK'));
    setProofStep('trust-break', 'complete', breakEvent?.checkpoint_id || 'recorded');
    setProofStep('blast-radius', 'complete', 'exact descendants recorded');
    setProofStep('action-blocked', 'complete', 'publish_action was blocked');
    setProofStep('safe-reuse', 'complete', `${run.benchmark.reused_agent_checkpoints} agent reused`);
    setProofStep('recomputed', 'complete', `${run.benchmark.selective_recovery_agent_executions} agents rerun`);
    setProofStep('verified-recovery', 'complete', 'publish_action VERIFIED');
  }
}

function render(run) {
  state.run = run;
  qs('#runId').textContent = run.run_id;
  const provider = run.execution?.provider || 'unknown';
  const model = run.execution?.model ? ` · ${run.execution.model}` : '';
  qs('#executionProvider').textContent = `${provider}${model}`.toUpperCase();
  qs('#executionProvider').className = 'pill ' + (run.execution?.live_google ? 'ok' : 'neutral');
  const c = counts(run);
  qs('#verifiedCount').textContent = c.VERIFIED;
  qs('#recomputeCount').textContent = c.RECOMPUTE + c.INVALIDATED;
  qs('#blockedCount').textContent = c.BLOCKED;
  qs('#reusableCount').textContent = run.active_blast_radius?.reusable_checkpoints?.length || run.benchmark?.reused_agent_checkpoints || 0;
  qs('#runState').textContent = c.BLOCKED ? 'ACTION BLOCKED' : (run.benchmark ? 'RECOVERED' : 'VERIFIED BASELINE');
  qs('#runState').className = 'pill ' + (run.benchmark ? 'ok' : 'neutral');
  renderProof(run);
  renderGraph(run);
  renderEvents(run.events);
  renderBenchmark(run.benchmark);
  qsa('[data-fault]').forEach(b => b.disabled = !!run.active_blast_radius);
  qs('#recover').disabled = !run.active_blast_radius;
  updateAccessUi();

  const moment = qs('#judgeMoment');
  if (run.active_blast_radius) {
    moment.className = 'judge-moment alert';
    qs('#momentTitle').textContent = 'TRUST BREAK DETECTED → UNSAFE ACTION BLOCKED';
    qs('#momentBody').textContent = `Source: ${run.active_blast_radius.invalidated_source}. Blast radius computed; unaffected work stays reusable.`;
  } else if (run.benchmark) {
    moment.className = 'judge-moment recovered';
    qs('#momentTitle').textContent = 'SELECTIVE RECOVERY VERIFIED → ACTION RESUMED';
    qs('#momentBody').textContent = 'Affected branch recomputed in dependency order; reusable checkpoints were preserved.';
  } else {
    moment.className = 'judge-moment';
    qs('#momentTitle').textContent = 'VERIFIED FLEET BASELINE';
    qs('#momentBody').textContent = 'All checkpoint dependencies passed deterministic trust gates.';
  }
}

function renderGraph(run) {
  const graph = qs('#graph');
  const reusable = reusedCheckpointIds(run);
  const breakSource = trustBreakSource(run);
  graph.innerHTML = run.checkpoints.map(cp => {
    const pos = graphOrder[cp.checkpoint_id] || [1,1];
    const deps = cp.dependencies.length ? cp.dependencies.join(' · ') : 'root';
    const isBreak = cp.checkpoint_id === breakSource;
    const isReused = reusable.has(cp.checkpoint_id);
    const historicalBreak = isBreak && !run.active_blast_radius && !!run.benchmark;
    const classes = ['node'];
    if (isReused) classes.push('reused');
    if (historicalBreak) classes.push('historical-break');
    let kind = cp.kind;
    if (isBreak) kind += ' · TRUST BREAK';
    if (isReused) kind += ' · REUSED';
    let status = cp.status;
    if (historicalBreak) status = `${cp.status} · REVERIFIED`;
    return `<article id="node-${cp.checkpoint_id}" class="${classes.join(' ')}" data-status="${cp.status}" style="grid-column:${pos[0]};grid-row:${pos[1]}">
      <div class="kind">${kind}</div>
      <h3>${cp.checkpoint_id.replaceAll('_',' ')}</h3>
      <div class="status">${status}</div>
      <div class="deps">deps: ${deps}</div>
    </article>`;
  }).join('');
  requestAnimationFrame(() => drawEdges(run));
}

function drawEdges(run) {
  const wrap = qs('#graphWrap'); const svg = qs('#edges');
  const box = wrap.getBoundingClientRect();
  svg.setAttribute('viewBox', `0 0 ${wrap.scrollWidth} ${wrap.scrollHeight}`);
  svg.setAttribute('width', wrap.scrollWidth); svg.setAttribute('height', wrap.scrollHeight);
  const affected = new Set(run.active_blast_radius?.contaminated_checkpoints || []);
  if (run.active_blast_radius?.invalidated_source) affected.add(run.active_blast_radius.invalidated_source);
  let paths = '';
  run.checkpoints.forEach(cp => cp.dependencies.forEach(dep => {
    const a = qs(`#node-${dep}`)?.getBoundingClientRect(); const b = qs(`#node-${cp.checkpoint_id}`)?.getBoundingClientRect();
    if (!a || !b) return;
    const x1 = a.right - box.left + wrap.scrollLeft, y1 = a.top + a.height/2 - box.top + wrap.scrollTop;
    const x2 = b.left - box.left + wrap.scrollLeft, y2 = b.top + b.height/2 - box.top + wrap.scrollTop;
    const dx = Math.max(24, (x2-x1)*0.45);
    const cls = affected.has(dep) && affected.has(cp.checkpoint_id) ? 'edge affected' : 'edge';
    paths += `<path class="${cls}" d="M ${x1} ${y1} C ${x1+dx} ${y1}, ${x2-dx} ${y2}, ${x2} ${y2}"/>`;
  }));
  svg.innerHTML = paths;
}

function renderEvents(events) {
  const root = qs('#events');
  if (!events.length) { root.innerHTML = '<p class="empty">No events yet.</p>'; return; }
  root.innerHTML = [...events].reverse().map(e => {
    const cls = e.event_type.includes('TRUST_BREAK') ? 'trust' : e.event_type.includes('BLOCKED') ? 'block' : e.event_type.includes('RECOVERY') || e.event_type.includes('RESUMED') || e.event_type.includes('REVERIFIED') ? 'recovery' : '';
    return `<div class="event ${cls}"><div class="event-index">${String(e.event_id).padStart(2,'0')}</div><div><strong>${e.event_type}</strong><p>${e.message}${e.checkpoint_id ? ` · ${e.checkpoint_id}` : ''}</p></div></div>`;
  }).join('');
}

function renderBenchmark(b) {
  const root = qs('#benchmark'); const pill = qs('#measurementClass');
  if (!b) {
    root.className='benchmark-empty';
    root.textContent='Run a recovery to produce a receipt. Deterministic test mode never claims Gemini model calls or token savings.';
    pill.textContent='NO RECEIPT'; pill.className='pill neutral'; return;
  }
  const reduction = Math.round(b.execution_reduction_ratio * 100);
  const live = b.measurement_class.startsWith('google_adk_live');
  const modelReduction = b.model_call_reduction_ratio == null ? null : Math.round(b.model_call_reduction_ratio * 100);
  const tokenReduction = b.input_token_reduction_ratio == null ? null : Math.round(b.input_token_reduction_ratio * 100);
  const savedInputTokens = b.full_restart_input_tokens != null && b.selective_recovery_input_tokens != null
    ? b.full_restart_input_tokens - b.selective_recovery_input_tokens
    : null;
  root.className='benchmark-grid';
  root.innerHTML = `
    <div class="bench"><span>Full restart agents</span><strong>${b.full_restart_agent_executions}</strong></div>
    <div class="bench"><span>Selective reruns</span><strong>${b.selective_recovery_agent_executions}</strong></div>
    <div class="bench"><span>Agents reused</span><strong>${b.reused_agent_checkpoints}</strong></div>
    <div class="bench"><span>Execution reduction</span><strong>${reduction}%*</strong></div>`;
  if (live) {
    root.insertAdjacentHTML('beforeend', `
      <div class="bench"><span>Full restart model calls</span><strong>${b.full_restart_model_calls ?? 'n/a'}</strong></div>
      <div class="bench"><span>Selective model calls</span><strong>${b.selective_recovery_model_calls ?? 'n/a'}</strong></div>
      <div class="bench"><span>Full restart input tokens</span><strong>${b.full_restart_input_tokens ?? 'n/a'}</strong></div>
      <div class="bench"><span>Selective input tokens</span><strong>${b.selective_recovery_input_tokens ?? 'n/a'}</strong></div>
      <div class="bench"><span>Model-call reduction</span><strong>${modelReduction == null ? 'n/a' : modelReduction + '%'}</strong></div>
      <div class="bench"><span>Input-token reduction</span><strong>${tokenReduction == null ? 'n/a' : tokenReduction + '%'}</strong></div>
      <div class="bench"><span>Input tokens saved</span><strong>${savedInputTokens ?? 'n/a'}</strong></div>
      <div class="bench"><span>Measurement</span><strong>LIVE</strong></div>`);
  }
  pill.textContent=b.measurement_class.toUpperCase(); pill.className='pill ' + (live ? 'ok' : 'neutral');
  const note = live
    ? '* Measured only for this controlled run. Model-call/token fields come from live ADK event usage when available; no general savings claim.'
    : '* Measured checkpoint-execution reduction in this controlled deterministic test scenario only. Gemini calls/tokens are intentionally unclaimed.';
  root.insertAdjacentHTML('beforeend', `<p class="benchmark-empty" style="grid-column:1/-1;margin:2px 0 0">${note}</p>`);
}

async function runAutorun() {
  const config = state.pendingAutorun;
  if (!config) return;
  if (state.accessRequired && !judgeKey()) return;
  state.pendingAutorun = null;
  try {
    let run = await request('/api/runs', {method:'POST'});
    render(run);
    await holdAutorunStage('baseline');
    run = await request(`/api/runs/${run.run_id}/fault/${config.scenario}`, {method:'POST'});
    render(run);
    await holdAutorunStage('incident');
    if (config.recover) {
      run = await request(`/api/runs/${run.run_id}/recover`, {method:'POST'});
      render(run);
      await holdAutorunStage('recovered');
    }
  } catch (e) {
    console.error('visual smoke harness failed', e);
    alert(`Judge autorun failed: ${e.message}`);
  }
}

qs('#saveJudgeKey').addEventListener('click', async () => {
  const input = qs('#judgeKey');
  const value = input.value.trim();
  if (!value) {
    sessionStorage.removeItem('recoveryMeshJudgeKey');
    updateAccessUi('LOCKED');
    return;
  }
  sessionStorage.setItem('recoveryMeshJudgeKey', value);
  input.value = '';
  updateAccessUi('KEY STORED');
  await runAutorun();
});
qs('#judgeKey').addEventListener('keydown', (event) => {
  if (event.key === 'Enter') qs('#saveJudgeKey').click();
});
qs('#startRun').addEventListener('click', async () => { try { render(await request('/api/runs',{method:'POST'})); } catch(e) { alert(e.message); } });
qsa('[data-fault]').forEach(btn => btn.addEventListener('click', async () => { if(!state.run) return; try { render(await request(`/api/runs/${state.run.run_id}/fault/${btn.dataset.fault}`,{method:'POST'})); } catch(e) { alert(e.message); } }));
qs('#recover').addEventListener('click', async () => { try { render(await request(`/api/runs/${state.run.run_id}/recover`,{method:'POST'})); } catch(e) { alert(e.message); } });
window.addEventListener('resize', () => state.run && drawEdges(state.run));

(async function initialize(){
  try {
    await loadHealth();
  } catch (e) {
    console.error('health check failed', e);
  }

  const p = new URLSearchParams(location.search);
  const scenario = p.get('autorun');
  if (!scenario) return;
  state.pendingAutorun = {scenario, recover: p.get('recover') === '1'};
  if (state.accessRequired && !judgeKey()) {
    console.info('visual smoke harness waiting for judge access key');
    return;
  }
  await runAutorun();
})();