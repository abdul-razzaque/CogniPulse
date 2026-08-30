# ⚡ CogniPulse — Autonomous Self-Learning & Adaptive AI Platform

**CogniPulse** is an advanced, autonomous self-learning AI model and interactive cognitive studio designed for continuous adaptation, dynamic Hebbian synaptic memory, and real-time knowledge graph synthesis.

---

## 🌟 Core Highlights

1. **Continuous Hebbian Synaptic Plasticity:**
   - Learns incrementally from every user interaction and ground-truth teaching.
   - High-speed sparse semantic vector resonance + associative link reinforcement (*"Neurons that fire together, wire together"*).
2. **Autonomous Concept & Knowledge Graph Builder:**
   - Ingests raw text, extracts entities, and discovers semantic triples (`Source ➔ [Relation] ➔ Target`) on the fly.
3. **Active Reinforcement & Self-Correction Loop (RLF):**
   - Incorporates thumbs up / thumbs down feedback.
   - When corrected, automatically synthesizes dynamic heuristic rules that adapt future reasoning behavior.
4. **Interactive 3D/2D Neural Visualizer:**
   - Physics-driven canvas rendering active memory clusters, electrical impulse firings, and synaptic weight heatmaps.
5. **Real-time Reinforcement Learning Lab (GridWorld):**
   - Live Q-learning agent demonstrating autonomous policy evolution, epsilon-greedy exploration, and Bellman TD loss telemetry.
6. **Document Digester & Research Hub:**
   - Drop articles, technical notes, or text to have CogniPulse extract concepts and expand its cognitive memory.

---

## 🚀 Quick Start

### 1. Launch with Python
```bash
python run.py
```

### 2. Or 1-Click Launch on Windows
Double-click [`start.bat`](start.bat) to launch the server and automatically open the Studio in your browser at `http://127.0.0.1:8000`.

---

## 🧪 Running Automated Tests
```bash
python -m unittest tests/test_cognipulse.py
```

---

## 📂 Project Architecture
```
AI project/
├── cognipulse_core/
│   ├── __init__.py
│   ├── brain.py            # Master agent orchestrating reasoning & memory
│   ├── memory.py           # Semantic vector recall & Hebbian plasticity
│   ├── knowledge_graph.py  # Concept extraction & relational network
│   ├── learning_engine.py  # Adaptive rule mutation & error reflection
│   └── neural_sim.py       # Real-time Q-learning simulation lab
├── web/
│   ├── index.html          # Cyberpunk glassmorphic Studio dashboard
│   ├── style.css           # Modern neon aesthetic & responsive design
│   ├── app.js              # Real-time telemetry & interaction controller
│   ├── neural_visualizer.js # Particle-synapse physics & impulse renderer
│   ├── knowledge_graph_view.js # Interactive graph network explorer
│   └── simulation_view.js  # GridWorld RL environment visualizer
├── tests/
│   └── test_cognipulse.py  # Unit test suite
├── server.py               # Multi-threaded REST & Static Web Server
├── run.py                  # Auto-browser launcher
├── start.bat               # Windows 1-click startup script
└── README.md
```
