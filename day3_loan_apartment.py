import ollama
import json
from typing import Dict, Any, List


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
                model="qwen3-coder:30b",
                messages=self.conversation_history,
                stream=False,
            )
            llm_response = response["message"]["content"].strip()

            # Добавляем ответ LLM в историю
            self.add_to_context("assistant", llm_response)

            return llm_response
        except Exception as e:
            print(f"Ошибка при обращении к LLM: {str(e)}")
            return ""

    def get_personal_info(self):
        """Получение личной информации через диалог с LLM"""
        print("=== Сбор личной информации ===\n")

        # Начальный запрос для сбора данных
        initial_prompt = """
        Пользователь запускает систему оформления кредита. 
        Соберите следующую информацию о заемщике:
        1. Полное имя (ФИО)
        2. Возраст
        3. Номер телефона
        4. Email
        
        Задавайте вопросы последовательно и используйте историю диалога для понимания контекста.
        """

        print("LLM: Давайте соберем вашу личную информацию для оформления кредита.")
        self.get_llm_response(initial_prompt)

        # Получаем имя
        name_prompt = "Пожалуйста, укажите ваше полное имя (ФИО):"
        full_name = self.get_llm_response(name_prompt)

        # Получаем возраст
        age_prompt = f"Спасибо, {full_name}. Уточните, сколько вам лет?"
        age = self.get_llm_response(age_prompt)

        # Получаем телефон
        phone_prompt = "Укажите ваш номер телефона для связи:"
        phone = self.get_llm_response(phone_prompt)

        # Получаем email
        email_prompt = "Укажите ваш email адрес:"
        email = self.get_llm_response(email_prompt)

        self.user_data["personal_info"] = {
            "full_name": full_name,
            "age": age,
            "phone": phone,
            "email": email,
        }

        print("Информация о личных данных собрана.")
        return self.user_data["personal_info"]

    def get_financial_info(self):
        """Получение финансовой информации через диалог с LLM"""
        print("\n=== Сбор финансовой информации ===\n")

        # Используем контекст из предыдущих сообщений
        financial_prompt = """
        Пользователь уже предоставил информацию о себе:
        - Имя: {full_name}
        - Возраст: {age}
        - Телефон: {phone}
        - Email: {email}
        
        Теперь соберем данные о финансовых возможностях:
        1. Ежемесячный доход
        2. Статус занятости (работает/студент/пенсионер и т.д.)
        3. Наличие кредитной истории
        
        Задавайте вопросы последовательно, используя предыдущую информацию.
        """.format(
            **self.user_data["personal_info"]
        )

        print("LLM: Давайте соберем информацию о ваших финансовых возможностях.")
        self.get_llm_response(financial_prompt)

        # Получаем доход
        income_prompt = "Каков ваш ежемесячный доход (в рублях)?"
        monthly_income = self.get_llm_response(income_prompt)

        # Получаем статус занятости
        employment_prompt = (
            f"Уточните ваш текущий статус: работаете, учитесь, на пенсии или иное?"
        )
        employment_status = self.get_llm_response(employment_prompt)

        # Получаем кредитную историю
        credit_history_prompt = "Есть ли у вас кредитная история? (да/нет)"
        credit_history = self.get_llm_response(credit_history_prompt)

        # Анализ кредитной истории
        analysis_prompt = f"""
        Пользователь имеет доход {monthly_income} руб. и работает {employment_status}.
        У него {'есть' if credit_history == 'да' else 'нет'} кредитная история.
        Оцените уровень кредитного риска и предложите рекомендации по улучшению кредитной истории.
        """

        credit_analysis = self.get_llm_response(analysis_prompt)

        self.user_data["financial_info"] = {
            "monthly_income": monthly_income,
            "employment_status": employment_status,
            "credit_history": credit_history,
            "llm_credit_analysis": credit_analysis,
        }

        print("Информация о финансах собрана.")
        return self.user_data["financial_info"]

    def get_property_info(self):
        """Получение информации о недвижимости через диалог с LLM"""
        print("\n=== Сбор информации о недвижимости ===\n")

        property_prompt = """
        Пользователь уже предоставил:
        - Личная информация: {full_name}, возраст {age}
        - Финансовая информация: доход {monthly_income}, статус {employment_status}
        
        Соберем информацию о недвижимости, которую планируете приобрести:
        1. Тип недвижимости (квартира, дом и т.д.)
        2. Стоимость объекта
        3. Сроки покупки
        4. Размер первоначального взноса
        
        Задавайте вопросы последовательно, используя предыдущую информацию.
        """.format(
            **self.user_data["personal_info"], **self.user_data["financial_info"]
        )

        print(
            "LLM: Давайте соберем информацию о недвижимости, которую вы планируете приобрести."
        )
        self.get_llm_response(property_prompt)

        # Получаем тип недвижимости
        property_type_prompt = (
            "Какой тип недвижимости вы планируете приобрести? (квартира, дом и т.д.)"
        )
        property_type = self.get_llm_response(property_type_prompt)

        # Получаем стоимость
        cost_prompt = "Какова примерная стоимость объекта недвижимости?"
        cost = self.get_llm_response(cost_prompt)

        # Получаем сроки покупки
        timeline_prompt = "Когда планируете совершить покупку? (указать срок)"
        timeline = self.get_llm_response(timeline_prompt)

        # Получаем размер взноса
        down_payment_prompt = "Какой размер первоначального взноса вы планируете?"
        down_payment = self.get_llm_response(down_payment_prompt)

        self.user_data["property_info"] = {
            "property_type": property_type,
            "cost": cost,
            "timeline": timeline,
            "down_payment": down_payment,
        }

        print("Информация о недвижимости собрана.")
        return self.user_data["property_info"]

    def get_loan_terms(self):
        """Получение условий кредита через диалог с LLM"""
        print("\n=== Сбор условий кредита ===\n")

        loan_prompt = """
        Пользователь уже предоставил:
        - Личная информация: {full_name}
        - Финансовая информация: доход {monthly_income}, статус {employment_status}
        - Информация о недвижимости: тип {property_type}, стоимость {cost}
        
        Соберем информацию о условиях кредита:
        1. Сумма кредита
        2. Срок кредита (в годах)
        3. Цель кредита
        4. Предпочтительный график погашения
        
        Задавайте вопросы последовательно, используя всю предыдущую информацию.
        """.format(
            **self.user_data["personal_info"],
            **self.user_data["financial_info"],
            **self.user_data["property_info"],
        )

        print("LLM: Давайте соберем информацию о условиях кредита.")
        self.get_llm_response(loan_prompt)

        # Получаем сумму кредита
        loan_amount_prompt = "Какую сумму кредита вы планируете получить?"
        loan_amount = self.get_llm_response(loan_amount_prompt)

        # Получаем срок кредита
        loan_term_prompt = "На какой срок планируете взять кредит (в годах)?"
        loan_term = self.get_llm_response(loan_term_prompt)

        # Получаем цель кредита
        purpose_prompt = "Какова цель получения кредита?"
        purpose = self.get_llm_response(purpose_prompt)

        # Получаем график погашения
        payment_schedule_prompt = "Какой график погашения предпочитаете? (аннуитетный, дифференцированный и т.д.)"
        payment_schedule = self.get_llm_response(payment_schedule_prompt)

        self.user_data["loan_terms"] = {
            "loan_amount": loan_amount,
            "loan_term": loan_term,
            "purpose": purpose,
            "payment_schedule": payment_schedule,
        }

        print("Условия кредита собраны.")
        return self.user_data["loan_terms"]

    def generate_summary(self):
        """Генерация итогового отчета"""
        summary_prompt = """
        Собранная информация о клиенте:
        Личные данные: {full_name}, возраст {age}, телефон {phone}, email {email}
        Финансовые данные: доход {monthly_income}, статус {employment_status}, кредитная история {credit_history}
        Недвижимость: тип {property_type}, стоимость {cost}, срок покупки {timeline}, взнос {down_payment}
        Условия кредита: сумма {loan_amount}, срок {loan_term}, цель {purpose}, график {payment_schedule}
        
        Сформируйте краткое резюме по всем собранным данным.
        """.format(
            **self.user_data["personal_info"],
            **self.user_data["financial_info"],
            **self.user_data["property_info"],
            **self.user_data["loan_terms"],
        )

        return self.get_llm_response(summary_prompt)

    def get_full_application(self):
        """Получение полного заявления через диалог"""
        print("Начинаем сбор данных для кредитной заявки...\n")

        # Собираем все данные последовательно
        self.get_personal_info()
        self.get_financial_info()
        self.get_property_info()
        self.get_loan_terms()

        # Генерируем итоговый отчет
        print("\n" + "=" * 50)
        print("ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 50)
        summary = self.generate_summary()
        print(summary)

        return self.user_data

    def save_application(self):
        """Сохранение данных в JSON файл"""
        try:
            with open("credit_application.json", "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, indent=2, ensure_ascii=False)
            print("\nДанные успешно сохранены в файл 'credit_application.json'")
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

        # Сохраняем данные
        bot.save_application()

        print("\n" + "=" * 50)
        print("ОБРАБОТКА ЗАЯВКИ ЗАВЕРШЕНА")
        print("=" * 50)

    except Exception as e:
        print(f"Произошла ошибка в процессе сбора данных: {str(e)}")


if __name__ == "__main__":
    main()
