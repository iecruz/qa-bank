from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort
from werkzeug.security import check_password_hash
from core.models import Transaction, Account, User
from core.forms import LoginForm, TransactionForm, TransferForm, InquiryForm
from core.wrappers import authenticated

from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route('/')
@authenticated
def index():
    return render_template('main/index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.get_or_none(User.email_address == form.email_address.data)
        if user and check_password_hash(user.password, form.password.data):
            session['user'] = user.id

            flash("Welcome back, {}!".format(user.first_name))
            return redirect(request.args.get('next', url_for('main.index')))
    return render_template('main/login.html', form=form)

@bp.route('/logout', methods=['GET', 'POST'])
@authenticated
def logout():
    session.pop('user')
    return redirect(url_for('main.login'))
    
@bp.route('/deposit', methods=['GET', 'POST'])
@authenticated
def deposit():
    form = TransactionForm(request.form)
    if form.validate_on_submit():
        account = Account.get(Account.account_number == form.account_number.data)

        Account.update(
            savings_balance = Account.savings_balance + form.amount.data,
            updated_at = datetime.now()
        ).where(Account.account_number == form.account_number.data).execute()

        Transaction.insert(
            account_id = account.id,
            amount = form.amount.data,
            type = 'DEPOSIT'
        ).execute()
        flash('Deposit successful')
        return redirect(url_for('main.deposit'))
    return render_template('main/deposit.html', form=form)

@bp.route('/withdraw', methods=['GET', 'POST'])
@authenticated
def withdraw():
    form = TransactionForm(request.form)
    if form.validate_on_submit():
        account = Account.get(Account.account_number == form.account_number.data)

        Account.update(
            savings_balance = Account.savings_balance - form.amount.data,
            updated_at = datetime.now()
        ).where(Account.account_number == form.account_number.data).execute()

        Transaction.insert(
            account_id = account.id,
            amount = form.amount.data,
            type = 'WITHDRAW'
        ).execute()
        flash('Withdraw successful')
        return redirect(url_for('main.withdraw'))
    return render_template('main/withdraw.html', form=form)

@bp.route('/transfer', methods=['GET', 'POST'])
@authenticated
def transfer():
    form = TransferForm(request.form)
    if form.validate_on_submit():
        sender_account = Account.get(Account.account_number == form.sender_account_number.data)
        receiver_account = Account.get(Account.account_number == form.sender_account_number.data)

        Account.update(
            savings_balance = Account.savings_balance - form.amount.data,
            updated_at = datetime.now()
        ).where(Account.account_number == form.sender_account_number.data).execute()

        Account.update(
            savings_balance = Account.savings_balance + form.amount.data,
            updated_at = datetime.now()
        ).where(Account.account_number == form.receiver_account_number.data).execute()

        Transaction.insert(
            account_id = sender_account.id,
            target_account = receiver_account.id,
            amount = form.amount.data,
            type = 'FUND TRANSFER'
        ).execute()
        flash('Fund Transfer successful')
        return redirect(url_for('main.transfer'))
    return render_template('main/transfer.html', form=form)

@bp.route('/inquiry', methods=['GET', 'POST'])
@authenticated
def inquiry():
    form = InquiryForm(request.form)
    account = None
    if form.validate_on_submit():
        account = Account.select(
            User.first_name,
            User.last_name,
            Account.savings_balance,
            Account.checking_balance
        ).join(User, attr='user').where(
            (Account.account_number == form.account_number.data)
        ).get()

    return render_template('main/inquiry.html', form=form, account=account)