import os
import joblib
import json
import httpx
import re
from dotenv import load_dotenv

load_dotenv()

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml', 'threat_model.pkl')
classifier = None

def load_classifier():
    global classifier
    if os.path.exists(MODEL_PATH):
        classifier = joblib.load(MODEL_PATH)
    else:
        print("Warning: threat_model.pkl not found. Run train_threat.py first.")

def classify(text: str, language: str = "English"):
    global classifier

    lang_map = {
        "english": "English",
        "hindi": "Hindi",
        "telugu": "Telugu",
        "tamil": "Tamil",
        "marathi": "Marathi",
        "hinglish": "Hinglish",
    }
    language = lang_map.get((language or "English").strip().lower(), language or "English")
    
    # Defaults
    tier = 1
    confidence = 0.0
    
    if classifier:
        # Predict uses [text] as array
        try:
            tier_pred = classifier.predict([text])[0]
            tier = int(tier_pred)
            probs = classifier.predict_proba([text])[0]
            confidence = float(max(probs))
            
            # Additional fallback logic: if a short text has low probability but strong words, we push it to fallback
        except Exception as e:
            print(f"Classification error: {str(e)}")
            confidence = 0.0

    if confidence < 0.70:
        return fallback_to_claude(text, language)
        
    # Local mapping to return objects based on tier matches front-end expectations
    tier_map = {
        1: {
            "tier": 1,
            "label": "Trolling",
            "key_phrases": [word for word in text.split()[:3] if len(word) > 4],
            "legal_sections": [],
            "recommended_actions": ["Document", "Block", "Move on"],
            "explanation": "This content contains generalized insults without specific threats of violence, harm, or sexual harassment."
        },
        2: {
            "tier": 2,
            "label": "Hate Speech",
            "key_phrases": [word for word in text.split()[:4]],
            "legal_sections": [
                {"name": "IT Act Section 66A", "description": "Sending offensive messages", "section_number": "66A"},
                {"name": "IPC Section 504", "description": "Intentional insult to provoke breach of peace", "section_number": "504"}
            ],
            "recommended_actions": ["Screenshot → Vault", "Platform report", "Monitor"],
            "explanation": "This content contains targeted hate speech or severe abuse aimed at causing emotional distress."
        },
        3: {
            "tier": 3,
            "label": "Sexual Threat",
            "key_phrases": [word for word in text.split()[:4]],
            "legal_sections": [
                {"name": "IT Act Section 66E", "description": "Violation of Privacy (sharing images)", "section_number": "66E"},
                {"name": "IPC Section 354A", "description": "Sexual Harassment", "section_number": "354A"}
            ],
            "recommended_actions": ["Vault evidence", "Generate legal notice", "Contact NGO"],
            "explanation": "This content contains explicit sexual harassment, blackmail, or non-consensual sharing threats."
        },
        4: {
            "tier": 4,
            "label": "Credible Danger",
            "key_phrases": [word for word in text.split()[:4]],
            "legal_sections": [
                {"name": "IPC Section 503", "description": "Criminal Intimidation", "section_number": "503"}
            ],
            "recommended_actions": ["Call 1930 NOW", "Vault evidence", "Generate FIR", "Safe location"],
            "explanation": "This content demonstrates credible, specific, and imminent threat to your physical safety."
        }
    }
    
    result = tier_map.get(tier, tier_map[1])
    result["confidence"] = round(confidence * 100, 2)
    return result


def fallback_to_claude(text: str, language: str):
    lowered = (text or "").lower()

    def _phrases(source: str):
        tokens = [t for t in re.findall(r"[a-zA-Z0-9']+", source) if len(t) >= 4]
        if not tokens:
            return ["abusive message detected"]
        return tokens[:4]

    def _local_rule_based_result():
        danger_words = ["kill", "murder", "acid", "shoot", "coming for you", "find you", "rape"]
        sexual_words = ["nude", "nudes", "leak", "mms", "sex", "morph", "deepfake", "blackmail"]
        abuse_words = ["hate", "trash", "slut", "bitch", "chutiya", "harass", "abuse"]

        tier = 1
        label = "Trolling"
        explanation = "The text appears abusive but does not indicate clear imminent physical harm."
        legal_sections = [
            {"name": "IPC Section 509", "description": "Word, gesture or act intended to insult modesty of a woman", "section_number": "509"}
        ]
        actions = ["Save evidence in vault", "Block the sender", "Report account on platform"]

        if any(w in lowered for w in danger_words):
            tier = 4
            label = "Credible Danger"
            explanation = "The text contains language indicating potential imminent physical danger."
            legal_sections = [
                {"name": "IPC Section 503", "description": "Criminal intimidation", "section_number": "503"},
                {"name": "IPC Section 506", "description": "Punishment for criminal intimidation", "section_number": "506"}
            ]
            actions = ["Call 1930 immediately", "Preserve all evidence", "Generate FIR draft", "Contact nearest police station"]
        elif any(w in lowered for w in sexual_words):
            tier = 3
            label = "Sexual Threat"
            explanation = "The content indicates sexual harassment, extortion, or intimate-image abuse risk."
            legal_sections = [
                {"name": "IT Act Section 66E", "description": "Violation of privacy", "section_number": "66E"},
                {"name": "IPC Section 354A", "description": "Sexual harassment", "section_number": "354A"},
                {"name": "IPC Section 354D", "description": "Stalking", "section_number": "354D"}
            ]
            actions = ["Secure screenshot in vault", "Generate legal notice", "File complaint to cyber cell"]
        elif any(w in lowered for w in abuse_words):
            tier = 2
            label = "Hate Speech"
            explanation = "The content includes targeted abusive language and harassment indicators."
            legal_sections = [
                {"name": "IPC Section 504", "description": "Intentional insult with intent to provoke breach of peace", "section_number": "504"},
                {"name": "IPC Section 509", "description": "Insulting the modesty of a woman", "section_number": "509"}
            ]
            actions = ["Save proof in vault", "Report on platform", "Escalate if repeated"]

        return {
            "tier": tier,
            "label": label,
            "confidence": 74.0,
            "key_phrases": _phrases(lowered),
            "legal_sections": legal_sections,
            "recommended_actions": actions,
            "explanation": explanation
        }

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return _local_rule_based_result()

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        system_prompt = """You are an Indian cyber law expert. 
Classify this text into: 
tier 1 (trolling), tier 2 (hate speech), 
tier 3 (sexual threat), tier 4 (credible danger).
Return JSON only matching exactly this structure:
{
  "tier": integer,
  "label": string,
  "confidence": float (percentage without % sign),
  "key_phrases": [string array of 3-4 extracted phrases],
  "legal_sections": [{"name": str, "description": str, "section_number": str}],
  "recommended_actions": [string array of 3-4 quick steps],
  "explanation": string
}"""
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=600,
            system=system_prompt,
            messages=[{"role": "user", "content": f"Text: {text}\nLanguage preference: {language}"}]
        )
        
        content = response.content[0].text.strip()
        # Find JSON boundaries
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end != -1:
            return json.loads(content[start:end])
        return json.loads(content)
        
    except Exception as e:
        print(f"Claude fallback failed: {str(e)}")
        result = _local_rule_based_result()
        result["confidence"] = 62.0
        result["explanation"] = f"Automatic AI evaluation failed; fallback safety model used. {result['explanation']}"
        return result
