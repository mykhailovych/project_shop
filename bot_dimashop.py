import os
import sqlite3
import logging
from decimal import Decimal

import telebot
from telebot import types
from dotenv import load_dotenv

# ----------------- Завантаження .env -----------------
load_dotenv()

import sys
try:
    # Ensure stdout/stderr use UTF-8 on Windows to allow emoji in prints/logs
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

BOT_TOKEN = os.getenv("BOT_TOKEN")
PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID") or 0)

if not BOT_TOKEN:
    raise SystemExit("❌ BOT_TOKEN не знайдено у .env")

bot = telebot.TeleBot(BOT_TOKEN)
logging.basicConfig(level=logging.INFO)

DB = os.path.join(os.path.dirname(__file__), "dimashop.db")

# ----------------- Ініціалізація бази -----------------
def init_db():
    """Створює локальну базу `dimashop.db` з усіма необхідними таблицями."""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Таблиця товарів
    cur.execute('''
    CREATE TABLE IF NOT EXISTS clothes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        name TEXT,
        price REAL,
        image TEXT
    )
    ''')

    # Таблиця кошика
    cur.execute('''
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        product_name TEXT,
        size TEXT,
        price REAL
    )
    ''')

    # Таблиця замовлень (з полями для доставки)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        items TEXT,
        total REAL,
        tg_payment_id TEXT,
        status TEXT,
        city TEXT,
        nova_poshta_branch TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()


init_db()

# ----------------- Допоміжні функції -----------------
def get_products(category):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('''
        SELECT name, price, GROUP_CONCAT(image, '|') AS images
        FROM clothes
        WHERE category=?
        GROUP BY name, price
    ''', (category,))
    products = cur.fetchall()
    conn.close()
    return products

user_positions = {}
user_current_category = {}
user_last_messages = {}  # Зберігаємо ID останніх повідомлень для видалення

# ----------------- Функція видалення попередніх повідомлень -----------------
def delete_previous_messages(user_id):
    """Видаляє попередні повідомлення користувача"""
    if user_id in user_last_messages:
        for msg_id in user_last_messages[user_id]:
            try:
                bot.delete_message(user_id, msg_id)
            except:
                pass  # Ігноруємо помилки видалення
        user_last_messages[user_id] = []

# ----------------- Головне меню -----------------
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("👕 Одяг"),
        types.KeyboardButton("👟 Взуття"),
        types.KeyboardButton("🧢 Аксесуари"),
        types.KeyboardButton("🛒 Кошик")
    )
    bot.send_message(message.chat.id, "👋 Вітаю у *DimaShop*! Оберіть категорію:", parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['myid'])
def get_my_id(message):
    bot.send_message(message.chat.id, f"🆔 Ваш Telegram ID: `{message.chat.id}`", parse_mode='Markdown')

# ----------------- Показ підкатегорій -----------------
@bot.message_handler(func=lambda m: m.text in ["👕 Одяг", "👟 Взуття", "🧢 Аксесуари"])
def show_subcategories(message):
    if message.text == "👕 Одяг":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            types.KeyboardButton("👚 Футболки"),
            types.KeyboardButton("🧥 Куртки"),
            types.KeyboardButton("👖 Штани"),
            types.KeyboardButton("🔙 Назад")
        )
        bot.send_message(message.chat.id, "👕 *Одяг* - оберіть підкатегорію:", parse_mode='Markdown', reply_markup=markup)
        
    elif message.text == "👟 Взуття":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            types.KeyboardButton("👟 Кросівки"),
            types.KeyboardButton("🔙 Назад")
        )
        bot.send_message(message.chat.id, "👟 *Взуття* - оберіть підкатегорію:", parse_mode='Markdown', reply_markup=markup)
        
    elif message.text == "🧢 Аксесуари":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            types.KeyboardButton("🧢 Кепки"),
            types.KeyboardButton("👓 Окуляри"),
            types.KeyboardButton("🔙 Назад")
        )
        bot.send_message(message.chat.id, "🧢 *Аксесуари* - оберіть підкатегорію:", parse_mode='Markdown', reply_markup=markup)

# ----------------- Показ товарів з підкатегорій -----------------
@bot.message_handler(func=lambda m: m.text in ["👚 Футболки", "🧥 Куртки", "👖 Штани", "👟 Кросівки", "🧢 Кепки", "👓 Окуляри"])
def show_products_from_subcategory(message):
    category_map = {
        "👚 Футболки": "Футболки",
        "🧥 Куртки": "Куртки",
        "👖 Штани": "Штани",
        "👟 Кросівки": "Кросівки",
        "🧢 Кепки": "Кепки",
        "👓 Окуляри": "Окуляри"
    }
    category = category_map[message.text]
    user_positions[message.chat.id] = 0
    user_current_category[message.chat.id] = category
    show_product(message.chat.id, category)

