/**
 * CogniPulse - Dynamic Knowledge Graph Explorer
 * Renders concept nodes, labeled directional edges, and relational subgraphs.
 */

class KnowledgeGraphViewer {
  constructor(canvasId, detailsId) {
    this.canvas = document.getElementById(canvasId);
    this.detailsElem = document.getElementById(detailsId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');

    this.nodes = [];
    this.edges = [];
    this.hoveredNode = null;
    this.selectedNode = null;
    this.searchTerm = "";

    this.initCanvas();
    this.bindEvents();
    this.animate();
  }

  initCanvas() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.width = this.canvas.width = rect.width || 800;
    this.height = this.canvas.height = 500;
    this.center = { x: this.width / 2, y: this.height / 2 };

    window.addEventListener('resize', () => {
      if (!this.canvas.parentElement) return;
      const r = this.canvas.parentElement.getBoundingClientRect();
      this.width = this.canvas.width = r.width || 800;
      this.height = this.canvas.height = 500;
      this.center = { x: this.width / 2, y: this.height / 2 };
    });
  }

  updateGraph(graphData) {
    if (!graphData || !graphData.nodes) return;

    const existingMap = new Map(this.nodes.map(n => [n.id, n]));
    const total = graphData.nodes.length;

    this.nodes = graphData.nodes.map((n, idx) => {
      const existing = existingMap.get(n.id);
      if (existing) {
        existing.occurrences = n.occurrences;
        existing.description = n.description;
        return existing;
      }
      const angle = (idx / total) * Math.PI * 2;
      const radius = 120 + Math.random() * 120;
      return {
        id: n.id,
        label: n.label || n.id,
        type: n.type || 'concept',
        occurrences: n.occurrences || 1,
        description: n.description || '',
        x: this.center.x + Math.cos(angle) * radius,
        y: this.center.y + Math.sin(angle) * radius,
        vx: 0,
        vy: 0,
        radius: 12 + Math.min(10, (n.occurrences || 1) * 2)
      };
    });

    this.edges = graphData.edges || [];
  }

  bindEvents() {
    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      this.hoveredNode = null;
      for (const node of this.nodes) {
        const dist = Math.hypot(node.x - mx, node.y - my);
        if (dist <= node.radius + 6) {
          this.hoveredNode = node;
          break;
        }
      }
      this.canvas.style.cursor = this.hoveredNode ? 'pointer' : 'default';
    });

    this.canvas.addEventListener('click', () => {
      if (this.hoveredNode) {
        this.selectedNode = this.hoveredNode;
        this.showNodeDetails(this.selectedNode);
      }
    });

    const searchInput = document.getElementById('kgSearchInput');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.searchTerm = e.target.value.toLowerCase().trim();
      });
    }
  }

  showNodeDetails(node) {
    if (!this.detailsElem) return;
    const connected = this.edges.filter(e => e.source.toLowerCase() === node.id.toLowerCase() || e.target.toLowerCase() === node.id.toLowerCase());
    
    let html = `<strong>📍 Concept: <span class="text-cyan">${node.label}</span></strong> &nbsp; | &nbsp; Type: <em>${node.type}</em> &nbsp; | &nbsp; Frequency: <em>${node.occurrences}</em>`;
    if (node.description) {
      html += `<p class="text-muted text-sm mt-1">"${node.description}"</p>`;
    }
    if (connected.length > 0) {
      html += `<div class="mt-2 text-sm"><strong>Relations:</strong> ` + connected.map(c => `<span class="node-chip">${c.source} ➔ [${c.relation}] ➔ ${c.target}</span>`).join(' ') + `</div>`;
    }
    this.detailsElem.innerHTML = html;
  }

  animate() {
    this.ctx.clearRect(0, 0, this.width, this.height);

    const nodeMap = new Map(this.nodes.map(n => [n.id.toLowerCase(), n]));

    // Physics Relaxation
    for (let i = 0; i < this.nodes.length; i++) {
      const n1 = this.nodes[i];
      // Center gravity
      n1.vx += (this.center.x - n1.x) * 0.0004;
      n1.vy += (this.center.y - n1.y) * 0.0004;

      for (let j = i + 1; j < this.nodes.length; j++) {
        const n2 = this.nodes[j];
        const dx = n2.x - n1.x;
        const dy = n2.y - n1.y;
        const dist = Math.hypot(dx, dy) || 1;
        if (dist < 160) {
          const force = (160 - dist) / 160 * 0.1;
          n1.vx -= (dx / dist) * force;
          n1.vy -= (dy / dist) * force;
          n2.vx += (dx / dist) * force;
          n2.vy += (dy / dist) * force;
        }
      }

      n1.x += n1.vx;
      n1.y += n1.vy;
      n1.vx *= 0.92;
      n1.vy *= 0.92;

      n1.x = Math.max(40, Math.min(this.width - 40, n1.x));
      n1.y = Math.max(40, Math.min(this.height - 40, n1.y));
    }

    // Draw Directed Edges
    this.edges.forEach(edge => {
      const src = nodeMap.get(edge.source.toLowerCase());
      const tgt = nodeMap.get(edge.target.toLowerCase());
      if (!src || !tgt) return;

      this.ctx.beginPath();
      this.ctx.moveTo(src.x, src.y);
      this.ctx.lineTo(tgt.x, tgt.y);
      this.ctx.strokeStyle = 'rgba(16, 185, 129, 0.4)';
      this.ctx.lineWidth = 1.5;
      this.ctx.stroke();

      // Relation Label in Middle
      const midX = (src.x + tgt.x) / 2;
      const midY = (src.y + tgt.y) / 2;
      this.ctx.font = '10px JetBrains Mono';
      this.ctx.fillStyle = '#10b981';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(edge.relation, midX, midY - 3);
    });

    // Draw Concept Nodes
    this.nodes.forEach(node => {
      const isMatch = !this.searchTerm || node.label.toLowerCase().includes(this.searchTerm);
      const isHovered = node === this.hoveredNode;
      const isSelected = node === this.selectedNode;

      const alpha = isMatch ? 1.0 : 0.2;
      this.ctx.globalAlpha = alpha;

      this.ctx.beginPath();
      this.ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
      this.ctx.fillStyle = isSelected ? '#00f0ff' : (isHovered ? '#10b981' : '#059669');
      this.ctx.fill();

      this.ctx.beginPath();
      this.ctx.arc(node.x, node.y, node.radius + (isHovered ? 4 : 2), 0, Math.PI * 2);
      this.ctx.strokeStyle = isSelected ? '#ffffff' : 'rgba(16, 185, 129, 0.6)';
      this.ctx.lineWidth = 2;
      this.ctx.stroke();

      // Text
      this.ctx.font = isHovered ? 'bold 12px Outfit' : '11px Outfit';
      this.ctx.fillStyle = '#ffffff';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(node.label, node.x, node.y + node.radius + 14);

      this.ctx.globalAlpha = 1.0;
    });

    requestAnimationFrame(() => this.animate());
  }
}
