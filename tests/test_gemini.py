import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


def env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def build_client() -> genai.Client:
    use_vertex = env_flag("GOOGLE_GENAI_USE_VERTEXAI", True)
    if use_vertex:
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        if not project:
            raise RuntimeError("GOOGLE_CLOUD_PROJECT is not set in .env")
        return genai.Client(vertexai=True, project=project, location=location)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in .env")
    return genai.Client(api_key=api_key)


def main() -> None:
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    client = build_client()
    prompt = (
        "Analyze these linked words and tell me if the relationship is correct: "
        "'Canine' -> 'Dog'. Answer strictly with 'True' or 'False'."
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    print(response.text)


if __name__ == "__main__":
    main()
