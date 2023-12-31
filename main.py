import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler
from telegram.ext import ContextTypes

from difflib import SequenceMatcher
import functions


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = '6783111297:AAFg5TGY5fD3j8OQOmupKYaP0imvWo3FhAA'
ADMINS = ['imMonkaS']


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I'm a Trivia Questions bot, ask me to give you a question with /question command and then try to answer.\nType /help for more info."
    )


async def match_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # if user asked for a question
    if update.message is None:
        return
    elif 'current_question' in context.user_data.keys():
        match = SequenceMatcher(None, update.message.text.lower(), context.user_data['current_question']['answer'].lower()).ratio()
        if 0.8 <= match < 1.0:
            text = 'You almost guessed it!'

        # You guessed it right
        elif match == 1.0:
            text = 'Yes, you are right!\n'
            functions.add_statistics(context, score=100-context.user_data['clue_level']*10, win_streak=1)
            context.user_data['clue_level'] = 0
            # check that status code is 200
            if functions.set_or_reset_question_in_context('http://jservice.io/api/random', context) is not None:
                text += "The next question is: " + context.user_data['current_question']['question'] + '.'
            else:
                text += 'Something went wrong with API, try to ask for new question with /question'
        else:
            text = 'Nope, that is not the correct answer.'
    else:
        text = 'You should ask for a /question first. /help for more info.'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def clues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'clue_level' not in context.user_data.keys():
        context.user_data['clue_level'] = 0

    if 'current_question' in context.user_data.keys():
        context.user_data['clue_level'] += 1
        text = functions.show_question(context)
    else:
        text = 'You should ask for a /question first. /help for more info.'

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['clue_level'] = 0
    if functions.set_or_reset_question_in_context('http://jservice.io/api/random', context) is not None:
        text = "Question: " + context.user_data['current_question']['question']
        functions.add_statistics(context, score=-10)
    else:
        text = 'Some error occurred when tried to get data from api'

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'current_question' in context.user_data.keys():
        text = functions.show_question(context)
    else:
        text = 'You should ask for a /question first. /help for more info.'

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def show_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.username in ADMINS:
        if 'current_question' in context.user_data.keys():
            text = context.user_data['current_question']['answer']
        else:
            text = 'You should ask for a /question first. /help for more info.'
    else:
        text = 'You have to be creator, to use this function'

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = functions.get_statistics(context)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def bot_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = '/start - to start this bot\n'
    help_text += '/question - get a question and then try to answer. Every time you use this command the question changes (if you have already asked for one) and your score drops by 10\n'
    help_text += '/remind - remind current question\n'
    help_text += '/clue - first clue: how many letter; second clue: first and last letter; third clue: all even letters; fourth clue: show word (game over); every clue lowers amount of score you will get, showing full word gives you negative score\n'
    help_text += '/showStats - show your statistic\n'
    if update.message.from_user.username in ADMINS:
        help_text += '/showAnswer - show an answer and close current question, then automatically generate a new one'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command. /help for more info.")


def add_handlers(app):
    start_handler = CommandHandler('start', start)
    app.add_handler(start_handler)

    question_handler = CommandHandler('question', question)
    app.add_handler(question_handler)

    show_answer_handler = CommandHandler('showAnswer', show_answer)
    app.add_handler(show_answer_handler)

    show_statistics_handler = CommandHandler('showStats', show_statistics)
    app.add_handler(show_statistics_handler)

    remind_handler = CommandHandler('remind', remind)
    app.add_handler(remind_handler)

    clues_handler = CommandHandler('clue', clues)
    app.add_handler(clues_handler)

    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), match_answer)
    app.add_handler(message_handler)

    help_handler = CommandHandler('help', bot_help)
    app.add_handler(help_handler)

    # Other triggers (should be the last one in code)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    app.add_handler(unknown_handler)


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    add_handlers(application)

    application.run_polling()
