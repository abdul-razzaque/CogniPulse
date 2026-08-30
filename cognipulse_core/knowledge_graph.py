"""
CogniPulse - Dynamic Autonomous Knowledge Graph System
Extracts concepts, entities, and relations, evolving a semantic network in real-time.
"""

import re
import json
import time
import os
from typing import Dict, List, Any, Set, Tuple

class KnowledgeNode:
    """Represents an entity or concept in the graph."""
    def __init__(self, name: str, node_type: str = "concept", description: str = ""):
        self.name = name
        self.node_type = node_type  # 'concept', 'entity', 'rule', 'agent'
        self.description = description
        self.occurrences = 1
        self.created_at = time.time()
        self.attributes: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "node_type": self.node_type,
            "description": self.description,
            "occurrences": self.occurrences,
            "created_at": self.created_at,
            "attributes": self.attributes
        }


class KnowledgeEdge:
    """Represents a directional relationship between two concepts."""
    def __init__(self, source: str, target: str, relation: str, weight: float = 1.0):
        self.source = source
        self.target = target
        self.relation = relation  # e.g., 'is_a', 'has_part', 'improves', 'related_to', 'causes'
        self.weight = weight
        self.confidence = 1.0
        self.last_updated = time.time()

    def reinforce(self, delta: float = 0.2):
        self.weight = min(5.0, self.weight + delta)
        self.confidence = min(1.0, self.confidence + 0.05)
        self.last_updated = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "weight": round(self.weight, 3),
            "confidence": round(self.confidence, 3),
            "last_updated": self.last_updated
        }


