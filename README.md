A telegram bot for learning english and spanish.

**Features**
  1. "Сегодняшнее слово" (Today's word) - An option to show 5 random words in the selected language, their translation, transcription and meaning. Words are generated by YaGPT;
  2. "Задание на перевод" (Translation exercize) - An option to send the user a sentence to translate into the selected language.
   YaGPT checks if the translation is correct and explains any mistakes the user might've made;
  3. "Упражнение по грамматике" (Grammar exercize) - Bot sends the user a message with some task (according to the selected languages), upon answering it the user gets an alert with the result. 
   Tasks are selected from grammar.json file;
  4. "Объяснить грамматическое правило" (Explain a grammatical rule) - User gets a message with two options: Enter manually or Generate.
   If the first option is chosen, the user needs to send a message with rule description, if the second option - YaGPT generates and explains the rule;
  6. "Личный кабинет" (Profile) - Shows user's selected languages and level.

**Quality of life features**
  1. To avoid trashing of the chat, the bot edits or deletes previous messages;
  2. A log file to log and debug bot activity;
  3. Storing of insensitive information. All user data is stored on the server, the data is not sensitive.