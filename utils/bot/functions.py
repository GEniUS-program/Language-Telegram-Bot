import telebot
from utils.database.data import UserData


ud = UserData()


def send_main_message(bot: telebot.TeleBot, chat_id: int, prev_msg: telebot.types.Message = None):
    markup = telebot.util.quick_markup(
        {
            "Сегодняшнее слово": {"callback_data": "m:0"},
            "Задание на перевод": {"callback_data": "m:1"},
            "Упражнение по грамматике": {"callback_data": "m:2"},
            "Объяснить грамматическое правило": {"callback_data": "m:3"},
            #"Повысить уровень": {"callback_data": "m:4"}, commented as it is not implemented yet
            "Личный кабинет": {"callback_data": "m:5"}
        }
    )
    text = f"Чем могу быть полезен?"
    if prev_msg is not None:
        bot.edit_message_text(
            text, chat_id, prev_msg.id, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)


def send_choose_lang_message(bot: telebot.TeleBot, call: telebot.types.CallbackQuery):
    call_index = call.data.split(':')[-1]
    markup = telebot.util.quick_markup(
        {
            "Английский🇬🇧": {"callback_data": f"cl:en:{call_index}"},
            "Испанский🇪🇸": {"callback_data": f"cl:es:{call_index}"}
        }
    )
    text = f"Выберите язык"

    bot.edit_message_text(
        text, call.message.chat.id, call.message.id, reply_markup=markup)


def process_prompts(lang: str, prompt: str, prompt_type: int, level: str = "C") -> str:
    langs = dict()
    if prompt_type == 1:
        langs = {
            'en': 'английском',
            'es': 'испанском'
        }
    elif prompt_type == 2:
        langs = {
            'en': 'английского',
            'es': 'испанского'
        }
    return prompt.replace(langs['es'], langs[lang]).replace('A', level)
