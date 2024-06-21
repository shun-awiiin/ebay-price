# models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    platform = db.Column(db.String(50), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    sale_amount = db.Column(db.Float, nullable=False)
    purchase_cost = db.Column(db.Float, nullable=False)
    shipping_cost = db.Column(db.Float, nullable=False)
    profit = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Transaction {self.id} {self.product_name}>'