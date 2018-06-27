from flask import Flask

from views import main, user, account, teller

from core.models import connect_db, close_db

import os

app = Flask(__name__)

env = os.getenv('ENVIRONMENT', 'development')

if env == 'production':
    app.config.from_object('core.config.ProductionConfig')
elif env == 'development':
    app.config.from_object('core.config.DevelopmentConfig')

app.register_blueprint(main.bp)
app.register_blueprint(account.bp, url_prefix='/account')
app.register_blueprint(user.bp, url_prefix='/user')
app.register_blueprint(teller.bp, url_prefix='/teller')

@app.before_request
def before_request():
    connect_db()
    
@app.teardown_request
def teardown_request(exception):
    close_db()

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG'))