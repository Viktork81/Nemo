import os
import openai

# The client will be initialized by the main script.
client = None

def initialize_client(api_key: str):
    """
    Initializes the OpenAI client with a provided API key and verifies it.
    Returns True on success, False on failure.
    """
    global client
    if not api_key or not api_key.strip():
        print("\n[ERROR] API key is missing. Cannot initialize OpenAI client.")
        client = None
        return False

    try:
        client = openai.OpenAI(api_key=api_key)
        client.models.list()  # Just to verify the key works
        print("[SUCCESS] OpenAI client initialized and key verified.")
        return True
    except openai.AuthenticationError:
        print("\n[ERROR] The provided OpenAI API key is invalid or has expired.")
        client = None
        return False
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred during OpenAI client initialization: {e}")
        client = None
        return False

def get_ai_response_with_history(system_prompt: str, history: list, model_name: str = "gpt-4o-2024-05-13") -> str:
    """
    Sends the full conversation history to the OpenAI model and gets a response.
    """
    if not client:
        return "░append_log \"[ERROR] OpenAI client not initialized. Cannot get AI response.\"█"

    messages = [{"role": "system", "content": system_prompt}] + history

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        ai_response_text = response.choices[0].message.content
        return ai_response_text

    except openai.APIError as e:
        error_message = f"[ERROR] OpenAI API error: {e}"
        print(error_message)
        return f"The API call failed with an error. I should log this. ░append_log \"{error_message}\"█"
    except Exception as e:
        error_message = f"[ERROR] An unexpected error occurred during API call: {e}"
        print(error_message)
        return f"An unexpected error occurred. I will log it. ░append_log \"{error_message}\"█"
