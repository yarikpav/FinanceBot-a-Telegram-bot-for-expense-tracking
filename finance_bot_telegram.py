import telebot
import json
from datetime import datetime
import os
import sys
import django

#Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "financebot.settings")
django.setup()

from bot_queries.models import UserQuery

TOKEN = "YOU_TOKEN"
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "expenses.json"

#работа с данными
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_expense(user_id, amount, category):
    data = load_data()
    data.append({
        "user": user_id,
        "amount": float(amount),
        "category": category,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    save_data(data)

def list_expenses(user_id):
    data = load_data()
    user_data = [e for e in data if e["user"] == user_id]
    if not user_data:
        return "Нет расходов."
    return "\n".join([f"{e['date']} | {e['category']} | {e['amount']} тг." for e in user_data])

def stats(user_id):
    data = load_data()
    user_data = [e for e in data if e["user"] == user_id]
    if not user_data:
        return "Нет данных для статистики."
    total = sum(e["amount"] for e in user_data)
    categories = {}
    for e in user_data:
        categories[e["category"]] = categories.get(e["category"], 0) + e["amount"]
    stats_text = f"💰 Всего расходов: {total} тг.\n📊 По категориям:\n"
    for cat, amt in categories.items():
        stats_text += f"  {cat}: {amt} тг.\n"
    return stats_text

def log_query(user_id, command, text):
    UserQuery.objects.create(
        user_id=user_id,
        command=command,
        message_text=text
    )

#Основные команды
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "👋 Привет! Я помогу вести учёт расходов.\nИспользуй /help для списка команд.")
    log_query(message.from_user.id, "start", message.text)

@bot.message_handler(commands=["help"])
def help_menu(message):
    bot.reply_to(message,
        "/add [сумма] [категория] - добавить расход\n"
        "/list - показать все расходы\n"
        "/stats - показать статистику\n"
        "/delete [номер] - удалить расход\n"
        "/clear - очистить все расходы\n"
        "/category [название] - расходы по категории\n"
        "/monthly - расходы за месяц\n"
        "/export - экспорт расходов\n"
        "/top - топ категории\n"
        "/about - информация о боте\n"
        "/feedback [текст] - отправить отзыв"
    )
    log_query(message.from_user.id, "help", message.text)

@bot.message_handler(commands=["add"])
def add(message):
    try:
        parts = message.text.split()
        if len(parts) >= 3:
            amount = parts[1]
            category = " ".join(parts[2:])
            add_expense(message.from_user.id, amount, category)
            bot.reply_to(message, f"✅ Добавлен расход: {amount} тг. ({category})")
        else:
            bot.reply_to(message, "❌ Формат: /add [сумма] [категория]")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")
    finally:
        log_query(message.from_user.id, "add", message.text)

@bot.message_handler(commands=["list"])
def list_cmd(message):
    bot.reply_to(message, list_expenses(message.from_user.id))
    log_query(message.from_user.id, "list", message.text)

@bot.message_handler(commands=["stats"])
def stats_cmd(message):
    bot.reply_to(message, stats(message.from_user.id))
    log_query(message.from_user.id, "stats", message.text)

#удаляет конкретный расход из списка (пример: "/delete 3" удалит третью запись пользователя)
@bot.message_handler(commands=["delete"])
def delete_cmd(message):
    try:
        parts = message.text.split()
        if len(parts) == 2 and parts[1].isdigit():
            idx = int(parts[1]) - 1
            data = load_data()
            user_data = [e for e in data if e["user"] == message.from_user.id]
            if 0 <= idx < len(user_data):
                expense = user_data[idx]
                data.remove(expense)
                save_data(data)
                bot.reply_to(message, f"🗑 Удалён расход: {expense['amount']} тг. ({expense['category']})")
            else:
                bot.reply_to(message, "❌ Нет записи с таким номером.")
        else:
            bot.reply_to(message, "❌ Формат: /delete [номер]")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")
    finally:
        log_query(message.from_user.id, "delete", message.text)

#очищает все расходы пользователя
@bot.message_handler(commands=["clear"])
def clear_cmd(message):
    data = load_data()
    data = [e for e in data if e["user"] != message.from_user.id]
    save_data(data)
    bot.reply_to(message, "🧹 Все расходы очищены.")
    log_query(message.from_user.id, "clear", message.text)

#сортировка по категории (пример: "/category еда")
@bot.message_handler(commands=["category"])
def category_cmd(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) == 2:
        cat = parts[1].strip()
        data = load_data()
        user_data = [e for e in data if e["user"] == message.from_user.id and e["category"].lower() == cat.lower()]
        if not user_data:
            bot.reply_to(message, f"Нет расходов по категории {cat}.")
        else:
            text = "\n".join([f"{e['date']} | {e['amount']} тг." for e in user_data])
            bot.reply_to(message, text)
    else:
        bot.reply_to(message, "❌ Формат: /category [название]")
    log_query(message.from_user.id, "category", message.text)

#показывает статистику за текущий месяц
@bot.message_handler(commands=["monthly"])
def monthly_cmd(message):
    now = datetime.now().strftime("%Y-%m")
    data = load_data()
    user_data = [e for e in data if e["user"] == message.from_user.id and e["date"].startswith(now)]
    if not user_data:
        bot.reply_to(message, "Нет расходов за этот месяц.")
    else:
        total = sum(e["amount"] for e in user_data)
        bot.reply_to(message, f"📅 Расходы за месяц: {total} тг.")
    log_query(message.from_user.id, "monthly", message.text)

#сохраняет расходы в файл (CSV или JSON) и отправить пользователю
@bot.message_handler(commands=["export"])
def export_cmd(message):
    filename = f"expenses_{message.from_user.id}.json"
    data = load_data()
    user_data = [e for e in data if e["user"] == message.from_user.id]
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=2, ensure_ascii=False)
    with open(filename, "rb") as f:
        bot.send_document(message.chat.id, f)
    log_query(message.from_user.id, "export", message.text)

#показывает топ‑3 категории, где больше всего расходов
@bot.message_handler(commands=["top"])
def top_cmd(message):
    data = load_data()
    user_data = [e for e in data if e["user"] == message.from_user.id]
    if not user_data:
        bot.reply_to(message, "Нет расходов.")
    else:
        categories = {}
        for e in user_data:
            categories[e["category"]] = categories.get(e["category"], 0) + e["amount"]
        top3 = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
        text = "🏆 Топ категории:\n" + "\n".join([f"{cat}: {amt} тг." for cat, amt in top3])
        bot.reply_to(message, text)
    log_query(message.from_user.id, "top", message.text)

#Сервесные команды!!
#показывает информацию о боте
@bot.message_handler(commands=["about"])
def about_cmd(message):
    bot.reply_to(message, "ℹ️ Я бот для учёта расходов.\nКоманды: /add, /list, /stats, /delete, /clear, /category, /monthly, /export, /top, /about, /feedback")
    log_query(message.from_user.id, "about", message.text)

#команда для отзыва
@bot.message_handler(commands=["feedback"])
def feedback_cmd(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) == 2:
        fb = parts[1]
        bot.reply_to(message, "✅ Спасибо за отзыв!")
        print(f"Feedback от {message.from_user.id}: {fb}")
    else:
        bot.reply_to(message, "❌ Формат: /feedback [текст]")
    log_query(message.from_user.id, "feedback", message.text)

#запуск бота
print("Бот запущен...")
bot.polling(none_stop=True, interval=1, timeout=20)