class DynamicKnowledgeGraph:
    """
    Continuous Self-Building Knowledge Graph.
    """
    def __init__(self, storage_path: str = "knowledge_graph.json"):
        self.storage_path = storage_path
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: Dict[str, KnowledgeEdge] = {}  # Key: "source::relation::target"
        self._init_defaults()
        self.load()

    def _init_defaults(self):
        seed_nodes = [
            ("CogniPulse", "agent", "Self-evolving neural AI model"),
            ("Self-Learning", "concept", "Autonomous improvement from interactions & experience"),
            ("Hebbian Plasticity", "rule", "Synaptic strengthening through co-activation"),
            ("Knowledge Graph", "concept", "Network of interconnected concepts and relations"),
            ("Neural Memory", "concept", "Vectorized associative storage architecture"),
            ("Reinforcement Loop", "concept", "Adaptive error correction and reward optimization")
        ]
        for name, ntype, desc in seed_nodes:
            if name.lower() not in self.nodes:
                self.nodes[name.lower()] = KnowledgeNode(name, ntype, desc)

        seed_edges = [
            ("CogniPulse", "uses", "Neural Memory"),
            ("CogniPulse", "implements", "Self-Learning"),
            ("Self-Learning", "driven_by", "Reinforcement Loop"),
            ("Neural Memory", "powered_by", "Hebbian Plasticity"),
            ("CogniPulse", "builds", "Knowledge Graph")
        ]
        for src, rel, tgt in seed_edges:
            self.add_edge(src, rel, tgt, weight=1.5)

    def add_node(self, name: str, node_type: str = "concept", description: str = "") -> KnowledgeNode:
        key = name.strip().lower()
        if key in self.nodes:
            self.nodes[key].occurrences += 1
            if description and not self.nodes[key].description:
                self.nodes[key].description = description
            return self.nodes[key]
        
        node = KnowledgeNode(name.strip(), node_type, description)
        self.nodes[key] = node
        return node

    def add_edge(self, source: str, relation: str, target: str, weight: float = 1.0) -> KnowledgeEdge:
        src_node = self.add_node(source)
        tgt_node = self.add_node(target)
        
        edge_key = f"{src_node.name.lower()}::{relation.strip().lower()}::{tgt_node.name.lower()}"
        if edge_key in self.edges:
            self.edges[edge_key].reinforce(delta=0.2)
            return self.edges[edge_key]

        edge = KnowledgeEdge(src_node.name, tgt_node.name, relation.strip().lower(), weight)
        self.edges[edge_key] = edge
        return edge

    def extract_and_ingest(self, text: str) -> Dict[str, Any]:
        """
        Extracts entities and relationships autonomously using grammatical and lexical pattern detectors.
        """
        extracted_concepts = []
        extracted_triples = []

        # Common relational patterns in factual text
        patterns = [
            (r'([A-Za-z0-9_\s]{2,25})\s+is\s+(?:a|an|the)?\s*([A-Za-z0-9_\s]{2,30})', 'is_a'),
            (r'([A-Za-z0-9_\s]{2,25})\s+uses\s+([A-Za-z0-9_\s]{2,30})', 'uses'),
            (r'([A-Za-z0-9_\s]{2,25})\s+creates\s+([A-Za-z0-9_\s]{2,30})', 'creates'),
            (r'([A-Za-z0-9_\s]{2,25})\s+causes\s+([A-Za-z0-9_\s]{2,30})', 'causes'),
            (r'([A-Za-z0-9_\s]{2,25})\s+improves\s+([A-Za-z0-9_\s]{2,30})', 'improves'),
            (r'([A-Za-z0-9_\s]{2,25})\s+contains\s+([A-Za-z0-9_\s]{2,30})', 'contains'),
            (r'([A-Za-z0-9_\s]{2,25})\s+requires\s+([A-Za-z0-9_\s]{2,30})', 'requires'),
            (r'([A-Za-z0-9_\s]{2,25})\s+helps\s+([A-Za-z0-9_\s]{2,30})', 'helps')
        ]

        sentences = re.split(r'[.!?;\n]+', text)
        for sent in sentences:
            sent_clean = sent.strip()
            if not sent_clean or len(sent_clean) < 4:
                continue

            matched = False
            for pat, rel in patterns:
                matches = re.findall(pat, sent_clean, re.IGNORECASE)
                for m_src, m_tgt in matches:
                    s_clean = m_src.strip().capitalize()
                    t_clean = m_tgt.strip().capitalize()
                    if 1 < len(s_clean) < 30 and 1 < len(t_clean) < 35:
                        # Clean words
                        s_clean = re.sub(r'^(the|a|an)\s+', '', s_clean, flags=re.I).strip()
                        t_clean = re.sub(r'^(the|a|an)\s+', '', t_clean, flags=re.I).strip()
                        if s_clean and t_clean and s_clean.lower() != t_clean.lower():
                            edge = self.add_edge(s_clean, rel, t_clean, weight=1.0)
                            extracted_triples.append({"source": s_clean, "relation": rel, "target": t_clean})
                            extracted_concepts.extend([s_clean, t_clean])
                            matched = True

            # If no pattern matched, extract key noun phrases as standalone concepts
            if not matched:
                words = [w.capitalize() for w in re.findall(r'\b[A-Za-z]{3,}\b', sent_clean) if len(w) > 3]
                for w in words[:3]:
                    self.add_node(w, "concept")
                    extracted_concepts.append(w)

        self.save()
        return {
            "concepts_extracted": list(set(extracted_concepts)),
            "triples_discovered": extracted_triples,
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges)
        }

    def query_subgraph(self, term: str, depth: int = 1) -> Dict[str, Any]:
        """Traverses the graph around a specific concept."""
        key = term.strip().lower()
        matched_nodes = []
        
        # Exact or partial match
        target_keys = set()
        for k in self.nodes:
            if key in k or k in key:
                target_keys.add(k)

        subgraph_nodes = set()
        subgraph_edges = []

        for t_k in target_keys:
            subgraph_nodes.add(self.nodes[t_k].name)
            for edge in self.edges.values():
                if edge.source.lower() == t_k or edge.target.lower() == t_k:
                    subgraph_nodes.add(edge.source)
                    subgraph_nodes.add(edge.target)
                    subgraph_edges.append(edge.to_dict())

        return {
            "center": term,
            "nodes": [self.nodes[n.lower()].to_dict() for n in subgraph_nodes if n.lower() in self.nodes],
            "edges": subgraph_edges
        }

    def get_graph_export(self, max_nodes: int = 60) -> Dict[str, Any]:
        """Exports graph in formatted node-link structure for WebGL/Canvas visualizer."""
        sorted_nodes = sorted(self.nodes.values(), key=lambda n: n.occurrences, reverse=True)[:max_nodes]
        node_names = {n.name.lower() for n in sorted_nodes}

        nodes_data = []
        for n in sorted_nodes:
            nodes_data.append({
                "id": n.name,
                "label": n.name,
                "type": n.node_type,
                "occurrences": n.occurrences,
                "description": n.description
            })

        edges_data = []
        for e in self.edges.values():
            if e.source.lower() in node_names and e.target.lower() in node_names:
                edges_data.append({
                    "source": e.source,
                    "target": e.target,
                    "relation": e.relation,
                    "weight": e.weight
                })

        return {
            "nodes": nodes_data,
            "edges": edges_data
        }

    def save(self):
        try:
            data = {
                "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
                "edges": {k: v.to_dict() for k, v in self.edges.items()},
                "saved_at": time.time()
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[KnowledgeGraph] Error saving: {e}")

    def load(self):
        if not os.path.exists(self.storage_path):
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, ndata in data.get("nodes", {}).items():
                    node = KnowledgeNode(ndata["name"], ndata.get("node_type", "concept"), ndata.get("description", ""))
                    node.occurrences = ndata.get("occurrences", 1)
                    node.created_at = ndata.get("created_at", time.time())
                    node.attributes = ndata.get("attributes", {})
                    self.nodes[k] = node

                for k, edata in data.get("edges", {}).items():
                    edge = KnowledgeEdge(edata["source"], edata["target"], edata["relation"], edata.get("weight", 1.0))
                    edge.confidence = edata.get("confidence", 1.0)
                    edge.last_updated = edata.get("last_updated", time.time())
                    self.edges[k] = edge
        except Exception as e:
            print(f"[KnowledgeGraph] Error loading: {e}")
