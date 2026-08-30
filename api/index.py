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
IS_VERCEL = os.environ.get("VERCEL", "0") == "1"
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
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_json_headers(200)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path.endswith("/telemetry") or path == "/api/telemetry":
            self._set_json_headers(200)
            telemetry = brain.get_full_telemetry()
            self.wfile.write(json.dumps(telemetry).encode("utf-8"))
            return

        if path.endswith("/memories") or path == "/api/memories":
            self._set_json_headers(200)
            mems = [m.to_dict() for m in brain.memory.memories.values()]
            self.wfile.write(json.dumps({"memories": mems}).encode("utf-8"))
            return

        if path.endswith("/graph") or path == "/api/graph":
            self._set_json_headers(200)
            graph_data = brain.kg.get_graph_export(max_nodes=60)
            self.wfile.write(json.dumps(graph_data).encode("utf-8"))
            return

        if path.endswith("/sim/state") or path == "/api/sim/state":
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

        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else "{}"
        
        try:
            payload = json.loads(post_body) if post_body else {}
        except Exception:
            payload = {}

        if path.endswith("/chat") or path == "/api/chat":
            query = payload.get("query", "")
            if not query.strip():
                self._set_json_headers(400)
                self.wfile.write(json.dumps({"error": "Query cannot be empty"}).encode("utf-8"))
                return
            
            result = brain.think_and_respond(query)
            self._set_json_headers(200)
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        if path.endswith("/teach") or path == "/api/teach":
            fact = payload.get("fact", "")
            category = payload.get("category", "fact")
            if not fact.strip():
                self._set_json_headers(400)
                self.wfile.write(json.dumps({"error": "Fact cannot be empty"}).encode("utf-8"))
                return
            
            result = brain.teach_fact(fact, category)
            self._set_json_headers(200)
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        if path.endswith("/feedback") or path == "/api/feedback":
            query = payload.get("query", "")
            response = payload.get("response", "")
            is_pos = payload.get("is_positive", True)
            correction = payload.get("correction", None)
            
            result = brain.provide_feedback(query, response, is_pos, correction)
            self._set_json_headers(200)
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        if path.endswith("/ingest") or path == "/api/ingest":
            text = payload.get("text", "")
            if not text.strip():
                self._set_json_headers(400)
                self.wfile.write(json.dumps({"error": "Text cannot be empty"}).encode("utf-8"))
                return
            
            brain.memory.store_memory(f"Ingested Document: {text[:200]}...", category="fact", confidence=1.0, tags=["document"])
            kg_res = brain.kg.extract_and_ingest(text)
            
            self._set_json_headers(200)
            self.wfile.write(json.dumps({
                "status": "ingested",
                "extracted_concepts": kg_res["concepts_extracted"],
                "triples_discovered": kg_res["triples_discovered"],
                "total_nodes": kg_res["total_nodes"],
                "total_edges": kg_res["total_edges"]
            }).encode("utf-8"))
            return

        if path.endswith("/sim/step") or path == "/api/sim/step":
            res = brain.sim.step()
            self._set_json_headers(200)
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        if path.endswith("/sim/train") or path == "/api/sim/train":
            episodes = int(payload.get("episodes", 20))
            res = brain.sim.run_episodes(episodes)
            self._set_json_headers(200)
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        if path.endswith("/sim/reset") or path == "/api/sim/reset":
            brain.sim.reset_agent()
            self._set_json_headers(200)
            self.wfile.write(json.dumps({"status": "reset", "agent_pos": brain.sim.agent_pos}).encode("utf-8"))
            return

        if path.endswith("/memory/reinforce") or path == "/api/memory/reinforce":
            mem_id = payload.get("id", "")
            delta = float(payload.get("delta", 0.5))
            brain.memory.reinforce_memory_by_id(mem_id, delta)
            self._set_json_headers(200)
            self.wfile.write(json.dumps({"status": "reinforced", "mem_id": mem_id}).encode("utf-8"))
            return

        self._set_json_headers(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))
