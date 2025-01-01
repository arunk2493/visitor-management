from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, IntegerField, DateField
from wtforms.validators import DataRequired

class VisitorForm(FlaskForm):
    entry_exit = RadioField('Entry or Exit', choices=[('Entry', 'Exit'), ('Exit', 'Exit')], validators=[DataRequired()])
    visitor_name = StringField('Visitor Name', validators=[DataRequired()])
    flat_no = StringField('Flat No', validators=[DataRequired()])
    resident_name = StringField('Resident Name', validators=[DataRequired()])
    resident_contact = StringField('Resident Contact Number', validators=[DataRequired()])
    visitor_contact = StringField('Visitor Contact Number', validators=[DataRequired()])
    purpose_of_visit = StringField('Purpose of Visit', validators=[DataRequired()])
    num_guests = IntegerField('No. of Guests', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    token = StringField('Token')