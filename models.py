from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)  # Masa numarası
    details = db.Column(db.Text, nullable=False)  # Sipariş detayları (JSON formatında saklanır)
    status = db.Column(db.String(50), nullable=False, default='Bekliyor')  # Sipariş durumu (Bekliyor, Tamamlandı)
