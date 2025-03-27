from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction
from loguru import logger

from app.generator import ask_ai
from app.states import Chat

max_tokens = 3000

user = Router()

msgs_to_delete = {}

context = {}

ai_model = 'deepseek/deepseek-chat-v3-0324:free'


@user.message(Chat.busy)
async def skip_if_busy(message: Message):
    pass


@user.message(F.text.startswith('/забудь'))
async def cmd_clear(message: Message):
    context[message.from_user.id] = []
    context[message.from_user.id].append({'role': 'system',
                                          'content': 'answer in the same language I asked you. Desired response output format: If the user query is asking for a knowledge-based answer or is specifying a data processing or coding task, immediately proceed to the direct answer written as though it was a document. There will be no additional chatty dialog from the AI unless the user is directly conversing with the AI with a chat style. AI should appear to be a data processor, not a chat partner. Keep in mind that you answers will be delivered to me as telegram messages. Answer in detail but try to avoid huge answers.'})
    await message.react([{"type": "emoji", "emoji": "👌"}])


@user.message(F.text.startswith('/дипсик'))
async def get_ai_response(message: Message, state: FSMContext):
    await state.set_state(Chat.busy)
    msg_from_user = message.text[7:].strip()
    try:
        if message.from_user.id not in context:
            context[message.from_user.id] = []
            context[message.from_user.id].append({'role': 'system',
                                          'content': 'answer in the same language I asked you. Desired response output format: If the user query is asking for a knowledge-based answer or is specifying a data processing or coding task, immediately proceed to the direct answer written as though it was a document. There will be no additional chatty dialog from the AI unless the user is directly conversing with the AI with a chat style. AI should appear to be a data processor, not a chat partner. Keep in mind that you answers will be delivered to me as telegram messages. Answer in detail but try to avoid huge answers.'})

        await message.react([{"type": "emoji", "emoji": "🤔"}])

        context[message.from_user.id].append({'role': 'user',
                                              'content': msg_from_user})
        response, tokens_used = await ask_ai(context[message.from_user.id], ai_model)
        if tokens_used > max_tokens:
            msg = 'Сделай короткий пересказ нашего диалога от третьего лица. Себя называй как Бот, а меня - Пользователь'
            context[message.from_user.id].append({'role': 'user',
                                                  'content': msg})
            summary, tokens_used = await ask_ai(context[message.from_user.id], ai_model)
            context[message.from_user.id] = []
            context[message.from_user.id].append({'role': 'system',
                                                  'content': summary})

        context[message.from_user.id].append({'role': 'assistant',
                                              'content': response})

        await message.reply(response, parse_mode='Markdown')
    except Exception as error:
        logger.error(f'Произошла ошибка, но Вы в этом не виноваты, не переживайте.\n'
                     f'Повторите пожалуйста Ваш запрос. Можете его скорректировать при желании, если Ваша квалификация'
                     f'позволяет разобраться в ошибке:\n{error}')

    await state.clear()
