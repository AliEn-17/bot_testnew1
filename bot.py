import telebot
from telebot import types
import random

# --- КОНФИГУРАЦИЯ ---
BOT_TOKEN = 'ВАШ_ТОКЕН_ЗДЕСЬ'
# ID администратора (замените на ваш реальный ID для получения админских сообщений)
ADMIN_ID = 123456789 

bot = telebot.TeleBot(BOT_TOKEN)

# --- ДАННЫЕ ШКОЛЫ ---

SCHOOL_NAME = "Академия 'Питончики'"
SCHOOL_MOTTO = "Кодим будущее вместе!"

SCHEDULE = {
    "Понедельник": "10:00 - Python Базовый, 18:00 - HTML/CSS Практика",
    "Вторник": "14:00 - JavaScript Основы",
    "Среда": "10:00 - Python Продвинутый, 18:00 - Figma для Веба",
    "Четверг": "14:00 - Алгоритмы и Структуры Данных",
    "Пятница": "12:00 - QA Тестирование (Свободная практика)",
    "Суббота": "11:00 - English for IT",
    "Воскресенье": "Выходной! 🧘‍♂️",
}

# --- ИНТЕРФЕЙС (Требования 1 и 4) ---

def main_keyboard():
    """Главная клавиатура для студента."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Требование 2: Кнопка расписания
    btn1 = types.KeyboardButton("🗓️ Расписание уроков") 
    
    btn2 = types.KeyboardButton("📚 Мои курсы")
    btn3 = types.KeyboardButton("❓ Задать вопрос")
    btn4 = types.KeyboardButton("🌟 Совет дня")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    return markup

def schedule_inline_keyboard():
    """Инлайн-клавиатура для навигации по расписанию."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    days_order = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
    
    for day in days_order:
        buttons.append(types.InlineKeyboardButton(f"Расписание на {day[:3]}.", callback_data=f"schedule_{day}"))
        
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("Показать всё расписание", callback_data="schedule_all"))
    return markup

# --- ХЭНДЛЕРЫ КОМАНД ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Приветственное сообщение и инициализация."""
    user = message.from_user.first_name if message.from_user.first_name else "Студент"
    
    welcome_text = (
        f"🤖 **С возвращением в {SCHOOL_NAME}, {user}!** 🎉\n\n"
        f"Наш девиз: *{SCHOOL_MOTTO}*\n\n"
        "Я ваш личный помощник. Выберите нужный раздел в меню ниже:"
    )
    
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        parse_mode='Markdown', 
        reply_markup=main_keyboard()
    )

@bot.message_handler(commands=['admin_info'])
def send_admin_info(message):
    """Информация для администратора (только для ADMIN_ID)."""
    if message.from_user.id == ADMIN_ID:
        info_text = (
            "**🛠️ Панель Администратора**\n"
            "Вы можете использовать эту команду для получения системной информации "
            "или для рассылки уведомлений (если реализовано).\n"
            f"Текущий токен: `{BOT_TOKEN[:10]}...`\n"
            "Все запросы от студентов ('Задать вопрос') пересылаются вам."
        )
        bot.send_message(message.chat.id, info_text, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "Эй, это секретная команда! 😉")

# --- ХЭНДЛЕРЫ КНОПОК REPLY KEYBOARD ---

@bot.message_handler(func=lambda message: message.text == "🗓️ Расписание уроков")
def handle_schedule_start(message):
    """Обработка кнопки Расписание."""
    bot.send_message(
        message.chat.id, 
        "Отлично! На какой день вы хотите узнать расписание, или показать все?", 
        reply_markup=schedule_inline_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "📚 Мои курсы")