# ----------------- Повернення до головного меню -----------------
@bot.message_handler(func=lambda m: m.text == "🔙 Назад")
def back_to_main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("👕 Одяг"),
        types.KeyboardButton("👟 Взуття"),
        types.KeyboardButton("🧢 Аксесуари"),
        types.KeyboardButton("🛒 Кошик")
    )
    bot.send_message(message.chat.id, "👋 Вітаю у *DimaShop*! Оберіть категорію:", parse_mode='Markdown', reply_markup=markup)

def show_product(user_id, category):
    # Видаляємо попередні повідомлення
    delete_previous_messages(user_id)
    
    products = get_products(category)
    if not products:
        msg = bot.send_message(user_id, f"❌ Немає товарів у категорії {category}.")
        user_last_messages[user_id] = [msg.message_id]
        return

    index = user_positions.get(user_id, 0)
    name, price, images_str = products[index]
    images = images_str.split('|')

    caption = f"🛍 <b>{name}</b>\n💰 Ціна: {price} грн\n\n{index+1}/{len(products)}"
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("⬅️ Назад", callback_data="prev"),
        types.InlineKeyboardButton("🛒 У кошик", callback_data=f"add_{index}"),
        types.InlineKeyboardButton("➡️ Далі", callback_data="next")
    )

    # Зберігаємо ID повідомлень для подальшого видалення
    message_ids = []
    
    # надсилаємо як колаж
    media = [types.InputMediaPhoto(img) for img in images]
    media_messages = bot.send_media_group(user_id, media)
    for msg in media_messages:
        message_ids.append(msg.message_id)
    
    # Відправляємо повідомлення з кнопками
    msg = bot.send_message(user_id, caption, parse_mode='html', reply_markup=markup)
    message_ids.append(msg.message_id)
    
    # Зберігаємо ID всіх повідомлень
    user_last_messages[user_id] = message_ids

# ----------------- Кнопки гортання і додавання -----------------
@bot.callback_query_handler(func=lambda call: call.data in ["next", "prev"] or call.data.startswith("add_"))
def callback_handler(call):
    user_id = call.message.chat.id
    category = user_current_category.get(user_id, "Футболки")
    products = get_products(category)

    if not products:
        bot.answer_callback_query(call.id, "Немає товарів.")
        return

    if call.data == "next":
        current_pos = user_positions.get(user_id, 0)
        user_positions[user_id] = (current_pos + 1) % len(products)
        show_product(user_id, category)
        bot.answer_callback_query(call.id, "➡️ Наступний товар")
    elif call.data == "prev":
        current_pos = user_positions.get(user_id, 0)
        user_positions[user_id] = (current_pos - 1) % len(products)
        show_product(user_id, category)
        bot.answer_callback_query(call.id, "⬅️ Попередній товар")
    elif call.data.startswith("add_"):
        index = int(call.data.split("_")[1])
        name, price, _ = products[index]
        bot.answer_callback_query(call.id, f"✅ {name} додано до кошика")
        msg = bot.send_message(user_id, f"Оберіть розмір для {name} (наприклад: S, M, L, XL або 42, 43):")
        bot.register_next_step_handler(msg, save_size_and_add_to_cart, name, price)

# ----------------- Додавання у кошик -----------------
def save_size_and_add_to_cart(message, name, price):
    size = message.text.strip().upper()
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO cart (user_id, product_id, product_name, size, price) VALUES (?, ?, ?, ?, ?)",
                (message.chat.id, 0, name, size, price))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"✅ {name} (розмір {size}) додано у кошик 🛒")


# ----------------- Кошик -----------------
@bot.message_handler(func=lambda m: m.text == "🛒 Кошик")
def show_cart(message):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT product_name, size, price FROM cart WHERE user_id=?", (message.chat.id,))
    items = cur.fetchall()
    conn.close()

    if not items:
        bot.send_message(message.chat.id, "🛒 Ваш кошик порожній.")
        return

    total = sum(i[2] for i in items)
    text = "🧾 <b>Ваш кошик:</b>\n\n"
    for name, size, price in items:
        text += f"👕 {name} — {size} — {price} грн\n"
    text += f"\n💰 <b>Разом:</b> {total} грн"

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Оплатити", callback_data="pay"),
        types.InlineKeyboardButton("🗑 Очистити кошик", callback_data="clear_cart")
    )
    bot.send_message(message.chat.id, text, parse_mode='html', reply_markup=markup)

