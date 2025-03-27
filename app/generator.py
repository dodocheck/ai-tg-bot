from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
from loguru import logger

load_dotenv()

client = AsyncOpenAI(base_url='https://openrouter.ai/api/v1',
                     api_key=os.getenv('AI_TOKEN'))


async def ask_ai(request, model):
    response = await client.chat.completions.create(
        messages=request,
        model=model
    )
    return response.choices[0].message.content, response.usage.total_tokens