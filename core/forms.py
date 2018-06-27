from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, IntegerField, DecimalField
from wtforms.fields.html5 import TelField, EmailField, DateField
from wtforms.validators import Required, Email, Regexp, EqualTo, Length, NumberRange, ValidationError
from core.models import User, Account

def validate_account_number(form, field):
    if not Account.get_or_none((Account.account_number == field.data) & (Account.deleted == False)):
        raise ValidationError('Account is inactivate or does not exists')

class TellerLoginForm(FlaskForm):
    account = StringField('Account Number', [Required()])
    password = PasswordField('PIN', [Required()])

class LoginForm(FlaskForm):
    email_address = EmailField('Email Address', [Required(), Email()])
    password = PasswordField('Password', [Required()])

class CreateUserForm(FlaskForm):
    first_name = StringField('First Name', [Required()])
    middle_name = StringField('Middle Name', [Required()])
    last_name = StringField('Last Name', [Required()])
    email_address = EmailField('Email Address', [Email(), Required()])
    phone_number = TelField('Phone Number', [Required(), Length(7,11), Regexp('[0-9]+')])
    address = StringField('Address', [Required()])
    birth_date = DateField('Birth Date', [Required()])
    password = PasswordField('Password', [Required(), Length(8), EqualTo('confirm_password', message='Password must match')])
    confirm_password = PasswordField('Confirm Password', [Required(), Length(8)])

class UpdateUserForm(FlaskForm):
    first_name = StringField('First Name', [Required()])
    middle_name = StringField('Middle Name', [Required()])
    last_name = StringField('Last Name', [Required()])
    email_address = EmailField('Email Address', [Email(), Required()])
    phone_number = TelField('Phone Number', [Required(), Length(7,11), Regexp('[0-9]+')])
    address = StringField('Address', [Required()])
    birth_date = DateField('Birth Date', [Required()])

class CreateAccountForm(FlaskForm):
    user_id = IntegerField('User ID', [Required()])
    def validate_user_id(form, field):
        if not User.get_or_none(User.id == field.data):
            raise ValidationError('User does not exists')
            
    pin = IntegerField('PIN', [Required(), NumberRange(1000,9999)])
    checking_balance = DecimalField('Checking Balance', [Required(), NumberRange(1000)], places=2)
    savings_balance = DecimalField('Savings Balance', [Required(), NumberRange(1000)], places=2)

class TransactionForm(FlaskForm):
    account_number = IntegerField('Account Number', [Required(), validate_account_number])
    amount = DecimalField('Amount', [Required(), NumberRange(500)], places=2)

class TransferForm(FlaskForm):
    sender_account_number = IntegerField('Sender Account Number', [Required(), validate_account_number])
    receiver_account_number = IntegerField('Receiver Account Number', [Required(), validate_account_number])
    amount = DecimalField('Amount', [Required(), NumberRange(500)], places=2)

class InquiryForm(FlaskForm):
    account_number = IntegerField('Account Number', [Required(), validate_account_number])