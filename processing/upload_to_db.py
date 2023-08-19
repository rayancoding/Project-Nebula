
import json
import psycopg2
import os

# Replace "postgresql://username:password@host:port/dbname" with your actual PostgreSQL credentials
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://username:password@host:port/dbname')
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

topics_queries = ['Solar Energy', 'Blockchain', 'Space Tech', 'Artificial Intelligence', 'Fusion Energy']

for topic in topics_queries:
    filename = f'processed_papers_{topic.replace(" ", "_")}.json'
    
    try:
        with open(filename, 'r') as file:
            data = json.load(file)

        titles = data['titles']
        authors = data['authors']
        dates = data['dates']
        pdf_urls = data['pdf_urls']
        article_texts = data['article_texts']
        topics = data['topics']

        for paper_id in titles.keys():
            topic = topics.get(paper_id)
            title = titles.get(paper_id)
            author = ', '.join(authors.get(paper_id, []))
            date = dates.get(paper_id)
            pdf_url = pdf_urls.get(paper_id)
            article_text = article_texts.get(paper_id)

            try:
                cursor.execute('INSERT INTO papers (topic, title, authors, date, pdf_url, article_text) VALUES (?, ?, ?, ?, ?, ?)', 
                               (topic, title, author, date, pdf_url, article_text))
                print(f"Inserted data for paper ID: {paper_id} into the database")
            except psycopg2.Error as e:
                print(f"An error occurred while inserting data for paper ID {paper_id}: {e}")
    except FileNotFoundError as e:
        print(f"File {filename} not found. Skipping this topic. Error: {e}")
        continue

conn.commit()
conn.close()

