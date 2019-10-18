"""
Design for command line submit to ballot
to reduce click and write time
"""

import sqlite3
import re
import pandas as pd
from datetime import datetime
import requests

keep_running = True
DATABASE = 'voting_result.db'

# Global functions
def get_db():
    db = sqlite3.connect(DATABASE)
    return db

def update_graphs():
    r = requests.get('http://localhost:5000/send')
    try:
        print("Request status: {}".format(r.status_code))
    except Exception as e:
        print(e)
        print('Fail to access send')

while keep_running:
    # Check current group
    check_current = True
    while check_current:
        print("What is current group?")
        current_gp = input('Current Group: ')

        if current_gp == 'x':
            break

        if re.search('^[0-9]+$', current_gp):
            # Check voting history
            conn = get_db()
            votted = pd.read_sql(
                'SELECT group_name FROM votes WHERE group_name = \'{}\''.format(
                    current_gp
                ), 
                conn
            )

            if len(votted['group_name']) == 0:

                check_current = False
                print('Checking: {}'.format(current_gp))
                current_gp = int(current_gp)
            else:
                print('Ticket had been submitted for group {}'.format(current_gp))
        else:
            print('Invalid group ID input')
        
    if current_gp == 'x':
        break

    # Check input ballot
    check_vote = True
    while check_vote:
        print('What is group {}\'s vote?'.format(current_gp))
        vote = input('Vote: ')

        if re.search('^[0-9,]+$', vote):
            vote_parts = [int(x.strip()) for x in vote.split(',')]

            if not current_gp in vote_parts:
                if pd.Series(vote_parts).value_counts().max() == 1:
                    # Insert into database
                    current_db = get_db()
                    cur = current_db.cursor()
                    total_votes = []

                    first_choice = vote_parts[0]
                    second_choice = vote_parts[1] if len(vote_parts) > 1 \
                        else None
                    third_choice = vote_parts[2] if len(vote_parts) > 2 \
                        else None

                    total_votes.append((datetime.now(), str(current_gp), 
                        first_choice, second_choice, third_choice))

                    cur.executemany('INSERT INTO votes VALUES (?,?,?,?,?)', 
                        total_votes)
                    post_message = 'Successfully voted for {x}'.format(
                        x=current_gp
                    )
                    current_db.commit()
                    check_vote = False

                    update_graphs()

                else:
                    print('Duplicate vote is found')
            else:
                print('Cannot vote yourself')
        else:
            print('Invalid input')