#<-- the start of the script to test users level UNFINISHED -->
import telebot
from utils.database.data import UserData
import json
from time import sleep

data = json.load(open('./data/knowledge_level_test.json', 'r', encoding='utf-8'))

# Store user scores in a dictionary
user_scores = {}
ud = UserData()
path = []

def handle_start(call, bot, lang, level):
    for question in data[lang][level]:
        query = ''
        for key, value in question.items():
            path.append()
            markup = telebot.util.quick_markup({f'{key}.) {value}': {"callback_data": f"answer_{key}_{lang}_{level}"} for key, value in value[1].items()})
            bot.send_message(call.message.chat.id, f"{key}\n\t{value[0] if value[0] else ''}\n", reply_markup=markup)
            sleep(0.3)
# Function to ask a question
def ask_question(user_id, bot, lang, level):
    
    # Select a random question from the predefined JSON data
    question_data = data[lang][level]
    
    for question, content in question_data.items():
        user_scores[user_id]['current_question'] = content
        question_text = content[0]
        options = content[1]
        
        # Create options for the user
        keyboard = telebot.types.InlineKeyboardMarkup()
        for key, value in options.items():
            keyboard.add(telebot.types.InlineKeyboardButton(value, callback_data=f"answer_{key}_{lang}_{level}"))
        
        bot.send_message(user_id, question_text, reply_markup=keyboard)
        # Remove this line if you want to ask all questions sequentially

# Handle user answer

def handle_answer(call, bot, lang, level):
    user_id = call.message.chat.id
    user_score = user_scores[user_id]
    question = user_score['current_question']
    
    answer_key = call.data.split('_')[1]
    correct_answer = question[2]
    
    if answer_key == correct_answer:
        user_score['score'] += 1
        bot.send_message(user_id, "Correct! 🎉")
    else:
        bot.send_message(user_id, "Wrong answer. 😢")
    
    # Ask the next question
    ask_question(user_id, bot, lang, level)
