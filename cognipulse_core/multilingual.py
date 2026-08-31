"""
CogniPulse - Natural Conversational Multilingual Engine
Translates concepts into crystal-clear, simple, and friendly everyday Roman Urdu (and standard English).
"""

import re
from typing import Dict, List, Tuple, Optional, Any

TOKENS_TO_REMOVE = {
    'k', 'ka', 'ki', 'ke', 'kay', 'ko', 'se', 'sy', 'main', 'mein', 'me', 'm', 'pe', 'par',
    'bary', 'bare', 'baray', 'barye', 'barey', 'bta', 'btao', 'btado', 'batao', 'btayein', 'btana',
    'samjhao', 'samjha', 'bataiye', 'karo', 'krna', 'kary', 'kare', 'karein',
    'kya', 'kia', 'kiya', 'hota', 'hoti', 'hote', 'hai', 'hain', 'hy', 'h', 'hyn', 'hn',
    'mujhe', 'mujy', 'humain', 'humein', 'ap', 'aap', 'kuch', 'thora', 'detail', 'details',
    'tell', 'me', 'about', 'what', 'is', 'who', 'where', 'how', 'does', 'are', 'the', 'a', 'an',
    'can', 'you', 'explain', 'give', 'information', 'info', 'on', 'please', 'plz'
}

