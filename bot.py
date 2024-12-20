from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters

from credentials import ChatGPT_TOKEN, BOT_TOKEN
from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler, load_prompt, send_text_buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'main'
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'random': 'Узнать случайный интересный факт 🤠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓'
    })

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await send_text(update, context, 'До свидания')
    await start(update, context)

async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'random'
    answer = await chat_gpt.send_question(load_prompt('random'), '')
    await send_text_buttons(update, context, answer, buttons={
        'random_more': 'Показать еще',
        'stop': 'Завершить'
    })

async def random_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    if context.user_data.get('mode') != 'random':
        return
    await random(update, context)

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'gpt'
    chat_gpt.set_prompt(load_prompt('gpt'))
    text = load_message('gpt')
    await send_image(update, context, 'gpt')
    await send_text(update, context, text)

async def gpt_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.message.text
    message = await send_text(update, context, 'Думаю над ответом...')
    answer = await chat_gpt.add_message(request)
    await message.delete()
    await send_text_buttons(update, context,
                            answer,
                            buttons={'stop': 'Завершить'})

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('mode') in ('main', 'random'):
        await start(update, context)
    elif context.user_data.get('mode') == 'gpt':
        await gpt_dialog(update, context)

chat_gpt = ChatGptService(ChatGPT_TOKEN)
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CallbackQueryHandler(random_buttons, pattern='random_more'))
app.add_handler(CallbackQueryHandler(stop, pattern='stop'))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()

