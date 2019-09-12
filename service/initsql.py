import sqlite3

DATABASE = 'voting_result.db'

conn = sqlite3.connect(DATABASE)

# Create tables
c = conn.cursor()

c.execute(
    '''
CREATE TABLE votes
(datetime TEXT, group_name TEXT, vote1 INT, vote2 INT, vote3 INT)
    '''.strip()
)

conn.commit()

conn.close()