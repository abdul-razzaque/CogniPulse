"""
CogniPulse - Serverless Telemetry Endpoint (/api/telemetry)
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
        telemetry = brain.get_full_telemetry()
        self.wfile.write(json.dumps(telemetry).encode("utf-8"))

    def do_POST(self):
        self.do_GET()
