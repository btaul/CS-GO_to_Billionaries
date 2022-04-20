from web import app
from flask import render_template, flash, request
from web.forms import TeamForm
from web.forms import SubmitForm
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


    
