import logging
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler
from telegram.ext import ContextTypes, InlineQueryHandler, CallbackContext


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = '6783111297:AAFg5TGY5fD3j8OQOmupKYaP0imvWo3FhAA'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!\n/help for more info")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(context.args)
    if len(context.args) == 0:
        text_caps = "You forgot to enter your text"
    else:
        text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


async def bot_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "I'm a simple bot i just repeat what you say, later I will grow into something bigger, I guess...\n\n"
    help_text += '/start - to start this bot\n'
    help_text += '/caps "arg" - to uppercase your argument\n'
    help_text += '/help - list of commands\n'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    caps_handler = CommandHandler('caps', caps)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    help_handler = CommandHandler('help', bot_help)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(caps_handler)
    application.add_handler(help_handler)

    # Other triggers (should be the last one in code)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling()
