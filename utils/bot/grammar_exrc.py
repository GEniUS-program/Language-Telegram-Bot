import telebot
import json
import codecs
import random
from utils.database.data import UserData


ud = UserData()


# Global dictionary to track user states
user_exercise_state = {}


def grammar_exrc(bot: telebot.TeleBot, call: telebot.types.CallbackQuery, lang: str):
    user_id = call.from_user.id

    # Reset or initialize user state
    if user_id not in user_exercise_state or user_exercise_state[user_id]['language'] != lang:
        user_exercise_state[user_id] = {
            'test_type': (random.randint(0, 3) if lang == 'en' else random.randint(0, 1)),
            'processed_expressions': [],
            'current_grammar': None,
            'language': lang
        }

    # Get current user state
    state = user_exercise_state[user_id]

    # Load grammar data
    try:
        with codecs.open("./data/grammar.json", "r", encoding="utf-8") as file:
            grammar_data = json.load(file)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Ошибка загрузки данных: {e}")
        return

    # Determine exercise type
    test = state['test_type']
    task = "Что нужно поставить на месте _?"

    # Get current grammar
    eng_grammar = grammar_data[lang][test]

    # Select unprocessed expressions
    available_expressions = [
        expr for expr in eng_grammar.items()
        if expr[0] not in state['processed_expressions']
    ]

    # Reset if all expressions processed
    if not available_expressions:
        state['processed_expressions'] = []
        available_expressions = list(eng_grammar.items())

    # Select random expression
    expression, right_answer = random.choice(available_expressions)

    # Generate answer options
    all_answers = list(eng_grammar.values())
    wrong_answers = [ans for ans in all_answers if ans != right_answer]

    random.shuffle(wrong_answers)
    selected_wrong_answers = wrong_answers[:3]

    # Create answer options
    answer_options = [right_answer] + selected_wrong_answers
    random.shuffle(answer_options)

    # Create markup
    markup_dict = {}
    for answer in answer_options:
        # Use unique callback data for each question
        unique_id = str(hash(expression + answer))
        if answer == right_answer:
            callback_data = f"correct_{test}_{unique_id}_{lang}"
        else:
            callback_data = f"wrong_{test}_{unique_id}_{lang}"

        markup_dict[answer] = {'callback_data': callback_data}

    # Add main menu button
    markup_dict["Выйти в главное меню⬅️"] = {'callback_data': "mm"}
    markup = telebot.util.quick_markup(markup_dict, row_width=2)

    # Send message
    sent_message = bot.send_message(
        call.message.chat.id,
        f"Задание: {task}\n\n{expression}",
        reply_markup=markup
    )

    # Update state
    state['processed_expressions'].append(expression)
    state['current_grammar'] = (expression, right_answer)
    state['last_message_id'] = sent_message.message_id
