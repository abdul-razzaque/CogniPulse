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
  let currentAttachedFiles = []; // [{ name, sizeFormatted, text }]

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

  // File Upload Elements
  const btnUploadFile = document.getElementById('btnUploadFile');
  const fileInput = document.getElementById('fileInput');
  const attachedFilesContainer = document.getElementById('attachedFilesContainer');

  // Header quick buttons
  const btnHeaderTeach = document.getElementById('btnHeaderTeach');
  const btnHeaderBrainView = document.getElementById('btnHeaderBrainView');
  const btnQuickTeach = document.getElementById('btnQuickTeach');
  const btnQuickIngest = document.getElementById('btnQuickIngest');

  // ==========================================
  // File Upload & Attachment Handlers
  // ==========================================
  if (btnUploadFile && fileInput) {
    btnUploadFile.addEventListener('click', () => {
      fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
      handleFilesSelected(e.target.files);
      fileInput.value = '';
    });
  }

  // Drag & Drop onto Chat
  window.addEventListener('dragover', (e) => {
    e.preventDefault();
  });

  window.addEventListener('drop', (e) => {
    e.preventDefault();
    if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFilesSelected(e.dataTransfer.files);
    }
  });

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
  }

  async function handleFilesSelected(files) {
    if (!files || files.length === 0) return;

    for (const file of Array.from(files)) {
      const fileNameLower = file.name.toLowerCase();

      if (fileNameLower.endsWith('.pdf')) {
        try {
          const arrayBuffer = await file.arrayBuffer();
          const pdfjs = window.pdfjsLib || window['pdfjs-dist/build/pdf'];
          if (pdfjs) {
            pdfjs.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
            const loadingTask = pdfjs.getDocument({ data: arrayBuffer });
            const pdfDoc = await loadingTask.promise;
            let fullText = '';
            for (let i = 1; i <= Math.min(pdfDoc.numPages, 25); i++) {
              const page = await pdfDoc.getPage(i);
              const textContent = await page.getTextContent();
              const pageStrings = textContent.items.map(item => item.str).join(' ');
              fullText += `[Page ${i}]\n${pageStrings}\n\n`;
            }
            currentAttachedFiles.push({
              name: file.name,
              sizeFormatted: formatBytes(file.size),
              text: fullText.trim() || `[PDF Document: ${file.name} - ${pdfDoc.numPages} Pages]`
            });
            renderAttachedPills();
          } else {
            currentAttachedFiles.push({
              name: file.name,
              sizeFormatted: formatBytes(file.size),
              text: `[PDF Document: ${file.name}]`
            });
            renderAttachedPills();
          }
        } catch (err) {
          console.error("PDF Parsing Error:", err);
          currentAttachedFiles.push({
            name: file.name,
            sizeFormatted: formatBytes(file.size),
            text: `[PDF Document: ${file.name}]`
          });
          renderAttachedPills();
        }
      } else {
        // Plain text, code, JSON, CSV, Markdown, etc.
        const reader = new FileReader();
        reader.onload = (event) => {
          currentAttachedFiles.push({
            name: file.name,
            sizeFormatted: formatBytes(file.size),
            text: event.target.result
          });
          renderAttachedPills();
        };
        reader.readAsText(file);
      }
    }
  }


  function renderAttachedPills() {
    if (!attachedFilesContainer) return;
    if (currentAttachedFiles.length === 0) {
      attachedFilesContainer.style.display = 'none';
      attachedFilesContainer.innerHTML = '';
      return;
    }

    attachedFilesContainer.style.display = 'flex';
    attachedFilesContainer.innerHTML = currentAttachedFiles.map((f, idx) => `
      <div class="attached-file-pill">
        <i data-lucide="file-code"></i>
        <span class="file-pill-name">${escapeHtml(f.name)}</span>
        <span class="file-pill-size">${f.sizeFormatted}</span>
        <button class="file-pill-remove" data-idx="${idx}">&times;</button>
      </div>
    `).join('');

    if (window.lucide) lucide.createIcons();

    attachedFilesContainer.querySelectorAll('.file-pill-remove').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const idx = parseInt(e.target.getAttribute('data-idx'), 10);
        currentAttachedFiles.splice(idx, 1);
        renderAttachedPills();
      });
    });
  }


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

  // AI Settings Elements & Modals
  const aiSettingsModal = document.getElementById('aiSettingsModal');
  const btnOpenAiSettings = document.getElementById('btnOpenAiSettings');
  const btnCloseAiSettingsModal = document.getElementById('btnCloseAiSettingsModal');
  const aiProviderSelect = document.getElementById('aiProviderSelect');
  const inputCustomApiKey = document.getElementById('inputCustomApiKey');
  const btnSaveAiSettings = document.getElementById('btnSaveAiSettings');
  const btnClearApiKey = document.getElementById('btnClearApiKey');

  // Load saved settings
  const savedProvider = localStorage.getItem('cognipulse_ai_provider') || 'auto';
  const savedApiKey = localStorage.getItem('cognipulse_api_key') || '';
  if (aiProviderSelect) aiProviderSelect.value = savedProvider;
  if (inputCustomApiKey) inputCustomApiKey.value = savedApiKey;

  if (btnOpenAiSettings && aiSettingsModal) {
    btnOpenAiSettings.addEventListener('click', () => {
      aiSettingsModal.style.display = 'flex';
      if (inputCustomApiKey) inputCustomApiKey.value = localStorage.getItem('cognipulse_api_key') || '';
      if (aiProviderSelect) aiProviderSelect.value = localStorage.getItem('cognipulse_ai_provider') || 'auto';
    });
  }

  if (btnCloseAiSettingsModal && aiSettingsModal) {
    btnCloseAiSettingsModal.addEventListener('click', () => {
      aiSettingsModal.style.display = 'none';
    });
  }

  if (btnSaveAiSettings) {
    btnSaveAiSettings.addEventListener('click', () => {
      const p = aiProviderSelect ? aiProviderSelect.value : 'auto';
      const k = inputCustomApiKey ? inputCustomApiKey.value.trim() : '';
      localStorage.setItem('cognipulse_ai_provider', p);
      if (k) {
        localStorage.setItem('cognipulse_api_key', k);
      } else {
        localStorage.removeItem('cognipulse_api_key');
      }
      aiSettingsModal.style.display = 'none';
      alert('AI Engine settings saved successfully!');
    });
  }

  if (btnClearApiKey) {
    btnClearApiKey.addEventListener('click', () => {
      localStorage.removeItem('cognipulse_api_key');
      if (inputCustomApiKey) inputCustomApiKey.value = '';
      alert('API Key cleared.');
    });
  }

  // ==========================================
  // 2. Chat Message Flow & Thought Accordion
  // ==========================================
  async function handleSendMessage(overrideText = null) {
    let rawText = overrideText !== null ? overrideText.trim() : chatInput.value.trim();
    
    // If no text but files are attached, provide default prompt
    if (!rawText && currentAttachedFiles.length > 0) {
      rawText = "Please analyze and extract insights from the attached file(s).";
    }

    if (!rawText && currentAttachedFiles.length === 0) return;

    // Snapshot attached files
    const filesToUpload = [...currentAttachedFiles];
    currentAttachedFiles = [];
    renderAttachedPills();

    // Prepare full query with file contents for CogniPulse
    let fullQueryPayload = rawText;
    if (filesToUpload.length > 0) {
      const filesContext = filesToUpload.map(f => `--- FILE: ${f.name} ---\n${f.text}\n--- END OF FILE ---`).join('\n\n');
      fullQueryPayload = `${filesContext}\n\nUser Question/Instruction: ${rawText}`;
    }

    // Hide hero welcome
    heroWelcome.style.display = 'none';

    // Append User Bubble with attached file badges
    if (overrideText === null) {
      appendUserMessage(rawText, filesToUpload);
      chatInput.value = '';
      chatInput.style.height = 'auto';
    }

    // Add Thinking Placeholder
    const thinkingRow = appendThinkingPlaceholder();

    // Trigger visual pulse
    neuralVis.triggerPulse();

    const currentApiKey = localStorage.getItem('cognipulse_api_key') || null;
    const currentProvider = localStorage.getItem('cognipulse_ai_provider') || 'auto';

    try {
      const resp = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: fullQueryPayload,
          apiKey: currentApiKey,
          provider: currentProvider
        })
      });
      const data = await resp.json();

      // Remove thinking placeholder
      thinkingRow.remove();

      if (!resp.ok || data.error) {
        appendSystemError(`CogniPulse Error: ${data.error || 'Unexpected response'}`);
        return;
      }

      // Render AI Message with Collapsible Thought Stream
      appendAiMessage(data.response || 'Knowledge assimilated.', rawText, data);

      if (data.firing_event && data.firing_event.activated_memories) {
        neuralVis.triggerPulse(data.firing_event.activated_memories);
      }

      fetchTelemetry();
    } catch (err) {
      thinkingRow.remove();
      appendSystemError(`Error connecting to CogniPulse: ${err.message}`);
    }
  }


  function appendUserMessage(content, attachedFiles = []) {
    const row = document.createElement('div');
    row.className = 'chat-row-user';

    let filesBadgesHtml = '';
    if (attachedFiles && attachedFiles.length > 0) {
      filesBadgesHtml = attachedFiles.map(f => `
        <div class="user-attached-file-badge">
          <i data-lucide="file-code"></i> ${escapeHtml(f.name)} (${f.sizeFormatted})
        </div>
      `).join('');
    }

    row.innerHTML = `
      <div class="user-bubble">
        ${filesBadgesHtml}
        ${escapeHtml(content).replace(/\n/g, '<br/>')}
      </div>
      <div class="user-actions-bar">
        <button class="btn-user-action btn-edit-msg" title="Edit Question">
          <i data-lucide="edit-3"></i> Edit
        </button>
        <button class="btn-user-action btn-retry-msg" title="Ask Again / Re-question">
          <i data-lucide="rotate-cw"></i> Ask Again
        </button>
        <button class="btn-user-action btn-copy-user-msg" title="Copy Question">
          <i data-lucide="copy"></i> Copy
        </button>
      </div>
    `;

    messagesList.appendChild(row);
    if (window.lucide) lucide.createIcons();
    scrollToBottom();


    // 1. Copy User Message
    const btnCopy = row.querySelector('.btn-copy-user-msg');
    if (btnCopy) {
      btnCopy.addEventListener('click', () => {
        navigator.clipboard.writeText(content);
        btnCopy.innerHTML = `<i data-lucide="check"></i> Copied`;
        if (window.lucide) lucide.createIcons();
        setTimeout(() => {
          btnCopy.innerHTML = `<i data-lucide="copy"></i> Copy`;
          if (window.lucide) lucide.createIcons();
        }, 1500);
      });
    }

    // 2. Retry / Re-question
    const btnRetry = row.querySelector('.btn-retry-msg');
    if (btnRetry) {
      btnRetry.addEventListener('click', () => {
        handleSendMessage(content);
      });
    }

    // 3. Inline Edit
    const btnEdit = row.querySelector('.btn-edit-msg');
    const userBubble = row.querySelector('.user-bubble');
    const actionsBar = row.querySelector('.user-actions-bar');

    if (btnEdit) {
      btnEdit.addEventListener('click', () => {
        userBubble.style.display = 'none';
        actionsBar.style.display = 'none';

        const editBox = document.createElement('div');
        editBox.className = 'user-inline-edit-box';
        editBox.innerHTML = `
          <textarea rows="2">${escapeHtml(content)}</textarea>
          <div class="user-inline-edit-actions">
            <button class="btn-inline-cancel">Cancel</button>
            <button class="btn-inline-save">Save & Submit</button>
          </div>
        `;

        row.prepend(editBox);
        const editArea = editBox.querySelector('textarea');
        editArea.focus();
        editArea.setSelectionRange(editArea.value.length, editArea.value.length);

        const btnCancel = editBox.querySelector('.btn-inline-cancel');
        const btnSave = editBox.querySelector('.btn-inline-save');

        btnCancel.addEventListener('click', () => {
          editBox.remove();
          userBubble.style.display = 'block';
          actionsBar.style.display = 'flex';
        });

        btnSave.addEventListener('click', () => {
          const newContent = editArea.value.trim();
          if (!newContent) return;

          content = newContent;
          userBubble.innerHTML = escapeHtml(newContent).replace(/\n/g, '<br/>');
          editBox.remove();
          userBubble.style.display = 'block';
          actionsBar.style.display = 'flex';

          // Resubmit edited question to CogniPulse
          handleSendMessage(newContent);
        });
      });
    }
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
      <div class="ai-avatar"><img src="logo.svg" alt="CogniPulse" style="width:100%; height:100%; object-fit:contain;"></div>
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