# ----------------- Очистка кошика -----------------
@bot.callback_query_handler(func=lambda c: c.data == "clear_cart")
def clear_cart(call):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("DELETE FROM cart WHERE user_id=?", (call.message.chat.id,))
    conn.commit()
    conn.close()
    bot.edit_message_text("🗑 Кошик очищено!", call.message.chat.id, call.message.message_id)

# ----------------- Оплата -----------------
@bot.callback_query_handler(func=lambda c: c.data == "pay")
def pay(call):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT product_name, size, price FROM cart WHERE user_id=?", (call.message.chat.id,))
    items = cur.fetchall()
    conn.close()

    if not items:
        bot.answer_callback_query(call.id, "Кошик порожній.")
        return

    total = sum(i[2] for i in items)
    prices = [types.LabeledPrice(label="Замовлення в DimaShop", amount=int(Decimal(total) * 100))]

    if not PROVIDER_TOKEN:
        bot.answer_callback_query(call.id, "⚠️ Оплата недоступна: немає PROVIDER_TOKEN")
        return

    bot.send_invoice(
        call.message.chat.id,
        title="Оплата замовлення",
        description="Ваше замовлення у DimaShop",
        provider_token=PROVIDER_TOKEN,
        currency="UAH",
        prices=prices,
        start_parameter="dima-shop",
        invoice_payload=f"order_{call.message.chat.id}"
    )

