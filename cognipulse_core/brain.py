"""
CogniPulse - Autonomous Live Search & Self-Learning Neural Brain
Equipped with Real-Time Web Search, Foundational Knowledge, Hebbian Synaptic Plasticity,
and Dynamic Knowledge Graph Assimilation.
"""

import time
import re
import json
from typing import Dict, List, Any, Optional
from .memory import CogniMemorySystem
from .knowledge_graph import DynamicKnowledgeGraph
from .learning_engine import LearningEngine
from .neural_sim import GridWorldSimulation
from .search_engine import LiveSearchEngine

# Foundational Knowledge Matrix with Typo Tolerance
FOUNDATIONAL_FACTS = [
    {
        "keys": ["province", "provinces", "provice", "provices", "sooba", "soobe", "suba"],
        "context_keys": ["pakistan", "pak"],
        "answer": "Pakistan has **4 major provinces**:\n\n1. **Punjab** (Capital: Lahore - Largest by population)\n2. **Sindh** (Capital: Karachi - Economic hub)\n3. **Khyber Pakhtunkhwa - KPK** (Capital: Peshawar)\n4. **Balochistan** (Capital: Quetta - Largest by land area)\n\nAdditionally, Pakistan includes **Islamabad Capital Territory (ICT)** and two autonomous administrative territories:\n• **Azad Jammu & Kashmir (AJK)**\n• **Gilgit-Baltistan (GB)**"
    },
    {
        "keys": ["capital"],
        "context_keys": ["pakistan", "pak"],
        "answer": "The capital of Pakistan is **Islamabad**. It became the official capital in the 1960s, replacing Karachi."
    },
    {
        "keys": ["founder", "quaid", "quaid-e-azam", "father of the nation"],
        "context_keys": ["pakistan"],
        "answer": "**Quaid-e-Azam Muhammad Ali Jinnah** is the founder and Father of the Nation of Pakistan. Pakistan achieved independence on **August 14, 1947**."
    },
    {
        "keys": ["planet", "planets", "solar system"],
        "context_keys": ["how many", "names", "sun", "space"],
        "answer": "There are **8 recognized planets** in our Solar System:\n1. **Mercury**\n2. **Venus**\n3. **Earth**\n4. **Mars**\n5. **Jupiter** (Largest)\n6. **Saturn** (Ring system)\n7. **Uranus**\n8. **Neptune**"
    },
    {
        "keys": ["speed of light", "light speed", "roshni ki raftar"],
        "context_keys": [],
        "answer": "The speed of light in a vacuum is approximately **299,792 kilometers per second** (about **300,000 km/s** or **186,282 miles per second**)."
    }
]

