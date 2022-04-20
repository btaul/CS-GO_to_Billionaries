from tkinter import W
from web import app
from flask import render_template,flash
from web.forms import TeamForm, PlayerPredForm
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


@app.route('/teamperdiction', methods=['GET', 'POST'])
def teampred():
    form = TeamForm()
    winner = 'no result'
    cursor.execute("SELECT map_name FROM maps")
    data_id = cursor.fetchall()
    form.selectmap.choices = [(i[0]) for i in data_id]
    mapid = 0
    if form.validate_on_submit():
        if form.team1name.data != form.team2name.data:
            pass
        else:
            flash('team names can\'t be same', 'warning')

      
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

            try:
                cursor.execute("SELECT map_id FROM maps WHERE map_name='%s'"%(form.selectmap.data))
                map = cursor.fetchone()
                mapid= map[0]
        
                cursor.execute("SELECT COUNT(*) FROM roster_stats where roster_id in (  SELECT roster_id FROM rosters WHERE team_id='%s') AND map_id = '%s'"%(team1id,mapid))
                num1 = cursor.fetchone()
                cursor.execute("SELECT COUNT(*) FROM roster_stats where roster_id in (  SELECT roster_id FROM rosters WHERE team_id='%s') AND map_id = '%s' AND won_this_map=1"%(team1id,mapid))
                win1 = cursor.fetchone()
                rate1 = win1[0]/num1[0]

                cursor.execute("SELECT COUNT(*) FROM roster_stats where roster_id in (  SELECT roster_id FROM rosters WHERE team_id='%s') AND map_id = '%s'"%(team2id,mapid))
                num2 = cursor.fetchone()
                cursor.execute("SELECT COUNT(*) FROM roster_stats where roster_id in (  SELECT roster_id FROM rosters WHERE team_id='%s') AND map_id = '%s' AND won_this_map=1"%(team2id,mapid))
                win2 = cursor.fetchone()
                rate2 = win2[0]/num2[0]
             
                if rate1 > rate2:
                    winner = form.team1name.data
                else:
                    winner = form.team2name.data
            except:
                flash('please check input', 'warning')

            
            
        except:
            flash('invalid team2 name!', 'error')
          

       



    return render_template("predteam.html",form=form,winner=winner)
  

@app.route('/playerperdiction', methods=['GET', 'POST'])
def playerpred():
    form = PlayerPredForm()
    if form.validate_on_submit():
      
        pass



    return render_template("predplayer.html",form=form)
