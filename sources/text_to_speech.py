import os
import re
import platform
import pyttsx3
from typing import List

if __name__ == "__main__":
    from utility import pretty_print, animate_thinking
else:
    from sources.utility import pretty_print, animate_thinking

class Speech():
    """
    Speech is a class for generating speech from text using pyttsx3.
    """
    def __init__(self, enable: bool = True, language: str = "en", voice_idx: int = 0) -> None:
        self.enable = enable
        self.language = language
        self.voice_idx = voice_idx
        self.engine = pyttsx3.init() if enable else None
        self.voice_folder = ".voices"
        self.create_voice_folder(self.voice_folder)
        if self.engine:
            self.set_voice(language, voice_idx)
            self.engine.setProperty('rate', 180)  # Скорость речи
            self.engine.setProperty('volume', 1.0)  # Громкость

    def create_voice_folder(self, path: str = ".voices") -> None:
        if not os.path.exists(path):
            os.makedirs(path)

    def get_voices(self, language: str) -> List:
        voices = self.engine.getProperty('voices')
        lang = language.lower()
        filtered = []
        for v in voices:
            # pyttsx3 voices: v.languages is a list of bytes or strings
            langs = [l.decode().lower() if isinstance(l, bytes) else l.lower() for l in v.languages]
            if any(lang in l for l in langs) or lang in v.id.lower():
                filtered.append(v)
        return filtered if filtered else voices

    def set_voice(self, language: str, voice_idx: int = 0):
        voices = self.get_voices(language)
        if not voices:
            pretty_print(f"No voices found for language '{language}', using default.", color="error")
            voices = self.engine.getProperty('voices')
        if voice_idx >= len(voices):
            pretty_print("Invalid voice number, using default voice", color="error")
            voice_idx = 0
        self.engine.setProperty('voice', voices[voice_idx].id)

    def speak(self, sentence: str, voice_idx: int = 0):
        if not self.enable or not self.engine:
            return
        self.set_voice(self.language, voice_idx)
        sentence = self.clean_sentence(sentence)
        self.engine.say(sentence)
        self.engine.runAndWait()

    def clean_sentence(self, sentence):
        lines = sentence.split('\n')
        filtered_lines = [line for line in lines if line.strip()]
        sentence = ' '.join(filtered_lines)
        sentence = re.sub(r'`.*?`', '', sentence)
        sentence = re.sub(r'https?://\S+', '', sentence)
        sentence = re.sub(r'\s+', ' ', sentence).strip()
        return sentence

if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    speech = Speech()
    tosay_en = "I looked up recent news using the website https://www.theguardian.com/world"
    tosay_ru = "Я посмотрел последние новости на сайте https://www.theguardian.com/world"
    tosay_uz = "Men so‘nggi yangiliklarni https://www.theguardian.com/world saytida ko‘rdim."
    tosay_zh = "你好，这是一个中文测试。"
    tosay_ja = "これは日本語のテストです。"
    tosay_fr = "Ceci est un test en français."

    # Пример для русского
    spk = Speech(enable=True, language="ru", voice_idx=0)
    spk.speak(tosay_ru)

    # Пример для узбекского (если установлен голос)
    spk = Speech(enable=True, language="uz", voice_idx=0)
    spk.speak(tosay_uz)

    # Примеры для других языков
    spk = Speech(enable=True, language="en", voice_idx=0)
    spk.speak(tosay_en)
    spk = Speech(enable=True, language="zh", voice_idx=0)
    spk.speak(tosay_zh)
    spk = Speech(enable=True, language="ja", voice_idx=0)
    spk.speak(tosay_ja)
    spk = Speech(enable=True, language="fr", voice_idx=0)
    spk.speak(tosay_fr)