from web import app

from flask import render_template, flash, request
from web.forms import SubmitForm, TeamPredForm, TeamForm

from web import cursor


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/index', methods=['GET'])
def index():
    return render_template("home.html")


@app.route('/manual', methods=['GET', 'POST'])
def manual():
    return render_template("manual.html")


@app.route('/players', methods=['GET'])
def player():
    form = SubmitForm()
    cursor.execute("SELECT DISTINCT event_name FROM events "
                   "JOIN matches ON events.event_id = matches.event_id "
                   "JOIN player_performance ON matches.match_id = player_performance.match_id "
                   "ORDER BY event_name ASC")
    events = cursor.fetchall()
    e = []
    for event in events:

        e.append(event[0])

    return render_template("player.html", events=e, form=form)


@app.route('/players/event', methods=['POST'])
def player_and_event():
    form = SubmitForm()
    event_name = request.form['event']

    query2 = "SELECT match_id FROM matches " \
             "JOIN events ON matches.event_id = events.event_id " \
             "WHERE event_name ='%s'" % event_name
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

    query = "SELECT DISTINCT map_name FROM player_performance " \
            "JOIN maps ON player_performance.map_id = maps.map_id " \
            "WHERE match_id ='%s'" % match_id
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

        cursor.execute("select map_name from maps where map_id in (SELECT distinct map_id FROM roster_stats where roster_id in (  SELECT roster_id FROM rosters WHERE team_id='%s')) order by map_id"%(team1id))
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
    rate_1 = 0.0
    rate_2=0.0

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
                    print(11111)
                    cursor.execute("SELECT COUNT(*) FROM roster_stats where roster_id in (  SELECT roster_id FROM rosters WHERE team_id='%s') AND map_id = '%s' AND won_this_map=1"%(team1id,mapid))
                    win1 = cursor.fetchone()
                    rate1 = 0.0
                    rate1 = win1[0]/num1[0]
                    print(win1[0]/num1[0])
                    print(rate1)
                    cursor.execute("SELECT COUNT(*) FROM roster_stats where roster_id in (  SELECT roster_id FROM rosters WHERE team_id='%s') AND map_id = '%s'"%(team2id,mapid))
                    num2 = cursor.fetchone()
                    cursor.execute("SELECT COUNT(*) FROM roster_stats where roster_id in (  SELECT roster_id FROM rosters WHERE team_id='%s') AND map_id = '%s' AND won_this_map=1"%(team2id,mapid))
                    win2 = cursor.fetchone()
                    rate2 = win2[0]/num2[0]
                    print(rate2)
                    if rate1 == 0 or rate2 == 0:
                        flash('Due to our limit database records, we can\'t predict the two teams on this map', 'warning')
                    else:
                        rate_1 = 100*rate1/(rate1+rate2)
                        rate_2 = 100*rate2/(rate1+rate2)
                        if rate1 > rate2:
                            winner = form.team1name.data
                            winrate = round(rate_1,2)
                        else:
                            winner = form.team2name.data
                            winrate = round(rate_2,2)

                   
                except:
                    flash('Due to our limit database records, we can\'t predict the two teams on this map', 'warning')
            except:
                    flash('please check input', 'warning')
        else:
            flash('team names can\'t be same', 'warning')      
          


    return render_template("predteam.html",form=form,winner=winner,winrate=winrate,rate_1=rate_1,rate_2=rate_2)
  

@app.route('/playerperdiction', methods=['GET'])
def playerpred():
    form = SubmitForm()
    query = "SELECT map_name, COUNT(*) FROM player_performance " \
            "join maps on player_performance.map_id = maps.map_id " \
            "group by player_performance.map_id"
    cursor.execute(query)
    maps = cursor.fetchall()
    map_names = []
    player_names = [" "]
    query2 = "SELECT DISTINCT player_name FROM players INNER JOIN player_performance ON players.player_id = player_performance.player_id ORDER BY player_name ASC"
    cursor.execute(query2)
    tmp = cursor.fetchall()
    for t in tmp:
        player_names.append(t[0])
    for m in maps:
        map_names.append(m[0])

    return render_template("predplayer.html", form=form, maps=map_names, players=player_names)


