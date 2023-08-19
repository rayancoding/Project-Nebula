
import arxiv
import io
import requests
from PyPDF2 import PdfReader
import openai
import sqlite3
import json


# OpenAI API key setup
openai.api_key = "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"

# List of topics and their respective queries
topics_queries = ["Fusion Energy", "Blockchain", "Solar Energy", "Space Tech", "Artificial Intelligence"]

def chunk_text(text, length=20000):
    """
    Function to split the text into chunks
    """
    chunks = [text[i:i + length] for i in range(0, len(text), length)]
    return chunks

def clean_text(text):
    """
    Function to clean the text by removing all line spacings
    and making the text one continuous string.
    """
    cleaned_text = text.replace('\n', ' ')
    # Remove any additional unwanted whitespace
    cleaned_text = ' '.join(cleaned_text.split())
    
    return cleaned_text

def process_paper(key, text):
    print(f"Processing PDF with key: {key}")

    # Clean and reformat the text using clean_text function
    text = clean_text(text)
    
    print(f"Total characters in cleaned and reformatted text: {len(text)}")
    chunks = chunk_text(text)
    print(f"Total chunks created for key {key}: {len(chunks)}")

    condensed_chunked_texts = []

    for index, chunk in enumerate(chunks):
        print(f"Number of characters in chunk {index + 1}: {len(chunk)}")
        
        if index == 0:
            # This is the first chunk of the paper. We can give it a special prompt.
            specialized_prompt = f"""
            Take this chunk of a text extracted from a research paper and condense into between 7000-10000 characters, if the paper
            I provide includes a reference list, exclude that from the condensed text. Also keep 
            in mind the text you generate will be integrated as the beginning of an article, alongside other condensed text. 
            I'll make the text better later, for now focus on reducing length while maintaining key info and meaning. 
            Here's the chunk of text: {chunk}
            """
        elif index == len(chunks) - 1:
            # This is the last chunk of the paper. We can give it another special prompt.
            specialized_prompt = f"""
            Take this chunk of a text extracted from a research paper and condense into less than 10000 characters, if the paper
            I provide includes a reference list, exclude that from the condensed text. Also keep 
            in mind the text you generate will be integrated as the end of an article, alongside other condensed text. 
            I'll make the text better later, for now focus on reducing length while maintaining key info and meaning. 
            Here's the chunk of text: {chunk}
            """
        else:
            # For all other chunks, we can use a generic prompt.
            specialized_prompt = f"""
            Take this chunk of a text extracted from a research paper and condense into less than 10000 characters, if the paper
            I provide includes a reference list, exclude that from the condensed text. Also keep 
            in mind the text you generate will be integrated into the middle of an article, the beginning and end have already 
            been condensed in a similar fashion. I'll make the text better later, for now focus on reducing length while 
            maintaining key info and meaning. 
            Here's the chunk of text: {chunk}
            """

        prompt_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": specialized_prompt}
        ]

        # Call the OpenAI API to generate a response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=prompt_messages,
            temperature=0.3,
            max_tokens= 6000
        )

        # Get the GPT-3 generated text
        generated_text = response.choices[0].message['content'].strip()

        # Append the GPT-3 generated text to the list
        condensed_chunked_texts.append(generated_text)

    # You can return or further process the condensed_chunked_texts here
    return condensed_chunked_texts

def max_tokens_calculator(condensed_text, specialized_prompt2):
    """
    Function to calculate max tokens for the second GPT-3 call
    """
    input_tokens = (len(condensed_text) / 4) + (len(specialized_prompt2) / 4)
    max_output_tokens = 16000 - input_tokens
    if max_output_tokens < 4000:
        max_output_tokens = 4000
    return int(max_output_tokens)

