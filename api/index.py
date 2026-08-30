"""
CogniPulse - Vercel Serverless Python Handler
Natively handles all API endpoints for Vercel's Python runtime.
"""

import sys
import os
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler

# Add root directory to python path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognipulse_core.brain import CogniPulseBrain

# In Serverless environments, /tmp is writable
IS_VERCEL = os.environ.get("VERCEL", "0") == "1" or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None
if IS_VERCEL:
    brain = CogniPulseBrain()
    brain.memory.storage_path = "/tmp/cognipulse_memory.json"
    brain.kg.storage_path = "/tmp/knowledge_graph.json"
    brain.learning.storage_path = "/tmp/cognipulse_rules.json"
else:
    brain = CogniPulseBrain()

class handler(BaseHTTPRequestHandler):
    def _set_json_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_json_headers(200)

    def _get_payload(self):
        try:
            cl = self.headers.get('Content-Length') or self.headers.get('content-length')
            content_len = int(cl) if cl else 0
            if content_len > 0:
                raw = self.rfile.read(content_len).decode('utf-8')
                return json.loads(raw) if raw else {}
            return {}
        except Exception:
            return {}

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path.endswith("/telemetry") or "/telemetry" in path:
            self._set_json_headers(200)
            telemetry = brain.get_full_telemetry()
            self.wfile.write(json.dumps(telemetry).encode("utf-8"))
            return

        if path.endswith("/memories") or "/memories" in path:
            self._set_json_headers(200)
            mems = [m.to_dict() for m in brain.memory.memories.values()]
            self.wfile.write(json.dumps({"memories": mems}).encode("utf-8"))
            return

        if path.endswith("/graph") or "/graph" in path:
            self._set_json_headers(200)
            graph_data = brain.kg.get_graph_export(max_nodes=60)
            self.wfile.write(json.dumps(graph_data).encode("utf-8"))
            return

        if path.endswith("/sim/state") or "/sim/state" in path:
            self._set_json_headers(200)
            sim_state = brain.sim.get_state()
            self.wfile.write(json.dumps(sim_state).encode("utf-8"))
            return

        # Fallback for health check
        self._set_json_headers(200)
        self.wfile.write(json.dumps({"status": "online", "message": "CogniPulse API is running"}).encode("utf-8"))

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip('/')
        payload = self._get_payload()

        if path.endswith("/chat") or "/chat" in path:
            query = payload.get("query", "")
            if not query or not str(query).strip():
                self._set_json_headers(200)
                self.wfile.write(json.dumps({
                    "response": "Hello! I am CogniPulse, an autonomous self-learning AI model. How can I assist or learn from you today?",
                    "thought_stream": [{"stage": "PERCEPTION", "message": "Received initial contact.", "timestamp": 0}],
                    "recalled_memories": [],
                    "latency_ms": 1.0
                }).encode("utf-8"))
                return
            
            result = brain.think_and_respond(str(query))
            self._set_json_headers(200)
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        if path.endswith("/teach") or "/teach" in path:
            fact = payload.get("fact", "")
            category = payload.get("category", "fact")
            if not fact or not str(fact).strip():
                self._set_json_headers(400)
                self.wfile.write(json.dumps({"error": "Fact cannot be empty"}).encode("utf-8"))
                return
            
            result = brain.teach_fact(str(fact), str(category))
            self._set_json_headers(200)
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        if path.endswith("/feedback") or "/feedback" in path:
            query = payload.get("query", "")
            response = payload.get("response", "")
            is_pos = payload.get("is_positive", True)
            correction = payload.get("correction", None)
            
            result = brain.provide_feedback(str(query), str(response), bool(is_pos), correction)
            self._set_json_headers(200)
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        if path.endswith("/ingest") or "/ingest" in path:
            text = payload.get("text", "")
            if not text or not str(text).strip():
                self._set_json_headers(400)
                self.wfile.write(json.dumps({"error": "Text cannot be empty"}).encode("utf-8"))
                return
            
            brain.memory.store_memory(f"Ingested Document: {str(text)[:200]}...", category="fact", confidence=1.0, tags=["document"])
            kg_res = brain.kg.extract_and_ingest(str(text))
            
            self._set_json_headers(200)
            self.wfile.write(json.dumps({
                "status": "ingested",
                "extracted_concepts": kg_res["concepts_extracted"],
                "triples_discovered": kg_res["triples_discovered"],
                "total_nodes": kg_res["total_nodes"],
                "total_edges": kg_res["total_edges"]
            }).encode("utf-8"))
            return

        if path.endswith("/sim/step") or "/sim/step" in path:
            res = brain.sim.step()
            self._set_json_headers(200)
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        if path.endswith("/sim/train") or "/sim/train" in path:
            episodes = int(payload.get("episodes", 20))
            res = brain.sim.run_episodes(episodes)
            self._set_json_headers(200)
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        if path.endswith("/sim/reset") or "/sim/reset" in path:
            brain.sim.reset_agent()
            self._set_json_headers(200)
            self.wfile.write(json.dumps({"status": "reset", "agent_pos": brain.sim.agent_pos}).encode("utf-8"))
            return

        if path.endswith("/memory/reinforce") or "/memory/reinforce" in path:
            mem_id = payload.get("id", "")
            delta = float(payload.get("delta", 0.5))
            brain.memory.reinforce_memory_by_id(str(mem_id), delta)
            self._set_json_headers(200)
            self.wfile.write(json.dumps({"status": "reinforced", "mem_id": mem_id}).encode("utf-8"))
            return

        self._set_json_headers(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))
