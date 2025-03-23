import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, Response
import sqlite3
from datetime import datetime
import json
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Veritabanı bağlantısı
def get_db():
    db = sqlite3.connect('restaurant.db')
    db.row_factory = sqlite3.Row
    return db

# Veritabanı tablolarını oluştur
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    
    # Test için örnek masalar ekle
    db.execute('INSERT OR IGNORE INTO completed_orders (table_number, details, total_price, completed_at) VALUES (?, ?, ?, ?)',
              [1, '[]', 0.0, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    db.execute('INSERT OR IGNORE INTO completed_orders (table_number, details, total_price, completed_at) VALUES (?, ?, ?, ?)',
              [2, '[]', 0.0, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    db.execute('INSERT OR IGNORE INTO completed_orders (table_number, details, total_price, completed_at) VALUES (?, ?, ?, ?)',
              [3, '[]', 0.0, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    
    db.commit()

@app.route('/')
def index():
    return redirect(url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'mcstone' and password == 'thekiller':
            flash('Başarıyla giriş yapıldı!', 'success')
            return redirect(url_for('admin_home'))
        else:
            flash('Kullanıcı adı veya şifre yanlış!', 'danger')
    return render_template('admin_login_page.html')

@app.route('/menu')
def show_menu():
    db = get_db()
    menus = db.execute('SELECT * FROM menus').fetchall()
    return render_template('index.html', menus=menus)

@app.route('/admin/home')
def admin_home():
    return render_template('admin_home.html')

@app.route('/manage_menu', methods=['GET'])
def manage_menu():
    db = get_db()
    filter_menu_id = request.args.get('filter_menu_id')
    
    if filter_menu_id:
        menu_items = db.execute('SELECT * FROM menu_items WHERE menu_id = ?', [filter_menu_id]).fetchall()
    else:
        menu_items = db.execute('SELECT * FROM menu_items').fetchall()
    
    menus = db.execute('SELECT * FROM menus').fetchall()
    return render_template('manage_menu.html', menu_items=menu_items, menus=menus)

@app.route('/manage_orders')
def manage_orders():
    db = get_db()
    orders = db.execute('SELECT * FROM orders ORDER BY created_at DESC').fetchall()
    return render_template('manage_orders.html', orders=orders)

@app.route('/submit_order', methods=['POST'])
def submit_order():
    try:
        data = request.get_json()
        table_number = data['table_number']
        items = data['items']
        
        db = get_db()
        db.execute(
            'INSERT INTO orders (table_number, details, status) VALUES (?, ?, ?)',
            [table_number, json.dumps(items), 'Bekliyor']
        )
        db.commit()
        
        # Son eklenen siparişin ID'sini al
        order_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        order = db.execute('SELECT * FROM orders WHERE id = ?', [order_id]).fetchone()
        
        # Yeni sipariş bildirimi gönder
        socketio.emit('new_order', {
            'id': order_id,
            'table_number': table_number,
            'details': items,
            'status': 'Bekliyor'
        })
        
        return jsonify({'success': True, 'message': 'Sipariş alındı'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/complete_order/<int:order_id>')
def complete_order(order_id):
    try:
        db = get_db()
        order = db.execute('SELECT * FROM orders WHERE id = ?', [order_id]).fetchone()
        
        if not order:
            flash('Sipariş bulunamadı!', 'error')
            return redirect(url_for('manage_orders'))
        
        details = json.loads(order['details'])
        total_price = sum(item['price'] * item['quantity'] for item in details)
        
        # Tamamlanan siparişler tablosuna ekle
        db.execute('''
            INSERT INTO completed_orders (table_number, details, total_price, completed_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', [order['table_number'], order['details'], total_price])
        
        # Mevcut siparişi güncelle
        db.execute('UPDATE orders SET status = ? WHERE id = ?', ['Tamamlandı', order_id])
        db.commit()
        
        # Sipariş durumu güncellemesi gönder
        socketio.emit('order_status_update', {
            'order_id': order_id,
            'status': 'Tamamlandı',
            'action': 'complete'
        })
        
        flash('Sipariş başarıyla tamamlandı!', 'success')
    except Exception as e:
        flash(f'Hata oluştu: {str(e)}', 'error')
    
    return redirect(url_for('manage_orders'))

@app.route('/cancel_order/<int:order_id>')
def cancel_order(order_id):
    try:
        db = get_db()
        db.execute('UPDATE orders SET status = ? WHERE id = ?', ['İptal', order_id])
        db.commit()
        
        # Sipariş durumu güncellemesi gönder
        socketio.emit('order_status_update', {
            'order_id': order_id,
            'status': 'İptal',
            'action': 'cancel'
        })
        
        flash('Sipariş başarıyla iptal edildi!', 'success')
    except Exception as e:
        flash(f'Hata oluştu: {str(e)}', 'error')
    
    return redirect(url_for('manage_orders'))

@app.route('/sicak-icecekler')
def sicak_icecekler():
    db = get_db()
    menu_items = db.execute('''
        SELECT mi.* FROM menu_items mi
        JOIN menus m ON mi.menu_id = m.id
        WHERE m.name = 'Sıcak İçecekler'
    ''').fetchall()
    return render_template('sicak-icecekler.html', menu_items=menu_items)

@app.route('/initialize_menus')
def initialize_menus():
    db = get_db()
    menus = ["Sıcak İçecekler", "Soğuk İçecekler", "Tatlılar"]
    for menu_name in menus:
        db.execute('INSERT OR IGNORE INTO menus (name) VALUES (?)', [menu_name])
    db.commit()
    return "Menüler başarıyla oluşturuldu!"

@app.route('/add_menu_item', methods=['POST'])
def add_menu_item():
    try:
        name = request.form['name']
        price = float(request.form['price'])
        menu_id = int(request.form['menu_id'])
        description = request.form.get('description', '')

        db = get_db()
        db.execute(
            'INSERT INTO menu_items (name, price, description, menu_id) VALUES (?, ?, ?, ?)',
            [name, price, description, menu_id]
        )
        db.commit()
        flash('Ürün başarıyla eklendi!', 'success')
    except Exception as e:
        flash(f'Hata oluştu: {str(e)}', 'error')

    return redirect(url_for('manage_menu'))

@app.route('/edit_menu_item/<int:item_id>', methods=['GET', 'POST'])
def edit_menu_item(item_id):
    db = get_db()
    
    if request.method == 'POST':
        try:
            name = request.form['name']
            price = float(request.form['price'])
            menu_id = int(request.form['menu_id'])
            description = request.form.get('description', '')

            db.execute(
                'UPDATE menu_items SET name = ?, price = ?, description = ?, menu_id = ? WHERE id = ?',
                [name, price, description, menu_id, item_id]
            )
            db.commit()
            flash('Ürün başarıyla güncellendi!', 'success')
            return redirect(url_for('manage_menu'))
        except Exception as e:
            flash(f'Hata oluştu: {str(e)}', 'error')
    
    item = db.execute('SELECT * FROM menu_items WHERE id = ?', [item_id]).fetchone()
    if not item:
        flash('Ürün bulunamadı!', 'error')
        return redirect(url_for('manage_menu'))
    
    menus = db.execute('SELECT * FROM menus').fetchall()
    return render_template('edit_menu_item.html', item=item, menus=menus)

@app.route('/delete_menu_item/<int:item_id>')
def delete_menu_item(item_id):
    try:
        db = get_db()
        db.execute('DELETE FROM menu_items WHERE id = ?', [item_id])
        db.commit()
        flash('Ürün başarıyla silindi!', 'success')
    except Exception as e:
        flash(f'Hata oluştu: {str(e)}', 'error')
    
    return redirect(url_for('manage_menu'))

@app.route('/manage_tables')
def manage_tables():
    db = get_db()
    # Tamamlanmış siparişlerden benzersiz masa numaralarını al
    tables = db.execute('''
        SELECT DISTINCT table_number, 
        (SELECT COUNT(*) FROM orders WHERE table_number = co.table_number AND status != 'İptal') as active_orders
        FROM completed_orders co
        ORDER BY table_number
    ''').fetchall()
    return render_template('manage_tables.html', tables=tables)

@app.route('/generate_qr/<int:table_number>')
def generate_qr(table_number):
    import qrcode
    import qrcode.image.svg

    # QR kodun içeriği - menü URL'si ve masa numarası
    url = f"http://127.0.0.1:5000/?table={table_number}"
    
    # QR kod oluştur
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # QR kodu SVG olarak oluştur
    factory = qrcode.image.svg.SvgImage
    img = qr.make_image(image_factory=factory)
    
    # SVG içeriğini string olarak al
    svg_string = img.to_string()
    
    return Response(svg_string, mimetype='image/svg+xml')

if __name__ == '__main__':
    init_db()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)