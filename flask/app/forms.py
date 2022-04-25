from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired



class entryForm(FlaskForm):
    value = DecimalField('Value', validators=[DataRequired()])
    submit = SubmitField('Save')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')