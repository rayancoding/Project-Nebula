import psycopg2

# Replace with your actual PostgreSQL credentials
DATABASE_URL = 'postgresql://username:password@host:port/dbname'

# Connect to the PostgreSQL database
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

# Define the SQL command to create the table
create_table_command = '''
CREATE TABLE papers (
    paper_id SERIAL PRIMARY KEY,
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

# Commit the changes
conn.commit()

# Close the connection
conn.close()