from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)

# Функция для получения данных из базы
def get_data():
    db_path = r'C:\YandexDisk\! Stuff\VIP-Pelmeni\voting.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Извлекаем всех экспертов
    cursor.execute("SELECT id, name FROM experts")
    experts = cursor.fetchall()

    # Извлекаем всех номинантов
    cursor.execute("SELECT id, name FROM nominants")
    nominants = cursor.fetchall()

    # Извлекаем все оценки
    cursor.execute("SELECT expert_id, nominant_id, rating FROM votes")
    votes = cursor.fetchall()

    conn.close()

    return experts, nominants, votes

@app.route('/')
def index():
    experts, nominants, votes = get_data()
    return render_template('index.html', experts=experts, nominants=nominants, votes=votes)

@app.route('/api/data')
def api_data():
    experts, nominants, votes = get_data()
    return jsonify(experts=experts, nominants=nominants, votes=votes)

if __name__ == "__main__":
    app.run(debug=True)
