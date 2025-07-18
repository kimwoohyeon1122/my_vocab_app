import requests
from googletrans import Translator
import openai

def get_suggestions(word):
    url = f"https://api.datamuse.com/sug?s={word}"
    try:
        r = requests.get(url)
        return [w['word'] for w in r.json()][:5]
    except:
        return []

def get_meaning_and_pos(word):
    try:
        translator = Translator()
        meaning = translator.translate(word, dest='ko').text
        # 간이 품사 추정
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        r = requests.get(url)
        data = r.json()
        pos = data[0]["meanings"][0]["partOfSpeech"] if isinstance(data, list) else "n"
    except:
        meaning = ""
        pos = "n"
    return meaning, pos

def get_example_sentence(word, openai_api_key):
    if not openai_api_key:
        return "OpenAI API 키가 필요합니다."
    openai.api_key = openai_api_key
    prompt = f"Give me one short English sentence using the word '{word}'. Also provide a Korean translation."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user", "content": prompt}],
            max_tokens=100
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"예문 생성 실패: {e}"
