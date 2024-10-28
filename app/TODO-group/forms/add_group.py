from wtforms import Form
from wtforms.fields import BooleanField, StringField, EmailField, SelectField
from wtforms.validators import InputRequired, Length, DataRequired, Email, Optional

class AddGroupForm(Form):
    
    groupName = StringField('groupName', validators=[InputRequired(), Length(min=1, max=100)])