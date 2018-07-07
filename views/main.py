from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort
from werkzeug.security import check_password_hash
from core.models import Transaction, Account, User, TimeDeposit, Log, DoesNotExist
from playhouse.shortcuts import model_to_dict
from core.forms import LoginForm, TransactionForm, TransferForm, InquiryForm, TimeDepositForm
from core.wrappers import authenticated

from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

@bp.route('/')
@authenticated
def index():
    time_deposits = TimeDeposit.select().where((TimeDeposit.terminal_date <= datetime.now()) & (TimeDeposit.deleted == False)).execute()

    for time_deposit in time_deposits:
        Account.update(
            account = Account.balance + (time_deposit.amount * time_deposit.interest) + time_deposit.amount
        ).where(Account.account_number == time_deposit.account_number).execute()

        TimeDeposit.update(
            deleted = True
        ).where(TimeDeposit.id == time_deposit.id).execute()

    try:
        log = (Log.select()
        .where(
            (Log.action == 'LOGIN') & 
            (Log.user_id == session['user']['id'])
        ).order_by(Log.created_at.desc()).get()).created_at.strftime('%d %B %Y %I:%M %p')
    except DoesNotExist:
        log = None
    return render_template('main/index.html', log=log)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.get_or_none(User.email_address == form.email_address.data)
        if user and check_password_hash(user.password, form.password.data):
            Log.insert(
                user_id = user.id,
                action = 'LOGIN'
            ).execute()
            session['user'] = model_to_dict(user)

            flash("Welcome back, {}!".format(user.first_name))

            if user.type == 1:
                return redirect(request.args.get('next', url_for('admin.index')))
            else:
                return redirect(request.args.get('next', url_for('admin.index')))
    return render_template('main/login.html', form=form)

@bp.route('/logout', methods=['GET', 'POST'])
@authenticated
def logout():
    Log.insert(
        user_id = session['user']['id'],
        action = 'LOGOUT'
    ).execute()
    session.pop('user')
    return redirect(url_for('main.login'))