# Crystal-Clear, Natural, Everyday Roman Urdu Knowledge Base
NATURAL_ROMAN_URDU: Dict[str, str] = {
    "bioinformatics": (
        "### 🧬 Bioinformatics Asan Lafzon Mein\n\n"
        "**Bioinformatics** asal mein **Biology aur Computer Science** ka jor hai.\n\n"
        "Jab doctors aur scientists k pas insani jism, DNA ya bimariyon ka bohot zyada data jama ho jata hai, "
        "to usay haath se check karna na-mumkin hota hai. Is liye **computer software aur algorithms** ki madad se is data ko samjha jata hai.\n\n"
        "**Yeh kahan kahan kaam aata hai?**\n"
        "1. **DNA aur Genes ko Samajhna:** Insan k DNA k andar chuppay raaz maloom karna.\n"
        "2. **Bimariyon ka Ilaj:** Cancer jesi bimariyon ki bunyadi waja daryaft karna.\n"
        "3. **Nayi Dawaiyan Banana:** Computers par test kar k behtar medicines banana taa-kay mareez jaldi theek hon.\n\n"
        "💡 **Mukhtasar:** Yeh computers ki taqat se biological maslay hal karnay ka shoba hai."
    ),
    "computer science": (
        "### 💻 Computer Science Kya Hai?\n\n"
        "**Computer Science (CS)** computers, programming aur software banana seekhnay ka shoba hai.\n\n"
        "Is mein sirf computer chalana nahi sikhaya jata, balkay yeh sikhaya jata hai k **computer kaam kesay karta hai** aur hum software ya apps k zariye maslay kesay hal kar saktay hain.\n\n"
        "**Is k Main Shobay:**\n"
        "1. **Software Development:** Mobile apps, websites aur softwares banana.\n"
        "2. **Artificial Intelligence (AI):** Smart software banana jo khud sochnay aur seekhnay ki salahiyat rakhay.\n"
        "3. **Data Science:** Baray data se kaam ki maloomat nikalna.\n"
        "4. **Cyber Security:** Hackers se data aur systems ko bachana.\n\n"
        "💡 **Future:** Aaj ki dunya mein har cheez (banks, hospitals, shopping, games) computer science par chal rahi hai."
    ),
    "artificial intelligence": (
        "### 🧠 Artificial Intelligence (AI) Kya Hai?\n\n"
        "**Artificial Intelligence (AI)** ka matlab hai **machine ya computer ko insani dimaag jesi aqal dena**.\n\n"
        "Aam computer sirf wahi karta hai jo usay bataya jaye, lekin AI wala software khud tajarbay (experience) se seekhta hai aur naye faislay karta hai.\n\n"
        "**Rozmarrah Zindagi Mein AI ki Misalein:**\n"
        "• **ChatGPT / Claude:** Jo aam insan ki tarha baat cheet kartay hain aur sawalon k jawab detay hain.\n"
        "• **YouTube & TikTok Recommendations:** Jo aapki pasand k mutabiq videos dikhatay hain.\n"
        "• **Face Unlock:** Jo aapka chehra pehchan kar mobile kholta hai.\n"
        "• **Google Maps:** Jo traffic dekh kar sab se behtareen rasta batata hai."
    ),
    "machine learning": (
        "### ⚙️ Machine Learning (ML) Kya Hai?\n\n"
        "**Machine Learning (ML)** AI ka aik hissa hai jis mein computer ko **data dekh kar khud seekhna** sikhaya jata hai.\n\n"
        "**Misal:** Agar aap computer ko 10,000 billiyon (cats) ki tasweerein dikhayein, to agli baar wo nayi tasveer dekh kar khud bata dega k 'Yeh billi hai', baghair kisi k bataye."
    ),
    "data science": (
        "### 📊 Data Science Kya Hai?\n\n"
        "**Data Science** ka matlab hai bohot baray data se kaam ki maloomat nikal kar behtareen faislay karna.\n\n"
        "**Misal:** Daraz ya Amazon yeh dekhta hai k log konsi cheezein zyada khareed rahay hain, aur Data Science ki madad se pehlay se stock jama kar leta hai."
    ),
    "cyber security": (
        "### 🔒 Cyber Security Kya Hai?\n\n"
        "**Cyber Security** ka matlab hai apnay mobile, computer, internet accounts aur bank data ko **hackers aur choron se mehfooz rakhna**.\n\n"
        "Yeh internet ki dunya ki police aur security guard ki tarha kaam karti hai."
    ),
    "physics": (
        "### 🔬 Physics (Ilm-e-Tabiyat) Kya Hai?\n\n"
        "**Physics** science ka wo shoba hai jo yeh samjhata hai k **hamari dunya aur kainaat kesay kaam karti hai**.\n\n"
        "Yeh roshni, bijli, aawaz, kashish-e-saqal (gravity), aur harkat k qawaneen ka mutala karti hai.\n\n"
        "**Misal:** Seb zameen par kyun girta hai? Gari break laganay par kyun rukti hai? Bijli kesay banti hai? Yeh sab Physics batati hai."
    ),
    "chemistry": (
        "### 🧪 Chemistry (Ilm-e-Keemiya) Kya Hai?\n\n"
        "**Chemistry** maddah (matter) aur cheezon k aapas mein milnay (chemical reaction) ka ilm hai.\n\n"
        "Yeh batati hai k paani kesay banta hai (Hydrogen + Oxygen), dawaiyan kesay kaam karti hain, aur sabun ya plastic kesay banta hai."
    ),
    "biology": (
        "### 🌿 Biology (Ilm-e-Hayatyaat) Kya Hai?\n\n"
        "**Biology** zindagi aur zindah jaan-daron (insan, janwar, poday) k baray mein parhnay ka ilm hai.\n\n"
        "Is mein jism k aaza (dil, dimaag, gurday), bimariyan aur podon ki afzaish ka mutala kiya jata hai."
    ),
    "provinces of pakistan": (
        "### 🇵🇰 Pakistan k Soobay (Provinces)\n\n"
        "Pakistan mein kul **4 ahem soobay** hain:\n\n"
        "1. **Punjab** (Darul Hukoomat: Lahore - Abadi k lehaz se sab se bara)\n"
        "2. **Sindh** (Darul Hukoomat: Karachi - Pakistan ka maashi markaz)\n"
        "3. **Khyber Pakhtunkhwa - KPK** (Darul Hukoomat: Peshawar)\n"
        "4. **Balochistan** (Darul Hukoomat: Quetta - Raqbay k lehaz se sab se bara)\n\n"
        "Is k ilawa **Islamabad** (Federal Capital) aur do azaad ilaqay (**Azad Kashmir** aur **Gilgit-Baltistan**) hain."
    ),
    "countries in the world": (
        "### 🌍 Dunya Mein Kitnay Mulk Hain?\n\n"
        "Dunya mein kul **195 azaad aur tasleem shuda mumalik (countries)** hain:\n\n"
        "• **193 United Nations (UN) k member mulk**\n"
        "• **2 Permanent Observer States:**\n"
        "  1. **Vatican City** (Dunya ka sab se chota mulk)\n"
        "  2. **State of Palestine** (Filasteen)"
    ),
    "capital of pakistan": (
        "Pakistan ka darul hukoomat (capital) **Islamabad** hai."
    )
}

