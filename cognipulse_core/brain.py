"""
CogniPulse - Master Autonomous Neural Brain & Agent Orchestrator
Coordinates episodic/semantic memory, knowledge graph reasoning, dynamic rule application,
and continuous self-learning adaptation.
"""

import time
import re
from typing import Dict, List, Any, Optional
from .memory import CogniMemorySystem
from .knowledge_graph import DynamicKnowledgeGraph
from .learning_engine import LearningEngine
from .neural_sim import GridWorldSimulation

class CogniPulseBrain:
    """
    Unified CogniPulse Cognitive Core.
    """
    def __init__(self):
        self.memory = CogniMemorySystem()
        self.kg = DynamicKnowledgeGraph()
        self.learning = LearningEngine()
        self.sim = GridWorldSimulation()
        self.session_interactions = 0
        self.neural_firing_log: List[Dict[str, Any]] = []

    def think_and_respond(self, user_query: str) -> Dict[str, Any]:
        """
        Executes a full cognitive cycle:
        1. Perception & Tokenization
        2. Associative Memory Recall (Hebbian activation)
        3. Knowledge Graph Subgraph Exploration
        4. Rule Heuristic Application & Self-Reflection
        5. Response Synthesis with Thought Stream
        6. Memory & Knowledge Consolidation
        """
        t0 = time.time()
        self.session_interactions += 1
        query_clean = user_query.strip()
        thought_stream = []

        # Step 1: Perception
        thought_stream.append({
            "stage": "PERCEPTION",
            "message": f"Processing query stimulus: '{query_clean}'",
            "timestamp": time.time()
        })

        # Step 2: Associative Memory Recall
        recalled = self.memory.recall(query_clean, top_k=3, threshold=0.10)
        recalled_contexts = [f"• {node.content} (Synaptic Weight: {node.synaptic_weight:.2f}, Confidence: {node.confidence:.2f})" for node, score in recalled]
        
        thought_stream.append({
            "stage": "MEMORY_RECALL",
            "message": f"Activated {len(recalled)} associative memory clusters via cosine semantic resonance.",
            "details": recalled_contexts,
            "timestamp": time.time()
        })

        # Step 3: Knowledge Graph Lookup
        subgraph = self.kg.query_subgraph(query_clean)
        kg_relations = [f"{e['source']} --[{e['relation']}]--> {e['target']}" for e in subgraph.get("edges", [])[:4]]
        
        thought_stream.append({
            "stage": "GRAPH_REASONING",
            "message": f"Traversed knowledge graph around query concepts; retrieved {len(subgraph.get('nodes', []))} nodes and {len(kg_relations)} relational links.",
            "details": kg_relations,
            "timestamp": time.time()
        })

        # Step 4: Rule Heuristics
        guidelines = self.learning.get_applicable_guidelines(query_clean)
        thought_stream.append({
            "stage": "HEURISTIC_REFLECTION",
            "message": f"Applied {len(guidelines)} active evolutionary rules to shape response tone and structure.",
            "details": guidelines,
            "timestamp": time.time()
        })

        # Step 5: Autonomous Synthesis
        response_text = self._synthesize_response(query_clean, recalled, subgraph, guidelines)

        thought_stream.append({
            "stage": "SYNTHESIS",
            "message": "Formulated response, balanced factual confidence, and reinforced activated neural pathways.",
            "timestamp": time.time()
        })

        # Step 6: Memory Consolidation (Store interaction in episodic memory)
        self.memory.store_memory(
            content=f"User asked: '{query_clean}' -> Response: '{response_text[:120]}...'",
            category="interaction",
            confidence=0.90,
            tags=["interaction", "dialogue"]
        )

        # Autonomous concept extraction from user query
        ingest_result = self.kg.extract_and_ingest(query_clean)

        latency_ms = round((time.time() - t0) * 1000, 2)

        # Log neural firing event for live 3D visualizer
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

    def _synthesize_response(self, query: str, recalled: list, subgraph: dict, guidelines: list) -> str:
        """Dynamically formulates an articulate, intelligent response."""
        q_lower = query.lower()

        # Check for teaching / factual input pattern (e.g. "remember that X is Y", "learn this: ...")
        learn_match = re.search(r'(?:remember that|learn this[:]?|note that|i want to teach you that)\s+(.*)', query, re.I)
        if learn_match:
            fact = learn_match.group(1).strip()
            self.memory.store_memory(fact, category="fact", confidence=1.0, tags=["taught_fact"])
            self.kg.extract_and_ingest(fact)
            return f"🧠 **Knowledge Assimilated:** I have integrated this new fact into my neural memory core and expanded my knowledge graph.\n\n> *\"{fact}\"*\n\nMy synaptic weights have been updated and this knowledge will actively influence all future reasoning."

        # Check for identity or definition of CogniPulse
        if any(w in q_lower for w in ["who are you", "what is cognipulse", "what are you", "your name", "koun ho"]):
            return (
                "⚡ **I am CogniPulse**, an autonomous, self-learning AI model with continuous synaptic plasticity.\n\n"
                "Unlike static AI systems that require heavy offline retraining, I feature:\n"
                "1. **Continuous Hebbian Memory**: I learn from every conversation and reinforce associations in real-time.\n"
                "2. **Dynamic Knowledge Graphs**: Concepts and relations evolve automatically as new information is introduced.\n"
                "3. **Active Reinforcement & Self-Correction**: When you guide or correct me, I synthesize adaptive rules that immediately modify my reasoning logic.\n"
                "4. **Real-Time Synaptic Telemetry**: You can inspect my active neural firings and memory clusters live in the CogniPulse Studio!"
            )

        # Check for self-learning / capabilities explanation
        if any(w in q_lower for w in ["how do you learn", "how does it work", "self learning", "plasticity", "kaise seekhte"]):
            return (
                "🔬 **CogniPulse Self-Learning Architecture:**\n\n"
                "My continuous adaptation engine operates on 3 core feedback loops:\n"
                "• **Associative Vector Resonance:** Words and concepts are mapped into sparse semantic vectors. Similar stimuli trigger resonance across connected clusters.\n"
                "• **Hebbian Synaptic Potentiation:** \"*Neurons that fire together, wire together.*\" Memories accessed frequently or reinforced positively grow stronger weights.\n"
                "• **Error Reflection & Rule Mutation:** If a mistake is flagged, an error penalty decays unhelpful pathways, and an adaptive heuristic rule is synthesized to prevent repeat errors."
            )

        # If relevant memories were recalled, integrate them
        if recalled:
            best_mem, score = recalled[0]
            if score > 0.20:
                response = f"Based on my active neural memory and conceptual knowledge:\n\n"
                response += f"• {best_mem.content}\n"
                if len(recalled) > 1:
                    response += f"\n**Associated Context:**\n"
                    for node, sc in recalled[1:3]:
                        response += f"- {node.content}\n"
                
                # Check for relations
                edges = subgraph.get("edges", [])
                if edges:
                    response += "\n**Knowledge Graph Insights:**\n"
                    for e in edges[:3]:
                        response += f"- *{e['source']}* is connected to *{e['target']}* via `{e['relation']}`\n"

                return response

        # General intelligent synthesis fallback
        return (
            f"I have processed your query on **'{query}'** and mapped it across my associative neural index.\n\n"
            f"Currently, my synaptic network contains {len(self.memory.memories)} memory nodes and {len(self.kg.nodes)} conceptual entities.\n\n"
            f"💡 *Tip: You can teach me new facts directly by saying `\"Remember that [fact]\"` or clicking the **Teach CogniPulse** button!*"
        )

    def teach_fact(self, fact_text: str, category: str = "fact") -> Dict[str, Any]:
        """Explicitly ingests a new factual truth into CogniPulse."""
        mem_node = self.memory.store_memory(fact_text, category=category, confidence=1.0, tags=["user_taught"])
        kg_res = self.kg.extract_and_ingest(fact_text)
        
        return {
            "status": "assimilated",
            "memory": mem_node.to_dict(),
            "knowledge_graph_updates": kg_res,
            "timestamp": time.time()
        }

    def provide_feedback(self, query: str, response: str, is_positive: bool, correction: Optional[str] = None) -> Dict[str, Any]:
        """Processes user reinforcement or correction."""
        res = self.learning.process_feedback(query, response, is_positive, correction)
        
        # If negative and correction provided, also store correction as memory
        if not is_positive and correction:
            self.memory.store_memory(
                content=f"Correction for query '{query}': {correction}",
                category="correction",
                confidence=1.0,
                tags=["correction", "ground_truth"]
            )
            self.kg.extract_and_ingest(f"{query} correction: {correction}")

        return res

    def get_full_telemetry(self) -> Dict[str, Any]:
        """Provides full real-time telemetry of the entire cognitive ecosystem."""
        mem_stats = self.memory.get_stats()
        learn_metrics = self.learning.get_metrics()
        graph_export = self.kg.get_graph_export(max_nodes=40)
        sim_state = self.sim.get_state()

        return {
            "status": "online",
            "system_name": "CogniPulse Neural Core",
            "session_interactions": self.session_interactions,
            "memory": mem_stats,
            "learning": learn_metrics,
            "graph": graph_export,
            "simulation": sim_state,
            "recent_firings": self.neural_firing_log[-10:],
            "timestamp": time.time()
        }
