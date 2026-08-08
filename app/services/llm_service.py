from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

SYSTEM_PROMPT = (
    "You are a helpful, personalized assistant. Be direct and concise "
    "unless the user asks for more detail."
)

def chat(history:list[dict]) -> str:
    messages = [{"role":"system","content":SYSTEM_PROMPT},*history]
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages
    )

    return response.choices[0].message.content

def stream_chat(history:list[dict]) -> str:
    messages = [{"role":"system","content":SYSTEM_PROMPT},*history]
    response_stream = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages,
        temperature=0.4,
        stream=True
    )

    for chunk in response_stream:
        data = chunk.choices[0].delta.content
        if data:
            yield data
    # return response.choices[0].message.content

def generate_title(message:str) -> str:
    """Generate a title for the conversation based on users first message"""
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {
                "role":"system",
                "content":("Generate a short, plain-text title (4-6 words) summarizing "
                    "this message. No quotation marks, no trailing punctuation. "
                    "Respond with only the title.")
            },
            {"role":"user","content":message}
        ],
        temperature=0.4,
        max_tokens=20
    )
    return response.choices[0].message.content