def refine_text(key, condensed_text):
    """
    Function to refine the condensed text
    """
    print(f"\nRefining Condensed Text with key: {key}")

    # Specialized Prompt for the Second Processing
    specialized_prompt2 = f"""
    
    I'm going to provide you with condensed text from a research paper to transform into an article for a news website, in order
    to do so, and do so well, I'll give you some guidelines. GUIDELINES ARE NOT OPTIONAL:

    1. **Specific Focus and Clarity**: 
    - The article should be focused, clear and specific. Make sure the reader knows why they should care about this article.
    - Break down complex topics into comprehensible pieces and avoid being vague. Clearly convey the core findings or aspects of the paper and how they connect to the broader theme.

    2. **Tone and Style**: 
    - Use a friendly and conversational tone, as if a knowledgeable friend is excitedly explaining a cool new scientific development.
    - Avoid jargon; when technical terms are unavoidable, provide a simple and relatable explanation or analogy.

    3. **Structure and Flow**: 
    - Start with a captivating introduction that grabs the reader’s attention and gives them a reason to stay engaged. 
    - End memorably in a way that revisits the significance of the research and leaves the reader pondering broader implications or exciting possibilities.

    4. **Storytelling and Context**: 
    - Use anecdotes, describe problems this research aims to solve.
    - Connect the research to bigger picture issues, trends, or implications, going beyond just summarizing the research paper.

    5. **Engagement and Readability**: 
    - Inject personality into the writing like you're a journalist in the respective field following the research very closely.
    - Break up the text with varied sentence lengths and structures to avoid looking and sounding robotic

    6. **Accuracy and Integrity**: 
    - Represent the research and its findings faithfully. Reference the researchers or the study only when it enhances the story and doesn't break the article's flow.
    - Do not exaggerate claims or speculate wildly. Stay grounded in what the research actually suggests.

    7. **Extra Insights and Analysis**: 
    - Include a section where you pose interesting questions or offer insightful commentary that goes beyond summarizing the research, addressing the 'so what?' aspect.
    - Discuss potential applications, challenges, and what experts in the field might be excited or concerned about.
    ALSO, DO NOT WRITE ANY HEADINGS OR SUBHEADINGS, ONLY WRITE THE BODIES OF THE ARTICLE.
    
    Example body(ies) of article titled "The Promise And Perils Of Superconductivity And Fusion Energy", use this example to better grasp and understand the guidelines layed out previously, specifically
    use the example to understand how to tone the article, structure, format etc.: 
    
    (start of example) 
    Superconductivity, or the idea that certain materials are capable of conducting direct current (DC) electricity without resistance or energy 
    loss, has been an elusive phenomenon for well over a century.

    In 1911, a Dutch scientist named Heike Kamerlingh-Onnes found that mercury could superconduct electricity at very low temperatures, a monumental
    discovery for which he was awarded the Nobel Prize.

    In the decades since, many more alloys and substances have also been shown to have superconductivity properties, but none so far has been able 
    to work in a stable, room-temperature setting—the Holy Grail of physics. That’s why it was such a big deal last month when a team of South 
    Korean scientists claimed to have created a breakthrough material, referred to as LK-99, that could supposedly conduct electricity without any 
    resistance at room temperatures and ambient (or normal) pressure. If confirmed, such a discovery could revolutionize the energy sector, 
    address climate change and significantly reduce energy waste and costs, not to mention contribute to advancements in MRI 
    technology, magnetic levitation trains, fusion energy and more.

    The Rise And Fall Of LK-99
    It’s impossible to overhype the significance of this allegation. Picture zero energy loss. The U.S. Energy Information Administration (EIA) 
    has estimated that roughly 5% of electricity transmission and distribution is lost annually. That may not sound like a lot—until you learn 
    that the U.S. generated over 4.2 trillion kilowatt hours (kWh) in 2022.
    We’re talking billions and billions of dollars in recovered energy every year.
    Following the startling announcement, shares of Korean and Chinese superconductor stocks soared, but as is often the case in any nascent 
    technology that makes extraordinary promises (do Elizabeth Holmes and Theranos ring a bell?), LK-99’s validity came under fierce scrutiny. 
    Many universities and labs around the world eagerly tried to replicate the experiment, to mixed results. The final blow came last week when 
    the University of Maryland’s Condensed Matter Theory Center (CMTC) tweeted, disappointedly, that LK-99 appeared not to be a superconductor 
    after all. The researchers, in fact, found that LK-99 was “a very resistive poor quality material.” This led to a swift downturn in South Korean 
    superconductor stocks. Wire technology companies Duksung Co. and Sunam Co. both closed last Tuesday’s session down approximately 30%.
    Despite the letdown, I don’t believe this is the last we’ll hear of a potential breakthrough in superconductivity. LK-99 may have been a 
    failure, but humans are far too innovative and competitive to let the matter rest.

    Fusion Ignition Is Lighting Up The Energy Landscape
    Last week, the LLNL announced that it repeated the results, achieving a net energy gain from a fusion reaction and heralding a pivotal milestone 
    toward the commercial realization of fusion power. Given these breakthroughs, fusion-related investments have skyrocketed. In 2021 alone, 
    investments surged to $2.6 billion from just $300 million in the prior year. Although 2022 saw a decrease to $521 million, 2023 is 
    already showing promising traction, according to Bloomberg. In the first half of the year, nuclear fusion firms and startups secured 
    $544 million in venture capital and private equity investments. The world currently boasts 33 nuclear fusion startups, according to 
    data provider Dealbook.co, all of them located in countries recognized for their contributions to international fusion research. Leading 
    the pack, the U.S. is home to five of these startups, followed by the U.K. with four. Germany has two, while Japan, Canada, France and Australia 
    each have one.
    As a reminder, we’re still many years away from using and enjoying fusion energy on a commercial scale, but the news is exciting 
    nonetheless, especially when paired with the promise of superconductivity.
    Innovation Versus Practicality For Investors
    Even with the anticipation swirling around fusion, we’re reminded of the costs and challenges involved in high-tech energy endeavors.
    Late last month, a new nuclear reactor began operations in Georgia, the first such U.S. plant in decades. Georgia Power Co., a 
    subsidiary of Atlanta-based Southern Company, announced the completion of Unit 3 at Plant Vogtle, which is now sending power to the grid. 
    When operating at its maximum capacity of 1,100 megawatts, the reactor is capable of powering over 500,000 homes and businesses across Georgia, 
    Florida and Alabama. However, Unit 3 reportedly came seven years behind schedule and a whopping $17 billion over budget. It’s a salient 
    reminder for investors to tread carefully, weighing the promise of innovation against practical challenges.
    I urge investors to keep a keen eye on developments in the superconductivity and fusion sectors. They represent not just the future of energy, 
    but also a realm of unique investment opportunities. Remember, in every challenge lies opportunity.

    (end of example)... When generating the article, you MUST keep in mind the overarching goal; to allow readers in the 
    related field, or interested in the field, to follow the specific research that's happening with low mental effort.
    Here is the full condensed text that needs to be transformed: {condensed_text}

    """

    prompt_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": specialized_prompt2}
    ]

    # Call the OpenAI API to generate a response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=prompt_messages,
        temperature=0.9,
        max_tokens= max_tokens_calculator(condensed_text, specialized_prompt2)
    )

    generated_text = response.choices[0].message['content'].strip()
    print(f"Finished refining condensed text with key: {key}")
    return generated_text


