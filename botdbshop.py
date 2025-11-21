import sqlite3

# === Підключення до нової бази ===
conn = sqlite3.connect('dimashop.db')
c = conn.cursor()

# === Таблиця товарів ===
c.execute('''
CREATE TABLE IF NOT EXISTS clothes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    name TEXT,
    price REAL,
    image TEXT
)
''')

# === Таблиця кошика ===
c.execute('''
CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_id INTEGER,
    product_name TEXT,
    size TEXT,
    price REAL
)
''')

# === Таблиця замовлень ===
c.execute('''
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

# === Очищення товарів (якщо були старі) ===
c.execute("DELETE FROM clothes")

# === Додавання початкових товарів ===
data = [
    # === ФУТБОЛКИ ===
    ('Футболки', 'Футболка чоловіча Nike T-Shirt Nsw Prem Essntl Sust Tee Black', 1700.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/5e/d3/de/55900-3213532-1340x1410_-jpg-84.webp'),
    ('Футболки', 'Футболка чоловіча Nike T-Shirt Nsw Prem Essntl Sust Tee Black', 1700.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/cd/7d/7d/55900-3213533-1340x1410_-jpg-84.webp'),
    ('Футболки', 'Футболка чоловіча Nike T-Shirt Nsw Prem Essntl Sust Tee Black', 1700.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/74/73/95/55900-0-1340x1410_-jpg-84.webp'),

    ('Футболки', 'Футболка чоловіча Air Jordan T-Shirt Jumpman Flight Black', 1300.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/b0/f2/6d/90163436-0-1340x1410_-jpg-84.webp'),
    ('Футболки', 'Футболка чоловіча Air Jordan T-Shirt Jumpman Flight Black', 1300.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/68/89/a2/90163436-2711959-1340x1410_-jpg-84.webp'),
    ('Футболки', 'Футболка чоловіча Air Jordan T-Shirt Jumpman Flight Black', 1300.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/8c/ac/ac/90163436-2711960-1340x1410_-jpg-84.webp'),

    # === КУРТКИ ===
    ('Куртки', 'Пуховик чоловічий Nike Sportswear Club Black', 8700.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/1c/0e/1e/90095611-0-1340x1410_-jpg-84.webp'),
    ('Куртки', 'Пуховик чоловічий Nike Sportswear Club Black', 8700.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/db/1f/74/90095611-3197617-1340x1410_-jpg-84.webp'),
    ('Куртки', 'Пуховик чоловічий Nike Sportswear Club Black', 8700.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/64/d9/63/90095611-3197621-1340x1410_-jpg-84.webp'),

    ('Куртки', 'Пуховик чоловічий Air Jordan Brooklyn Black', 8700.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/da/fb/02/90228685-0-1340x1410_-jpg-84.webp'),
    ('Куртки', 'Пуховик чоловічий Air Jordan Brooklyn Black', 8700.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/f9/08/0d/90228685-3123388-1340x1410_-jpg-84.webp'),
    ('Куртки', 'Пуховик чоловічий Air Jordan Brooklyn Black', 8700.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/5e/bc/48/90228685-3123392-1340x1410_-jpg-84.webp'),

    # === ШТАНИ ===
    ('Штани', 'Штани чоловічі Gap Logo Fleece Pants Tapestry Navy', 1500.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/61/21/06/76100034-0-1340x1410_-jpg-84.webp'),
    ('Штани', 'Штани чоловічі Gap Logo Fleece Pants Tapestry Navy', 1500.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/f9/55/76/76100034-3184141-1340x1410_-jpg-84.webp'),
    ('Штани', 'Штани чоловічі Gap Logo Fleece Pants Tapestry Navy', 1500.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/54/7a/40/76100034-3184139-1340x1410_-jpg-84.webp'),

    ('Штани', 'Штани чоловічі Nike Sportswear Tech Fleece Black', 4500.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/22/29/0e/90095627-0-1340x1410_-jpg-84.webp'),
    ('Штани', 'Штани чоловічі Nike Sportswear Tech Fleece Black', 4500.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/48/25/06/90095627-3180291-1340x1410_-jpg-84.webp'),
    ('Штани', 'Штани чоловічі Nike Sportswear Tech Fleece Black', 4500.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/de/d9/25/90095627-3180294-1340x1410_-jpg-84.webp'),

    # === КРОСІВКИ ===
    ('Кросівки', 'Кросівки унісекс New Balance 9060 Grey U9060Blk', 7000.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/7e/fe/7d/76507-0-1340x1410_-jpg-84.webp'),
    ('Кросівки', 'Кросівки унісекс New Balance 9060 Grey U9060Blk', 7000.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/ba/26/13/76507-3217764-1340x1410_-jpg-84.webp'),

    ('Кросівки', 'Кросівки чоловічі Nike Dunk Low Retro Black/White', 4000.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/d8/d0/c9/47075-0-1340x1410_-jpg-84.webp'),
    ('Кросівки', 'Кросівки чоловічі Nike Dunk Low Retro Black/White', 4000.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/30/1e/ad/47075-3216546-1340x1410_-jpg-84.webp'),
    ('Кросівки', 'Кросівки чоловічі Nike Dunk Low Retro Black/White', 4000.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/6a/62/ed/47075-3216549-1340x1410_-jpg-84.webp'),

    # === КЕПКИ ===
    ('Кепки', 'Кепка унісекс Nike Df Club Cap U Cb Maxtn', 1090.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/de/9f/b8/90165937-0-1340x1410_-jpg-84.webp'),
    ('Кепки', 'Кепка унісекс Nike Df Club Cap U Cb Maxtn', 1090.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/51/9d/d1/90165937-3214477-1340x1410_-jpg-84.webp'),
    ('Кепки', 'Кепка унісекс Nike Df Club Cap U Cb Maxtn', 1090.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/a9/b9/cc/90165937-3214480-1340x1410_-jpg-84.webp'),
    ('Кепки', 'Кепка чоловіча Air Jordan RiseStructured Metal Jumpman Hat Black', 1690.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/a4/33/13/90236531-0-1340x1410_-jpg-84.webp'),
    ('Кепки', 'Кепка чоловіча Air Jordan RiseStructured Metal Jumpman Hat Black', 1690.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/fd/52/ae/90236531-3214978-1340x1410_-jpg-84.webp'),
    ('Кепки', 'Кепка чоловіча Air Jordan RiseStructured Metal Jumpman Hat Black', 1690.0, 'https://yesoriginal.com.ua/media/cache/catalog/products/dd/36/71/90236531-3214980-1340x1410_-jpg-84.webp'),
    
    # === ОКУЛЯРИ ===
    ('Окуляри', 'Сонцезахисні окуляри Ray-Ban Scuderia Ferrari Collection', 8700.0, 'https://www.rb.ua/getimg.php?file=raybans/Ray-Ban-Scuderia-Ferrari-Collection-RB4363M-F659-87.jpg&w=600'),
    ('Окуляри', 'Сонцезахисні окуляри Ray-Ban Scuderia Ferrari Collection', 8700.0, 'https://www.rb.ua/getimg.php?file=raybans/Ray-Ban-Scuderia-Ferrari-Collection-RB4363M-F659-87-2.jpg&w=600'),
    ('Окуляри', 'Сонцезахисні окуляри Ray-Ban Scuderia Ferrari Collection', 8700.0, 'https://www.rb.ua/getimg.php?file=raybans/Ray-Ban-Scuderia-Ferrari-Collection-RB4363M-F659-87-1.jpg&w=600'),
    
    ('Окуляри', 'Окуляри віртуальної реальності XREAL One Pro', 31999.0, 'https://img.jabko.ua/image/cache/catalog/products/2025/10/070940/1-1397x1397.jpg.webp'),
    ('Окуляри', 'Окуляри віртуальної реальності XREAL One Pro', 31999.0, 'https://img.jabko.ua/image/cache/catalog/products/2025/10/070940/2-1397x1397.jpg.webp'),
    ('Окуляри', 'Окуляри віртуальної реальності XREAL One Pro', 31999.0, 'https://img.jabko.ua/image/cache/catalog/products/2025/10/070941/9-1397x1397.jpg.webp')
]

c.executemany("INSERT INTO clothes (category, name, price, image) VALUES (?, ?, ?, ?)", data)
conn.commit()
conn.close()

print("✅ База даних dimashop.db створена і заповнена успішно!")
