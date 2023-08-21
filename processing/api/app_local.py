from flask import Flask, render_template
import psycopg2
import os

app = Flask(__name__, template_folder='../templates')

DATABASE_URL = 'postgresql://rayanalyousef:Rayangsy1@localhost:5432/papers'
# Database connection for local testing
conn = psycopg2.connect(DATABASE_URL, sslmode='prefer')  # 'prefer' for flexibility on local setups

@app.route('/')
def index():
    cursor = conn.cursor()
    cursor.execute('SELECT topic, title, authors, date, pdf_url, article_text FROM papers')
    papers = cursor.fetchall()
    cursor.close()

    summarized_papers = []
    for paper in papers:
        summarized_paper = {
            'title': paper[1],
            'authors': paper[2],
            'date': paper[3],
            'pdf_url': paper[4]
        }
        summarized_papers.append(summarized_paper)

    print("Index route - Papers:", summarized_papers)

    return render_template('index.html', papers=summarized_papers)

@app.route('/papers')
def papers():
    cursor = conn.cursor()
    cursor.execute('SELECT topic, title, authors, date, pdf_url, article_text FROM papers')
    papers = cursor.fetchall()
    cursor.close()

    print("Papers route - Papers:", papers)
    return render_template('papers.html', papers=papers)

@app.route('/<topic>')
def topic(topic):
    topic_db_map = {
        'solar_energy': 'Solar Energy',
        'blockchain': 'Blockchain',
        'fusion_energy': 'Fusion Energy',
        'space_tech': 'Space Tech',
        'ai': 'Artificial Intelligence',
    }

    topic_template_map = {
        'solar_energy': 'solar_energy.html',
        'blockchain': 'blockchain.html',
        'fusion_energy': 'fusion_energy.html',
        'space_tech': 'space_tech.html',
        'ai': 'ai.html',
    }
    
    formatted_topic = topic_db_map.get(topic, '')
    template_filename = topic_template_map.get(topic, '')
    
    cursor = conn.cursor()
    cursor.execute('SELECT topic, title, authors, date, pdf_url, article_text FROM papers WHERE topic = %s', (formatted_topic,))
    topic_articles = cursor.fetchall()
    cursor.close()

    articles_dicts = []
    for article in topic_articles:
        article_dict = {
            'title': article[1],
            'authors': article[2],
            'date': article[3],
            'pdf_url': article[4],
            'article_text': article[5]
        }
        articles_dicts.append(article_dict)

    print("Topic route - Topic:", formatted_topic)
    
    if template_filename:
        return render_template(f'topics/{template_filename}', topic=formatted_topic, articles=articles_dicts)
    else:
        return "Topic not found", 404

if __name__ == '__main__':
    app.run(debug=True)
