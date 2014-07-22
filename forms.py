from flask_wtf import Form
from wtforms import TextField, DateField
from wtforms.validators import DataRequired

DATE_FORMAT = '%Y-%m-%d'
class EventForm(Form):
    id = TextField('Identifier', validators=[DataRequired()])
    startdate = DateField('Start', validators=[DataRequired()], 
                          format=DATE_FORMAT)
    enddate = DateField('End', validators=[DataRequired()])
