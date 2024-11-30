import requests
from utils.database.data import UserData


ud = UserData()


def gpt_prompt(prompt: str) -> requests.Response:
    """
    Make a request to the Yandex AI API to generate a response to the given prompt.

    Parameters:
        prompt (str): The user's prompt to generate a response to.

    Returns:
        requests.Response: The response from the Yandex AI API.
    """
    ud.open_()
    ud.log.write("GPT prompt: " + prompt + "\n")
    prompt = {
        # идентификатор каталога сюда
        "modelUri": "gpt://<catalog-id>/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.3,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты профессиональный лингвист с обширными знаниями русского, испанского и английского языков. Твоя задача - помогать начинающим лингвистам. Ответы даёшь короткие, систематизированные, но информативные."
            },
            {
                "role": "user",
                "text": prompt
            }
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key <API-key>"  # сюда API-ключ
    }

    response = requests.post(url, headers=headers,  # Отправка запроса к API
                             json=prompt)
    ud.open_()
    ud.log.write('GPT response:' + response.text + '\n')
    return process_gpt_response(response)


def process_gpt_response(response: requests.Response) -> str | None:
    """
    Process the response from the GPT API and extract the relevant text.

    Parameters:
        response (requests.Response): The response object from the GPT API request.

    Returns:
        str: The extracted text from the response if successful, otherwise None.
    """

    try:
        result = response.text.replace('*', '')
        result = result.replace('\\n', '\n')
        start = result.index('"text":') + 8
        end = result.index('"}') + 1
    except Exception as e:
        ud.log.write(str(e) + '\n')  # Логирование ошибок
        result = None
    else:
        # Обрезает лишнюю информацию в начале и в конце
        ud.log.write('GPT request success\n')
        result = result[start:end]  # Извлечение текста из ответа
    finally:
        ud.log.close()
        return result.rstrip('"')
