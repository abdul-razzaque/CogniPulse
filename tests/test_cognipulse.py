"""
Automated Unit Tests for CogniPulse Self-Learning Neural Core.
"""

import os
import unittest
from cognipulse_core.brain import CogniPulseBrain
from cognipulse_core.memory import CogniMemorySystem, SemanticVectorizer
from cognipulse_core.knowledge_graph import DynamicKnowledgeGraph
from cognipulse_core.learning_engine import LearningEngine
from cognipulse_core.neural_sim import GridWorldSimulation

class TestCogniPulseCore(unittest.TestCase):
    def setUp(self):
        self.brain = CogniPulseBrain()

    def test_semantic_vectorizer(self):
        vec = SemanticVectorizer()
        docs = ["Quantum computing uses qubits", "Neural networks learn representations"]
        vec.fit_corpus(docs)
        v1 = vec.encode("Quantum qubits computation")
        v2 = vec.encode("Neural deep representations")
        sim_diff = SemanticVectorizer.cosine_similarity(v1, v2)
        sim_same = SemanticVectorizer.cosine_similarity(v1, v1)
        self.assertAlmostEqual(sim_same, 1.0, places=3)
        self.assertLess(sim_diff, 0.5)

    def test_memory_storage_and_recall(self):
        mem = CogniMemorySystem(storage_path="test_memory.json")
        mem.store_memory("Antigravity is an IDE for advanced agentic coding", category="fact", tags=["ide"])
        results = mem.recall("Tell me about Antigravity IDE", top_k=2)
        self.assertGreater(len(results), 0)
        top_node, score = results[0]
        self.assertIn("Antigravity", top_node.content)
        if os.path.exists("test_memory.json"):
            os.remove("test_memory.json")

    def test_knowledge_graph_extraction(self):
        kg = DynamicKnowledgeGraph(storage_path="test_kg.json")
        res = kg.extract_and_ingest("CogniPulse creates adaptive neural pathways.")
        self.assertGreaterEqual(res["total_nodes"], 1)
        if os.path.exists("test_kg.json"):
            os.remove("test_kg.json")

    def test_learning_feedback_and_rule_mutation(self):
        le = LearningEngine(storage_path="test_rules.json")
        feedback_res = le.process_feedback(
            query="capital of france",
            response="Berlin",
            is_positive=False,
            correction_text="The capital of France is Paris."
        )
        self.assertEqual(feedback_res["status"], "corrected")
        self.assertIsNotNone(feedback_res["new_rule"])
        if os.path.exists("test_rules.json"):
            os.remove("test_rules.json")

    def test_reinforcement_sim_step(self):
        sim = GridWorldSimulation()
        step_res = sim.step()
        self.assertIn("reward", step_res)
        self.assertIn("agent_pos", step_res)
        batch_res = sim.run_episodes(count=3)
        self.assertEqual(batch_res["episodes_completed"], 3)

    def test_brain_thought_cycle(self):
        res = self.brain.think_and_respond("Who are you and what makes CogniPulse unique?")
        self.assertIn("response", res)
        self.assertIn("thought_stream", res)
        self.assertGreater(len(res["thought_stream"]), 3)

if __name__ == "__main__":
    unittest.main()