def handle_my_courses(message):
    """Демонстрация раздела Мои курсы."""
    text = (
        "Пока что эта функция в разработке, но скоро здесь появится:\n"
        "1. Ссылки на Zoom/Google Meet.\n"
        "2. Домашние задания.\n"
        "3. Материалы уроков.\n\n"
        "Не пропустите анонсы! 🚀"
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "❓ Задать вопрос")
def handle_question_request(message):
    """Запрос на связь с администратором."""
    msg = bot.send_message(
        message.chat.id, 
        "Напишите ваш вопрос или проблему. Я перешлю его администрации.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    # Переход в режим ожидания сообщения от пользователя
    bot.register_next_step_handler(msg, forward_question_to_admin)

def forward_question_to_admin(message):
    """Пересылка вопроса администратору."""
    if message.text:
        user_info = f"От: @{message.from_user.username} (ID: `{message.from_user.id}`)\n" if message.from_user.username else f"От: {message.from_user.first_name} (ID: `{message.from_user.id}`)\n"
        
        admin_message = (
            f"🚨 **НОВЫЙ ВОПРОС ОТ СТУДЕНТА** 🚨\n\n"
            f"{user_info}"
            f"**Вопрос:** {message.text}"
        )
        
        # Пересылка администратору
        bot.send_message(
            ADMIN_ID, 
            admin_message, 
            parse_mode='Markdown'
        )
        
        bot.send_message(
            message.chat.id, 
            "✅ Ваш вопрос передан администраторам! Ожидайте ответа.",
            reply_markup=main_keyboard()
        )
    else:
        # Если прислали не текст (фото, стикер и т.д.)
        bot.send_message(
            message.chat.id, 
            "Пожалуйста, сформулируйте свой вопрос текстом.",
            reply_markup=main_keyboard()
        )

@bot.message_handler(func=lambda message: message.text == "🌟 Совет дня")
def handle_tip_of_day(message):
    """Интересный совет для студентов (Требование: сделать бота интересным)."""
    tips = [
        "Не пытайтесь запомнить синтаксис, пытайтесь понять *логику*.",
        "Лучший способ учиться — это *учить* других.",
        "Каждый раз, когда вы сталкиваетесь с ошибкой, вы становитесь *лучше*.",
        "Пейте достаточно воды и делайте перерывы! Ваш мозг скажет вам спасибо. 🧠",
        "Создайте pet-проект! Начать что-то свое — это *самое* мотивирующее.",
        "Синхронность хороша для простоты, но асинхронность — это ключ к масштабу! 😉",
    ]
    bot.send_message(
        message.chat.id, 
        f"✨ **СОВЕТ ДНЯ:** {random.choice(tips)}",
        parse_mode='Markdown'
    )


# --- ХЭНДЛЕРЫ INLINE КНОПОК ---

@bot.callback_query_handler(func=lambda call: call.data.startswith('schedule_'))
def callback_schedule(call):
    """Обработка нажатия на инлайн-кнопки расписания."""
    day_key = call.data.replace('schedule_', '')
    response_text = ""
    
    if day_key == "all":
        response_text = "**Полное расписание Академии** 🗓️\n\n"
        for day, lesson in SCHEDULE.items():
            response_text += f"**{day}:** {lesson}\n"
        response_text += "\n*Успешного обучения!*"
        
        # Удаляем клавиатуру после показа всего расписания
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response_text,
            parse_mode='Markdown',
            reply_markup=None # Удаляем инлайн-клавиатуру
        )
    else:
        # Показываем расписание на конкретный день
        lesson = SCHEDULE.get(day_key, "Занятия не запланированы.")
        response_text = f"**Расписание на {day_key}:**\n{lesson}"
        
        # Обновляем сообщение, сохраняя клавиатуру для выбора других дней
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response_text,
            parse_mode='Markdown',
            reply_markup=schedule_inline_keyboard() 
        )
        
    bot.answer_callback_query(call.id)


# --- ЗАПУСК БОТА ---
if __name__ == '__main__':
    print(f"Бот {SCHOOL_NAME} запущен (синхронный polling).")
    try:
        # none_stop=True позволяет боту игнорировать ошибки и продолжать работу
        bot.polling(none_stop=True, interval=0) 
    except Exception as e:
        print(f"Критическая ошибка при запуске: {e}")
