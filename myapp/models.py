from myapp import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=False)
    records = db.relationship("Record", back_populates="user", lazy="dynamic")
    income_account = db.relationship("IncomeAccount", back_populates="user", uselist=False, primaryjoin="User.id == IncomeAccount.user_id")

    def __repr__(self):
        return f'User {self.username}'
class IncomeAccount(db.Model):
    __tablename__ = "income_account"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    balance = db.Column(db.Float(precision=2), default=0.0, nullable=False)

    user = db.relationship("User", back_populates="income_account", uselist=False, primaryjoin="User.id == IncomeAccount.user_id")

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=False)
    record = db.relationship("Record", back_populates="category", lazy="dynamic")
class Record(db.Model):
    __tablename__ = "record"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=False, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float(precision=2), unique=False, nullable=False)

    user = db.relationship("User", back_populates="records")
    category = db.relationship("Category", back_populates="record")
