# 💸 Flask Finance App

[🌐 Live Site on Render](https://flask-finance-app-axfb.onrender.com)

This is a personal stock trading simulation app built using Flask, Bootstrap, and SQLite. Users can register, log in, buy and sell stocks, and view their portfolio and transaction history.

---

## 🚀 Features

- 🔐 User authentication (register, login, logout)
- 📈 Buy and sell stocks with live market prices (via `lookup()` API)
- 💰 View current holdings and cash balance
- 🧾 Track transaction history
- ⚠️ Input validation and user-friendly error messages

---

## 🛠 Technologies Used

- **Python & Flask** – backend logic and routing  
- **SQLite** – lightweight database for storing user data  
- **Flask-Session** – for secure server-side sessions  
- **Bootstrap** – responsive UI styling  
- **Jinja2** – HTML templating  
- **Render** – for live deployment  

---


## 🚀 How to Run Locally

```bash
git clone https://github.com/yourusername/flask-finance-app.git
cd flask-finance-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run
