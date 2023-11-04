import logging
import requests
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler
from telegram.ext import ContextTypes

from difflib import SequenceMatcher


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = '6783111297:AAFg5TGY5fD3j8OQOmupKYaP0imvWo3FhAA'


def process_answer(text: str):
    text = text.replace('<i>', '')
    text = text.replace('</i>', '')
    text = text.replace('<b>', '')
    text = text.replace('</b>', '')
    text = text.replace('/', '')
    return text



def set_or_reset_question_in_context(link: str, context: ContextTypes.DEFAULT_TYPE):
    response = requests.get(link)
    if response.status_code == 200:
        context.user_data['current_question'] = dict(response.json()[0])
        context.user_data['current_question']['answer'] = process_answer(response.json()[0]['answer'])
        print(response.json()[0]['answer'], context.user_data['current_question']['answer'], sep=' - ')
        return 0
    else:
        return None


def show_question(context: ContextTypes.DEFAULT_TYPE):
    if 'clue_level' not in context.user_data.keys():
        context.user_data['clue_level'] = 0
    clue_level = context.user_data['clue_level']
    text = context.user_data['current_question']['question']
    answer = context.user_data['current_question']['answer']
    symbols = "-+—–−,.:;'" + '"'
    print(symbols)
    # show how many letters
    if clue_level == 1:
        text += '\n\nAnswer: '
        for i in range(len(answer)):
            if answer[i] == ' ':
                text += '    '
            else:
                text += answer[i] if answer[i] in symbols else '__ '

    # show first and last letter
    elif clue_level == 2:
        text += '\n\nAnswer: '
        for i in range(len(answer)):
            if answer[i] == ' ':
                text += '    '
            else:
                text += answer[i] if i == 0 or i == len(answer) - 1 or answer[i] in symbols else '__ '

    # show every even letter
    elif clue_level == 3:
        text += '\n\nAnswer: '
        for i in range(len(answer)):
            if answer[i] == ' ':
                text += '    '
            else:
                text += answer[i] if i % 2 == 0 or answer[i] in symbols else '__ '

    # show all letters
    elif clue_level == 4:
        text = 'You lost!\n The answer was: ' + context.user_data['current_question']['answer'] + '\n'
        add_statistics(context, score=-10)
        context.user_data['clue_level'] = 0
        context.user_data['best_streak'] = max(context.user_data['best_streak'], context.user_data['win_streak'])
        context.user_data['win_streak'] = 0

        if set_or_reset_question_in_context('http://jservice.io/api/random', context) is not None:
            text += "The next question is: " + context.user_data['current_question']['question'] + '.'
        else:
            text += 'Something went wrong with API, try to ask for new question with /question'

    return text


def add_statistics(context: ContextTypes.DEFAULT_TYPE, **stats):
    if 'score' not in context.user_data.keys():
        context.user_data['score'] = 0
    if 'win_streak' not in context.user_data.keys():
        context.user_data['win_streak'] = 0
    if 'best_streak' not in context.user_data.keys():
        context.user_data['best_streak'] = 0

    if 'score' in stats.keys():
        context.user_data['score'] += stats['score']
        context.user_data['score'] = max(0, context.user_data['score'])

    if 'win_streak' in stats.keys():
        context.user_data['win_streak'] += stats['win_streak']


def get_statistics(context: ContextTypes.DEFAULT_TYPE):
    if 'score' not in context.user_data.keys():
        context.user_data['score'] = 0
    if 'win_streak' not in context.user_data.keys():
        context.user_data['win_streak'] = 0
    if 'best_streak' not in context.user_data.keys():
        context.user_data['best_streak'] = 0

    text = f"Your score is: {context.user_data['score']}\n"
    text += f"Your current win streak is: {context.user_data['win_streak']}\n"
    text += f"Your best streak is: {context.user_data['best_streak']}"
    return text


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
        print(match, update.message.text, context.user_data['current_question']['answer'])
        if 0.8 <= match < 1.0:
            text = 'You almost guessed it!'

        # You guessed it right
        elif match == 1.0:
            text = 'Yes, you are right!\n'
            add_statistics(context, score=100-context.user_data['clue_level']*10, win_streak=1)
            context.user_data['clue_level'] = 0
            # check that status code is 200
            if set_or_reset_question_in_context('http://jservice.io/api/random', context) is not None:
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
        text = show_question(context)
    else:
        text = 'You should ask for a /question first. /help for more info.'

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['clue_level'] = 0
    if set_or_reset_question_in_context('http://jservice.io/api/random', context) is not None:
        text = "Question: " + context.user_data['current_question']['question']
    else:
        text = 'Some error occurred when tried to get data from api'

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'current_question' in context.user_data.keys():
        text = show_question(context)
    else:
        text = 'You should ask for a /question first. /help for more info.'

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def show_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'current_question' in context.user_data.keys():
        text = context.user_data['current_question']['answer']
    else:
        text = 'You should ask for a /question first. /help for more info.'

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_statistics(context)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def bot_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = '/start - to start this bot\n'
    help_text += '/question - get a question and then try to answer. Every time you use this command the question changes (if you have already asked for one)\n'
    help_text += '/remind - remind current question\n'
    help_text += '/clue - first clue: how many letter; second clue: first and last letter; third clue: all even letters; fourth clue: show word (game over); every clue lowers amount of score you will get, showing full word gives you negative score\n'
    help_text += '/showAnswer - show an answer and close current question, then automatically generate a new one\n'
    help_text += '/showStats - show your statistic'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command. /help for more info.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    question_handler = CommandHandler('question', question)
    application.add_handler(question_handler)

    showAnswer_handler = CommandHandler('showAnswer', show_answer)
    application.add_handler(showAnswer_handler)

    show_statistics_handler = CommandHandler('showStats', show_statistics)
    application.add_handler(show_statistics_handler)

    remind_handler = CommandHandler('remind', remind)
    application.add_handler(remind_handler)

    clues_handler = CommandHandler('clue', clues)
    application.add_handler(clues_handler)

    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), match_answer)
    application.add_handler(message_handler)

    help_handler = CommandHandler('help', bot_help)
    application.add_handler(help_handler)

    # Other triggers (should be the last one in code)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling()
