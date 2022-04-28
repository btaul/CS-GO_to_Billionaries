from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired


class TeamForm(FlaskForm):
    team1name = StringField('Team1', validators=[DataRequired()])
    team2name = StringField('Team2', validators=[DataRequired()])
    selectmap =  SelectField(u'Map')
    submit = SubmitField(label='Predict', validators=[DataRequired()])


class SubmitForm(FlaskForm):
    submit = SubmitField(label='Submit', validators=[DataRequired()])
