# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField,SubmitField,TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class Generateform(FlaskForm):
    id = IntegerField('tempid')

class OpenAiform(FlaskForm):
    key = StringField('Stripe Api Key', validators=[DataRequired()])
    
class CourseForm(FlaskForm):
    name = StringField('Course Title', validators=[DataRequired()])