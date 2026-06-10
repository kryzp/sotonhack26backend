import json
import random
import pathlib
from app.config import (
	GOOGLE_CLOUD_LOCATION,
	GOOGLE_CLOUD_PROJECT,
	GOOGLE_GENAI_USE_VERTEXAI,
	GEMINI_API_KEY,
	GEMINI_MODEL,
)

_PROMPTS_DIR = pathlib.Path(__file__).parent / "prompts"
_MOCK = (
	not GOOGLE_CLOUD_PROJECT
	if GOOGLE_GENAI_USE_VERTEXAI
	else not GEMINI_API_KEY
)

if _MOCK:
	import logging
	if GOOGLE_GENAI_USE_VERTEXAI:
		logging.warning(
			"[WARNING] GOOGLE_CLOUD_PROJECT not set for Vertex AI — running in MOCK MODE "
			"(fake words & auto-valid answers)"
		)
	else:
		logging.warning(
			"[WARNING] GEMINI_API_KEY not set — running in MOCK MODE "
			"(fake words & auto-valid answers)"
		)

_MOCK_PAIRS = [
	("apple", "ocean"),
	("castle", "music"),
	("fire", "library"),
	("mountain", "piano"),
	("robot", "garden"),
	("diamond", "storm"),
	("telescope", "cake"),
	("shadow", "compass"),
	("bridge", "dream"),
	("clock", "forest"),
	("rocket", "bread"),
	("mirror", "whale"),
	("candle", "airport"),
	("umbrella", "volcano"),
	("anchor", "rainbow")
]


_genai_client = None

def _client():
	global _genai_client
	if _genai_client is None:
		from google import genai
		if GOOGLE_GENAI_USE_VERTEXAI:
			_genai_client = genai.Client(
				vertexai=True,
				project=GOOGLE_CLOUD_PROJECT,
				location=GOOGLE_CLOUD_LOCATION,
			)
		else:
			_genai_client = genai.Client(api_key=GEMINI_API_KEY)
	return _genai_client


def _load_prompt(filename: str) -> str:
	return (_PROMPTS_DIR / filename).read_text(encoding="utf-8")


def _strip_fences(text: str) -> str:
	text = text.strip()
	
	if text.startswith("```"):
		text = "\n".join(text.split("\n")[1:])
	
	if text.endswith("```"):
		text = "\n".join(text.split("\n")[:-1])
	
	return text.strip()


def generate_words(amount: int = 1) -> list:
	if _MOCK:
		pairs = random.sample(_MOCK_PAIRS, min(amount, len(_MOCK_PAIRS)))
		return [{"word_one": p[0], "word_two": p[1]} for p in pairs]

	try:
		template = _load_prompt("generate_words.txt")
		prompt = template.format(amount=amount)
		resp = _client().models.generate_content(
			model=GEMINI_MODEL,
			contents=prompt,
		)
		return json.loads(_strip_fences(resp.text))
	except Exception as e:
		import logging
		logging.error(f"Gemini API Error in generate_words: {e}. Falling back to mock data.")
		pairs = random.sample(_MOCK_PAIRS, min(amount, len(_MOCK_PAIRS)))
		return [{"word_one": p[0], "word_two": p[1]} for p in pairs]


DIFFICULTY_INSTRUCTIONS = {
	"easy": (
		"DIFFICULTY: EASY — Be generous and forgiving. Accept any connection that vaguely makes sense, "
		"even if it's a stretch. Creative, funny, or loose chains are totally fine. "
		"Only reject answers that are complete nonsense or don't mention both words."
	),
	"medium": (
		"DIFFICULTY: MEDIUM — Allow creative and funny chains, but require some logical thread. "
		"Each step should have a defensible reason. Reject hand-waving or 'vibes-only' connections."
	),
	"hard": (
		"DIFFICULTY: HARD — Require clear, direct, logical reasoning at every step. "
		"Penalise vague leaps, metaphors without substance, and 'reminds me of' connections. "
		"The chain must be defensible to a skeptic."
	),
	"brutal": (
		"DIFFICULTY: BRUTAL — Only accept tight, well-reasoned chains with verifiable logic. "
		"Every single step must be factually or logically sound. Reject anything subjective, "
		"hand-wavy, or relying on loose associations. Be merciless."
	),
}


def validate_answer(word_one: str, word_two: str, answer: str, difficulty: str = "medium", first_player_answer: str | None = None) -> dict:
	if _MOCK:
		steps = random.randint(2, 5)
		overlap = random.randint(0, 2) if first_player_answer else 0
		return {
			"valid": True,
			"score": random.randint(40, 95),
			"steps": steps,
			"short_reason": "Mock mode — auto-approved",
			"overlap_penalty": overlap,
		}

	diff_text = DIFFICULTY_INSTRUCTIONS.get(difficulty, DIFFICULTY_INSTRUCTIONS["medium"])

	overlap_text = ""
	if first_player_answer:
		overlap_text = (
			f"\n\nIMPORTANT — OVERLAP CHECK:\n"
			f"The first player's answer was: \"{first_player_answer}\"\n"
			f"If the second player reuses the same intermediate words or connections as the first player, "
			f"count how many shared intermediate steps there are and return that as \"overlap_penalty\" (integer). "
			f"Each shared intermediate concept/word counts as 1 overlap. If no overlap, set overlap_penalty to 0."
		)

	try:
		template = _load_prompt("validate_answer.txt")
		prompt = template.format(
			word_one=word_one,
			word_two=word_two,
			answer=answer,
			difficulty_instructions=diff_text,
		) + overlap_text

		resp = _client().models.generate_content(
			model=GEMINI_MODEL,
			contents=prompt,
		)

		result = json.loads(_strip_fences(resp.text))
		if "overlap_penalty" not in result:
			result["overlap_penalty"] = 0
		return result
	except Exception as e:
		import logging
		logging.error(f"Gemini API Error in validate_answer: {e}. Falling back to mock data.")
		return {
			"valid": True,
			"score": random.randint(40, 95),
			"steps": random.randint(2, 5),
			"short_reason": "Mock mode fallback — quota exceeded",
			"overlap_penalty": 0,
		}
