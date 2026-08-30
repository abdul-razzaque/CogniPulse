"""
CogniPulse - Serverless Simulation & Ingestion Endpoints
"""

import sys
import os
import json
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cognipulse_core.brain import CogniPulseBrain

brain = CogniPulseBrain()
brain.memory.storage_path = "/tmp/cognipulse_memory.json"
brain.kg.storage_path = "/tmp/knowledge_graph.json"
brain.learning.storage_path = "/tmp/cognipulse_rules.json"

class handler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        self._set_headers(200)
        self.wfile.write(json.dumps(brain.sim.get_state()).encode("utf-8"))

    def do_POST(self):
        try:
            cl = self.headers.get('Content-Length') or self.headers.get('content-length')
            content_len = int(cl) if cl else 0
            post_body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else "{}"
            payload = json.loads(post_body) if post_body else {}
        except Exception:
            payload = {}

        action = payload.get("action", "step")
        if action == "train":
            episodes = int(payload.get("episodes", 20))
            res = brain.sim.run_episodes(episodes)
        elif action == "reset":
            brain.sim.reset_agent()
            res = {"status": "reset", "agent_pos": brain.sim.agent_pos}
        else:
            res = brain.sim.step()

        self._set_headers(200)
        self.wfile.write(json.dumps(res).encode("utf-8"))
