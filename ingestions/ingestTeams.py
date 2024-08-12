import cfbd
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

def get_api_key():
    envApiKey = os.environ.get("CFBD_API_KEY")
    return envApiKey

configuration = cfbd.Configuration()
CFBD_api_key = get_api_key()
configuration.api_key['Authorization'] = CFBD_api_key
configuration.api_key_prefix['Authorization'] = 'Bearer'
api_config = cfbd.ApiClient(configuration)

teams_api = cfbd.TeamsApi(api_config)
teams = teams_api.get_fbs_teams()
response = [{
    "name": school.school, 
    "latitude": school.location.latitude, 
    "longitude": school.location.longitude, 
    "logolink": school.logos[0] if len(school.logos) > 0 else None, 
    "color": school.color, 
    "alt_color": school.alt_color
} for school in teams]


# Get a connection from the pool
conn = connection_pool.getconn()

# Create a cursor object
cur = conn.cursor()

# Insert each school into the teams table
for school in response:
    try:
        # Prepare the INSERT statement
        insert_query = '''
        INSERT INTO teams (name, latitude, longitude, logolink, color, alt_color)
        VALUES (%s, %s, %s, %s, %s, %s);
        '''
        
        # Execute the query
        cur.execute(insert_query, (
            school['name'],
            school['latitude'],
            school['longitude'],
            school['logolink'],
            school['color'],
            school['alt_color']
        ))
        
        print(f"Inserted {school['name']} into teams table.")
    except Exception as e:
        print(f"Error inserting {school['name']}: {e}")
        conn.rollback()  # Rollback in case of error
    else:
        conn.commit()  # Commit the transaction

# Close the cursor and return the connection to the pool
cur.close()
connection_pool.putconn(conn)
# Close all connections in the pool
connection_pool.closeall()