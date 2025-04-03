from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject
from loguru import logger
from dataclasses import dataclass, field

from app.generator import ask_ai
import app.keyboards as kb

user = Router()

max_tokens = 3000


@dataclass
class UserData:
    """Default User obj"""
    ai_model: str = 'deepseek/deepseek-chat-v3-0324:free'
    context: list[dict] = field(default_factory=lambda: [
        {'role': 'system',
         'content': 'answer in the same language I asked you. Desired response output format: If the user query is asking for a knowledge-based answer or is specifying a data processing or coding task, immediately proceed to the direct answer written as though it was a document. There will be no additional chatty dialog from the AI unless the user is directly conversing with the AI with a chat style. AI should appear to be a data processor, not a chat partner. Keep in mind that you answers will be delivered to me as telegram messages. Answer in detail but try to avoid huge answers.'}
    ])
    is_busy: bool = False


users = {}  # dict of users -> {user_id: UserData}


@user.message(Command('model'))
async def cmd_change_ai_model(message: Message) -> None:

    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = UserData()

    await message.answer(text='Выберите модель из списка',
                         reply_markup=kb.inline_kb_aimodel)


@user.callback_query(F.data)
async def callback_change_ai_model(callback: CallbackQuery) -> None:

    user_id = callback.from_user.id
    if user_id not in users:
        users[user_id] = UserData()

    users[user_id].ai_model = callback.data
    await callback.answer(f'Вы выбрали модель {callback.data}')


@user.message(Command('clear'))
async def cmd_clear(message: Message) -> None:
    """Clears chat context for particular user"""
    user_id = message.from_user.id

    if user_id not in users:
        users[user_id] = UserData()
    else:
        users[user_id].context = [{'role': 'system',
                                   'content': 'answer in the same language I asked you. Desired response output format: If the user query is asking for a knowledge-based answer or is specifying a data processing or coding task, immediately proceed to the direct answer written as though it was a document. There will be no additional chatty dialog from the AI unless the user is directly conversing with the AI with a chat style. AI should appear to be a data processor, not a chat partner. Keep in mind that you answers will be delivered to me as telegram messages. Answer in detail but try to avoid huge answers.'},]

    await message.react([{"type": "emoji", "emoji": "👌"}])


@user.message(Command('ai'))
async def ask_ai_in_private(message: Message, command: CommandObject) -> None:
    """ If in chat - add /ai before question """
    await _process_msg_to_ai(message, command.args)


@user.message(F.text, F.chat.type == "private")
async def ask_ai_in_private(message: Message) -> None:
    """ If in direct - write as it is """
    await _process_msg_to_ai(message, message.text)


async def _process_msg_to_ai(message: Message, msg_from_user: str) -> None:
    """Writes a response to user's particular message

    Args:
        message (Message): message_obj from particular user
        msg_from_user (str): text from user
    """
    user_id = message.from_user.id

    if not msg_from_user:
        # if no text was provided by user
        await message.react([{"type": "emoji", "emoji": "👀"}])
        return

    if user_id not in users:
        users[user_id] = UserData()

    if users[user_id].is_busy:
        await message.react([{"type": "emoji", "emoji": "👨‍💻"}])
        return

    users[user_id].is_busy = True

    try:
        users[user_id].context.append({'role': 'user',
                                       'content': msg_from_user})

        await message.react([{"type": "emoji", "emoji": "✍️"}])

        response, tokens_used = await ask_ai(users[user_id].context, users[user_id].ai_model)

        if tokens_used > max_tokens:  # compressing context to 1 message to control tokens spending
            msg = 'Сделай короткий пересказ нашего диалога от третьего лица. Себя называй как Бот, а меня - Пользователь'
            users[user_id].context.append({'role': 'user',
                                           'content': msg})
            summary, tokens_used = await ask_ai(users[user_id].context, users[user_id].ai_model)
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
