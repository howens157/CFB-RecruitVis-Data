import csv
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

csv_filename = "recruits20-25.csv"

with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    # Get a connection from the pool
    conn = connection_pool.getconn()

    # Create a cursor object
    cur = conn.cursor()
    for row in reader:
        [year, name, position, rating, team, highschool, city, state] = row
        try:
            # Prepare the INSERT statement
            insert_query = '''
            INSERT INTO recruits (year, name, position, team, city, state, rating)
            VALUES (%s, %s, %s, (SELECT id FROM teams WHERE name = %s), %s, %s, %s);
            '''
            
            # Execute the query
            cur.execute(insert_query, (
                year,
                name,
                position,
                team,
                city,
                state,
                rating
            ))
            
            print(f"Inserted {name} into recruits table.")
        except Exception as e:
            print(f"Error inserting {name}: {e}")
            conn.rollback()  # Rollback in case of error
        else:
            conn.commit()  # Commit the transaction

    # Close the cursor and return the connection to the pool
    cur.close()
    connection_pool.putconn(conn)
    # Close all connections in the pool
    connection_pool.closeall()
