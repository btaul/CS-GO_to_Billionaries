from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired


class TeamPredForm(FlaskForm):
    #team1name = StringField('Team1', validators=[DataRequired()])
    team1name =  SelectField(u'Team1')
    team2name =  SelectField(u'Team2')
    selectmap =  SelectField(u'Map')
    submit = SubmitField(label='Predict', validators=[DataRequired()])
class TeamForm(FlaskForm):
    team1name =  SelectField(u'Pick a team')
    #team2name =  SelectField(u'Pick a team to compare')
    submit = SubmitField(label='Submit')
class PlayerPredForm(FlaskForm):
    player1 = StringField('Player1', validators=[DataRequired()])
    player2 = StringField('Player2', validators=[DataRequired()])
    player3 = StringField('Player3', validators=[DataRequired()])
    player4 = StringField('Player4', validators=[DataRequired()])
    player5 = StringField('Player5', validators=[DataRequired()])
    map = StringField('Map', validators=[DataRequired()])
    submit = SubmitField(label='Predict', validators=[DataRequired()])


class SubmitForm(FlaskForm):
    submit = SubmitField(label='Submit', validators=[DataRequired()])
