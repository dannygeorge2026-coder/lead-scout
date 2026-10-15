from backend.config import settings


def test_config_loading():
    assert settings.GOOGLE_API_KEY is not None, "GOOGLE_API_KEY must be set"
    assert settings.TAVILY_API_KEY is not None, "TAVILY_API_KEY must be set"
    assert settings.DEFAULT_MODEL == "gemini-2.5-flash"
    print("\n✅ Config & Environment loaded successfully!")


if __name__ == "__main__":
    test_config_loading()