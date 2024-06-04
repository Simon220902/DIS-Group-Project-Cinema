from typing import Optional
import psycopg
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, username, email, id=None, password_hash=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

def __select_user(id=None, username=None, email=None) -> Optional[User]:
    if id != None or username != None or email != None:
        if id != None:
            sql = f"SELECT (id, username, email, password_hash) FROM users WHERE id = {id}"
        elif username != None:
            sql = f"SELECT (id, username, email, password_hash) FROM users WHERE username = '{username}'"
        elif email != None:
            sql = f"SELECT (id, username, email, password_hash) FROM users WHERE email = '{email}'"
        cur = db.cursor()
        cur.execute(sql)
        data_row = cur.fetchone()
        cur.close()
        if data_row == None:
            return None
        else:
            ((id, username, email, password_hash),) = data_row
            user = User(username=username, email=email)
            user.id = id
            user.password_hash = password_hash
        return user
    else:
        print("! YOU HAVE TO SPECIFY EITHER AN ID, USERNAME OR EMAIL !")
        return None

@login.user_loader
def select_user_by_id(id) -> Optional[User]:
    return __select_user(id=id)

def select_user_by_username(username) -> Optional[User]:
    return __select_user(username=username)

def select_user_by_email(email) -> Optional[User]:
    return __select_user(email=email)

def insert_user(user):
    if user != None and type(user) == User and user.password_hash != None:
        cur = db.cursor()
        sql = f"""INSERT INTO users (username, email, password_hash)
                  VALUES ('{user.username}', '{user.email}', '{user.password_hash}')"""
        cur.execute(sql)
        db.commit()
        cur.close()
        return user
    else:
        print("! INSERT NOT DONE !")
        print(f"User was either None or not a User or password was not set. user = {user}")