from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, \
    filters, ConversationHandler

from credentials import ChatGPT_TOKEN, BOT_TOKEN
from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler, load_prompt, send_text_buttons)

from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(action="ignore", message=r"CallbackQueryHandler", category=PTBUserWarning)

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

async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'talk'
    text = load_message('talk')
    await send_image(update, context, 'talk')
    await send_text_buttons(update, context, text, buttons={
        'talk_cobain': 'Курт Кобейн',
        'talk_queen': 'Елизавета II',
        'talk_tolkien': 'Джон Толкиен',
        'talk_nietzsche': 'Фридрих Ницше',
        'talk_hawking': 'Стивен Хокинг',
    })

async def talk_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = update.callback_query.data
    chat_gpt.set_prompt(load_prompt(data))
    great = await chat_gpt.add_message('Поздоровайся со мной')
    await send_image(update, context, data)
    await send_text(update, context, great)

async def talk_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('mode') in ('main', 'random'):
        await start(update, context)
    elif context.user_data.get('mode') in ('gpt', 'talk'):
        await gpt_dialog(update, context)


chat_gpt = ChatGptService(ChatGPT_TOKEN)
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('talk', talk))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpt))

app.add_handler(CallbackQueryHandler(talk_buttons, pattern='^talk_.*'))
app.add_handler(CallbackQueryHandler(random_buttons, pattern='random_more'))
app.add_handler(CallbackQueryHandler(stop, pattern='stop'))


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'quiz'
    context.user_data['score'] = 0
    chat_gpt.set_prompt(load_prompt('quiz'))
    await send_text_buttons(update, context, 'Выберите тему', buttons={
        'quiz_prog': 'Программирование',
        'quiz_math': 'Математика',
    })
    return THEME

async def quiz_theme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    question = await chat_gpt.add_message(update.callback_query.data)
    await send_text(update, context, question)
    return ANSWER

async def quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    if answer == 'Правильно!':
        context.user_data['score'] = context.user_data.get('score', 0) + 1
    await send_text_buttons(update, context, answer + '\n\nВаш счет: ' + str(
        context.user_data.get('score')), buttons={
        'quiz_more': 'Следующий вопрос',
        'quiz_change': 'Выбрать другую тему',
        'stop': 'Завершить'
    })

    return CHOOSE_AFTER

async def quiz_choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == 'quiz_more':
        return await quiz_theme(update, context)
    else:
        await update.callback_query.answer()
        return await quiz(update, context)

THEME, CHOOSE, ANSWER, CHOOSE_AFTER = range(4)
app.add_handler(ConversationHandler(
    entry_points=[CommandHandler('quiz', quiz)],
    states={
        THEME: [CallbackQueryHandler(quiz_theme, pattern='^quiz_.*')],
        CHOOSE: [
            CallbackQueryHandler(quiz_theme, pattern='quiz_more'),
            CallbackQueryHandler(quiz, 'quiz_change')
        ],
        ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_answer)],
        CHOOSE_AFTER: [
            CallbackQueryHandler(quiz_choose, pattern='^quiz_*')
        ]
    },
    fallbacks=[CommandHandler('stop', stop)]
))

app.add_handler(CallbackQueryHandler(default_callback_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
app.run_polling()

