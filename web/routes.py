from tkinter import W
from web import app

from flask import render_template, flash, request
from web.forms import TeamForm
from web.forms import SubmitForm
from web.forms import TeamForm, PlayerPredForm
from web import cursor


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/index', methods=['GET'])
def index():
    return render_template("home.html")


@app.route('/players', methods=['GET'])
def player():
    form = SubmitForm()
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    e = []
    for event in events:

        e.append(event[1])

    return render_template("player.html", events=e, form=form)


@app.route('/players/event', methods=['POST'])
def player_and_event():
    form = SubmitForm()
    event_name = request.form['event']

    query = "SELECT * FROM events WHERE event_name ='%s'" % event_name
    cursor.execute(query)
    event = cursor.fetchone()

    query2 = "SELECT match_id FROM matches WHERE event_id ='%s'" % event[0]
    cursor.execute(query2)
    matches = cursor.fetchmany()

    m = []
    for match in matches:
        m.append(match[0])

    return render_template("playerAndEvents.html", event=event_name, matches=m, form=form)


@app.route('/players/event/match', methods=['POST'])
def player_event_and_match():
    form = SubmitForm()
    event_name = request.form['event']
    match_id = request.form['match']

    query = "SELECT map_name FROM picks INNER JOIN maps ON picks.map_id = maps.map_id WHERE match_id ='%s'" % match_id
    cursor.execute(query)
    maps = cursor.fetchall()

    m2 = []
    for m in maps:
        m2.append(m[0])

    return render_template("playerEventAndMatch.html", maps=m2, event=event_name, match=match_id, form=form)


@app.route('/players/event/match/map', methods=['POST'])
def player_event_match_and_map():
    form = SubmitForm()
    event_name = request.form['event']
    match_id = request.form['match']
    map_name = request.form['map']

    query = "SELECT map_id FROM maps WHERE map_name = '%s'" % map_name
    cursor.execute(query)
    map_id = cursor.fetchone()[0]

    query2 = "SELECT * FROM player_performance WHERE match_id = '%s' and map_id = '%s'" % (match_id, map_id)
    cursor.execute(query2)
    player_info = cursor.fetchall()

    kda = []
    adr = []
    player_names = []
    if len(player_info) == 0:
        print("null")
    for p in player_info:
        formula = 0
        if p[4] != 0:
            formula = float(p[3] + (.5 * p[5]))/float(p[4])
        else:
            formula = float(p[3] + (.5 * p[5]))
        kda.append(formula)
        adr.append(p[7])
        query3 = "SELECT player_name FROM players WHERE player_id = '%s'" % p[0]
        cursor.execute(query3)
        players = cursor.fetchone()
        player_names.append(players[0])

    return render_template("playerEventMatchAndMap.html", players=player_names, kda=kda, adr=adr, map=map_name, event=event_name, match=match_id, form=form)


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
