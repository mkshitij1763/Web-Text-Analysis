import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
# from requests_html import HTMLSession
from requests_html import HTMLSession
import multiprocessing

# Function to load stopwords from external files
def load_stopwords():
    stopwords_files = ['StopWords_Auditor.txt', 'StopWords_Currencies.txt', 'StopWords_DatesandNumbers.txt',
                       'StopWords_Generic.txt', 'StopWords_GenericLong.txt', 'StopWords_Geographic.txt', 'StopWords_Names.txt']
    stopwords = set()
    # using set because so as to avoid repetition
    for file in stopwords_files:
        with open(file, 'r') as f:
            words = f.read().split()
            stopwords.update(words)
    return stopwords

# Global variable for caching
url_cache = {}

# Function to fetch URL content
def fetch_url_content(url):
    if url in url_cache:
        return url_cache[url]
    else:
        session = HTMLSession()
        response = session.get(url)
        response.html.render()
        text = response.html.text
        url_cache[url] = text
        return text

# Function to clean text using stopwords
def clean_text(text):
    stop_words = load_stopwords()
    tokens = word_tokenize(text.lower())
    cleaned_tokens = [re.sub(r'[^\w\s]', '', word)
                      for word in tokens if word.isalnum() and word not in stop_words]
    return cleaned_tokens

# Function to perform sentimental analysis
def sentimental_analysis(text):
    positive_words = set(open('positive-words.txt').read().split())
    negative_words = set(open('negative-words.txt').read().split())

    positive_score = sum(1 for word in text if word in positive_words)
    negative_score = sum(1 for word in text if word in negative_words)
    total_words = len(text)
    polarity_score = ((positive_score - negative_score)/(positive_score + negative_score + 0.000001))
    subjectivity_score = ((positive_score + negative_score)/(total_words + 0.000001))

    return positive_score, negative_score, polarity_score, subjectivity_score

# Function to perform readability analysis
def readability_analysis(text):
    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    word_count = len(words)
    total_sentences = len(sentences)

    # Average Sentence Length
    avg_sentence_length = word_count / total_sentences

    # Percentage of Complex words
    complex_words = [word for word in words if len(word) > 2]
    percentage_complex_words = len(complex_words) / word_count

    # Fog Index
    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)

    # Average Number of Words Per Sentence
    avg_words_per_sentence = word_count / total_sentences

    # Complex Word Count
    complex_word_count = len(complex_words)

    # Syllable Per Word
    syllable_per_word = sum([syllables(word) for word in words]) / word_count

    # Personal Pronouns
    personal_pronouns = len(re.findall(r'\b(?:I|we|my|ours|us)\b', text))

    # Excluding 'US' from personal pronouns
    personal_pronouns -= len(re.findall(r'\bUS\b', text))

    # Average Word Length
    avg_word_length = sum(len(word) for word in words) / word_count

    return avg_sentence_length, percentage_complex_words, fog_index, avg_words_per_sentence, complex_word_count, word_count, syllable_per_word, personal_pronouns, avg_word_length

# Function to count syllables in a word
def syllables(word):
    vowels = "aeiou"
    exceptions = ["es", "ed"]
    count = 0

    for letter in word:
        if letter in vowels:
            count += 1

    for exception in exceptions:
        if word.endswith(exception):
            count -= 1

    return count

# Function to process a single URL
def process_url(url_data):
    url_id, url = url_data
    try:
        text = fetch_url_content(url)
        cleaned_text = clean_text(text)
        positive_score, negative_score, polarity_score, subjectivity_score = sentimental_analysis(
            cleaned_text)
        avg_sentence_length, percentage_complex_words, fog_index, avg_words_per_sentence, complex_word_count, word_count, syllable_per_word, personal_pronouns, avg_word_length = readability_analysis(
            text)

        return [url_id, url, positive_score, negative_score, polarity_score, subjectivity_score, avg_sentence_length, percentage_complex_words,
                fog_index, avg_words_per_sentence, complex_word_count, word_count, syllable_per_word, personal_pronouns, avg_word_length]
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        return None

# Function to process URLs using multiprocessing
def process_urls(urls):
    with multiprocessing.Pool() as pool:
        processed_data = pool.map(process_url, urls)
    return [data for data in processed_data if data is not None]

# Main function
def main():
    input_file = "input.xlsx"
    df = pd.read_excel(input_file)
    total_urls = len(df)
    chunk_size = 10  # Adjust chunk size as needed
    url_chunks = [df[i:i+chunk_size] for i in range(0, total_urls, chunk_size)]
    output_data = []

    for chunk in url_chunks:
        processed_chunk = process_urls(chunk[['URL_ID', 'URL']].values)
        output_data.extend(processed_chunk)
        print(f"Processed {len(output_data)} of {total_urls} URLs")

    output_df = pd.DataFrame(output_data, columns=['URL_ID', 'URL', 'POSITIVE SCORE', 'NEGATIVE SCORE', 'POLARITY SCORE', 'SUBJECTIVITY SCORE', 'AVG SENTENCE LENGTH',
                         'PERCENTAGE OF COMPLEX WORDS', 'FOG INDEX', 'AVG NUMBER OF WORDS PER SENTENCE', 'COMPLEX WORD COUNT', 'WORD COUNT', 'SYLLABLE PER WORD', 'PERSONAL PRONOUNS', 'AVG WORD LENGTH'])

    output_file = "optimised_output.xlsx"
    output_df.to_excel(output_file, index=False)
    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    main()
