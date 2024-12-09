from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
app.config['SECRET_KEY'] = 'secret_key_here'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Ürün adı
    price = db.Column(db.Float, nullable=False)       # Ürün fiyatı

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)  # Masa numarası
    details = db.Column(db.Text, nullable=False)          # Sipariş detayları (JSON yerine açıklama)
    status = db.Column(db.String(50), nullable=False, default='Bekliyor')  # Sipariş durumu
    total_price = db.Column(db.Float, nullable=False, default=0.0)         # Toplam fiyat
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Sipariş oluşturma zamanı

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)  # Ürün adı
    quantity = db.Column(db.Integer, nullable=False)          # Ürün miktarı
    price = db.Column(db.Float, nullable=False)               # Birim fiyat
    total_price = db.Column(db.Float, nullable=False)         # Toplam fiyat (miktar * birim fiyat)

# ROUTES

@app.route('/')
def admin_login_page():
    return render_template('admin_login_page.html')

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

@app.route('/admin/home')
def admin_home():
    return render_template('admin_home.html')

@app.route('/manage_menu')
def manage_menu():
    menu_items = MenuItem.query.all()  # Tüm menü öğelerini al
    return render_template('manage_menu.html', menu_items=menu_items)

@app.route('/add_menu_item', methods=['POST'])
def add_menu_item():
    name = request.form.get('name')
    price = request.form.get('price')
    if not name or not price:
        flash('Ürün adı ve fiyatı zorunludur.', 'danger')
        return redirect(url_for('manage_menu'))
    new_item = MenuItem(name=name, price=float(price))
    db.session.add(new_item)
    db.session.commit()
    flash('Yeni ürün başarıyla eklendi!', 'success')
    return redirect(url_for('manage_menu'))

@app.route('/delete_menu_item/<int:item_id>')
def delete_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Ürün başarıyla silindi!', 'success')
    return redirect(url_for('manage_menu'))

@app.route('/manage_orders')
def manage_orders():
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template('manage_orders.html', orders=orders)

@app.route('/add_order', methods=['POST'])
def add_order():
    data = request.get_json()
    table_number = data.get('table_number')
    details = data.get('details')

    if not table_number or not details:
        return jsonify({"error": "Masa numarası ve sipariş detayları zorunludur."}), 400

    new_order = Order(
        table_number=table_number,
        details=details,
        status='Bekliyor'
    )
    db.session.add(new_order)
    db.session.commit()
    return jsonify({"message": "Sipariş başarıyla kaydedildi."}), 201

@app.route('/submit_order', methods=['POST', 'GET'])
def submit_order():
    if request.method == 'POST':
        data = request.get_json()
        ...
        return jsonify({'message': 'Sipariş başarıyla kaydedildi!'}), 201

    if request.method == 'GET':
        return "Lütfen bu endpoint için POST isteği gönderin.", 405
    data = request.get_json()
    table_number = data.get('table_number')
    cart = data.get('details')

    # Eksik veri kontrolü
    if not table_number or not cart:
        return jsonify({'message': 'Eksik bilgi! Masa numarası ve ürün bilgileri gerekli.'}), 400

    try:
        # Siparişi kaydet
        total_price = sum(item['price'] * item['quantity'] for item in cart)
        order = Order(
            table_number=table_number,
            details='OrderItem tablosunda detaylar saklanıyor.',
            status='Bekliyor',
            total_price=total_price
        )
        db.session.add(order)
        db.session.commit()

        # Sipariş ürünlerini kaydet
        for item in cart:
            order_item = OrderItem(
                order_id=order.id,
                product_name=item['name'],
                quantity=item['quantity'],
                price=item['price'],
                total_price=item['price'] * item['quantity']
            )
            db.session.add(order_item)

        db.session.commit()
        return jsonify({'message': 'Sipariş başarıyla kaydedildi!'}), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Veritabanına kaydedilirken hata oluştu: {e}")
        return jsonify({'message': f'Hata oluştu: {str(e)}'}), 500


@app.route('/complete_order/<int:order_id>')
def complete_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'Tamamlandı'
    db.session.commit()
    flash('Sipariş başarıyla tamamlandı!', 'success')
    return redirect(url_for('manage_orders'))

@app.route('/cancel_order/<int:order_id>')
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Sipariş başarıyla iptal edildi!', 'danger')
    return redirect(url_for('manage_orders'))

@app.route('/menu')
def menu():
    menu_items = MenuItem.query.all()
    return render_template('sicak-icecekler.html', menu_items=menu_items)

@app.route('/')
def index():
    return redirect(url_for('menu'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
