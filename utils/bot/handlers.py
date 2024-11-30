import telebot
from utils.database.data import UserData
from utils.gpt import gpt_prompt
from utils.bot.functions import *
from utils.bot.grammar_exrc import grammar_exrc
from utils.bot.level_test import handle_start
import datetime as dt
import codecs
import json

ud = UserData()
log = ud.log

cab_markup = telebot.util.quick_markup(
    {
        "Английский🇬🇧": {"callback_data": "l:en"},
        "Испанский🇪🇸": {"callback_data": "l:es"}
    }
)
exit_to_main_markup = telebot.util.quick_markup(
    {
        "Выйти в главное меню⬅️": {"callback_data": "mm"}
    }
)

with codecs.open("./data/prompts.txt", "r", "utf-8") as prompt_file:
    prompts_global = prompt_file.readlines()


def start_handler(message: telebot.types.Message, bot: telebot.TeleBot):
    markup = telebot.util.quick_markup(
        {
            "Да!": {"callback_data": "s:"}
        }
    )
    if ud.is_chat(message.chat.id):
        log.write("User chat found\n")
        send_main_message(bot, message.chat.id)
    else:
        log.write("User chat not found\n")
        log.write("Creating new entry to database\n")
        bot.send_message(message.chat.id, 'Привет, искатель знаний!📚 \
                            \nЯ - бот для изучения языков. Здесь ты можешь тренировать свой Английский, Испанский.🇬🇧🇪🇸 \
                            \nГотов приступить к занятиям?🔋🎉', reply_markup=markup)


def new_user_handler(call, bot):
    log.write("New user handler triggered\n")
    ud.add(call.message.chat.id, languages=[""], level=[""])
    markup = telebot.util.quick_markup(
        {
            "Английский🇬🇧": {"callback_data": "l:en"},
            "Испанский🇪🇸": {"callback_data": "l:es"}
        }
    )
    bot.edit_message_text("Какой язык Вы хотите изучить?",
                          call.message.chat.id, call.message.id, reply_markup=markup)


def select_language(call: telebot.types.CallbackQuery, bot: telebot.TeleBot):
    lan = call.data.split(':')[1]
    log.write("First language selected: " + lan + "\n")
    ud.update(call.message.chat.id, languages=[lan])
    markup = telebot.util.quick_markup(
        {
            "Начальный(A1, A2)": {"callback_data": "v:A"},
            "Средний(B1, B2)": {"callback_data": "v:B"},
            "Продвинутый(C1, C2)": {"callback_data": "v:C"}
        }
    )
    bot.edit_message_text("Какой у вас уровень знания языка?",
                          call.message.chat.id, call.message.id, reply_markup=markup)


def select_level(call: telebot.types.CallbackQuery, bot: telebot.TeleBot):
    lvl = call.data.split(':')[1]
    log.write("Level selected: " + lvl + "\n")
    ud.update(call.message.chat.id, level=[lvl])


