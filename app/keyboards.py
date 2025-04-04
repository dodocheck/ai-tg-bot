from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

inline_kb_aimodel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='DeepSeek V3-0324',
                          callback_data='deepseek/deepseek-chat-v3-0324:free')],
    [InlineKeyboardButton(text='Gemini 2.5 Pro',
                          callback_data='google/gemini-2.5-pro-exp-03-25:free')],
    [InlineKeyboardButton(text='Qwen 2.5 Coder',
                          callback_data='qwen/qwen-2.5-coder-32b-instruct:free')],
    [InlineKeyboardButton(text='Quasar Alpha',
                          callback_data='openrouter/quasar-alpha')],
])
