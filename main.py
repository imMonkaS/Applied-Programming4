import logging
import requests
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler
from telegram.ext import ContextTypes, InlineQueryHandler, CallbackContext


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = '6783111297:AAFg5TGY5fD3j8OQOmupKYaP0imvWo3FhAA'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I'm a Trivia Questions bot, ask me to give you a question with /question command and then try to answer.\nType /help for more info."
    )


async def match_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'current_question' in context.user_data.keys():
        if update.message.text == context.user_data['current_question']['answer']:
            text = 'Yes, you are right!\n'
            response = requests.get('http://jservice.io/api/random')
            if response.status_code == 200:
                context.user_data['current_question'] = dict(response.json()[0])
                text += "The next question is: " + context.user_data['current_question']['question'] + '.'
        else:
            text = 'Nope, that is not the correct answer.'
    else:
        text = 'You should ask for a question first. /help for more info.'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = requests.get('http://jservice.io/api/random')
    if response.status_code == 200:
        context.user_data['current_question'] = dict(response.json()[0])
        text = "Question: " + context.user_data['current_question']['question']
    else:
        text = 'Some error occurred when tried to get data from api'

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'current_question' in context.user_data.keys():
        text = context.user_data['current_question']['question']
    else:
        text = 'You should ask for a question first. /help for more info.'

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def showAnswer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'current_question' in context.user_data.keys():
        text = context.user_data['current_question']['answer']
    else:
        text = 'You should ask for a question first. /help for more info.'

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


# async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     print(context.args)
#     if len(context.args) == 0:
#         text_caps = "You forgot to enter your text"
#     else:
#         text_caps = ' '.join(context.args).upper()
#     await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


async def bot_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = '/start - to start this bot\n'
    help_text += '/question - get a question and then try to answer. Every time you use this command the question changes (if you have already asked for one)\n'
    help_text += '/remind - remind current question\n'
    help_text += '/showAnswer - show an answer and close current question, then automatically generate a new one'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command. /help for more info.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    # caps_handler = CommandHandler('caps', caps)
    # test_handler = CommandHandler('test', test)
    question_handler = CommandHandler('question', question)
    showAnswer_handler = CommandHandler('showAnswer', showAnswer)
    remind_handler = CommandHandler('remind', remind)
    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), match_answer)
    help_handler = CommandHandler('help', bot_help)

    application.add_handler(start_handler)
    # application.add_handler(echo_handler)
    application.add_handler(message_handler)
    # application.add_handler(test_handler)
    application.add_handler(question_handler)
    application.add_handler(showAnswer_handler)
    application.add_handler(remind_handler)
    # application.add_handler(caps_handler)
    application.add_handler(help_handler)

    # Other triggers (should be the last one in code)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling()
