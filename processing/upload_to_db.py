
import json
import psycopg2
import os
import sys

# Database Connection String
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://rayanalyousef:Rayangsy1@localhost:5432/papers')
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Create Table If Not Exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS papers (
        id serial PRIMARY KEY,
        topic VARCHAR(255),
        title VARCHAR(1024),
        authors TEXT,
        date DATE,
        pdf_url VARCHAR(1024),
        article_text TEXT
    );
""")
conn.commit()

# List of Topics
topics_queries = ['Solar Energy', 'Blockchain', 'Space Tech', 'Artificial Intelligence', 'Fusion Energy']

# Base Path to Project Nebula Directory
project_nebula_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Process Each Topic
for topic in topics_queries:
    # Construct Absolute File Path
    filename = os.path.join(project_nebula_dir, f'processed_papers_{topic.replace(" ", "_")}.json')
    
    try:
        # Open and Load JSON File
        with open(filename, 'r') as file:
            data = json.load(file)

        # Extract Paper Data from JSON
        titles = data['titles']
        authors = data['authors']
        dates = data['dates']
        pdf_urls = data['pdf_urls']
        article_texts = data['article_texts']
        topics = data['topics']

        # Insert Each Paper into Database
        for paper_id in titles.keys():
            topic = topics.get(paper_id)
            title = titles.get(paper_id)
            author = ', '.join(authors.get(paper_id, []))
            date = dates.get(paper_id)
            pdf_url = pdf_urls.get(paper_id)
            article_text = article_texts.get(paper_id)

            try:
                # Execute SQL Insert Statement
                cursor.execute('INSERT INTO papers (topic, title, authors, date, pdf_url, article_text) VALUES (%s, %s, %s, %s, %s, %s)', 
                               (topic, title, author, date, pdf_url, article_text))
                print(f"Inserted data for paper ID: {paper_id} into the database")
            except psycopg2.Error as e:
                print(f"An error occurred while inserting data for paper ID {paper_id}: {e}")
    except FileNotFoundError as e:
        print(f"File {filename} not found. Skipping this topic. Error: {e}")
        continue

# Commit Transactions and Close Connection
conn.commit()
conn.close()
