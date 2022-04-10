from web import app
from flask import render_template,flash
from web.forms import TeamForm
from web import cursor



@app.route('/')
def home():
    return render_template("home.html")


@app.route('/player')
def player():
    return render_template("player.html")

@app.route('/team', methods=['GET', 'POST'])
def team():
    form = TeamForm()
    if form.validate_on_submit():
      
        try:
            cursor.execute("SELECT team_id FROM teams WHERE team_name='%s'"%(form.team1name.data))
            team1 = cursor.fetchone()
            team1id= team1[0]

            
        except:
            flash('invalid team1 name!', 'warning')

        try:
            cursor.execute("SELECT team_id FROM teams WHERE team_name='%s'"%(form.team2name.data))
            team2 = cursor.fetchone()
            team2id= team2[0]
            
            
        except:
            flash('invalid team2 name!', 'error')

        if team1id != team2id:
            pass
        else:
            flash('team names can\'t be same', 'warning')



    return render_template("team.html",form=form)


    
