from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired


class TeamPredForm(FlaskForm):
    #team1name = StringField('Team1', validators=[DataRequired()])
    team1name =  SelectField(u'Team1')
    team2name =  SelectField(u'Team2')
    selectmap =  SelectField(u'Map')
    submit = SubmitField(label='Predict', validators=[DataRequired()])


class SubmitForm(FlaskForm):
    submit = SubmitField(label='Submit', validators=[DataRequired()])
