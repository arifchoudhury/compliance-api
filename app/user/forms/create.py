from wtforms import Form
from wtforms.fields import BooleanField, StringField, EmailField, SelectField, IntegerField
from wtforms.validators import InputRequired, Length, DataRequired, Email, Optional

class UserCreateForm(Form):

    email = EmailField('email', validators=[Email(), InputRequired(), Length(min=1, max=100)])
    fullname = StringField('fullname', validators=[InputRequired(), Length(min=1, max=100)])
    role_name = StringField('role_name', validators=[InputRequired()])
    group_name = StringField('group_name', validators=[InputRequired()])
    send_welcome_email = BooleanField('send_welcome_email')
    active = BooleanField('active')

