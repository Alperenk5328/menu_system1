import sqlite3



# Veritabanına bağlan
connection = sqlite3.connect("instance/cafe.db")
cursor = connection.cursor()

# Veri ekleme
cursor.execute("INSERT INTO menu_item (name, price) VALUES (?, ?)", ("Kahve", 30))

# Değişiklikleri kaydet ve bağlantıyı kapat
connection.commit()
connection.close()

print("Veri başarıyla eklendi!")
