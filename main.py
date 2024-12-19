import datetime

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler

from credentials import BOT_TOKEN
from util import send_text, send_image


# Функция для обработки сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    # context.user_data [''] - хранить данные
    print(f'{text}, - {update.effective_user.full_name} | {datetime.datetime.now()}')
    await context.bot.send_message(update.effective_chat.id, f'Вы написали: {text}')


async def default_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'gpt')
    # markup = ReplyKeyboardMarkup(
    #     [
    #         ['1','2','3',],
    #         ['4','5','6',],
    #         ['7','8','9',],
    #     ], one_time_keyboard=True
    # )
    # Создаем инлайн-кнопки
    markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('Один', callback_data='start_one')],
            [InlineKeyboardButton('Два', callback_data='start_two')],
            [InlineKeyboardButton('Три', callback_data='start_three')],
        ]
    )
    await  context.bot.send_message(update.effective_chat.id, 'Привет и добро пожаловать 😎', reply_markup=markup)

async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = update.callback_query.data
    print(data)

token = BOT_TOKEN
app = Application.builder().token(token).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.add_handler(CommandHandler('start', default_command_handler))
app.add_handler(CallbackQueryHandler(cb_handler, '^start_.*'))
app.run_polling()