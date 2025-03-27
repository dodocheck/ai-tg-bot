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


@user.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('/start - просто здороваемся;\n'
                         '/clear - очистить контекст беседы.')


@user.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f'Добро пожаловать!')
    await message.answer('Какой у Вас вопрос?')

    if message.from_user.id not in context:
        context[message.from_user.id] = []
        msgs_to_delete[message.from_user.id] = []

    context[message.from_user.id].append({'role': 'system',
                                          'content': 'answer in the same language I asked you. Desired response output format: If the user query is asking for a knowledge-based answer or is specifying a data processing or coding task, immediately proceed to the direct answer written as though it was a document. There will be no additional chatty dialog from the AI unless the user is directly conversing with the AI with a chat style. AI should appear to be a data processor, not a chat partner. Keep in mind that you answers will be delivered to me as telegram messages. Answer in detail but try to avoid huge answers.'})


@user.message(Command('clear'))
async def cmd_clear(message: Message):
    context[message.from_user.id] = []
    context[message.from_user.id].append({'role': 'system',
                                          'content': 'answer in the same language I asked you. Desired response output format: If the user query is asking for a knowledge-based answer or is specifying a data processing or coding task, immediately proceed to the direct answer written as though it was a document. There will be no additional chatty dialog from the AI unless the user is directly conversing with the AI with a chat style. AI should appear to be a data processor, not a chat partner. Keep in mind that you answers will be delivered to me as telegram messages. Answer in detail but try to avoid huge answers.'})
    await message.answer('Я понял, начинаем беседу с чистого листа')


@user.message(Chat.busy)
async def answer_that_busy(message: Message):
    msg = await message.answer('Подождите, происходит обработка предыдущего запроса...')
    msgs_to_delete[message.from_user.id].append(msg.message_id)


@user.message(F.text)
async def get_chatgpt_response(message: Message, state: FSMContext):
    await state.set_state(Chat.busy)

    try:
        if message.from_user.id not in context:
            context[message.from_user.id] = []
            msgs_to_delete[message.from_user.id] = []

        msg = await message.answer('Обработка запроса...')
        msgs_to_delete[message.from_user.id].append(msg.message_id)
        await message.bot.send_chat_action(chat_id=message.from_user.id,
                                           action=ChatAction.TYPING)

        context[message.from_user.id].append({'role': 'user',
                                              'content': message.text})
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

        await message.bot.delete_messages(chat_id=message.from_user.id,
                                          message_ids=msgs_to_delete[message.from_user.id])
        await message.answer(response, parse_mode='Markdown')
    except Exception as error:
        logger.error(f'Произошла ошибка, но Вы в этом не виноваты, не переживайте.\n'
                     f'Повторите пожалуйста Ваш запрос. Можете его скорректировать при желании, если Ваша квалификация'
                     f'позволяет разобраться в ошибке:\n{error}')

    await state.clear()


@user.message()
async def get_photo(message: Message):
    msg = await message.answer('К сожалению я могу обработать только текстовый запрос')
    msgs_to_delete[message.from_user.id].append(msg.message_id)