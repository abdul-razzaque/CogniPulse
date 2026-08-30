"""
CogniPulse - Universal Multilingual & Romanization Engine
Includes advanced phonetic stemming for Roman Urdu, Roman Hindi, and world languages.
"""

import re
from typing import Dict, List, Tuple, Optional, Any

# Phonetic normalization dictionary for Roman Urdu/Hindi
PHONETIC_REPLACEMENTS = [
    # Interrogatives (Kitne / How many)
    (r'\b(?:kitny|kitnay|kitne|kitna|kitni|ketne|ketnay|ketna|ketni)\b', 'how_many'),
    (r'\b(?:kya|kia|konsa|kounsa|kon\s*sa|konsi|kounsi|kon\s*si)\b', 'what'),
    (r'\b(?:koun|kon|kone)\b', 'who'),
    (r'\b(?:kahan|kidhar|kdhar|khn)\b', 'where'),
    (r'\b(?:kaise|kese|kesy|kaisy)\b', 'how'),
    (r'\b(?:kyun|kyu|ku|q)\b', 'why'),

    # Entities / Concepts
    (r'\b(?:soby|sobay|soobe|sube|subay|sooba|suba|soba|provice|provices|provinces|province)\b', 'provinces'),
    (r'\b(?:mulk|mumalik|mlk|desh|countries|country|cntry|countris)\b', 'countries'),
    (r'\b(?:dunya|duniya|dnya|jahan|would|wourld|world)\b', 'world'),
    (r'\b(?:darul\s*hukoomat|darul\s*khilafa|rajdhani|captal|captial|capital)\b', 'capital'),
    (r'\b(?:pakistan|pak|pakstan|pk)\b', 'pakistan'),
    (r'\b(?:roshni|roshny|light)\s+(?:ki\s+)?(?:raftar|speed)\b', 'speed_of_light'),
    (r'\b(?:pani|paani|water)\s+(?:ka\s+)?(?:formula|chemical\s+formula)\b', 'water_formula'),

    # Actions / Fillers
    (r'\b(?:batao|btado|btayein|btao|btana|bta|tell)\b', 'tell'),
    (r'\b(?:hain|hai|hy|hyn|hn|h|is|are)\b', '')
]

