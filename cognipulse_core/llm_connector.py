"""
CogniPulse - Multi-Model LLM Connector (Groq, Gemini, OpenAI, OpenRouter)
Enables deep reasoning, code generation, and worldwide multilingual conversational intelligence.
"""

import os
import json
import urllib.request
import urllib.parse
from typing import Dict, List, Any, Optional

class LLMConnector:
    """
    Connects CogniPulse to state-of-the-art LLMs (Groq Llama-3.3, Google Gemini, OpenAI, OpenRouter).
    """
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")

    def generate_response(self, prompt: str, search_context: str = "", custom_api_key: Optional[str] = None, provider: str = "auto") -> Optional[str]:
        """
        Sends the query + retrieved live search context to the best available LLM.
        """
        system_instruction = (
            "You are CogniPulse, an advanced self-evolving AI assistant. "
            "Provide accurate, comprehensive, helpful, and articulate answers. "
            "If the user asks in Roman Urdu (e.g., 'k bary main btao', 'kitne soobe hain'), respond in natural, friendly, fluent Roman Urdu. "
            "If the user asks in Urdu, respond in Urdu script. "
            "If the user asks in English or any other language, respond in that language. "
            "Format your answers with clean Markdown, bullet points, and code blocks when appropriate."
        )

        user_content = prompt
        if search_context:
            user_content = f"[Live Web Search Context]:\n{search_context}\n\n[User Query]: {prompt}"

        # 1. Try Groq (Ultra-fast, Llama-3.3 70B)
        groq_key = custom_api_key if provider == "groq" else (custom_api_key or self.groq_api_key)
        if groq_key and (provider in ["groq", "auto"]):
            res = self._call_groq(user_content, system_instruction, groq_key)
            if res:
                return res

        # 2. Try Google Gemini (Gemini 1.5 Flash / 2.0)
        gemini_key = custom_api_key if provider == "gemini" else (custom_api_key or self.gemini_api_key)
        if gemini_key and (provider in ["gemini", "auto"]):
            res = self._call_gemini(user_content, system_instruction, gemini_key)
            if res:
                return res

        # 3. Try OpenAI / OpenRouter
        openai_key = custom_api_key if provider in ["openai", "openrouter"] else (custom_api_key or self.openai_api_key or self.openrouter_api_key)
        if openai_key and (provider in ["openai", "openrouter", "auto"]):
            res = self._call_openai(user_content, system_instruction, openai_key)
            if res:
                return res

        return None

    def _call_groq(self, prompt: str, system_msg: str, api_key: str) -> Optional[str]:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.6,
            "max_tokens": 1500
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=15.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"]
        except Exception:
            pass
        return None

    def _call_gemini(self, prompt: str, system_msg: str, api_key: str) -> Optional[str]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "system_instruction": {"parts": [{"text": system_msg}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.6, "maxOutputTokens": 1500}
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=15.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
        except Exception:
            pass
        return None

    def _call_openai(self, prompt: str, system_msg: str, api_key: str) -> Optional[str]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.6,
            "max_tokens": 1500
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=15.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"]
        except Exception:
            pass
        return None
