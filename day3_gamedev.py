import ollama
import json
from typing import Dict, Any, List
import re


class CreditApplicationBot:
    def __init__(self):
        self.conversation_history = []
        self.user_data = {}

    def add_to_context(self, role: str, content: str):
        """Добавление сообщения в историю контекста"""
        self.conversation_history.append({"role": role, "content": content})

    def get_llm_response(self, prompt: str) -> str:
        """Получение ответа от LLM с сохранением контекста"""
        # Добавляем новый запрос в историю
        self.add_to_context("user", prompt)

        try:
            response = ollama.chat(
                model="qwen3:30b",
                messages=self.conversation_history,
                stream=False,
            )
            llm_response = response["message"]["content"].strip()

            # Добавляем ответ LLM в историю
            self.add_to_context("assistant", llm_response)

            return re.sub(r'<think>.*?</think>', '', llm_response, flags=re.DOTALL).strip()
        except Exception as e:
            print(f"Ошибка при обращении к LLM: {str(e)}")
            return ""

    def get_gamedev_tz_info(self):
        """Получение личной информации через диалог с LLM"""
        print("=== Сбор информации для составления базового технического задания для разработки игры ===\n")

        # Начальный запрос для сбора данных
        system_prompt = """
        Ты система для формирования базового технического задания на разработку игры
        Отвечай только фактом, без "я думаю", "можно сказать" и других рассуждений.  
        Нужно собрать следующею информацию:
        1. Игровой движок
        2. Жанр или жанры
        3. Ограничение по возрасту
        4. Реверенсные игры
        
        
        Задавайте вопросы последовательно, используй историю диалога для понимания контекста, при необходимости переспрашивай, допустимо править явные опечатки, ответы пользователя нужно приводить в общепринятые написания и очищать от мусора.
        Ответы пользователя нужно проверять на достоверность и правдивость
        При выводе Жанра нужно указать общий жанр и указаный пользователем если они отличаются
        По итогу опроса нужно собрать ответы пользователя вместе. 
        Итоговый ответ должен быть в формате json по следующей строго по схеме:
        {
            engine: Содержит игровой движок,
            genre: Содержит жанр или жанры,
            age_rating: содержит ограничение по возрасту,
            reference_games: Содержит реверенсные игры
        }
        """
        self.add_to_context('system', system_prompt)
        response = self.get_llm_response('Привет')
        print(f"Бот: {response}")
        while True:
            try:
                user_input = input("\nВы: ").strip()
                response = self.get_llm_response(user_input)
                try:
                    response_json = json.loads(response)
                    self.save_application(response_json)
                    print(f"Бот: {response_json}")
                    break
                except Exception as e:
                    print(f"Бот: {response}")
            except Exception as e:
                print(f"Произошла ошибка: {e}")
    
    def get_full_application(self):
        self.get_gamedev_tz_info()
        print(f"Сбор данных закончен")

    def save_application(self, gamedev_tz_info):
        """Сохранение данных в JSON файл"""
        try:
            with open("gamedev.json", "w", encoding="utf-8") as f:
                json.dump(gamedev_tz_info, f, indent=2, ensure_ascii=False)
            print("\nДанные успешно сохранены в файл 'gamedev.json'")
            return True
        except Exception as e:
            print(f"Ошибка при сохранении файла: {str(e)}")
            return False

def main():
    # Создаем бота для сбора данных
    bot = CreditApplicationBot()

    try:
        # Получаем полную заявку
        application_data = bot.get_full_application()

    except Exception as e:
        print(f"Произошла ошибка в процессе сбора данных: {str(e)}")


if __name__ == "__main__":
    main()
