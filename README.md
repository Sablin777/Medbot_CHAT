# Как пользоваться?
### Шаги:

Клонировать репозиторий 
```bash
git clone https://github.com/Sablin777/Medbot_CHAT.git
```
### ШАГ 01- После открытия репозитория создайте среду conda.

```bash
conda create -n medibot python=3.10 -y
```

```bash
conda activate medibot
```


### ШАГ 02- Установите необходимые зависимости
```bash
pip install -r requirements.txt
```


### Создайте файл `.env` в корневом каталоге и добавьте в него свои учетные данные Pinecone и OpenRouter (можно пользоваться любым другим сервисом) следующим образом.:

```ini
PINECONE_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
OPENROUTER_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```


```bash
# Выполните следующую команду, чтобы сохранить эмбеддинги в Pinecone
python store_index.py
```

```bash
# Выполните следующую команду
python app.py
```

Далее
```bash
open up localhost:
```


### Используемый стек:

- Python
- LangChain
- Flask
- Gpt-oss-20b (free) (OpenRouter)
- Pinecone

