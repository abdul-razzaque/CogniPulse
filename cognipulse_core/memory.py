"""
CogniPulse - Dynamic Semantic & Episodic Memory System
Implements associative vector recall, episodic memory logs, and Hebbian synaptic consolidation.
"""

import math
import re
import time
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter

class SemanticVectorizer:
    """
    Lightweight, high-speed pure-python embedding & vectorizer
    calculating dimensional feature vectors and cosine similarities.
    """
    def __init__(self):
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.doc_count: int = 0
        self.doc_freq: Counter = Counter()

    def tokenize(self, text: str) -> List[str]:
        # Lowercase and clean alphanumeric tokens
        tokens = re.findall(r'\b[a-zA-Z0-9_]{2,}\b', text.lower())
        return tokens

    def fit_corpus(self, docs: List[str]):
        self.doc_count = len(docs)
        self.doc_freq = Counter()
        all_tokens = set()
        
        for doc in docs:
            tokens = set(self.tokenize(doc))
            for t in tokens:
                self.doc_freq[t] += 1
                all_tokens.add(t)

        self.vocabulary = {token: idx for idx, token in enumerate(sorted(all_tokens))}
        self.idf = {}
        for token, count in self.doc_freq.items():
            self.idf[token] = math.log((1.0 + self.doc_count) / (1.0 + count)) + 1.0

    def encode(self, text: str) -> Dict[int, float]:
        """Encodes text into a normalized sparse TF-IDF vector."""
        tokens = self.tokenize(text)
        if not tokens:
            return {}
        
        tf = Counter(tokens)
        vector = {}
        norm_sq = 0.0

        for token, count in tf.items():
            # Update vocabulary on the fly if new word encountered
            if token not in self.vocabulary:
                self.vocabulary[token] = len(self.vocabulary)
                self.idf[token] = math.log((1.0 + self.doc_count + 1) / 1.0) + 1.0
            
            idx = self.vocabulary[token]
            weight = (count / len(tokens)) * self.idf.get(token, 1.0)
            vector[idx] = weight
            norm_sq += weight * weight

        # Normalize vector
        if norm_sq > 0:
            norm = math.sqrt(norm_sq)
            for idx in vector:
                vector[idx] /= norm

        return vector

    @staticmethod
    def cosine_similarity(v1: Dict[int, float], v2: Dict[int, float]) -> float:
        """Calculates cosine similarity between two sparse unit vectors."""
        if not v1 or not v2:
            return 0.0
        # Dot product of intersecting dimensions
        if len(v1) > len(v2):
            v1, v2 = v2, v1
        dot = sum(val * v2.get(idx, 0.0) for idx, val in v1.items())
        return max(0.0, min(1.0, dot))


class MemoryNode:
    """Represents a single episodic/semantic memory in CogniPulse's brain."""
    def __init__(self, mem_id: str, content: str, category: str = "general", confidence: float = 1.0, tags: List[str] = None):
        self.id = mem_id
        self.content = content
        self.category = category  # 'fact', 'interaction', 'rule', 'correction'
        self.confidence = confidence
        self.access_count = 1
        self.created_at = time.time()
        self.last_accessed = time.time()
        self.synaptic_weight = 1.0
        self.tags = tags or []
        self.vector: Dict[int, float] = {}
        self.connected_nodes: Dict[str, float] = {}  # Associative Hebbian connections: {node_id: weight}

    def boost_synapse(self, factor: float = 0.2):
        """Hebbian plasticity: 'Neurons that fire together, wire together'"""
        self.access_count += 1
        self.last_accessed = time.time()
        self.synaptic_weight = min(5.0, self.synaptic_weight + factor)
        self.confidence = min(1.0, self.confidence + 0.05)

    def decay_synapse(self, decay_rate: float = 0.01):
        """Simulates synaptic pruning for stale, unreinforced memories."""
        elapsed_hours = (time.time() - self.last_accessed) / 3600.0
        decay = decay_rate * elapsed_hours
        self.synaptic_weight = max(0.2, self.synaptic_weight - decay)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "category": self.category,
            "confidence": round(self.confidence, 3),
            "access_count": self.access_count,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "synaptic_weight": round(self.synaptic_weight, 3),
            "tags": self.tags,
            "connected_nodes": {k: round(v, 3) for k, v in self.connected_nodes.items()}
        }