topics_queries = ['Solar Energy', 'Blockchain', 'Space Tech', 'Artificial Intelligence', 'Fusion Energy']

for topic in topics_queries:
    print(f"\nFetching papers for the topic: {topic}")

    titles = {}
    authors = {}
    dates = {}
    pdf_urls = {}
    pdf_texts = {}
    condensed_texts = {}
    article_texts = {}
    topics = {}

    processed_papers_count = 0

    Search = arxiv.Search(
        query=topic,
        max_results=100,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Ascending
    )

    for paper in Search.results():
        if processed_papers_count >= 3:
            break

        paper_id = paper.entry_id
        pdf_url = paper.pdf_url
        print(f"Processing paper ID {paper_id} ...")

        try:
            r = requests.get(pdf_url)
            with open('paper.pdf', 'wb') as f:
                f.write(r.content)

            with open('paper.pdf', 'rb') as f:
                reader = PdfReader(f)
                text = ' '.join(page.extract_text() for page in reader.pages)

        except Exception as e:
            print(f"An error occurred while processing paper ID {paper_id}: {e}")
            continue

        if len(text) < 150000:
            pdf_texts[paper_id] = text
            titles[paper_id] = paper.title
            authors[paper_id] = [str(author) for author in paper.authors]
            dates[paper_id] = paper.published.isoformat()
            pdf_urls[paper_id] = pdf_url
            topics[paper_id] = topic

            condensed_text = process_paper(paper_id, text)
            condensed_texts[paper_id] = condensed_text

            refined_text = refine_text(paper_id, condensed_text)
            article_texts[paper_id] = refined_text

            processed_papers_count += 1

    for paper in Search.results():
        if processed_papers_count >= 3:
            break

        paper_id = paper.entry_id
        pdf_url = paper.pdf_url

        try:
            r = requests.get(pdf_url)
            with open('paper.pdf', 'wb') as f:
                f.write(r.content)

            with open('paper.pdf', 'rb') as f:
                reader = PdfReader(f)
                text = ' '.join(page.extract_text() for page in reader.pages)

            pdf_texts[paper_id] = text
            titles[paper_id] = paper.title
            authors[paper_id] = [str(author) for author in paper.authors]
            dates[paper_id] = paper.published.isoformat()
            pdf_urls[paper_id] = pdf_url
            topics[paper_id] = topic

            condensed_text = process_paper(paper_id, text)
            condensed_texts[paper_id] = condensed_text

            refined_text = refine_text(paper_id, condensed_text)
            article_texts[paper_id] = refined_text

            processed_papers_count += 1

        except Exception as e:
            print(f"An error occurred during the fallback mechanism for paper ID {paper_id}: {e}")
            continue

    with open(f'processed_papers_{topic.replace(" ", "_")}.json', 'w') as file:
        json.dump({
            'titles': titles,
            'authors': authors,
            'dates': dates,
            'pdf_urls': pdf_urls,
            'topics': topics,
            'article_texts': article_texts
        }, file)

    print(f"Saved processed data for topic: {topic}")

print("Processing completed.")