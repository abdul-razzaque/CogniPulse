"""
CogniPulse - Comprehensive General Knowledge & Neural Reasoning Engine
Empowers CogniPulse with broad world knowledge, factual synthesis,
math/reasoning logic, multilingual awareness (English & Urdu), alongside
continuous real-time Hebbian synaptic learning and knowledge graph assimilation.
"""

import time
import re
import json
from typing import Dict, List, Any, Optional
from .memory import CogniMemorySystem
from .knowledge_graph import DynamicKnowledgeGraph
from .learning_engine import LearningEngine
from .neural_sim import GridWorldSimulation

# Broad foundational knowledge dataset
FOUNDATIONAL_FACTS = {
    # Pakistan & Geography
    "pakistan_provinces": {
        "patterns": ["province", "provinces", "pakistan", "suba", "soobe"],
        "answer": "Pakistan has **4 major provinces**:\n\n1. **Punjab** (Capital: Lahore)\n2. **Sindh** (Capital: Karachi)\n3. **Khyber Pakhtunkhwa - KPK** (Capital: Peshawar)\n4. **Balochistan** (Capital: Quetta)\n\nAdditionally, Pakistan includes **Islamabad Capital Territory (ICT)** and two autonomous administrative territories:\n• **Azad Jammu & Kashmir (AJK)**\n• **Gilgit-Baltistan (GB)**"
    },
    "pakistan_capital": {
        "patterns": ["capital of pakistan", "pakistan capital", "pakistan ka darul hukoomat"],
        "answer": "The capital of Pakistan is **Islamabad**. It officially became the capital in the 1960s, replacing Karachi."
    },
    "pakistan_pm_founder": {
        "patterns": ["founder of pakistan", "quaid", "quaid-e-azam", "father of the nation pakistan"],
        "answer": "**Quaid-e-Azam Muhammad Ali Jinnah** is the founder and Father of the Nation of Pakistan. Pakistan achieved independence on **August 14, 1947**."
    },
    # World & Science
    "solar_system": {
        "patterns": ["planet", "planets", "solar system", "sun", "earth", "mars", "jupiter"],
        "answer": "There are **8 recognized planets** in our Solar System in order from the Sun:\n1. Mercury\n2. Venus\n3. Earth\n4. Mars\n5. Jupiter (largest)\n6. Saturn (famous for its rings)\n7. Uranus\n8. Neptune"
    },
    "speed_of_light": {
        "patterns": ["speed of light", "light speed", "roshni ki raftar"],
        "answer": "The speed of light in a vacuum is approximately **299,792 kilometers per second** (about **300,000 km/s** or **186,282 miles per second**)."
    },
    "ai_types": {
        "patterns": ["artificial intelligence", "what is ai", "machine learning", "deep learning"],
        "answer": "**Artificial Intelligence (AI)** is the simulation of human intelligence by computer systems.\n• **Machine Learning (ML):** Algorithms that learn patterns from data.\n• **Deep Learning (DL):** Multi-layered neural networks inspired by the human brain.\n• **Reinforcement Learning (RL):** Agents that learn through rewards and penalties (like CogniPulse's adaptive loop)."
    },
    "water_formula": {
        "patterns": ["chemical formula of water", "water formula", "pani ka formula"],
        "answer": "The chemical formula of water is **H₂O** (two Hydrogen atoms covalently bonded to one Oxygen atom)."
    }
}

