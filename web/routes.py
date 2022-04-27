from tkinter import W
from web import app

from flask import render_template, flash, request
from web.forms import TeamForm
from web.forms import SubmitForm
from web.forms import TeamForm, PlayerPredForm,TeamPredForm
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
    
    cursor.execute("SELECT team_name FROM teams")
    team_id = cursor.fetchall()
    form.team1name.choices = [(i[0]) for i in team_id]
    #form.team2name.choices = [(i[0]) for i in team_id]
    map = []
    maparr = []
    sumarr = []
    winarr = []
    ratearr = []
    
    if form.validate_on_submit():
       
        maparr = []
        sumarr = []
        winarr = []
        ratearr = []

        cursor.execute("SELECT team_id FROM teams WHERE team_name='%s'"%(form.team1name.data))
        team1 = cursor.fetchone()
        team1id= team1[0]
        
        # if team1id != 0: #team2id:
        #     pass
        # else:
        #     flash('team names can\'t be same', 'warning')

        cursor.execute("select map_name from maps where map_id in (SELECT distinct map_id FROM roster_stats where roster_id in (  SELECT roster_id FROM rosters WHERE team_id='%s'))"%(team1id))
        map = cursor.fetchall()
       
        for item in map:
            maparr.append(item[0])
        print(maparr)
        cursor.execute("select count(ss.roster_id) from (SELECT * FROM roster_stats where roster_id in (  SELECT roster_id FROM rosters WHERE team_id='%s') AND map_id in (SELECT distinct map_id FROM roster_stats where roster_id in (  SELECT roster_id FROM rosters WHERE team_id='%s'))) AS ss group by ss.map_id order by ss.map_id"%(team1id, team1id))
        sum = cursor.fetchall()
        for item in sum:
            sumarr.append(item[0])
        print(sumarr)

        cursor.execute("select COALESCE(sss.co,0) from (select ss.map_id,count(ss.roster_id) from (SELECT * FROM roster_stats where roster_id in (  SELECT roster_id FROM rosters WHERE team_id='%s') AND map_id in (SELECT distinct map_id FROM roster_stats where roster_id in (  SELECT roster_id FROM rosters WHERE team_id='%s'))) AS ss group by ss.map_id order by ss.map_id) AS a left outer JOIN (select ss.map_id ,count(ss.roster_id) AS co from (SELECT * FROM roster_stats where roster_id in (  SELECT roster_id FROM rosters WHERE team_id='%s') AND map_id in (SELECT distinct map_id FROM roster_stats where roster_id in (  SELECT roster_id FROM rosters WHERE team_id='%s')) AND won_this_map=1 ) AS ss group by ss.map_id) AS sss on a.map_id = sss.map_id order by a.map_id;"%(team1id, team1id,team1id, team1id))
        win = cursor.fetchall()
        for item in win:
            winarr.append(item[0])
        print(winarr)
        try:
            for x in range(len(maparr)):
                a = 100*winarr[x]/sumarr[x]
                ratearr.append(a)
        except:
            flash('no winning record on this team')
        print(ratearr)
    return render_template("team.html",form=form,ratearr = ratearr,maparr = maparr)


@app.route('/teamperdiction', methods=['GET', 'POST'])
def teampred():
    form = TeamPredForm()
    winner = 'no result'
    cursor.execute("SELECT map_name FROM maps")
    data_id = cursor.fetchall()
    form.selectmap.choices = [(i[0]) for i in data_id]
    mapid = 0
    winrate = 'no result'
    rate_1 = 0
    rate_2=0

    cursor.execute("SELECT team_name FROM teams")
    team_id = cursor.fetchall()
    form.team1name.choices = [(i[0]) for i in team_id]
    form.team2name.choices = [(i[0]) for i in team_id]

    if form.validate_on_submit():
        if form.team1name.data != form.team2name.data:
            pass


      
        
            cursor.execute("SELECT team_id FROM teams WHERE team_name='%s'"%(form.team1name.data))
            team1 = cursor.fetchone()
            team1id= team1[0]

            cursor.execute("SELECT team_id FROM teams WHERE team_name='%s'"%(form.team2name.data))
            team2 = cursor.fetchone()
            team2id= team2[0]


            
       
            try:

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
                    rate_1 = 100*rate1/(rate1+rate2)
                    rate_2 = 100*rate2/(rate1+rate2)
                    if rate1 > rate2:
                        winner = form.team1name.data
                        winrate = rate_1
                    else:
                        winner = form.team2name.data
                        winrate = rate_2

                   
                except:
                    flash('Due to our limit database records, we can\'t predict the two teams on this map', 'warning')
            except:
                    flash('please check input', 'warning')
        else:
            flash('team names can\'t be same', 'warning')      
          


    return render_template("predteam.html",form=form,winner=winner,winrate=winrate,rate_1=rate_1,rate_2=rate_2)
  

@app.route('/playerperdiction', methods=['GET', 'POST'])
def playerpred():
    form = PlayerPredForm()
    if form.validate_on_submit():
      
        pass



    return render_template("predplayer.html",form=form)
