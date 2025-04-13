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

    # Извлекаем всех номинантов (secret_name, price, grams)
    cursor.execute("SELECT id, secret_name, price, grams FROM nominants")
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

    # Добавляем вычисления "Цена за кг" и "КПД"
    nominant_details = []
    for nominant in nominants:
        nominant_id = nominant[0]
        price = nominant[2]
        grams = nominant[3]
        
        # Вычисление "Цены за кг"
        price_per_kg = (price / grams) * 1000 if grams != 0 else 0
        
        # Вычисление КПД (средняя оценка / цена за кг)
        avg_rating = nominant_stats.get(nominant_id, {}).get('avg', 0)
        kpd = avg_rating / price_per_kg if price_per_kg != 0 else 0
        
        nominant_details.append({
            'id': nominant_id,
            'secret_name': nominant[1],
            'price_per_kg': price_per_kg,
            'kpd': kpd
        })

    conn.close()
    return experts, nominants, votes, nominant_stats, nominant_details


@app.route('/')
def index():
    experts, nominants, votes, nominant_stats, nominant_details = get_data()
    return render_template('index.html', experts=experts, nominants=nominants, votes=votes, 
                           nominant_stats=nominant_stats, nominant_details=nominant_details)


@app.route('/api/data')
def api_data():
    experts, nominants, votes, nominant_stats, nominant_details = get_data()
    return jsonify(experts=experts, nominants=nominants, votes=votes, 
                   nominant_stats=nominant_stats, nominant_details=nominant_details)


if __name__ == "__main__":
    app.run(debug=True)
