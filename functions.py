import requests
from telegram.ext import ContextTypes


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
        print(context.user_data['current_question']['answer'])
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
                text += answer[i] if i % 2 == 0 or answer[i] in symbols or i == 0 or i == len(answer) - 1 else '__ '

    # show all letters
    elif clue_level == 4:
        text = 'You lost!\nThe answer was: ' + context.user_data['current_question']['answer'] + '\n'
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

    context.user_data['best_streak'] = max(context.user_data['win_streak'], context.user_data['best_streak'])


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
