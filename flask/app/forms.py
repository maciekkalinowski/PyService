
import datetime
from email.policy import default


from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, BooleanField, SubmitField, \
    PasswordField, SelectMultipleField, DateField, SelectField        
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
    valueMin = DecimalField('ValueMin', default=0 )
    valueMax = DecimalField('ValueMax', default=100000000 )
    dateStart = DateField('DateStart', default=datetime.date(2000,1,1) )
    dateEnd = DateField('DateEnd', default=datetime.date.today() )
    tags = SelectMultipleField(u'Tags')
    submit = SubmitField('Wyszukaj')