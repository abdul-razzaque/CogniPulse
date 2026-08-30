/**
 * CogniPulse - Dynamic 3D/2D Neural Synapse Visualizer
 * Physics-based interactive particle & Hebbian neural graph simulation.
 */

class NeuralVisualizer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    
    this.nodes = [];
    this.edges = [];
    this.impulses = []; // Electrical sparks travelling along synapses
    this.hoveredNode = null;
    this.draggedNode = null;
    
    this.width = 0;
    this.height = 0;
    this.center = { x: 0, y: 0 };
    
    this.colorPalette = {
      identity: '#00f0ff',
      fact: '#a855f7',
      concept: '#10b981',
      rule: '#f59e0b',
      interaction: '#64748b'
    };

    this.initCanvas();
    this.bindEvents();
    this.seedDefaultNetwork();
    this.animate();
  }

  initCanvas() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.width = this.canvas.width = rect.width || 800;
    this.height = this.canvas.height = rect.height || 600;
    this.center = { x: this.width / 2, y: this.height / 2 };

    window.addEventListener('resize', () => {
      if (!this.canvas.parentElement) return;
      const r = this.canvas.parentElement.getBoundingClientRect();
      this.width = this.canvas.width = r.width || 800;
      this.height = this.canvas.height = r.height || 600;
      this.center = { x: this.width / 2, y: this.height / 2 };
    });
  }

  seedDefaultNetwork() {
    const seed = [
      { id: 'mem_identity', label: 'CogniPulse Core', cat: 'identity', weight: 3.5 },
      { id: 'mem_purpose', label: 'Autonomous Plasticity', cat: 'concept', weight: 2.8 },
      { id: 'mem_arch', label: 'Hebbian Resonance', cat: 'rule', weight: 2.5 },
      { id: 'mem_kg', label: 'Knowledge Graph', cat: 'concept', weight: 2.2 },
      { id: 'mem_vector', label: 'Semantic Vectors', cat: 'fact', weight: 2.0 },
      { id: 'mem_rlf', label: 'Reinforcement Loop', cat: 'rule', weight: 2.6 }
    ];

    this.nodes = seed.map((s, idx) => {
      const angle = (idx / seed.length) * Math.PI * 2;
      const radius = 140 + Math.random() * 50;
      return {
        id: s.id,
        label: s.label,
        cat: s.cat,
        weight: s.weight,
        x: this.center.x + Math.cos(angle) * radius,
        y: this.center.y + Math.sin(angle) * radius,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        radius: 12 + s.weight * 3,
        pulse: 0
      };
    });

    // Interconnect core nodes
    this.edges = [
      { source: 'mem_identity', target: 'mem_purpose', weight: 2.0 },
      { source: 'mem_identity', target: 'mem_arch', weight: 1.8 },
      { source: 'mem_identity', target: 'mem_kg', weight: 1.5 },
      { source: 'mem_arch', target: 'mem_vector', weight: 1.6 },
      { source: 'mem_purpose', target: 'mem_rlf', weight: 1.9 },
      { source: 'mem_kg', target: 'mem_vector', weight: 1.4 }
    ];
  }

  updateFromBrainData(memories) {
    if (!memories || memories.length === 0) return;

    const existingMap = new Map(this.nodes.map(n => [n.id, n]));
    const newNodes = [];
    const newEdges = [];

    memories.forEach((m, idx) => {
      let node = existingMap.get(m.id);
      if (!node) {
        const angle = Math.random() * Math.PI * 2;
        const radius = 100 + Math.random() * 180;
        node = {
          id: m.id,
          label: m.content.length > 25 ? m.content.substring(0, 22) + '...' : m.content,
          cat: m.category || 'fact',
          weight: m.synaptic_weight || 1.0,
          x: this.center.x + Math.cos(angle) * radius,
          y: this.center.y + Math.sin(angle) * radius,
          vx: (Math.random() - 0.5) * 0.4,
          vy: (Math.random() - 0.5) * 0.4,
          radius: 10 + (m.synaptic_weight || 1) * 3,
          pulse: 1.0
        };
      } else {
        node.weight = m.synaptic_weight || 1.0;
        node.radius = 10 + node.weight * 3;
      }
      newNodes.push(node);

      if (m.connected_nodes) {
        Object.entries(m.connected_nodes).forEach(([targetId, weight]) => {
          newEdges.push({ source: m.id, target: targetId, weight });
        });
      }
    });

    this.nodes = newNodes;
    if (newEdges.length > 0) {
      this.edges = newEdges;
    }
  }

  triggerPulse(activatedNodeIds = []) {
    // Fire electrical sparks across active synapses
    this.nodes.forEach(n => {
      if (activatedNodeIds.includes(n.id) || activatedNodeIds.length === 0) {
        n.pulse = 1.0;
        // Spawn impulses on outgoing edges
        this.edges.forEach(e => {
          if (e.source === n.id || e.target === n.id) {
            this.impulses.push({
              source: e.source,
              target: e.target,
              progress: 0,
              speed: 0.03 + Math.random() * 0.02,
              color: this.colorPalette[n.cat] || '#00f0ff'
            });
          }
        });
      }
    });
  }

  bindEvents() {
    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      if (this.draggedNode) {
        this.draggedNode.x = mx;
        this.draggedNode.y = my;
        return;
      }

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

    this.canvas.addEventListener('mousedown', (e) => {
      if (this.hoveredNode) {
        this.draggedNode = this.hoveredNode;
        this.triggerPulse([this.draggedNode.id]);
      }
    });

    window.addEventListener('mouseup', () => {
      this.draggedNode = null;
    });
  }

  animate() {
    this.ctx.clearRect(0, 0, this.width, this.height);

    // Apply gentle physics forces
    const nodeMap = new Map(this.nodes.map(n => [n.id, n]));

    for (let i = 0; i < this.nodes.length; i++) {
      const n1 = this.nodes[i];
      if (n1 === this.draggedNode) continue;

      // Soft center attraction
      const dxCenter = this.center.x - n1.x;
      const dyCenter = this.center.y - n1.y;
      n1.vx += dxCenter * 0.0003;
      n1.vy += dyCenter * 0.0003;

      // Repulsion between nodes
      for (let j = i + 1; j < this.nodes.length; j++) {
        const n2 = this.nodes[j];
        const dx = n2.x - n1.x;
        const dy = n2.y - n1.y;
        const dist = Math.hypot(dx, dy) || 1;
        if (dist < 180) {
          const force = (180 - dist) / 180 * 0.08;
          n1.vx -= (dx / dist) * force;
          n1.vy -= (dy / dist) * force;
          n2.vx += (dx / dist) * force;
          n2.vy += (dy / dist) * force;
        }
      }

      // Apply velocity and damping
      n1.x += n1.vx;
      n1.y += n1.vy;
      n1.vx *= 0.94;
      n1.vy *= 0.94;

      // Boundary constrain
      n1.x = Math.max(40, Math.min(this.width - 40, n1.x));
      n1.y = Math.max(40, Math.min(this.height - 40, n1.y));

      // Pulse decay
      if (n1.pulse > 0) {
        n1.pulse = Math.max(0, n1.pulse - 0.02);
      }
    }

    // Draw Synaptic Connections (Edges)
    this.edges.forEach(edge => {
      const src = nodeMap.get(edge.source);
      const tgt = nodeMap.get(edge.target);
      if (!src || !tgt) return;

      const alpha = Math.min(0.6, 0.15 + (edge.weight || 1) * 0.1);
      this.ctx.beginPath();
      this.ctx.moveTo(src.x, src.y);
      this.ctx.lineTo(tgt.x, tgt.y);
      this.ctx.strokeStyle = `rgba(0, 240, 255, ${alpha})`;
      this.ctx.lineWidth = Math.min(4, 1 + (edge.weight || 1) * 0.6);
      this.ctx.stroke();
    });

    // Draw Moving Electrical Impulses
    for (let i = this.impulses.length - 1; i >= 0; i--) {
      const imp = this.impulses[i];
      const src = nodeMap.get(imp.source);
      const tgt = nodeMap.get(imp.target);
      if (!src || !tgt) {
        this.impulses.splice(i, 1);
        continue;
      }

      imp.progress += imp.speed;
      if (imp.progress >= 1.0) {
        this.impulses.splice(i, 1);
        continue;
      }

      const px = src.x + (tgt.x - src.x) * imp.progress;
      const py = src.y + (tgt.y - src.y) * imp.progress;

      this.ctx.beginPath();
      this.ctx.arc(px, py, 4, 0, Math.PI * 2);
      this.ctx.fillStyle = imp.color;
      this.ctx.shadowColor = imp.color;
      this.ctx.shadowBlur = 12;
      this.ctx.fill();
      this.ctx.shadowBlur = 0;
    }

    // Draw Neural Nodes
    this.nodes.forEach(node => {
      const color = this.colorPalette[node.cat] || '#00f0ff';
      const isHovered = node === this.hoveredNode;
      const pulseSize = node.pulse * 12;

      // Synaptic outer glow
      this.ctx.beginPath();
      this.ctx.arc(node.x, node.y, node.radius + 4 + pulseSize, 0, Math.PI * 2);
      this.ctx.fillStyle = isHovered ? 'rgba(0, 240, 255, 0.35)' : `rgba(0, 240, 255, ${0.08 + node.pulse * 0.4})`;
      this.ctx.fill();

      // Node Body
      this.ctx.beginPath();
      this.ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
      this.ctx.fillStyle = color;
      this.ctx.shadowColor = color;
      this.ctx.shadowBlur = isHovered ? 20 : (10 + node.pulse * 15);
      this.ctx.fill();
      this.ctx.shadowBlur = 0;

      // Inner Core
      this.ctx.beginPath();
      this.ctx.arc(node.x, node.y, node.radius * 0.4, 0, Math.PI * 2);
      this.ctx.fillStyle = '#ffffff';
      this.ctx.fill();

      // Text Label
      this.ctx.font = isHovered ? 'bold 13px Outfit' : '11px Outfit';
      this.ctx.fillStyle = '#f3f4f6';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(node.label, node.x, node.y + node.radius + 14);
    });

    requestAnimationFrame(() => this.animate());
  }
}
