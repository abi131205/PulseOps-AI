import os
from dotenv import load_dotenv

# Load configurations
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize SDK and flag status
API_ENABLED = False
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        API_ENABLED = True
        print("[Google Gemini API] Key detected. explanation service initialized.")
    except Exception as e:
        print(f"[Google Gemini API] Failed to initialize SDK: {e}. Falling back to template-based explanations.")
else:
    print("[Google Gemini API] GEMINI_API_KEY not found in environment. Running with local template-based explanations.")

def get_local_fallback_explanation(recommendation: dict) -> str:
    """
    Constructs a highly detailed, professional operational briefing locally.
    Ensures that the application operates correctly even without external API access.
    """
    action = recommendation.get("action")
    ops = recommendation.get("operational_priority_score", 50)
    reasoning = recommendation.get("reasoning", "")
    impact = recommendation.get("expected_impact", "")
    alternative = recommendation.get("alternative", "using standby inventory")
    
    return (
        f"⚠️ JUSTIFICATION: This action has been prioritized due to a high Operational Priority Score of {ops}/100. {reasoning} "
        f"📈 IMPACT: Implementing this transfer results in: {impact}. "
        f"⚙️ ALTERNATIVE: The alternative option ({alternative}) does not satisfy urgent capacity needs."
    )

def generate_recommendation_briefing(recommendation: dict) -> str:
    """
    Accepts a structured recommendation object and uses the Google Gemini API
    to compile a natural language justification for hospital coordinators.
    """
    if not API_ENABLED:
        return get_local_fallback_explanation(recommendation)
        
    try:
        import google.generativeai as genai
        
        # Configure model parameters
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        Act as an elite Hospital Operations Decision Support Coordinator.
        Your job is to translate a structured machine-generated resource recommendation into a clear, professional, and persuasive briefing for a hospital administrator.
        
        STRUCTURED RECOMMENDATION DATA:
        - Action: {recommendation.get('action')}
        - Operational Priority Score (OPS): {recommendation.get('operational_priority_score')}/100
        - Base Reasoning Factors: {recommendation.get('reasoning')}
        - Expected Operational Impact: {recommendation.get('expected_impact')}
        - Alternative Option: {recommendation.get('alternative')}
        
        INSTRUCTIONS:
        1. Keep the briefing concise (3 sentences maximum).
        2. Focus strictly on logistical efficiency, resource allocation, and equipment health.
        3. Do NOT make clinical or medical recommendations. Focus entirely on hospital operations.
        4. Do NOT calculate or change any scores. Use the provided Operational Priority Score (OPS).
        5. Format the briefing EXACTLY in the following structural layout:
           ⚠️ JUSTIFICATION: [1 sentence explaining the critical need based on base reasoning factors]
           📈 IMPACT: [1 sentence explaining the expected operational impact]
           ⚙️ ALTERNATIVE: [1 sentence explaining why the alternative option is less optimal than the recommended action]
        """
        
        response = model.generate_content(prompt)
        explanation = response.text.strip()
        
        if not explanation:
            return get_local_fallback_explanation(recommendation)
            
        return explanation
    except Exception as e:
        print(f"[Google Gemini API] Error calling model: {e}. Falling back to template-based explanation.")
        return get_local_fallback_explanation(recommendation)
