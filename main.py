import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из файла .env
load_dotenv()

# Токен вашего бота
TOKEN = os.getenv('BOT_TOKEN')  # Получаем токен из переменной окружения

# Путь к файлу базы данных SQLite
DB_FILE = 'voting.db'

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Позволяет работать с результатами запроса как с dict
    return conn

# Функция для добавления эксперта в базу данных
def add_expert(user_id, username, name, profile_picture=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Добавляем пользователя, если его нет в базе
    cursor.execute("INSERT OR IGNORE INTO expert (username, name, profile_picture) VALUES (?, ?, ?)", (username, name, profile_picture))
    conn.commit()
    conn.close()

# Функция для добавления или обновления голоса
def add_or_update_vote(expert_username, nominant_name, rating):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем id эксперта
    cursor.execute("SELECT id FROM expert WHERE username = ?", (expert_username,))
    expert = cursor.fetchone()
    if expert is None:
        print(f"Ошибка: эксперт с никнеймом {expert_username} не найден.")  # Отладочное сообщение
        return None  # Эксперт не найден
    
    # Получаем id кандидата
    cursor.execute("SELECT id FROM nominants WHERE name = ?", (nominant_name,))
    nominant = cursor.fetchone()
    if nominant is None:
        print(f"Ошибка: кандидат с именем {nominant_name} не найден.")  # Отладочное сообщение
        return None  # Кандидат не найден

    # Проверка, существует ли уже голос этого пользователя за данного кандидата
    cursor.execute("""
        SELECT id FROM votes WHERE expert_id = ? AND nominant_id = ?
    """, (expert['id'], nominant['id']))
    existing_vote = cursor.fetchone()

    if existing_vote:
        # Если голос существует, обновляем его
        cursor.execute("""
            UPDATE votes SET rating = ? WHERE id = ?
        """, (rating, existing_vote['id']))
        conn.commit()
        conn.close()
        return "Ваш голос был обновлен."
    else:
        # Если голоса нет, добавляем новый
        cursor.execute("""
            INSERT INTO votes (expert_id, nominant_id, rating) VALUES (?, ?, ?)
        """, (expert['id'], nominant['id'], rating))
        conn.commit()
        conn.close()
        return "Ваш голос за нового кандидата сохранен!"

# Функция для получения всех голосов пользователя
def get_user_votes(expert_username):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем все голоса для данного эксперта
    cursor.execute("""
        SELECT nominants.name, votes.rating 
        FROM votes
        JOIN nominants ON votes.nominant_id = nominants.id
        JOIN expert ON votes.expert_id = expert.id
        WHERE expert.username = ?
    """, (expert_username,))
    
    votes = cursor.fetchall()
    conn.close()
    return votes

# Стартовая команда
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    
    # Получаем фотографию профиля пользователя
    profile_picture = None
    photos = await user.get_profile_photos()  # Асинхронно получаем фотографии профиля
    if photos.total_count > 0:
        # Сохраняем ID последней фотографии профиля
        profile_picture = photos.photos[-1][-1].file_id  # Последний фото ID
    
    # Добавляем пользователя в базу данных
    add_expert(user.id, user.username, user.first_name, profile_picture)

    # Создаем inline клавиатуру с кнопками /vote и /my_votes
    keyboard = [
        [InlineKeyboardButton("Проголосовать", callback_data="vote")],
        [InlineKeyboardButton("Мои голоса", callback_data="my_votes")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с кнопками
    await update.message.reply_text("Добро пожаловать! Выберите действие:", reply_markup=reply_markup)


# Команда для начала голосования
async def vote(update: Update, context: CallbackContext):
    user = update.callback_query.from_user  # Используем from_user из callback_query
    # Проверка наличия пользователя в базе данных
    conn = get_db_connection()
    cursor = conn.cursor()

    # Проверяем, есть ли пользователь в базе данных
    cursor.execute("SELECT * FROM expert WHERE username = ?", (user.username,))
    existing_user = cursor.fetchone()

    if not existing_user:
        # Если пользователя нет в базе, добавляем его
        profile_picture = None
        photos = await user.get_profile_photos()
        if photos.total_count > 0:
            profile_picture = photos.photos[-1][-1].file_id

        # Добавляем пользователя в базу данных
        add_expert(user.id, user.username, user.first_name, profile_picture)
        await update.callback_query.answer("Вы были добавлены в базу данных. Теперь вы можете проголосовать.")

    candidates = load_candidates()
    if not candidates:
        await update.callback_query.answer("Нет доступных кандидатов для голосования.")
        return

    keyboard = [
        [InlineKeyboardButton(candidate['name'], callback_data=f"candidate_{candidate['id']}")]
        for candidate in candidates
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("Выберите кандидата:", reply_markup=reply_markup)


# Функция для загрузки всех кандидатов из базы данных
def load_candidates():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM nominants")
    candidates = cursor.fetchall()
    conn.close()
    return candidates

# Обработка выбора кнопки
async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "my_votes":
        # Если нажата кнопка "Мои голоса", вызываем команду /my_votes
        await my_votes(update, context)
    elif query.data == "vote":
        # Если нажата кнопка "Проголосовать", вызываем команду /vote
        await vote(update, context)

    # Если нажата кнопка кандидата, то начинаем голосование
    else:
        nominant_id = int(query.data.split("_")[1])  # Получаем ID кандидата из callback_data
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM nominants WHERE id = ?", (nominant_id,))
        nominant = cursor.fetchone()
        conn.close()

        if nominant:
            context.user_data['nominant_id'] = nominant_id  # Сохраняем id выбранного кандидата
            context.user_data['nominant_name'] = nominant['name']  # Сохраняем имя кандидата
            await query.edit_message_text(
                text=f"Вы выбрали {nominant['name']}.\nПожалуйста, поставьте оценку от 1 до 10."
            )

# Обработка ввода оценки
async def receive_rating(update: Update, context: CallbackContext):
    try:
        rating = int(update.message.text)
        if 1 <= rating <= 10:
            # Получаем никнейм пользователя
            expert_username = update.message.from_user.username
            if not expert_username:
                expert_username = update.message.from_user.first_name  # В случае, если никнейм пуст

            # Получаем имя кандидата из контекста
            nominant_name = context.user_data.get('nominant_name')
            if not nominant_name:
                await update.message.reply_text("Сначала выберите кандидата с помощью /vote.")
                return

            # Добавляем или обновляем голос в базе данных
            message = add_or_update_vote(expert_username, nominant_name, rating)
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("Пожалуйста, поставьте оценку от 1 до 10.")
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число от 1 до 10.")

# Команда для отображения голосов пользователя
async def my_votes(update: Update, context: CallbackContext):
    user = update.callback_query.from_user  # Используем from_user из callback_query
    expert_username = user.username

    # Получаем все голоса пользователя
    votes = get_user_votes(expert_username)

    if not votes:
        await update.callback_query.answer("У вас нет голосов.")  # Используем callback_query для ответа
        return

    # Формируем сообщение с голосами
    vote_text = "Ваши голоса:\n"
    for vote in votes:
        vote_text += f"{vote['name']} - {vote['rating']} баллов\n"

    await update.callback_query.edit_message_text(vote_text)  # Редактируем сообщение, а не отправляем новое

# Основная функция для запуска бота
def main():
    # Создаем объект Application
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("vote", vote))
    application.add_handler(CallbackQueryHandler(button))  # Обработчик выбора кандидата
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_rating))  # Обработчик оценки
    application.add_handler(CommandHandler("my_votes", my_votes))  # Обработчик для команды /my_votes

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
