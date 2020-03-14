from flask import Flask, render_template, request, session, redirect
import datetime
from flask_migrate import Migrate
from models import db, User, Meal, Category, Order
from forms import CartForm, AuthForm, UserForm
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__)
admin = Admin(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meals_v2.db'
app.secret_key = 'my-super-secret-phrase-I-dont-tell-this-to-nobody'
db.init_app(app)
migrate = Migrate(app, db)

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Order, db.session))
admin.add_view(ModelView(Meal, db.session))
admin.add_view(ModelView(Category, db.session))



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
    meals_list = db.session.query(Meal).all()
    cart = session.get("cart", [])
    meals = []
    for i in cart:
        meals.append(i)
    form = CartForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        address = form.address.data
        user_mail = form.user_mail.data
        phone = form.phone.data
        date = datetime.date.today().strftime("%d.%m.%Y")
        status = "Выполняется"
        order_form = Order(name=name, address=address, user_mail=user_mail, phone=phone, meals=meals, summ=summ(), date=date)
        db.session.add(order_form)
        db.session.commit()
        return redirect('/ordered/')

    output = render_template('cart.html', form=form, cart=cart, meals_list=meals_list)
    return output


@app.route('/remove-from-cart/<int:meal_id>/')
def remove_from_cart(meal_id):
    cart = session.get('cart', [])
    cart.remove(meal_id)
    session['cart'] = cart
    return redirect('/cart/')


@app.route('/ordered/', methods=['GET', 'POST'])
def orders_page():
    form = CartForm()
    if session.get("user_id"):
        return redirect('/account/')
    output = render_template("ordered.html", form=form)
    return output


@app.route('/register/', methods=["GET", "POST"])
def registration():
    form = UserForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        mail = form.mail.data
        password_hash = form.password.data
        role = "user"
        user = User(name=name, mail=mail, role=role)
        user.password_hash = password_hash
        db.session.add(user)
        db.session.commit()
        return redirect('/account/')
    else:
        return render_template("reg.html", form=form)


@app.route('/account/', methods=["GET", "POST"])
def profile():
    user = session.get("user_id")
    form = UserForm()
    if not session.get('user_id'):
        return redirect("/")
    output = render_template('account.html', form=form, user=user)
    return output


@app.route('/login/', methods=["GET", "POST"])
def log_in():
    if session.get("user_id"):
        return redirect("/account/")
    form = AuthForm()
    if request.method == "POST":
        user = User.query.filter_by(mail=form.mail.data).first()
        if user.mail and user.password_valid(form.password.data):
            session["user_id"] = {
                "id": user.id,
                "mail": user.mail,
                "role": user.role,
            }
            return redirect("/account/")

    return render_template("auth.html", form=form)


@app.route('/logout/')
def log_out():
    if session.get("user_id"):
        session.pop("user_id")
    return redirect("/login/")


def summ():
    meals = db.session.query(Meal).all()
    cart = session.get("cart", [])
    summ = 0
    for meal in meals:
        for i in cart:
            if meal.id == i:
                summ += meal.price
    return summ


@app.context_processor
def cart_data():

    return dict(summ=summ)


app.run(debug=True)
