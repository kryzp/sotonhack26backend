import os
from dotenv import load_dotenv

load_dotenv()
from google import genai
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

try:
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="say hello",
    )
    print("SUCCESS")
    print(resp.text)
except Exception as e:
    print("EXCEPTION:", type(e).__name__)
    print(str(e))
