from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash
from core.models import Account, User
from core.forms import CreateAccountForm
from core.wrappers import authenticated

from random import randint
from datetime import datetime

bp = Blueprint('account', __name__)

@bp.route('/')
@authenticated
def index():
    accounts = Account.select(
        Account.id, 
        Account.account_number, 
        Account.balance, 
        Account.type, 
        Account.deleted, 
        User.first_name, 
        User.last_name
    ).join(User, attr='user').execute()
    return render_template('account/index.html', accounts=accounts)

@bp.route('/create', methods=['GET', 'POST'])
@authenticated
def create():
    form = CreateAccountForm(request.form)
    if form.validate_on_submit():
        Account.insert(
            account_number = randint(1000000000, 9999999999),
            user_id = form.user_id.data,
            pin = generate_password_hash(str(form.pin.data)),
            type = form.type.data,
            balance = form.balance.data
        ).execute()
        flash('Account successfully opened')
        return redirect(url_for('account.index'))
    return render_template('account/create.html', form=form)

@bp.route('/deactivate/<int:id>')
@authenticated
def deactivate(id):
    Account.update(
        deleted=True,
        updated_at=datetime.now()
    ).where(Account.id == id).execute()
    return redirect(url_for('account.index'))

@bp.route('/activate/<int:id>')
@authenticated
def activate(id):
    Account.update(
        deleted=False,
        updated_at=datetime.now()
    ).where(Account.id == id).execute()
    return redirect(url_for('account.index'))