from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from loguru import logger
from dataclasses import dataclass

from app.generator import ask_ai


user = Router()

max_tokens = 3000

ai_model = 'deepseek/deepseek-chat-v3-0324:free'


@dataclass
class UserData:
    context: list
    is_busy: bool


users = {}  # dict of users -> {user_id: UserData}


@user.message(Command('clear'))
async def cmd_clear(message: Message):
    user_id = message.from_user.id

    if user_id not in users:
        users[user_id] = UserData(context=[],
                                  is_busy=False)
    else:
        users[user_id].context = []

    users[user_id].context.append({'role': 'system',
                                   'content': 'answer in the same language I asked you. Desired response output format: If the user query is asking for a knowledge-based answer or is specifying a data processing or coding task, immediately proceed to the direct answer written as though it was a document. There will be no additional chatty dialog from the AI unless the user is directly conversing with the AI with a chat style. AI should appear to be a data processor, not a chat partner. Keep in mind that you answers will be delivered to me as telegram messages. Answer in detail but try to avoid huge answers.'})

    await message.react([{"type": "emoji", "emoji": "👌"}])


@user.message(Command('ai'))
async def get_ai_response(message: Message, command: CommandObject):
    user_id = message.from_user.id

    if user_id not in users:
        users[user_id] = UserData(context=[],
                                  is_busy=False)
        users[user_id].context.append({'role': 'system',
                                       'content': 'answer in the same language I asked you. Desired response output format: If the user query is asking for a knowledge-based answer or is specifying a data processing or coding task, immediately proceed to the direct answer written as though it was a document. There will be no additional chatty dialog from the AI unless the user is directly conversing with the AI with a chat style. AI should appear to be a data processor, not a chat partner. Keep in mind that you answers will be delivered to me as telegram messages. Answer in detail but try to avoid huge answers.'})

    if users[user_id].is_busy:
        await message.react([{"type": "emoji", "emoji": "👨‍💻"}])
        return

    msg_from_user = command.args
    if not msg_from_user:
        await message.react([{"type": "emoji", "emoji": "👀"}])
        return

    users[user_id].is_busy = True

    try:
        users[user_id].context.append({'role': 'user',
                                       'content': msg_from_user})

        await message.react([{"type": "emoji", "emoji": "✍️"}])

        response, tokens_used = await ask_ai(users[user_id].context, ai_model)

        if tokens_used > max_tokens:
            msg = 'Сделай короткий пересказ нашего диалога от третьего лица. Себя называй как Бот, а меня - Пользователь'
            users[user_id].context.append({'role': 'user',
                                           'content': msg})
            summary, tokens_used = await ask_ai(users[user_id].context, ai_model)
            users[user_id].context = []
            users[user_id].context.append({'role': 'system',
                                           'content': summary})
            print(1)

        users[user_id].context.append({'role': 'assistant',
                                       'content': response})

        await message.reply(response, parse_mode='Markdown')

    except Exception as error:
        logger.error(f'Error: {error}')

    users[user_id].is_busy = False
