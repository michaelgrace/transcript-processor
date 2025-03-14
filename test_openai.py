import os
from dotenv import load_dotenv
import openai

load_dotenv()

# Get the API key
api_key = os.getenv("API_KEY")
model = os.getenv("AI_MODEL", "gpt-4-turbo")

print(f"Testing OpenAI connection with model: {model}")
print(f"API Key configured: {'Yes (first 5 chars: ' + api_key[:5] + '...)' if api_key else 'No'}")

try:
    openai.api_key = api_key
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Format this text into paragraphs: This is a test. It has multiple sentences. They should be formatted properly."}
        ],
        temperature=0.3,
        max_tokens=500
    )
    print("✅ Success! Response:")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"❌ Error: {str(e)}")