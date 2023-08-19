
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('/Users/rayanalyousef/Documents/GitHub/Project-Nebula/papers.db')
cursor = conn.cursor()

# Define the SQL command to create the table
create_table_command = '''
CREATE TABLE papers (
    topic TEXT,
    title TEXT,
    authors TEXT,
    date TEXT,
    pdf_url TEXT,
    article_text TEXT
)
'''

# Execute the SQL command
cursor.execute(create_table_command)

# Commit the changes and close the connection
conn.commit()
conn.close()
