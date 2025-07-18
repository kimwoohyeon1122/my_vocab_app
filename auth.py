import bcrypt
from database import add_user, get_user

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def signup(username, password):
    pw_hash = hash_password(password)
    return add_user(username, pw_hash)

def login(username, password):
    user = get_user(username)
    if user and check_password(password, user[2]):
        return user
    return None
