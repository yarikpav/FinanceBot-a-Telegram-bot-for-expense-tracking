# FinanceBot-a-Telegram-bot-for-expense-tracking
## 📌 Project Description
FinanceBot is a Telegram bot for tracking personal expenses.  
It allows you to add expenses, view a list of expenses, get statistics by category, and export data.  
The project is integrated with Django for storing requests and managing the admin panel.

---

## 🛠 Technologies Used
- **Python 3.10**
- **Django** — admin panel and database
- **PyTelegramBotAPI** — working with the Telegram Bot API
- **JSON** — storing expenses
- **SQLite** (or another Django database)

---

## ⚙️ Installation Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/username/financebot.git
   cd financebot

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   
3. Set up Django:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser

4. Get a token from BotFather and paste it into finance_bot_telegram.py:
   ```python
   TOKEN = "YOU_TOKEN"

---

🚀 Startup Guide
1. Start the Django admin interface:
   ```bash
   python manage.py runserver

2. Launch the Telegram bot:
   ```bash
   python telegrambot/finance_bot_telegram.py

3. The bot will start listening for commands on Telegram.

---

💬 Examples of chatbot functionality
  Adding a flow rate:
  
      ```command
      /add 120000 Maxim
  <img width="684" height="147" alt="image" src="https://github.com/user-attachments/assets/6b566e2e-6c56-4356-95d2-d997522a0926" />
  
  View list:

    ```command
    /list
  <img width="687" height="279" alt="image" src="https://github.com/user-attachments/assets/7ec23260-fed2-4e19-9190-612a14b5aed1" />

  Statistics:

    ```command
    /stats
  <img width="673" height="331" alt="image" src="https://github.com/user-attachments/assets/51f9f1e4-7111-482c-aa29-732ffad0ba98" />

---

FinanceBot makes tracking expenses simple and convenient right in Telegram.
Future plans include adding charts and integrating with banking API.
