from flask import Flask, render_template, request, send_from_directory, redirect
from flask import jsonify, g
from flask_socketio import SocketIO, send, emit
import pandas as pd
import numpy as np
import logging
import sqlite3
from datetime import datetime

import random
# logging.basicConfig(level=logging.INFO)

# Setting parameters
total_gps = 14
DATABASE = 'voting_result.db'

# Global functions
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def gen_voting_result():
    # Get the total votes
    conn = get_db()

    total_votes = pd.read_sql(
        '''SELECT vote1 as vote FROM votes 
UNION ALL 
SELECT vote2 as vote FROM votes WHERE vote2 IS NOT NULL 
UNION ALL 
SELECT vote3 as vote FROM votes WHERE vote3 IS NOT NULL'''.strip(), 
        conn)

    vote_counts = total_votes['vote'].value_counts().reset_index()\
        .sort_values(['index'])
    vote_counts = pd.DataFrame({'index': [x+1 for x in range(total_gps)]}).merge(
        vote_counts,
        on='index',
        how='left'
    ).fillna(0).sort_values(['index'])
    send_vote_counts = [
        {
            'name': 'Group {x}'.format(x=int(x[1][0])),
            'y': int(x[1][1])
        } for x in vote_counts.iterrows()
    ]

    votes_connection = pd.read_sql("""
SELECT vote1, vote2 FROM votes WHERE vote2 IS NOT NULL
UNION ALL
SELECT vote2 as vote1, vote3 as vote2 FROM votes WHERE vote3 IS NOT NULL
UNION ALL
SELECT vote1, vote3 as vote2 FROM votes WHERE vote3 IS NOT NULL
UNION ALL
SELECT vote1, vote1 as vote2 FROM votes WHERE vote2 IS NULL
""", conn)

    votes_connection['count'] = 1
    votes_con = votes_connection.groupby(['vote1', 'vote2'])['count'].count()\
        .reset_index()

    send_vote_con = [[int(x['vote1']), int(x['vote2']), int(x['count'])] 
        for y, x in votes_con.iterrows()]

    return send_vote_counts, send_vote_con


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hasnp'
socketio = SocketIO(app)

@app.route("/", methods=['POST', 'GET'])
def index():
    # Redirect to HA homepage

    return redirect("https://www.ha.org.hk", code=302)

@app.route("/voting/graphs", methods=['GET'])
def show_graphs():

    return render_template('index.html')

@app.route("/voting/vote_panel/", methods=['POST', 'GET'])
def postform():
    post_message = None
    current_db = get_db()
    if request.method == 'POST':
        # Search for result
        selected_gps = request.form.getlist('group_list[]')
        post_gp = request.form['group']
        print(selected_gps)
        if (len(selected_gps) < 4) and \
            (len(selected_gps) > 0):
            # Insert into db
            total_votes = []
            cur = current_db.cursor()
            
            post_group_id = post_gp.replace('Group ', '').strip()
            second_choice = selected_gps[1] if len(selected_gps) > 1 else None
            third_choice = selected_gps[2] if len(selected_gps) > 2 else None
            total_votes.append((datetime.now(), post_group_id, selected_gps[0], 
                second_choice, third_choice))

            cur.executemany('INSERT INTO votes VALUES (?,?,?,?,?)', total_votes)
            post_message = 'Successfully voted for {x}'.format(
                x=post_gp
            )
            current_db.commit()
    # Read the submitted list
    submitted_list = pd.read_sql('SELECT group_name FROM votes', current_db)

    gp_list = []
    for i in range(total_gps):
        gp_list.append({
            'name': 'Grp {id}'.format(id=i+1),
            'fullname':'Group {id}'.format(id=i+1),
            'id': (i+1),
            'class': 'btn-success' if str(i+1) in submitted_list['group_name'].values \
                else 'btn-primary'
        })

    new_data, new_conn = gen_voting_result()
    
    socketio.emit('new data', {
        'bar': new_data,
        'con': new_conn
    }, namespace='/ws')

    return render_template('vote.html',
            allgpinfo=gp_list,
            message=post_message)

@app.route('/files/<path:path>')
def send_js(path):
    return send_from_directory('files', path)


@app.route('/send', methods=['GET'])
def sending():

    new_data, new_conn = gen_voting_result()
    
    socketio.emit('new data', {
        'bar': new_data,
        'con': new_conn
    }, namespace='/ws')
    print('Emit new data')
    return 'sent'

@socketio.on('my event', namespace='/ws')
def handle_message(message):
    print('received message: ' + str(message))
    new_data, new_conn = gen_voting_result()
    emit('new data', {
        'bar': new_data,
        'con': new_conn
    }, namespace='/ws')

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    socketio.run(app, port=5000)
    print(request.path)
