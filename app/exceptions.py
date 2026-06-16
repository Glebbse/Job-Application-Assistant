
from openai import APIConnectionError, APIError, AuthenticationError, RateLimitError
from pydantic import ValidationError


def format_ai_error(error: Exception) -> str:
    if isinstance(error, AuthenticationError):
        return f"OpenAI authentication failed. Check OPENAI_API_KEY\n Origin error: {str(error)}"
    elif isinstance(error, RateLimitError):
        return f"OpenAI rate limit or quota exceeded\n Origin error: {str(error)}"
    elif isinstance(error, APIConnectionError):
        return f"Could not connect to OpenAI API\n Origin error: {str(error)}"
    elif isinstance(error, APIError):
        return f"OpenAI API Error\n Origin error: {str(error)}"
    elif isinstance(error, ValidationError):
        return f"AI response did not match expected schema\n Origin error: {str(error)}"
    else:
        return f"Unexpected error: {str(error)}"
    
