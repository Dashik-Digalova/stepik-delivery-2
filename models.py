from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    mail = db.Column(db.String, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    orders = db.relationship("Order", back_populates="user")

    @hybrid_property
    def password_hash(self):
        # Запретим прямое обращение к паролю
        raise AttributeError("Вам не нужно знать пароль!")

    @password_hash.setter
    def password_hash(self, password):
        # Устанавливаем пароль через этот метод
        self._password_hash = generate_password_hash(password)

    def password_valid(self, password):
        # Проверяем пароль через этот метод
        # Функция check_password_hash превращает password в хеш и сравнивает с хранимым
        print(self._password_hash, password)
        return check_password_hash(self._password_hash, password)


class Meal(db.Model):
    __tablename__ = "meals"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    picture = db.Column(db.String, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    category = db.relationship("Category", back_populates="meals")


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    meals = db.relationship("Meal", back_populates="category")


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    summ = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False)
    meals = db.Column(db.String)
    user_mail= db.Column(db.String, db.ForeignKey("users.mail"))
    user = db.relationship("User", back_populates="orders")





