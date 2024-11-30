import telebot
from utils.bot.handlers import *
from utils.bot.functions import process_prompts
from utils.bot.level_test import handle_start, handle_answer

API_TOKEN = '<token>'
bot = telebot.TeleBot(API_TOKEN, threaded=False)


@bot.message_handler(commands=['start'])
def start_command(message):
    start_handler(message, bot)


@bot.callback_query_handler(lambda call: call.data.split(':')[0] in 'svl')
def new_user(call):
    call_type = call.data.split(':')[0]
    if call_type == 's':
        new_user_handler(call, bot)
    elif call_type == 'l':
        select_language(call, bot)
    elif call_type == 'v':
        select_level(call, bot)


@bot.callback_query_handler(lambda call: call.data.split(':')[0] in ['m', 'cl'])
def main_actions(call):
    if call.data.split(':')[0] == 'cl':
        main_menu_gateway(call, bot, lang=call.data.split(':')[1])
    else:
        main_menu_gateway(call, bot)


@bot.callback_query_handler(lambda call: call.data == 'mm')
def show_main_message(call):
    send_main_message(bot, call.message.chat.id, call.message)


@bot.callback_query_handler(lambda call: call.data == 'r')
def redact_profile(call):
    redact_profile_handler(call, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith(('correct_', 'wrong_')))
def handle_grammar_answer(call: telebot.types.CallbackQuery):

    parts = call.data.split('_')
    answer_type = parts[0]
    lang = parts[-1]

    if answer_type == 'correct':
        bot.answer_callback_query(call.id, "Правильно! 👍")
        # Recreate call with current language
        fake_call = telebot.types.CallbackQuery(
            id=call.id,
            from_user=call.from_user,
            message=call.message,
            chat_instance=call.chat_instance,
            data=None,
            json_string=call.json
        )
        grammar_exrc(bot, fake_call, lang)
    else:
        bot.answer_callback_query(call.id, "Неверно. Попробуйте снова. 👎")


@bot.callback_query_handler(func=lambda call: call.data.startswith('input:'))
def handle_grammar_input(call):
    data = call.data.split(':')
    with codecs.open("./data/prompts.txt", "r", "utf-8") as prompt_file:
        prompts = prompt_file.readlines()
    if data[1] == '0':
        send_input_request(bot, call, process_prompts(
            data[-1], prompts[int(data[-2])], 2))
    else:
        process_rule_input(bot=bot, call=call, prompt=process_prompts(
            data[-1], prompts[int(data[-2])], 2))

@bot.callback_query_handler(func=lambda call: call.data.startswith('answer_'))
def handle_test_answer(call):
    handle_answer(call, bot, *call.data.split('_')[1:3])

if __name__ == '__main__':
    print("Bot is polling...")
    bot.polling(none_stop=True)
