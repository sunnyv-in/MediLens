from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("KEY:", os.getenv("GEMINI_API_KEY")[:15])

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Reply only with Hello"
)

print(response.text)