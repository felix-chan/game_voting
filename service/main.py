from flask import Flask, render_template, request, send_from_directory, redirect
from flask import jsonify, g, url_for
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, send, emit
import pandas as pd
import numpy as np
import logging
import sqlite3
import os
from datetime import datetime

import random
# logging.basicConfig(level=logging.INFO)

# Setting parameters
total_gps = 16
DATABASE = 'voting_result.db'
UPLOAD_FOLDER = '../image_tools/upload_image'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
GROUP_KEY_PAIRS = {
    '2846CAC71F': 'group01.jpg',
	'978A8FED4C': 'group02.jpg',
	'B125E677F4': 'group03.jpg',
	'4D4F79E101': 'group04.jpg',
	'BF835C8991': 'group05.jpg',
	'933AF2A0F2': 'group06.jpg',
	'13E3236A83': 'group07.jpg',
	'EBDBA6608A': 'group08.jpg',
	'65F933EF62': 'group09.jpg',
	'B0943812D6': 'group10.jpg',
	'01FBEB60EB': 'group11.jpg',
	'68D61DD646': 'group12.jpg',
	'ECE6999387': 'group13.jpg',
	'96325F0A1D': 'group14.jpg',
	'97FD18D0B4': 'group15.jpg',
	'A0D45620DB': 'group16.jpg'
}

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
        '''SELECT vote1 as vote, 5 as score FROM votes 
UNION ALL 
SELECT vote2 as vote, 3 as score FROM votes WHERE vote2 IS NOT NULL 
UNION ALL 
SELECT vote3 as vote, 1 as score FROM votes WHERE vote3 IS NOT NULL'''.strip(), 
        conn)

    vote_counts = total_votes.groupby(['vote'])['score'].sum().reset_index()\
        .sort_values(['vote'])
    vote_counts = pd.DataFrame({'vote': [x+1 for x in range(total_gps)]}).merge(
        vote_counts,
        on='vote',
        how='left'
    ).fillna(0).sort_values(['vote'])
    send_vote_counts = [
        {
            'name': 'Table {x}'.format(x=int(x[1][0])),
            'y': int(x[1][1])
        } for x in vote_counts.iterrows()
    ]

    # Calculate the top 3 groups
    top3_votes = vote_counts.sort_values(['score'], ascending=[False])\
        ['vote'].head(3)
    top3_vote_list = [int(x) for x in top3_votes.values]

    last_vote = pd.read_sql('''
SELECT * FROM votes
ORDER BY datetime DESC
LIMIT 1
    '''.strip(), conn)

    last_vote_list = []
    for i, rows in last_vote.iterrows():
        last_vote_list.append(rows['vote1'])
        if rows['vote2']:
            last_vote_list.append(rows['vote2'])
        if rows['vote3']:
            last_vote_list.append(rows['vote3'])

    return send_vote_counts, {
        'group_id': last_vote['group_name'].values[0] \
            if len(last_vote['group_name'].values) > 0 else 0,
        'votes': last_vote_list
    }, top3_vote_list

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hasnp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
        selected_gps = []
        for gid in range(total_gps):
            g_name = 'group_list_{id}'.format(id=(gid + 1))
            group_option = request.form[g_name] if g_name in request.form else ''
            if group_option != '':
                selected_gps.append({
                    'group_id': (gid + 1), 
                    'option': int(group_option)
                })
        post_gp = request.form['group']
        print(selected_gps)
        if (len(selected_gps) < 4) and \
            (len(selected_gps) > 0):
            # Insert into db
            selected_gps_df = pd.DataFrame(selected_gps)
            total_votes = []
            cur = current_db.cursor()
            
            post_group_id = post_gp.replace('Group ', '').strip()
            first_choice = int(selected_gps_df[selected_gps_df.option == 1]['group_id'].values[0])
            second_choice = int(selected_gps_df[selected_gps_df.option == 2]['group_id'].values[0]) \
                if len(selected_gps) > 1 else None
            third_choice = int(selected_gps_df[selected_gps_df.option == 3]['group_id'].values[0]) \
                if len(selected_gps) > 2 else None
            total_votes.append((datetime.now(), post_group_id, first_choice, 
                second_choice, third_choice))
            print(total_votes)

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

    new_data, last_vote, top3 = gen_voting_result()
    
    socketio.emit('new data', {
        'bar': new_data,
        'last_vote': last_vote,
        'top3': top3
    }, namespace='/ws')

    return render_template('vote.html',
            allgpinfo=gp_list,
            message=post_message)

@app.route('/files/<path:path>')
def send_js(path):
    return send_from_directory('files', path)


@app.route('/send', methods=['GET'])
def sending():

    new_data, last_vote, top3 = gen_voting_result()
    
    socketio.emit('new data', {
        'bar': new_data,
        'last_vote': last_vote,
        'top3': top3
    }, namespace='/ws')
    print('Emit new data')
    return 'sent'

@app.route('/submit_gpimg/<key>/', methods=['GET', 'POST'])
def submit_img(key):
    post_message = ''
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            post_message = 'No file part'
            
        file = request.files['file']
        # Check if filename exists
        if file.filename == '':
            post_message = 'No selected file'
            
        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            
            if key in GROUP_KEY_PAIRS:
                filename = GROUP_KEY_PAIRS[key]
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect('/snpstaffforum/success.html')
            else:
                post_message = 'Invalid key'
        else:
            post_message = 'Not allowed image type'

    return render_template('upload.html',
        input_key=key,
        message=post_message)

@socketio.on('my event', namespace='/ws')
def handle_message(message):
    print('received message: ' + str(message))
    new_data, last_vote, top3 = gen_voting_result()
    emit('new data', {
        'bar': new_data,
        'last_vote': last_vote,
        'top3': top3
    }, namespace='/ws')

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    socketio.run(app, port=5000)
    print(request.path)
