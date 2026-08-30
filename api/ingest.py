"""
CogniPulse - Serverless Ingestion Endpoint (/api/ingest)
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

    def do_POST(self):
        try:
            cl = self.headers.get('Content-Length') or self.headers.get('content-length')
            content_len = int(cl) if cl else 0
            post_body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else "{}"
            payload = json.loads(post_body) if post_body else {}
        except Exception:
            payload = {}

        text = payload.get("text", "").strip()
        if not text:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Text cannot be empty"}).encode("utf-8"))
            return

        brain.memory.store_memory(f"Ingested Document: {text[:200]}...", category="fact", confidence=1.0, tags=["document"])
        kg_res = brain.kg.extract_and_ingest(text)

        self._set_headers(200)
        self.wfile.write(json.dumps({
            "status": "ingested",
            "extracted_concepts": kg_res["concepts_extracted"],
            "triples_discovered": kg_res["triples_discovered"],
            "total_nodes": kg_res["total_nodes"],
            "total_edges": kg_res["total_edges"]
        }).encode("utf-8"))
