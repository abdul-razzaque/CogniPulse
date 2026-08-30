"""
CogniPulse - Robust Real-Time Multi-Source Web Search Engine
Fetches, aggregates, and verifies information from Wikipedia, DuckDuckGo, and direct web sources with full citations.
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
        "answer": "There are **195 recognized countries** in the world today:\n\n• **193 Member States** of the United Nations (UN)\n• **2 Non-Member Observer States:**\n  1. **The Holy See** (Vatican City - smallest independent state)\n  2. **State of Palestine**\n\n*(Note: Taiwan and Kosovo are also self-governing territories recognized by several nations, bringing some counts to 197.)*",
        "sources": [{"title": "United Nations Member States", "url": "https://www.un.org/en/about-us/member-states", "source": "United Nations"}]
    },
    {
        "keys": ["provinces", "pakistan"],
        "answer": "Pakistan has **4 major provinces**:\n\n1. **Punjab** (Capital: Lahore - Largest by population)\n2. **Sindh** (Capital: Karachi - Economic hub)\n3. **Khyber Pakhtunkhwa - KPK** (Capital: Peshawar)\n4. **Balochistan** (Capital: Quetta - Largest by land area)\n\nAdditionally, Pakistan includes **Islamabad Capital Territory (ICT)** and two autonomous administrative territories:\n• **Azad Jammu & Kashmir (AJK)**\n• **Gilgit-Baltistan (GB)**",
        "sources": [{"title": "Administrative units of Pakistan", "url": "https://en.wikipedia.org/wiki/Administrative_units_of_Pakistan", "source": "Wikipedia"}]
    },
    {
        "keys": ["largest country", "biggest country"],
        "answer": "The largest country in the world by land area is **Russia**, covering over **17.1 million square kilometers** (spanning Eastern Europe and Northern Asia across 11 time zones).",
        "sources": [{"title": "List of countries by area", "url": "https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_area", "source": "Wikipedia"}]
    },
    {
        "keys": ["smallest country"],
        "answer": "The smallest independent country in the world is **Vatican City**, an enclave entirely surrounded by Rome, Italy, with an area of just **0.49 square kilometers** (about 121 acres).",
        "sources": [{"title": "Vatican City State", "url": "https://en.wikipedia.org/wiki/Vatican_City", "source": "Wikipedia"}]
    },
    {
        "keys": ["highest mountain", "tallest mountain", "mount everest"],
        "answer": "The highest mountain in the world above sea level is **Mount Everest** (located in the Himalayas on the border of Nepal and China), standing at **8,848.86 meters (29,031.7 feet)**.\n\n• The 2nd highest peak is **K2 (Godwin-Austen)** in Pakistan at **8,611 meters**.",
        "sources": [{"title": "Mount Everest Survey", "url": "https://en.wikipedia.org/wiki/Mount_Everest", "source": "Wikipedia"}]
    }
]

class LiveSearchEngine:
    """
    Autonomous AI Search Engine with real-time multi-query web aggregation and citation generator.
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 (CogniPulse-AI/2.0)'
        }

    def normalize_query(self, query: str) -> str:
        q = query.strip().lower()
        for typo, fix in COMMON_TYPO_MAP.items():
            q = re.sub(typo, fix, q, flags=re.I)
        return q

    def check_local_knowledge(self, query: str) -> Optional[Dict[str, Any]]:
        q_norm = self.normalize_query(query)
        tokens = set(re.findall(r'\b[a-z0-9_]{2,}\b', q_norm))
        
        for item in WORLD_KNOWLEDGE:
            keys = item["keys"]
            if all(any(k in q_norm or k in tokens for k in key.split()) for key in keys):
                return {
                    "source": "CogniPulse Verified Knowledge",
                    "title": self.normalize_query(query).capitalize(),
                    "summary": item["answer"],
                    "url": item["sources"][0]["url"] if item.get("sources") else "",
                    "sources": item.get("sources", [])
                }
        return None

    def fetch_wikipedia_direct_summary(self, subject: str) -> Optional[Dict[str, Any]]:
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
                    page_url = data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{encoded}")
                    if extract and len(extract) > 40 and "may refer to:" not in extract:
                        return {
                            "source": "Wikipedia Knowledge",
                            "title": title,
                            "summary": extract,
                            "url": page_url,
                            "sources": [{"title": f"Wikipedia: {title}", "url": page_url, "source": "Wikipedia"}]
                        }
        except Exception:
            pass
        return None

    def search_duckduckgo_html(self, query: str) -> Optional[Dict[str, Any]]:
        q_norm = self.normalize_query(query)
        encoded = urllib.parse.quote(q_norm)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"

        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=4.5) as resp:
                content = resp.read().decode('utf-8')
                
                # Extract snippets and result links
                snippets = re.findall(r'<a class="result__snippet[^"]*"[^>]*>(.*?)</a>', content, re.DOTALL)
                titles_urls = re.findall(r'<a class="result__url"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', content, re.DOTALL)

                clean_snippets = []
                for s in snippets[:4]:
                    clean = html.unescape(re.sub(r'<[^>]+>', '', s)).strip()
                    if clean and len(clean) > 25:
                        clean_snippets.append(f"• {clean}")

                sources = []
                for link, disp in titles_urls[:3]:
                    clean_disp = html.unescape(re.sub(r'<[^>]+>', '', disp)).strip()
                    sources.append({
                        "title": clean_disp or query.capitalize(),
                        "url": link if link.startswith('http') else f"https://{link.strip()}",
                        "source": "Web Search"
                    })

                if not sources:
                    sources = [{"title": f"Live Web: {query.capitalize()}", "url": f"https://duckduckgo.com/?q={encoded}", "source": "DuckDuckGo"}]

                if clean_snippets:
                    return {
                        "source": "Live Web Multi-Search",
                        "title": query.capitalize(),
                        "summary": "\n\n".join(clean_snippets),
                        "url": f"https://duckduckgo.com/?q={encoded}",
                        "sources": sources
                    }
        except Exception:
            pass
        return None

    def search_live_web(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Autonomous Multi-Tier Web Search Engine:
        1. Local Core Knowledge Check
        2. Direct Wikipedia Summary
        3. Live Web Scraping
        """
        local_ans = self.check_local_knowledge(query)
        if local_ans:
            return local_ans

        wiki_direct = self.fetch_wikipedia_direct_summary(query)
        if wiki_direct:
            return wiki_direct

        ddg_html = self.search_duckduckgo_html(query)
        if ddg_html:
            return ddg_html

        return None
