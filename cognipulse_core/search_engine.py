"""
CogniPulse - Robust Real-Time Web Search & Query Normalizer
Includes intelligent spelling correction, multi-source live web extraction (DuckDuckGo + Wikipedia),
and factual synthesis.
"""

import urllib.request
import urllib.parse
import json
import re
import html
from typing import Dict, List, Any, Optional

COMMON_TYPO_MAP = {
    r'\bwho\s+many\b': 'how many',
    r'\bhow\s+meny\b': 'how many',
    r'\bin\s+the\s+would\b': 'in the world',
    r'\bin\s+the\s+wourld\b': 'in the world',
    r'\bprovice\b': 'province',
    r'\bprovices\b': 'provinces',
    r'\bpakstan\b': 'pakistan',
    r'\bcaptial\b': 'capital',
    r'\bcaptal\b': 'capital',
    r'\bcntry\b': 'country',
    r'\bcountris\b': 'countries',
    r'\blangauge\b': 'language',
    r'\blanguge\b': 'language',
    r'\bpresidant\b': 'president',
    r'\bprimeminister\b': 'prime minister',
    r'\bpopulaion\b': 'population'
}

WORLD_KNOWLEDGE = [
    {
        "keys": ["how many", "countries", "world"],
        "answer": "There are **195 recognized countries** in the world today:\n\n• **193 Member States** of the United Nations (UN)\n• **2 Non-Member Observer States:**\n  1. **The Holy See** (Vatican City - smallest independent state)\n  2. **State of Palestine**\n\n*(Note: Taiwan and Kosovo are also self-governing territories recognized by several nations, bringing some counts to 197.)*"
    },
    {
        "keys": ["largest country", "biggest country"],
        "answer": "The largest country in the world by land area is **Russia**, covering over **17.1 million square kilometers** (spanning Eastern Europe and Northern Asia across 11 time zones)."
    },
    {
        "keys": ["smallest country"],
        "answer": "The smallest independent country in the world is **Vatican City**, an enclave entirely surrounded by Rome, Italy, with an area of just **0.49 square kilometers** (about 121 acres)."
    },
    {
        "keys": ["highest mountain", "tallest mountain", "mount everest"],
        "answer": "The highest mountain in the world above sea level is **Mount Everest** (located in the Himalayas on the border of Nepal and China), standing at **8,848.86 meters (29,031.7 feet)**.\n\n• The 2nd highest peak is **K2 (Godwin-Austen)** in Pakistan at **8,611 meters**."
    },
    {
        "keys": ["longest river"],
        "answer": "The **Nile River** in Africa is traditionally recognized as the longest river in the world, stretching approximately **6,650 kilometers (4,132 miles)**.\n• The **Amazon River** in South America is the largest river by water volume."
    }
]

class LiveSearchEngine:
    """
    Autonomous live search engine that corrects typos, checks foundational world facts,
    and searches the live web (DuckDuckGo + Wikipedia) in real-time.
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def normalize_query(self, query: str) -> str:
        """Applies intelligent typo correction and normalizes query."""
        q = query.strip().lower()
        for typo, fix in COMMON_TYPO_MAP.items():
            q = re.sub(typo, fix, q, flags=re.I)
        return q

    def check_local_knowledge(self, query: str) -> Optional[str]:
        """Fast match against core verified world facts."""
        q_norm = self.normalize_query(query)
        tokens = set(re.findall(r'\b[a-z0-9_]{2,}\b', q_norm))
        
        for item in WORLD_KNOWLEDGE:
            keys = item["keys"]
            if all(any(k in q_norm or k in tokens for k in key.split()) for key in keys):
                return item["answer"]
        return None

    def fetch_wikipedia_search(self, query: str) -> Optional[Dict[str, Any]]:
        """Queries Wikipedia Search API with typo-corrected terms."""
        q_norm = self.normalize_query(query)
        # Strip questioning prefix
        search_term = re.sub(r'^(how many|what is|who is|where is|tell me about|explain)\s+', '', q_norm, flags=re.I).strip()
        encoded = urllib.parse.quote(search_term or q_norm)
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded}&format=json&utf8=1"

        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    search_results = data.get("query", {}).get("search", [])
                    if search_results:
                        top = search_results[0]
                        title = top.get("title", search_term)
                        raw_snippet = top.get("snippet", "")
                        # Clean HTML tags from snippet
                        clean_snippet = html.unescape(re.sub(r'<[^>]+>', '', raw_snippet))
                        
                        # Fetch full page summary for the top matched article
                        page_summary = self._fetch_wiki_summary_by_title(title)
                        if page_summary:
                            return {
                                "source": "Wikipedia",
                                "title": title,
                                "summary": page_summary,
                                "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
                            }
                        elif len(clean_snippet) > 30:
                            return {
                                "source": "Wikipedia Search",
                                "title": title,
                                "summary": clean_snippet,
                                "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
                            }
        except Exception:
            pass

        return None

    def _fetch_wiki_summary_by_title(self, title: str) -> Optional[str]:
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title.replace(' ', '_'))}"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    return data.get("extract", None)
        except Exception:
            pass
        return None

    def fetch_duckduckgo_instant(self, query: str) -> Optional[Dict[str, Any]]:
        """Queries DuckDuckGo Instant Answer API."""
        q_norm = self.normalize_query(query)
        encoded = urllib.parse.quote(q_norm)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"

        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    abstract = data.get("AbstractText", "") or data.get("Answer", "")
                    heading = data.get("Heading", query)
                    if abstract and len(abstract) > 20:
                        return {
                            "source": "DuckDuckGo Knowledge",
                            "title": heading,
                            "summary": abstract,
                            "url": data.get("AbstractURL", "")
                        }
        except Exception:
            pass
        return None

    def search_live_web(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Executes multi-tier live search:
        1. Local Core World Knowledge
        2. Wikipedia Full Summary
        3. DuckDuckGo Instant Knowledge
        """
        # Tier 1: Local Knowledge Check
        local_ans = self.check_local_knowledge(query)
        if local_ans:
            return {
                "source": "CogniPulse World Knowledge",
                "title": self.normalize_query(query).capitalize(),
                "summary": local_ans,
                "url": ""
            }

        # Tier 2: Wikipedia Search
        wiki_res = self.fetch_wikipedia_search(query)
        if wiki_res:
            return wiki_res

        # Tier 3: DuckDuckGo
        ddg_res = self.fetch_duckduckgo_instant(query)
        if ddg_res:
            return ddg_res

        return None
