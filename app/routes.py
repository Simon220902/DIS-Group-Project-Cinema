from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm
import psycopg
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, select_user_by_email, insert_user
from urllib.parse import urlsplit

@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'name': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'name': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]

    return render_template('index.html', title='Home', posts=posts)


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         # TRYING TO GET SOME STUFF FROM THE DATABASE
#         try:
#             cur = db.cursor()
#             cur.execute("SELECT * FROM users")
#             for result in cur.fetchall():
#                 flash(f"RESULT: {result} was in the database and has type {type(result)}")
#         except Exception as e:
#             print(f"GOT ERRROR {str(e)}")

#         # THIS IS JUST FROM THE TUTORIAL
#         flash(f"Login requested for user {form.username.data}, remember_me={form.remember_me.data}")
#         return redirect(url_for("index"))
#     return render_template('login.html', title='Sign In', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = select_user_by_email(form.email.data)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email-address or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        insert_user(user)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)