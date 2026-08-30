/**
 * CogniPulse - Reinforcement Learning Lab Visualizer
 * Renders GridWorld environment, agent trajectory, obstacle avoidance, and learned policy fields.
 */

class SimulationViewer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    
    this.size = 8;
    this.cellSize = this.canvas.width / this.size;
    this.state = null;
    this.autoInterval = null;
  }

  updateState(state) {
    this.state = state;
    this.size = state.size || 8;
    this.cellSize = this.canvas.width / this.size;
    this.render();
  }

  render() {
    if (!this.state) return;
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    const { agent_pos, goal_pos, obstacles, q_grid } = this.state;

    // Draw Grid Cells & Q-Policy Arrows
    for (let r = 0; r < this.size; r++) {
      for (let c = 0; c < this.size; c++) {
        const x = c * this.cellSize;
        const y = r * this.cellSize;

        // Base cell background
        this.ctx.fillStyle = '#0e1422';
        this.ctx.fillRect(x, y, this.cellSize, this.cellSize);

        // Border
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(x, y, this.cellSize, this.cellSize);

        // Q-Value Arrow or Policy Hint
        if (q_grid && q_grid[r] && q_grid[r][c]) {
          const cellData = q_grid[r][c];
          if (cellData.best_action && cellData.best_action !== "NONE") {
            this.drawPolicyArrow(x + this.cellSize / 2, y + this.cellSize / 2, cellData.best_action, cellData.max_q);
          }
        }
      }
    }

    // Draw Obstacles
    if (obstacles) {
      obstacles.forEach(([or, oc]) => {
        const ox = oc * this.cellSize;
        const oy = or * this.cellSize;
        this.ctx.fillStyle = 'rgba(244, 63, 94, 0.25)';
        this.ctx.fillRect(ox + 4, oy + 4, this.cellSize - 8, this.cellSize - 8);
        this.ctx.strokeStyle = '#f43f5e';
        this.ctx.lineWidth = 1.5;
        this.ctx.strokeRect(ox + 4, oy + 4, this.cellSize - 8, this.cellSize - 8);
        
        // Hazard Cross
        this.ctx.beginPath();
        this.ctx.moveTo(ox + 10, oy + 10);
        this.ctx.lineTo(ox + this.cellSize - 10, oy + this.cellSize - 10);
        this.ctx.moveTo(ox + this.cellSize - 10, oy + 10);
        this.ctx.lineTo(ox + 10, oy + this.cellSize - 10);
        this.ctx.stroke();
      });
    }

    // Draw Goal
    if (goal_pos) {
      const gx = goal_pos[1] * this.cellSize;
      const gy = goal_pos[0] * this.cellSize;
      
      this.ctx.fillStyle = 'rgba(245, 158, 11, 0.25)';
      this.ctx.fillRect(gx + 4, gy + 4, this.cellSize - 8, this.cellSize - 8);
      
      this.ctx.beginPath();
      this.ctx.arc(gx + this.cellSize / 2, gy + this.cellSize / 2, this.cellSize / 3, 0, Math.PI * 2);
      this.ctx.fillStyle = '#f59e0b';
      this.ctx.shadowColor = '#f59e0b';
      this.ctx.shadowBlur = 15;
      this.ctx.fill();
      this.ctx.shadowBlur = 0;
      
      this.ctx.fillStyle = '#000';
      this.ctx.font = 'bold 12px Outfit';
      this.ctx.textAlign = 'center';
      this.ctx.fillText('GOAL', gx + this.cellSize / 2, gy + this.cellSize / 2 + 4);
    }

    // Draw Agent
    if (agent_pos) {
      const ax = agent_pos[1] * this.cellSize + this.cellSize / 2;
      const ay = agent_pos[0] * this.cellSize + this.cellSize / 2;

      this.ctx.beginPath();
      this.ctx.arc(ax, ay, this.cellSize / 2.8, 0, Math.PI * 2);
      this.ctx.fillStyle = '#00f0ff';
      this.ctx.shadowColor = '#00f0ff';
      this.ctx.shadowBlur = 20;
      this.ctx.fill();
      this.ctx.shadowBlur = 0;

      this.ctx.beginPath();
      this.ctx.arc(ax, ay, this.cellSize / 5, 0, Math.PI * 2);
      this.ctx.fillStyle = '#ffffff';
      this.ctx.fill();
    }
  }

  drawPolicyArrow(cx, cy, action, maxQ) {
    const intensity = Math.min(1.0, Math.max(0.2, maxQ / 20.0));
    this.ctx.fillStyle = `rgba(0, 240, 255, ${0.15 + intensity * 0.4})`;
    this.ctx.strokeStyle = `rgba(0, 240, 255, ${0.3 + intensity * 0.5})`;
    this.ctx.lineWidth = 2;

    const len = 12;
    let dx = 0, dy = 0;
    if (action === "UP") dy = -len;
    if (action === "DOWN") dy = len;
    if (action === "LEFT") dx = -len;
    if (action === "RIGHT") dx = len;

    this.ctx.beginPath();
    this.ctx.moveTo(cx, cy);
    this.ctx.lineTo(cx + dx, cy + dy);
    this.ctx.stroke();

    // Arrowhead
    this.ctx.beginPath();
    this.ctx.arc(cx + dx, cy + dy, 3, 0, Math.PI * 2);
    this.ctx.fill();
  }
}
