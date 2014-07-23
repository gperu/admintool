from flask_wtf import Form
from wtforms import TextField, DateField
from wtforms.validators import DataRequired, URL

DATE_FORMAT = '%Y-%m-%d'

class EventForm(Form):
    id = TextField('Identifier', validators=[DataRequired()])
    startdate = DateField('Start', validators=[DataRequired()],
                          format=DATE_FORMAT)
    enddate = DateField('End', format=DATE_FORMAT)
    site = TextField('site')
    details_url = TextField('Details URL', validators=[URL()])
