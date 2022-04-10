from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class TeamForm(FlaskForm):
    team1name = StringField('Team1', validators=[DataRequired()])
    team2name = StringField('Team2', validators=[DataRequired()])
    submit = SubmitField(label='Compare', validators=[DataRequired()])

