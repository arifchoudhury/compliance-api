from wtforms import Form
from wtforms.fields import BooleanField, StringField, EmailField, SelectField, DateTimeField, BooleanField, IntegerField
from wtforms.validators import InputRequired, Length, DataRequired, Email, Optional

class CreateInteractionForm(Form):
    
    external_id = StringField('external_id', validators=[Optional(), Length(min=1, max=100)])
    start_time = DateTimeField('start_time', validators=[InputRequired()])
    end_time = DateTimeField('end_time', validators=[InputRequired()])
    withheld = BooleanField('withheld') # TODO input required doesnt work well with withheld
    direction = SelectField('direction', choices=['inbound', 'outbound'], validators=[InputRequired()])
    recorded_phone_number = StringField('recorded_phone_number', validators=[InputRequired()])
    third_party_phone_number = StringField('third_party_phone_number', validators=[InputRequired()])