@app.route('/playerperdiction/submit', methods=['POST'])
def playerpred_calculation():
    form = SubmitForm()
    p1 = request.form['player1']
    p2 = request.form['player2']
    p3 = request.form['player3']
    p4 = request.form['player4']
    p5 = request.form['player5']
    map_name = request.form['map']

    query = "SELECT map_name, COUNT(*) FROM player_performance " \
            "join maps on player_performance.map_id = maps.map_id " \
            "group by player_performance.map_id"
    cursor.execute(query)
    maps = cursor.fetchall()
    player_names = [" "]
    map_names = []
    query2 = "SELECT DISTINCT player_name FROM players " \
             "INNER JOIN player_performance ON players.player_id = player_performance.player_id " \
             "ORDER BY player_name ASC"
    cursor.execute(query2)
    tmp = cursor.fetchall()
    for t in tmp:
        player_names.append(t[0])
    for m in maps:
        map_names.append(m[0])

    if p1 == p2 or p1 == p3 or p1 == p4 or p1 == p5 or \
            p2 == p3 or p2 == p4 or p2 == p5 or \
            p3 == p4 or p3 == p5 or \
            p4 == p5:

        flash('Please Check Player Names', 'error')

        return render_template("predplayer.html", form=form, maps=map_names, players=player_names)

    print("Map map:" + map_name)

    #######################################################################################

    p1query = "SELECT * FROM player_performance " \
              "LEFT JOIN players ON players.player_id = player_performance.player_id " \
              "JOIN maps ON player_performance.map_id = maps.map_id " \
              "WHERE player_name = '%s' AND map_name = '%s'" % (p1, map_name)
    cursor.execute(p1query)
    player_history = cursor.fetchall()

    p1KDA = 0
    p1ADR = 0
    p1Ranking = 0
    counter = 0
    if not player_history:
        flash(p1 + " has no matches for Map: " + map_name, 'error')
    for h in player_history:
        counter += 1
        p1ADR += h[7]
        p1Ranking += h[6]

        if h[4] != 0:
            formula = float(h[3] + (.5 * h[5])) / float(h[4])
        else:
            formula = float(h[3] + (.5 * h[5]))

        p1KDA += formula

    if counter != 0:
        p1ADR /= counter
        p1Ranking /= counter
        p1KDA /= counter

    ##########################################################################################

    p2query = "SELECT * FROM player_performance " \
              "LEFT JOIN players ON players.player_id = player_performance.player_id " \
              "JOIN maps ON player_performance.map_id = maps.map_id " \
              "WHERE player_name = '%s' AND map_name = '%s'" % (p2, map_name)
    cursor.execute(p2query)
    player2_history = cursor.fetchall()

    p2KDA = 0
    p2ADR = 0
    p2Ranking = 0
    counter = 0
    if not player2_history:
        flash(p2 + " has no matches for Map: " + map_name, 'error')
    for h in player2_history:

        counter += 1
        p2ADR += h[7]
        p2Ranking += h[6]

        if h[4] != 0:
            formula = float(h[3] + (.5 * h[5])) / float(h[4])
        else:
            formula = float(h[3] + (.5 * h[5]))

        p2KDA += formula

    if counter != 0:
        p2ADR /= counter
        p2Ranking /= counter
        p2KDA /= counter

    ##########################################################################################

    p3query = "SELECT * FROM player_performance " \
              "LEFT JOIN players ON players.player_id = player_performance.player_id " \
              "JOIN maps ON player_performance.map_id = maps.map_id " \
              "WHERE player_name = '%s' AND map_name = '%s'" % (p3, map_name)
    cursor.execute(p3query)
    player3_history = cursor.fetchall()

    p3KDA = 0
    p3ADR = 0
    p3Ranking = 0
    counter = 0
    if not player3_history:
        flash(p3 + " has no matches for Map: " + map_name, 'error')
    for h in player3_history:

        counter += 1
        p3ADR += h[7]
        p3Ranking += h[6]

        if h[4] != 0:
            formula = float(h[3] + (.5 * h[5])) / float(h[4])
        else:
            formula = float(h[3] + (.5 * h[5]))

        p3KDA += formula

    if counter != 0:
        p3ADR /= counter
        p3Ranking /= counter
        p3KDA /= counter

    ##########################################################################################

    p4query = "SELECT * FROM player_performance " \
              "LEFT JOIN players ON players.player_id = player_performance.player_id " \
              "JOIN maps ON player_performance.map_id = maps.map_id " \
              "WHERE player_name = '%s' AND map_name = '%s'" % (p4, map_name)
    cursor.execute(p4query)
    player4_history = cursor.fetchall()

    p4KDA = 0
    p4ADR = 0
    p4Ranking = 0
    counter = 0
    if not player4_history:
        flash(p4 + " has no matches for Map: " + map_name, 'error')
    for h in player4_history:

        counter += 1
        p4ADR += h[7]
        p4Ranking += h[6]

        if h[4] != 0:
            formula = float(h[3] + (.5 * h[5])) / float(h[4])
        else:
            formula = float(h[3] + (.5 * h[5]))

        p4KDA += formula

    if counter != 0:
        p4ADR /= counter
        p4Ranking /= counter
        p4KDA /= counter

    ##########################################################################################

    p5query = "SELECT * FROM player_performance " \
              "LEFT JOIN players ON players.player_id = player_performance.player_id " \
              "JOIN maps ON player_performance.map_id = maps.map_id " \
              "WHERE player_name = '%s' AND map_name = '%s'" % (p5, map_name)
    cursor.execute(p5query)
    player5_history = cursor.fetchall()

    p5KDA = 0
    p5ADR = 0
    p5Ranking = 0
    counter = 0
    if not player5_history:
        flash(p5 + " has no matches for Map: " + map_name, 'error')
    for h in player5_history:

        counter += 1
        p5ADR += h[7]
        p5Ranking += h[6]

        if h[4] != 0:
            formula = float(h[3] + (.5 * h[5])) / float(h[4])
        else:
            formula = float(h[3] + (.5 * h[5]))

        p5KDA += formula

    if counter != 0:
        p5ADR /= counter
        p5Ranking /= counter
        p5KDA /= counter

    #############################################################################################

    target = " "
    max_adr = max(p1ADR, p2ADR, p3ADR, p4ADR, p5ADR)
    max_kda = max(p1KDA, p2KDA, p3KDA, p4KDA, p5KDA)
    max_ranking = max(p1Ranking, p2Ranking, p3Ranking, p4Ranking, p5Ranking)
    stats = []
    reasoning = ""

    if max_adr == p1ADR and max_ranking == p1Ranking and max_kda == p1KDA:
        target = p1
        stats.append(p1ADR)
        stats.append(p1Ranking)
        stats.append(p1KDA)
        reasoning = p1 + " had highest average ranking, adr, and kda."
    elif max_adr == p2ADR and max_ranking == p2Ranking and max_kda == p2KDA:
        target = p2
        stats.append(p2ADR)
        stats.append(p2Ranking)
        stats.append(p2KDA)
        reasoning = p2 + " had highest average ranking, adr, and kda."
    elif max_adr == p3ADR and max_ranking == p3Ranking and max_kda == p3KDA:
        target = p3
        stats.append(p3ADR)
        stats.append(p3Ranking)
        stats.append(p3KDA)
        reasoning = p3 + " had highest average ranking, adr, and kda."
    elif max_adr == p4ADR and max_ranking == p4Ranking and max_kda == p4KDA:
        target = p4
        stats.append(p4ADR)
        stats.append(p4Ranking)
        stats.append(p4KDA)
        reasoning = p4 + " had highest average ranking, adr, and kda."
    elif max_adr == p5ADR and max_ranking == p5Ranking and max_kda == p5KDA:
        target = p5
        stats.append(p5ADR)
        stats.append(p5Ranking)
        stats.append(p5KDA)
        reasoning = p5 + " had highest average ranking, adr, and kda."

    if target == " ":
        if max_adr == p1ADR and max_ranking == p1Ranking:
            target = p1
            stats.append(p1ADR)
            stats.append(p1Ranking)
            reasoning = p1 + " had highest average ranking and adr."
        elif max_adr == p2ADR and max_ranking == p2Ranking:
            target = p2
            stats.append(p2ADR)
            stats.append(p2Ranking)
            stats.append(p2KDA)
            reasoning = p2 + " had highest average ranking and adr."
        elif max_adr == p3ADR and max_ranking == p3Ranking:
            target = p3
            stats.append(p3ADR)
            stats.append(p3Ranking)
            stats.append(p3KDA)
            reasoning = p3 + " had highest average ranking and adr."
        elif max_adr == p4ADR and max_ranking == p4Ranking:
            target = p4
            stats.append(p4ADR)
            stats.append(p4Ranking)
            stats.append(p4KDA)
            reasoning = p4 + " had highest average ranking and adr."
        elif max_adr == p5ADR and max_ranking == p5Ranking:
            target = p5
            stats.append(p5ADR)
            stats.append(p5Ranking)
            stats.append(p5KDA)
            reasoning = p5 + " had highest average ranking and adr."

    if target == " ":
        if max_ranking == p1Ranking:
            target = p1
            stats.append(p1ADR)
            stats.append(p1Ranking)
            stats.append(p1KDA)
            reasoning = p1 + " had highest average ranking."
        elif max_ranking == p2Ranking:
            target = p2
            stats.append(p2ADR)
            stats.append(p2Ranking)
            stats.append(p2KDA)
            reasoning = p2 + " had highest average ranking."
        elif max_ranking == p3Ranking:
            target = p3
            stats.append(p3ADR)
            stats.append(p3Ranking)
            stats.append(p3KDA)
            reasoning = p3 + " had highest average ranking."
        elif max_ranking == p4Ranking:
            target = p4
            stats.append(p4ADR)
            stats.append(p4Ranking)
            stats.append(p4KDA)
            reasoning = p4 + " had highest average ranking."
        elif max_ranking == p5Ranking:
            target = p5
            stats.append(p5ADR)
            stats.append(p5Ranking)
            stats.append(p5KDA)
            reasoning = p5 + " had highest average ranking."

    labels = ["ADR", "Ranking", "KDA"]

    return render_template("predplayer.html", form=form, maps=map_names, players=player_names, target=target, stats=stats, labels=labels, reason=reasoning)
