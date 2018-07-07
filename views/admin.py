from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort
from werkzeug.security import check_password_hash
from core.models import Transaction, Account, User, TimeDeposit, Log, DoesNotExist
from playhouse.shortcuts import model_to_dict
from core.forms import LoginForm, TransactionForm, TransferForm, InquiryForm, TimeDepositForm
from core.wrappers import authenticated

from datetime import datetime, timedelta

bp = Blueprint('admin', __name__)

@bp.route('/')
@authenticated
def index():
    time_deposits = TimeDeposit.select().where((TimeDeposit.terminal_date <= datetime.now()) & (TimeDeposit.deleted == False)).execute()
    history = Transaction.select().order_by(Transaction.created_at.desc()).execute()
    for time_deposit in time_deposits:
        Account.update(
            account = Account.balance + (time_deposit.amount * time_deposit.interest) + time_deposit.amount
        ).where(Account.account_number == time_deposit.account_number).execute()

        TimeDeposit.update(
            deleted = True
        ).where(TimeDeposit.id == time_deposit.id).execute()

    return render_template('admin/index.html', history=history)
    
@bp.route('/deposit', methods=['GET', 'POST'])
@authenticated
def deposit():
    form = TransactionForm(request.form)
    if form.validate_on_submit():
        Account.update(
            balance = Account.balance + form.amount.data,
            updated_at = datetime.now()
        ).where(Account.account_number == form.account_number.data).execute()

        Transaction.insert(
            account_number = form.account_number.data,
            reference_number = form.account_number.data,
            amount = form.amount.data,
            type = 'DEPOSIT'
        ).execute()
        flash('Deposit successful')
        return redirect(url_for('admin.deposit'))
    return render_template('admin/deposit.html', form=form)

@bp.route('/time_deposit', methods=['GET', 'POST'])
@authenticated
def time_deposit():
    form = TimeDepositForm(request.form)
    form.duration.choices = ([
        (3, '3 months (7.0% interest)'),
        (6, '6 months (8.0% interest)'),
        (12, '12 months (9.0% interest)')
    ])

    if form.validate_on_submit():
        interest_ref = {
            3: 7.0,
            6: 8.0,
            12: 9.0
        }

        Account.update(
            time_deposit = Account.time_deposit + form.amount.data,
            updated_at = datetime.now()
        ).where(Account.account_number == form.account_number.data).execute()

        TimeDeposit.insert(
            account_number = form.account_number.data,
            amount = form.amount.data,
            interest = interest_ref[form.duration.data],
            terminal_date = datetime.now() + timedelta(days=form.duration.data*30)
        ).execute()

        Transaction.insert(
            account_number = form.account_number.data,
            reference_number = form.account_number.data,
            amount = form.amount.data,
            type = 'TIME DEPOSIT'
        ).execute()
        flash('Time Deposit successful')
        return redirect(url_for('admin.time_deposit'))
    return render_template('admin/time_deposit.html', form=form)

@bp.route('/withdraw', methods=['GET', 'POST'])
@authenticated
def withdraw():
    form = TransactionForm(request.form)
    if form.validate_on_submit():
        Account.update(
            balance = Account.balance - form.amount.data,
            updated_at = datetime.now()
        ).where(Account.account_number == form.account_number.data).execute()

        Transaction.insert(
            account_number = form.account_number.data,
            reference_number = form.account_number.data,
            amount = form.amount.data,
            type = 'WITHDRAW'
        ).execute()
        flash('Withdraw successful')
        return redirect(url_for('admin.withdraw'))
    return render_template('admin/withdraw.html', form=form)

@bp.route('/transfer', methods=['GET', 'POST'])
@authenticated
def transfer():
    form = TransferForm(request.form)
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

@bp.route('/inquiry', methods=['GET', 'POST'])
@authenticated
def inquiry():
    form = InquiryForm(request.form)
    account = None
    if form.validate_on_submit():
        account = Account.select(
            User.first_name,
            User.last_name,
            Account.balance,
            Account.time_deposit,
        ).join(User, attr='user').where(
            (Account.account_number == form.account_number.data)
        ).get()

    return render_template('admin/inquiry.html', form=form, account=account)