/**
 * CogniPulse - Modern AI Studio Controller (Claude/Gemini/ChatGPT Style)
 */

document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) {
    lucide.createIcons();
  }

  // Visualizer instances
  const neuralVis = new NeuralVisualizer('neuralCanvas');
  const kgViewer = new KnowledgeGraphViewer('kgCanvas', 'kgNodeDetails');
  const simViewer = new SimulationViewer('simCanvas');

  // State
  let activeCorrectionContext = null;
  let isSimAutoRunning = false;
  let simAutoInterval = null;

  // DOM Elements
  const sidebar = document.getElementById('sidebar');
  const btnToggleSidebar = document.getElementById('btnToggleSidebar');
  const btnOpenSidebarMobile = document.getElementById('btnOpenSidebarMobile');
  const btnNewChat = document.getElementById('btnNewChat');

  const navItems = document.querySelectorAll('.nav-item');
  const viewPanels = document.querySelectorAll('.view-panel');
  const btnCloseViews = document.querySelectorAll('.btn-close-view');

  const heroWelcome = document.getElementById('heroWelcome');
  const messagesList = document.getElementById('messagesList');
  const chatMessagesScroll = document.getElementById('chatMessagesScroll');
  const chatInput = document.getElementById('chatInput');
  const btnSendChat = document.getElementById('btnSendChat');

  // Header quick buttons
  const btnHeaderTeach = document.getElementById('btnHeaderTeach');
  const btnHeaderBrainView = document.getElementById('btnHeaderBrainView');
  const btnQuickTeach = document.getElementById('btnQuickTeach');
  const btnQuickIngest = document.getElementById('btnQuickIngest');

  // Modals
  const teachModal = document.getElementById('teachModal');
  const btnCloseTeachModal = document.getElementById('btnCloseTeachModal');
  const btnCancelTeach = document.getElementById('btnCancelTeach');
  const btnSubmitTeach = document.getElementById('btnSubmitTeach');
  const modalFactText = document.getElementById('modalFactText');
  const modalFactCategory = document.getElementById('modalFactCategory');

  const ingestModal = document.getElementById('ingestModal');
  const btnCloseIngestModal = document.getElementById('btnCloseIngestModal');
  const btnCancelIngest = document.getElementById('btnCancelIngest');
  const btnSubmitIngest = document.getElementById('btnSubmitIngest');
  const ingestTextInput = document.getElementById('ingestTextInput');

  const correctModal = document.getElementById('correctModal');
  const btnCloseCorrectModal = document.getElementById('btnCloseCorrectModal');
  const btnCancelCorrect = document.getElementById('btnCancelCorrect');
  const btnSubmitCorrection = document.getElementById('btnSubmitCorrection');
  const modalCorrectionText = document.getElementById('modalCorrectionText');

  // Sim buttons
  const btnSimStep = document.getElementById('btnSimStep');
  const btnSimAutoPlay = document.getElementById('btnSimAutoPlay');
  const btnSimTrainBatch = document.getElementById('btnSimTrainBatch');
  const btnSimReset = document.getElementById('btnSimReset');

  // ==========================================
  // 1. Sidebar & View Switching
  // ==========================================
  if (btnToggleSidebar) {
    btnToggleSidebar.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
    });
  }

  if (btnOpenSidebarMobile) {
    btnOpenSidebarMobile.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
    });
  }

  function switchView(viewId) {
    navItems.forEach(item => {
      if (item.getAttribute('data-view') === viewId) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    viewPanels.forEach(panel => {
      if (panel.id === viewId) {
        panel.classList.add('active');
      } else {
        panel.classList.remove('active');
      }
    });

    if (viewId === 'brain-view') neuralVis.initCanvas();
    if (viewId === 'graph-view') kgViewer.initCanvas();
  }

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      switchView(item.getAttribute('data-view'));
    });
  });

  btnCloseViews.forEach(btn => {
    btn.addEventListener('click', () => {
      switchView('chat-view');
    });
  });

  if (btnHeaderBrainView) {
    btnHeaderBrainView.addEventListener('click', () => {
      switchView('brain-view');
    });
  }

  // New Chat
  btnNewChat.addEventListener('click', () => {
    messagesList.innerHTML = '';
    heroWelcome.style.display = 'flex';
    switchView('chat-view');
  });

  // Suggestion Cards Click
  document.querySelectorAll('.suggestion-card').forEach(card => {
    card.addEventListener('click', () => {
      const prompt = card.getAttribute('data-prompt');
      chatInput.value = prompt;
      handleSendMessage();
    });
  });

  // Auto-expanding textarea
  chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
  });

  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });

  btnSendChat.addEventListener('click', handleSendMessage);

  // ==========================================
  // 2. Chat Message Flow & Thought Accordion
  // ==========================================
  async function handleSendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Hide hero welcome
    heroWelcome.style.display = 'none';

    // Append User Bubble
    appendUserMessage(text);
    chatInput.value = '';
    chatInput.style.height = 'auto';

    // Add Thinking Placeholder
    const thinkingRow = appendThinkingPlaceholder();

    // Trigger visual pulse
    neuralVis.triggerPulse();

    try {
      const resp = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text })
      });
      const data = await resp.json();

      // Remove thinking placeholder
      thinkingRow.remove();

      if (!resp.ok || data.error) {
        appendSystemError(`CogniPulse Error: ${data.error || 'Unexpected response'}`);
        return;
      }

      // Render AI Message with Collapsible Thought Stream
      appendAiMessage(data.response || 'Knowledge assimilated.', text, data);

      if (data.firing_event && data.firing_event.activated_memories) {
        neuralVis.triggerPulse(data.firing_event.activated_memories);
      }

      fetchTelemetry();
    } catch (err) {
      thinkingRow.remove();
      appendSystemError(`Error connecting to CogniPulse: ${err.message}`);
    }
  }

  function appendUserMessage(content) {
    const row = document.createElement('div');
    row.className = 'chat-row-user';
    row.innerHTML = `<div class="user-bubble">${escapeHtml(content).replace(/\n/g, '<br/>')}</div>`;
    messagesList.appendChild(row);
    scrollToBottom();
  }

  function appendThinkingPlaceholder() {
    const row = document.createElement('div');
    row.className = 'chat-row-ai';
    row.innerHTML = `
      <div class="ai-avatar"><i data-lucide="brain-circuit"></i></div>
      <div class="ai-body">
        <div class="thought-accordion">
          <div class="thought-summary-btn" style="cursor:default;">
            <div class="thought-title-wrap">
              <i data-lucide="loader-2" class="spin"></i>
              <span>Thinking & recalling synapses...</span>
            </div>
          </div>
        </div>
      </div>
    `;
    messagesList.appendChild(row);
    if (window.lucide) lucide.createIcons();
    scrollToBottom();
    return row;
  }

  function appendAiMessage(responseContent, userQuery, fullData) {
    const row = document.createElement('div');
    row.className = 'chat-row-ai';

    const latency = fullData && fullData.latency_ms ? fullData.latency_ms : '12';
    const thoughtSteps = fullData && fullData.thought_stream ? fullData.thought_stream : [];

    let thoughtStepsHtml = '';
    if (thoughtSteps.length > 0) {
      thoughtStepsHtml = thoughtSteps.map(st => `
        <div class="thought-step-line">
          <strong>[${st.stage}]</strong> ${escapeHtml(st.message)}
        </div>
      `).join('');
    }

    const formattedText = formatMarkdown(responseContent);

    row.innerHTML = `
      <div class="ai-avatar"><i data-lucide="brain-circuit"></i></div>
      <div class="ai-body">
        
        <!-- Thought Process Accordion -->
        <div class="thought-accordion">
          <button class="thought-summary-btn">
            <div class="thought-title-wrap">
              <i data-lucide="sparkles"></i>
              <span>Thought Process (${latency}ms)</span>
            </div>
            <i data-lucide="chevron-down" class="acc-chevron"></i>
          </button>
          <div class="thought-content-box">
            ${thoughtStepsHtml || '<div class="text-sm text-muted">Associative recall and Hebbian resonance completed.</div>'}
          </div>
        </div>

        <!-- AI Text Body -->
        <div class="ai-text">${formattedText}</div>

        <!-- Action Toolbar -->
        <div class="ai-actions-bar">
          <button class="btn-ai-action btn-reinforce" title="Good response (+0.3 synaptic boost)">
            <i data-lucide="thumbs-up"></i>
          </button>
          <button class="btn-ai-action btn-correct-trigger" title="Teach correction & synthesize heuristic rule">
            <i data-lucide="wrench"></i> Teach Correction
          </button>
          <button class="btn-ai-action btn-copy-msg" title="Copy response">
            <i data-lucide="copy"></i>
          </button>
        </div>
      </div>
    `;

    messagesList.appendChild(row);
    if (window.lucide) lucide.createIcons();
    scrollToBottom();

    // Accordion toggle
    const accordionBtn = row.querySelector('.thought-summary-btn');
    const accordionContent = row.querySelector('.thought-content-box');
    if (accordionBtn && accordionContent) {
      accordionBtn.addEventListener('click', () => {
        accordionContent.classList.toggle('open');
      });
    }

    // Reinforce button
    const btnReinforce = row.querySelector('.btn-reinforce');
    if (btnReinforce) {
      btnReinforce.addEventListener('click', async () => {
        btnReinforce.innerHTML = `<i data-lucide="check"></i>`;
        btnReinforce.style.color = '#10b981';
        if (window.lucide) lucide.createIcons();
        await fetch('/api/feedback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: userQuery, response: responseContent, is_positive: true })
        });
        neuralVis.triggerPulse();
        fetchTelemetry();
      });
    }

    // Correction button
    const btnCorrect = row.querySelector('.btn-correct-trigger');
    if (btnCorrect) {
      btnCorrect.addEventListener('click', () => {
        activeCorrectionContext = { query: userQuery, response: responseContent };
        modalCorrectionText.value = '';
        correctModal.classList.add('active');
      });
    }

    // Copy button
    const btnCopy = row.querySelector('.btn-copy-msg');
    if (btnCopy) {
      btnCopy.addEventListener('click', () => {
        navigator.clipboard.writeText(responseContent);
        btnCopy.innerHTML = `<i data-lucide="check"></i>`;
        if (window.lucide) lucide.createIcons();
        setTimeout(() => {
          btnCopy.innerHTML = `<i data-lucide="copy"></i>`;
          if (window.lucide) lucide.createIcons();
        }, 1500);
      });
    }
  }

  function appendSystemError(msg) {
    const row = document.createElement('div');
    row.className = 'chat-row-ai';
    row.innerHTML = `
      <div class="ai-avatar" style="color:#f43f5e; border-color:#f43f5e;"><i data-lucide="alert-circle"></i></div>
      <div class="ai-body">
        <div class="ai-text" style="color:#f43f5e;">${escapeHtml(msg)}</div>
      </div>
    `;
    messagesList.appendChild(row);
    if (window.lucide) lucide.createIcons();
    scrollToBottom();
  }

  function scrollToBottom() {
    chatMessagesScroll.scrollTop = chatMessagesScroll.scrollHeight;
  }

  function escapeHtml(str) {
    return (str || '').toString().replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function formatMarkdown(text) {
    let t = escapeHtml(text);
    // Bold
    t = t.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italic
    t = t.replace(/\*(.*?)\*/g, '<em>$1</em>');
    // Blockquote
    t = t.replace(/^>\s*(.*?)$/gm, '<blockquote>$1</blockquote>');
    // Linebreaks
    t = t.replace(/\n/g, '<br/>');
    return t;
  }

  // ==========================================
  // 3. Modals: Teach & Ingestion & Correction
  // ==========================================
  function openTeachModal() {
    modalFactText.value = '';
    teachModal.classList.add('active');
  }
  if (btnHeaderTeach) btnHeaderTeach.addEventListener('click', openTeachModal);
  if (btnQuickTeach) btnQuickTeach.addEventListener('click', openTeachModal);
  if (btnCloseTeachModal) btnCloseTeachModal.addEventListener('click', () => teachModal.classList.remove('active'));
  if (btnCancelTeach) btnCancelTeach.addEventListener('click', () => teachModal.classList.remove('active'));

  if (btnSubmitTeach) {
    btnSubmitTeach.addEventListener('click', async () => {
      const fact = modalFactText.value.trim();
      const cat = modalFactCategory.value;
      if (!fact) return;

      btnSubmitTeach.textContent = 'Assimilating...';
      try {
        await fetch('/api/teach', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fact, category: cat })
        });
        teachModal.classList.remove('active');
        heroWelcome.style.display = 'none';
        appendAiMessage(`🧠 **Knowledge Assimilated:** I have integrated this new fact into my neural core:\n\n> *"${fact}"*`, "Teach fact", {});
        neuralVis.triggerPulse();
        fetchTelemetry();
      } finally {
        btnSubmitTeach.textContent = 'Assimilate Fact';
      }
    });
  }

  // Ingest Modal
  if (btnQuickIngest) {
    btnQuickIngest.addEventListener('click', () => {
      ingestTextInput.value = '';
      ingestModal.classList.add('active');
    });
  }
  if (btnCloseIngestModal) btnCloseIngestModal.addEventListener('click', () => ingestModal.classList.remove('active'));
  if (btnCancelIngest) btnCancelIngest.addEventListener('click', () => ingestModal.classList.remove('active'));

  if (btnSubmitIngest) {
    btnSubmitIngest.addEventListener('click', async () => {
      const text = ingestTextInput.value.trim();
      if (!text) return;

      btnSubmitIngest.textContent = 'Digesting...';
      try {
        const resp = await fetch('/api/ingest', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text })
        });
        const data = await resp.json();
        ingestModal.classList.remove('active');
        heroWelcome.style.display = 'none';
        appendAiMessage(`📚 **Document Synthesized:** Discovered ${data.total_nodes || 0} concept entities and linked relational triples into the knowledge graph.`, "Digest Document", {});
        neuralVis.triggerPulse();
        fetchTelemetry();
      } finally {
        btnSubmitIngest.textContent = 'Digest & Learn';
      }
    });
  }

  // Correction Modal
  if (btnCloseCorrectModal) btnCloseCorrectModal.addEventListener('click', () => correctModal.classList.remove('active'));
  if (btnCancelCorrect) btnCancelCorrect.addEventListener('click', () => correctModal.classList.remove('active'));

  if (btnSubmitCorrection) {
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
        appendAiMessage(`🔧 **Adaptive Rule Synthesized:** I registered your ground truth and evolved my reasoning rules:\n\n> *"${corr}"*`, "Apply correction", {});
        neuralVis.triggerPulse();
        fetchTelemetry();
      } catch (e) {
        alert('Error applying correction: ' + e.message);
      }
    });
  }

  // ==========================================
  // 4. Simulation Controls
  // ==========================================
  if (btnSimStep) {
    btnSimStep.addEventListener('click', async () => {
      const resp = await fetch('/api/sim', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'step' })
      });
      const data = await resp.json();
      updateSimTelemetry(data);
      fetchSimState();
    });
  }

  if (btnSimAutoPlay) {
    btnSimAutoPlay.addEventListener('click', () => {
      isSimAutoRunning = !isSimAutoRunning;
      if (isSimAutoRunning) {
        btnSimAutoPlay.innerHTML = `<i data-lucide="pause"></i> Pause`;
        simAutoInterval = setInterval(async () => {
          const resp = await fetch('/api/sim', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'step' })
          });
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
  }

  if (btnSimTrainBatch) {
    btnSimTrainBatch.addEventListener('click', async () => {
      btnSimTrainBatch.textContent = 'Training...';
      try {
        await fetch('/api/sim', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'train', episodes: 25 })
        });
        fetchSimState();
      } finally {
        btnSimTrainBatch.innerHTML = `<i data-lucide="zap"></i> Train Batch (25 Ep)`;
        if (window.lucide) lucide.createIcons();
      }
    });
  }

  if (btnSimReset) {
    btnSimReset.addEventListener('click', async () => {
      await fetch('/api/sim', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'reset' })
      });
      fetchSimState();
    });
  }

  function updateSimTelemetry(data) {
    if (!data) return;
    const epVal = document.getElementById('simEpisodeVal');
    const stVal = document.getElementById('simStepsVal');
    const lossVal = document.getElementById('simLossVal');
    if (epVal) epVal.textContent = data.episode || 0;
    if (stVal) stVal.textContent = data.total_steps || 0;
    if (lossVal) lossVal.textContent = (data.td_loss !== undefined ? data.td_loss : 0.0).toFixed(3);
  }

  async function fetchSimState() {
    try {
      const resp = await fetch('/api/sim');
      const state = await resp.json();
      simViewer.updateState(state);
    } catch (e) {}
  }

  // ==========================================
  // 5. Telemetry & Memory Sync
  // ==========================================
  async function fetchTelemetry() {
    try {
      const resp = await fetch('/api/telemetry');
      const data = await resp.json();

      // Update sidebar telemetry
      const sideMem = document.getElementById('sideMemCount');
      const sideAcc = document.getElementById('sideAccuracy');
      const sidePlast = document.getElementById('sidePlasticity');
      if (sideMem) sideMem.textContent = data.memory.total_memories || '0';
      if (sideAcc) sideAcc.textContent = `${data.learning.accuracy_percentage || 96}%`;
      if (sidePlast) sidePlast.textContent = data.learning.synaptic_plasticity_index || '0.85';

      // Update Visualizers
      if (data.graph) kgViewer.updateGraph(data.graph);
      
      const memResp = await fetch('/api/memories');
      const memData = await memResp.json();
      if (memData.memories) {
        neuralVis.updateFromBrainData(memData.memories);

        // Populate sidebar memory chips
        const memList = document.getElementById('sidebarMemoryList');
        if (memList && memData.memories.length > 0) {
          memList.innerHTML = memData.memories.slice(0, 8).map(m => `
            <div class="memory-chip-item" title="${escapeHtml(m.content)}">
              <i data-lucide="sparkles" class="chip-ico"></i>
              <span class="chip-txt">${escapeHtml(m.content.length > 30 ? m.content.substring(0, 28) + '...' : m.content)}</span>
            </div>
          `).join('');
          if (window.lucide) lucide.createIcons();
        }
      }
    } catch (e) {}
  }

  // Initialize
  fetchTelemetry();
  fetchSimState();
  setInterval(fetchTelemetry, 4000);
});