@bot.pre_checkout_query_handler(func=lambda q: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    user_id = message.chat.id
    payment = message.successful_payment
    tg_payment_id = payment.telegram_payment_charge_id

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT product_name, size, price FROM cart WHERE user_id=?", (user_id,))
    items = cur.fetchall()
    total = sum(i[2] for i in items)
    items_text = "\n".join([f"{n} ({s}) - {p} грн" for n, s, p in items])

    # Зберігаємо замовлення без даних доставки (поки що)
    cur.execute("INSERT INTO orders (user_id, items, total, tg_payment_id, status) VALUES (?, ?, ?, ?, ?)",
                (user_id, items_text, total, tg_payment_id, "PAID"))
    conn.commit()
    conn.close()

    # Запитуємо дані для доставки
    bot.send_message(user_id, 
        f"✅ Оплата успішна!\n\n"
        f"Ваше замовлення:\n{items_text}\n💰 Разом: {total} грн\n\n"
        f"📦 Для доставки вкажіть місто та номер відділення Нової Пошти:\n\n"
        f"Наприклад: `Київ, 1` або `Львів, 15`", 
        parse_mode='Markdown')
    
    # Реєструємо обробник для збору даних доставки
    bot.register_next_step_handler(message, collect_delivery_info, user_id, items_text, total, tg_payment_id)

def collect_delivery_info(message, user_id, items_text, total, tg_payment_id):
    try:
        delivery_text = message.text.strip()
        
        # Парсимо місто та номер відділення
        if ',' in delivery_text:
            city, branch = delivery_text.split(',', 1)
            city = city.strip()
            branch = branch.strip()
        else:
            # Якщо немає коми, спробуємо розділити по пробілах
            parts = delivery_text.split()
            if len(parts) >= 2:
                city = ' '.join(parts[:-1])
                branch = parts[-1]
            else:
                raise ValueError("Неправильний формат")
        
        # Оновлюємо замовлення з даними доставки
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("""
            UPDATE orders 
            SET city = ?, nova_poshta_branch = ? 
            WHERE user_id = ? AND tg_payment_id = ?
        """, (city, branch, user_id, tg_payment_id))
        conn.commit()
        conn.close()
        
        # Очищаємо кошик
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("DELETE FROM cart WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()
        
        bot.send_message(user_id, 
            f"✅ Дані доставки збережено!\n\n"
            f"🏙 Місто: {city}\n"
            f"🏢 Відділення Нової Пошти: {branch}\n\n"
            f"📦 Ваше замовлення буде відправлено найближчим часом!")
        
        # Повідомляємо адміна
        if ADMIN_ID:
            bot.send_message(ADMIN_ID, 
                f"🆕 Нове замовлення від {user_id}\n"
                f"📦 Товари:\n{items_text}\n"
                f"💰 Разом: {total} грн\n"
                f"🏙 Місто: {city}\n"
                f"🏢 НП: {branch}")
        
    except Exception as e:
        bot.send_message(user_id, 
            f"❌ Помилка при обробці даних доставки: {str(e)}\n\n"
            f"Спробуйте ще раз у форматі: `Місто, Номер`\n"
            f"Наприклад: `Київ, 1`", 
            parse_mode='Markdown')
        # Повторно реєструємо обробник
        bot.register_next_step_handler(message, collect_delivery_info, user_id, items_text, total, tg_payment_id)

# ----------------- АДМІН-ПАНЕЛЬ -----------------
def is_admin(user_id):
    """Перевіряє, чи є користувач адміністратором"""
    # Тут вкажіть ваш Telegram ID
    admin_ids = [708739024]  # Замініть на ваш ID
    return user_id in admin_ids

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not is_admin(message.chat.id):
        bot.send_message(message.chat.id, "❌ У вас немає прав доступу до адмін-панелі.")
        return
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("➕ Додати товар", callback_data="admin_add_product"),
        types.InlineKeyboardButton("📝 Редагувати товар", callback_data="admin_edit_product"),
        types.InlineKeyboardButton("🗑 Видалити товар", callback_data="admin_delete_product"),
        types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")
    )
    bot.send_message(message.chat.id, "🔧 *Адмін-панель DimaShop*", parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_callback_handler(call):
    if not is_admin(call.message.chat.id):
        bot.answer_callback_query(call.id, "❌ Немає прав доступу")
        return
    
    if call.data == "admin_add_product":
        bot.answer_callback_query(call.id, "Додавання товару")
        msg = bot.send_message(call.message.chat.id, 
            "📝 *Додавання нового товару*\n\n"
            "Відправте дані у форматі:\n"
            "`Категорія|Назва|Ціна|URL_фото`\n\n"
            "Приклад:\n"
            "`Футболки|Nike Air Max|1500|https://example.com/photo.jpg`", 
            parse_mode='Markdown')
        bot.register_next_step_handler(msg, add_product_handler)
    
    elif call.data == "admin_stats":
        bot.answer_callback_query(call.id, "Статистика")
        show_admin_stats(call.message.chat.id)
    
    elif call.data == "admin_edit_product":
        bot.answer_callback_query(call.id, "Редагування товару")
        bot.send_message(call.message.chat.id, "🔄 Функція редагування в розробці")
    
    elif call.data == "admin_delete_product":
        bot.answer_callback_query(call.id, "Видалення товару")
        bot.send_message(call.message.chat.id, "🗑 Функція видалення в розробці")

def add_product_handler(message):
    try:
        data = message.text.split('|')
        if len(data) != 4:
            bot.send_message(message.chat.id, "❌ Неправильний формат. Використовуйте: Категорія|Назва|Ціна|URL_фото")
            return
        
        category, name, price_str, image_url = data
        price = float(price_str)
        
        # Додаємо товар до бази даних
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("INSERT INTO clothes (category, name, price, image) VALUES (?, ?, ?, ?)",
                   (category.strip(), name.strip(), price, image_url.strip()))
        conn.commit()
        conn.close()
        
        bot.send_message(message.chat.id, 
            f"✅ Товар успішно додано!\n\n"
            f"📂 Категорія: {category}\n"
            f"📝 Назва: {name}\n"
            f"💰 Ціна: {price} грн\n"
            f"🖼 Фото: {image_url}")
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Помилка: ціна повинна бути числом")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Помилка при додаванні товару: {str(e)}")

def show_admin_stats(chat_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    # Загальна статистика
    cur.execute("SELECT COUNT(*) FROM clothes")
    total_products = cur.fetchone()[0]
    
    # Статистика по категоріях
    cur.execute("SELECT category, COUNT(*) FROM clothes GROUP BY category")
    categories = cur.fetchall()
    
    # Статистика замовлень
    cur.execute("SELECT COUNT(*) FROM orders")
    total_orders = cur.fetchone()[0]
    
    # Статистика кошиків
    cur.execute("SELECT COUNT(*) FROM cart")
    total_carts = cur.fetchone()[0]
    
    # Останні замовлення з доставкою
    cur.execute("""
        SELECT user_id, items, total, city, nova_poshta_branch, created_at 
        FROM orders 
        WHERE city IS NOT NULL 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    recent_orders = cur.fetchall()
    
    conn.close()
    
    stats_text = f"📊 *Статистика DimaShop*\n\n"
    stats_text += f"📦 Всього товарів: {total_products}\n"
    stats_text += f"🛒 Активних кошиків: {total_carts}\n"
    stats_text += f"✅ Замовлень: {total_orders}\n\n"
    stats_text += f"📂 *Товари по категоріях:*\n"
    
    for category, count in categories:
        stats_text += f"• {category}: {count} товарів\n"
    
    if recent_orders:
        stats_text += f"\n📦 *Останні замовлення з доставкою:*\n"
        for order in recent_orders:
            user_id, items, total, city, branch, created_at = order
            stats_text += f"• ID {user_id}: {city}, НП {branch} - {total} грн\n"
    
    bot.send_message(chat_id, stats_text, parse_mode='Markdown')

# ----------------- Запуск -----------------
if __name__ == "__main__":
    print("✅ Бот DimaShop запущений!")
    bot.infinity_polling(timeout=60, long_polling_timeout=5)