def main_menu_gateway(call: telebot.types.CallbackQuery, bot: telebot.TeleBot, lang: str = None):
    ud.open_()
    ud.log.write("Main menu gateway triggered\n")
    languages = list()
    langs = {"en": "английский🇬🇧", "es": "испанский🇪🇸"}
    lvls = {"A": "начальный(A)", "B": "средний(B)", "C": "продвинутый(C)"}
    if lang is None:
        ud.log.write("No lang argument, requesting data from database\n")
        languages = list(
            ud.dict_("languages", chat_id=call.message.chat.id).values())[0]
        ud.open_()
    else:
        languages = [lang]
        ud.log.write("Lang argument found, using it\n")

    # not language-dependent action (profile)
    if int(call.data.split(':')[-1]) == 5:
        markup = telebot.util.quick_markup(
            {
                "Редактировать": {"callback_data": "r"},
                "Выйти в главное меню⬅️": {"callback_data": "mm"}
            }
        )
        text = "Ваш личный кабинет"

        # format text

        data = ud.dict_("languages", "level", chat_id=call.message.chat.id)[
            call.message.chat.id]
        ud.open_()
        text += "\nЯзыки: "
        text += '\n - ' + '\n - '.join([f"{langs[data['languages'][i]]} уровень {lvls[data['level'][i]]}" for i in range(
            len(data["languages"]))])

        # Личный кабинет
        bot.edit_message_text(
            text, call.message.chat.id, call.message.id, reply_markup=markup)

    else:
        if len(languages) == 1:
            ud.log.write("Language selected: " + languages[0] + "\n")
            language = languages[0]
            match int(call.data.split(':')[-1]):
                case 0:
                    # Сегодняшнее слово
                    ud.log.write("Getting today's words\n")
                    today = dt.date.today().strftime("%Y-%m-%d")
                    with codecs.open("./data/bot_data.json", "r", "utf-8") as f:
                        f = json.loads(f.read())
                        if today == f["daily-words"][language]["words_last_update"]:
                            words = f["daily-words"][language]["words"]
                            ud.log.write(f"Using stored words: {words}\n")

                        else:
                            ud.log.write("Generating new words\n")
                            prompt = prompts_global[0]
                            levels = ud.dict_("level", chat_id=call.message.chat.id)[
                                call.message.chat.id]
                            ud.open_()
                            if language == "en":
                                lvl = levels[0]
                            else:
                                lvl = levels[1]
                            prompt = process_prompts(
                                language, prompt, 1, lvl)
                            ud.log.write(f"Generated prompt: {prompt}\n")
                            bot.edit_message_text(
                                "Запрос обрабатывается, подождите⏳", call.message.chat.id, call.message.id
                            )
                            words = gpt_prompt(prompt)

                            ud.log.write(f"Generated words: {words}\n")
                            f["daily-words"][language]["words"] = words
                            f["daily-words"][language]["words_last_update"] = today
                        bot.edit_message_text(
                            words, call.message.chat.id, call.message.id, reply_markup=exit_to_main_markup)
                    with codecs.open("./data/bot_data.json", "w", "utf-8") as json_file:
                        json_file.write(json.dumps(f, indent=4))

                case 1:
                    prompts = prompts_global[1:3]

                    levels = ud.dict_("level", chat_id=call.message.chat.id)[
                        call.message.chat.id]
                    ud.open_()

                    if language == "en":
                        lvl = levels[0]
                    else:
                        lvl = levels[1]

                    prompt_gen_og = process_prompts(
                        language, prompts[0], 1, lvl
                    )
                    prompt_gen_trans = process_prompts(
                        language, prompts[1], 1, lvl
                    )
                    bot.edit_message_text(
                        "Запрос обрабатывается, подождите⏳", call.message.chat.id, call.message.id
                    )
                    text = gpt_prompt(prompt_gen_og)
                    text_og = ''
                    tmp = 1
                    for symbol in text:
                        if symbol == "«":
                            tmp = 0
                            continue
                        if symbol == "»":
                            break
                        if not tmp:
                            text_og += symbol
                    msg = bot.edit_message_text(
                        "Задание на перевод. Переведите:\n\t" +
                        text_og, call.message.chat.id, call.message.id
                    )
                    bot.register_next_step_handler(
                        msg, compared_translation, text_og, prompt_gen_trans, call, bot
                    )
                    # Задание на перевод
                case 2:
                    ud.open_()
                    ud.log.write("Starting grammatic exercise\n")
                    grammar_exrc(bot, call, language)
                case 3:
                    ud.open_()
                    ud.log.write("Get grammatical rule\n")

                    markup = telebot.util.quick_markup(
                        {
                            "Ввести в ручную": {"callback_data": f"input:0:4:{language}"},
                            "Сгенерировать": {"callback_data": f"input:1:3:{language}"},
                            "Выйти в главное меню⬅️": {"callback_data": "mm"}
                        }
                    )
                    text = "Выберите способ получения правила\n"
                    bot.edit_message_text(
                        text, call.message.chat.id, call.message.id, reply_markup=markup)

                case 4: # commented as it is not implemented yet
                    pass
                    #levels = ud.dict_("level", chat_id=call.message.chat.id)[
                    #    call.message.chat.id]
                    #if language == "en":
                    #    handle_start(call, bot, language, levels[0])
                    #else:
                    #    handle_start(call, bot, language, levels[1])

        else:
            ud.log.write(
                "Multiple languages detected, sending choose language message\n")
            send_choose_lang_message(bot, call)

    ud.log.close()