class CogniMemorySystem:
    """
    Episodic, Semantic & Working Memory Core with Synaptic Plasticity.
    """
    def __init__(self, storage_path: str = "cognipulse_memory.json"):
        self.storage_path = storage_path
        self.vectorizer = SemanticVectorizer()
        self.memories: Dict[str, MemoryNode] = {}
        self.working_memory: List[Dict[str, Any]] = []  # Short-term buffer
        self.max_working_memory = 10
        self._init_defaults()
        self.load()

    def _init_defaults(self):
        """Initialize foundational core beliefs and identity."""
        seed_data = [
            ("mem_identity", "I am CogniPulse, an autonomous self-evolving neural AI model capable of real-time continuous learning and associative memory.", "fact", 1.0, ["identity", "cognipulse"]),
            ("mem_purpose", "My purpose is to continuously assimilate new knowledge, self-correct from feedback, and evolve my reasoning capacity dynamically.", "fact", 1.0, ["purpose", "learning"]),
            ("mem_arch", "CogniPulse architecture uses Hebbian synaptic reinforcement, dynamic concept graphs, and episodic vector retrieval.", "fact", 1.0, ["architecture", "neural"])
        ]
        for mid, text, cat, conf, tags in seed_data:
            if mid not in self.memories:
                node = MemoryNode(mid, text, cat, conf, tags)
                self.memories[mid] = node
        self._rebuild_vectors()

    def _rebuild_vectors(self):
        docs = [node.content for node in self.memories.values()]
        self.vectorizer.fit_corpus(docs)
        for node in self.memories.values():
            node.vector = self.vectorizer.encode(node.content)

    def store_memory(self, content: str, category: str = "general", confidence: float = 0.95, tags: List[str] = None) -> MemoryNode:
        """Stores a new memory, encodes its vector, and wires associative links."""
        mem_id = f"mem_{int(time.time() * 1000)}_{len(self.memories)}"
        node = MemoryNode(mem_id, content, category, confidence, tags)
        node.vector = self.vectorizer.encode(content)
        
        # Check for associative wiring with top existing memories
        for other_id, other_node in self.memories.items():
            sim = SemanticVectorizer.cosine_similarity(node.vector, other_node.vector)
            if sim > 0.4:
                node.connected_nodes[other_id] = sim
                other_node.connected_nodes[mem_id] = sim

        self.memories[mem_id] = node
        self.add_to_working_memory("store", content, {"id": mem_id, "category": category})
        self.save()
        return node

    def recall(self, query: str, top_k: int = 4, threshold: float = 0.15) -> List[Tuple[MemoryNode, float]]:
        """
        Associative recall based on semantic similarity + synaptic weight + confidence.
        """
        query_vec = self.vectorizer.encode(query)
        scored_nodes = []

        for node in self.memories.values():
            node.decay_synapse()
            sim = SemanticVectorizer.cosine_similarity(query_vec, node.vector)
            if sim >= threshold:
                # Combined Activation Potential: Similarity * Synaptic Plasticity * Confidence
                activation = sim * (0.6 + 0.4 * min(node.synaptic_weight / 2.0, 1.0)) * node.confidence
                scored_nodes.append((node, activation))

        # Sort by highest activation potential
        scored_nodes.sort(key=lambda x: x[1], reverse=True)
        top_results = scored_nodes[:top_k]

        # Reinforce activated memories and cross-activate connected nodes
        for node, score in top_results:
            node.boost_synapse(factor=0.15 * score)
            # Hebbian co-activation of connected nodes
            for conn_id, conn_weight in list(node.connected_nodes.items())[:3]:
                if conn_id in self.memories:
                    self.memories[conn_id].boost_synapse(factor=0.05 * conn_weight)

        self.add_to_working_memory("recall", query, {"retrieved_count": len(top_results)})
        return top_results

    def add_to_working_memory(self, action: str, details: str, meta: Dict[str, Any] = None):
        """Maintains the active working memory buffer."""
        entry = {
            "timestamp": time.time(),
            "action": action,
            "details": details,
            "meta": meta or {}
        }
        self.working_memory.append(entry)
        if len(self.working_memory) > self.max_working_memory:
            self.working_memory.pop(0)

    def reinforce_memory_by_id(self, mem_id: str, delta_weight: float = 0.5):
        """Direct reinforcement or penalization of a specific memory."""
        if mem_id in self.memories:
            node = self.memories[mem_id]
            node.synaptic_weight = max(0.1, min(5.0, node.synaptic_weight + delta_weight))
            if delta_weight > 0:
                node.confidence = min(1.0, node.confidence + 0.1)
            else:
                node.confidence = max(0.1, node.confidence - 0.2)
            self.save()

    def get_stats(self) -> Dict[str, Any]:
        """Returns comprehensive cognitive memory metrics."""
        total = len(self.memories)
        if total == 0:
            return {"total_memories": 0, "avg_synaptic_weight": 0.0, "categories": {}}
        
        avg_weight = sum(m.synaptic_weight for m in self.memories.values()) / total
        avg_conf = sum(m.confidence for m in self.memories.values()) / total
        categories = Counter(m.category for m in self.memories.values())
        
        return {
            "total_memories": total,
            "avg_synaptic_weight": round(avg_weight, 3),
            "avg_confidence": round(avg_conf, 3),
            "categories": dict(categories),
            "total_synapses": sum(len(m.connected_nodes) for m in self.memories.values()) // 2
        }

    def save(self):
        try:
            data = {
                "memories": {k: v.to_dict() for k, v in self.memories.items()},
                "saved_at": time.time()
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[CogniMemory] Error saving: {e}")

    def load(self):
        if not os.path.exists(self.storage_path):
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                loaded_mems = data.get("memories", {})
                for mid, mdata in loaded_mems.items():
                    node = MemoryNode(
                        mem_id=mdata["id"],
                        content=mdata["content"],
                        category=mdata.get("category", "general"),
                        confidence=mdata.get("confidence", 1.0),
                        tags=mdata.get("tags", [])
                    )
                    node.access_count = mdata.get("access_count", 1)
                    node.created_at = mdata.get("created_at", time.time())
                    node.last_accessed = mdata.get("last_accessed", time.time())
                    node.synaptic_weight = mdata.get("synaptic_weight", 1.0)
                    node.connected_nodes = mdata.get("connected_nodes", {})
                    self.memories[mid] = node
            self._rebuild_vectors()
        except Exception as e:
            print(f"[CogniMemory] Error loading: {e}")
