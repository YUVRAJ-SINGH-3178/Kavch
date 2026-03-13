import os
import datetime
from dotenv import load_dotenv

load_dotenv()


def _normalize_doc_type(doc_type: str) -> str:
    value = (doc_type or "").strip().lower()
    aliases = {
        "fir": "FIR Draft",
        "fir draft": "FIR Draft",
        "platform takedown": "Platform Takedown",
        "takedown": "Platform Takedown",
        "legal notice": "Legal Notice",
        "notice": "Legal Notice",
        "ncw complaint": "NCW Complaint",
        "ncw": "NCW Complaint",
    }
    return aliases.get(value, doc_type or "FIR Draft")


def _normalize_language(language: str) -> str:
    value = (language or "English").strip().lower()
    aliases = {
        "english": "English",
        "hindi": "Hindi",
        "telugu": "Telugu",
        "tamil": "Tamil",
        "marathi": "Marathi",
        "hinglish": "Hinglish",
    }
    return aliases.get(value, "English")


def _fallback_document(doc_type: str, city: str, platform: str, date: str, language: str, incident_text: str, evidence_ids: list) -> str:
    evidence_block = "\n".join([f"- {e}" for e in (evidence_ids or [])]) or "- None"
    incident = incident_text or "Incident details to be inserted by complainant."

    templates = {
        "English": {
            "FIR Draft": f"""To,
The Station House Officer,
Cyber Crime Police Station, {city}

Date: {date}

Subject: FIR for cyber harassment and intimidation on {platform}

Respected Sir/Madam,

I wish to lodge this FIR regarding cyber harassment on {platform}. Incident summary: {incident}

Applicable legal provisions may include IPC 354D/503/506/509 and relevant IT Act provisions.

Evidence IDs:
{evidence_block}

I request registration of FIR and immediate investigation.

Complainant Name: ____________________
Contact: ____________________
Signature: ____________________
""",
            "Platform Takedown": f"""To,
Grievance Officer,
{platform}

Date: {date}

Subject: Urgent takedown request for abusive/unauthorized content

I request immediate removal of harmful content under IT (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021 and applicable IT Act provisions.

Incident summary: {incident}

Evidence IDs:
{evidence_block}

Please remove the content, preserve metadata, and confirm action.

Name: ____________________
Email/Phone: ____________________
""",
            "Legal Notice": f"""LEGAL NOTICE

Date: {date}
From: Complainant (details to be filled)
To: Opposite Party (name/address to be filled)

Subject: Cease and desist from cyber harassment/defamation

Under instructions from my client, you are hereby called upon to immediately cease unlawful acts including online harassment, intimidation, and reputational harm.

Incident summary: {incident}
Platform: {platform}
City: {city}

Evidence IDs:
{evidence_block}

Failing compliance within 48 hours, my client will initiate civil and criminal proceedings.
""",
            "NCW Complaint": f"""To,
The Chairperson,
National Commission for Women (NCW)

Date: {date}

Subject: Complaint regarding gender-based cyber harassment

I am filing this complaint regarding sustained online harassment and safety concerns.

Incident summary: {incident}
Platform: {platform}
City: {city}

Evidence IDs:
{evidence_block}

I request urgent intervention, advisory to concerned authorities, and protection measures.

Complainant details:
Name: ____________________
Contact: ____________________
Address: ____________________
""",
        },
        "Hindi": {
            "FIR Draft": f"""सेवा में,
थाना प्रभारी,
साइबर क्राइम पुलिस स्टेशन, {city}

दिनांक: {date}

विषय: {platform} पर साइबर उत्पीड़न के संबंध में एफआईआर दर्ज करने हेतु आवेदन

महोदय/महोदया,

मैं {platform} पर हुए साइबर उत्पीड़न की शिकायत दर्ज करना चाहती/चाहता हूं। घटना का संक्षेप: {incident}

संभावित धाराएं: IPC 354D/503/506/509 तथा आईटी अधिनियम की प्रासंगिक धाराएं।

साक्ष्य आईडी:
{evidence_block}

कृपया एफआईआर दर्ज कर आवश्यक जांच करें।
""",
            "Platform Takedown": f"""सेवा में,
ग्रिवांस ऑफिसर,
{platform}

दिनांक: {date}

विषय: आपत्तिजनक/अनधिकृत सामग्री हटाने हेतु तात्कालिक अनुरोध

मैं आईटी नियम, 2021 के तहत हानिकारक सामग्री हटाने का अनुरोध करती/करता हूं। घटना: {incident}

साक्ष्य आईडी:
{evidence_block}

कृपया सामग्री हटाकर कार्रवाई की पुष्टि करें।
""",
            "Legal Notice": f"""विधिक नोटिस

दिनांक: {date}

विषय: साइबर उत्पीड़न एवं मानहानि संबंधी गतिविधियां तत्काल बंद करने हेतु नोटिस

आपको सूचित किया जाता है कि आप मेरे मुवक्किल के विरुद्ध अवैध ऑनलाइन कृत्य तुरंत बंद करें। घटना: {incident}

प्लेटफॉर्म: {platform}
शहर: {city}
साक्ष्य आईडी:
{evidence_block}

48 घंटे में पालन न करने पर विधिक कार्यवाही की जाएगी।
""",
            "NCW Complaint": f"""सेवा में,
अध्यक्ष महोदया,
राष्ट्रीय महिला आयोग (NCW)

दिनांक: {date}

विषय: लैंगिक आधार पर साइबर उत्पीड़न के संबंध में शिकायत

मैं ऑनलाइन उत्पीड़न के संबंध में शिकायत प्रस्तुत कर रही/रहा हूं। घटना: {incident}

प्लेटफॉर्म: {platform}
शहर: {city}
साक्ष्य आईडी:
{evidence_block}

कृपया त्वरित हस्तक्षेप और आवश्यक सहायता प्रदान करें।
""",
        },
    "Telugu": {
        "FIR Draft": f"""కు,
సైబర్ క్రైమ్ పోలీస్ స్టేషన్ అధికారి, {city}

తేదీ: {date}

విషయం: {platform} లో సైబర్ వేధింపులపై FIR ఫిర్యాదు

ఘటన సారాంశం: {incident}

సాక్ష్య IDలు:
{evidence_block}
""",
        "Platform Takedown": f"""కు,
గ్రీవెన్స్ ఆఫీసర్, {platform}

తేదీ: {date}

విషయం: హానికర కంటెంట్ తొలగింపు కోసం అత్యవసర అభ్యర్థన

సాక్ష్య IDలు:
{evidence_block}
""",
        "Legal Notice": f"""లీగల్ నోటీస్

తేదీ: {date}

మీరు సైబర్ వేధింపులు తక్షణం నిలిపివేయాలి. లేకపోతే చట్టపరమైన చర్యలు తీసుకోబడతాయి.

ప్లాట్‌ఫారం: {platform}
నగరం: {city}
సాక్ష్య IDలు:
{evidence_block}
""",
        "NCW Complaint": f"""కు,
జాతీయ మహిళా కమిషన్ (NCW)

తేదీ: {date}

విషయం: మహిళలపై సైబర్ వేధింపుల ఫిర్యాదు

ఘటన సారాంశం: {incident}
సాక్ష్య IDలు:
{evidence_block}
""",
    },
    "Tamil": {
        "FIR Draft": f"""அனைவருக்கும்,
சைபர் குற்றப்பிரிவு காவல் நிலைய அதிகாரி, {city}

தேதி: {date}

பொருள்: {platform} இல் நடந்த சைபர் தொல்லை குறித்து FIR மனு

நிகழ்வு சுருக்கம்: {incident}

ஆதார IDகள்:
{evidence_block}
""",
        "Platform Takedown": f"""To,
Grievance Officer, {platform}

தேதி: {date}

பொருள்: தீங்கான உள்ளடக்கத்தை உடனடி நீக்கம் செய்ய கோரிக்கை

ஆதார IDகள்:
{evidence_block}
""",
        "Legal Notice": f"""சட்ட நோட்டீஸ்

தேதி: {date}

சைபர் தொல்லையை உடனடியாக நிறுத்துமாறு இதன் மூலம் அறிவிக்கப்படுகிறது.

மேடை: {platform}
நகர்: {city}
ஆதார IDகள்:
{evidence_block}
""",
        "NCW Complaint": f"""To,
National Commission for Women (NCW)

தேதி: {date}

பொருள்: பெண்களுக்கு எதிரான சைபர் தொல்லை குறித்த புகார்

நிகழ்வு சுருக்கம்: {incident}
ஆதார IDகள்:
{evidence_block}
""",
    },
    "Marathi": {
        "FIR Draft": f"""प्रति,
सायबर क्राइम पोलीस स्टेशन अधिकारी, {city}

दिनांक: {date}

विषय: {platform} वर झालेल्या सायबर छळाबाबत FIR अर्ज

घटनेचा सारांश: {incident}

पुरावा आयडी:
{evidence_block}
""",
        "Platform Takedown": f"""प्रति,
ग्रीव्हन्स ऑफिसर, {platform}

दिनांक: {date}

विषय: हानिकारक सामग्री तात्काळ काढण्याबाबत विनंती

पुरावा आयडी:
{evidence_block}
""",
        "Legal Notice": f"""कायदेशीर नोटीस

दिनांक: {date}

सायबर छळ तात्काळ थांबवावा, अन्यथा कायदेशीर कारवाई करण्यात येईल.

प्लॅटफॉर्म: {platform}
शहर: {city}
पुरावा आयडी:
{evidence_block}
""",
        "NCW Complaint": f"""प्रति,
राष्ट्रीय महिला आयोग (NCW)

दिनांक: {date}

विषय: महिलांविरुद्ध सायबर छळाबाबत तक्रार

घटनेचा सारांश: {incident}
पुरावा आयडी:
{evidence_block}
""",
    },
    }

    lang_templates = templates.get(language, templates["English"])
    return lang_templates.get(doc_type, lang_templates["FIR Draft"])

