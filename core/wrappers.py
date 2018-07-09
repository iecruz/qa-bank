from flask import request, session, redirect, url_for
from functools import wraps

def authenticated(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            if 'admin' in session:
                return redirect(url_for('admin.index'))
            else:
                return redirect(url_for('main.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            if 'user' in session:
                return redirect(url_for('main.index'))
            else:
                return redirect(url_for('main.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def teller_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'atm_auth' not in session:
            return redirect(url_for('teller.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function