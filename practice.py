# Actually i had created different functions for calculation of different variable given in the doc
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

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


input_file = "input.xlsx"
df = pd.read_excel(input_file)
stop_words = load_stopwords()

# Function to clean text using stopwords
def clean_text(text):
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

# Iterate over URLs in the DataFrame and perform analysis
output_data = []
total_urls = len(df)
for index, row in df.iterrows():
    url_id = row['URL_ID']
    url = row['URL']

    # Extract article text
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
    except Exception as e:
        print(f"Error extracting text from {url}: {e}")
        continue

    # Clean text
    cleaned_text = clean_text(text)

    # Sentimental Analysis
    positive_score, negative_score, polarity_score, subjectivity_score = sentimental_analysis(
        cleaned_text)

    # Readability Analysis
    avg_sentence_length, percentage_complex_words, fog_index, avg_words_per_sentence, complex_word_count, word_count, syllable_per_word, personal_pronouns, avg_word_length = readability_analysis(
        text)

    output_data.append([url_id, url, positive_score, negative_score, polarity_score, subjectivity_score, avg_sentence_length, percentage_complex_words,
                       fog_index, avg_words_per_sentence, complex_word_count, word_count, syllable_per_word, personal_pronouns, avg_word_length])

    # Print status update
    print(f"Processed {index + 1} of {total_urls} URLs")

# Create DataFrame for output
output_df = pd.DataFrame(output_data, columns=['URL_ID', 'URL', 'POSITIVE SCORE', 'NEGATIVE SCORE', 'POLARITY SCORE', 'SUBJECTIVITY SCORE', 'AVG SENTENCE LENGTH',
                         'PERCENTAGE OF COMPLEX WORDS', 'FOG INDEX', 'AVG NUMBER OF WORDS PER SENTENCE', 'COMPLEX WORD COUNT', 'WORD COUNT', 'SYLLABLE PER WORD', 'PERSONAL PRONOUNS', 'AVG WORD LENGTH'])

# Save output to Excel file
output_file = "output.xlsx"
output_df.to_excel(output_file, index=False)
print(f"Output saved to {output_file}")
