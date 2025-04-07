from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = AsyncOpenAI(base_url='https://openrouter.ai/api/v1',
                     api_key=os.getenv('AI_TOKEN'))


async def ask_ai(request: list[dict], model: str) -> str:
    """Gets a response from ai

    Args:
        request (list[dict]): chat's context
        model (str): ai model name from API

    Returns:
        str: answer from AI
    """
    response = await client.chat.completions.create(
        messages=request,
        model=model
    )
    return response.choices[0].message.content