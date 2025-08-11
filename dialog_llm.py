import requests

OLLAMA_URL = "http://localhost:11434"
MAX_MESSAGES = 10

def get_llm_response(prompt, conversation_history=None):
    try:
        url = f"{OLLAMA_URL}/api/generate"
        if conversation_history:
            full_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
            full_prompt += f"\nuser: {prompt}"
        else:
            full_prompt = prompt
        payload = {
            "model": "qwen3-coder:30b",
            "prompt": full_prompt,
            "stream": False
        }
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "Нет ответа от модели")
        else:
            return f"Ошибка API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Ошибка: {str(e)}"

def get_ollama_info():
    try:
        version_response = requests.get(f"{OLLAMA_URL}/api/version", timeout=5)
        info = {}
        if version_response.status_code == 200:
            version_data = version_response.json()
            info["version"] = version_data.get("version", "Неизвестная версия")
        else:
            info["version"] = "Не удалось получить версию"
        models_response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if models_response.status_code == 200:
            models_data = models_response.json()
            info["models"] = models_data.get("models", [])
        else:
            info["models"] = []
        return info
    except requests.exceptions.ConnectionError:
        return {
            "version": "Ollama не запущена",
            "models": []
        }
    except Exception as e:
        return {
            "version": f"Ошибка: {str(e)}",
            "models": []
        }

def main():
    print("Простой чат-бот")
    print("Введите '!quit' для выхода")
    print("Введите '!clear' для очистки истории")
    print("-" * 40)
    ollama = get_ollama_info()
    print(f"OLLAMA: {ollama.get('version', 'Ошибка')}")
    models = [{k: d[k] for k in ['name', 'modified_at']} for d in ollama.get('models',[])]
    print(f"Доступные модели: {models}")
    
    conversation_history = []
   
    while True:
        try:
            user_input = input("\nВы: ").strip()
            if user_input.lower() in ['!quit']:
                print("Бот: До свидания!")
                break
            if user_input.lower() == '!clear':
                conversation_history = []
                print("Начат новый диалог")
                continue
            if not user_input:
                continue
            conversation_history.append({"role": "user", "content": user_input})
            if len(conversation_history) > MAX_MESSAGES * 2:
                conversation_history = conversation_history[-MAX_MESSAGES * 2:]
            response = get_llm_response(user_input, conversation_history)
            conversation_history.append({"role": "assistant", "content": response})
            print(f"Бот: {response}")
        except Exception as e:
            print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()