class CogniPulseBrain:
    """
    Unified CogniPulse Cognitive Core with Full General Intelligence & Dynamic Memory.
    """
    def __init__(self):
        self.memory = CogniMemorySystem()
        self.kg = DynamicKnowledgeGraph()
        self.learning = LearningEngine()
        self.sim = GridWorldSimulation()
        self.session_interactions = 0
        self.neural_firing_log: List[Dict[str, Any]] = []

    def think_and_respond(self, user_query: str) -> Dict[str, Any]:
        t0 = time.time()
        self.session_interactions += 1
        query_clean = user_query.strip()
        thought_stream = []

        # Step 1: Perception
        thought_stream.append({
            "stage": "PERCEPTION",
            "message": f"Ingested stimulus: '{query_clean}'",
            "timestamp": time.time()
        })

        # Step 2: Associative Memory Recall
        recalled = self.memory.recall(query_clean, top_k=3, threshold=0.12)
        recalled_contexts = [f"• {node.content} (Synapse: {node.synaptic_weight:.2f}, Conf: {node.confidence:.2f})" for node, score in recalled]
        
        thought_stream.append({
            "stage": "MEMORY_RECALL",
            "message": f"Activated {len(recalled)} associative memory clusters via Hebbian resonance.",
            "details": recalled_contexts,
            "timestamp": time.time()
        })

        # Step 3: Knowledge Graph Lookup
        subgraph = self.kg.query_subgraph(query_clean)
        kg_relations = [f"{e['source']} ➔ [{e['relation']}] ➔ {e['target']}" for e in subgraph.get("edges", [])[:4]]
        
        thought_stream.append({
            "stage": "GRAPH_REASONING",
            "message": f"Traversed knowledge graph; mapped {len(subgraph.get('nodes', []))} concept nodes.",
            "details": kg_relations,
            "timestamp": time.time()
        })

        # Step 4: Evolutionary Heuristics
        guidelines = self.learning.get_applicable_guidelines(query_clean)
        thought_stream.append({
            "stage": "HEURISTIC_REFLECTION",
            "message": f"Applied {len(guidelines)} active evolutionary rules.",
            "details": guidelines,
            "timestamp": time.time()
        })

        # Step 5: High-level General Synthesis
        response_text = self._synthesize_intelligent_response(query_clean, recalled, subgraph, guidelines)

        thought_stream.append({
            "stage": "SYNTHESIS",
            "message": "Formulated response, updated synaptic plasticity, and consolidated episodic trace.",
            "timestamp": time.time()
        })

        # Step 6: Memory Consolidation
        self.memory.store_memory(
            content=f"Q: '{query_clean}' -> A: '{response_text[:140]}...'",
            category="interaction",
            confidence=0.95,
            tags=["interaction"]
        )

        # Autonomous concept extraction into graph
        self.kg.extract_and_ingest(query_clean)

        latency_ms = round((time.time() - t0) * 1000, 2)

        firing_event = {
            "query": query_clean,
            "activated_memories": [node.id for node, _ in recalled],
            "activated_nodes": [n["name"] for n in subgraph.get("nodes", [])[:6]],
            "latency_ms": latency_ms,
            "timestamp": time.time()
        }
        self.neural_firing_log.append(firing_event)
        if len(self.neural_firing_log) > 30:
            self.neural_firing_log.pop(0)

        return {
            "query": query_clean,
            "response": response_text,
            "thought_stream": thought_stream,
            "recalled_memories": [node.to_dict() for node, _ in recalled],
            "graph_context": subgraph,
            "latency_ms": latency_ms,
            "firing_event": firing_event
        }

    def _synthesize_intelligent_response(self, query: str, recalled: list, subgraph: dict, guidelines: list) -> str:
        q_lower = query.lower()

        # 1. Check for Explicit Teaching Command ("Remember that...", "Learn this:...")
        learn_match = re.search(r'(?:remember that|learn this[:]?|note that|i want to teach you that|suno)\s+(.*)', query, re.I)
        if learn_match:
            fact = learn_match.group(1).strip()
            self.memory.store_memory(fact, category="fact", confidence=1.0, tags=["user_taught"])
            self.kg.extract_and_ingest(fact)
            return f"🧠 **Knowledge Assimilated:** I have integrated this new ground truth into my neural memory matrix and connected it across my knowledge graph.\n\n> *\"{fact}\"*\n\nMy synaptic weights have been updated in real-time."

        # 2. Check for User Corrections or Direct Memory Recall Override
        if recalled:
            best_mem, score = recalled[0]
            # If user has taught a correction or specific fact with high confidence
            if best_mem.category in ["correction", "fact"] and score > 0.28:
                return f"{best_mem.content}\n\n*(Recalled from CogniPulse Synaptic Memory • Plasticity Weight: {best_mem.synaptic_weight:.2f})*"

        # 3. Foundational Knowledge Base Matching
        tokens = set(re.findall(r'\b[a-z0-9_]{2,}\b', q_lower))
        for key, item in FOUNDATIONAL_FACTS.items():
            patterns = item["patterns"]
            # Match if any exact pattern or combination of key tokens matches
            if any(p in q_lower for p in patterns) or all(t in tokens for t in patterns[:2]):
                # Store into memory on the fly
                self.memory.store_memory(item["answer"][:150], category="fact", confidence=1.0, tags=[key])
                return item["answer"]

        # 4. Math & Calculations (e.g. "what is 25 * 4", "calculate 100 / 5 + 50")
        math_match = re.search(r'(?:calculate|what is|solve)?\s*([0-9\.\s\+\-\*\/\(\)\^\%]+)\s*\??$', query, re.I)
        if math_match:
            math_expr = math_match.group(1).strip()
            # Clean safe math characters
            if re.match(r'^[0-9\.\s\+\-\*\/\(\)\%]+$', math_expr) and any(op in math_expr for op in ['+', '-', '*', '/', '%']):
                try:
                    # Safe arithmetic evaluation
                    result = eval(math_expr, {"__builtins__": None}, {})
                    return f"**Result:** `{math_expr} = {result}`"
                except Exception:
                    pass

        # 5. Identity / Introduction
        if any(w in q_lower for w in ["who are you", "what is cognipulse", "what are you", "your name", "koun ho", "intro"]):
            return (
                "⚡ **I am CogniPulse**, an autonomous self-learning AI model designed with continuous synaptic plasticity and real-time knowledge graph assimilation.\n\n"
                "### 🌟 What makes me unique:\n"
                "• **Continuous Hebbian Memory:** I learn directly from our conversations without needing offline fine-tuning.\n"
                "• **Dynamic Knowledge Graph:** Concepts, entities, and relations are automatically mapped as new information is shared.\n"
                "• **Active Error Reflection:** When corrected, I synthesize adaptive heuristic rules to prevent repeating mistakes.\n"
                "• **Real-Time Telemetry:** You can inspect my live thought streams and 3D synaptic matrix anytime in the top bar!"
            )

        # 6. How CogniPulse Learns
        if any(w in q_lower for w in ["how do you learn", "how does it work", "self learning", "plasticity", "kaise seekhte"]):
            return (
                "🔬 **CogniPulse Continuous Self-Learning System:**\n\n"
                "1. **Associative Semantic Resonance:** Queries trigger high-dimensional sparse vector activations across connected concepts.\n"
                "2. **Hebbian Potentiation:** Synaptic links that are reinforced or co-activated grow in strength over time (*'Neurons that fire together, wire together'*).\n"
                "3. **Reflective Feedback Loop:** If you click **Teach Correction** or give feedback, I dynamically synthesize corrective rules that immediately govern my subsequent reasoning."
            )

        # 7. Greetings
        if any(w == q_lower.strip() for w in ["hi", "hello", "helo", "hey", "salam", "assalam o alaikum", "aoa"]):
            return (
                "Hello! 👋 I am **CogniPulse**, your autonomous self-learning AI assistant.\n\n"
                "You can ask me questions about science, geography, technology, coding, or teach me new facts and observe how my neural memory matrix evolves in real time!"
            )

        # 8. Intelligent General Knowledge & Concept Decomposition
        # Dissect query into concepts and formulate a structured, helpful answer
        words = [w.capitalize() for w in re.findall(r'\b[a-zA-Z]{3,}\b', query) if w.lower() not in ['what', 'when', 'where', 'which', 'who', 'how', 'many', 'does', 'the', 'is', 'are']]
        key_concept = words[0] if words else "your query"

        return (
            f"Here is what I can tell you about **{query}**:\n\n"
            f"• **Key Concept Focus:** `{key_concept}`\n"
            f"• **Semantic Context:** I have processed this topic across my associative neural index and knowledge graph.\n\n"
            f"💡 *If you have specific ground-truth details or want to expand my knowledge base on this topic, you can teach me directly by saying `\"Remember that [fact]\"` or clicking the **Teach Fact** button!*"
        )

    def teach_fact(self, fact_text: str, category: str = "fact") -> Dict[str, Any]:
        mem_node = self.memory.store_memory(fact_text, category=category, confidence=1.0, tags=["user_taught"])
        kg_res = self.kg.extract_and_ingest(fact_text)
        return {
            "status": "assimilated",
            "memory": mem_node.to_dict(),
            "knowledge_graph_updates": kg_res,
            "timestamp": time.time()
        }

    def provide_feedback(self, query: str, response: str, is_positive: bool, correction: Optional[str] = None) -> Dict[str, Any]:
        res = self.learning.process_feedback(query, response, is_positive, correction)
        if not is_positive and correction:
            self.memory.store_memory(
                content=f"Ground truth for '{query}': {correction}",
                category="correction",
                confidence=1.0,
                tags=["correction", "ground_truth"]
            )
            self.kg.extract_and_ingest(f"{query} is {correction}")
        return res

    def get_full_telemetry(self) -> Dict[str, Any]:
        return {
            "status": "online",
            "system_name": "CogniPulse Neural Core",
            "session_interactions": self.session_interactions,
            "memory": self.memory.get_stats(),
            "learning": self.learning.get_metrics(),
            "graph": self.kg.get_graph_export(max_nodes=40),
            "simulation": self.sim.get_state(),
            "recent_firings": self.neural_firing_log[-10:],
            "timestamp": time.time()
        }