def redact_profile_handler(call: telebot.types.CallbackQuery, bot: telebot.TeleBot):
    ud.open_()
    ud.log.write("Redact profile handler triggered\n")
    msg = bot.edit_message_text("Чтобы настроить свой профиль, напишите: '<язык>, <уровень>', где <язык> замените на желаемый язык(en - английский, es - испанский), <уровень> - на желаемый уровень знания языка(A, B, C). Уровни знания языка A, B, C соответствуют уровням владения языка на уровне начинального, среднего и продвинутого. Если у вас есть несколько языков, напишите их через ';' Например: 'en, A; es, B'. Языки перечислять в следующем порядке: 1. Английский, 2. Испанский.", call.message.chat.id, call.message.id, reply_markup=exit_to_main_markup)
    bot.register_next_step_handler(msg, save_profile, bot, call)
    ud.log.close()


def save_profile(message: telebot.types.Message, bot: telebot.TeleBot, call: telebot.types.CallbackQuery):
    ud.open_()
    ud.log.write("Save profile handler triggered\n")
    ud.update(message.chat.id, languages=[m.split(",")[0] for m in message.text.split(
        ";")], level=[m.split(", ")[1] for m in message.text.split("; ")])
    bot.edit_message_text("Профиль успешно сохранен",
                          message.chat.id, call.message.id, reply_markup=exit_to_main_markup)
    ud.log.close()


def compared_translation(message: telebot.types.Message, text_og: str, prompt_gen_trans: str, call: telebot.types.CallbackQuery, bot: telebot.TeleBot):
    ud.open_()
    ud.log.write("Compared translation handler triggered\n")
    bot.edit_message_text(
        "Запрос обрабатывается, подождите⏳", call.message.chat.id, call.message.id
    )
    text_trans = gpt_prompt(
        prompt_gen_trans + "Оригинальный текст: " + text_og + "Перевод: " + message.text)
    bot.edit_message_text("Оригинальный текст:\n\t" + text_og + "\nПеревод:\n\t" + message.text + "\nСравнение:\n\t" + text_trans, message.chat.id,
                          call.message.id, reply_markup=exit_to_main_markup)
    bot.delete_message(message.chat.id, message.id)
    ud.log.close()


def send_input_request(bot: telebot.TeleBot, call: telebot.types.CallbackQuery, prompt: str):
    msg = bot.edit_message_text(
        "Введите правило", call.message.chat.id, call.message.id, reply_markup=exit_to_main_markup
    )
    bot.register_next_step_handler(msg, process_rule_input, bot, call, prompt)


def process_rule_input(message: telebot.types.Message = None, bot: telebot.TeleBot = None, call: telebot.types.CallbackQuery = None, prompt: str = ''):
    ud.open_()

    bot.edit_message_text(
        "Запрос обрабатывается, подождите⏳", call.message.chat.id, call.message.id
    )

    if message:
        text = gpt_prompt(prompt + "Правило: " + message.text)
        ud.log.write(f"Got rule input: {message.text}\n")
    else:
        ud.log.write("No rule input, generating rule\n")
        text = gpt_prompt(prompt)

    bot.edit_message_text(
        text, call.message.chat.id, call.message.id, reply_markup=exit_to_main_markup
    )
    ud.log.close()
