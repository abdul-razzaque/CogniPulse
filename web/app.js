/**
 * CogniPulse Studio - Main Application Controller
 * Orchestrates real-time telemetry polling, chat stream, teach modal,
 * reinforcement feedback loops, document ingestion, and simulation.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide Icons
  if (window.lucide) {
    lucide.createIcons();
  }

  // Initialize visualizers
  const neuralVis = new NeuralVisualizer('neuralCanvas');
  const kgViewer = new KnowledgeGraphViewer('kgCanvas', 'kgNodeDetails');
  const simViewer = new SimulationViewer('simCanvas');

  // State
  let activeCorrectionContext = null;
  let isSimAutoRunning = false;
  let simAutoInterval = null;

  // DOM Elements
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  const messagesContainer = document.getElementById('messagesContainer');
  const chatInput = document.getElementById('chatInput');
  const btnSendChat = document.getElementById('btnSendChat');
  const btnClearChat = document.getElementById('btnClearChat');
  const thoughtStreamArea = document.getElementById('thoughtStreamArea');
  const recalledNodesList = document.getElementById('recalledNodesList');
  const lastLatency = document.getElementById('lastLatency');

  // Modals
  const teachModal = document.getElementById('teachModal');
  const btnOpenTeach = document.getElementById('btnOpenTeach');
  const btnCloseTeachModal = document.getElementById('btnCloseTeachModal');
  const btnCancelTeach = document.getElementById('btnCancelTeach');
  const btnSubmitTeach = document.getElementById('btnSubmitTeach');
  const modalFactText = document.getElementById('modalFactText');
  const modalFactCategory = document.getElementById('modalFactCategory');

  const correctModal = document.getElementById('correctModal');
  const btnCloseCorrectModal = document.getElementById('btnCloseCorrectModal');
  const btnCancelCorrect = document.getElementById('btnCancelCorrect');
  const btnSubmitCorrection = document.getElementById('btnSubmitCorrection');
  const modalCorrectionText = document.getElementById('modalCorrectionText');

  // Ingestion
  const ingestTextInput = document.getElementById('ingestTextInput');
  const btnIngestText = document.getElementById('btnIngestText');
  const btnLoadSampleDoc = document.getElementById('btnLoadSampleDoc');
  const ingestResultsBox = document.getElementById('ingestResultsBox');
  const extractedConceptsTags = document.getElementById('extractedConceptsTags');
  const extractedTriplesList = document.getElementById('extractedTriplesList');

  // Simulation buttons
  const btnSimStep = document.getElementById('btnSimStep');
  const btnSimAutoPlay = document.getElementById('btnSimAutoPlay');
  const btnSimTrainBatch = document.getElementById('btnSimTrainBatch');
  const btnSimReset = document.getElementById('btnSimReset');

  // ==========================================
  // 1. Tab Navigation
  // ==========================================
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tabButtons.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add('active');
      }

      if (targetId === 'neural-tab') neuralVis.initCanvas();
      if (targetId === 'graph-tab') kgViewer.initCanvas();
    });
  });

  // Quick Prompt Chips
  document.querySelectorAll('.prompt-tag').forEach(tag => {
    tag.addEventListener('click', () => {
      chatInput.value = tag.getAttribute('data-prompt');
      handleSendMessage();
    });
  });

  // ==========================================
  // 2. Chat & Evolution Thought Stream
  // ==========================================
  btnSendChat.addEventListener('click', handleSendMessage);
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });

  btnClearChat.addEventListener('click', () => {
    messagesContainer.innerHTML = '';
    thoughtStreamArea.innerHTML = `
      <div class="empty-state">
        <i data-lucide="eye" class="empty-icon"></i>
        <p>Send a message to inspect CogniPulse's live associative memory recall, heuristic checks, and synaptic activations.</p>
      </div>`;
    if (window.lucide) lucide.createIcons();
  });

  async function handleSendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Append User Message
    appendMessage(text, 'user');
    chatInput.value = '';

    // Trigger visual synaptic spark
    neuralVis.triggerPulse();

    try {
      const resp = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text })
      });
      const data = await resp.json();

      // Append Model Message
      appendMessage(data.response, 'model', text, data);

      // Render Cognitive Stream
      renderThoughtStream(data.thought_stream, data.latency_ms);

      // Render Recalled Synaptic Nodes
      renderRecalledMemories(data.recalled_memories);

      // Trigger active firing node highlight in visualizer
      if (data.firing_event && data.firing_event.activated_memories) {
        neuralVis.triggerPulse(data.firing_event.activated_memories);
      }

      // Refresh telemetry
      fetchTelemetry();
    } catch (err) {
      appendMessage(`⚠️ Error communicating with CogniPulse core: ${err.message}`, 'system');
    }
  }

  function appendMessage(content, type, queryContext = "", fullData = null) {
    const card = document.createElement('div');
    card.className = `message-card ${type === 'user' ? 'user-msg' : (type === 'model' ? 'model-msg' : 'system-message')}`;

    let avatarIcon = type === 'user' ? 'user' : (type === 'model' ? 'brain-circuit' : 'info');
    let formattedText = content.replace(/\n/g, '<br/>');

    let actionsHtml = '';
    if (type === 'model' && queryContext) {
      actionsHtml = `
        <div class="msg-actions">
          <button class="btn-feedback btn-reinforce" title="Reinforce this response (Positive Reward)">
            <i data-lucide="thumbs-up"></i> Reinforce
          </button>
          <button class="btn-feedback btn-correct" title="Correct mistake & synthesize adaptive rule">
            <i data-lucide="wrench"></i> Teach Correction
          </button>
        </div>
      `;
    }

    card.innerHTML = `
      <div class="msg-avatar"><i data-lucide="${avatarIcon}"></i></div>
      <div class="msg-content">
        <p>${formattedText}</p>
        ${actionsHtml}
      </div>
    `;

    messagesContainer.appendChild(card);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    if (window.lucide) lucide.createIcons();

    // Attach feedback events
    if (type === 'model' && queryContext) {
      const btnReinforce = card.querySelector('.btn-reinforce');
      const btnCorrect = card.querySelector('.btn-correct');

      if (btnReinforce) {
        btnReinforce.addEventListener('click', async () => {
          btnReinforce.innerHTML = `<i data-lucide="check"></i> Reinforced (+0.3)`;
          btnReinforce.style.color = '#10b981';
          await fetch('/api/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: queryContext, response: content, is_positive: true })
          });
          neuralVis.triggerPulse();
          fetchTelemetry();
        });
      }

      if (btnCorrect) {
        btnCorrect.addEventListener('click', () => {
          activeCorrectionContext = { query: queryContext, response: content };
          modalCorrectionText.value = '';
          correctModal.classList.add('active');
        });
      }
    }
  }

  function renderThoughtStream(stream, latency) {
    if (!stream || stream.length === 0) return;
    lastLatency.textContent = `${latency} ms`;
    thoughtStreamArea.innerHTML = '';

    stream.forEach(step => {
      const card = document.createElement('div');
      card.className = 'thought-card';

      let detailsHtml = '';
      if (step.details && step.details.length > 0) {
        detailsHtml = `<ul class="thought-details-list">` + step.details.map(d => `<li>${d}</li>`).join('') + `</ul>`;
      }

      card.innerHTML = `
        <span class="thought-stage-tag stage-${step.stage}">${step.stage}</span>
        <div class="thought-msg">${step.message}</div>
        ${detailsHtml}
      `;
      thoughtStreamArea.appendChild(card);
    });
    thoughtStreamArea.scrollTop = thoughtStreamArea.scrollHeight;
  }

  function renderRecalledMemories(memories) {
    if (!memories || memories.length === 0) {
      recalledNodesList.innerHTML = `<span class="text-muted text-sm">No associative memory resonance needed.</span>`;
      return;
    }
    recalledNodesList.innerHTML = memories.map(m => `
      <div class="node-chip">
        <strong>${m.category.toUpperCase()}:</strong> ${m.content} (Synapse: ${m.synaptic_weight})
      </div>
    `).join('');
  }

  // ==========================================
  // 3. Modals: Teach & Correction
  // ==========================================
  btnOpenTeach.addEventListener('click', () => {
    modalFactText.value = '';
    teachModal.classList.add('active');
  });
  btnCloseTeachModal.addEventListener('click', () => teachModal.classList.remove('active'));
  btnCancelTeach.addEventListener('click', () => teachModal.classList.remove('active'));

  btnSubmitTeach.addEventListener('click', async () => {
    const fact = modalFactText.value.trim();
    const cat = modalFactCategory.value;
    if (!fact) return;

    btnSubmitTeach.textContent = 'Assimilating...';
    try {
      const resp = await fetch('/api/teach', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fact, category: cat })
      });
      await resp.json();
      teachModal.classList.remove('active');
      appendMessage(`🧠 **Taught Fact:** "${fact}" was successfully assimilated into the neural memory matrix.`, 'system');
      neuralVis.triggerPulse();
      fetchTelemetry();
    } finally {
      btnSubmitTeach.innerHTML = `<i data-lucide="check"></i> Ingest Fact`;
      if (window.lucide) lucide.createIcons();
    }
  });

  btnCloseCorrectModal.addEventListener('click', () => correctModal.classList.remove('active'));
  btnCancelCorrect.addEventListener('click', () => correctModal.classList.remove('active'));

  btnSubmitCorrection.addEventListener('click', async () => {
    const corr = modalCorrectionText.value.trim();
    if (!corr || !activeCorrectionContext) return;

    try {
      await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: activeCorrectionContext.query,
          response: activeCorrectionContext.response,
          is_positive: false,
          correction: corr
        })
      });
      correctModal.classList.remove('active');
      appendMessage(`🔧 **Adaptive Rule Created:** CogniPulse registered your correction and updated its reasoning heuristics.`, 'system');
      neuralVis.triggerPulse();
      fetchTelemetry();
    } catch (err) {
      alert(`Error applying correction: ${err.message}`);
    }
  });

  // ==========================================
  // 4. Ingestion / Document Digester
  // ==========================================
  btnLoadSampleDoc.addEventListener('click', () => {
    ingestTextInput.value = `Artificial General Intelligence is a system capable of autonomous problem solving. Deep Reinforcement Learning combines neural networks with policy iteration. Neural Plasticity allows biological and synthetic brains to reorganize synaptic weights dynamically based on experience. Knowledge Graphs represent real-world entities and formal semantic relationships.`;
  });

  btnIngestText.addEventListener('click', async () => {
    const text = ingestTextInput.value.trim();
    if (!text) return;

    btnIngestText.textContent = 'Digesting...';
    try {
      const resp = await fetch('/api/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      const data = await resp.json();

      ingestResultsBox.style.display = 'block';
      extractedConceptsTags.innerHTML = (data.extracted_concepts || []).map(c => `<span class="tag-concept">${c}</span>`).join(' ');
      extractedTriplesList.innerHTML = (data.triples_discovered || []).map(t => `<li>➔ <strong>${t.source}</strong> [${t.relation}] <strong>${t.target}</strong></li>`).join('');
      
      neuralVis.triggerPulse();
      fetchTelemetry();
    } finally {
      btnIngestText.innerHTML = `<i data-lucide="binary"></i> Digest & Assimilate Into Brain`;
      if (window.lucide) lucide.createIcons();
    }
  });

  // ==========================================
  // 5. Reinforcement Learning Lab
  // ==========================================
  btnSimStep.addEventListener('click', async () => {
    const resp = await fetch('/api/sim/step', { method: 'POST' });
    const data = await resp.json();
    updateSimTelemetry(data);
    fetchSimState();
  });

  btnSimAutoPlay.addEventListener('click', () => {
    isSimAutoRunning = !isSimAutoRunning;
    if (isSimAutoRunning) {
      btnSimAutoPlay.innerHTML = `<i data-lucide="pause"></i> Pause`;
      simAutoInterval = setInterval(async () => {
        const resp = await fetch('/api/sim/step', { method: 'POST' });
        const data = await resp.json();
        updateSimTelemetry(data);
        fetchSimState();
      }, 150);
    } else {
      btnSimAutoPlay.innerHTML = `<i data-lucide="fast-forward"></i> Auto Learn`;
      clearInterval(simAutoInterval);
    }
    if (window.lucide) lucide.createIcons();
  });

  btnSimTrainBatch.addEventListener('click', async () => {
    btnSimTrainBatch.textContent = 'Training 25 Episodes...';
    try {
      await fetch('/api/sim/train', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ episodes: 25 })
      });
      fetchSimState();
      fetchTelemetry();
    } finally {
      btnSimTrainBatch.innerHTML = `<i data-lucide="zap"></i> Batch Train (25 Ep)`;
      if (window.lucide) lucide.createIcons();
    }
  });

  btnSimReset.addEventListener('click', async () => {
    await fetch('/api/sim/reset', { method: 'POST' });
    fetchSimState();
  });

  function updateSimTelemetry(data) {
    if (!data) return;
    document.getElementById('simEpisodeVal').textContent = data.episode || 0;
    document.getElementById('simStepsVal').textContent = data.total_steps || 0;
    document.getElementById('simLastRewardVal').textContent = (data.reward !== undefined ? data.reward : 0.0).toFixed(1);
    document.getElementById('simLossVal').textContent = (data.td_loss !== undefined ? data.td_loss : 0.0).toFixed(4);
    document.getElementById('simEpsilonBadge').textContent = `ε (Exploration): ${data.epsilon || 0.8}`;
  }

  async function fetchSimState() {
    try {
      const resp = await fetch('/api/sim/state');
      const state = await resp.json();
      simViewer.updateState(state);
      
      // Update Q-Table preview snippet
      const qBox = document.getElementById('qTablePreview');
      if (state.q_grid) {
        let previewHtml = `<table style="width:100%; font-size:11px; font-family:var(--font-mono);">
          <tr style="color:var(--text-dim);"><th>State (R,C)</th><th>Best Action</th><th>Max Q-Val</th></tr>`;
        
        let count = 0;
        for (let r = 0; r < state.q_grid.length && count < 6; r++) {
          for (let c = 0; c < state.q_grid[r].length && count < 6; c++) {
            const cell = state.q_grid[r][c];
            if (cell.max_q > 0) {
              previewHtml += `<tr><td>(${r}, ${c})</td><td class="text-cyan">${cell.best_action}</td><td class="text-amber">${cell.max_q}</td></tr>`;
              count++;
            }
          }
        }
        previewHtml += `</table>`;
        qBox.innerHTML = count > 0 ? previewHtml : `<span class="text-muted text-sm">Agent exploring environment to learn optimal action policy...</span>`;
      }
    } catch (e) {}
  }

  // ==========================================
  // 6. Live Telemetry & Rules Polling
  // ==========================================
  async function fetchTelemetry() {
    try {
      const resp = await fetch('/api/telemetry');
      const data = await resp.json();

      // Top bar
      document.getElementById('plasticityVal').textContent = data.learning.synaptic_plasticity_index || '0.85';
      document.getElementById('memCountVal').textContent = data.memory.total_memories || '0';
      document.getElementById('conceptsCountVal').textContent = (data.graph.nodes || []).length || '0';

      // Telemetry Tab Stats
      document.getElementById('telAccuracy').textContent = `${data.learning.accuracy_percentage}%`;
      document.getElementById('telReinforceCount').textContent = data.learning.total_reinforcements;
      document.getElementById('telCorrectionsCount').textContent = data.learning.total_corrections;
      document.getElementById('telSynapsesCount').textContent = data.memory.total_synapses || 0;

      // Rules Table
      const tableBody = document.getElementById('rulesTableBody');
      if (tableBody && data.learning.rules) {
        tableBody.innerHTML = data.learning.rules.map(r => `
          <tr>
            <td><code class="text-cyan">${r.rule_id}</code></td>
            <td><code>${r.trigger_pattern}</code></td>
            <td>${r.action_guidance}</td>
            <td class="text-amber"><strong>${r.reward_score}</strong></td>
            <td class="text-emerald">${(r.success_rate * 100).toFixed(0)}%</td>
          </tr>
        `).join('');
      }

      // Update Visualizers with latest graph & memory data
      if (data.graph) kgViewer.updateGraph(data.graph);
      
      // Update Neural matrix
      const memResp = await fetch('/api/memories');
      const memData = await memResp.json();
      if (memData.memories) {
        neuralVis.updateFromBrainData(memData.memories);
      }

    } catch (err) {
      console.warn("Telemetry poll notice:", err.message);
    }
  }

  // Initial Fetch & Regular Polling
  fetchTelemetry();
  fetchSimState();
  setInterval(fetchTelemetry, 3000);
});