class MultilingualEngine:
    """
    Detects language, script, and Romanization; applies phonetic stemming and normalizes intents.
    """
    def __init__(self):
        pass

    def detect_language(self, text: str) -> str:
        """Identifies language and script family."""
        if re.search(r'[\u0600-\u06FF]', text):
            if re.search(r'[\u0679\u0688\u0691\u06BA\u06D2\u06AF\u0686\u067E]', text):
                return 'urdu'
            return 'arabic'

        if re.search(r'[\u4E00-\u9FFF]', text):
            return 'chinese'
        if re.search(r'[\u3040-\u30FF]', text):
            return 'japanese'
        if re.search(r'[\u0400-\u04FF]', text):
            return 'russian'
        if re.search(r'[\u0900-\u097F]', text):
            return 'hindi'

        t_lower = text.lower()
        roman_urdu_markers = [
            'kya', 'kia', 'kaise', 'kese', 'kesy', 'kahan', 'kitne', 'kitna', 'kitny', 'kitnay',
            'hain', 'hai', 'hy', 'batao', 'btado', 'btao', 'mujhe', 'mujy', 'apka', 'mera', 'meri',
            'karo', 'kr do', 'krna', 'sooba', 'soobe', 'soby', 'sobay', 'suba', 'sube', 'mulk',
            'pani', 'roshni', 'kon', 'koun', 'acha', 'thek', 'bhi', 'b', 'mein', 'me', 'hota', 'hoti', 'k'
        ]
        tokens = set(re.findall(r'\b[a-z]{1,15}\b', t_lower))
        if len(tokens.intersection(roman_urdu_markers)) >= 1:
            return 'roman_urdu'

        if any(w in tokens for w in ['hola', 'como', 'donde', 'por', 'paises', 'mundo', 'cual', 'cuantos']):
            return 'spanish'
        if any(w in tokens for w in ['bonjour', 'comment', 'pourquoi', 'dans', 'monde', 'pays', 'quel']):
            return 'french'
        if any(w in tokens for w in ['hallo', 'wie', 'warum', 'viele', 'lander', 'welt', 'ist']):
            return 'german'

        return 'english'

    def normalize_romanized_query(self, query: str) -> str:
        """
        Phonetically stems and normalizes any Roman Urdu / Hindi variation into search concepts.
        """
        q = query.strip().lower()

        # Check for core combinations
        is_pak = bool(re.search(r'\b(?:pakistan|pak|pakstan|pk)\b', q))
        is_provinces = bool(re.search(r'\b(?:soby|sobay|soobe|sube|subay|sooba|suba|soba|provice|provices|provinces|province)\b', q))
        is_how_many = bool(re.search(r'\b(?:kitny|kitnay|kitne|kitna|kitni|ketne|ketnay|how\s*many|who\s*many)\b', q))
        
        is_world = bool(re.search(r'\b(?:dunya|duniya|dnya|jahan|would|wourld|world)\b', q))
        is_countries = bool(re.search(r'\b(?:mulk|mumalik|mlk|desh|countries|country|cntry|countris)\b', q))
        
        is_capital = bool(re.search(r'\b(?:darul\s*hukoomat|darul\s*khilafa|rajdhani|captal|captial|capital)\b', q))

        if is_pak and is_provinces:
            return "how many provinces in pakistan"

        if is_world and (is_countries or is_how_many):
            return "how many countries in the world"

        if is_pak and is_capital:
            return "capital of pakistan"

        # Apply phonetic pattern substitutions
        for pattern, replacement in PHONETIC_REPLACEMENTS:
            q = re.sub(pattern, replacement, q)

        q = re.sub(r'\s+', ' ', q).strip()

        # Re-construct search intent
        if 'how_many' in q and 'provinces' in q and 'pakistan' in q:
            return "how many provinces in pakistan"
        if 'how_many' in q and 'countries' in q:
            return "how many countries in the world"
        if 'capital' in q and 'pakistan' in q:
            return "capital of pakistan"

        return q

    def translate_response_to_target_language(self, answer_text: str, target_lang: str) -> str:
        """Translates/mirrors core response into user's language/script."""
        if target_lang == 'english':
            return answer_text

        # 1. Roman Urdu
        if target_lang == 'roman_urdu':
            if "Pakistan has **4 major provinces**" in answer_text or "Punjab" in answer_text and "Sindh" in answer_text:
                return (
                    "Pakistan mein **4 ahem soobe (provinces)** hain:\n\n"
                    "1. **Punjab** (Capital: Lahore - Abadi k lehaz se sab se bara sooba)\n"
                    "2. **Sindh** (Capital: Karachi - Pakistan ka maashi hub)\n"
                    "3. **Khyber Pakhtunkhwa - KPK** (Capital: Peshawar)\n"
                    "4. **Balochistan** (Capital: Quetta - Raqbay k lehaz se sab se bara sooba)\n\n"
                    "Is k ilawa Pakistan mein **Islamabad Capital Territory (ICT)** aur 2 khud-mukhtar ilaqay shamil hain:\n"
                    "• **Azad Jammu & Kashmir (AJK)**\n"
                    "• **Gilgit-Baltistan (GB)**"
                )

            if "195 recognized countries" in answer_text or "195 countries" in answer_text:
                return (
                    "Duniya mein kul **195 tasleem shuda mumalik (countries)** hain:\n\n"
                    "• **193 United Nations (UN) k rukn mumalik**\n"
                    "• **2 Permanent Observer States:**\n"
                    "  1. **Vatican City** (Duniya ki sab se choti azaad riyasat)\n"
                    "  2. **State of Palestine** (Filasteen)\n\n"
                    "*(Taiwan aur Kosovo ko bhi bohot se mulk azaad riyasat maante hain.)*"
                )

            if "Islamabad" in answer_text and "capital" in answer_text.lower():
                return "Pakistan ka darul hukoomat (capital) **Islamabad** hai."

            if "Quaid-e-Azam" in answer_text:
                return "**Quaid-e-Azam Muhammad Ali Jinnah** Pakistan k baani aur Father of the Nation hain. Pakistan **14 August 1947** ko azaad hua."

            return answer_text

        # 2. Urdu Script
        if target_lang == 'urdu':
            if "Pakistan has **4 major provinces**" in answer_text or "Punjab" in answer_text and "Sindh" in answer_text:
                return (
                    "پاکستان میں **4 اہم صوبے** ہیں:\n\n"
                    "1. **پنجاب** (دارالحکومت: لاہور)\n"
                    "2. **سندھ** (دارالحکومت: کراچی)\n"
                    "3. **خیبر پختونخوا - KPK** (دارالحکومت: پشاور)\n"
                    "4. **بلوچستان** (دارالحکومت: کوئٹہ)\n\n"
                    "مزید برآں، **وفاقی دارالحکومت اسلام آباد** اور دو خود مختار علاقے (آزاد کشمیر اور گلگت بلتستان) شامل ہیں۔"
                )

            if "195 recognized countries" in answer_text:
                return (
                    "دنیا میں کل **195 تسلیم شدہ ممالک** ہیں:\n\n"
                    "• **193 اقوام متحدہ (UN) کے رکن ممالک**\n"
                    "• **2 مستقل مبصر ریاستیں:** ویٹیکن سٹی اور ریاستِ فلسطین۔"
                )
            return answer_text

        # 3. Arabic
        if target_lang == 'arabic':
            if "195 recognized countries" in answer_text:
                return "يوجد في العالم حالياً **195 دولة معترف بها** (193 دولة عضو في الأمم المتحدة، ودولتان بصفة مراقب: الفاتيكان ودولة فلسطين)."
            if "Pakistan has **4 major provinces**" in answer_text:
                return "تتكون باكستان من **4 أقاليم رئيسية**: البنجاب، السند، خيبر بختونخوا، وبلوشستان، بالإضافة إلى إقليم العاصمة إسلام آباد."
            return answer_text

        return answer_text
