"""
CogniPulse - Autonomous Live Web & Knowledge Retrieval Engine
Enables CogniPulse to automatically search Wikipedia, DuckDuckGo, and live internet
sources in real-time for any question, extracting and synthesizing accurate factual answers.
"""

import urllib.request
import urllib.parse
import json
import re
import html
from typing import Dict, List, Any, Optional

class LiveSearchEngine:
    """
    Autonomous multi-source internet retrieval engine with zero external API key requirements.
    Uses Wikipedia REST API + DuckDuckGo Instant Answer API + Open Live Endpoints.
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'CogniPulse/1.0 (Autonomous Self-Learning AI Agent; contact@cognipulse.ai)'
        }

    def clean_query(self, query: str) -> str:
        # Strip conversational filler words for clean search
        q = re.sub(r'^(what is|who is|where is|tell me about|how many|how does|why is|explain|define|kya hai|koun hai)\s+', '', query.strip(), flags=re.I)
        q = re.sub(r'[?!\.]+$', '', q).strip()
        return q or query.strip()

    def fetch_wikipedia_summary(self, topic: str) -> Optional[Dict[str, Any]]:
        """Queries Wikipedia's official free REST API for detailed factual summaries."""
        clean_topic = self.clean_query(topic)
        encoded_title = urllib.parse.quote(clean_topic.replace(' ', '_'))
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"

        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    extract = data.get("extract", "")
                    title = data.get("title", clean_topic)
                    if extract and len(extract) > 20:
                        return {
                            "source": "Wikipedia",
                            "title": title,
                            "summary": extract,
                            "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
                        }
        except Exception:
            pass

        # Fallback: Wikipedia Search OpenSearch API
        search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(clean_topic)}&limit=1&namespace=0&format=json"
        try:
            req = urllib.request.Request(search_url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    if len(data) >= 4 and data[1] and data[2]:
                        matched_title = data[1][0]
                        matched_desc = data[2][0]
                        matched_url = data[3][0] if data[3] else ""
                        if matched_desc and len(matched_desc) > 20:
                            return {
                                "source": "Wikipedia Search",
                                "title": matched_title,
                                "summary": matched_desc,
                                "url": matched_url
                            }
        except Exception:
            pass

        return None

    def fetch_duckduckgo_answer(self, query: str) -> Optional[Dict[str, Any]]:
        """Queries DuckDuckGo Instant Answer API for fast facts and entity details."""
        encoded = urllib.parse.quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"

        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    abstract = data.get("AbstractText", "") or data.get("Answer", "")
                    heading = data.get("Heading", query)
                    if abstract and len(abstract) > 15:
                        return {
                            "source": "DuckDuckGo Instant Knowledge",
                            "title": heading,
                            "summary": abstract,
                            "url": data.get("AbstractURL", "")
                        }
                    
                    # Check RelatedTopics
                    related = data.get("RelatedTopics", [])
                    if related and isinstance(related[0], dict) and "Text" in related[0]:
                        return {
                            "source": "DuckDuckGo Knowledge",
                            "title": heading,
                            "summary": related[0]["Text"],
                            "url": related[0].get("FirstURL", "")
                        }
        except Exception:
            pass

        return None

    def search_live_web(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Executes multi-tier live search: Wikipedia -> DuckDuckGo -> Direct Lexical Inference.
        """
        # 1. Try Wikipedia Primary
        wiki_res = self.fetch_wikipedia_summary(query)
        if wiki_res:
            return wiki_res

        # 2. Try DuckDuckGo
        ddg_res = self.fetch_duckduckgo_answer(query)
        if ddg_res:
            return ddg_res

        # 3. Try searching with keyword variations (e.g. "Provinces of Pakistan" instead of "how many provices in pakistan")
        q_clean = query.lower()
        if "provice" in q_clean or "province" in q_clean:
            if "pakistan" in q_clean:
                return self.fetch_wikipedia_summary("Provinces of Pakistan")
        if "capital" in q_clean:
            words = [w.capitalize() for w in re.findall(r'\b[A-Za-z]{3,}\b', query) if w.lower() not in ['what', 'capital', 'the', 'city']]
            if words:
                return self.fetch_wikipedia_summary(words[0])

        return None
