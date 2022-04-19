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
    print("Total rows are:  ", len(events))
    print("Printing each row")
    e = []
    for event in events:
        print("Id: ", event[0])
        print("Name: ", event[1])
        e.append(event[1])
        print("\n")

    return render_template("player.html", events=e, form=form)


@app.route('/players/event', methods=['POST'])
def player_and_event():
    form = SubmitForm()
    event_name = request.form['event']
    print("event_name: " + event_name)
    query = "SELECT * FROM events WHERE event_name ='%s'" % event_name
    cursor.execute(query)
    event = cursor.fetchone()

    print("Player + Event")
    print("Id: ", event[0])
    print("Name: ", event[1])

    query2 = "SELECT match_id FROM matches WHERE event_id ='%s'" % event[0]
    cursor.execute(query2)
    matches = cursor.fetchmany()

    m = []
    for match in matches:
        print("Match Id: ", match[0])
        m.append(match[0])
        print("\n")

    return render_template("playerAndEvents.html", event=event[1], matches=m, form=form)


@app.route('/players/event/match', methods=['POST'])
def player_event_and_match():
    form = SubmitForm()

    match_id = request.form['match']
    query2 = "SELECT * FROM matches WHERE match_id ='%s'" % match_id
    cursor.execute(query2)
    match = cursor.fetchone()

    query = "SELECT * FROM events WHERE event_id ='%s'" % match[1]
    cursor.execute(query)
    event = cursor.fetchone()

    query3 = "SELECT map_name FROM picks INNER JOIN maps ON picks.map_id = maps.map_id WHERE match_id ='%s'" % match_id
    cursor.execute(query3)
    maps = cursor.fetchall()

    print("Player + Event + Match")
    print("Id: ", event[0])
    print("Name: ", event[1])
    print("Match Id: ", match[0])

    m2 = []
    for m in maps:
        print("Map Name: ", m[0])
        m2.append(m[0])
        print("\n")

    return render_template("playerEventAndMatch.html", maps=m2, event=event[1], match=match[0], form=form)


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


    
