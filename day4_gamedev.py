import ollama
import json
from typing import Dict, Any, List
import re


class BasicActionLLM:
    def __init__(self):
        self.model = ""
        self.conversation_history = []
        self.system_prompt = ""
        self.finish_prompt = ""
        self.think_delete = False

    def add_to_context(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})

    def get_llm_response(self, prompt: str):
        final_response = False
        self.add_to_context("user", prompt)
        try:
            response = ollama.chat(
                model=self.model,
                messages=self.conversation_history,
                stream=False,
            )
            llm_response = response["message"]["content"].strip()
            self.add_to_context("assistant", llm_response)
            if self.think_delete:
                llm_response = self.clean_response(llm_response)
                try:
                    llm_response = json.loads(llm_response)
                    final_response = True
                except Exception as e:
                    pass
                return final_response, llm_response
            else:
                try:
                    llm_response_clear = self.clean_response(llm_response)
                    llm_response_clear = json.loads(llm_response_clear)
                    llm_response = llm_response_clear
                    final_response = True
                except Exception as e:
                    pass
                return final_response, llm_response
        except Exception as e:
            print(f"Ошибка при обращении к LLM: {str(e)}")
            return final_response, ""

    def clean_response(self, llm_response: str):
        return re.sub(r"<think>.*?</think>", "", llm_response, flags=re.DOTALL).strip()

    def save_application(self, info: str, file_name: str):
        try:
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(info, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            return False


class GeneralInformation(BasicActionLLM):
    def __init__(self):
        self.model = "qwen3:30b"
        self.conversation_history = []
        self.system_prompt = """
            Ты система для формирования базового технического задания на разработку игры
            Отвечай только фактом, без "я думаю", "можно сказать" и других рассуждений.  
            Нужно собрать следующею информацию:
            1. Игровой движок
            2. Жанр или жанры
            3. Ограничение по возрасту
            4. Референсные игры
            
            
            Задавайте вопросы последовательно, используй историю диалога для понимания контекста, при необходимости переспрашивай, допустимо править явные опечатки, ответы пользователя нужно приводить в общепринятые написания и очищать от мусора.
            Ответы пользователя нужно проверять на достоверность и правдивость
            При выводе Жанра нужно указать общий жанр и указанный пользователем если они отличаются
            По итогу опроса нужно собрать ответы пользователя вместе. 
            Итоговый ответ должен быть в формате json по следующей строго по схеме:
            {
                engine: Содержит игровой движок,
                genre: Содержит жанр или жанры,
                age_rating: содержит ограничение по возрасту,
                reference_games: Содержит референсные игры
            }
        """
        self.sending_prompt = ""
        self.think_delete = True

    def get_gamedev_tz_info(self):
        self.add_to_context("system", self.system_prompt)
        _final, response = self.get_llm_response("Привет")
        print(f"Бот_ТЗ: {response}")
        while True:
            try:
                user_input = input("\nВы: ").strip()
                final, response = self.get_llm_response(user_input)
                if final:
                    self.save_application(response, "GeneralInformation.json")
                    return self.convert_for_sending(response)
                print(f"Бот_ТЗ: {response}")
            except Exception as e:
                print(f"Произошла ошибка: {e}")

    def convert_for_sending(self, final: dict) -> str:
        return f"""
            1. Игровой движок - {final.get('engine')}
            2. Жанр или жанры - {final.get('genre')}
            3. Ограничение по возрасту - {final.get('age_rating')}
            4. Референсные игры - {final.get('reference_games')}
        """


class CheckingCorrectness(BasicActionLLM):
    def __init__(self):
        self.model = "qwen3:30b"
        self.conversation_history = []
        self.system_prompt = """
            Ты система для проверки корректности технического задания на разработку игры
            Отвечай только фактом, без "я думаю", "можно сказать" и других рассуждений.
            
            Техническое задание:
            {tz}
            
            Необходимо проверить сочетаемость и не взаимоисключаемость характеристик технического задания.
        """
        self.finish_prompt = ""
        self.think_delete = True

    def corrector_tz(self, tz):
        system_prompt_actual = self.system_prompt.format(tz=tz)
        self.add_to_context("system", system_prompt_actual)
        _final, response = self.get_llm_response("Проверь на корректность")
        print(f"Бот_корректор: {response}")


def main():
    bot_info = GeneralInformation()
    bot_validate = CheckingCorrectness()
    try:
        game_tz_info = bot_info.get_gamedev_tz_info()
        print("")
        print("Подготовленное ТЗ отправлено на проверку, ожидайте")
        print("")
        bot_validate.corrector_tz(game_tz_info)

    except Exception as e:
        print(f"Произошла ошибка в процессе сбора данных: {str(e)}")


if __name__ == "__main__":
    main()
