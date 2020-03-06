from flask import Flask, render_template, request, session, redirect
from flask_migrate import Migrate
from random import shuffle
from hashlib import md5
from models import db, User, Meal, Category, Order, OrderData
from forms import CartForm, AuthForm, UserForm


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meals_v2.db'
app.secret_key = 'my-super-secret-phrase-I-dont-tell-this-to-nobody'
db.init_app(app)
migrate = Migrate(app, db)


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    categories = db.session.query(Category).all()
    output = render_template('index.html', categories=categories)
    return output


@app.route('/addtocart/<int:meal_id>/')
def add_tocart(meal_id):
    meals = db.session.query(Meal).get(meal_id)
    cart = session.get("cart", [])
    cart.append(meal_id)
    session['cart'] = cart
    return redirect('/cart/')


@app.route('/cart/', methods=["GET", "POST"])
def cart_page():
    meals = db.session.query(Meal).all()
    form = CartForm()
    if form.validate_on_submit():
        return redirect('/ordered/')
    cart = session.get("cart", [])
    output = render_template('cart.html', form=form, cart=cart, meals=meals)
    return output


@app.route('/reset/')
def deleted():

    return redirect('/cart/')


@app.route('/ordered/', methods=['POST'])
def orders_page():
    form = CartForm()
    name = form.name.data
    address = form.address.data
    mail = form.mail.data
    phone = form.phone.data
    order_form = OrderData(name=name, address=address, mail=mail, phone=phone)
    db.session.add(order_form)
    db.session.commit()
    output = render_template("ordered.html", form=form)
    return output


@app.route('/register/', methods=["GET", "POST"])
def registration():
    form = UserForm()
    if form.validate_on_submit():
        return redirect('/account/')
    else:
        return render_template("reg.html", form=form)


@app.route('/account/', methods=["POST"])
def profile():
    form = UserForm()
    name = form.name.data
    mail = form.mail.data
    password = form.password.data
    confirm_password = form.confirm_password.data
    salt = "OMG!"
    hash_password = md5((password + salt).encode())
    password_hash = hash_password.hexdigest()
    password = password_hash
    user_form = User(name=name, mail=mail, password=password)
    db.session.add(user_form)
    db.session.commit()
    output = render_template('account.html', form=form)
    return output


@app.route('/login/')
def log_in():
#    if not session.get('is_auth'):
#        return redirect('/auth/')
    return render_template("auth.html")


@app.route('/logout/')
def log_out():
    output = render_template('logout.html')
    return output


@app.context_processor
def cart_data():
    def summ():
        meals = db.session.query(Meal).all()
        cart = session.get("cart", [])
        summ = 0
        for meal in meals:
            for i in cart:
                if meal.id == i:
                    summ += meal.price
        return summ
    return dict(summ=summ)


app.run(debug=True)
