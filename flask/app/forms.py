from ast import List
from msilib.schema import CheckBox
from tkinter import Label
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, BooleanField, SubmitField, \
    PasswordField, Label, SelectMultipleField, DateField, DecimalRangeField, SelectField        
from wtforms.validators import DataRequired



class entryForm(FlaskForm):
    value = DecimalField('Value', validators=[DataRequired()])
    #author = Label('id','')
    author = SelectField('Author')
    tags  = SelectMultipleField(u'Entry tags')
    newTag = StringField('newTag')
    comment = StringField('Comment')

    submit = SubmitField('Dodaj wpis')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class statsForm(FlaskForm):
    authors = SelectMultipleField(u'Authors')
    valueMin = DecimalField('ValueMin' )
    valueMax = DecimalField('ValueMax', validators=None )
    dateStart = DateField('DateStart' )
    dateEnd = DateField('DateEnd' )
    tags = SelectMultipleField(u'Tags')
    submit = SubmitField('Wyszukaj')