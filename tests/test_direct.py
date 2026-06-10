from app.ai_client import _call_ollama
try:
    print(_call_ollama("Say hello"))
except Exception as e:
    print("FAILED:", type(e).__name__, str(e))