def generate_document(doc_type: str, city: str, platform: str, date: str, language: str, incident_text: str, evidence_ids: list):
    doc_type = _normalize_doc_type(doc_type)
    language = _normalize_language(language)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        return {
            "document_type": doc_type,
            "content": _fallback_document(doc_type, city, platform, date, language, incident_text, evidence_ids),
            "language": language,
            "generated_at": datetime.datetime.now().isoformat(),
            "applicable_sections": [],
            "filing_instructions": "AI key missing, so an offline draft was generated. Review and file with your local authority/platform."
        }

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        doc_specific_rules = {
            "FIR Draft": "Produce a police-style FIR application with station header, facts, legal sections, prayer, verification clause.",
            "Platform Takedown": "Produce a formal intermediary takedown notice to the platform grievance officer under IT Rules 2021.",
            "Legal Notice": "Produce an advocate-style legal notice to the alleged offender with cease-and-desist language and timeline for compliance.",
            "NCW Complaint": "Produce an NCW complaint letter with gender-based harm framing, relief sought, and request for intervention.",
        }

        system_prompt = f"""You are an expert Indian cyber law attorney specializing in women's digital safety cases.
Generate formal legal documents following exact Indian legal formatting requirements.

You know: IT Act 2000 (amended 2008), IPC sections 354D/499/500/506/507/509, Protection of Women from Domestic Violence Act, NCW complaint procedures, Cybercrime portal filing requirements.

Always include: proper legal headers, case facts section, relevant sections with exact wording, prayer/relief sought, verification clause.

Document type is strictly: {doc_type}
Type-specific rule: {doc_specific_rules.get(doc_type, 'Produce a formal legal document matching the requested type.')}

Respond in {language}. Return plain text document only. No markdown. No explanation. Just the document."""

        user_prompt = f"""Generate a {doc_type} for the following incident:
City: {city}
Platform: {platform}
Date: {date}
Incident: {incident_text}
Evidence IDs: {', '.join(evidence_ids) if evidence_ids else 'None provided'}

Make it ready to submit. Fill all standard fields."""

        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        doc_text = response.content[0].text.strip()
        
        return {
            "document_type": doc_type,
            "content": doc_text,
            "language": language,
            "generated_at": datetime.datetime.now().isoformat(),
            "applicable_sections": ["Refer to Document Body"],
            "filing_instructions": "Review carefully, fill in any bracketed information, and submit to your local cyber cell or platform grievance officer."
        }
        
    except Exception as e:
        return {
            "document_type": doc_type,
            "content": _fallback_document(doc_type, city, platform, date, language, incident_text, evidence_ids),
            "language": language,
            "generated_at": datetime.datetime.now().isoformat(),
            "applicable_sections": [],
            "filing_instructions": f"AI generation failed ({str(e)}). Offline draft generated instead."
        }
