import httpx
import logging
from typing import AsyncIterator
from app.config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID

_MOCK = not ELEVENLABS_API_KEY

if _MOCK:
	logging.warning(
		"[WARNING] ELEVENLABS_API_KEY not set — TTS will return empty audio"
	)

ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"


async def generate_speech_stream(text: str, voice_id: str | None = None) -> AsyncIterator[bytes]:
	"""Stream speech audio chunks from ElevenLabs. Yields MP3 chunks as they arrive."""
	if _MOCK or not text.strip():
		return

	vid = voice_id or ELEVENLABS_VOICE_ID
	url = ELEVENLABS_TTS_URL.format(voice_id=vid)

	try:
		async with httpx.AsyncClient() as client:
			async with client.stream(
				"POST",
				url,
				headers={
					"xi-api-key": ELEVENLABS_API_KEY,
					"Content-Type": "application/json",
					"Accept": "audio/mpeg",
				},
				json={
					"text": text,
					"model_id": "eleven_turbo_v2_5",
					"voice_settings": {
						"stability": 0.4,
						"similarity_boost": 0.8,
						"style": 0.6,
						"use_speaker_boost": True,
					},
				},
				timeout=15.0,
			) as resp:
				resp.raise_for_status()
				async for chunk in resp.aiter_bytes(1024):
					yield chunk
	except Exception as e:
		logging.error(f"ElevenLabs TTS streaming error: {e}")
