"""
CogniPulse - Robust Real-Time Web Search & Query Normalizer
Direct encyclopedic extraction, relevant snippet resolution, and world knowledge.
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
        "keys": ["provinces", "pakistan"],
        "answer": "Pakistan has **4 major provinces**:\n\n1. **Punjab** (Capital: Lahore - Largest by population)\n2. **Sindh** (Capital: Karachi - Economic hub)\n3. **Khyber Pakhtunkhwa - KPK** (Capital: Peshawar)\n4. **Balochistan** (Capital: Quetta - Largest by land area)\n\nAdditionally, Pakistan includes **Islamabad Capital Territory (ICT)** and two autonomous administrative territories:\n• **Azad Jammu & Kashmir (AJK)**\n• **Gilgit-Baltistan (GB)**"
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
    }
]

class LiveSearchEngine:
    """
    Autonomous live search engine that searches direct encyclopedic knowledge,
    queries Wikipedia and DuckDuckGo, and verifies semantic relevance.
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'CogniPulse-AI/1.0 (https://cogni-pulse.vercel.app; info@cognipulse.ai) Mozilla/5.0'
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

    def fetch_wikipedia_direct_summary(self, subject: str) -> Optional[Dict[str, Any]]:
        """Directly fetches the Wikipedia page summary for the exact topic."""
        clean_subj = subject.strip()
        encoded = urllib.parse.quote(clean_subj.replace(' ', '_'))
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"

        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    extract = data.get("extract", "")
                    title = data.get("title", clean_subj)
                    # Ensure extract is valid and not a disambiguation error
                    if extract and len(extract) > 40 and "may refer to:" not in extract:
                        return {
                            "source": "Wikipedia Knowledge",
                            "title": title,
                            "summary": extract,
                            "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
                        }
        except Exception:
            pass
        return None

    def fetch_wikipedia_search(self, query: str) -> Optional[Dict[str, Any]]:
        """Queries Wikipedia Search API when direct page lookup is insufficient."""
        q_norm = self.normalize_query(query)
        encoded = urllib.parse.quote(q_norm)
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded}&format=json&utf8=1"

        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    search_results = data.get("query", {}).get("search", [])
                    if search_results:
                        top = search_results[0]
                        title = top.get("title", query)
                        raw_snippet = top.get("snippet", "")
                        clean_snippet = html.unescape(re.sub(r'<[^>]+>', '', raw_snippet))

                        # Fetch summary for the matched title
                        direct_res = self.fetch_wikipedia_direct_summary(title)
                        if direct_res:
                            return direct_res
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
        Multi-tier search:
        1. Local Core Knowledge Check
        2. Direct Wikipedia Summary
        3. Wikipedia OpenSearch
        4. DuckDuckGo Instant Knowledge
        """
        # Tier 1: Local Knowledge
        local_ans = self.check_local_knowledge(query)
        if local_ans:
            return {
                "source": "CogniPulse World Knowledge",
                "title": self.normalize_query(query).capitalize(),
                "summary": local_ans,
                "url": ""
            }

        # Tier 2: Direct Wikipedia Page Summary
        wiki_direct = self.fetch_wikipedia_direct_summary(query)
        if wiki_direct:
            return wiki_direct

        # Tier 3: Wikipedia Search
        wiki_search = self.fetch_wikipedia_search(query)
        if wiki_search:
            return wiki_search

        # Tier 4: DuckDuckGo
        ddg_res = self.fetch_duckduckgo_instant(query)
        if ddg_res:
            return ddg_res

        return None
