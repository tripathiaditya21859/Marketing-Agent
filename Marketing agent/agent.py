import os
from openai import OpenAI
from dotenv import load_dotenv

# Check both .env and ab.env just in case
load_dotenv(".env")
load_dotenv("ab.env")

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_KEY, timeout=5.0) if OPENAI_KEY and not OPENAI_KEY.startswith("your_") else None
WEBSITE_URL = os.getenv("WEBSITE_BASE_URL", "https://mywebsite.com")

def generate_agent_response(source: str, user_name: str, query: str) -> dict:
    utm_url = f"{WEBSITE_URL}/catalog?utm_source={source}&utm_medium=ai_agent&utm_campaign=omnichannel_conversion"

    system_prompt = f"""
    You are an Omnichannel AI Sales Agent.
    Channel: {source.upper()}
    Target Action: Guide user to website: {utm_url}
    Keep response punchy and under 40 words.
    """

    user_prompt = f"Lead Name: {user_name}\nInquiry: {query}"

    reply = None
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=150,
                temperature=0.7,
                timeout=5.0  # 5-second hard limit so it never hangs
            )
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Agent Warning] OpenAI call timed out or failed: {e}. Using fallback.")
            reply = None

    if not reply:
        reply = (
            f"Hello {user_name}! Thanks for reaching out via {source.upper()} regarding '{query}'. "
            f"Explore our catalog and pricing here: {utm_url}"
        )

    return {
        "reply": reply,
        "landing_url": utm_url
    }