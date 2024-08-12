import os
from psycopg2 import pool
from dotenv import load_dotenv

# Load .env file
load_dotenv()
# Get the connection string from the environment variable
connection_string = os.getenv('DATABASE_URL')
# Create a connection pool
connection_pool = pool.SimpleConnectionPool(
    1,  # Minimum number of connections in the pool
    10,  # Maximum number of connections in the pool
    connection_string
)
# Check if the pool was created successfully
if connection_pool:
    print("Connection pool created successfully")

# Get a connection from the pool
conn = connection_pool.getconn()

# Create a cursor object
cur = conn.cursor()
teams = []

try:
    # Prepare the INSERT statement
    teams_query = '''
    select name from teams
    '''
    
    # Execute the query
    cur.execute(teams_query)
    teams = cur.fetchall()
    
except Exception as e:
    conn.rollback()  # Rollback in case of error
else:
    conn.commit()  # Commit the transaction

for team in teams:
    try:
        # Prepare the INSERT statement
        count_query = '''
        select count(*) from recruits where team = (select id from teams where name = %s);
        '''
        
        # Execute the query
        cur.execute(count_query, (
            team[0],
        ))

        currCount = cur.fetchone()
        if currCount[0] == 0:
            print(team[0])
            print(currCount[0])
        
    except Exception as e:
        print(f"Error counting {team[0]}: {e}")
        conn.rollback()  # Rollback in case of error
    else:
        conn.commit()  # Commit the transaction

# Close the cursor and return the connection to the pool
cur.close()
connection_pool.putconn(conn)
# Close all connections in the pool
connection_pool.closeall()
