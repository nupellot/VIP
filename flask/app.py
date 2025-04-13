from flask import Flask, render_template, jsonify
import sqlite3
import statistics

app = Flask(__name__)

def get_data():
    db_path = r'C:\YandexDisk\! Stuff\VIP-Pelmeni\voting.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Извлекаем всех экспертов
    cursor.execute("SELECT id, name FROM experts")
    experts = cursor.fetchall()

    # Извлекаем всех номинантов (secret_name вместо name)
    cursor.execute("SELECT id, secret_name FROM nominants")
    nominants = cursor.fetchall()

    # Извлекаем все оценки
    cursor.execute("SELECT expert_id, nominant_id, rating FROM votes")
    votes = cursor.fetchall()

    # Создаем словарь для хранения оценок по номинантам
    nominant_ratings = {nominant[0]: [] for nominant in nominants}
    for vote in votes:
        nominant_ratings[vote[1]].append(vote[2])

    # Вычисляем среднюю оценку и дисперсию для каждого номинанта
    nominant_stats = {}
    for nominant_id, ratings in nominant_ratings.items():
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            variance = statistics.variance(ratings) if len(ratings) > 1 else 0
            nominant_stats[nominant_id] = {'avg': avg_rating, 'variance': variance}
        else:
            nominant_stats[nominant_id] = {'avg': 0, 'variance': 0}

    conn.close()
    return experts, nominants, votes, nominant_stats

@app.route('/')
def index():
    experts, nominants, votes, nominant_stats = get_data()
    return render_template('index.html', experts=experts, nominants=nominants, votes=votes, nominant_stats=nominant_stats)

@app.route('/api/data')
def api_data():
    experts, nominants, votes, nominant_stats = get_data()
    return jsonify(experts=experts, nominants=nominants, votes=votes, nominant_stats=nominant_stats)

if __name__ == "__main__":
    app.run(debug=True)