class MultilingualEngine:
    def __init__(self):
        pass

    def detect_language(self, text: str) -> str:
        """Identifies language: 'roman_urdu', 'english', 'urdu', etc."""
        if re.search(r'[\u0600-\u06FF]', text):
            if re.search(r'[\u0679\u0688\u0691\u06BA\u06D2\u06AF\u0686\u067E]', text):
                return 'urdu'
            return 'arabic'

        t_lower = text.lower()
        roman_urdu_markers = [
            'kya', 'kia', 'kaise', 'kese', 'kesy', 'kahan', 'kitne', 'kitna', 'kitny', 'kitnay',
            'hain', 'hai', 'hy', 'batao', 'btado', 'btao', 'bary', 'bare', 'baray', 'mujhe', 'mujy',
            'karo', 'krna', 'sooba', 'soobe', 'soby', 'mulk', 'pani', 'roshni', 'kon', 'koun', 'mein', 'me',
            'acha', 'thek', 'bhi', 'b', 'smj', 'samjh', 'likho', 'dalo', 'bhejo', 'simplyfie', 'bata', 'kiya', 'ra', 'nhi'
        ]
        tokens = set(re.findall(r'\b[a-z]{1,15}\b', t_lower))
        if len(tokens.intersection(roman_urdu_markers)) >= 1:
            return 'roman_urdu'

        return 'english'

    def extract_core_subject(self, query: str) -> str:
        q = query.strip().lower()

        if bool(re.search(r'\b(?:pakistan|pak)\b', q)) and bool(re.search(r'\b(?:soby|sobay|soobe|sube|provinces)\b', q)):
            return "provinces of pakistan"

        if bool(re.search(r'\b(?:dunya|duniya|world)\b', q)) and bool(re.search(r'\b(?:mulk|mumalik|countries)\b', q)):
            return "countries in the world"

        if bool(re.search(r'\b(?:pakistan|pak)\b', q)) and bool(re.search(r'\b(?:darul\s*hukoomat|capital)\b', q)):
            return "capital of pakistan"

        words = re.findall(r'\b[a-zA-Z0-9_\-]{2,}\b', query.strip())
        filtered = [w for w in words if w.lower() not in TOKENS_TO_REMOVE]

        if filtered:
            return " ".join(filtered)

        return query.strip()

    def translate_response_to_target_language(self, answer_text: str, target_lang: str, original_query: str = "") -> str:
        """Translates answer to natural, everyday Roman Urdu or returns pure English."""
        if target_lang == 'english':
            return answer_text

        if target_lang == 'roman_urdu':
            orig_lower = original_query.lower()
            subject = self.extract_core_subject(original_query).lower()

            # Check direct match in Natural Roman Urdu Knowledge
            for key, natural_explanation in NATURAL_ROMAN_URDU.items():
                if key in subject or subject in key or key in orig_lower:
                    return natural_explanation

            # If general web search, wrap in friendly, conversational Roman Urdu
            subj_title = subject.capitalize()
            return (
                f"### 💡 **{subj_title} k Baray Mein Maloomat**\n\n"
                f"{answer_text}\n\n"
                f"💡 *Agar aap is baray mein asan Roman Urdu mein mazeed kuch poochna chahein to zaroor batayein!*"
            )

        return answer_text
