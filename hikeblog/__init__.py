import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
import click


app = Flask(__name__)
db = SQLAlchemy(app)
admin = Admin(app, name='hikeblog', template_mode='bootstrap3')

basedir = os.path.abspath(os.path.dirname(__file__))

#app.config['WTF_CSRF_SECRET_KEY'] = 'DSWncdweuwiqSD23435-=-p=pxzwa.,m2345hh'
app.config['SECRET_KEY'] = '\x9c\xcd\xe4\x1c\xd1b\x01\x1c\xf8\xda\\h\xe1L\x92\xa9@2\xb9\x11\x9b\xb0\xf4\xed\xae\xc4\xd6\xf9Y^.\xf7\x19V9\x7f\x12A'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'flask_alchemy.db')
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LfNzhoUAAAAAJcBh1rMQdFEnB5A3u78UrLblLCy'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LfNzhoUAAAAAHWXUyDydCYNYacCr_0lReUk0dHC'


import hikeblog.views

@app.cli.command()
def initdb():
	"""Initialize the database"""
	click.echo(" ")
	click.echo("Attempt to init db")	
	db.create_all()
	click.echo("Database created!")
	