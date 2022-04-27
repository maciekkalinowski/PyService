from ast import List
from msilib.schema import CheckBox
from tkinter import Label
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, BooleanField, SubmitField, PasswordField, Label, SelectMultipleField
from wtforms.validators import DataRequired



class entryForm(FlaskForm):
    value = DecimalField('Value', validators=[DataRequired()])
    author = Label('id','')
    tags  = SelectMultipleField(u'Entry tags')
    newTag = StringField('newTag')
    comment = StringField('Comment')

    submit = SubmitField('Dodaj wpis')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
