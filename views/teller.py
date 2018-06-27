from flask import Blueprint, render_template, request
from core.forms import TellerLoginForm

bp = Blueprint('teller', __name__)

@bp.route('/')
def index():
    return render_template('teller/index.html')

@bp.route('/inquiry')
def inquiry():
    return render_template('teller/inquiry.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = TellerLoginForm(request.form)
    if form.validate_on_submit():
        return '1234'
    return render_template('teller/login.html', form=form)

@bp.route('/logout')
def logout():
    pass