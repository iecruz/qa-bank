from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort
from werkzeug.security import check_password_hash
from core.models import Transaction, Account, User, TimeDeposit, Log, DoesNotExist
from playhouse.shortcuts import model_to_dict
from core.forms import LoginForm, TransactionForm, UserTransferForm, InquiryForm, TimeDepositForm
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

    accounts = Account.select().where(Account.user_id == session['user']['id']).execute()
    transactions = len(Transaction.select(Transaction)
        .join(Account, on=(Transaction.account_number == Account.account_number))
        .join(User, on=(Account.user_id == User.id))
        .where(User.id == session['user']['id'])
        .dicts()
    )

    return render_template('main/index.html', accounts=accounts, transactions=transactions)

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

            if user.type <= 2:
                return redirect(url_for('admin.index'))
            else:
                return redirect(url_for('main.index'))
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

@bp.route('/history')
@authenticated
def history():
    transactions = (Transaction.select(Transaction)
        .join(Account, on=(Transaction.account_number == Account.account_number))
        .join(User, on=(Account.user_id == User.id))
        .where(User.id == session['user']['id'])
        .execute()
    )
    return render_template('main/history.html', transactions=transactions)

@bp.route('/transfer', methods=['GET', 'POST'])
@authenticated
def transfer():
    accounts = Account.select().where((Account.user_id == session['user']['id']) & (Account.type != 3)).execute()

    form = UserTransferForm(request.form)
    form.sender_account_number.choices = [(account.account_number, "{} ({})".format(account.account_number, 'Savings' if account.type == 1 else 'ATM')) for account in accounts]
    if form.validate_on_submit():
        sender_account = Account.get(Account.account_number == form.sender_account_number.data)
        receiver_account = Account.get(Account.account_number == form.receiver_account_number.data)

        Account.update(
            balance = Account.balance - form.amount.data,
            updated_at = datetime.now()
        ).where(Account.account_number == form.sender_account_number.data).execute()

        Account.update(
            balance = Account.balance + form.amount.data,
            updated_at = datetime.now()
        ).where(Account.account_number == form.receiver_account_number.data).execute()

        Transaction.insert(
            account_number = form.sender_account_number.data,
            reference_number = form.receiver_account_number.data,
            amount = form.amount.data,
            type = 'FUND TRANSFER'
        ).execute()
        flash('Fund Transfer successful')
        return redirect(url_for('main.transfer'))
    return render_template('main/transfer.html', form=form)