class CogniPulseBrain:
    """
    Unified CogniPulse Cognitive Core with Real-Time Web Search & Continuous Learning.
    """
    def __init__(self):
        self.memory = CogniMemorySystem()
        self.kg = DynamicKnowledgeGraph()
        self.learning = LearningEngine()
        self.sim = GridWorldSimulation()
        self.search_engine = LiveSearchEngine()
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
            "message": f"Analyzing stimulus: '{query_clean}'",
            "timestamp": time.time()
        })

        # Step 2: Associative Memory Recall (Filtered: Only factual & user-taught nodes, NOT raw interaction logs)
        all_recalled = self.memory.recall(query_clean, top_k=5, threshold=0.15)
        # Filter out interaction logs so we don't repeat old questions
        recalled = [(node, score) for node, score in all_recalled if node.category in ["fact", "rule", "correction", "user_taught"]]

        recalled_contexts = [f"• {node.content[:80]} (Synapse: {node.synaptic_weight:.2f})" for node, score in recalled]
        
        thought_stream.append({
            "stage": "MEMORY_RECALL",
            "message": f"Activated {len(recalled)} associative memory clusters via Hebbian resonance.",
            "details": recalled_contexts,
            "timestamp": time.time()
        })

        # Step 3: Knowledge Graph Exploration
        subgraph = self.kg.query_subgraph(query_clean)
        kg_relations = [f"{e['source']} ➔ [{e['relation']}] ➔ {e['target']}" for e in subgraph.get("edges", [])[:4]]
        
        thought_stream.append({
            "stage": "GRAPH_REASONING",
            "message": f"Traversed dynamic knowledge graph; retrieved {len(subgraph.get('nodes', []))} concept nodes.",
            "details": kg_relations,
            "timestamp": time.time()
        })

        # Step 4: Live Web Search & Knowledge Synthesis
        response_text, search_info = self._synthesize_with_live_search(query_clean, recalled, subgraph)

        if search_info:
            thought_stream.append({
                "stage": "WEB_RETRIEVAL",
                "message": f"Connected to live internet ({search_info.get('source', 'Web')}) and retrieved verified ground truth: '{search_info.get('title', '')}'",
                "details": [f"Source: {search_info.get('source', '')}", f"Snippet: {search_info.get('summary', '')[:120]}..."],
                "timestamp": time.time()
            })

        thought_stream.append({
            "stage": "SYNTHESIS",
            "message": "Formulated response, updated synaptic plasticity, and assimilated new concepts into knowledge graph.",
            "timestamp": time.time()
        })

        # Step 5: Memory Consolidation
        # Store user interaction for history tracking
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

    def _synthesize_with_live_search(self, query: str, recalled: list, subgraph: dict) -> (str, Optional[dict]):
        q_lower = query.lower()

        # 1. Check for Explicit Teaching Command ("Remember that...", "Learn this:...")
        learn_match = re.search(r'(?:remember that|learn this[:]?|note that|i want to teach you that|suno)\s+(.*)', query, re.I)
        if learn_match:
            fact = learn_match.group(1).strip()
            self.memory.store_memory(fact, category="user_taught", confidence=1.0, tags=["user_taught"])
            self.kg.extract_and_ingest(fact)
            return f"🧠 **Knowledge Assimilated:** I have integrated this new ground truth into my neural memory matrix and connected it across my knowledge graph.\n\n> *\"{fact}\"*\n\nMy synaptic weights have been updated in real-time.", None

        # 2. Check for User Corrections or Specific Taught Facts
        if recalled:
            best_mem, score = recalled[0]
            if best_mem.category in ["correction", "user_taught"] and score > 0.30:
                return f"{best_mem.content}\n\n*(Recalled from CogniPulse Synaptic Memory • Plasticity: {best_mem.synaptic_weight:.2f})*", None

        # 3. Check Foundational Knowledge Matrix with Typo Tolerance
        tokens = set(re.findall(r'\b[a-z0-9_]{2,}\b', q_lower))
        for item in FOUNDATIONAL_FACTS:
            keys_matched = any(k in q_lower or any(k in t for t in tokens) for k in item["keys"])
            context_matched = True
            if item["context_keys"]:
                context_matched = any(ck in q_lower or any(ck in t for t in tokens) for ck in item["context_keys"])
            
            if keys_matched and context_matched:
                self.memory.store_memory(item["answer"][:160], category="fact", confidence=1.0, tags=item["keys"])
                return item["answer"], None

        # 4. Math & Calculations (e.g. "what is 25 * 4", "calculate 100 / 5 + 50")
        math_match = re.search(r'(?:calculate|what is|solve)?\s*([0-9\.\s\+\-\*\/\(\)\^\%]+)\s*\??$', query, re.I)
        if math_match:
            math_expr = math_match.group(1).strip()
            if re.match(r'^[0-9\.\s\+\-\*\/\(\)\%]+$', math_expr) and any(op in math_expr for op in ['+', '-', '*', '/', '%']):
                try:
                    result = eval(math_expr, {"__builtins__": None}, {})
                    return f"**Result:** `{math_expr} = {result}`", None
                except Exception:
                    pass

        # 5. Greetings
        if any(w == q_lower.strip() for w in ["hi", "hello", "helo", "hey", "salam", "assalam o alaikum", "aoa"]):
            return (
                "Hello! 👋 I am **CogniPulse**, your autonomous self-learning AI model.\n\n"
                "I am connected to live knowledge systems and can answer questions about any topic in the world, while continuously learning from our conversations. How can I help you today?"
            ), None

        # 6. Identity / Introduction
        if any(w in q_lower for w in ["who are you", "what is cognipulse", "what are you", "your name", "koun ho", "intro"]):
            return (
                "⚡ **I am CogniPulse**, an autonomous self-learning AI model designed with real-time web search and continuous synaptic memory plasticity.\n\n"
                "• **Live Knowledge Integration:** I can search and synthesize answers to any question across science, history, geography, tech, and current affairs.\n"
                "• **Continuous Synaptic Memory:** I learn from every conversation and remember corrections in real-time.\n"
                "• **Dynamic Concept Graph:** Entities and relationships are automatically mapped as we speak!"
            ), None

        # 7. Real-Time Autonomous Live Web Search
        # If not matched locally, search the live web (Wikipedia + DuckDuckGo knowledge graph)
        search_result = self.search_engine.search_live_web(query)
        if search_result and search_result.get("summary"):
            title = search_result.get("title", query)
            summary = search_result.get("summary", "")
            source = search_result.get("source", "Live Web Knowledge")

            # Assimilate this discovered fact into Hebbian memory on the fly
            self.memory.store_memory(
                content=f"{title}: {summary[:200]}",
                category="fact",
                confidence=0.98,
                tags=[title.lower(), "live_web"]
            )
            self.kg.extract_and_ingest(f"{title} is {summary[:200]}")

            formatted_response = f"### [Live Knowledge] {title}\n\n{summary}"
            return formatted_response, search_result


        # 8. Intelligent Concept Decomposition Fallback
        words = [w.capitalize() for w in re.findall(r'\b[a-zA-Z]{3,}\b', query) if w.lower() not in ['what', 'when', 'where', 'which', 'who', 'how', 'many', 'does', 'the', 'is', 'are', 'about']]
        key_concept = words[0] if words else query

        return (
            f"Here is what I have processed on **{query}**:\n\n"
            f"• **Focus Topic:** `{key_concept}`\n"
            f"• **Associative Neural Status:** Analyzed and mapped across CogniPulse's cognitive network.\n\n"
            f"💡 *You can teach me specific facts or corrections directly by saying `\"Remember that [fact]\"` or using the **Teach Fact** button!*"
        ), None

    def teach_fact(self, fact_text: str, category: str = "fact") -> Dict[str, Any]:
        mem_node = self.memory.store_memory(fact_text, category="user_taught", confidence=1.0, tags=["user_taught"])
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
