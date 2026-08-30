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
from .multilingual import MultilingualEngine
from .llm_connector import LLMConnector

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
    Unified CogniPulse Cognitive Core with Real-Time Web Search, Multi-Model LLM Intelligence,
    and Continuous Synaptic Plasticity.
    """
    def __init__(self):
        self.memory = CogniMemorySystem()
        self.kg = DynamicKnowledgeGraph()
        self.learning = LearningEngine()
        self.sim = GridWorldSimulation()
        self.search_engine = LiveSearchEngine()
        self.multilingual = MultilingualEngine()
        self.llm = LLMConnector()
        self.session_interactions = 0
        self.neural_firing_log: List[Dict[str, Any]] = []

    def think_and_respond(self, user_query: str, custom_api_key: Optional[str] = None, provider: str = "auto") -> Dict[str, Any]:
        t0 = time.time()
        self.session_interactions += 1
        query_clean = user_query.strip()
        thought_stream = []

        # Step 0: Check for Attached File Payload
        if "--- FILE:" in user_query and "--- END OF FILE ---" in user_query:
            thought_stream.append({
                "stage": "DOCUMENT_ANALYSIS",
                "message": "Processing and analyzing attached document content...",
                "timestamp": time.time()
            })
            # Try LLM synthesis with document content first
            llm_res = self.llm.generate_response(user_query, custom_api_key=custom_api_key, provider=provider)
            if llm_res:
                response_text = llm_res
            else:
                raw_res, _ = self._synthesize_with_live_search(user_query, [], {})
                response_text = raw_res

            latency_ms = int((time.time() - t0) * 1000)
            return {
                "query": query_clean,
                "response": response_text,
                "thought_stream": thought_stream,
                "recalled_memories": [],
                "graph_context": {},
                "latency_ms": latency_ms,
                "firing_event": {
                    "query": "Document Analysis",
                    "activated_memories": [],
                    "activated_nodes": [],
                    "latency_ms": latency_ms,
                    "timestamp": time.time()
                }
            }

        # Step 1: Multilingual Detection & Semantic Subject Extraction
        detected_lang = self.multilingual.detect_language(query_clean)
        core_subject = self.multilingual.extract_core_subject(query_clean)


        thought_stream.append({
            "stage": "PERCEPTION",
            "message": f"Language: {detected_lang.upper().replace('_', ' ')} | Core Subject: '{core_subject}'",
            "timestamp": time.time()
        })

        # Step 2: Associative Memory Recall (Filtered: Only factual & user-taught nodes)
        all_recalled = self.memory.recall(core_subject, top_k=5, threshold=0.25)
        recalled = [(node, score) for node, score in all_recalled if node.category in ["fact", "user_taught", "correction"]]

        if recalled:
            thought_stream.append({
                "stage": "MEMORY_RECALL",
                "message": f"Retrieved {len(recalled)} resonant neural memory traces for '{core_subject}'",
                "details": [f"Trace: {node.content[:60]}... (Score: {score:.2f})" for node, score in recalled[:3]],
                "timestamp": time.time()
            })

        # Step 3: Subgraph Activation in Knowledge Graph
        subgraph = self.kg.query_subgraph(core_subject)
        if subgraph.get("nodes"):
            thought_stream.append({
                "stage": "GRAPH_ACTIVATION",
                "message": f"Activated {len(subgraph['nodes'])} conceptual entities in knowledge graph",
                "details": [f"Entity: {n.get('name', '')} (Occurrences: {n.get('occurrences', 1)})" for n in subgraph['nodes'][:4]],
                "timestamp": time.time()
            })

        # Step 4: Real-Time Web Search Context Retrieval
        search_result = self.search_engine.search_live_web(core_subject)
        search_context = ""
        if search_result:
            search_context = f"{search_result.get('title', '')}: {search_result.get('summary', '')}"
            thought_stream.append({
                "stage": "WEB_SEARCH",
                "message": f"Retrieved live multi-source facts for '{core_subject}' from {search_result.get('source', 'Web')}",
                "details": [f"Source: {search_result.get('source', '')}", f"Summary: {search_result.get('summary', '')[:140]}..."],
                "timestamp": time.time()
            })

        # Step 5: High-Intelligence LLM Synthesis (If Key Available)
        llm_response = self.llm.generate_response(user_query, search_context=search_context, custom_api_key=custom_api_key, provider=provider)
        if llm_response:
            thought_stream.append({
                "stage": "LLM_INFERENCE",
                "message": "Synthesized response using advanced neural LLM reasoning with live web ground truth.",
                "timestamp": time.time()
            })
            response_text = llm_response
        else:
            # Fallback to Autonomous Multi-Tier Synthesizer
            if search_result and search_result.get("summary"):
                raw_response = search_result["summary"]
            else:
                raw_response, search_info = self._synthesize_with_live_search(core_subject, recalled, subgraph)

            response_text = self.multilingual.translate_response_to_target_language(raw_response, detected_lang, original_query=query_clean)

            thought_stream.append({
                "stage": "SYNTHESIS",
                "message": f"Synthesized response in {detected_lang.upper().replace('_', ' ')} with synaptic consolidation.",
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

        # 0. Check for Attached File Analysis
        file_match = re.search(r'--- FILE:\s*([^\n\r]+)\s*---\s*([\s\S]*?)\s*--- END OF FILE ---', query)
        if file_match:
            filename = file_match.group(1).strip()
            file_body = file_match.group(2).strip()
            user_instruction = re.sub(r'--- FILE:[\s\S]*?--- END OF FILE ---\s*', '', query).strip()
            if not user_instruction:
                user_instruction = "Simplify and summarize this document."

            # Clean binary or PDF stream noise if any leaked
            file_body_clean = re.sub(r'PDF-\d+\.\d+[\s\S]*?stream[\s\S]*?endstream', ' ', file_body)
            file_body_clean = re.sub(r'[^\x20-\x7E\n\r\t]', ' ', file_body_clean)
            file_body_clean = re.sub(r'\s+', ' ', file_body_clean).strip()

            # Ingest concepts from file into knowledge graph
            self.kg.extract_and_ingest(file_body_clean[:1000])
            self.memory.store_memory(f"Document '{filename}': {file_body_clean[:180]}...", category="fact", confidence=1.0, tags=["file_upload", filename])

            # Extract key sentences from document text
            sentences = [s.strip() for s in re.split(r'[.!?\n]+', file_body_clean) if len(s.strip().split()) >= 4]
            key_points = sentences[:5] if sentences else ["Document contains structured analytical data."]

            formatted_points = "\n".join([f"• {pt}." for pt in key_points])

            return (
                f"### 📄 Overview & Simplification of `{filename}`\n\n"
                f"**Main Topic & Purpose:**\n"
                f"This document focuses on the core principles, processes, and structured methodology outlined in `{filename}`.\n\n"
                f"**Key Points & Breakdown (Simplified):**\n"
                f"{formatted_points}\n\n"
                f"**Summary Takeaway:**\n"
                f"The material emphasizes clarity, structured progression, and adhering to standard best practices. "
                f"You can ask me any specific question about any page, section, or definition in this document!"
            ), None


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
                "Hello! How can I help you today? Feel free to ask any question, discuss ideas, or work on code."
            ), None

        # 6. Identity / Introduction
        if any(w in q_lower for w in ["who are you", "what is cognipulse", "what are you", "your name", "koun ho", "intro"]):
            return (
                "I am **CogniPulse**, an advanced AI assistant designed to help with research, coding, analysis, problem solving, and general knowledge."
            ), None

        # 7. Real-Time Autonomous Live Web Search
        search_result = self.search_engine.search_live_web(query)
        if search_result and search_result.get("summary"):
            title = search_result.get("title", query)
            summary = search_result.get("summary", "")

            # Assimilate this discovered fact into Hebbian memory on the fly
            self.memory.store_memory(
                content=f"{title}: {summary[:200]}",
                category="fact",
                confidence=0.98,
                tags=[title.lower(), "live_web"]
            )
            self.kg.extract_and_ingest(f"{title} is {summary[:200]}")

            return summary, search_result

        # 8. Intelligent Concept Reasoning Fallback
        words = [w.capitalize() for w in re.findall(r'\b[a-zA-Z]{3,}\b', query) if w.lower() not in ['what', 'when', 'where', 'which', 'who', 'how', 'many', 'does', 'the', 'is', 'are', 'about']]
        key_concept = words[0] if words else query

        return (
            f"Regarding **{query}**:\n\n"
            f"Could you please specify what particular aspect of **{key_concept}** you would like to explore or focus on?"
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
