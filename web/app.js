/**
 * CogniPulse - Full Claude AI Frontend Engine
 * Includes Conversations Manager, Model Selector, Artifacts Split Canvas, and Live Web Grounding.
 */

document.addEventListener('DOMContentLoaded', () => {
  // ==========================================
  // 1. App State & Persistence
  // ==========================================
  let conversations = JSON.parse(localStorage.getItem('cognipulse_conversations') || '[]');
  let activeConvId = localStorage.getItem('cognipulse_active_conv_id') || null;
  let currentModel = localStorage.getItem('cognipulse_model') || 'sonnet-3.7';
  let isWebSearchEnabled = true;
  let currentAttachedFiles = []; // [{ name, sizeFormatted, text }]
  let activeArtifact = null; // { title, type, code }

  // Visualizers
  const neuralVis = new NeuralVisualizer('neuralCanvas');
  const kgViewer = new KnowledgeGraphViewer('graphCanvas');
  const simViewer = new SimulationViewer('simCanvas');

  // DOM Elements
  const appLayout = document.getElementById('appLayout');
  const sidebar = document.getElementById('sidebar');
  const btnToggleSidebar = document.getElementById('btnToggleSidebar');
  const btnOpenSidebarMobile = document.getElementById('btnOpenSidebarMobile');
  const btnNewChat = document.getElementById('btnNewChat');
  const inputSearchChats = document.getElementById('inputSearchChats');
  const conversationsList = document.getElementById('conversationsList');

  // Model Dropdown Elements
  const btnModelDropdown = document.getElementById('btnModelDropdown');
  const modelDropdownMenu = document.getElementById('modelDropdownMenu');
  const selectedModelLabel = document.getElementById('selectedModelLabel');
  const inputModelPill = document.getElementById('inputModelPill');
  const modelOptions = document.querySelectorAll('.model-option');

  // Chat Elements
  const heroWelcome = document.getElementById('heroWelcome');
  const messagesList = document.getElementById('messagesList');
  const chatMessagesScroll = document.getElementById('chatMessagesScroll');
  const chatInput = document.getElementById('chatInput');
  const btnSendChat = document.getElementById('btnSendChat');
  const btnUploadFile = document.getElementById('btnUploadFile');
  const fileInput = document.getElementById('fileInput');
  const attachedFilesContainer = document.getElementById('attachedFilesContainer');
  const btnToggleWebSearch = document.getElementById('btnToggleWebSearch');

  // Artifacts Canvas Drawer Elements
  const artifactsCanvasDrawer = document.getElementById('artifactsCanvasDrawer');
  const artifactTitle = document.getElementById('artifactTitle');
  const artifactTypeBadge = document.getElementById('artifactTypeBadge');
  const btnTabPreview = document.getElementById('btnTabPreview');
  const btnTabCode = document.getElementById('btnTabCode');
  const canvasPreviewPane = document.getElementById('canvasPreviewPane');
  const canvasCodePane = document.getElementById('canvasCodePane');
  const artifactIframe = document.getElementById('artifactIframe');
  const artifactCodeContent = document.getElementById('artifactCodeContent');
  const btnCopyArtifactCode = document.getElementById('btnCopyArtifactCode');
  const btnDownloadArtifact = document.getElementById('btnDownloadArtifact');
  const btnFullscreenArtifact = document.getElementById('btnFullscreenArtifact');
  const btnCloseArtifactsCanvas = document.getElementById('btnCloseArtifactsCanvas');

  // Navigation & Views
  const navItems = document.querySelectorAll('.nav-item');
  const viewPanels = document.querySelectorAll('.view-panel');
  const btnCloseViews = document.querySelectorAll('.btn-close-view');

  // Modals
  const aiSettingsModal = document.getElementById('aiSettingsModal');
  const btnHeaderAiSettings = document.getElementById('btnHeaderAiSettings');
  const btnSidebarAiSettings = document.getElementById('btnSidebarAiSettings');
  const btnCloseAiSettingsModal = document.getElementById('btnCloseAiSettingsModal');
  const aiProviderSelect = document.getElementById('aiProviderSelect');
  const inputCustomApiKey = document.getElementById('inputCustomApiKey');
  const btnSaveAiSettings = document.getElementById('btnSaveAiSettings');
  const btnClearApiKey = document.getElementById('btnClearApiKey');

  const teachModal = document.getElementById('teachModal');
  const btnHeaderTeach = document.getElementById('btnHeaderTeach');
  const btnSidebarTeach = document.getElementById('btnSidebarTeach');
  const btnCloseTeachModal = document.getElementById('btnCloseTeachModal');
  const btnCancelTeach = document.getElementById('btnCancelTeach');
  const btnSubmitTeach = document.getElementById('btnSubmitTeach');
  const modalFactText = document.getElementById('modalFactText');
  const modalFactCategory = document.getElementById('modalFactCategory');

  // ==========================================
  // 2. Sidebar & Navigation Logic
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

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const targetView = item.getAttribute('data-view');
      navItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');

      viewPanels.forEach(p => {
        p.classList.toggle('active', p.id === targetView);
      });

      if (targetView === 'neural-view') neuralVis.start();
      if (targetView === 'graph-view') kgViewer.start();
      if (targetView === 'sim-view') simViewer.start();
    });
  });

  btnCloseViews.forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelector('.nav-item[data-view="chat-view"]').click();
    });
  });

  // ==========================================
  // 3. Claude Model Selector
  // ==========================================
  const modelLabels = {
    'sonnet-3.7': 'CogniPulse 3.7 Sonnet',
    'haiku-3.5': 'CogniPulse 3.5 Haiku',
    'opus-3': 'CogniPulse Opus'
  };

  const modelShortPills = {
    'sonnet-3.7': 'Sonnet 3.7',
    'haiku-3.5': 'Haiku 3.5',
    'opus-3': 'Opus 3'
  };

  function updateSelectedModel(modelKey) {
    currentModel = modelKey;
    localStorage.setItem('cognipulse_model', modelKey);
    selectedModelLabel.textContent = modelLabels[modelKey] || 'CogniPulse 3.7 Sonnet';
    inputModelPill.textContent = modelShortPills[modelKey] || 'Sonnet 3.7';
    modelOptions.forEach(opt => {
      opt.classList.toggle('active', opt.getAttribute('data-model') === modelKey);
    });
  }

  updateSelectedModel(currentModel);

  btnModelDropdown.addEventListener('click', (e) => {
    e.stopPropagation();
    const isVisible = modelDropdownMenu.style.display === 'flex';
    modelDropdownMenu.style.display = isVisible ? 'none' : 'flex';
  });

  document.addEventListener('click', () => {
    if (modelDropdownMenu) modelDropdownMenu.style.display = 'none';
  });

  modelOptions.forEach(opt => {
    opt.addEventListener('click', () => {
      const m = opt.getAttribute('data-model');
      updateSelectedModel(m);
      modelDropdownMenu.style.display = 'none';
    });
  });

  // ==========================================
  // 4. Conversation History Management (Claude style)
  // ==========================================
  function createNewConversation() {
    const newConv = {
      id: 'conv_' + Date.now(),
      title: 'New Conversation',
      timestamp: Date.now(),
      messages: []
    };
    conversations.unshift(newConv);
    activeConvId = newConv.id;
    saveConversations();
    renderConversationsList();
    loadActiveConversation();
    chatInput.focus();
  }

  function saveConversations() {
    localStorage.setItem('cognipulse_conversations', JSON.stringify(conversations));
    localStorage.setItem('cognipulse_active_conv_id', activeConvId);
  }

  function renderConversationsList() {
    if (!conversationsList) return;
    const searchFilter = (inputSearchChats ? inputSearchChats.value.trim().toLowerCase() : '');

    const filtered = conversations.filter(c => !searchFilter || c.title.toLowerCase().includes(searchFilter));

    if (filtered.length === 0) {
      conversationsList.innerHTML = `<div style="padding: 10px; font-size: 11.5px; color: var(--text-dim);">No conversations yet.</div>`;
      return;
    }

    conversationsList.innerHTML = filtered.map(c => `
      <div class="conversation-item ${c.id === activeConvId ? 'active' : ''}" data-id="${c.id}">
        <div class="conv-title-wrap">
          <i data-lucide="message-square"></i>
          <span class="conv-title-text">${escapeHtml(c.title)}</span>
        </div>
        <button class="conv-delete-btn" title="Delete Conversation" data-id="${c.id}">
          <i data-lucide="trash-2"></i>
        </button>
      </div>
    `).join('');

    if (window.lucide) lucide.createIcons();

    conversationsList.querySelectorAll('.conversation-item').forEach(item => {
      item.addEventListener('click', (e) => {
        if (e.target.closest('.conv-delete-btn')) return;
        const id = item.getAttribute('data-id');
        activeConvId = id;
        saveConversations();
        renderConversationsList();
        loadActiveConversation();
      });
    });

    conversationsList.querySelectorAll('.conv-delete-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const id = btn.getAttribute('data-id');
        conversations = conversations.filter(c => c.id !== id);
        if (activeConvId === id) {
          activeConvId = conversations.length > 0 ? conversations[0].id : null;
        }
        saveConversations();
        renderConversationsList();
        loadActiveConversation();
      });
    });
  }

  function loadActiveConversation() {
    messagesList.innerHTML = '';
    closeArtifactsCanvas();

    const activeConv = conversations.find(c => c.id === activeConvId);
    if (!activeConv || !activeConv.messages || activeConv.messages.length === 0) {
      heroWelcome.style.display = 'flex';
      return;
    }

    heroWelcome.style.display = 'none';
    activeConv.messages.forEach(msg => {
      if (msg.role === 'user') {
        appendUserMessageDOM(msg.content, msg.attachedFiles || [], false);
      } else {
        appendAiMessageDOM(msg.content, msg.fullData || {}, false);
      }
    });
    scrollToBottom();
  }

  btnNewChat.addEventListener('click', createNewConversation);

  // Keyboard shortcut Ctrl+K / Cmd+K for New Chat
  window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      createNewConversation();
    }
  });

  if (inputSearchChats) {
    inputSearchChats.addEventListener('input', renderConversationsList);
  }

  // Suggestion Cards
  document.querySelectorAll('.suggestion-card').forEach(card => {
    card.addEventListener('click', () => {
      const prompt = card.getAttribute('data-prompt');
      chatInput.value = prompt;
      handleSendMessage();
    });
  });

  // Web Search Toggle
  if (btnToggleWebSearch) {
    btnToggleWebSearch.addEventListener('click', () => {
      isWebSearchEnabled = !isWebSearchEnabled;
      btnToggleWebSearch.classList.toggle('active', isWebSearchEnabled);
      btnToggleWebSearch.title = isWebSearchEnabled ? "Live Web Search: ON" : "Live Web Search: OFF";
    });
  }

  // ==========================================
  // 5. File Upload & PDF Document Handling
  // ==========================================
  if (btnUploadFile && fileInput) {
    btnUploadFile.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => {
      handleFilesSelected(e.target.files);
      fileInput.value = '';
    });
  }

  window.addEventListener('dragover', (e) => e.preventDefault());
  window.addEventListener('drop', (e) => {
    e.preventDefault();
    if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFilesSelected(e.dataTransfer.files);
    }
  });

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  }

  async function handleFilesSelected(files) {
    if (!files || files.length === 0) return;

    for (const file of Array.from(files)) {
      const isPdf = file.name.toLowerCase().endsWith('.pdf');
      if (isPdf) {
        try {
          const arrayBuffer = await file.arrayBuffer();
          const pdfjs = window.pdfjsLib || window['pdfjs-dist/build/pdf'];
          if (pdfjs) {
            pdfjs.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
            const loadingTask = pdfjs.getDocument({ data: arrayBuffer });
            const pdfDoc = await loadingTask.promise;
            let fullText = '';
            for (let i = 1; i <= Math.min(pdfDoc.numPages, 20); i++) {
              const page = await pdfDoc.getPage(i);
              const content = await page.getTextContent();
              const pageStr = content.items.map(item => item.str).join(' ');
              fullText += `[Page ${i}]\n${pageStr}\n\n`;
            }
            currentAttachedFiles.push({
              name: file.name,
              sizeFormatted: formatBytes(file.size),
              text: fullText.trim() || `[Document: ${file.name}]`
            });
            renderAttachedPills();
          }
        } catch (err) {
          currentAttachedFiles.push({
            name: file.name,
            sizeFormatted: formatBytes(file.size),
            text: `[Document: ${file.name}]`
          });
          renderAttachedPills();
        }
      } else {
        const reader = new FileReader();
        reader.onload = (e) => {
          currentAttachedFiles.push({
            name: file.name,
            sizeFormatted: formatBytes(file.size),
            text: e.target.result
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

  // Auto-grow textarea
  chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 180) + 'px';
  });

  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });

  btnSendChat.addEventListener('click', () => handleSendMessage());

  // ==========================================
  // 6. Chat Message Pipeline & API Inference
  // ==========================================
  async function handleSendMessage(overrideText = null) {
    let rawText = overrideText !== null ? overrideText.trim() : chatInput.value.trim();

    if (!rawText && currentAttachedFiles.length > 0) {
      rawText = "Please analyze and simplify the attached document.";
    }

    if (!rawText && currentAttachedFiles.length === 0) return;

    if (!activeConvId) {
      createNewConversation();
    }

    const filesToUpload = [...currentAttachedFiles];
    currentAttachedFiles = [];
    renderAttachedPills();

    // Prepare full query with document context if present
    let fullQueryPayload = rawText;
    if (filesToUpload.length > 0) {
      const filesContext = filesToUpload.map(f => `--- FILE: ${f.name} ---\n${f.text}\n--- END OF FILE ---`).join('\n\n');
      fullQueryPayload = `${filesContext}\n\nUser Instruction: ${rawText}`;
    }

    // Hide hero
    heroWelcome.style.display = 'none';

    // Append to active conversation state
    const activeConv = conversations.find(c => c.id === activeConvId);
    if (activeConv) {
      if (activeConv.messages.length === 0) {
        activeConv.title = rawText.length > 28 ? rawText.substring(0, 26) + '...' : rawText;
        renderConversationsList();
      }
      activeConv.messages.push({
        role: 'user',
        content: rawText,
        attachedFiles: filesToUpload,
        timestamp: Date.now()
      });
      saveConversations();
    }

    // Append user bubble to DOM
    if (overrideText === null) {
      appendUserMessageDOM(rawText, filesToUpload);
      chatInput.value = '';
      chatInput.style.height = 'auto';
    }

    // Thinking placeholder
    const thinkingRow = appendThinkingPlaceholder();
    neuralVis.triggerPulse();

    const savedApiKey = localStorage.getItem('cognipulse_api_key') || null;
    const savedProvider = localStorage.getItem('cognipulse_ai_provider') || 'auto';

    try {
      const resp = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: fullQueryPayload,
          apiKey: savedApiKey,
          provider: savedProvider,
          model: currentModel,
          webSearch: isWebSearchEnabled
        })
      });
      const data = await resp.json();

      thinkingRow.remove();

      if (!resp.ok || data.error) {
        appendSystemError(`CogniPulse Error: ${data.error || 'Unexpected response'}`);
        return;
      }

      const responseText = data.response || 'Knowledge assimilated.';

      if (activeConv) {
        activeConv.messages.push({
          role: 'assistant',
          content: responseText,
          fullData: data,
          timestamp: Date.now()
        });
        saveConversations();
      }

      appendAiMessageDOM(responseText, data);

      // Check if response contains runnable web artifact
      detectAndRenderArtifact(responseText);

      if (data.firing_event && data.firing_event.activated_memories) {
        neuralVis.triggerPulse(data.firing_event.activated_memories);
      }

      fetchTelemetry();
    } catch (err) {
      thinkingRow.remove();
      appendSystemError(`Error connecting to CogniPulse: ${err.message}`);
    }
  }

  function appendUserMessageDOM(content, attachedFiles = [], shouldScroll = true) {
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
        <button class="btn-user-action btn-edit-msg" title="Edit Prompt">
          <i data-lucide="edit-3"></i> Edit
        </button>
        <button class="btn-user-action btn-retry-msg" title="Retry Prompt">
          <i data-lucide="rotate-cw"></i> Retry
        </button>
        <button class="btn-user-action btn-copy-user-msg" title="Copy Prompt">
          <i data-lucide="copy"></i> Copy
        </button>
      </div>
    `;

    messagesList.appendChild(row);
    if (window.lucide) lucide.createIcons();
    if (shouldScroll) scrollToBottom();

    // Copy Action
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

    // Retry Action
    const btnRetry = row.querySelector('.btn-retry-msg');
    if (btnRetry) {
      btnRetry.addEventListener('click', () => handleSendMessage(content));
    }

    // Inline Edit Action
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
          editBox.remove();
          userBubble.style.display = 'block';
          actionsBar.style.display = 'flex';
          handleSendMessage(newContent);
        });
      });
    }
  }

  function appendThinkingPlaceholder() {
    const row = document.createElement('div');
    row.className = 'chat-row-ai';
    row.innerHTML = `
      <div class="ai-avatar"><img src="logo.svg" alt="CogniPulse" style="width:100%;height:100%;object-fit:contain;"></div>
      <div class="ai-body">
        <div class="thought-accordion">
          <div class="thought-summary-btn" style="cursor:default;">
            <div class="thought-title-wrap">
              <i data-lucide="loader-2" class="spin"></i>
              <span>CogniPulse is thinking & synthesizing...</span>
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

  function appendAiMessageDOM(responseContent, fullData = {}, shouldScroll = true) {
    const row = document.createElement('div');
    row.className = 'chat-row-ai';

    const latency = fullData && fullData.latency_ms ? fullData.latency_ms : '14';
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
      <div class="ai-avatar"><img src="logo.svg" alt="CogniPulse" style="width:100%;height:100%;object-fit:contain;"></div>
      <div class="ai-body">
        
        <!-- Claude Thinking Accordion -->
        <div class="thought-accordion">
          <button class="thought-summary-btn">
            <div class="thought-title-wrap">
              <i data-lucide="sparkles"></i>
              <span>Thought Process (${latency}ms)</span>
            </div>
            <i data-lucide="chevron-down" class="acc-chevron"></i>
          </button>
          <div class="thought-content-box">
            ${thoughtStepsHtml || '<div class="text-sm text-muted">Associative recall and reasoning completed.</div>'}
          </div>
        </div>

        <!-- AI Markdown Content -->
        <div class="ai-text">${formattedText}</div>

        <!-- AI Actions Toolbar -->
        <div class="ai-actions-bar">
          <button class="btn-ai-action btn-copy-ai" title="Copy Response">
            <i data-lucide="copy"></i> Copy
          </button>
          <button class="btn-ai-action btn-good" title="Good Response">
            <i data-lucide="thumbs-up"></i>
          </button>
          <button class="btn-ai-action btn-bad" title="Needs Correction">
            <i data-lucide="thumbs-down"></i>
          </button>
        </div>
      </div>
    `;

    messagesList.appendChild(row);
    if (window.lucide) lucide.createIcons();
    if (shouldScroll) scrollToBottom();

    // Accordion Toggle
    const thoughtBtn = row.querySelector('.thought-summary-btn');
    const thoughtBox = row.querySelector('.thought-content-box');
    if (thoughtBtn && thoughtBox) {
      thoughtBtn.addEventListener('click', () => {
        thoughtBox.classList.toggle('open');
      });
    }

    // Copy Response
    const btnCopy = row.querySelector('.btn-copy-ai');
    if (btnCopy) {
      btnCopy.addEventListener('click', () => {
        navigator.clipboard.writeText(responseContent);
        btnCopy.innerHTML = `<i data-lucide="check"></i> Copied`;
        if (window.lucide) lucide.createIcons();
        setTimeout(() => {
          btnCopy.innerHTML = `<i data-lucide="copy"></i> Copy`;
          if (window.lucide) lucide.createIcons();
        }, 1500);
      });
    }

    // Feedback
    const btnGood = row.querySelector('.btn-good');
    const btnBad = row.querySelector('.btn-bad');
    if (btnGood) {
      btnGood.addEventListener('click', () => {
        btnGood.style.color = 'var(--primary-emerald)';
        fetch('/api/feedback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: 'Response feedback', response: responseContent, is_positive: true })
        });
      });
    }
    if (btnBad) {
      btnBad.addEventListener('click', () => {
        btnBad.style.color = 'var(--primary-rose)';
        fetch('/api/feedback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: 'Response feedback', response: responseContent, is_positive: false })
        });
      });
    }
  }

  function appendSystemError(errMsg) {
    const row = document.createElement('div');
    row.className = 'chat-row-ai';
    row.innerHTML = `
      <div class="ai-avatar"><img src="logo.svg" alt="CogniPulse" style="width:100%;height:100%;object-fit:contain;"></div>
      <div class="ai-body">
        <div class="ai-text" style="color: var(--primary-rose);">${escapeHtml(errMsg)}</div>
      </div>
    `;
    messagesList.appendChild(row);
    if (window.lucide) lucide.createIcons();
    scrollToBottom();
  }

  // ==========================================
  // 7. Claude Interactive Artifacts / Canvas Engine
  // ==========================================
  function detectAndRenderArtifact(responseText) {
    // Check for HTML/JS/SVG code blocks
    const htmlBlockMatch = responseText.match(/```(?:html|svg|xml)\n([\s\S]*?)```/i);
    if (htmlBlockMatch) {
      const code = htmlBlockMatch[1];
      openArtifact({
        title: "Interactive Web Artifact",
        type: "HTML / Web App",
        code: code
      });
    }
  }

  function openArtifact(artData) {
    activeArtifact = artData;
    artifactTitle.textContent = artData.title;
    artifactTypeBadge.textContent = artData.type;
    artifactCodeContent.textContent = artData.code;

    // Load iframe live preview
    const doc = artifactIframe.contentDocument || artifactIframe.contentWindow.document;
    doc.open();
    doc.write(artData.code);
    doc.close();

    artifactsCanvasDrawer.style.display = 'flex';
    setCanvasTab('preview');
  }

  function closeArtifactsCanvas() {
    artifactsCanvasDrawer.style.display = 'none';
    artifactsCanvasDrawer.classList.remove('fullscreen');
  }

  function setCanvasTab(tab) {
    if (tab === 'preview') {
      btnTabPreview.classList.add('active');
      btnTabCode.classList.remove('active');
      canvasPreviewPane.style.display = 'block';
      canvasCodePane.style.display = 'none';
    } else {
      btnTabCode.classList.add('active');
      btnTabPreview.classList.remove('active');
      canvasCodePane.style.display = 'block';
      canvasPreviewPane.style.display = 'none';
    }
  }

  btnTabPreview.addEventListener('click', () => setCanvasTab('preview'));
  btnTabCode.addEventListener('click', () => setCanvasTab('code'));
  btnCloseArtifactsCanvas.addEventListener('click', closeArtifactsCanvas);

  btnCopyArtifactCode.addEventListener('click', () => {
    if (activeArtifact && activeArtifact.code) {
      navigator.clipboard.writeText(activeArtifact.code);
      btnCopyArtifactCode.innerHTML = `<i data-lucide="check"></i>`;
      if (window.lucide) lucide.createIcons();
      setTimeout(() => {
        btnCopyArtifactCode.innerHTML = `<i data-lucide="copy"></i>`;
        if (window.lucide) lucide.createIcons();
      }, 1500);
    }
  });

  btnDownloadArtifact.addEventListener('click', () => {
    if (activeArtifact && activeArtifact.code) {
      const blob = new Blob([activeArtifact.code], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${activeArtifact.title.toLowerCase().replace(/\s+/g, '_')}.html`;
      a.click();
      URL.revokeObjectURL(url);
    }
  });

  btnFullscreenArtifact.addEventListener('click', () => {
    artifactsCanvasDrawer.classList.toggle('fullscreen');
  });

  // ==========================================
  // 8. Markdown Parser & Typography Engine
  // ==========================================
  function escapeHtml(str) {
    return (str || '').toString().replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function formatMarkdown(text) {
    if (!text) return '';
    let t = escapeHtml(text);

    // 1. Code blocks (```lang ... ```)
    t = t.replace(/```([a-zA-Z0-9_\-]*)?\n([\s\S]*?)```/g, (match, lang, code) => {
      return `<pre class="code-block-wrap"><code class="lang-${lang || 'text'}">${code.trim()}</code></pre>`;
    });

    // 2. Inline code (`code`)
    t = t.replace(/`([^`\n]+)`/g, '<code class="inline-code">$1</code>');

    // 3. Headings (###, ##, #)
    t = t.replace(/^###\s+(.*?)$/gm, '<h3 class="md-h3">$1</h3>');
    t = t.replace(/^##\s+(.*?)$/gm, '<h2 class="md-h2">$1</h2>');
    t = t.replace(/^#\s+(.*?)$/gm, '<h1 class="md-h1">$1</h1>');

    // 4. Blockquotes (> quote)
    t = t.replace(/^>\s+(.*?)$/gm, '<blockquote class="md-quote">$1</blockquote>');

    // 5. Bold & Italic
    t = t.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    t = t.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // 6. Bullet lists (• item or - item or * item)
    t = t.replace(/^[•\-\*]\s+(.*?)$/gm, '<li class="md-li">$1</li>');
    t = t.replace(/(<li class="md-li">[\s\S]*?<\/li>)/g, (match) => `<ul class="md-ul">${match}</ul>`);
    t = t.replace(/<\/ul>\s*<ul class="md-ul">/g, '');

    // 7. Numbered lists (1. item, 2. item)
    t = t.replace(/^\d+\.\s+(.*?)$/gm, '<li class="md-oli">$1</li>');
    t = t.replace(/(<li class="md-oli">[\s\S]*?<\/li>)/g, (match) => `<ol class="md-ol">${match}</ol>`);
    t = t.replace(/<\/ol>\s*<ol class="md-ol">/g, '');

    // 8. Paragraphs and clean spacing
    const blocks = t.split(/\n{2,}/);
    t = blocks.map(b => {
      b = b.trim();
      if (!b) return '';
      if (b.startsWith('<h') || b.startsWith('<pre') || b.startsWith('<ul') || b.startsWith('<ol') || b.startsWith('<blockquote')) {
        return b;
      }
      return `<p class="md-p">${b.replace(/\n/g, '<br/>')}</p>`;
    }).join('');

    return t;
  }

  function scrollToBottom() {
    chatMessagesScroll.scrollTop = chatMessagesScroll.scrollHeight;
  }

  // ==========================================
  // 9. Modals (AI Settings & Teach Fact)
  // ==========================================
  function openAiSettings() {
    aiSettingsModal.style.display = 'flex';
    aiSettingsModal.classList.add('active');
    if (aiProviderSelect) aiProviderSelect.value = localStorage.getItem('cognipulse_ai_provider') || 'auto';
    if (inputCustomApiKey) inputCustomApiKey.value = localStorage.getItem('cognipulse_api_key') || '';
  }

  function closeAiSettings() {
    aiSettingsModal.style.display = 'none';
    aiSettingsModal.classList.remove('active');
  }

  if (btnHeaderAiSettings) btnHeaderAiSettings.addEventListener('click', openAiSettings);
  if (btnSidebarAiSettings) btnSidebarAiSettings.addEventListener('click', openAiSettings);
  if (btnCloseAiSettingsModal) btnCloseAiSettingsModal.addEventListener('click', closeAiSettings);

  if (btnSaveAiSettings) {
    btnSaveAiSettings.addEventListener('click', () => {
      const p = aiProviderSelect.value;
      const k = inputCustomApiKey.value.trim();
      localStorage.setItem('cognipulse_ai_provider', p);
      if (k) localStorage.setItem('cognipulse_api_key', k);
      else localStorage.removeItem('cognipulse_api_key');
      closeAiSettings();
      alert('AI Engine settings saved!');
    });
  }

  if (btnClearApiKey) {
    btnClearApiKey.addEventListener('click', () => {
      localStorage.removeItem('cognipulse_api_key');
      inputCustomApiKey.value = '';
      alert('API Key cleared.');
    });
  }

  function openTeachModal() {
    modalFactText.value = '';
    teachModal.style.display = 'flex';
    teachModal.classList.add('active');
    modalFactText.focus();
  }

  function closeTeachModal() {
    teachModal.style.display = 'none';
    teachModal.classList.remove('active');
  }

  if (btnHeaderTeach) btnHeaderTeach.addEventListener('click', openTeachModal);
  if (btnSidebarTeach) btnSidebarTeach.addEventListener('click', openTeachModal);
  if (btnCloseTeachModal) btnCloseTeachModal.addEventListener('click', closeTeachModal);
  if (btnCancelTeach) btnCancelTeach.addEventListener('click', closeTeachModal);

  // Close modals on outside click or ESC key
  window.addEventListener('click', (e) => {
    if (e.target === teachModal) closeTeachModal();
    if (e.target === aiSettingsModal) closeAiSettings();
  });

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeTeachModal();
      closeAiSettings();
      closeArtifactsCanvas();
    }
  });

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
        closeTeachModal();
        appendAiMessageDOM(`🧠 **Knowledge Assimilated:** I have integrated this new fact into my neural core:\n\n> *"${fact}"*`);
        neuralVis.triggerPulse();
        fetchTelemetry();
      } finally {
        btnSubmitTeach.textContent = 'Assimilate Fact';
      }
    });
  }


  // ==========================================
  // 10. Background Telemetry & Initialization
  // ==========================================
  async function fetchTelemetry() {
    try {
      const resp = await fetch('/api/telemetry');
      const data = await resp.json();
      if (data.graph) kgViewer.updateGraph(data.graph);
    } catch (e) {}
  }

  // Initialize conversations
  if (conversations.length === 0) {
    createNewConversation();
  } else {
    renderConversationsList();
    loadActiveConversation();
  }

  fetchTelemetry();
  setInterval(fetchTelemetry, 6000);
});
