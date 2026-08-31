"""
CogniPulse - Multi-Model High-Intelligence LLM Connector
Powered by Groq 120B / Qwen 27B, Google Gemini, and OpenAI.
"""

import os
import json
import urllib.request
import urllib.parse
from typing import Dict, List, Any, Optional

GROQ_DEFAULT_KEY = "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"

class LLMConnector:
    """
    Connects CogniPulse to state-of-the-art LLMs.
    """
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY", GROQ_DEFAULT_KEY)
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")

    def generate_response(self, prompt: str, search_context: str = "", custom_api_key: Optional[str] = None, provider: str = "auto") -> Optional[str]:
        """
        Sends the query + retrieved live search context to the best available LLM.
        """
        system_instruction = (
            "You are CogniPulse, an ultra-intelligent, world-class AI assistant. "
            "You provide accurate, deeply knowledgeable, highly articulate, and structured responses.\n\n"
            "MANDATORY INSTRUCTIONS:\n"
            "1. LANGUAGE: If the user asks in Roman Urdu (e.g., 'k bary main btao', 'kiya hota hai', 'kaise solve karein', 'samjhao'), "
            "your ENTIRE response MUST be in natural, fluent, friendly, everyday Roman Urdu with clear headings, bullet points, and practical examples.\n"
            "2. If the user asks in Urdu script, respond in standard Urdu script.\n"
            "3. If the user asks in English or another language, respond in that language.\n"
            "4. MATHEMATICS & PROBLEMS: Provide complete step-by-step solutions, intermediate derivations, formulas, and highlighted final answers.\n"
            "5. CODE & PROJECTS: Write clean, modular, fully runnable code blocks with explanatory comments."
        )

        user_content = prompt
        if search_context:
            user_content = f"[Live Web Ground Truth Knowledge]:\n{search_context}\n\n[User Request]:\n{prompt}"

        # 1. Primary: Groq (120B / 27B Deep Neural Reasoning)
        groq_key = custom_api_key if provider == "groq" else (custom_api_key or self.groq_api_key or GROQ_DEFAULT_KEY)
        if groq_key and (provider in ["groq", "auto"]):
            res = self._call_groq(user_content, system_instruction, groq_key)
            if res:
                return res

        # 2. Google Gemini
        gemini_key = custom_api_key if provider == "gemini" else (custom_api_key or self.gemini_api_key)
        if gemini_key and (provider in ["gemini", "auto"]):
            res = self._call_gemini(user_content, system_instruction, gemini_key)
            if res:
                return res

        # 3. OpenAI / OpenRouter
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
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        
        models_to_try = [
            "openai/gpt-oss-120b",
            "qwen/qwen3.8-27b",
            "groq/compound",
            "qwen/qwen3.6-27b"
        ]

        for model in models_to_try:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            try:
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
                with urllib.request.urlopen(req, timeout=20.0) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        choices = data.get("choices", [])
                        if choices:
                            return choices[0].get("message", {}).get("content", "")
            except Exception:
                continue

        return None

    def _call_gemini(self, prompt: str, system_msg: str, api_key: str) -> Optional[str]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "system_instruction": {"parts": [{"text": system_msg}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2000}
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=18.0) as resp:
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
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Mozilla/5.0"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=18.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"]
        except Exception:
            pass
        return None
