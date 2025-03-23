-- Menüler tablosu
CREATE TABLE IF NOT EXISTS menus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);

-- Menü öğeleri tablosu
CREATE TABLE IF NOT EXISTS menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT,
    menu_id INTEGER,
    FOREIGN KEY (menu_id) REFERENCES menus (id)
);

-- Aktif siparişler tablosu
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_number INTEGER NOT NULL,
    details TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tamamlanan siparişler tablosu
CREATE TABLE IF NOT EXISTS completed_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_number INTEGER NOT NULL,
    details TEXT NOT NULL,
    total_price REAL NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
