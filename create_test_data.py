import sqlite3

# Путь к файлу базы данных SQLite
DB_FILE = 'voting.db'

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Позволяет работать с результатами запроса как с dict
    return conn

# Функция для добавления тестовых данных
def fill_test_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Добавление тестовых экспертов (пользователей)
    experts = [
        ('user1', 'User One', 'https://example.com/profile1.jpg'),
        ('user2', 'User Two', 'https://example.com/profile2.jpg'),
        ('user3', 'User Three', 'https://example.com/profile3.jpg'),
    ]

    cursor.executemany("INSERT OR IGNORE INTO expert (username, name, profile_picture) VALUES (?, ?, ?)", experts)

    # Добавление тестовых кандидатов
    nominants = [
        ('Номинант 1', 'https://example.com/candidate1.jpg', 100),
        ('Номинант 2', 'https://example.com/candidate2.jpg', 200),
        ('Номинант 3', 'https://example.com/candidate3.jpg', 300),
        ('Номинант 4', 'https://example.com/candidate4.jpg', 400),
        ('Номинант 5', 'https://example.com/candidate5.jpg', 500),
    ]

    cursor.executemany("INSERT OR IGNORE INTO nominants (name, image, price) VALUES (?, ?, ?)", nominants)

    # Добавление тестовых голосов
    votes = [
        ('user1', 'Номинант 1', 8),
        ('user1', 'Номинант 2', 7),
        ('user2', 'Номинант 3', 9),
        ('user3', 'Номинант 1', 10),
        ('user3', 'Номинант 5', 6),
    ]

    for vote in votes:
        # Получаем id эксперта
        cursor.execute("SELECT id FROM expert WHERE username = ?", (vote[0],))
        expert = cursor.fetchone()
        if expert:
            expert_id = expert['id']
        
        # Получаем id номинанта
        cursor.execute("SELECT id FROM nominants WHERE name = ?", (vote[1],))
        nominant = cursor.fetchone()
        if nominant:
            nominant_id = nominant['id']
        
        # Добавляем голос
        cursor.execute("INSERT INTO votes (expert_id, nominant_id, rating) VALUES (?, ?, ?)", (expert_id, nominant_id, vote[2]))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    fill_test_data()
    print("База данных заполнена тестовыми данными.")
